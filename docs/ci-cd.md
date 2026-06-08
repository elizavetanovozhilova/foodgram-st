# Инструкция по CI/CD

## Что сделано в проекте

В проект добавлена настройка для задания "8. Работа с CI/CD".

Файлы:

- `.releaserc.json` - настройка `semantic-release`.
- `package.json` - зависимости для запуска `semantic-release`.
- `.github/scripts/semantic-release.mjs` - запуск `semantic-release` и передача тега в pipeline.
- `.github/workflows/release-deploy.yml` - основной pipeline: тег, сборка Docker-образов, деплой через Helm.
- `.github/workflows/runner-check.yml` - проверка своего runner.
- `infra/github-runner/controller-values.yaml` - values для controller chart.
- `infra/github-runner/runner-scale-set-values.yaml` - values для runner scale set.

## Часть 1. Semantic-release, Docker и деплой

Pipeline запускается при push в ветку `main` или вручную через GitHub Actions.

Этапы pipeline:

1. `semantic-release` смотрит историю коммитов и создает тег вида `v1.2.3`.
2. GitHub Actions собирает Docker-образы:

```text
ghcr.io/<owner>/<repo>/backend:<tag>
ghcr.io/<owner>/<repo>/frontend:<tag>
```

3. Pipeline деплоит эти образы в Kubernetes через Helm chart `foodgram`.

Для автоматического тега нужны коммиты в формате Conventional Commits:

```text
feat: add ci cd pipeline
fix: correct backend image build
```

`feat` создает minor-версию, `fix` создает patch-версию.

## Что нужно добавить в GitHub

В репозитории GitHub открой:

```text
Settings -> Secrets and variables -> Actions
```

Добавь secret:

```text
KUBE_CONFIG
```

В `KUBE_CONFIG` нужно вставить содержимое kubeconfig от Kubernetes-кластера.

После подключения своего runner добавь variable:

```text
CI_RUNNER_LABEL=foodgram-runner-set
```

Пока variable не добавлена, pipeline будет запускаться на обычном GitHub runner `ubuntu-latest`.

## Как запустить Kubernetes локально

Самый простой вариант для проверки на Mac - Docker Desktop.

1. Открой Docker Desktop.
2. Зайди в `Settings -> Kubernetes`.
3. Включи `Enable Kubernetes`.
4. Нажми `Apply & Restart`.
5. Дождись статуса `Kubernetes is running`.

Проверь, что Kubernetes работает:

```bash
kubectl cluster-info
kubectl get nodes
```

Если используешь minikube:

```bash
minikube start --driver=docker --cpus=2 --memory=3072
kubectl get nodes
```

Если была ошибка из-за памяти Docker Desktop, сначала удали неудачный профиль и запусти minikube с меньшей памятью:

```bash
minikube delete
minikube start --driver=docker --cpus=2 --memory=3072
kubectl get nodes
```

## Как проверить Helm-деплой локально

Сначала проверь, что chart собирается:

```bash
helm template foodgram ./foodgram \
  --namespace foodgram \
  --set-string backend.image=ghcr.io/elizavetanovozhilova/foodgram-st/backend:v1.0.0 \
  --set-string frontend.image=ghcr.io/elizavetanovozhilova/foodgram-st/frontend:v1.0.0
```

Если ошибок нет, можно выполнить локальный деплой:

```bash
helm dependency update ./foodgram

helm upgrade --install foodgram ./foodgram \
  --namespace foodgram \
  --create-namespace \
  --set-string backend.image=ghcr.io/elizavetanovozhilova/foodgram-st/backend:v1.0.0 \
  --set-string frontend.image=ghcr.io/elizavetanovozhilova/foodgram-st/frontend:v1.0.0 \
  --wait \
  --timeout 10m
```

Проверка:

```bash
kubectl get pods -n foodgram
kubectl get svc -n foodgram
kubectl get ingress -n foodgram
```

Если образы еще не опубликованы в GHCR, локальный деплой может не скачать их. Тогда сначала нужно запустить GitHub Actions pipeline, чтобы он собрал и отправил образы в registry.

Для локальной проверки без GHCR можно собрать образы прямо внутри minikube:

```bash
eval $(minikube docker-env)

docker build -t foodgram-backend:local ./backend
docker build -t foodgram-frontend:local -f ./frontend/Dockerfile .

helm upgrade --install foodgram ./foodgram \
  --namespace foodgram \
  --create-namespace \
  --set-string backend.image=foodgram-backend:local \
  --set-string frontend.image=foodgram-frontend:local \
  --set global.tls.enabled=false \
  --wait \
  --timeout 10m

kubectl get pods -n foodgram
kubectl get svc -n foodgram
```

## Как передать kubeconfig в GitHub

Посмотри текущий kubeconfig:

```bash
kubectl config view --raw
```

Скопируй вывод и вставь его в GitHub secret `KUBE_CONFIG`.

Для локального Docker Desktop это подойдет только если GitHub runner имеет доступ к твоему локальному Kubernetes. Обычно GitHub-hosted runner не имеет такого доступа, поэтому для полной проверки лучше использовать свой runner внутри того же кластера или рядом с ним.

## Часть 2. Подключение своего runner через Helm chart

Runner разворачивается через официальный Helm chart GitHub Actions Runner Controller.

Установи controller:

```bash
helm upgrade --install arc \
  --namespace arc-systems \
  --create-namespace \
  -f infra/github-runner/controller-values.yaml \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller
```

Создай token в GitHub:

```text
GitHub -> Settings -> Developer settings -> Personal access tokens
```

Token должен иметь доступ к репозиторию.

Создай secret для runner:

```bash
kubectl create namespace arc-runners

kubectl create secret generic github-config-secret \
  --namespace arc-runners \
  --from-literal=github_token='<github-token>'
```

Установи runner scale set:

```bash
helm upgrade --install foodgram-runner-set \
  --namespace arc-runners \
  --create-namespace \
  -f infra/github-runner/runner-scale-set-values.yaml \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set
```

Проверь runner:

```bash
kubectl get pods -n arc-systems
kubectl get pods -n arc-runners
```

В GitHub открой:

```text
Settings -> Actions -> Runners
```

Там должен появиться runner `foodgram-runner-set`.

## Как запустить pipeline на своем runner

1. Открой GitHub repository.
2. Перейди в `Actions`.
3. Запусти workflow `Self-hosted Runner Check`.
4. Если он прошел успешно, добавь repository variable:

```text
CI_RUNNER_LABEL=foodgram-runner-set
```

5. Запусти workflow `Release, Build and Deploy`.

## Что показать преподавателю

Покажи эти файлы:

- `.releaserc.json`
- `.github/workflows/release-deploy.yml`
- `.github/workflows/runner-check.yml`
- `infra/github-runner/controller-values.yaml`
- `infra/github-runner/runner-scale-set-values.yaml`
- `docs/ci-cd.md`

Покажи в GitHub Actions:

- успешный запуск `Release, Build and Deploy`;
- созданный semantic-release тег;
- опубликованные Docker-образы в GHCR;
- успешный запуск `Self-hosted Runner Check` на runner `foodgram-runner-set`.

Покажи в Kubernetes:

```bash
kubectl get pods -n foodgram
kubectl get pods -n arc-runners
```
