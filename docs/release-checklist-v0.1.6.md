# Release Checklist v0.1.6

## Purpose

Use this checklist before creating the `v0.1.6` Release for Vercel Blob OIDC image upload support, product registration feedback cleanup, image upload fallback continuity, and navigation latency documentation.

## Release Candidate Information

- Recommended tag: `v0.1.6-blob-upload-performance`
- Recommended Release title: `BreadGo Blob Upload Performance Release v0.1.6`
- Release body source: `docs/release-note-v0.1.6.md`
- Target branch: `main`
- Current official Release before this RC: `v0.1.5-google-oauth-live`

## Scope Confirmation

Included:

- Vercel Blob OIDC product image upload support
- Upload status endpoint behavior for `enabled=true`, `backend=vercel_blob`, `auth_mode=oidc`
- Live PNG upload confirmation
- Blob public URL returned and saved as `image_url`
- Product registration success feedback cleanup
- Image upload fallback and direct image URL input preservation
- Navigation latency guidance and Render cold/sleep caveat

Excluded:

- New feature development
- DB schema changes
- Migration changes
- New tag or Release during Phase 156
- Actual PG, delivery, POS, email, Kakao, Push, Slack, Discord, or webhook integration
- Secret/token/key values in repository content

## Pre-release Git Checks

Run before tag creation:

```powershell
git status
git branch --show-current
git status -sb
git log --oneline -10
git tag --list
```

Expected:

- Branch is `main`
- Working tree is clean
- Existing tags are not deleted or moved
- `v0.1.6-blob-upload-performance` does not already exist unless intentionally re-checking an existing tag

## Validation Commands

Heavy validation was already completed during Phase 155 and the product registration feedback fix. Before final Release creation, run the full set once more if code has changed after Phase 156.

Backend:

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/seed_demo.py
python scripts/smoke_test.py
python -m pytest tests -q
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

## Manual Site Checks

Product image upload:

- `/merchant/products` file input is enabled when Vercel Blob is configured.
- PNG or JPG upload returns a Blob public URL.
- The returned URL is copied into the product `image_url`.
- Product creation succeeds with the Blob URL.
- Product list and public product detail show the image.
- Storage fallback message is not shown when Blob OIDC is enabled.
- Direct image URL input still works when file upload is unavailable.

Product registration feedback:

- Success shows `상품이 등록되었습니다.`
- Success does not render a red empty error box.
- Failures show a red error message only when an actual error exists.
- Empty messages do not render a message box.

Navigation:

- Customer, merchant, and admin menus preserve role-based navigation.
- Render cold/sleep latency is documented as a backend infrastructure caveat.

## Security Checks

Confirm:

- No `BLOB_READ_WRITE_TOKEN` value is committed.
- No Google client secret is committed.
- No API key, secret, token, or webhook URL appears in README, docs, source, fixtures, or logs.
- Environment variable names may be documented, but actual values must not be documented.

## Release Registration Values

Use these values if creating the GitHub Release later:

- Tag: `v0.1.6-blob-upload-performance`
- Release title: `BreadGo Blob Upload Performance Release v0.1.6`
- Release body source: `docs/release-note-v0.1.6.md`
- Target branch: `main`
