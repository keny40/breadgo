# Post-release Verification v0.1.6

## Purpose

Use this template after publishing the `v0.1.6` Release.

## Release Metadata

- Expected tag: `v0.1.6-blob-upload-performance`
- Expected title: `BreadGo Blob Upload Performance Release v0.1.6`
- Expected body source: `docs/release-note-v0.1.6.md`
- Expected target branch: `main`

## GitHub Release Checks

Record after publication:

- Release URL:
- Latest Release shown: yes/no
- Tag points to expected `main` commit: yes/no
- `v0.1.5-google-oauth-live` remains as previous official Release: yes/no
- Existing tags are preserved: yes/no

## Documentation Checks

Confirm:

- README links to v0.1.6 RC/release docs if needed.
- `docs/release-note-v0.1.6.md` is visible on GitHub.
- `docs/release-checklist-v0.1.6.md` is visible on GitHub.
- `docs/post-release-verification-v0.1.6.md` is visible on GitHub.
- `docs/release-candidate-check-phase156.md` is visible on GitHub.

## Production Site Checks

Vercel Blob:

- Upload status endpoint reports `enabled=true`.
- Upload status endpoint reports `backend=vercel_blob`.
- Upload status endpoint reports `auth_mode=oidc` when using Vercel OIDC.
- Product image PNG/JPG upload succeeds.
- A public Blob URL is returned.
- Product creation saves the returned URL as `image_url`.
- Customer product views render the image.

Product feedback:

- Product registration success shows `상품이 등록되었습니다.`
- Product registration success does not show a red empty error box.
- Failure states show red error only when an actual error message exists.

Fallback:

- If storage is disabled, upload is safely blocked.
- Direct image URL input remains available.

Navigation:

- Customer navigation remains customer-only.
- Merchant navigation remains merchant-only.
- Admin navigation remains admin-only.
- Render cold/sleep latency remains documented as an operational caveat.

## Validation Commands

Run after Release if needed:

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/seed_demo.py
python scripts/smoke_test.py
python -m pytest tests -q
```

```powershell
cd frontend
npm run lint
npm run build
```

## Security Verification

Confirm:

- No secret/token/key value appears in Release body.
- No secret/token/key value appears in README or docs.
- No secret/token/key value appears in source, fixtures, or logs.
- Only environment variable names are documented.

## Result

- Post-release status:
- Follow-up needed:
