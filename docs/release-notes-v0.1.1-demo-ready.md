# BreadGo MVP Demo Ready Release

Tag: `v0.1.1-demo-ready`

## 릴리즈 목적

BreadGo MVP와 BreadGo Pro 운영 기능을 데모/시연/제출 가능한 상태로 정리한 demo-ready 릴리즈다. 소비자 예약/Mock 결제/픽업, 점주 운영, 관리자 운영, BreadGo Pro 수율 관리와 Weekly Report 운영 흐름을 하나의 시나리오로 설명할 수 있게 준비했다.

이번 릴리즈는 실제 외부 발송이나 외부 결제/배송/POS 연동을 추가하지 않는다. 이메일, 전화번호, 주소, 외부 발송 토큰은 Pro 운영 로그와 화면에 저장하거나 노출하지 않는다.

## 주요 기능 요약

### 소비자 MVP

- 지역 기반 마감 할인 상품 조회
- 상품 이미지, 원가/할인가, 재고 확인
- 픽업/퀵배송/택배 수령 방식 선택
- 예약 생성
- Mock 결제
- 내 예약, 내 결제, 픽업 코드 확인
- 예약 취소와 Mock 환불 상태 확인
- 인앱 알림 확인과 읽음 처리

### 점주 MVP

- 가맹점/매장 관리
- 상품 등록, 수정, 숨김, 다시 판매
- 상품 이미지 업로드
- 주문/예약 관리
- 픽업 코드 확인과 픽업 확정
- 배송 상태 수동 변경
- 정산 내역과 정산 계좌 관리
- CSV 상품 일괄 등록
- Mock POS 동기화

### 관리자 MVP

- 사용자, 가맹점, 매장, 상품, 예약, 결제 목록 확인
- 가맹점 승인 상태 변경
- 배송 상태 변경
- 정산 관리
- 운영 점검 화면
- BreadGo Pro 운영 모니터링 화면

### BreadGo Pro

- 점주용 수율 대시보드
- 반복 상품 등록과 요일별 템플릿
- ESG/폐기 절감 리포트
- 추천 재고/할인가 MVP
- 추천 사용/채택/성과/퍼널 추적
- 고객 상품 조회/예약 전환 퍼널
- 다중 매장 통합 대시보드
- Free/Pro/Enterprise 플랜 MVP
- Inventory Ledger
- 재고 이상 감지와 조치 이력
- Daily Pro Brief와 이력 저장

### Weekly Report 운영 자동화

- Weekly Pro Report 생성
- Weekly Report snapshot/history/export
- Auto snapshot preview/execute
- Batch run/item log
- Admin 전체 merchant batch preview/execute
- Scheduler CLI: `python scripts/run_weekly_report_batch.py`
- Failed item retry

### Delivery Preview / In-app Mock Delivery

- Delivery preview run/item log
- snapshot이 있는 merchant는 READY, 없는 merchant는 SKIPPED
- READY item 대상 BreadGo 내부 알림 Mock 발송
- 실제 이메일/카카오/Push 발송 없음

### Notification / Reminder

- Merchant Weekly Report notification 목록
- 미확인 개수 조회
- 개별 읽음 처리
- 모두 읽음 처리
- Admin notification summary/list
- Unread reminder mock flow

### Pro Operations Dashboard

- Weekly Report batch 요약
- Delivery 요약
- Notification 요약
- Attention messages
- Health Check 요약
- Health Alerts 요약
- Quick Actions
- 최근 Audit Trail

### Audit Trail / CSV Export / Purge

- 관리자 주요 Pro 운영 액션 audit log 기록
- Audit Log Explorer
- action/status/target/date 필터
- Audit Log CSV export
- Audit Log purge preview/execute
- purge 결과 audit log 기록

### Health Check / Health Alert / CLI

- Pro Operations Health Check
- scheduler, batch, delivery, notification, audit log, purge policy 상태 점검
- WARNING/CRITICAL 결과 기반 내부 Health Alert 생성
- Alert acknowledge/resolve
- Health Alert CLI: `python scripts/run_pro_health_alert_check.py`

## 검증 완료 항목

- `python -m compileall app scripts`
- `python -m alembic upgrade head`
- `python scripts/seed_demo.py`
- `python scripts/smoke_test.py`
- `python scripts/run_weekly_report_batch.py`
- `python scripts/run_pro_health_alert_check.py`
- `npm run lint`
- `npm run build`
- 관리자 Pro 운영 화면 route 확인
- 점주 Weekly Report notification 화면 route 확인
- Delivery preview / In-app mock delivery 리허설
- Audit Log CSV export 리허설
- Health Alert / notification read 리허설

## Mock 처리된 항목

- Mock 결제
- Mock 환불
- Mock POS 동기화
- In-app mock delivery
- Health Alert 내부 alert
- Weekly Report scheduler CLI
- Health Alert scheduler CLI

## 아직 실제 연동되지 않은 항목

- 실제 PG 결제
- 실제 카드 환불
- 실제 퀵배송/택배 API
- 실제 이메일, SMS, 카카오, Push 발송
- Slack, Discord, Webhook 발송
- 외부 POS API
- 실제 AI 모델
- 실서버 cron 등록
- 자동 복구
- 자동 purge scheduler
- 세부 관리자 권한 분리
- 대량 비동기 큐

## 데모 실행 전 주의사항

- `python scripts/seed_demo.py`로 데모 계정을 준비한다.
- 백엔드 서버를 실행한 뒤 `python scripts/smoke_test.py`를 실행한다.
- 프론트엔드는 `npm run lint`, `npm run build`, 필요 시 `npm run dev`로 확인한다.
- Render 무료 인스턴스는 sleep 이후 첫 요청이 느릴 수 있다.
- 데모 계정은 운영 환경에서 사용하면 안 된다.
- Audit Log purge는 데모 중 preview까지만 보여주는 것을 권장한다.
- 외부 발송은 모두 미연동이며 BreadGo 내부 알림 Mock으로만 설명한다.
