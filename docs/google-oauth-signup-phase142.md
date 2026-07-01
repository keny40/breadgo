# Phase 142 Google OAuth Customer Signup/Login

## Purpose

Add a basic Google OAuth entry point for BreadGo customer signup/login while keeping admin and merchant account flows separated.

## Account Policy

- Customer: Google OAuth signup/login is allowed.
- Merchant: automatic Google signup is not allowed in this phase. Merchant accounts continue to use the existing approval/registration flow.
- Admin: Google signup/login is not allowed.
- Existing email/password login remains available.
- Demo accounts remain available.

If a Google profile email already belongs to an admin or merchant user, the OAuth login is rejected. If the email belongs to an existing customer, BreadGo issues the normal JWT. If the email is new and verified by Google, BreadGo creates a customer user.

## Backend Flow

Endpoints:

- `GET /api/v1/auth/google/status`
  - Returns whether Google OAuth is enabled/configured.
- `GET /api/v1/auth/google/start`
  - Redirects to Google OAuth when enabled.
  - Returns a safe disabled/configuration error when not enabled.
- `GET /api/v1/auth/google/callback`
  - Exchanges the authorization code for a Google profile.
  - Requires `email_verified=true`.
  - Creates or logs in a customer user.
  - Redirects to the frontend callback page with the BreadGo JWT.

Frontend callback:

- `/auth/google/callback`
  - Reads the BreadGo JWT returned by the backend.
  - Calls `/api/v1/auth/me`.
  - Stores the token/user using the existing localStorage auth flow.
  - Redirects by role using the existing `routeForRole` helper.

## Environment Variables

Backend:

```text
GOOGLE_OAUTH_ENABLED=false
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

Frontend:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Notes:

- Do not commit real `GOOGLE_CLIENT_SECRET` values.
- Google client secret must be managed through deployment environment variables or a secret manager.
- Callback/redirect URLs must be registered in Google Cloud Console for the target environment.

## Security Boundaries

- Google access tokens are not logged.
- Google refresh tokens are not stored.
- Google ID tokens are not stored.
- BreadGo stores no Google token fields in the database.
- This phase uses the existing `users.email` field to connect accounts.
- `email_verified=false` is rejected.
- Admin and merchant accounts are not auto-created through Google OAuth.

## UI Copy

Login/register screens now show:

- Button: `Google로 계속하기`
- Help: `Google 계정으로 고객 회원가입 또는 로그인을 진행합니다.`
- Boundary note: `관리자와 가맹점 계정은 별도 승인 방식으로 운영됩니다.`

When disabled:

- `현재 환경에서는 Google OAuth가 꺼져 있습니다. 데모 계정 또는 이메일 로그인을 사용해 주세요.`

## Validation

Phase 142 validation:

- `git status`: PASS
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## Limitations

- No Google OAuth secrets are included in the repo.
- No admin/merchant Google signup is implemented.
- The callback currently returns the BreadGo JWT to the frontend callback route for MVP simplicity.
- Production hardening should add stronger state/session validation and token handoff hardening before public rollout.

## Phase 143 Deployment Check

Checked against the deployed demo environment:

- Frontend:
  - `/login`: `Google로 계속하기` button is visible.
  - `/register`: `Google로 계속하기` button is visible.
  - Both buttons are disabled because deployed Google OAuth status returns `enabled=false`.
  - Disabled guidance is shown: `현재 환경에서는 Google OAuth가 꺼져 있습니다. 데모 계정 또는 이메일 로그인을 사용해 주세요.`
  - Admin/merchant boundary copy is shown: `관리자와 가맹점 계정은 별도 승인 방식으로 운영됩니다.`
- Backend:
  - `GET /api/v1/auth/google/status`: returns `{"enabled": false, "message": "Google OAuth is disabled or not configured for this environment."}`.
  - No `accounts.google.com`, `oauth2.googleapis.com`, or Google live OAuth request was triggered.
- Existing auth:
  - `customer@breadgo.test / 12345678`: login PASS.
  - `merchant@breadgo.test / 12345678`: login PASS.
  - `admin@breadgo.test / 12345678`: login PASS.
  - Representative customer, merchant, and admin API checks returned 200.
- Browser check:
  - No page errors were observed.
  - One `/favicon.ico` 404 console message was observed on `/login`; it is unrelated to Google OAuth and does not block login.

No Vercel Google OAuth environment variables were added in this phase. Live Google OAuth remains disabled.

### Phase 143 Recheck - 2026-07-01

- `/login`: Google button remains visible and disabled.
- `/register`: Google button remains visible and disabled.
- `GET /api/v1/auth/google/status`: returns `enabled=false`.
- No Google live OAuth endpoint calls were observed.
- Customer, merchant, and admin demo logins still return 200.
- No OAuth-related console or network errors were observed. The existing `/favicon.ico` 404 on `/login` is unrelated to OAuth.
