# Phase 150 v0.1.5 Pre-release Site Check

## Purpose

Verify the deployed BreadGo site before the v0.1.5 Release.

Checked areas:

- Google OAuth customer login readiness
- Signup role separation
- Role-based login redirect and navigation
- Site performance and backend cold start behavior
- Product image upload fallback when storage is not configured
- Secret/token/key non-disclosure

## Deployment Targets

- Frontend: `https://breadgo.vercel.app`
- Backend: `https://breadgo-api.onrender.com`
- Current local/origin main: `cfb03dc75faa17ff32ccd337fe1319d7b39b7b82`

## Vercel Frontend Check

Static page checks:

| URL | Result | Notes |
| --- | --- | --- |
| `/login` | 200 | Google button text present |
| `/register` | 200 | Google button and merchant application CTA present |
| `/merchant/apply` | 200 | Merchant application screen present |
| `/merchant/products` | 200 | Merchant product page reachable |
| `/admin` | 200 | Admin page reachable |

The frontend is considered updated for the image upload fallback because production returned the new Korean storage-disabled response from:

- `https://breadgo.vercel.app/api/upload/product-image`

Response summary:

- `enabled=false`
- `backend=none`
- `message=이미지 파일 업로드 storage가 설정되지 않았습니다. 이미지 URL 직접 입력은 계속 사용할 수 있습니다.`
- `missing_env=["BLOB_READ_WRITE_TOKEN"]`

No secret/key values were returned.

## Render Backend Check

Backend checks:

| Endpoint | Result |
| --- | --- |
| `/health` | first request timed out once at 60 seconds, later returned 200 |
| `/health` warm retry | 200, about 2.7 seconds in this run |
| `/api/v1/auth/google/status` | 200, `enabled=true` |
| `/api/v1/auth/google/start` | 302 to `accounts.google.com` |

The backend is functional, but Render cold/sleep latency is still visible.

## Google OAuth Check

Confirmed:

- `/login` page shows `Google로 계속하기`.
- Backend status endpoint returns `enabled=true`.
- OAuth start endpoint redirects to Google authorization host.
- Redirect includes OAuth redirect/client parameters without exposing secret values in logs/docs.

Not repeated in this automated check:

- Full Google account login completion, because that requires an interactive Google account credential.

Reference:

- Phase 144 already verified live Google login success after the Render `GOOGLE_CLIENT_ID` correction.

## Role-based Login / Access Check

Production backend login responses:

| Account | Role |
| --- | --- |
| `customer@breadgo.test` | `customer` |
| `merchant@breadgo.test` | `merchant` |
| `admin@breadgo.test` | `admin` |

Access checks:

| Check | Result |
| --- | --- |
| customer token -> `/api/v1/merchants/me` | blocked by missing merchant profile |
| merchant token -> `/api/v1/admin/summary` | 403 |
| admin token -> `/api/v1/admin/merchant-applications` | 200 |
| public signup with `role=merchant` | 403 |

Expected frontend redirects remain:

- customer -> `/products`
- merchant -> `/merchant`
- admin -> `/admin`

Expected NavBar branches remain:

- customer: 상품 보기, 내 예약, 내 결제
- merchant: 가맹점 홈, 상품관리, 주문관리, 픽업, POS, 재고 이력
- admin: Admin, 운영 점검, Pro 운영, Batch Monitor

Browser-level click automation was limited in this environment, so final visual navigation should be spot-checked manually after Vercel deployment if needed.

## Signup Role Separation

Confirmed:

- `/register` is customer signup oriented.
- Google OAuth remains customer-only.
- `/merchant/apply` is reachable for merchant application.
- Public `role=merchant` signup is blocked with 403.
- Admin merchant application API is reachable with admin credentials.

## Image Upload Fallback

Confirmed production behavior:

- File upload storage is currently not configured.
- The production upload status route returns a friendly Korean message.
- Missing environment variable names only are exposed.
- Image URL direct input remains available in the merchant product form.

Frontend code behavior:

- File input is disabled when storage is not configured.
- Upload button is disabled when storage is not configured.
- The image URL field is unchanged.

## Performance Check

Measured from local machine:

| URL | Approx time |
| --- | --- |
| `https://breadgo.vercel.app/login` | 4027 ms |
| `https://breadgo.vercel.app/register` | 932 ms |
| `https://breadgo.vercel.app/merchant/apply` | 964 ms |
| `https://breadgo.vercel.app/merchant/products` | 573 ms |
| `https://breadgo.vercel.app/admin` | 1232 ms |

Backend:

- First `/health` request in this run timed out at 60 seconds.
- Later `/health` response returned 200.
- OAuth status warm response returned in about 323 ms.

Conclusion:

- Frontend page delivery is generally acceptable after warm-up.
- Backend cold/sleep remains the largest intermittent latency source.
- v0.1.5 frontend changes reduce avoidable auth/nav revalidation, but cannot fully remove Render cold start latency.

## Secret / Token / Key Check

- No `GOOGLE_CLIENT_SECRET` value was printed or documented.
- No Google token was printed or documented.
- No storage access key or secret key was printed or documented.
- Production upload status response included missing env names only.

## Validation Results

- `git status`: PASS, local working tree contains only documentation/front-end changes for current pre-release checks and prior Phase 149 work.
- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS after starting local FastAPI on `127.0.0.1:8000`.
- `python -m pytest tests -q`: PASS, 15 passed.
- `npm run lint`: PASS
- `npm run build`: PASS

## DB / Migration

No DB schema change.

No migration added.

## Remaining Notes

- Google full login should be manually spot-checked with an authorized Google test account before publishing the final GitHub Release.
- Render backend cold/sleep can still make the first backend-dependent click feel slow.
- Image file upload requires storage environment variables in Vercel before actual file uploads are enabled.

## Suggested Commit Message

`Document v0.1.5 pre-release site check`
