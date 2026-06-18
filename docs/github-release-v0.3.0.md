# BreadGo v0.3.0 Demo Release

## Highlights

- Web MVP for customer, merchant, and admin flows
- Flutter customer mobile MVP
- Region and nearby product discovery
- Reservation, mock payment, cancellation, and mock refund flows
- Pickup code confirmation and manual delivery status management
- Settlement and platform revenue visibility
- Reservation status history
- In-app notification center
- Ops status endpoint and admin ops dashboard
- Deployment documentation for Vercel, Render, and Neon

## Demo URLs

- Frontend: https://breadgo.vercel.app
- Demo guide: https://breadgo.vercel.app/demo
- Backend: https://breadgo-api.onrender.com
- Health: https://breadgo-api.onrender.com/health
- Swagger: https://breadgo-api.onrender.com/docs

Render free instances may sleep. Open `/health` before the demo to warm up the backend.

## Demo Accounts

```text
customer@breadgo.test / 12345678
merchant@breadgo.test / 12345678
admin@breadgo.test / 12345678
```

## What Is Included

### Web

- Customer product discovery, reservation, mock payment, cancellation, notifications, and status history
- Merchant store/product/order/pickup/delivery/settlement management
- Admin dashboard, merchant approval, reservation/payment/product tables, settlement management, and ops checks

### Flutter Mobile

- Customer login
- Product list and detail
- Fulfillment method selection
- Reservation creation
- Mock payment
- My reservations
- Cancellation and mock refund status
- Notifications and read status
- Reservation history timeline

### Backend and Ops

- FastAPI backend
- PostgreSQL with Alembic migrations
- JWT authentication
- Mock payment provider
- Payment provider adapter skeleton
- Notification channel adapter skeleton
- Ops status API
- Smoke test script

## What Is Not Included Yet

- Real payment gateway integration
- Real card refund
- Real delivery/courier/parcel API
- Real SMS/email/Kakao Alimtalk/push notification
- Real map SDK
- Flutter merchant/admin apps
- Flutter secure token storage
- App Store / Play Store deployment
- Real bank transfer

## Verification

The following checks passed for the release documentation phase:

- Backend compile
- Alembic upgrade head
- Backend smoke test
- Frontend lint
- Frontend build
- Flutter pub get
- Dart format
- Flutter analyze
- Flutter test

Production smoke result document:

- `docs/production-smoke-result-v0.3.0.md`

## Known Limitations

- Mock payment and mock refund only
- Render free instance cold start can make the first request slow
- Demo accounts are for demo only
- Production secrets are not included in this repository
- Production write-flow smoke tests should be performed manually when needed
