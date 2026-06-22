# CommerceX (sMart) — ML-Powered E-Commerce Platform

A full-stack e-commerce platform connecting customers, retailers, and wholesalers, with JWT authentication, a complete shopping/order/payment flow, and ML-powered product recommendations and semantic search. Originally built as an Object-Oriented Programming course project.

## Repository Layout

```
.
├── frontend/          React + TypeScript SPA (Vite, Tailwind CSS)
├── oopsProject/       FastAPI backend (the "real" production-style API)
├── simple_backend.py  Standalone mock FastAPI backend with in-memory data,
│                      useful for frontend development without a database
├── QUICKSTART.md      Combined quick-start guide for both apps
├── SERVER_STATUS.md   Notes on server setup/status
└── START_SERVERS.md   Instructions for starting both servers together
```

There are two backend options:

- **`oopsProject/`** — the full FastAPI application with SQLAlchemy models, repositories/services, Alembic migrations, Celery tasks, and ML modules. This is the real backend.
- **`simple_backend.py`** — a single-file FastAPI app with mock/in-memory data (no database required), intended for quickly running the frontend against a fake API while the full backend is still in progress.

## Tech Stack

### Frontend (`frontend/`)
- React 19 + TypeScript, built with Vite
- Tailwind CSS for styling
- Zustand for state management
- React Router v7 for routing
- TanStack React Query + Axios for data fetching
- React Hook Form + Zod for form validation
- Lucide React (icons), React Hot Toast (notifications)

### Backend (`oopsProject/`)
- FastAPI (async) on Python 3.10+
- SQLAlchemy 2.0 (async) with SQLite (dev) or PostgreSQL (prod) — Alembic for migrations
- Redis for caching and rate limiting; Celery for background tasks
- JWT auth (python-jose) with bcrypt password hashing
- Razorpay (payments), Twilio (SMS), SendGrid/SMTP (email), Google/Facebook OAuth
- MinIO (S3-compatible object storage)

### ML Stack
- scikit-learn — collaborative filtering / recommendations
- sentence-transformers — semantic product search
- transformers, XGBoost/LightGBM, Prophet — NLP, ranking, demand forecasting

## Features

- **Auth**: registration, login, JWT access/refresh tokens, role-based access (Customer / Retailer / Wholesaler / Admin)
- **Catalog**: product CRUD, categories, semantic search, filtering, featured products
- **Shopping**: cart, wishlist, multi-seller support, real-time stock validation
- **Orders & Payments**: full order lifecycle, tracking, Razorpay + COD, refunds
- **Reviews & Ratings**: 1–5 star reviews with verified-purchase badges
- **Notifications**: in-app notifications, WebSocket live updates
- **Admin**: analytics dashboard, sales/revenue reports, inventory management
- **ML**: personalized recommendations, "similar products", trending items, semantic search

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- PostgreSQL 14+ and Redis (only required for the full `oopsProject` backend in production-like mode — SQLite works for local dev without them)

### 1. Backend (full API — `oopsProject/`)

```bash
cd oopsProject
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env   # then edit .env with your own settings/secrets
alembic upgrade head
uvicorn app.main:app --reload
```

API available at `http://localhost:8000` — interactive docs at `http://localhost:8000/docs`.

### 1b. Backend (mock API — `simple_backend.py`)

For quick frontend iteration without setting up a database:

```bash
pip install fastapi uvicorn pyjwt bcrypt
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")  # Windows: set SECRET_KEY=...
uvicorn simple_backend:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_URL if not using the default
npm run dev
```

App available at `http://localhost:5173`.

See [QUICKSTART.md](QUICKSTART.md) for a more detailed walkthrough and [START_SERVERS.md](START_SERVERS.md) for running both servers together.

## Configuration

Both apps load configuration from `.env` files (never committed — see `.gitignore`). Copy the corresponding `.env.example` in each directory and fill in real values:

- `oopsProject/.env.example` — `SECRET_KEY`, database URL, Redis, MinIO, email/SMS providers, payment gateway, OAuth client secrets, ML settings
- `frontend/.env.example` — `VITE_API_URL`

**Never commit a populated `.env` file or hardcode secrets in source.** Generate a strong `SECRET_KEY` with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Testing

```bash
cd oopsProject
pytest                          # run all tests
pytest --cov=app --cov-report=html   # with coverage
```

## License

Educational project — built for an Object-Oriented Programming course.
