# Phase 152 v0.1.5 Final Tag / Release Registration Prep

## Purpose

Create the final v0.1.5 release tag from the latest `main` without deleting or moving the earlier v0.1.5 tag.

Final release target:

- Final tag: `v0.1.5-google-oauth-live`
- Release title: `BreadGo Google OAuth Live Release v0.1.5`
- Release body source: `docs/release-note-v0.1.5.md`
- Target branch: `main`

## Existing v0.1.5 Tag Status

The earlier tag is preserved as-is:

- Existing tag: `v0.1.5-google-oauth-role-onboarding`
- Existing tag target: `0b26bedb1930cdc161205b3aa4ee291a439c5c53`
- Classification: earlier/initial v0.1.5 tag
- Action taken: not deleted, not moved, not force-pushed

Reason:

- The existing tag does not include later Phase 149/150/151 stabilization and documentation commits.
- The project policy for this phase is to keep existing tags immutable.

## Final Tag Plan

The final tag `v0.1.5-google-oauth-live` is created as an annotated tag from the latest `main` after this Phase 152 documentation update is committed and pushed.

Tag message:

`BreadGo Google OAuth Live Release v0.1.5`

## GitHub Release Registration

Create the GitHub Release manually from the GitHub Web UI:

1. Open the GitHub repository.
2. Go to Releases.
3. Click Draft a new release.
4. Select tag: `v0.1.5-google-oauth-live`.
5. Target: `main`.
6. Title: `BreadGo Google OAuth Live Release v0.1.5`.
7. Paste the contents of `docs/release-note-v0.1.5.md`.
8. Confirm that no secret/token/key values are included.
9. Publish the release manually.

This phase does not create the GitHub Release automatically.

## Release Scope

Included at the final tag:

- Google OAuth customer login/signup live verification
- Render backend OAuth status `enabled=true`
- Customer/merchant/admin signup role separation
- Merchant application and admin approve/reject flow
- Role-based redirect and navigation fixes
- Product image upload storage fallback documentation
- Site performance diagnosis and navigation latency notes
- Pre-release deployed site check
- Phase 151 tag conflict documentation

Known operating note:

- Render cold/sleep latency remains a known operating issue and is documented in `docs/pre-release-site-check-v0.1.5-phase150.md`.

## Validation Results

Executed during Phase 152:

- `git status`: PASS, clean before tag creation; clean again after final verification
- `git branch --show-current`: PASS, `main`
- `git log --oneline -5`: PASS, latest `main` includes final v0.1.5 live release tag preparation
- `git tag --list`: PASS, both the earlier tag and final live tag are present
- `git show v0.1.5-google-oauth-live --no-patch`: PASS, annotated tag exists
- `git ls-remote --tags origin v0.1.5-google-oauth-live`: PASS, remote tag exists
- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS after explicitly waiting for the local backend `/health` endpoint
- `python -m pytest tests -q`: PASS, 15 passed, 1 warning
- `npm run lint`: PASS
- `npm run build`: PASS

## DB / Migration

No DB schema change.

No migration added.

## Secret / Token / Key Policy

- No `GOOGLE_CLIENT_SECRET` value is documented.
- No OAuth token is documented.
- No storage access key or secret key is documented.
- Environment variable names may be referenced in existing setup docs, but real values must stay in deployment secret stores only.

## Suggested Commit Message

`Prepare final v0.1.5 live release tag`
