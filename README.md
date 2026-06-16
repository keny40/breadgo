# BreadGo MVP

BreadGo is a local food rescue marketplace MVP for bakery leftovers. The current local demo includes customer discovery, reservation, mock payment, merchant pickup confirmation, and admin monitoring.

## Local Demo

### Backend

```powershell
cd backend
.\.venv\Scripts\activate
python -m alembic upgrade head
python scripts/seed_demo.py
python -m uvicorn app.main:app --reload --port 8000
```

If you are not using a virtual environment, run the same Python commands from `backend` with your local Python environment.

### Smoke Test

Run this in another terminal while the backend is running:

```powershell
cd backend
python scripts/smoke_test.py
```

Expected result:

```text
[PASS] Health check
[PASS] Customer login
[PASS] Region products found
[PASS] Reservation created
[PASS] Mock payment confirmed
[PASS] Pickup confirmed
[PASS] Admin summary loaded
[PASS] BreadGo MVP smoke test completed
```

### Frontend

```powershell
cd frontend
npm run dev
```

Open:

[http://localhost:3000/demo](http://localhost:3000/demo)

## Demo Accounts

```text
admin@breadgo.test / 12345678
merchant@breadgo.test / 12345678
customer@breadgo.test / 12345678
```

## Recommended Demo Flow

1. Login as `customer@breadgo.test`.
2. Open `/products`.
3. Select `서울특별시 / 강남구 / 역삼동`.
4. Reserve a product.
5. Complete mock payment.
6. Check the pickup code in `/my-reservations`.
7. Login as `merchant@breadgo.test`.
8. Confirm pickup from `/merchant/pickup`.
9. Login as `admin@breadgo.test`.
10. Check `/admin`.

## Known Limitations

- No real payment gateway.
- Mock payment only.
- No real map or GPS search yet.
- No production email verification.
- Local PostgreSQL only.
- Admin role is assigned by seed data or SQL.
- No production deployment yet.

## Release Checklist

See [docs/release-check-v0.1.0.md](docs/release-check-v0.1.0.md) for the local demo release checkpoint.

## Deployment Preparation

BreadGo is prepared for deployment, but this repository does not deploy the app automatically.

Target deployment plan:

- Frontend: Vercel
- Backend: Render or similar Python web service
- Database: Managed PostgreSQL
- Local development: still runs without Docker

### Local Run Commands

Backend:

```powershell
cd backend
.\.venv\Scripts\activate
python -m alembic upgrade head
python scripts/seed_demo.py
python -m uvicorn app.main:app --reload --port 8000
```

Frontend:

```powershell
cd frontend
npm run dev
```

Open:

[http://localhost:3000/demo](http://localhost:3000/demo)

### Backend Deployment Checklist

- Python version: `3.11` or newer.
- Backend root directory: `backend`.
- Install command:

```bash
pip install -e .
```

- Build command: none required.
- Production start command:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

- Migration command:

```bash
python -m alembic upgrade head
```

Required backend environment variables:

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
JWT_SECRET_KEY=<secure random secret, at least 32 characters>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=https://your-frontend-url.example.com
```

`BACKEND_CORS_ORIGINS` must include the deployed frontend URL. Multiple origins can be comma-separated.

Alembic already reads the database URL from the backend settings module, so `python -m alembic upgrade head` uses `DATABASE_URL` when it is set.

### Frontend Deployment Checklist

- Frontend root directory: `frontend`.
- Install command:

```bash
npm install
```

- Build command:

```bash
npm run build
```

Required frontend environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.example.com
```

For local development, keep:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Database Migration Steps

1. Create a managed PostgreSQL database.
2. Set `DATABASE_URL` on the backend service.
3. Run `python -m alembic upgrade head`.
4. Start or restart the backend service.
5. Verify `/health` and Swagger load on the deployed backend.

### Smoke Test Limitations

The current smoke test script targets the local backend at `http://localhost:8000`. It is safe for local demo verification. For deployed environments, run manual checks or extend the script to accept a deployed base URL before using it outside local development.

### Production Limitations

- No real payment gateway.
- Mock payment only.
- No real PG integration.
- No real map or GPS search yet.
- No production email verification.
- Demo seed accounts should not be used in production.
- Admin user must be created securely.
- Production monitoring and alerting are not configured yet.

See [docs/deployment-checklist-v0.1.0.md](docs/deployment-checklist-v0.1.0.md) for the deployment readiness checklist.
