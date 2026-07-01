# Phase 144 Google OAuth Live Verification

## Purpose

Record the live Google OAuth verification after configuring Google Cloud Console, Render backend environment variables, and the Vercel frontend/backend URL wiring.

## Live Integration State

- Frontend URL: `https://breadgo.vercel.app`
- Backend API base URL: `https://breadgo-api.onrender.com`
- Status endpoint: `https://breadgo-api.onrender.com/api/v1/auth/google/status`
- Redirect URI: `https://breadgo-api.onrender.com/api/v1/auth/google/callback`
- Google OAuth live status: enabled for customer accounts
- Actual Google login: verified successful by manual live test

## Status Endpoint Result

`GET https://breadgo-api.onrender.com/api/v1/auth/google/status`

```json
{
  "enabled": true,
  "message": "Google OAuth is enabled for customer accounts."
}
```

## Frontend Verification

- `/login`
  - `Google로 계속하기` button is visible.
  - Button is enabled.
  - Customer guidance copy is visible.
  - Admin/merchant separate approval guidance is visible.
- `/register`
  - `Google로 계속하기` button is visible.
  - Button is enabled.
  - Customer guidance copy is visible.
  - Admin/merchant separate approval guidance is visible.

No page errors, OAuth-related console errors, or failed OAuth readiness requests were observed during the verification check.

## Login Result

Google login completed successfully in the deployed site after fixing the Render backend `GOOGLE_CLIENT_ID` value.

Account handling policy:

- If the Google email already belongs to a customer user, BreadGo logs in the existing customer.
- If the Google email is new and `email_verified=true`, BreadGo creates a new `customer` user.
- Admin and merchant Google auto-signup/login remain blocked.

The verification confirmed that the customer-only OAuth policy remains the intended behavior. No admin or merchant automatic Google signup was enabled.

## Existing Login Impact

Existing email/password login and demo accounts remain supported:

- `customer@breadgo.test / 12345678`
- `merchant@breadgo.test / 12345678`
- `admin@breadgo.test / 12345678`

Phase 144 did not change the email/password auth flow.

## invalid_client Incident

Observed issue:

- Google returned an `invalid_client` error during live setup.

Root cause:

- Render `GOOGLE_CLIENT_ID` was set to an incorrect or incomplete Client ID value.

Resolution:

- The full Google Cloud OAuth Client ID value was re-entered in Render backend environment variables.
- Render backend was redeployed.
- Google login succeeded after the corrected Client ID was applied.

## Secret and Token Handling

- `GOOGLE_CLIENT_SECRET` is configured only as a Render backend environment variable.
- No Google Client Secret is stored in code, docs, test fixtures, README, or logs.
- Google access tokens are not stored in the DB.
- Google refresh tokens are not stored in the DB.
- Google ID tokens are not stored in the DB.
- OAuth verification notes do not include real secrets, access tokens, refresh tokens, ID tokens, or API keys.

## Environment Variables

Frontend Vercel:

```text
NEXT_PUBLIC_API_BASE_URL=https://breadgo-api.onrender.com
```

Backend Render:

```text
GOOGLE_OAUTH_ENABLED=true
GOOGLE_CLIENT_ID=<Google OAuth Client ID>
GOOGLE_CLIENT_SECRET=<Render secret only>
GOOGLE_REDIRECT_URI=https://breadgo-api.onrender.com/api/v1/auth/google/callback
FRONTEND_URL=https://breadgo.vercel.app
BACKEND_URL=https://breadgo-api.onrender.com
```

Google Cloud Console Authorized redirect URI:

```text
https://breadgo-api.onrender.com/api/v1/auth/google/callback
```

## Change Boundaries

- DB schema changed: No
- Migration added: No
- Google token DB storage added: No
- Admin/merchant automatic Google signup enabled: No
- New tag or GitHub Release created: No
- Secret/token/key written to repo: No

## Validation

Phase 144 validation:

- `git status`: PASS
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS
