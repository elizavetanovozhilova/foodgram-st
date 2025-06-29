# Foodgram - Платформа для обмена рецептами

## Описание проекта

**Foodgram** - это веб-приложение для обмена кулинарными рецептами. Пользователи могут создавать, просматривать и сохранять рецепты, подписываться на других авторов, формировать список покупок и многое другое.


## Развертывание проекта

### Предварительные требования

- Docker
- Docker Compose

### Инструкция по запуску

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd foodgram-st
   ```

2. **Создайте файл .env в папке infra:**
   ```bash
   cd infra
   touch .env
   ```

3. **Добавьте в .env следующие переменные:**
   ```env
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=
   POSTGRES_USER=
   POSTGRES_PASSWORD=
   DB_HOST=
   DB_PORT=
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

4. **Запустите проект через Docker Compose:**
   ```bash
   docker-compose up -d
   ```

5. **Примените миграции:**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

6. **Создайте суперпользователя (опционально):**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

7. **Загрузите тестовые данные (опционально):**
   ```bash
   docker-compose exec backend python manage.py import_data
   ```

### Доступ к приложению

- **Frontend:** http://localhost/
- **Backend API:** http://localhost/api
- **Admin панель:** http://localhost/admin



### API Endpoints

Основные эндпоинты API:

- `GET /api/recipes/` - список рецептов
- `POST /api/recipes/` - создание рецепта
- `GET /api/users/` - список пользователей
- `PUT /api/users/avatar/` - загрузка аватара
- `GET /api/ingredients/` - список ингредиентов
- `GET /api/tags/` - список тегов
