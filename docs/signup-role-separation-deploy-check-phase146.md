# Phase 146 Signup Role Separation Deployment Check

## Purpose

Verify that Phase 145 customer signup, merchant application, and admin approval/rejection flows are deployed and working in production.

## Deployment Targets

- Frontend: `https://breadgo.vercel.app`
- Backend: `https://breadgo-api.onrender.com`
- Migration: `202606180024_create_merchant_applications.py`
- New table: `merchant_applications`

## Deployment State

- Render backend is serving Phase 145 endpoints.
- Vercel frontend is serving Phase 145 signup/application screens.
- Backend health: PASS
  - `GET https://breadgo-api.onrender.com/health`
  - Result: `200`, `{"status":"ok"}`

## Production Migration Verification

Production migration is considered applied because the production backend successfully created, listed, approved, and rejected `merchant_applications` records.

Checked production flow:

- `POST /api/v1/merchants/apply`: PASS, returned `201`, status `PENDING`
- `GET /api/v1/admin/merchant-applications`: PASS, returned `200`
- `GET /api/v1/admin/merchant-applications/{application_id}`: PASS, returned `200`
- `POST /api/v1/admin/merchant-applications/{application_id}/approve`: PASS, returned `APPROVED`
- `POST /api/v1/admin/merchant-applications/{application_id}/reject`: PASS, returned `REJECTED`

No additional schema changes were made in Phase 146.

## Frontend Verification

- `/register`: PASS
  - Customer signup copy is visible.
  - Google button is visible and enabled.
  - Merchant application CTA is visible.
  - Admin approval boundary copy is visible.
- `/merchant/apply`: PASS
  - Merchant application screen is visible.
  - Application/approval copy is visible.
  - No Google signup button is shown on the merchant application page.
- `/login`: PASS
  - Google login button remains visible and enabled.

No page errors, OAuth-related console errors, or failed signup/application network requests were observed during browser verification.

## Google OAuth Verification

- `GET https://breadgo-api.onrender.com/api/v1/auth/google/status`: PASS
- Result: `enabled=true`
- Google OAuth remains customer-only.
- No Google Client Secret, token, or key was read or written in this phase.

## Role Boundary Verification

- `POST /api/v1/auth/register` with `role=merchant`: PASS, returned `403`
- `POST /api/v1/auth/register` with `role=admin`: PASS, returned `403`
- Existing merchant user calling admin application list: PASS, returned `403`
- Customer without merchant profile calling `/api/v1/merchants/me`: PASS, returned `404`

## Existing Login and Core Flow Verification

Production checks:

- `customer@breadgo.test / 12345678`: PASS
- `merchant@breadgo.test / 12345678`: PASS
- `admin@breadgo.test / 12345678`: PASS
- Region products API: PASS
- Admin summary API: PASS

Local regression checks:

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## Production Alembic Note

If a future Render deployment does not show the merchant application endpoints or the production API returns a table-missing error, run the backend migration in the Render environment:

```bash
python -m alembic upgrade head
```

Do not print or copy Render secrets while running operational commands.

## Secret Handling

- No secret/token/key values were printed.
- Google Client Secret was not read or documented.
- No DB credentials were documented.
- No new tag or GitHub Release was created.
