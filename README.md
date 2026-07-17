# Payment System API

Асинхронное REST API для управления платежами.

---

## Технологии

- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM
- **PostgreSQL** - база данных
- **Alembic** - миграции
- **Argon2** - хеширование паролей
- **JWT** - аутентификация
- **Docker Compose** - контейнеризация

---

## Запуск проекта

### Тестовые данные

| Роль | Email | Пароль |
|------|-------|--------|
| Администратор | admin@test.com | admin123 |
| Пользователь | user@test.com | user123 |

---

### Локальный запуск (без Docker)

#### 1. Установка PostgreSQL

**macOS:**
bash
brew install postgresql@15
brew services start postgresql@15
Ubuntu:

bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
#### 2. Создание БД и пользователя

bash
sudo -u postgres psql
sql
CREATE USER payment_user WITH PASSWORD 'payment_pass';
CREATE DATABASE payment_db OWNER payment_user;
GRANT ALL PRIVILEGES ON DATABASE payment_db TO payment_user;
\q
#### 3. Настройка проекта

bash
# Клонируем и переходим в папку
git clone <repository-url>
cd payment-system

# Создаем виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Устанавливаем зависимости
pip install -r requirements.txt
Создайте .env:

env
DB_HOST=localhost
DB_PORT=5432
DB_USER=payment_user
DB_PASSWORD=payment_pass
DB_NAME=payment_db
DB_ECHO=False

SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret_key_here_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_EXP=3600
JWT_REFRESH_EXP=86400

ADMIN_EMAIL=admin@test.com
ADMIN_PASSWORD=admin123
ADMIN_FULL_NAME=Admin User

USER_EMAIL=user@test.com
USER_PASSWORD=user123
USER_FULL_NAME=Test User

#### 4. Миграции и запуск

bash
# Применяем миграции
alembic upgrade head

# Запускаем приложение
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
Приложение доступно: http://localhost:8000
Swagger: http://localhost:8000/docs

---

### Запуск с Docker Compose

#### 1. Запуск

bash
# Сборка и запуск
docker-compose up -d --build

#### 2. Доступ

API: http://localhost:8000
Swagger: http://localhost:8000/docs
PostgreSQL: localhost:5433 (пароль: payment_pass)
#### 3. Остановка

bash
docker-compose down
API Эндпоинты

--- 

### Аутентификация

| Метод | Эндпоинт | Описание | Группа |
|-------|----------|----------|--------|
| POST | `/api/auth/login` | Вход (email/password) | Аутентификация |
| GET | `/api/users/me` | Данные пользователя | Пользовательские |
| GET | `/api/users/me/accounts` | Список счетов | Пользовательские |
| GET | `/api/users/me/transactions` | История платежей | Пользовательские |
| GET | `/api/admin/me` | Данные админа | Административные |
| POST | `/api/admin/users` | Создать пользователя | Административные |
| GET | `/api/admin/users` | Список пользователей | Административные |
| GET | `/api/admin/users/{id}` | Получить пользователя | Административные |
| PUT | `/api/admin/users/{id}` | Обновить пользователя | Административные |
| DELETE | `/api/admin/users/{id}` | Удалить пользователя | Административные |
| GET | `/api/admin/users/{id}/accounts` | Счета пользователя | Административные |
| POST | `/api/webhook/payment` | Обработка вебхука | Вебхук |
| POST | `/api/webhook/generate-signature` | Генерация подписи (только админ) | Вебхук |


--- 

### Тестирование вебхука пошагово

#### Шаг 1: Логин админа

Swagger:

POST /api/auth/login
Body: {"email":"admin@test.com","password":"admin123"}
Скопировать access_token
curl:

bash
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}' \
  | jq -r '.access_token')

#### Шаг 2: Генерация подписи

Swagger:

Нажать "Authorize", ввести Bearer <admin_token>
POST /api/webhook/generate-signature
Body: {"user_id": 1, "account_id": 1, "amount": 100.50}
Скопировать весь payload из ответа
curl:

bash
curl -X POST http://localhost:8000/api/webhook/generate-signature \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "account_id": 1, "amount": 100.50}'

#### Шаг 3: Отправка вебхука

Swagger:

POST /api/webhook/payment
Вставить скопированный payload
curl:

bash
curl -X POST http://localhost:8000/api/webhook/payment \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "7f8d3a2b-1c4e-5f6a-7b8c-9d0e1f2a3b4c",
    "user_id": 1,
    "account_id": 1,
    "amount": 100.50,
    "signature": "abc123def456..."
  }'

#### Шаг 4: Проверка баланса

Swagger:

Авторизоваться как пользователь (user@test.com / user123)
GET /api/users/me/accounts - баланс должен увеличиться
curl:

bash
USER_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"user123"}' \
  | jq -r '.access_token')

curl -X GET http://localhost:8000/api/users/me/accounts \
  -H "Authorization: Bearer $USER_TOKEN"

--- 

### Примечания

#### Формирование подписи

Подпись формируется через SHA256:

text
{account_id}{amount}{transaction_id}{user_id}{secret_key}
Пример:

python
import hashlib

account_id = 1
amount = 100
transaction_id = "5eae174f-7cd0-472c-bd36-35660f00132b"
user_id = 1
secret_key = "gfdmhghif38yrf9ew0jkf32"

signature_string = f"{account_id}{amount}{transaction_id}{user_id}{secret_key}"
signature = hashlib.sha256(signature_string.encode()).hexdigest()
# 7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8

#### Особенности

Argon2 (безопасный, нет ограничений по длине)
Автоматическое создание счета при первом платеже
Защита от дублирования транзакций (уникальность transaction_id)
JWT токены для аутентификации
Разделение ролей user/admin
Структура проекта