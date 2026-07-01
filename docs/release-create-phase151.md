# Phase 151 v0.1.5 Tag / Release Registration Prep

## Purpose

Prepare the v0.1.5 GitHub Release registration using the Release Candidate documents and pre-release site check results.

Requested Release target:

- Tag: `v0.1.5-google-oauth-role-onboarding`
- Release title: `BreadGo Google OAuth Role Onboarding Release v0.1.5`
- Release body source: `docs/release-note-v0.1.5.md`
- Target branch: `main`

## Important Tag Status

The requested tag already exists locally and on origin.

- Existing tag: `v0.1.5-google-oauth-role-onboarding`
- Tag type: annotated tag
- Tag message: `BreadGo Google OAuth Role Onboarding Release v0.1.5`
- Current tag target commit: `0b26bedb1930cdc161205b3aa4ee291a439c5c53`
- Remote tag ref: `refs/tags/v0.1.5-google-oauth-role-onboarding`

Because this phase explicitly forbids deleting or moving existing tags, the existing tag was not recreated, deleted, moved, or force-pushed.

## Current Main Status

Current `main` contains later v0.1.5 stabilization work after the existing tag:

- image upload storage fallback and documentation
- navigation latency improvement
- v0.1.5 pre-release deployed site check

The current `main` HEAD at the start of Phase 151 was:

- `8a5f58d Document v0.1.5 pre-release site check`

## GitHub Release Registration Guidance

If using the existing tag as requested:

1. Open the GitHub repository.
2. Go to Releases.
3. Click Draft a new release.
4. Select tag: `v0.1.5-google-oauth-role-onboarding`.
5. Target: `main`.
6. Title: `BreadGo Google OAuth Role Onboarding Release v0.1.5`.
7. Paste the contents of `docs/release-note-v0.1.5.md`.
8. Confirm that no secret/token/key values are included.
9. Publish manually from the GitHub Web UI.

Important note:

- The existing tag points to `0b26bed`, not the latest `main` commit with Phase 149/150 follow-up fixes.
- Updating the existing tag to point to latest `main` would require moving the tag, which this phase forbids.
- If the release must include all latest Phase 149/150 commits at tag level, use a new tag in a separate approved phase, or explicitly approve moving the tag.

## GitHub CLI Note

This phase does not create the GitHub Release automatically.

If a future operator uses GitHub CLI manually:

```powershell
gh release create v0.1.5-google-oauth-role-onboarding `
  --title "BreadGo Google OAuth Role Onboarding Release v0.1.5" `
  --notes-file docs/release-note-v0.1.5.md
```

## Validation Results

Executed during Phase 151:

- `git status`: PASS, documentation-only working tree changes before commit
- `git branch --show-current`: PASS, `main`
- `git log --oneline -5`: PASS, latest local `main` includes Phase 150 pre-release site check
- `git tag --list`: PASS, `v0.1.5-google-oauth-role-onboarding` exists
- `git show v0.1.5-google-oauth-role-onboarding --no-patch`: PASS, annotated tag points to `0b26bedb1930cdc161205b3aa4ee291a439c5c53`
- `git ls-remote --tags origin v0.1.5-google-oauth-role-onboarding`: PASS, remote tag exists at `refs/tags/v0.1.5-google-oauth-role-onboarding`
- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS, 15 passed, 1 warning
- `npm run lint`: PASS
- `npm run build`: PASS

## DB / Migration

No DB schema change.

No migration added.

## Secret / Token / Key Policy

- No `GOOGLE_CLIENT_SECRET` value is documented.
- No Google token is documented.
- No storage access key or secret key is documented.
- Render cold/sleep remains a known operating issue and is documented separately in `docs/pre-release-site-check-v0.1.5-phase150.md`.

## Suggested Commit Message

`Document v0.1.5 release registration prep`
