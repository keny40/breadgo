# Vercel Blob OIDC Upload Support

## Purpose

Support Vercel Blob project connections that use OIDC instead of a long-lived `BLOB_READ_WRITE_TOKEN`.

## Diagnosis

The BreadGo production Blob Store `breadgo-blob` is connected to the Vercel project through OIDC.

Observed Vercel state:

- Blob Store exists.
- Access is Public.
- Project `breadgo` is connected for Production and Preview.
- Vercel Storage shows `BLOB_STORE_ID` and `BLOB_WEBHOOK_PUBLIC_KEY`.
- Vercel UI says connected projects are connected via OIDC.
- `BLOB_READ_WRITE_TOKEN` is not created automatically.

Before this update, BreadGo treated Vercel Blob as enabled only when `BLOB_READ_WRITE_TOKEN` existed. That caused production status to return:

```json
{
  "enabled": false,
  "backend": "none",
  "missing_env": ["BLOB_READ_WRITE_TOKEN"]
}
```

## Official Vercel Blob Authentication Model

Current `@vercel/blob` supports OIDC on Vercel deployments.

For Vercel-hosted server code:

- `BLOB_STORE_ID` identifies the Blob Store.
- `VERCEL_OIDC_TOKEN` is populated and rotated by Vercel at runtime.
- `put()` can authenticate through OIDC without a long-lived `BLOB_READ_WRITE_TOKEN`.

Use `BLOB_READ_WRITE_TOKEN` only for non-OIDC environments, local development that does not have an OIDC token, or workflows that explicitly need a static read-write token.

## Code Change

`frontend/app/api/upload/product-image/route.ts` now treats Vercel Blob as enabled when either condition is true:

1. `BLOB_READ_WRITE_TOKEN` exists.
2. `BLOB_STORE_ID` and `VERCEL_OIDC_TOKEN` both exist.

The endpoint also returns `auth_mode`:

- `oidc`
- `read_write_token`
- `none`

Expected production status after Vercel redeploy:

```json
{
  "enabled": true,
  "backend": "vercel_blob",
  "message": "Vercel Blob 이미지 업로드를 사용할 수 있습니다.",
  "missing_env": [],
  "auth_mode": "oidc"
}
```

## Vercel Settings

For OIDC mode on Vercel:

```text
IMAGE_UPLOAD_ENABLED=true
STORAGE_BACKEND=vercel_blob
BLOB_STORE_ID=<provided by Vercel Blob project connection>
```

`VERCEL_OIDC_TOKEN` is provided by Vercel at runtime and normally does not appear as a manually editable environment variable.

Do not add the actual token value to code, docs, logs, screenshots, or test fixtures.

## Retest Steps

After pushing this change and redeploying Vercel:

1. Open `https://breadgo.vercel.app/api/upload/product-image`.
2. Confirm:
   - `enabled=true`
   - `backend=vercel_blob`
   - `auth_mode=oidc`
   - `missing_env=[]`
3. Log in as `merchant@breadgo.test`.
4. Open `/merchant/products`.
5. Confirm the file input and `이미지 업로드` button are enabled.
6. Upload a small JPG or PNG.
7. Confirm the returned `image_url` is a Vercel Blob public URL.
8. Register a product with that URL.
9. Confirm the product image appears on the product listing.

## Fallback Behavior

If OIDC variables are not present:

- File upload remains disabled.
- Manual image URL input remains available.
- The API reports missing environment variable names only.
- No secret values are exposed.

## Security

- No `BLOB_READ_WRITE_TOKEN` value was added.
- No OIDC token value was added.
- No access key, secret key, or webhook secret value was added.
- DB schema and migrations are unchanged.

