#!/usr/bin/env bash
set -Eeuo pipefail

log() { printf "%s\n" "$*" >&2; }
die() { printf "ERROR: %s\n" "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "Required '$1' in PATH"; }

cleanup() {
  [[ -n "${TMP_DIR:-}" && -d "$TMP_DIR" ]] && rm -rf "$TMP_DIR"
}
trap cleanup EXIT

RELEASE_NAME="${RELEASE_NAME:-foodgram}"
NAMESPACE="${NAMESPACE:-foodgram}"
CHART_PATH="${CHART_PATH:-./foodgram}"
VALUES_FILE="${VALUES_FILE:-$CHART_PATH/values.yaml}"
HELM_TIMEOUT="${HELM_TIMEOUT:-10m}"

FALLBACK_ADDR="${FALLBACK_ADDR:-http://127.0.0.1:8200}"

log "Loading variables from .env (if exists)..."
[[ -f .env ]] && set -a && source .env && set +a

need curl
need helm
need vals

[[ -f "$VALUES_FILE" ]] || die "Values file not found: $VALUES_FILE"
[[ -d "$CHART_PATH" ]]  || die "Chart directory not found: $CHART_PATH"

: "${VAULT_ROLE_ID:?VAULT_ROLE_ID not set (in .env or environment)}"
: "${VAULT_SECRET_ID:?VAULT_SECRET_ID not set (in .env or environment)}"
: "${VAULT_ADDR:?VAULT_ADDR not set (in .env or environment)}"

if [[ "$VAULT_ADDR" =~ ^https?:// ]]; then
  VAULT_ADDR_NORM="$VAULT_ADDR"
else
  VAULT_ADDR_NORM="http://$VAULT_ADDR"
fi

check_and_deploy_for_addr() {
  local ADDR="$1"
  log "Checking Vault availability at $ADDR ..."
  local code
  code="$(curl -fsS -o /dev/null -w '%{http_code}' "$ADDR/v1/sys/health" || true)"
  case "$code" in
    200|429) log "Vault is available (code=$code)." ;;
    503)     die "Vault is sealed at $ADDR. Unseal and retry." ;;
    "")      die "Could not connect to $ADDR/v1/sys/health (network issue?)" ;;
    *)       die "Unexpected response from Vault $ADDR: HTTP $code" ;;
  esac

  log "Testing AppRole login via $ADDR ..."
  local login_http
  login_http="$(curl -sS -o /dev/null -w '%{http_code}' \
    -H "Content-Type: application/json" \
    -d "{\"role_id\":\"$VAULT_ROLE_ID\",\"secret_id\":\"$VAULT_SECRET_ID\"}" \
    "$ADDR/v1/auth/approle/login" || true)"
  if [[ "$login_http" != "200" ]]; then
    die "AppRole login at $ADDR returned HTTP $login_http.
Check:
  • /v1/auth/approle/login accessibility via Ingress/address;
  • ROLE_ID/SECRET_ID correctness;
  • policies and 'auth/approle' mount."
  fi
  log "AppRole login successful."

  export VALS_VAULT_ADDR="$ADDR"
  export VALS_VAULT_AUTH_METHOD="approle"
  export VALS_VAULT_ROLE_ID="$VAULT_ROLE_ID"
  export VALS_VAULT_SECRET_ID="$VAULT_SECRET_ID"
  export VALS_VAULT_SKIP_VERIFY="true"

  log "Testing secret access via vals (secret not printed)..."
  if ! output="$(vals get 'ref+vault://secret/foodgram/database#POSTGRES_PASSWORD' 2>&1 >/dev/null)"; then
    printf "%s\n" "$output" >&2
    die "Failed to read secret via vals at $ADDR."
  fi
  log "Secret read access confirmed."

  TMP_DIR="$(mktemp -d)"
  local RENDERED="$TMP_DIR/values.rendered.yaml"

  log "Rendering $VALUES_FILE via vals ..."
  vals eval -f "$VALUES_FILE" > "$RENDERED"
  [[ -s "$RENDERED" ]] || die "Empty values render result"

  log "Deploying Helm chart '${RELEASE_NAME}' to namespace '${NAMESPACE}' ..."
  helm upgrade --install "$RELEASE_NAME" "$CHART_PATH" \
    -n "$NAMESPACE" --create-namespace \
    -f "$RENDERED" \
    --atomic --timeout "$HELM_TIMEOUT"

  log "Deployment completed successfully via $ADDR."
}

check_and_deploy_for_addr "$VAULT_ADDR_NORM"

log "Foodgram deployment completed!"