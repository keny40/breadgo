# Phase 145 Signup Role Separation and Merchant Application

## Purpose

Separate BreadGo public customer signup from merchant onboarding. Customers can sign up with email/password or Google OAuth, while merchants must submit an application and wait for admin approval.

## Policy

- Customer:
  - Public email signup is allowed.
  - Google OAuth signup/login is allowed.
- Merchant:
  - Public automatic signup is blocked.
  - Merchant onboarding starts with an application.
  - Admin approval is required before a merchant profile is activated.
- Admin:
  - Public signup is blocked.
  - Admin accounts must be managed outside the public signup flow.
- Google OAuth:
  - Customer-only.
  - Existing admin or merchant emails are rejected by the OAuth service.

## Public Signup Changes

`POST /api/v1/auth/register` now accepts public signup only for `customer`.

If a caller sends:

- `role=merchant`
- `role=admin`

the API returns `403` and does not create a privileged account.

The `/register` screen is now customer-focused and links merchants to `/merchant/apply`.

## Merchant Application Flow

Public endpoint:

- `POST /api/v1/merchants/apply`

Fields:

- `store_name`
- `owner_name`
- `email`
- `phone`
- `business_registration_number`
- `address`
- `region_sido`
- `region_sigungu`
- `region_dong`
- `product_category`
- `pickup_available_time`
- `note`

Application statuses:

- `PENDING`
- `APPROVED`
- `REJECTED`

Applicants cannot access merchant management screens before approval.

## Admin Review Flow

Admin endpoints:

- `GET /api/v1/admin/merchant-applications`
- `GET /api/v1/admin/merchant-applications/{application_id}`
- `POST /api/v1/admin/merchant-applications/{application_id}/approve`
- `POST /api/v1/admin/merchant-applications/{application_id}/reject`

Approval behavior:

- Creates or reuses a `users` row for the applicant email.
- Sets the user role to `merchant` unless the email belongs to an admin.
- Creates or activates a `merchants` profile with `APPROVED` status.
- Stores the application review metadata.
- Does not expose generated credentials in API response or logs.

Rejection behavior:

- Sets status to `REJECTED`.
- Stores the rejection reason.
- Does not create a merchant profile.

## UI Changes

- `/register`: customer signup first, Google OAuth remains customer-only, merchant application CTA added.
- `/merchant/apply`: public merchant application form.
- `/merchant`: no longer shows direct merchant registration. It points users to merchant application if no approved profile exists.
- `/admin`: merchant application list with approve/reject actions.

## DB Change

Added table:

- `merchant_applications`

Migration:

- `backend/alembic/versions/202606180024_create_merchant_applications.py`

No existing `users` role enum or `merchants` table structure was changed.

## Security Boundaries

- Public users cannot self-assign admin or merchant role.
- Public merchant auto-registration is blocked.
- Google OAuth remains customer-only.
- Admin review APIs require admin JWT.
- Google tokens are still not stored.
- No external email or notification is sent in this phase.

## Validation

Phase 145 validation:

- Customer email signup: PASS
- Customer Google OAuth policy: preserved
- `role=merchant` public signup blocked: PASS
- `role=admin` public signup blocked: PASS
- Merchant application creation: PASS
- Admin application list/detail: PASS
- Admin approve/reject: PASS
- Merchant blocked from admin application APIs: PASS
- Existing customer/merchant/admin demo login: PASS
- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## Limitations

- Approval creates/activates merchant account/profile but does not send credentials externally.
- No external email/Kakao/Push notification is sent.
- Merchant onboarding email delivery and invitation-password setup should be handled in a later phase.
