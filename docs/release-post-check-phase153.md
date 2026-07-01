# Phase 153 v0.1.5 Release Post-check

## Purpose

Verify the GitHub Web UI release registration for v0.1.5 and record the post-release state.

## Release Target

- Tag: `v0.1.5-google-oauth-live`
- Release title: `BreadGo Google OAuth Live Release v0.1.5`
- Release body source: `docs/release-note-v0.1.5.md`
- Target branch: `main`
- Release URL: `https://github.com/keny40/breadgo/releases/tag/v0.1.5-google-oauth-live`

## GitHub Release Status

- Release URL: PASS
- Release title: PASS, `BreadGo Google OAuth Live Release v0.1.5`
- Release tag: PASS, `v0.1.5-google-oauth-live`
- Target branch: PASS, `main`
- Draft status: PASS, `false`
- Prerelease status: PASS, `false`
- Latest Release: PASS, GitHub latest release API returns `v0.1.5-google-oauth-live`

The release page was reachable and displayed the `Latest` badge.

## Related Tag / Release State

- `v0.1.5-google-oauth-live`: official v0.1.5 GitHub Release tag.
- `v0.1.5-google-oauth-role-onboarding`: earlier v0.1.5 tag, preserved without deletion or movement. GitHub release lookup for this tag returned `404`, so it remains a tag without a GitHub Release.
- `v0.1.4-readiness-ux-boundary`: previous official GitHub Release, still reachable and no longer Latest.

## Production Feature Checks

Google OAuth:

- Status endpoint: `https://breadgo-api.onrender.com/api/v1/auth/google/status`
- Result: `enabled=true`
- Message: `Google OAuth is enabled for customer accounts.`
- Live login status: verified in Phase 144 and kept as the v0.1.5 release basis.

Signup / onboarding:

- Customer email signup remains available.
- Customer Google OAuth signup/login remains available.
- Merchant automatic public signup remains blocked.
- Merchant onboarding uses application -> admin approve/reject.
- Admin public signup remains blocked.

Role-based redirect/navigation:

- Customer login defaults to customer product flow.
- Merchant login defaults to `/merchant`.
- Admin login defaults to `/admin`.
- NavBar role-specific menu branching is included in the v0.1.5 release scope.

Image upload fallback:

- Product image upload storage fallback documentation and UI guidance are included.
- Direct image URL input remains the fallback when upload storage is not configured.

Known operating issue:

- Render free instance cold/sleep latency can make the first backend request slow after inactivity.
- This is documented in `docs/pre-release-site-check-v0.1.5-phase150.md`.

## Secret / Token / Key Check

- No `GOOGLE_CLIENT_SECRET` value is documented.
- No OAuth token is documented.
- No storage access key or secret key is documented.
- GitHub Release and local docs should continue to avoid real secret/token/key values.

## Validation Results

Executed during Phase 153:

- `git status`: PASS
- `git branch --show-current`: PASS, `main`
- `git tag --list`: PASS
- `git show v0.1.5-google-oauth-live --no-patch`: PASS
- v0.1.5 Release URL check: PASS
- v0.1.4 Release URL check: PASS
- Google OAuth status endpoint: PASS, `enabled=true`
- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS, 15 passed, 1 warning
- `npm run lint`: PASS
- `npm run build`: PASS

## Notes

The GitHub Release body was created from `docs/release-note-v0.1.5.md`. The local release note has been updated to reflect completion status after post-check.
