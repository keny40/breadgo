# BreadGo v0.3.0 운영 URL Smoke Test 결과

## 작성 목적

이 문서는 BreadGo v0.3.0 데모 릴리즈 후보의 운영 URL 기준 smoke test 수행 결과를 기록합니다.
기준 문서:

```text
docs/production-smoke-test-v0.3.0.md
```

직접 확인한 항목만 `PASS`로 기록했습니다.
브라우저에서 직접 조작하지 않았거나 운영 DB 데이터를 변경할 수 있는 항목은 `NOT TESTED` 또는 `SKIP`으로 표시했습니다.

## 테스트 기준 URL

- Frontend: [https://breadgo.vercel.app](https://breadgo.vercel.app)
- Backend: [https://breadgo-api.onrender.com](https://breadgo-api.onrender.com)
- Health: [https://breadgo-api.onrender.com/health](https://breadgo-api.onrender.com/health)
- Swagger: [https://breadgo-api.onrender.com/docs](https://breadgo-api.onrender.com/docs)

## 공개 URL 접속 결과

| 항목 | URL | 결과 | 기록 |
| --- | --- | --- | --- |
| 프론트엔드 홈 | `https://breadgo.vercel.app` | PASS | HTTP 200, HTML 응답 확인, 약 2.6초 |
| 데모 페이지 | `https://breadgo.vercel.app/demo` | PASS | HTTP 200, HTML 응답 확인, 약 0.8초 |
| 백엔드 health | `https://breadgo-api.onrender.com/health` | PASS | HTTP 200, `{"status":"ok"}` 확인, 약 14.1초 |
| 백엔드 Swagger | `https://breadgo-api.onrender.com/docs` | PASS | HTTP 200, Swagger HTML 응답 확인, 약 0.3초 |

## Render Sleep 기록

- `/health` 첫 확인 응답이 약 14.1초로 다른 요청보다 느렸습니다.
- 이는 Render free instance cold start 또는 sleep 해제 영향일 수 있습니다.
- 이후 Swagger 요청은 약 0.3초로 빠르게 응답했습니다.
- 데모 시작 전 `/health`를 먼저 호출해 Render instance를 깨우는 것을 권장합니다.

## 읽기 중심 API 확인 결과

운영 DB 변경을 피하기 위해 로그인과 조회 중심 API만 확인했습니다.
Access token 값은 문서에 기록하지 않습니다.

| 항목 | 결과 | 기록 |
| --- | --- | --- |
| 고객 API 로그인 | PASS | `customer@breadgo.test` 로그인 성공 |
| 지역 상품 API | PASS | 역삼동 상품 `count=3` 확인 |
| 고객 내 예약 API | PASS | 예약 `count=4` 확인 |
| 고객 알림 API | PASS | 알림 `count=0` 확인 |
| 가맹점 API 로그인 | PASS | `merchant@breadgo.test` 로그인 성공 |
| 가맹점 예약/주문 API | PASS | 주문 `count=5` 확인 |
| 관리자 API 로그인 | PASS | `admin@breadgo.test` 로그인 성공 |
| 관리자 summary API | PASS | `users=4`, `reservations=5` 확인 |
| 관리자 ops API | PASS | `app=ok`, `db=ok` 확인 |

## 고객 데모 흐름 결과

| 항목 | 결과 | 기록 |
| --- | --- | --- |
| 고객 로그인 | PASS | API 로그인으로 확인. 브라우저 UI 로그인은 NOT TESTED |
| 상품 목록 확인 | PASS | 공개 상품 API로 역삼동 상품 3개 확인. 브라우저 UI 상세 표시는 NOT TESTED |
| 예약 생성 | SKIP | 운영 DB 변경을 피하기 위해 이번 결과 기록에서는 실행하지 않음 |
| Mock 결제 | SKIP | 운영 DB 변경을 피하기 위해 이번 결과 기록에서는 실행하지 않음 |
| 내 예약 확인 | PASS | API로 내 예약 목록 조회 성공 |
| 알림 확인 | PASS | API로 알림 목록 조회 성공 |
| 예약 상태 이력 확인 | NOT TESTED | 특정 예약 상세 이력 조회는 이번 결과 기록에서 수행하지 않음 |

## 가맹점 데모 흐름 결과

| 항목 | 결과 | 기록 |
| --- | --- | --- |
| 가맹점 로그인 | PASS | API 로그인으로 확인. 브라우저 UI 로그인은 NOT TESTED |
| 주문 확인 | PASS | API로 가맹점 예약/주문 목록 조회 성공 |
| 픽업 확정 | SKIP | 운영 DB 상태 변경을 피하기 위해 실행하지 않음 |
| 배송 상태 변경 | SKIP | 운영 DB 상태 변경을 피하기 위해 실행하지 않음 |
| 정산 내역 확인 | NOT TESTED | 이번 결과 기록에서 별도 API/브라우저 확인하지 않음 |

## 관리자 데모 흐름 결과

| 항목 | 결과 | 기록 |
| --- | --- | --- |
| 관리자 로그인 | PASS | API 로그인으로 확인. 브라우저 UI 로그인은 NOT TESTED |
| 대시보드 확인 | PASS | 관리자 summary API 응답 확인 |
| 정산 관리 확인 | NOT TESTED | 이번 결과 기록에서 별도 API/브라우저 확인하지 않음 |
| 예약 상태 이력 확인 | NOT TESTED | 이번 결과 기록에서 별도 확인하지 않음 |
| `/admin/ops` 운영 점검 확인 | PASS | 관리자 ops API에서 `app=ok`, `db=ok` 확인. 브라우저 UI는 NOT TESTED |

## 환경 변수 점검 결과

실제 secret 값은 확인하거나 기록하지 않았습니다.
설정 여부는 운영 URL 동작 결과와 문서 기준으로만 판단했습니다.

| 환경 변수 | 대상 | 결과 | 기록 |
| --- | --- | --- | --- |
| `DATABASE_URL` | Render Backend | OK | `/health`, 관리자 ops DB 상태 `ok`로 간접 확인 |
| `JWT_SECRET_KEY` | Render Backend | OK | 고객/가맹점/관리자 로그인 및 인증 API 동작으로 간접 확인 |
| `JWT_ALGORITHM` | Render Backend | OK | JWT 인증 API 동작으로 간접 확인 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Render Backend | NOT CHECKED | 실제 값 확인하지 않음 |
| `BACKEND_CORS_ORIGINS` | Render Backend | NOT CHECKED | 브라우저 CORS 직접 확인은 수행하지 않음 |
| `PYTHON_VERSION` | Render Backend | NOT CHECKED | Render 설정값 직접 확인하지 않음 |
| `NEXT_PUBLIC_API_BASE_URL` | Vercel Frontend | NOT CHECKED | Vercel 설정값 직접 확인하지 않음 |
| `BLOB_READ_WRITE_TOKEN` | Vercel Frontend | NOT CHECKED | 이미지 업로드 직접 확인하지 않음 |
| `BREADGO_API_BASE_URL` | Flutter | NOT CHECKED | 운영 Flutter 실행은 이번 결과 기록에서 수행하지 않음 |

## 배포 이슈/조치사항

| 항목 | 내용 |
| --- | --- |
| 발견된 이슈 | 현재 문서 작성 시점에서 기록된 이슈 없음 |
| 원인 추정 | `/health` 첫 응답이 약 14.1초로 느렸으며 Render free instance sleep 영향 가능성 있음 |
| 조치 여부 | 데모 전 `/health` 호출 권장 사항 문서화 |
| 후속 작업 | 운영 URL 브라우저 수동 시나리오 전체 수행 권장 |

## 최종 판단

- 공개 URL과 읽기 중심 API는 정상 응답했습니다.
- 운영 DB를 변경하는 예약 생성, Mock 결제, 픽업 확정, 배송 상태 변경은 이번 결과 기록에서 실행하지 않았습니다.
- v0.3.0 데모 전에는 `docs/production-smoke-test-v0.3.0.md`에 따라 브라우저 기반 수동 smoke test를 한 번 더 수행하는 것을 권장합니다.
