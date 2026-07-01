# Phase 147 Role Based Redirect and Navigation Check

## Purpose

Fix and verify the login redirect and navigation behavior by authenticated role.

- Customer accounts should land on the customer product flow.
- Merchant accounts should land on the merchant home.
- Admin accounts should land on the admin dashboard.
- Google OAuth remains customer-only.

## Changes

- Added a single `saveAuthSession(token, user)` helper so the frontend stores the auth token and user role together before emitting the auth state change event.
- Updated email login, customer registration, and Google OAuth callback to use the combined session save.
- Updated the global NavBar so a logged-in session with an unknown or not-yet-loaded role does not fall back to customer navigation.
- Reordered and renamed merchant navigation links to make the core merchant flow visible first:
  - `가맹점 홈`
  - `상품관리`
  - `주문관리`
  - `픽업`
  - `POS`
  - `재고 이력`
- Admin navigation continues to show admin and Pro Operations links.

## Role Redirect Rules

| Role | Default route | Primary menu |
| --- | --- | --- |
| `customer` | `/products` | 상품 보기, 내 예약, 내 결제 |
| `merchant` | `/merchant` | 가맹점 홈, 상품관리, 주문관리, 픽업, POS, 재고 이력 |
| `admin` | `/admin` | Admin, 운영 점검, Pro 운영, Batch Monitor |

## Google OAuth Impact

Google OAuth still uses the backend customer-only policy.

- The backend creates or logs in customer accounts only.
- Merchant/admin auto signup through Google remains blocked by policy.
- The callback keeps using `routeForRole(user.role)`, so Google customer login lands on the customer flow.

## Production Role Check

Production API base URL:

- `https://breadgo-api.onrender.com`

Checked production login responses without logging tokens or secrets:

| Account | Production role |
| --- | --- |
| `customer@breadgo.test` | `customer` |
| `merchant@breadgo.test` | `merchant` |
| `admin@breadgo.test` | `admin` |
| `merchant3@breadgo.test` | `customer` |

`merchant3@breadgo.test` currently returns `customer` from production. That account will follow the customer redirect/menu until the production user role is changed through the approved merchant flow or data correction. The canonical seeded seller demo account is still `merchant@breadgo.test`.

## Access Check

Production API checks:

- `customer@breadgo.test` login: OK, role `customer`
- `merchant@breadgo.test` login: OK, role `merchant`
- `admin@breadgo.test` login: OK, role `admin`
- Customer token calling `/api/v1/merchants/me`: blocked by missing merchant profile
- Merchant token calling `/api/v1/admin/summary`: `403`
- Admin token calling `/api/v1/admin/summary`: `200`
- Merchant token calling `/api/v1/merchants/me`: `200`

Frontend role guards remain responsible for redirecting unauthorized page access to the default route for the logged-in role.

## Deployment Check Notes

- `/login` production page renders the Google button.
- `/register` production page renders the Google button and merchant application CTA.
- Production currently needs a frontend redeploy after this Phase 147 commit before the updated NavBar labels/session-save behavior appear on `https://breadgo.vercel.app`.

## Validation Results

Local checks:

- `git status`: completed, working tree contains Phase 146/147 document and frontend changes.
- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: first attempt failed because the local backend server was not running; PASS after starting local FastAPI on `127.0.0.1:8000`.
- `python scripts/run_weekly_report_batch.py`: PASS
- `python scripts/run_pro_health_alert_check.py`: PASS
- `python -m pytest tests -q`: PASS, 15 passed.
- `npm run lint`: PASS
- `npm run build`: PASS

Production checks:

- `/login`: reachable and Google button markup present.
- `/register`: reachable and Google button markup present.
- Production login role check:
  - customer demo account returns `customer`.
  - merchant demo account returns `merchant`.
  - admin demo account returns `admin`.
  - `merchant3@breadgo.test` currently returns `customer`.

## DB / Migration

No DB schema change.

No migration added.

## Remaining Limits

- This phase does not create or repair production user roles. `merchant3@breadgo.test` is currently a customer account in production data.
- Browser UI automation through the in-app browser was limited in this environment, so production role behavior was verified primarily through production API responses and static page checks.
- Full post-deploy visual confirmation should be repeated after the frontend redeploy completes.

## Suggested Commit Message

`Fix role based login redirect navigation`
