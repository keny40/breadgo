# Demo Walkthrough v0.1.1

## 데모 목적

`v0.1.1-demo-ready` 기준 BreadGo MVP와 BreadGo Pro 운영 흐름을 외부 시연자가 처음부터 끝까지 이해할 수 있게 정리한다.

BreadGo는 한국판 Too Good To Go를 목표로 하는 마감할인 푸드 플랫폼 MVP이며, BreadGo Pro는 점주용 운영 코치 / 수율 관리 엔진이다.

이번 데모는 실제 결제, 배송, POS, 이메일, 카카오, Push, Slack, Discord, Webhook 연동을 포함하지 않는다. 모든 외부 연동성 흐름은 Mock 또는 내부 기록 방식으로만 동작한다.

## 로컬 실행 순서

## 1. Backend 준비

```powershell
cd backend
python -m alembic upgrade head
python scripts/seed_demo.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

정상 확인:

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing
```

응답에 `{"status":"ok"}`가 보이면 정상이다.

## 2. Frontend 실행

```powershell
cd frontend
npm run dev
```

브라우저에서 아래 화면을 연다.

```text
http://localhost:3000/demo
```

## 3. 검증 명령

Backend:

```powershell
cd backend
python -m compileall app scripts
python scripts/seed_demo.py
python scripts/smoke_test.py
python scripts/run_weekly_report_batch.py
python scripts/run_pro_health_alert_check.py
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

## 데모 계정

```text
customer@breadgo.test / 12345678
merchant@breadgo.test / 12345678
admin@breadgo.test / 12345678
```

## 고객 데모 흐름

1. `/login`에서 `customer@breadgo.test`로 로그인한다.
2. `/products`에서 지역 상품을 확인한다.
3. 서울특별시 / 강남구 / 역삼동 기준 상품을 선택한다.
4. 수량과 수령 방식을 선택해 예약한다.
5. Mock 결제를 진행한다.
6. `/my-reservations`에서 예약 상태와 픽업코드를 확인한다.
7. `/my-payments`에서 Mock 결제 상태를 확인한다.

강조할 점:

- 실제 PG 결제나 카드 청구는 없다.
- 배송 정보는 요청 정보 저장 단계이며 실제 배송 provider를 호출하지 않는다.
- 환불도 실제 카드 환불이 아닌 Mock 상태 변경이다.

## 점주 데모 흐름

1. `/login`에서 `merchant@breadgo.test`로 로그인한다.
2. `/merchant`에서 점주 대시보드를 확인한다.
3. `/merchant/products`에서 상품과 재고를 확인한다.
4. `/merchant/pickup`에서 고객 픽업코드로 수령을 확정한다.
5. `/merchant/pro`에서 BreadGo Pro 대시보드를 확인한다.
6. `/merchant/pro/weekly-report`에서 Weekly Report를 확인한다.
7. `/merchant/pro/weekly-report-notifications`에서 내부 Weekly Report 알림을 확인한다.

강조할 점:

- POS sync는 실제 외부 POS API 호출이 아니라 Mock POS sync다.
- Weekly Report 알림은 BreadGo 내부 알림이며 이메일/카카오/Push 발송이 아니다.
- Pro 추천과 인사이트는 실제 AI 모델이 아닌 rule-based MVP다.

## 관리자 데모 흐름

1. `/login`에서 `admin@breadgo.test`로 로그인한다.
2. `/admin`에서 전체 사용자/가맹점/예약/결제 현황을 확인한다.
3. `/admin/pro/operations`에서 Pro Operations Dashboard를 확인한다.
4. Quick Actions 영역에서 운영 액션의 의미를 설명한다.
5. `/admin/pro/weekly-report-batches`에서 batch run 이력을 확인한다.
6. `/admin/pro/weekly-report-deliveries`에서 delivery preview와 내부 알림 Mock 흐름을 확인한다.
7. `/admin/pro/operations/audit-logs`에서 운영 액션 audit trail을 확인한다.
8. `/admin/pro/operations/health-alerts`에서 Health Alert 확인/해결 흐름을 설명한다.

강조할 점:

- 실제 cron은 운영 문서에 예시만 있고, 로컬에서는 CLI로 실행한다.
- Delivery preview와 In-app mock delivery는 외부 발송이 아니다.
- Health Alert는 Slack/Discord/Webhook을 호출하지 않는 내부 관리자 alert다.

## Pro Operations 데모 흐름

권장 순서:

1. Operations Summary 확인
2. Health Check 상태 확인
3. Weekly Report batch 이력 확인
4. Delivery preview 생성 흐름 설명
5. In-app mock delivery 실행 결과 설명
6. Merchant notification 화면에서 내부 알림 확인
7. Audit Log Explorer에서 운영 액션 이력 확인
8. Health Alert 생성/확인/해결 흐름 설명

주의:

- 외부 발송 없음
- 개인정보/연락처/주소/외부 발송 토큰 저장 없음
- audit log CSV export는 운영 점검용이며 metadata 전체 export는 하지 않음

## Mock 처리 항목

- Mock payment
- Mock refund state
- Mock POS sync
- BreadGo 내부 in-app mock delivery
- Weekly Report scheduler CLI
- Health Alert scheduler CLI
- Health Alert mock flow
- Rule-based recommendation / insights

## 실제 미연동 항목

- 실제 PG 결제
- 실제 카드 환불
- 실제 배송 provider
- 실제 POS API
- 실제 이메일 발송
- 실제 카카오 발송
- 실제 Push 발송
- Slack / Discord / Webhook 발송
- 실제 AI 모델
- 실서버 cron 등록
- 대량 비동기 큐
- 세부 관리자 권한 분리

## 문제가 생겼을 때

아래 문서를 먼저 확인한다.

- [Operations Troubleshooting Guide](operations-troubleshooting-guide.md)
- [Environment Reference](environment-reference.md)
- [Pro Demo Quickstart](pro-demo-quickstart.md)

빠른 판단:

- `SKIPPED` batch는 동일 기간 중복 실행 방지라면 정상이다.
- Health Alert `skipped_count`는 같은 source_key의 OPEN/ACKNOWLEDGED alert가 이미 있으면 정상일 수 있다.
- smoke test 실패 시 `[FAIL]` step 이름과 response body를 먼저 확인한다.
- 외부 발송/실제 결제가 된 것처럼 보이면 Mock 안내 문구와 release note의 known limitations를 확인한다.
