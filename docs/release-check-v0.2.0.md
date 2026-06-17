# BreadGo v0.2.0 Release Check

Release target: BreadGo MVP deployed demo

Last updated: 2026-06-17

## Release Status

BreadGo v0.2.0 is the current deployed MVP checkpoint for customer, merchant, and admin demo flows.

## Deployed URLs

- Frontend: https://breadgo.vercel.app
- Backend: https://breadgo-api.onrender.com
- Health: https://breadgo-api.onrender.com/health
- Demo guide: https://breadgo.vercel.app/demo
- API diagnostics: https://breadgo.vercel.app/debug/api

## Demo Accounts

- Customer: `customer@breadgo.test` / `12345678`
- Merchant: `merchant@breadgo.test` / `12345678`
- Admin: `admin@breadgo.test` / `12345678`

## Completed Features

- Auth/register/login/logout
- Role-based redirects
- Navbar user email display
- Region product discovery
- Nearby product discovery
- Reservation flow
- Mock payment flow
- My reservations
- My payments
- Merchant dashboard
- Store management
- Product create/edit/hide/unhide
- Product image URL
- Product image upload with Vercel Blob
- Pickup code lookup
- Pickup confirmation
- Admin dashboard
- Demo guide

## Final Manual Test Checklist

### Customer

- [ ] Login
- [ ] Products
- [ ] Region search
- [ ] Nearby search
- [ ] Reserve product
- [ ] Mock payment
- [ ] Check pickup code
- [ ] My reservations
- [ ] My payments

### Merchant

- [ ] Login
- [ ] Merchant dashboard
- [ ] Stores
- [ ] Product registration
- [ ] Image upload
- [ ] Product edit
- [ ] Hide/unhide product
- [ ] Pickup code lookup
- [ ] Pickup confirm

### Admin

- [ ] Login
- [ ] Admin dashboard
- [ ] Users
- [ ] Merchants
- [ ] Stores
- [ ] Products
- [ ] Reservations
- [ ] Payments

## Environment Variable Checklist

### Render Backend

- [ ] `DATABASE_URL`
- [ ] `JWT_SECRET_KEY`
- [ ] `JWT_ALGORITHM`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES`
- [ ] `BACKEND_CORS_ORIGINS`
- [ ] `PYTHON_VERSION`

Recommended values:

```text
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["https://breadgo.vercel.app"]
PYTHON_VERSION=3.12.8
```

### Vercel Frontend

- [ ] `NEXT_PUBLIC_API_BASE_URL`
- [ ] `BLOB_READ_WRITE_TOKEN`

Recommended values:

```text
NEXT_PUBLIC_API_BASE_URL=https://breadgo-api.onrender.com
BLOB_READ_WRITE_TOKEN=replace-with-vercel-blob-token
```

## Diagnostics Page

`/debug/api` remains in the deployed frontend as a deployment diagnostics page.

Use it to verify:

- The frontend is reading the expected `NEXT_PUBLIC_API_BASE_URL`.
- The backend `/health` endpoint is reachable from the browser.
- Region product discovery works from the deployed frontend.

Do not use this page for secrets. It must not expose tokens, database URLs, or private environment values.

## Known Limitations

- Render free instance can sleep.
- Mock payment only, no real PG payment.
- Vercel Blob token required for image upload.
- No real POS integration yet.
- No AI demand prediction yet.
- No mobile native app yet.
- No review/point/notification system yet.

## Local Validation Commands

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

Backend:

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/smoke_test.py
```

## Deployed Browser Check

- [ ] https://breadgo.vercel.app/
- [ ] https://breadgo.vercel.app/demo
- [ ] https://breadgo.vercel.app/login
- [ ] https://breadgo.vercel.app/products
- [ ] https://breadgo.vercel.app/my-reservations
- [ ] https://breadgo.vercel.app/my-payments
- [ ] https://breadgo.vercel.app/merchant
- [ ] https://breadgo.vercel.app/merchant/stores
- [ ] https://breadgo.vercel.app/merchant/products
- [ ] https://breadgo.vercel.app/merchant/pickup
- [ ] https://breadgo.vercel.app/admin

## Release Decision

- [x] Frontend lint passed.
- [x] Frontend build passed.
- [x] Backend compile passed.
- [x] Alembic upgrade passed.
- [x] Smoke test passed.
- [x] Deployed frontend pages opened successfully.
- [x] Deployed backend health check passed.
- [x] Demo accounts are ready.
- [x] Known limitations are accepted for MVP release.

## Latest Verification Result

Checked on 2026-06-17.

Local validation:

- [x] `cd frontend && npm run lint`
- [x] `cd frontend && npm run build`
- [x] `cd backend && python -m compileall app scripts`
- [x] `cd backend && python -m alembic upgrade head`
- [x] `cd backend && python scripts/smoke_test.py`

Deployed backend:

- [x] `https://breadgo-api.onrender.com/health` returned `{"status":"ok"}`.
- [x] Region product API returned HTTP 200 with product data.

Deployed frontend pages:

- [x] `/`
- [x] `/demo`
- [x] `/login`
- [x] `/products`
- [x] `/my-reservations`
- [x] `/my-payments`
- [x] `/merchant`
- [x] `/merchant/stores`
- [x] `/merchant/products`
- [x] `/merchant/pickup`
- [x] `/admin`
- [x] `/debug/api`
