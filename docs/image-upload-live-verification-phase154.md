# Phase 154 Vercel Blob Image Upload Live Verification

## Purpose

Verify whether Vercel Blob product image uploads work on the deployed BreadGo site.

Target:

- Frontend: `https://breadgo.vercel.app`
- Upload status endpoint: `https://breadgo.vercel.app/api/upload/product-image`
- Merchant product screen: `https://breadgo.vercel.app/merchant/products`

## Expected Configuration

The intended Vercel frontend environment configuration is:

```text
IMAGE_UPLOAD_ENABLED=true
STORAGE_BACKEND=vercel_blob
BLOB_READ_WRITE_TOKEN=<set in Vercel only>
```

The actual token value must stay only in Vercel environment variables.

## Live Verification Result

Current live status: **NOT ENABLED**

`GET /api/upload/product-image` returned:

```json
{
  "enabled": false,
  "backend": "none",
  "message": "이미지 파일 업로드 storage가 설정되지 않았습니다. 이미지 URL 직접 입력은 계속 사용할 수 있습니다.",
  "missing_env": ["BLOB_READ_WRITE_TOKEN"]
}
```

This means the deployed frontend did not see `BLOB_READ_WRITE_TOKEN` at runtime/build time. The most likely causes are:

- `BLOB_READ_WRITE_TOKEN` is not set in the Vercel project/environment used by `https://breadgo.vercel.app`.
- `IMAGE_UPLOAD_ENABLED` / `STORAGE_BACKEND` are not set in the same Vercel environment.
- The Vercel deployment was not redeployed after setting the variables.
- The token was set in a different Vercel project, team, or environment scope than the production deployment.

## Merchant Product Screen Check

Logged in as the demo merchant account and opened `/merchant/products`.

Observed state:

- File input: disabled
- `이미지 업로드` button: disabled
- Storage warning: still visible
- Manual image URL input: still available

Visible warning:

```text
이미지 파일 업로드 storage가 설정되지 않았습니다. 이미지 URL 직접 입력은 계속 사용할 수 있습니다. 파일 업로드가 필요하면 운영 환경변수를 설정하세요.
```

## POST Upload Check

A tiny test PNG was submitted to:

```text
POST https://breadgo.vercel.app/api/upload/product-image
```

Result:

- HTTP status: `503 Service Unavailable`
- No Blob URL returned
- No upload occurred
- Response included missing environment variable names only
- No secret/token/key value was exposed

Response body:

```json
{
  "detail": "이미지 파일 업로드 storage가 설정되지 않았습니다. 이미지 URL 직접 입력은 계속 사용할 수 있습니다.",
  "storage": {
    "enabled": false,
    "backend": "none",
    "message": "이미지 파일 업로드 storage가 설정되지 않았습니다. 이미지 URL 직접 입력은 계속 사용할 수 있습니다.",
    "missing_env": ["BLOB_READ_WRITE_TOKEN"]
  }
}
```

## Product Registration / Display Result

Blob file upload could not be completed because storage is disabled in the live deployment.

Because upload is disabled, this phase did not create a new production product solely for testing. The UI still keeps the manual image URL field available, so operators can use an externally hosted image URL until Vercel Blob is correctly enabled.

## Required Fix Before Retest

For Vercel Blob OIDC-connected stores, the old read-write token check is not sufficient. See `docs/vercel-blob-oidc-phase155.md`.

In Vercel project settings for the production frontend deployment:

1. Confirm the Blob Store is connected to the correct Vercel project and environment.
2. Confirm the variables are available for the same environment:
   - `BLOB_STORE_ID`
   - Vercel-provided runtime `VERCEL_OIDC_TOKEN`
   - `IMAGE_UPLOAD_ENABLED=true`
   - `STORAGE_BACKEND=vercel_blob`
3. If OIDC cannot be used, create a read-write token and set `BLOB_READ_WRITE_TOKEN` in Vercel instead.
4. Redeploy the production frontend after changing variables.
5. Recheck:
   - `GET https://breadgo.vercel.app/api/upload/product-image`
6. Expected enabled response:

```json
{
  "enabled": true,
  "backend": "vercel_blob",
  "message": "Vercel Blob 이미지 업로드를 사용할 수 있습니다.",
  "missing_env": [],
  "auth_mode": "oidc"
}
```

## Security Check

- `BLOB_READ_WRITE_TOKEN` value was not printed.
- No storage token, access key, or secret key was added to docs.
- No DB schema change.
- No migration added.

## Validation Results

Executed during Phase 154:

- `git status`: PASS, documentation-only changes
- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS, 15 passed, 1 warning
- `npm run lint`: PASS
- `npm run build`: PASS

## Suggested Commit Message

`Document Vercel Blob upload live verification`
