# BreadGo MVP

BreadGo는 동네 빵집의 마감 할인 상품을 고객이 예약하고, 결제하고, 픽업 또는 배송 요청까지 할 수 있는 로컬 푸드 리스큐 마켓플레이스 MVP입니다.

현재 프로젝트는 웹 MVP와 Flutter 고객 앱 MVP가 모두 데모 가능한 수준까지 구현되어 있습니다. 실제 PG 결제, 실제 배송 API, Push/Firebase, 실제 외부 알림 채널은 아직 연결하지 않았고, 서비스 흐름 검증을 위한 Mock 결제/환불과 운영 준비 구조를 포함합니다.

## 배포 URL

- 프론트엔드: [https://breadgo.vercel.app](https://breadgo.vercel.app)
- 백엔드: [https://breadgo-api.onrender.com](https://breadgo-api.onrender.com)
- Health Check: [https://breadgo-api.onrender.com/health](https://breadgo-api.onrender.com/health)
- Swagger: [https://breadgo-api.onrender.com/docs](https://breadgo-api.onrender.com/docs)
- 데모 가이드: [https://breadgo.vercel.app/demo](https://breadgo.vercel.app/demo)

Render 무료 인스턴스는 일정 시간 요청이 없으면 sleep 상태가 될 수 있습니다. 첫 요청은 느릴 수 있습니다.

## Demo Ready Release

- Current demo tag: `v0.1.1-demo-ready`
- Official public demo release 기준: `v0.1.1-demo-ready`
- GitHub Release: [v0.1.1-demo-ready](https://github.com/keny40/breadgo/releases/tag/v0.1.1-demo-ready)
- v0.1.2 stabilized release: [v0.1.2-demo-stabilized](https://github.com/keny40/breadgo/releases/tag/v0.1.2-demo-stabilized)
- v0.1.2 completion: [Phase 122 Release Completion](docs/release-completion-phase122.md)
- Release completion: [Phase 112 Release Completion](docs/release-completion-phase112.md)
- Operations stabilization: [Phase 113 Operations Stabilization](docs/operations-stabilization-phase113.md)
- Operations troubleshooting: [Operations Troubleshooting Guide](docs/operations-troubleshooting-guide.md)
- Environment reference: [Environment Reference](docs/environment-reference.md)
- Demo walkthrough: [Demo Walkthrough v0.1.1](docs/demo-walkthrough-v0.1.1.md)
- Demo UX final review: [Phase 123 Demo UX Final Review](docs/demo-ux-final-review-phase123.md)
- Admin operations report: [Phase 124 Admin Operations Report](docs/admin-operations-report-phase124.md)
- v0.1.2 scope candidate: [v0.1.2 Scope Candidate](docs/v0.1.2-scope-candidate.md)
- v0.1.2 release checklist: [Release Checklist v0.1.2](docs/release-checklist-v0.1.2.md)
- v0.1.2 post-release verification: [Post-release Verification v0.1.2](docs/post-release-verification-v0.1.2.md)
- v0.1.2 release note draft: [Release Note v0.1.2](docs/release-note-v0.1.2.md)
- v0.1.2 RC check: [Release Candidate Check Phase 118](docs/release-candidate-check-phase118.md)
- GitHub Release draft: [GitHub Release v0.1.1 Demo Ready](docs/github-release-v0.1.1-demo-ready.md)
- Final release note: [Release Note v0.1.1](docs/release-note-v0.1.1.md)
- GitHub Release publish guide: [GitHub Release Publish Guide](docs/github-release-publish-guide.md)
- Post-release verification: [Post-release Verification v0.1.1](docs/post-release-verification-v0.1.1.md)
- Release notes: [BreadGo MVP Demo Ready Release](docs/release-notes-v0.1.1-demo-ready.md)
- Demo handoff: [Demo Handoff Pack](docs/demo-handoff-pack.md)
- Demo quickstart: [Pro Demo Quickstart](docs/pro-demo-quickstart.md)

## 데모 계정

```text
customer@breadgo.test / 12345678
merchant@breadgo.test / 12345678
admin@breadgo.test / 12345678
```

## 데모 실행 순서

1. Backend migration과 seed를 실행합니다.
2. Backend server를 실행합니다.
3. Frontend dev server를 실행하고 [`/demo`](https://breadgo.vercel.app/demo)를 엽니다.
4. `/demo`의 역할별 시작 버튼을 따라 고객 예약/Mock 결제 → 가맹점 픽업 → 관리자 Pro Operations → 점주 Weekly Report 알림 순서로 시연합니다.
5. 문제가 생기면 [Operations Troubleshooting Guide](docs/operations-troubleshooting-guide.md)를 확인합니다.

자세한 시연 스크립트는 [Demo Walkthrough v0.1.1](docs/demo-walkthrough-v0.1.1.md)을 참고하세요.

## 프로젝트 개요

BreadGo는 한국판 Too Good To Go를 목표로 하는 마감할인 푸드 플랫폼 MVP입니다. 동네 빵집과 소규모 식품 매장이 당일 남는 상품을 할인 판매하고, 소비자는 지역 기반으로 상품을 예약한 뒤 Mock 결제와 픽업/배송 요청 흐름을 확인할 수 있습니다.

역할은 세 가지입니다.

- 소비자: 지역 상품 탐색, 예약, Mock 결제, 픽업 코드 확인, 예약/결제/알림 확인
- 점주: 매장/상품/재고/주문/픽업/배송 상태/정산 확인
- 관리자: 사용자/가맹점/상품/예약/결제/정산/운영 상태 확인

BreadGo Pro는 점주용 수율 관리 엔진입니다. 단순 마감 할인앱을 넘어 수율 대시보드, 추천 재고/할인가, Weekly Report, Inventory Ledger, CSV/POS 준비 기능, 운영 알림, 관리자 Pro Operations 도구를 제공합니다.

## 기술 스택

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL, JWT
- Frontend: Next.js, React, TypeScript, Vercel Blob 이미지 업로드
- Mobile: Flutter 고객 앱 MVP
- Operations: Python CLI scripts, smoke test, rule-based health/audit/reporting flow
- External integrations: 실제 PG/배송/이메일/카카오/Push/Slack/Webhook은 아직 연결하지 않으며 Mock 또는 skeleton 구조만 포함

## BreadGo Pro 운영 기능

- 점주 Pro 대시보드와 Daily Brief
- Weekly Pro Report 생성, 저장, export, archive
- Weekly Report scheduler CLI
- Weekly Report batch monitor, retry failed
- Delivery preview와 BreadGo 내부 in-app mock delivery
- Merchant Weekly Report notification 읽음/미확인 처리
- Notification analytics와 unread reminder
- Admin Pro Operations Dashboard와 Quick Actions
- Pro Operations Audit Trail, Audit Log Explorer, CSV export, purge preview/execute
- Pro Operations Health Check
- Health Alert mock flow와 Health Alert CLI scheduler

자세한 데모 준비 문서는 [Pro 운영 데모 준비 문서](docs/pro-operations-demo-readiness.md)와 [Pro Demo Quickstart](docs/pro-demo-quickstart.md)를 참고하세요.

## 현재 MVP 진행 상태

### 웹 MVP 완료 기능

고객:

- 회원가입, 로그인, 로그아웃
- 역할 기반 리다이렉트와 접근 제한
- 지역 기반 상품 탐색
- 브라우저 현재 위치 기반 근처 상품 탐색
- 지도 기반 상품 탐색 UI
- 상품 이미지 표시
- 상품별 수령 방식 선택
  - 매장 직접 픽업
  - 퀵배달 요청
  - 택배 배송
- 상품별 수령 가능 방식과 배송비 반영
- 예약 생성
- Mock 결제
- 내 예약 확인
- 내 결제 확인
- 픽업 코드 확인
- 예약 취소
- Mock 환불 상태 확인
- 예약 상태 이력 확인
- 인앱 알림 확인 및 읽음 처리

가맹점:

- 가맹점 등록
- 가맹점 대시보드
- 매장 등록 및 관리
- 매장 지역 정보 등록
- 상품 등록, 수정, 재고 수정
- 상품 대표 이미지 URL 등록
- Vercel Blob 기반 상품 이미지 업로드
- 상품 숨김 처리 및 다시 판매
- 상품별 수령 가능 방식과 배송비 설정
- 주문 관리
- 픽업 코드 조회 및 픽업 확정
- 배송 상태 수동 변경
- 정산 내역 확인
- 정산 계좌 등록 및 수정
- 주문 상태 이력 확인
- 인앱 알림 확인 및 읽음 처리

관리자:

- 관리자 대시보드
- 사용자, 가맹점, 매장, 상품, 예약, 결제 목록 확인
- 가맹점 승인 상태 변경
- 배송 상태 변경
- 정산 관리
- 정산 완료/보류 처리
- 예약 상태 이력 확인
- 인앱 알림 확인 및 읽음 처리
- 운영 점검 화면

### Flutter 고객 앱 MVP 완료 기능

Flutter 앱은 [mobile/README.md](mobile/README.md)에 별도 실행 문서가 있습니다.

- 고객 로그인
- 지역 기반 상품 목록 조회
- 상품 상세 조회
- 수령 방식 선택
- 예약 생성
- Mock 결제
- 내 예약 조회
- 예약 취소 및 Mock 환불 상태 확인
- 인앱 알림 조회
- 알림 개별 읽음 처리
- 알림 모두 읽음 처리
- 예약 상태 이력 bottom sheet 확인
- Android emulator 기본 API 주소 `http://10.0.2.2:8000`
- `--dart-define=BREADGO_API_BASE_URL=...`로 API 주소 변경 지원

### 운영 전환 준비 완료 항목

- 결제 Provider 구조 준비
  - Mock provider 유지
  - Toss provider skeleton 추가
- 알림 Channel 구조 준비
  - In-app channel 유지
  - Email/SMS/Kakao Alimtalk/Push skeleton 추가
- 운영 모니터링/로깅 준비
  - Python logging 공통 설정
  - `/api/v1/ops/status`
  - `/admin/ops`
  - Slack/Sentry incident notifier skeleton
- 백엔드 smoke test 스크립트
- Render/Vercel/Neon 배포 문서
- Vercel Blob 이미지 업로드 문서

## 추천 데모 흐름

자세한 통합 데모 시나리오는 [docs/demo-scenario-v0.3.0.md](docs/demo-scenario-v0.3.0.md)를 참고하세요.

고객 웹:

1. `customer@breadgo.test`로 로그인
2. `/products`에서 지역 선택 또는 내 위치로 찾기
3. 상품 선택
4. 수령 방식 선택
5. 예약 생성
6. Mock 결제
7. `/my-reservations`에서 픽업 코드와 상태 확인
8. 예약 상태 이력 확인
9. `/my-payments`에서 결제 상태 확인
10. `/notifications`에서 알림 확인

가맹점 웹:

1. `merchant@breadgo.test`로 로그인
2. `/merchant`에서 대시보드 확인
3. `/merchant/stores`에서 매장 확인
4. `/merchant/products`에서 상품 등록/수정/숨김 처리
5. `/merchant/orders`에서 주문 확인
6. 픽업 주문은 픽업 확정
7. 배송 주문은 배송 상태 변경
8. `/merchant/settlements`에서 정산 내역 확인

관리자 웹:

1. `admin@breadgo.test`로 로그인
2. `/admin`에서 전체 운영 현황 확인
3. 사용자, 가맹점, 매장, 상품, 예약, 결제 확인
4. `/admin/settlements`에서 정산 관리
5. `/admin/ops`에서 운영 점검 상태 확인

Flutter 고객 앱:

1. 고객 계정으로 로그인
2. 상품 목록 확인
3. 상품 상세에서 수령 방식 선택
4. 예약 생성 후 Mock 결제
5. 내 예약 확인
6. 상태 이력 확인
7. 예약 취소 및 Mock 환불 상태 확인
8. 알림 확인 및 읽음 처리

## 로컬 개발 실행

Docker 없이 로컬 Windows PostgreSQL 기준으로 실행합니다.

### 백엔드

```powershell
cd backend
.\.venv\Scripts\activate
python -m alembic upgrade head
python scripts/seed_demo.py
python -m uvicorn app.main:app --reload --port 8000
```

가상환경을 사용하지 않는 경우에도 `backend` 폴더에서 동일한 Python 명령을 실행하면 됩니다.

### 백엔드 Smoke Test

백엔드 서버가 실행 중인 상태에서 다른 터미널에서 실행합니다.

```powershell
cd backend
python scripts/smoke_test.py
```

Smoke test는 고객 예약/Mock 결제/픽업 흐름과 함께 Admin Pro Operations read-only API, Weekly Report batch 조회, Health Alert 목록, merchant 권한 차단까지 확인합니다.

### Pro 운영 CLI

Weekly Report scheduler MVP:

```powershell
cd backend
python scripts/run_weekly_report_batch.py
```

Health Alert scheduler MVP:

```powershell
cd backend
python scripts/run_pro_health_alert_check.py
```

두 CLI 모두 실제 외부 발송을 수행하지 않습니다. 운영 서버 cron 등록 예시는 [Weekly Report batch runbook](docs/weekly-report-batch-runbook.md)과 [Health Alert scheduler runbook](docs/pro-health-alert-scheduler-runbook.md)을 참고하세요.

### 웹 프론트엔드

```powershell
cd frontend
npm install
npm run dev
```

브라우저에서 [http://localhost:3000/demo](http://localhost:3000/demo)을 엽니다.

### Flutter 모바일 앱

자세한 내용은 [mobile/README.md](mobile/README.md)를 참고하세요.

Android emulator에서 로컬 백엔드에 연결:

```powershell
cd mobile
flutter pub get
flutter run --dart-define=BREADGO_API_BASE_URL=http://10.0.2.2:8000
```

Render 배포 백엔드에 연결:

```powershell
cd mobile
flutter run --dart-define=BREADGO_API_BASE_URL=https://breadgo-api.onrender.com
```

## 검증 명령

백엔드:

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/seed_demo.py
python scripts/smoke_test.py
python scripts/run_weekly_report_batch.py
python scripts/run_pro_health_alert_check.py
```

웹 프론트엔드:

```powershell
cd frontend
npm run lint
npm run build
```

Flutter:

```powershell
cd mobile
flutter pub get
dart format lib test
flutter analyze --no-pub
flutter test --no-pub
```

## 환경 변수

백엔드:

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
JWT_SECRET_KEY=replace-with-secure-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
PYTHON_VERSION=3.12.8
```

배포 환경에서는 `BACKEND_CORS_ORIGINS`에 Vercel URL을 포함해야 합니다.

```text
BACKEND_CORS_ORIGINS=["https://breadgo.vercel.app"]
```

웹 프론트엔드:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
BLOB_READ_WRITE_TOKEN=replace-with-vercel-blob-token
```

배포 환경:

```text
NEXT_PUBLIC_API_BASE_URL=https://breadgo-api.onrender.com
BLOB_READ_WRITE_TOKEN=replace-with-vercel-blob-token
```

Flutter:

```text
BREADGO_API_BASE_URL=http://10.0.2.2:8000
```

Flutter는 `--dart-define`으로 API 주소를 넘깁니다.

## 배포 개요

Render 백엔드:

- Root directory: `backend`
- Install command: `pip install -r requirements.txt`
- Migration command: `python -m alembic upgrade head`
- Start command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Vercel 프론트엔드:

- Root directory: `frontend`
- Install command: `npm install`
- Build command: `npm run build`
- Required env: `NEXT_PUBLIC_API_BASE_URL`, `BLOB_READ_WRITE_TOKEN`

Neon PostgreSQL:

- Render `DATABASE_URL`에 Neon PostgreSQL connection string 설정
- 배포 후 Alembic migration 실행 필요

## 현재 한계

- 실제 PG 결제 연동 없음
- 실제 카드 환불 없음
- Mock 결제/Mock 환불 상태만 지원
- 실제 퀵배달/택배 API 연동 없음
- 실제 SMS, 카카오톡, 이메일, push 알림 없음
- 실제 Slack/Discord/Webhook 발송 없음
- 인앱 알림만 지원
- 실제 지도 SDK 없음
- Flutter 앱은 고객 앱만 구현
- Flutter JWT 보안 저장소 미적용
- 앱스토어 배포 설정 없음
- 운영용 이메일 인증 없음
- 비밀번호 재설정 없음
- 정산 계좌 암호화 미적용
- 실제 송금 없음
- Render 무료 인스턴스 sleep 가능
- 데모 계정은 운영 환경에서 사용하면 안 됨
- Weekly Report/Health Alert scheduler는 CLI와 runbook만 제공하며 실서버 cron 등록은 별도 작업 필요
- 자동 복구, 자동 purge scheduler, 세부 관리자 권한 분리, 대량 비동기 큐는 아직 없음
- 이메일, 전화번호, 주소, 외부 발송 토큰은 Pro 운영 로그/알림에 저장하거나 노출하지 않음

## 추천 다음 단계

1. Flutter 내 결제 화면 연결
2. Flutter JWT 보안 저장소 적용
3. 실제 Toss Payments 연동
4. 실제 알림 채널 연동
5. 지도 SDK 기반 위치 탐색 고도화
6. 이메일 인증과 비밀번호 재설정
7. 정산 계좌 암호화
8. 가맹점 모바일 앱
9. 운영 모니터링 실제 Sentry/Slack 연동
10. 리뷰/평점/포인트/쿠폰
11. AI 수요 예측과 할인 추천

## 관련 문서

- [CHANGELOG](CHANGELOG.md)
- [GitHub Release v0.1.1 Demo Ready](docs/github-release-v0.1.1-demo-ready.md)
- [Phase 112 Release Completion](docs/release-completion-phase112.md)
- [Phase 113 Operations Stabilization](docs/operations-stabilization-phase113.md)
- [Operations Troubleshooting Guide](docs/operations-troubleshooting-guide.md)
- [Environment Reference](docs/environment-reference.md)
- [Demo Walkthrough v0.1.1](docs/demo-walkthrough-v0.1.1.md)
- [v0.1.2 Scope Candidate](docs/v0.1.2-scope-candidate.md)
- [Release Checklist v0.1.2](docs/release-checklist-v0.1.2.md)
- [Post-release Verification v0.1.2](docs/post-release-verification-v0.1.2.md)
- [Release Note v0.1.2](docs/release-note-v0.1.2.md)
- [Release Candidate Check Phase 118](docs/release-candidate-check-phase118.md)
- [Release Note v0.1.1](docs/release-note-v0.1.1.md)
- [GitHub Release Publish Guide](docs/github-release-publish-guide.md)
- [Post-release Verification v0.1.1](docs/post-release-verification-v0.1.1.md)
- [Release Notes v0.1.1 Demo Ready](docs/release-notes-v0.1.1-demo-ready.md)
- [Demo Handoff Pack](docs/demo-handoff-pack.md)
- [MVP 기능 요약](docs/mvp-feature-summary.md)
- [데모 계정과 시나리오](docs/demo-accounts-and-scenarios.md)
- [최종 릴리즈 체크리스트](docs/final-release-checklist.md)
- [Pro 운영 데모 준비 문서](docs/pro-operations-demo-readiness.md)
- [Pro Demo Quickstart](docs/pro-demo-quickstart.md)
- [Weekly Report batch runbook](docs/weekly-report-batch-runbook.md)
- [Health Alert scheduler runbook](docs/pro-health-alert-scheduler-runbook.md)
- [Audit Log 보관 정책](docs/pro-audit-log-retention-policy.md)
- [통합 데모 시나리오 v0.3.0](docs/demo-scenario-v0.3.0.md)
- [통합 릴리즈 요약 v0.3.0](docs/release-summary-v0.3.0.md)
- [릴리즈 노트 v0.3.0](docs/release-note-v0.3.0.md)
- [GitHub Release 본문 v0.3.0](docs/github-release-v0.3.0.md)
- [태그 생성 가이드 v0.3.0](docs/tagging-guide-v0.3.0.md)
- [릴리즈 발행 결과 v0.3.0](docs/release-publish-result-v0.3.0.md)
- [배포 환경 점검 체크리스트 v0.3.0](docs/deployment-checklist-v0.3.0.md)
- [운영 URL Smoke Test v0.3.0](docs/production-smoke-test-v0.3.0.md)
- [운영 URL Smoke Test 결과 v0.3.0](docs/production-smoke-result-v0.3.0.md)
- [Phase 49 릴리즈 체크](docs/release-check-phase49.md)
- [Phase 48 릴리즈 체크](docs/release-check-phase48.md)
- [Phase 46 릴리즈 체크](docs/release-check-phase46.md)
- [Phase 47 릴리즈 체크](docs/release-check-phase47.md)
- [Phase 45 릴리즈 체크](docs/release-check-phase45.md)
- [Flutter 모바일 앱 README](mobile/README.md)
- [배포 체크리스트 v0.1.0](docs/deployment-checklist-v0.1.0.md)
- [결제 Provider 설계](docs/payment-provider-design-phase37.md)
- [알림 Channel 설계](docs/notification-channel-design-phase38.md)
- [운영 모니터링 설계](docs/ops-monitoring-design-phase39.md)
