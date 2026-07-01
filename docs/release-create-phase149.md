# Phase 149 v0.1.5 Tag / Release Registration Prep

## Purpose

Create and push the official `v0.1.5` tag for the Google OAuth, role onboarding, and role-based navigation Release Candidate, then prepare GitHub Web UI release registration details.

This phase does not create a GitHub Release automatically.

## Release Target

- Tag: `v0.1.5-google-oauth-role-onboarding`
- Release title: `BreadGo Google OAuth Role Onboarding Release v0.1.5`
- Release body source: `docs/release-note-v0.1.5.md`
- Target branch: `main`

## Pre-check

- Current branch: `main`
- Working tree before Phase 149 doc change: clean
- Existing tag check: `v0.1.5-google-oauth-role-onboarding` did not exist locally.
- Remote tag check: `origin` did not have `v0.1.5-google-oauth-role-onboarding`.
- Existing tags were not deleted or moved.
- Current official latest Release remains `v0.1.4-readiness-ux-boundary` until the v0.1.5 GitHub Release is manually published.

## Phase 149 Document Change

This document records the tag creation and GitHub Release registration prep.

README was updated with a short Phase 149 release prep link.

## Tag Creation Plan

After committing this Phase 149 document:

```powershell
git tag -a v0.1.5-google-oauth-role-onboarding -m "BreadGo Google OAuth Role Onboarding Release v0.1.5"
git push origin v0.1.5-google-oauth-role-onboarding
```

## GitHub Release Registration

Use the GitHub Web UI after the tag is pushed.

1. Open the GitHub repository.
2. Go to Releases.
3. Click Draft a new release.
4. Select tag: `v0.1.5-google-oauth-role-onboarding`.
5. Target: `main`.
6. Title: `BreadGo Google OAuth Role Onboarding Release v0.1.5`.
7. Copy the content of `docs/release-note-v0.1.5.md` into the Release body.
8. Confirm no secret/token/key values are present.
9. Publish the Release.

## GitHub CLI Note

This phase intentionally does not create the GitHub Release with `gh`.

If a future operator chooses to use GitHub CLI after this phase:

```powershell
gh release create v0.1.5-google-oauth-role-onboarding `
  --title "BreadGo Google OAuth Role Onboarding Release v0.1.5" `
  --notes-file docs/release-note-v0.1.5.md
```

## Security Notes

- No `GOOGLE_CLIENT_SECRET` value is documented.
- No Google token is documented.
- No API key, secret, token, or webhook URL is documented.
- OAuth secret remains an environment variable only.

## Validation Results

- `git status`: PASS before commit/tag, only Phase 149 docs/README changed.
- `git branch --show-current`: PASS, `main`.
- `git log --oneline -5`: PASS.
- `git tag --list`: PASS, v0.1.5 tag was absent before creation.
- `git show v0.1.5-google-oauth-role-onboarding --no-patch`: PASS.
- `git ls-remote --tags origin v0.1.5-google-oauth-role-onboarding`: PASS.
- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS after starting local FastAPI on `127.0.0.1:8000`.
- `python -m pytest tests -q`: PASS, 15 passed.
- `npm run lint`: PASS
- `npm run build`: PASS

## Tag Result

- Created tag: `v0.1.5-google-oauth-role-onboarding`
- Tag type: annotated tag
- Tag message: `BreadGo Google OAuth Role Onboarding Release v0.1.5`
- Tag target commit: `0b26bedb1930cdc161205b3aa4ee291a439c5c53`
- Tag push: completed to `origin`
- Remote tag ref: `refs/tags/v0.1.5-google-oauth-role-onboarding`

This status note was recorded after the tag push. The tag itself was not moved after creation.

## DB / Migration

No DB schema change.

No migration added.

## Feature Code

No feature code changed in Phase 149.

## Suggested Commit Message

`Prepare v0.1.5 release tag registration`
