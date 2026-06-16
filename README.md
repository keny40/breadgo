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
