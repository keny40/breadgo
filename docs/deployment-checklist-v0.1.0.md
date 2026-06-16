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

- Build command: none required for the current FastAPI service.
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
BACKEND_CORS_ORIGINS=https://your-frontend-url.example.com
```

Production notes:

- `JWT_SECRET_KEY` must be generated securely and must not use the local demo default.
- `BACKEND_CORS_ORIGINS` must include the deployed Vercel frontend URL.
- If multiple origins are needed, separate them with commas.

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
NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.example.com
```

Local development can continue using:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

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

The local `scripts/smoke_test.py` currently targets `http://localhost:8000`. For deployed environments, either run manual verification or adapt the script to accept a deployed base URL before using it against production-like services.

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
