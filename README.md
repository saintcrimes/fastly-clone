# Fastly Clone — FastAPI

A full-stack clone of [fastly.com](https://www.fastly.com)'s signup and authentication flow, built with **FastAPI**. It replicates the sign-up experience end to end: account creation, email verification, JWT-based authentication, password reset, and disposable-email filtering — all backed by PostgreSQL, Redis, and a Jinja2-templated mail system.

This project was built as a hands-on exercise in production-style backend architecture: proper auth flows, background email tasks, rate limiting, and clean separation between routers, schemas, and services.

---

## ✨ Features

- **Sign up / Sign in** with hashed passwords (bcrypt)
- **Email verification** via signed tokens, sent through a styled HTML template
- **Password reset** flow with short-lived reset links
- **JWT authentication** with access tokens stored in HTTP-only cookies
- **Disposable email detection** — blocks throwaway/temp-mail domains at signup, backed by Redis
- **Rate limiting** on sensitive endpoints (e.g. login attempts)
- **Async SQLAlchemy** models with Alembic migrations
- **Background email delivery** via FastAPI's `BackgroundTasks`, so requests don't block on SMTP

---

## 🛠 Tech Stack

| Layer          | Technology                     |
|----------------|---------------------------------|
| Framework      | FastAPI                        |
| Database       | PostgreSQL + SQLAlchemy (async) |
| Migrations     | Alembic                        |
| Auth           | JWT (via `authx`)               |
| Caching        | Redis                          |
| Email          | `fastapi-mail` (Jinja2 templates) |
| Password hashing | bcrypt                       |
| Templating (frontend) | Jinja2 + plain HTML/CSS/JS |

---

## 📁 Project Structure

```
fastly/
├── src/
│   ├── db/
│   │   ├── models/        # SQLAlchemy models
│   │   ├── seeders/       # Seed data scripts
│   │   ├── base.py
│   │   └── seed.py
│   ├── mailsystem/
│   │   ├── config.py      # Mail connection config
│   │   └── mail.py        # Message creation, disposable-email checker
│   ├── migrations/        # Alembic migration scripts
│   ├── routers/
│   │   ├── authentication.py
│   │   └── sign_up.py
│   ├── schemas/           # Pydantic request/response models
│   ├── templates/
│   │   └── mail/          # HTML email templates
│   ├── utils/
│   └── main.py            # App entrypoint, lifespan, router registration
├── alembic.ini
├── Dockerfile
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (local instance or hosted)
- An SMTP-capable email account (e.g. Gmail with an App Password)

### 1. Clone the repository

```bash
git clone https://github.com/saintcrimes/fastly-clone.git
cd fastly-clone
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and fill in your own values:

```bash
cp .env.example .env
```

Then edit `.env` with your actual database URL, JWT secret, mail credentials, and Redis URL. See `.env.example` for the full list of required variables.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start Redis

Make sure a Redis instance is running and reachable at the URL set in `.env` (defaults to `redis://localhost:6379/0`).

### 7. Run the app locally

```bash
uvicorn main:app --host localhost --port 8000 --reload
```

The app will be available at **http://localhost:8000**, with interactive API docs at **http://localhost:8000/docs**.

---

## 🌐 Running on a Server

For production, drop `--reload` (it's a development-only flag that adds overhead and isn't meant for live traffic) and bind to all interfaces so the app is reachable externally:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Typically you'd run this behind a reverse proxy (e.g. Nginx) handling HTTPS termination, and manage the process with something like `systemd` or a process manager such as `pm2` / `supervisor`, rather than running uvicorn directly in a terminal.

### Using Docker

A `Dockerfile` is included. Build and run with:

```bash
docker build -t fastly-clone .
docker run -d -p 8000:8000 --env-file .env fastly-clone
```

---

## 🔑 Environment Variables

See [`.env.example`](./.env.example) for the complete list. Key variables include:

- `DATABASE_URL` — PostgreSQL connection string
- `JWT_SECRET_KEY` — secret used to sign access tokens (use a strong, random 32+ character value)
- `MAIL_USERNAME` / `MAIL_PASSWORD` — SMTP credentials for sending verification and reset emails
- `REDIS_URL` — Redis connection string
- `DOMAIN` — base domain used to build verification/reset links

---

## 📌 Notes

- This project is for **educational purposes** — it clones the UI/UX of fastly.com's signup flow but is not affiliated with or endorsed by Fastly, Inc.
- Passwords are hashed with bcrypt before storage; raw passwords are never persisted or logged.
- Email verification and password reset tokens are short-lived and single-purpose.

---

## 📄 License

💖This project is open source and available for learning purposes.