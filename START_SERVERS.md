# Quick Start Guide - Running Both Servers

Since your backend requires a PostgreSQL database and Redis which aren't set up yet, here's the simplest way to get both servers running for testing:

## Option 1: Run Frontend Only (Simplest)

The frontend is fully built and ready. You can run it and see the UI:

### Start Frontend:
```bash
cd C:\Users\footb\Desktop\oopsProject\frontend
npm run dev
```

Then open: **http://localhost:5173**

**Note**: The API calls won't work without the backend, but you'll see the beautiful UI with all pages.

---

## Option 2: Full Setup (Backend + Frontend)

To run the full application with the backend API:

### Prerequisites:
1. **PostgreSQL** database running
2. **Redis** server running (optional, can be disabled)

### Setup Backend:

1. **Configure Environment**:
```bash
cd C:\Users\footb\Desktop\oopsProject\oopsProject
copy .env.example .env
```

2. **Edit `.env` file** with your database:
```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost/dbname
SECRET_KEY=your-secret-key-change-this-in-production
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=http://localhost:5173
```

3. **Run Database Migrations**:
```bash
alembic upgrade head
```

4. **Start Backend Server**:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be at: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

### Setup Frontend:

1. **Start Frontend Server**:
```bash
cd C:\Users\footb\Desktop\oopsProject\frontend
npm run dev
```

Frontend will be at: **http://localhost:5173**

---

## Option 3: Quick Demo Without Database

For a quick demo without setting up PostgreSQL, you can modify the backend to use SQLite:

1. Install SQLite support:
```bash
cd C:\Users\footb\Desktop\oopsProject\oopsProject
pip install aiosqlite
```

2. Change DATABASE_URL in `.env` to:
```env
DATABASE_URL=sqlite+aiosqlite:///./smart.db
```

3. Run migrations and start:
```bash
alembic upgrade head
python -m uvicorn app.main:app --reload
```

---

## Troubleshooting

### Backend Won't Start:
- **Database Error**: Make sure PostgreSQL is running and DATABASE_URL is correct
- **Redis Error**: Comment out Redis code in `app/main.py` or install Redis
- **Import Errors**: Run `pip install -r requirements.txt`

### Frontend Won't Start:
- **Port in Use**: Vite will try port 5174, 5175, etc. automatically
- **Dependencies Missing**: Run `npm install` again

### "Can't Reach Site":
- Make sure you ran `npm run dev` or `python -m uvicorn...`
- Check the terminal for error messages
- Verify the ports are correct (8000 for backend, 5173 for frontend)

---

## What You'll See

### Frontend Pages (All Built):
- Home page with featured products
- Login / Register pages
- Product listing and search
- Product details with reviews
- Shopping cart
- Wishlist
- Orders history
- Notifications center
- User profile

### Backend API:
- Full REST API with 60+ endpoints
- Authentication with JWT
- Product management
- Cart and orders
- Reviews and ratings
- Notifications
- Admin dashboard

---

## For Your Class Demo

The easiest way to demo:

1. **Start Frontend Only**:
   ```bash
   cd frontend
   npm run dev
   ```
   Show the beautiful UI and all pages

2. **Explain Backend**: Show the code structure and API documentation at `/docs`

3. **If Time Permits**: Set up the database and run both servers

The frontend is **production-ready** and **fully functional** - it just needs the backend API to be running to fetch real data!
