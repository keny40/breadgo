# Release Note Draft v0.1.6

## Status

`v0.1.6` is a Release Candidate for the product image upload and perceived navigation stability improvements added after `v0.1.5-google-oauth-live`.

- Current official Release before this RC: `v0.1.5-google-oauth-live`
- Recommended tag: `v0.1.6-blob-upload-performance`
- Recommended Release title: `BreadGo Blob Upload Performance Release v0.1.6`
- Release body source: `docs/release-note-v0.1.6.md`
- Target branch: `main`

No tag or GitHub Release is created in Phase 156.

## Purpose

This RC documents the final polish around merchant product image upload, product registration feedback, and navigation latency guidance.

The release keeps the v0.1.x safety boundary:

- No DB schema change
- No migration change
- No new external payment, delivery, POS, email, Kakao, Push, Slack, Discord, or webhook integration
- No secret, token, key, or webhook URL committed to the repository

## Included in This Release Candidate

### Vercel Blob OIDC Product Image Upload

BreadGo now supports Vercel Blob deployments connected through OIDC.

Confirmed behavior:

- Vercel Blob can be used without `BLOB_READ_WRITE_TOKEN` when the project has `BLOB_STORE_ID` and Vercel runtime OIDC context.
- The upload status endpoint can report `enabled=true`, `backend=vercel_blob`, and `auth_mode=oidc`.
- PNG image upload succeeded in the live verification.
- The upload route returned a public Blob URL.
- Product registration and public product lookup showed the uploaded `image_url` normally.

The static token mode remains documented for environments that do not use Vercel OIDC.

### Product Registration Feedback UI

Merchant product creation feedback was clarified.

Commit:

- `90c1e92 Fix merchant product form feedback`

Changes summarized:

- A successful product registration no longer shows a red empty error box.
- Success displays `상품이 등록되었습니다.`
- A red error message is shown only for actual failures.
- Empty or whitespace-only messages are not rendered.
- Product creation resets the create form, selected image file, and message state correctly.
- Blob-backed image URLs and manually entered image URLs remain valid product image sources.

### Image Upload Fallback

The image upload fallback remains in place.

- If storage is not configured, file upload stays safely blocked.
- The user-facing guidance explains that direct image URL input can still be used.
- Product creation through direct `image_url` input remains supported.

### Navigation Latency Guidance

The frontend navigation latency work remains documented.

- Role-based local session data is used to avoid unnecessary role re-fetch work during navigation.
- Protected screens should not fall back to customer navigation while role information is still loading.
- Render cold/sleep latency remains a known operational issue for the backend and is documented as an infrastructure caveat, not a frontend bundle-size problem.

## Excluded Scope

This RC does not include:

- New product/business features
- DB schema changes
- Alembic migration changes
- New tag creation
- GitHub Release creation
- New payment provider integration
- New delivery provider integration
- New POS API integration
- New external notification integration
- Secret or token value documentation

## Validation Summary

The following validation results are carried forward from Phase 155 and the product feedback fix:

- `npm run lint`: PASS
- `npm run build`: PASS
- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS, 15 tests passed
- Vercel Blob OIDC status endpoint: `enabled=true`, `backend=vercel_blob`, `auth_mode=oidc`
- Live PNG upload: PASS
- Blob public URL returned: PASS
- Product registration with Blob `image_url`: PASS
- Product registration feedback fix commit: `90c1e92`

Phase 156 is documentation-only, so the heavy test suite was not repeated.

## Release Creation Notes

Recommended future release values:

- Tag: `v0.1.6-blob-upload-performance`
- Release title: `BreadGo Blob Upload Performance Release v0.1.6`
- Release body: `docs/release-note-v0.1.6.md`
- Target branch: `main`

Before creating the tag, confirm that the working tree is clean and that no secret/token/key value appears in docs, source, fixtures, logs, or release notes.
