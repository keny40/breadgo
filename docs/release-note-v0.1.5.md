# Release Note Draft v0.1.5

## 상태

`v0.1.5`는 Google OAuth live 로그인과 role 기반 onboarding 안정화를 정리한 최종 Release 등록 준비 상태다.

- 현재 공식 최신 Release: `v0.1.4-readiness-ux-boundary` until the v0.1.5 GitHub Release is manually published
- v0.1.5 final tag: `v0.1.5-google-oauth-live`
- v0.1.5 earlier tag: `v0.1.5-google-oauth-role-onboarding`
- v0.1.5 GitHub Release: manual registration pending
- final tag is prepared separately from the earlier v0.1.5 tag
- 새 GitHub Release 생성 없음
- 기존 tag 삭제/이동 없음

## v0.1.5 목적

v0.1.5는 v0.1.4 이후 실제 데모 운영에 필요한 로그인/가입/역할 분리 흐름을 정리하는 release다.

이번 범위는 Google OAuth 고객 로그인 live 연동, 공개 회원가입 role 분리, 가맹점 입점 신청과 관리자 승인/반려, role 기반 redirect/navigation 안정화에 초점을 둔다.

## v0.1.4 대비 변경 요약

- Google OAuth 고객 로그인/회원가입 live 연동 검증
- Render backend OAuth status `enabled=true` 확인
- Google 실제 로그인 성공 확인
- 고객/가맹점/관리자 회원가입 역할 분리
- 가맹점 입점 신청에서 관리자 승인/반려까지의 onboarding 흐름 추가
- `role=merchant` / `role=admin` 공개 가입 차단
- merchant/admin Google 자동 가입 차단 정책 유지
- customer/merchant/admin 로그인 후 role 기반 기본 화면 이동 정리
- NavBar role별 메뉴 분기 정리
- `merchant3@breadgo.test` production role 데이터 기준 설명 추가

## Google OAuth Live Integration

확인된 production 설정:

- Frontend: `https://breadgo.vercel.app`
- Backend API: `https://breadgo-api.onrender.com`
- Status endpoint: `https://breadgo-api.onrender.com/api/v1/auth/google/status`
- Status result: `enabled=true`
- Redirect URI: `https://breadgo-api.onrender.com/api/v1/auth/google/callback`

Google OAuth는 customer 계정 전용이다.

- 기존 customer가 있으면 해당 customer로 로그인
- 기존 user가 없으면 customer role로 신규 생성
- `email_verified=false` profile은 차단
- admin/merchant 자동 Google 가입 없음
- Google access token / refresh token / id token은 DB에 저장하지 않음
- secret/token/key 값은 문서/코드/로그에 남기지 않음

## Signup Role Separation

공개 회원가입 정책:

- customer: 이메일/password 가입 가능
- customer: Google OAuth 가입/로그인 가능
- merchant: 공개 자동 가입 금지
- merchant: 입점 신청 후 관리자 승인 필요
- admin: 공개 회원가입 금지

공개 API에서 `role=merchant` 또는 `role=admin`을 직접 전달하면 차단한다.

## Merchant Application Flow

가맹점 onboarding 흐름:

1. 신청자가 `/merchant/apply`에서 입점 신청
2. backend가 `merchant_applications`에 `PENDING` 신청 저장
3. admin이 신청 목록/상세 확인
4. admin이 승인 또는 반려
5. 승인 시 merchant user/profile 활성화
6. 반려 시 상태와 사유 저장

기존 demo merchant 계정은 유지한다.

## Role Based Redirect / Navigation

로그인 후 기본 이동:

| Role | Default route | Primary nav |
| --- | --- | --- |
| `customer` | `/products` | 상품 보기, 내 예약, 내 결제 |
| `merchant` | `/merchant` | 가맹점 홈, 상품관리, 주문관리, 픽업, POS, 재고 이력 |
| `admin` | `/admin` | Admin, 운영 점검, Pro 운영, Batch Monitor |

NavBar는 저장된 user role과 `/auth/me` 기반 auth state를 사용한다. 로그인 세션 저장은 token과 user role을 함께 반영하여 role 미확인 중 customer 메뉴가 잘못 보이지 않도록 한다.

## Production Data Note

Production API 확인 기준:

- `customer@breadgo.test`: `customer`
- `merchant@breadgo.test`: `merchant`
- `admin@breadgo.test`: `admin`
- `merchant3@breadgo.test`: 현재 `customer`

따라서 `merchant3@breadgo.test`는 production DB에서 customer role인 데이터 상태이며, 해당 계정은 merchant 화면으로 redirect되지 않는다. 판매자 데모 기준 계정은 `merchant@breadgo.test`다.

## 포함 범위

- Google OAuth customer live verification
- customer-only Google OAuth policy
- signup role separation
- merchant application table/migration from Phase 145
- admin merchant application approve/reject flow
- role direct assignment blocking
- role based frontend redirect/navigation
- production deployment verification notes
- v0.1.5 release candidate documents

## 제외 범위

- admin Google signup
- merchant Google auto signup
- 실제 이메일 인증 고도화
- 비밀번호 재설정
- 세부 관리자 권한 분리
- 실명/사업자번호 외부 검증 API
- 실제 결제/배송/POS/외부 알림 API 신규 연동
- secret manager 고도화
- 새 tag 생성
- GitHub Release 생성

## Security / Secret Policy

- `GOOGLE_CLIENT_SECRET` 값은 repository에 저장하지 않는다.
- Google token, external API key, webhook URL은 문서/로그/코드에 남기지 않는다.
- Google OAuth token은 DB에 저장하지 않는다.
- admin/merchant 자동 권한 상승 경로를 만들지 않는다.

## DB Schema / Migration

v0.1.5 RC 기준 추가 DB 변경은 없다.

이 범위에서 사용하는 migration:

- `202606180024_create_merchant_applications.py`

Phase 148에서는 DB schema 변경 없음, migration 추가 없음.

## 검증 결과

Release Candidate 준비 기준으로 아래 명령을 실행한다.

- `python -m compileall app scripts`
- `python -m alembic upgrade head`
- `python scripts/seed_demo.py`
- `python scripts/smoke_test.py`
- `python -m pytest tests -q`
- `npm run lint`
- `npm run build`

실행 결과는 `docs/release-candidate-check-phase148.md`에 기록한다.

## 추천 Release 정보

- 추천 tag: `v0.1.5-google-oauth-role-onboarding`
- 추천 Release title: `BreadGo Google OAuth Role Onboarding Release v0.1.5`
- Release body source: `docs/release-note-v0.1.5.md`
- Target branch: `main`

## Release 생성 전 주의사항

- v0.1.5 tag는 아직 만들지 않는다.
- GitHub Release는 아직 만들지 않는다.
- production OAuth secret, token, key 값을 문서에 포함하지 않는다.
- `merchant3@breadgo.test`는 role 데이터가 customer임을 데모 전 명확히 설명한다.

## Suggested commit message

`Prepare v0.1.5 release candidate docs`
