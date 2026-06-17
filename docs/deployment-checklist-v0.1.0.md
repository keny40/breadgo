# BreadGo v0.1.0 Deployment Checklist

This document tracks the current BreadGo MVP deployment on Vercel + Render and the checks required before and after each deployment.

## Current Deployed URLs

- Frontend: `https://breadgo.vercel.app`
- Backend: `https://breadgo-api.onrender.com`
- Backend health: `https://breadgo-api.onrender.com/health`
- Backend Swagger: `https://breadgo-api.onrender.com/docs`

Render free instances may sleep after inactivity. Allow the first request to warm up the backend.

## Before Deployment

- Confirm local backend verification passes.
- Confirm frontend lint and build pass.
- Confirm no real secrets are committed.
- Confirm the production database is a managed PostgreSQL instance.
- Confirm demo seed accounts are not used as production accounts.
- Confirm the production admin user creation process is secure and private.

## Backend Setup

Recommended target: Render or a similar Python web service.

- Python version: `3.12.8` recommended.
- Root directory: `backend`.
- Install command:

```bash
pip install -e .
```

- Alternative install command if Render prefers requirements files:

```bash
pip install -r requirements.txt
```

- Build command:

```bash
python -m alembic upgrade head
```

- Start command:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

- Local Windows development command remains:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

## Backend Environment Variables

Set these in the backend hosting provider:

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
JWT_SECRET_KEY=<secure random secret, at least 32 characters>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["https://breadgo.vercel.app"]
PYTHON_VERSION=3.12.8
```

Production notes:

- `JWT_SECRET_KEY` must be generated securely and must not use the local demo default.
- `BACKEND_CORS_ORIGINS` must include `https://breadgo.vercel.app`.
- `BACKEND_CORS_ORIGINS` accepts JSON array strings or comma-separated values.
- Local development can use `["http://localhost:3000","http://127.0.0.1:3000"]`.

## Render Deployment Steps

1. Create a PostgreSQL database on Render or another managed PostgreSQL provider.
2. Copy the external PostgreSQL connection string.
3. Convert the connection string to the SQLAlchemy psycopg format if needed:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
```

4. Create a Render Web Service from `https://github.com/keny40/breadgo`.
5. Set root directory to `backend`.
6. Set build command:

```bash
pip install -e . && python -m alembic upgrade head
```

7. Set start command:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

8. Set required environment variables:

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
JWT_SECRET_KEY=<secure random secret, at least 32 characters>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["https://breadgo.vercel.app"]
PYTHON_VERSION=3.12.8
```

9. Deploy the service.
10. Verify health check:

```text
https://breadgo-api.onrender.com/health
```

11. Verify Swagger docs:

```text
https://breadgo-api.onrender.com/docs
```

Do not run `python scripts/seed_demo.py` automatically in production. For a temporary demo deployment only, run it manually after confirming that demo accounts are acceptable for that environment.

## Database Setup

Recommended target: managed PostgreSQL.

1. Create a managed PostgreSQL database.
2. Copy the connection string.
3. Use the SQLAlchemy psycopg driver format:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
```

4. Set it as `DATABASE_URL` in the backend service.
5. Run migrations:

```bash
python -m alembic upgrade head
```

Alembic reads `DATABASE_URL` through the backend settings module, so the same environment variable drives app runtime and migrations.

## Frontend Setup

Recommended target: Vercel.

- Root directory: `frontend`.
- Install command:

```bash
npm install
```

- Build command:

```bash
npm run build
```

- Environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://breadgo-api.onrender.com
BLOB_READ_WRITE_TOKEN=replace-with-vercel-blob-token
```

Local development can continue using:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

`BLOB_READ_WRITE_TOKEN` is required for actual image file upload through Vercel Blob. Manual product image URL input continues to work without Blob storage.

## Vercel Deployment Steps

1. Import `https://github.com/keny40/breadgo` into Vercel.
2. Set root directory to `frontend`.
3. Set install command:

```bash
npm install
```

4. Set build command:

```bash
npm run build
```

5. Set environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://breadgo-api.onrender.com
BLOB_READ_WRITE_TOKEN=replace-with-vercel-blob-token
```

6. Create or connect a Vercel Blob store for product image uploads.
7. Deploy the frontend.
8. Verify the homepage at `https://breadgo.vercel.app`.
9. Verify `/demo`.
10. Verify `/products`.
11. Verify `/my-reservations` and `/my-payments`.
12. Verify `/merchant/products` can upload an image when `BLOB_READ_WRITE_TOKEN` is set.
13. Confirm Render `BACKEND_CORS_ORIGINS` includes `https://breadgo.vercel.app`.

## Post-Deployment Verification

After deployment:

1. Confirm backend `/health` works: `https://breadgo-api.onrender.com/health`.
2. Confirm Vercel frontend works: `https://breadgo.vercel.app`.
3. Confirm Swagger loads: `https://breadgo-api.onrender.com/docs`.
4. Confirm product API returns data:

```text
https://breadgo-api.onrender.com/api/v1/regions/products?sido=서울특별시&sigungu=강남구&dong=역삼동
```

5. Confirm customer demo flow: login → products → reserve → mock payment → pickup code → my reservations/payments.
6. Confirm merchant demo flow: login → dashboard → stores → products → image upload → pickup confirmation.
7. Confirm admin demo flow: login → admin dashboard → users/merchants/stores/products/reservations/payments.
8. Confirm image upload uses Vercel Blob and requires `BLOB_READ_WRITE_TOKEN`.
9. Confirm CORS includes `https://breadgo.vercel.app` in Render `BACKEND_CORS_ORIGINS`.

The local `scripts/smoke_test.py` targets `http://localhost:8000` by default. It can also target a deployed backend when `BREADGO_API_BASE_URL` is set:

```powershell
cd backend
$env:BREADGO_API_BASE_URL="https://breadgo-api.onrender.com"
python scripts/smoke_test.py
```

The smoke test expects demo accounts and seeded demo products. Do not run it against production unless that environment intentionally contains safe demo data.

## Rollback Notes

- Keep the previous deployed backend version available until migrations and smoke checks pass.
- If frontend deployment fails, roll back to the previous Vercel deployment.
- If backend deployment fails before migrations, roll back the service release without touching the database.
- If a migration succeeds but a backend release fails, review migration reversibility before attempting downgrade.
- Do not run demo seed data against production.

## Known Production Limitations

- Mock payment only.
- No real PG integration.
- No real map UI.
- No email verification.
- Demo seed accounts should not be used in production.
- Admin user must be created securely.
- No production monitoring, alerting, or log aggregation has been configured yet.
- Product image upload depends on Vercel Blob and requires `BLOB_READ_WRITE_TOKEN`.
- Render free instances may sleep and make the first request slow.
