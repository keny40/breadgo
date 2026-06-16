# BreadGo v0.1.0 Deployment Checklist

This document prepares BreadGo for deployment. It does not mean the app has been deployed.

## Before Deployment

- Confirm local backend verification passes.
- Confirm frontend lint and build pass.
- Confirm no real secrets are committed.
- Confirm the production database is a managed PostgreSQL instance.
- Confirm demo seed accounts are not used as production accounts.
- Confirm the production admin user creation process is secure and private.

## Backend Setup

Recommended target: Render or a similar Python web service.

- Python version: `3.11` or newer.
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
BACKEND_CORS_ORIGINS=["https://your-vercel-app.vercel.app"]
```

Production notes:

- `JWT_SECRET_KEY` must be generated securely and must not use the local demo default.
- `BACKEND_CORS_ORIGINS` must include the deployed Vercel frontend URL.
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
BACKEND_CORS_ORIGINS=["https://your-vercel-app.vercel.app"]
```

9. Deploy the service.
10. Verify health check:

```text
https://your-render-backend-url.onrender.com/health
```

11. Verify Swagger docs:

```text
https://your-render-backend-url.onrender.com/docs
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
NEXT_PUBLIC_API_BASE_URL=https://your-render-backend-url.onrender.com
```

Local development can continue using:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

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
NEXT_PUBLIC_API_BASE_URL=https://your-render-backend-url.onrender.com
```

6. Deploy the frontend.
7. Verify the homepage.
8. Verify `/demo`.
9. Verify `/products`.
10. After the Vercel URL is known, update Render `BACKEND_CORS_ORIGINS` to include that URL and redeploy/restart the backend.

## Post-Deployment Verification

After deployment:

1. Open the deployed frontend URL.
2. Confirm the home page and `/demo` page load.
3. Confirm the frontend can call backend `/health`.
4. Register or log in with a non-demo production test account.
5. Confirm region product discovery loads data.
6. Confirm reservation creation works.
7. Confirm mock payment flow works.
8. Confirm merchant pickup confirmation works.
9. Confirm admin dashboard is protected.

The local `scripts/smoke_test.py` targets `http://localhost:8000` by default. It can also target a deployed backend when `BREADGO_API_BASE_URL` is set:

```powershell
cd backend
$env:BREADGO_API_BASE_URL="https://your-render-backend-url.onrender.com"
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
- No real map or GPS search.
- No email verification.
- Demo seed accounts should not be used in production.
- Admin user must be created securely.
- No production monitoring, alerting, or log aggregation has been configured yet.
