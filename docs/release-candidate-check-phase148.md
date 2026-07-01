# Phase 148 v0.1.5 Release Candidate Check

## Purpose

Prepare the `v0.1.5` Release Candidate documentation for the Google OAuth, role separation, merchant onboarding, and role-based navigation work completed after v0.1.4.

## Status

- v0.1.5 is Release Candidate documentation only.
- New tag: not created.
- GitHub Release: not created.
- Existing tags: not deleted or moved.
- Current official latest Release remains `v0.1.4-readiness-ux-boundary`.

## Included Scope

- Google OAuth customer login/signup live integration
- Render backend OAuth status `enabled=true`
- Google customer login success
- Customer / merchant / admin signup role separation
- Merchant application -> admin approve/reject flow
- `role=merchant` / `role=admin` public signup blocking
- merchant/admin Google auto signup blocking policy
- customer/merchant/admin role based redirect
- NavBar role-based menu branching
- `merchant3@breadgo.test` production data note
- Existing demo accounts remain available
- secret/token/key non-disclosure principle

## Excluded Scope

- New feature code in Phase 148
- DB schema change in Phase 148
- New migration in Phase 148
- New tag
- GitHub Release creation
- Admin Google signup
- Merchant Google auto signup
- Actual PG / delivery / POS / external notification integration
- Secret manager implementation

## Recommended Release Information

- Recommended tag: `v0.1.5-google-oauth-role-onboarding`
- Recommended Release title: `BreadGo Google OAuth Role Onboarding Release v0.1.5`
- Release body source: `docs/release-note-v0.1.5.md`
- Target branch: `main`

## DB / Migration

No DB schema change in Phase 148.

No migration added in Phase 148.

The merchant onboarding feature uses the existing Phase 145 migration:

- `202606180024_create_merchant_applications.py`

## Security / Secret Check

- No `GOOGLE_CLIENT_SECRET` value was added to docs/code.
- No Google token was added to docs/code.
- No API key, secret, token, or webhook URL was added.
- OAuth secret remains an environment variable only.

## Validation Results

- `git status`: PASS, Phase 148 docs/README changes only after this package.
- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS after starting local FastAPI on `127.0.0.1:8000`.
- `python -m pytest tests -q`: PASS, 15 passed.
- `npm run lint`: PASS
- `npm run build`: PASS

## Remaining Notes

- Production frontend needs redeployment for the latest role-based NavBar/session-save behavior from Phase 147 if it has not already deployed.
- `merchant3@breadgo.test` is currently customer role in production data and should not be used as the merchant demo account unless production data is corrected.

## Suggested Commit Message

`Prepare v0.1.5 release candidate docs`
