#!/bin/bash
set -e

echo "🧹 Останавливаю старый Vault и чищу namespace..."
pkill vault || true
kubectl delete namespace foodgram --ignore-not-found

echo "🚀 Запускаю Vault в dev-режиме..."
vault server -dev > vault.log 2>&1 &

echo "⏳ Ожидаю запуск Vault..."
for i in {1..15}; do
  if grep -q "Root Token:" vault.log; then
    break
  fi
  sleep 1
done

VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_ADDR

echo "📜 Проверяю лог Vault..."
tail -n 10 vault.log
sleep 3
ROOT_TOKEN=$(grep -m1 "Root Token:" vault.log | awk '{print $3}')
if [ -z "$ROOT_TOKEN" ]; then
  echo "❌ Не удалось получить Root Token. Проверь лог vault.log."
  exit 1
fi

export VAULT_TOKEN=$ROOT_TOKEN
echo "🔑 Vault Root Token: $ROOT_TOKEN"

echo "⚙️ Настраиваю Vault..."
vault auth enable approle || true

vault kv put secret/foodgram/rabbitmq RABBITMQ_USERNAME=user RABBITMQ_PASSWORD=12345

vault policy write foodgram-rabbitmq-policy - <<EOF
path "secret/data/foodgram/rabbitmq" {
  capabilities = ["read"]
}
EOF

vault write auth/approle/role/foodgram-rabbitmq \
    token_policies="foodgram-rabbitmq-policy" \
    secret_id_ttl=24h \
    token_ttl=1h \
    token_max_ttl=4h

ROLE_ID=$(vault read -field=role_id auth/approle/role/foodgram-rabbitmq/role-id)
SECRET_ID=$(vault write -f -field=secret_id auth/approle/role/foodgram-rabbitmq/secret-id)

echo "✅ ROLE_ID: $ROLE_ID"
echo "✅ SECRET_ID: $SECRET_ID"

echo "🧩 Обновляю .env..."
cat > .env <<EOF
VAULT_ADDR=$VAULT_ADDR
VAULT_ROLE_ID=$ROLE_ID
VAULT_SECRET_ID=$SECRET_ID
EOF

echo "🚢 Запускаю деплой..."
bash deploy.sh

echo "🎉 Всё готово! Vault и RabbitMQ успешно развернуты."
