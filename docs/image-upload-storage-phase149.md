# Phase 149 Image Upload Storage Configuration

## Purpose

Fix the confusing product image upload failure on `/merchant/products`.

Original production symptom:

- Merchant selects an image file.
- Upload fails with `Image upload storage is not configured.`
- Manual image URL input still works.

## Root Cause

Product image file upload is handled by the frontend Next.js route:

- `frontend/app/api/upload/product-image/route.ts`
- Public endpoint: `/api/upload/product-image`

Before this phase, the route only supported Vercel Blob and required:

- `BLOB_READ_WRITE_TOKEN`

When that token was missing in the Vercel frontend environment, the route returned a generic 500 error.

FastAPI backend and Render were not the active image upload path for this route. Render backend settings are still relevant for future backend-hosted storage, but the current file upload button runs through the Vercel frontend deployment.

## Changes

- Added upload storage status check:
  - `GET /api/upload/product-image`
- Improved disabled storage response:
  - HTTP `503`
  - Korean user-friendly message
  - no secret values in response
- Kept manual image URL input working.
- Disabled file input and upload button when storage is not configured.
- Added Vercel Blob and S3-compatible storage configuration paths.
- Added S3-compatible signed PUT support without storing secrets in code.

## Supported Storage Backends

### Vercel Blob

Use this when hosting the frontend on Vercel.

Recommended Vercel frontend environment variables for OIDC-connected Blob Stores:

```text
IMAGE_UPLOAD_ENABLED=true
STORAGE_BACKEND=vercel_blob
BLOB_STORE_ID=<provided by Vercel Blob project connection>
```

Vercel provides `VERCEL_OIDC_TOKEN` at runtime for connected projects. The app uses `BLOB_STORE_ID + VERCEL_OIDC_TOKEN` when available.

For non-OIDC environments, use a read-write token instead:

```text
BLOB_READ_WRITE_TOKEN=<set in hosting provider only>
```

Do not commit token values.

### S3-compatible storage

Use this for Cloudflare R2, AWS S3, or compatible storage.

Required frontend environment variables:

```text
IMAGE_UPLOAD_ENABLED=true
STORAGE_BACKEND=s3
S3_BUCKET=<bucket-name>
S3_REGION=<region-or-auto>
S3_ACCESS_KEY_ID=<set in hosting provider only>
S3_SECRET_ACCESS_KEY=<set in hosting provider only>
PUBLIC_ASSET_BASE_URL=https://assets.example.com
```

For Cloudflare R2, also set:

```text
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
S3_REGION=auto
PUBLIC_ASSET_BASE_URL=https://<public-r2-domain-or-custom-domain>
```

For AWS S3 without a custom endpoint, `S3_ENDPOINT_URL` can be omitted. The bucket must be configured so the returned object URL is readable by the frontend.

## Render Backend Notes

Current product image upload is a Next.js route on Vercel, not a Render FastAPI endpoint.

Render backend does not need image upload storage variables for the current implementation.

If a future phase moves file upload to FastAPI, configure the same conceptual variables on Render:

```text
IMAGE_UPLOAD_ENABLED=true
STORAGE_BACKEND=s3
S3_ENDPOINT_URL=
S3_BUCKET=
S3_REGION=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
PUBLIC_ASSET_BASE_URL=
```

Never paste actual access key or secret key values into documentation, git, logs, or screenshots.

## Frontend Behavior

When storage is configured:

- File input is enabled.
- `이미지 업로드` button uploads the selected image.
- Returned URL is copied into the image URL field.

When storage is not configured:

- File input is disabled.
- Upload button is disabled.
- The page shows:
  - `이미지 파일 업로드 storage가 설정되지 않았습니다. 이미지 URL 직접 입력은 계속 사용할 수 있습니다.`
- Manual image URL input remains available.

## Phase 154 Live Verification

Phase 154 rechecked the production Vercel deployment after the intended Vercel Blob setup.

Actual production status on `https://breadgo.vercel.app/api/upload/product-image`:

- `enabled=false`
- `backend=none`
- `missing_env=["BLOB_READ_WRITE_TOKEN"]`
- `/merchant/products` still disables the file input and `이미지 업로드` button.
- Manual image URL input remains available.
- No secret/token/key value was exposed.

Conclusion:

- Vercel Blob is not yet active on the live deployment.
- Confirm that `BLOB_READ_WRITE_TOKEN`, `IMAGE_UPLOAD_ENABLED=true`, and `STORAGE_BACKEND=vercel_blob` are set in the correct Vercel production environment, then redeploy.
- Detailed result: `docs/image-upload-live-verification-phase154.md`

## OIDC Support Update

Vercel Blob now supports OIDC-connected projects. In that mode Vercel does not create a visible `BLOB_READ_WRITE_TOKEN`; instead, it provides `BLOB_STORE_ID` and a short-lived `VERCEL_OIDC_TOKEN` at runtime.

BreadGo now enables Vercel Blob upload when either of these auth paths is available:

- `BLOB_READ_WRITE_TOKEN`
- `BLOB_STORE_ID + VERCEL_OIDC_TOKEN`

Detailed OIDC note: `docs/vercel-blob-oidc-phase155.md`

## Security

- No storage access key or secret key is stored in code.
- No storage access key or secret key is written to logs.
- API responses include missing environment variable names only, not values.
- Product image upload does not change DB schema.

## Validation

- Storage disabled status endpoint: PASS
  - `GET /api/upload/product-image`
  - `enabled=false`
  - message: `이미지 파일 업로드 storage가 설정되지 않았습니다. 이미지 URL 직접 입력은 계속 사용할 수 있습니다.`
  - missing env names only, no secret values.
- Storage disabled UI behavior: implemented in `/merchant/products`.
  - file input disabled.
  - upload button disabled.
  - image URL direct input remains available.
- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS, 15 passed.
- `npm run lint`: PASS
- `npm run build`: PASS

## Suggested Commit Message

`Configure product image upload storage guidance`
