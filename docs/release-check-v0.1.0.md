# BreadGo MVP v0.1.0 Local Demo Release Check

## Project Status Summary

BreadGo v0.1.0 is ready as a stable local demo release. The MVP runs locally with FastAPI, PostgreSQL, and Next.js without Docker, and it supports the core customer, merchant, and admin demonstration flow.

The release is intended for product validation and stakeholder demos, not production deployment.

## Completed Phases

- Phase 1: FastAPI foundation, PostgreSQL connection, SQLAlchemy, Alembic, user model, JWT auth.
- Phase 2: Merchant and store onboarding.
- Phase 3: Product listing for merchant-owned stores.
- Phase 4: Reservation flow with product quantity updates.
- Phase 5: Pickup confirmation by reservation pickup code.
- Phase 6: Minimal Next.js MVP web UI.
- Phase 7: Demo-ready frontend flow and navigation.
- Phase 8: Minimal admin dashboard.
- Phase 9: Region-based store and product discovery.
- Phase 10: Mock payment flow.
- Phase 11: Demo seed data and reset tooling.
- Phase 12-A: Presentation-ready `/demo` page.
- Phase 12-B: Backend smoke test script.
- Phase 13: Local demo release checkpoint documentation.

## Backend Features

- JWT registration, login, and current-user lookup.
- Merchant registration and merchant profile lookup.
- Store creation and management.
- Region fields on stores: `sido`, `sigungu`, `dong`, `latitude`, `longitude`.
- Public region product discovery.
- Product creation and soft hiding.
- Customer reservation creation.
- Reservation quantity decrement and sold-out handling.
- Reservation cancellation with quantity restoration.
- Pickup code lookup and merchant pickup confirmation.
- Mock payment ready, confirm, fail, and cancel flow.
- Admin summary, users, merchants, stores, products, reservations, and payments APIs.
- Demo seed script.
- End-to-end backend smoke test script.

## Frontend Features

- Home and demo guide pages.
- Login and register pages.
- Region-based product browsing.
- Reservation and mock payment flow.
- My reservations page with pickup code.
- My payments page.
- Merchant dashboard.
- Store management with region fields.
- Product management with store dropdown.
- Pickup confirmation page.
- Admin dashboard with summary and data tables.
- Shared navigation and basic session handling.

## Demo Accounts

```text
admin@breadgo.test / 12345678
merchant@breadgo.test / 12345678
customer@breadgo.test / 12345678
```

## Local Run Commands

### Backend

```powershell
cd backend
.\.venv\Scripts\activate
python -m alembic upgrade head
python scripts/seed_demo.py
python -m uvicorn app.main:app --reload --port 8000
```

If the virtual environment is not used, run the Python commands from `backend` with the active local Python environment.

### Frontend

```powershell
cd frontend
npm run dev
```

Open:

[http://localhost:3000/demo](http://localhost:3000/demo)

## Seed Command

```powershell
cd backend
python scripts/seed_demo.py
```

The seed script is idempotent and can be run multiple times. It creates or updates demo users, an approved merchant, three stores, and active bakery products.

## Smoke Test Command

Start the backend first, then run:

```powershell
cd backend
python scripts/smoke_test.py
```

Expected result:

```text
[PASS] Health check
[PASS] Customer login
[PASS] Region products found
[PASS] Active product with stock found
[PASS] Reservation created
[PASS] Mock payment ready
[PASS] Mock payment confirmed
[PASS] My reservations loaded
[PASS] Merchant login
[PASS] Pickup confirmed
[PASS] Admin login
[PASS] Admin summary loaded
[PASS] BreadGo MVP smoke test completed
```

## Verification Checklist

### Backend

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/seed_demo.py
python scripts/smoke_test.py
```

### Frontend

```powershell
cd frontend
npm run lint
npm run build
```

## Known Limitations

- No real payment gateway.
- Mock payment only.
- No real map or GPS search yet.
- No production email verification.
- Local PostgreSQL only.
- Admin role is assigned by seed data or SQL.
- No production deployment yet.

## Next Recommended Phases

- Phase 14: UI polish and responsive mobile layout.
- Phase 15: Deployment preparation.
- Phase 16: Real map and location search.
- Phase 17: Reviews and ratings.
- Phase 18: Real payment integration.
- Phase 19: AI discount recommendation.
