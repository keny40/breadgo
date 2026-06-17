# BreadGo MVP

BreadGo is a local food rescue marketplace MVP for bakery leftovers. The current MVP includes region and location-based discovery, customer reservations, mock payment, merchant product/image management, QR-style pickup confirmation, and admin monitoring.

## Deployed URLs

- Frontend: [https://breadgo.vercel.app](https://breadgo.vercel.app)
- Backend: [https://breadgo-api.onrender.com](https://breadgo-api.onrender.com)
- Backend health check: [https://breadgo-api.onrender.com/health](https://breadgo-api.onrender.com/health)
- Backend Swagger docs: [https://breadgo-api.onrender.com/docs](https://breadgo-api.onrender.com/docs)

Render free instances may sleep after inactivity. The first backend request can be slow while the service wakes up.

## Completed MVP Features

- JWT authentication with role-based redirects and logged-in email display.
- Demo seed accounts for customer, merchant, and admin flows.
- Merchant onboarding, store management, and product management.
- Product representative image URL support and Vercel Blob image upload.
- Region-based product discovery and browser geolocation nearby discovery.
- Customer reservation flow with pickup code.
- Mock payment flow with card, KakaoPay, and NaverPay demo methods.
- Customer reservation and payment history pages.
- Merchant pickup confirmation by pickup code.
- Admin dashboard for users, merchants, stores, products, reservations, and payments.
- Backend smoke test for the full MVP happy path.

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

Customer:

1. Login as `customer@breadgo.test`.
2. Open `/products`.
3. Select a region or use `내 위치로 찾기`.
4. Reserve a product.
5. Complete mock payment.
6. Check pickup code, reservation status, and payment status in `/my-reservations` and `/my-payments`.

Merchant:

1. Login as `merchant@breadgo.test`.
2. Open `/merchant`, `/merchant/stores`, and `/merchant/products`.
3. Create or update stores and products.
4. Upload or paste a product image URL.
5. Confirm pickup from `/merchant/pickup`.

Admin:

1. Login as `admin@breadgo.test`.
2. Open `/admin`.
3. Review users, merchants, stores, products, reservations, payments, and summary cards.

## Known Limitations

- No real payment gateway.
- Mock payment only.
- No real map UI yet.
- No production email verification.
- Admin role is assigned by seed data or SQL.
- Render free instances may sleep and need a warm-up request.

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
BACKEND_CORS_ORIGINS=["https://breadgo.vercel.app"]
PYTHON_VERSION=3.12.8
```

`BACKEND_CORS_ORIGINS` must include the deployed frontend URL. JSON array strings and comma-separated values are both supported.

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
NEXT_PUBLIC_API_BASE_URL=https://breadgo-api.onrender.com
BLOB_READ_WRITE_TOKEN=replace-with-vercel-blob-token
```

For local development, keep:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

`BLOB_READ_WRITE_TOKEN` is required only for actual product image file uploads through Vercel Blob. Local development and deployed demos can still use the manual `image_url` input without a Blob token.

### Database Migration Steps

1. Create a managed PostgreSQL database.
2. Set `DATABASE_URL` on the backend service.
3. Run `python -m alembic upgrade head`.
4. Start or restart the backend service.
5. Verify `/health` and Swagger load on the deployed backend.

### Smoke Test Limitations

The smoke test script targets the local backend at `http://localhost:8000` by default. For a safe demo deployment, set `BREADGO_API_BASE_URL` before running it against Render.

### Production Limitations

- No real payment gateway.
- Mock payment only.
- No real PG integration.
- No real map UI yet.
- No production email verification.
- Demo seed accounts should not be used in production.
- Admin user must be created securely.
- Production monitoring and alerting are not configured yet.

See [docs/deployment-checklist-v0.1.0.md](docs/deployment-checklist-v0.1.0.md) for the deployment readiness checklist.

## Actual Deployment

This section prepares the exact Vercel + Render setup. Do not commit real secrets.

### Render Backend

1. Create a managed PostgreSQL database.
2. Copy the database connection string.
3. Create a Render Web Service from [https://github.com/keny40/breadgo](https://github.com/keny40/breadgo).
4. Set root directory:

```text
backend
```

5. Set build command:

```bash
pip install -e . && python -m alembic upgrade head
```

If editable installs are unavailable, use:

```bash
pip install -r requirements.txt && python -m alembic upgrade head
```

6. Set start command:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

7. Set Render environment variables:

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
JWT_SECRET_KEY=<secure random secret, at least 32 characters>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["https://breadgo.vercel.app"]
PYTHON_VERSION=3.12.8
```

Local CORS example:

```text
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

8. Verify:

```text
https://breadgo-api.onrender.com/health
https://breadgo-api.onrender.com/docs
```

Do not run `python scripts/seed_demo.py` automatically in production. For a temporary demo deployment only, it can be run manually after confirming the environment is not production.

### Vercel Frontend

1. Import [https://github.com/keny40/breadgo](https://github.com/keny40/breadgo) into Vercel.
2. Set root directory:

```text
frontend
```

3. Set install command:

```bash
npm install
```

4. Set build command:

```bash
npm run build
```

5. Set Vercel environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://breadgo-api.onrender.com
BLOB_READ_WRITE_TOKEN=replace-with-vercel-blob-token
```

For local development, keep:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

6. Deploy.
7. Verify the homepage, `/demo`, and `/products`.
8. Copy the final Vercel URL into Render `BACKEND_CORS_ORIGINS`.

Vercel Blob is required for actual product image uploads from `/merchant/products`. Create a Vercel Blob store, copy its read/write token into `BLOB_READ_WRITE_TOKEN`, and redeploy the frontend. Without this token, merchants can still paste a direct image URL manually.

### Deployed Smoke Test

The smoke test uses `http://localhost:8000` by default. To point it at Render:

```powershell
cd backend
$env:BREADGO_API_BASE_URL="https://breadgo-api.onrender.com"
python scripts/smoke_test.py
```

The deployed smoke test expects demo accounts and seeded demo products. Use it only against a safe demo deployment.

### Common Deployment Errors

- CORS error: add `https://breadgo.vercel.app` to `BACKEND_CORS_ORIGINS` on Render and restart the backend.
- `DATABASE_URL` error: confirm the URL uses `postgresql+psycopg://` and points to the managed PostgreSQL database.
- `401` token issue: log out and log in again after changing `JWT_SECRET_KEY` or backend URL.
- No products: migrations may have run but demo seed data was not loaded in the demo environment.
- Migration not run: run `python -m alembic upgrade head` against the Render environment before testing APIs.
- Image upload not configured: add `BLOB_READ_WRITE_TOKEN` to Vercel frontend environment variables and redeploy.
- Slow first request: Render free instances may be waking up.
