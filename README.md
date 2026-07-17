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
bash<br>
brew install postgresql@15<br>
brew services start postgresql@15<br>
Ubuntu:<br>

bash<br>
sudo apt update<br>
sudo apt install postgresql postgresql-contrib<br>
sudo service postgresql start<br>
#### 2. Создание БД и пользователя

bash<br>
sudo -u postgres psql<br>
sql<br>
CREATE USER payment_user WITH PASSWORD 'payment_pass';<br>
CREATE DATABASE payment_db OWNER payment_user;<br>
GRANT ALL PRIVILEGES ON DATABASE payment_db TO payment_user;<br>
\q<br>
#### 3. Настройка проекта

bash<br>
# Клонируем и переходим в папку
git clone <repository-url><br>
cd payment-system<br>

# Создаем виртуальное окружение
python -m venv venv<br>
source venv/bin/activate  # Linux/Mac<br>
# venv\Scripts\activate   # Windows

# Устанавливаем зависимости
pip install -r requirements.txt<br>
Создайте .env:<br>

env<br>
DB_HOST=localhost<br>
DB_PORT=5432<br>
DB_USER=payment_user<br>
DB_PASSWORD=payment_pass<br>
DB_NAME=payment_db<br>
DB_ECHO=False<br>

SECRET_KEY=your_secret_key<br>
JWT_SECRET=your_jwt_secret_key_here_change_in_production<br>
JWT_ALGORITHM=HS256<br>
JWT_ACCESS_EXP=3600<br>
JWT_REFRESH_EXP=86400<br>

ADMIN_EMAIL=admin@test.com<br>
ADMIN_PASSWORD=admin123<br>
ADMIN_FULL_NAME=Admin User<br>

USER_EMAIL=user@test.com<br>
USER_PASSWORD=user123<br>
USER_FULL_NAME=Test User<br>

#### 4. Миграции и запуск

bash<br>
# Применяем миграции
alembic upgrade head<br>

# Запускаем приложение
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload<br>
Приложение доступно: http://localhost:8000<br>
Swagger: http://localhost:8000/docs<br>

---

### Запуск с Docker Compose

#### 1. Запуск

bash<br>
# Сборка и запуск
docker-compose up -d --build<br>

#### 2. Доступ

API: http://localhost:8000<br>
Swagger: http://localhost:8000/docs<br>
PostgreSQL: localhost:5433 (пароль: payment_pass)<br>
#### 3. Остановка

bash<br>
docker-compose down<br>
API Эндпоинты<br>

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

Swagger:<br>

POST /api/auth/login<br>
Body: {"email":"admin@test.com","password":"admin123"}<br>
Скопировать access_token<br>
curl:<br>

bash<br>
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \<br>
  -H "Content-Type: application/json" \<br>
  -d '{"email":"admin@test.com","password":"admin123"}' \<br>
  | jq -r '.access_token')<br>

#### Шаг 2: Генерация подписи

Swagger:<br>

Нажать "Authorize", ввести Bearer <admin_token><br>
POST /api/webhook/generate-signature<br>
Body: {"user_id": 1, "account_id": 1, "amount": 100.50}<br>
Скопировать весь payload из ответа<br>
curl:<br>

bash<br>
curl -X POST http://localhost:8000/api/webhook/generate-signature \<br>
  -H "Authorization: Bearer $ADMIN_TOKEN" \<br>
  -H "Content-Type: application/json" \<br>
  -d '{"user_id": 1, "account_id": 1, "amount": 100.50}'<br>

#### Шаг 3: Отправка вебхука

Swagger:<br>

POST /api/webhook/payment<br>
Вставить скопированный payload<br>
curl:<br>

bash<br>
curl -X POST http://localhost:8000/api/webhook/payment \<br>
  -H "Content-Type: application/json" \<br>
  -d '{<br>
    "transaction_id": "7f8d3a2b-1c4e-5f6a-7b8c-9d0e1f2a3b4c",<br>
    "user_id": 1,<br>
    "account_id": 1,<br>
    "amount": 100.50,<br>
    "signature": "abc123def456..."<br>
  }'<br>

#### Шаг 4: Проверка баланса

Swagger:<br>

Авторизоваться как пользователь (user@test.com / user123)<br>
GET /api/users/me/accounts - баланс должен увеличиться<br>
curl:<br>

bash<br>
USER_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \<br>
  -H "Content-Type: application/json" \<br>
  -d '{"email":"user@test.com","password":"user123"}' \<br>
  | jq -r '.access_token')<br>

curl -X GET http://localhost:8000/api/users/me/accounts \<br>
  -H "Authorization: Bearer $USER_TOKEN"<br>

--- 

### Примечания

#### Формирование подписи

Подпись формируется через SHA256:<br>

text<br>
{account_id}{amount}{transaction_id}{user_id}{secret_key}<br>
Пример:<br>

python<br>
import hashlib<br>

account_id = 1<br>
amount = 100<br>
transaction_id = "5eae174f-7cd0-472c-bd36-35660f00132b"<br>
user_id = 1<br>
secret_key = "gfdmhghif38yrf9ew0jkf32"<br>

signature_string = f"{account_id}{amount}{transaction_id}{user_id}{secret_key}"<br>
signature = hashlib.sha256(signature_string.encode()).hexdigest()<br>
```7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8```<br>

#### Особенности

- **Argon2** — безопасное хеширование паролей, без ограничений по длине
- **Автоматическое создание счета** — при первом платеже пользователя
- **Защита от дублирования** — уникальность `transaction_id` для транзакций
- **JWT токены** — для аутентификации пользователей
- **Разделение ролей** — пользователь (`user`) и администратор (`admin`)
- **Структура проекта** — организована по модульному принципу (чистая архитектура)