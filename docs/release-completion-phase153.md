# Phase 153 v0.1.5 Release Completion

## Final Status

v0.1.5 is complete as the current official GitHub Release.

- Official latest Release: `v0.1.5-google-oauth-live`
- Release title: `BreadGo Google OAuth Live Release v0.1.5`
- Release URL: `https://github.com/keny40/breadgo/releases/tag/v0.1.5-google-oauth-live`
- Previous official Release: `v0.1.4-readiness-ux-boundary`
- Earlier v0.1.5 tag: `v0.1.5-google-oauth-role-onboarding`

## Tag Relationship

- `v0.1.5-google-oauth-live`: final v0.1.5 release tag, GitHub Release exists, Latest.
- `v0.1.5-google-oauth-role-onboarding`: earlier tag preserved for traceability, no GitHub Release.
- `v0.1.4-readiness-ux-boundary`: previous official release.

No existing tag was deleted or moved during completion.

## Completed Scope

v0.1.5 completed the following demo/live onboarding work:

- Google OAuth customer signup/login live verification.
- Render backend OAuth status `enabled=true`.
- Customer-only Google OAuth policy.
- Customer / merchant / admin signup role separation.
- Merchant application flow with admin approve/reject.
- Public `role=merchant` and `role=admin` signup blocking.
- Merchant/admin Google auto-signup blocking.
- Role-based login redirect and NavBar branching.
- Production role data clarification for `merchant3@breadgo.test`.
- Product image upload storage fallback documentation and UI guidance.
- Site navigation latency diagnosis and Render cold/sleep note.

## Excluded Scope

v0.1.5 does not add:

- Actual payment provider integration.
- Actual delivery provider integration.
- Actual POS API integration.
- Actual email/Kakao/Push/Slack/Discord/Webhook sending.
- Secret manager hardening.
- Additional migrations in Phase 153.

## Production Operating Notes

- Frontend: `https://breadgo.vercel.app`
- Backend API: `https://breadgo-api.onrender.com`
- Google OAuth status endpoint: `https://breadgo-api.onrender.com/api/v1/auth/google/status`
- Render cold/sleep latency can make the first backend request slow after inactivity.

## Security Boundary

- `GOOGLE_CLIENT_SECRET` is stored only in deployment environment variables.
- OAuth tokens are not stored in the database.
- Real secret/token/key values are not documented in repository files.
- Admin and merchant accounts cannot be created through public Google signup.

## Verification Summary

Final verification is recorded in `docs/release-post-check-phase153.md`.

## Suggested Commit Message

`Document v0.1.5 release completion`

