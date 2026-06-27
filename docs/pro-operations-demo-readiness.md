# BreadGo Pro Operations Demo Readiness

## 개요

BreadGo Pro 운영 기능은 Weekly Report 생성, delivery preview, 내부 알림, 운영 대시보드, audit trail, health check, health alert까지 이어지는 관리자/점주용 운영 점검 흐름이다.

이번 문서는 Phase 78~98에서 구현된 Weekly Report 운영 기능을 데모/배포 전 기준으로 한 번에 설명하기 위한 통합 문서다.

실제 이메일, 카카오, Push, Slack, Discord, Webhook 발송은 아직 없다. 외부 발송 API도 연동하지 않는다. 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않는다.

## 주요 화면 경로

### 관리자 화면

- `/admin`
  - 전체 관리자 대시보드와 Pro 운영 화면 진입점
- `/admin/pro/operations`
  - Pro Operations Dashboard, Health Check, Health Alerts, Quick Actions, Audit Trail 요약
- `/admin/pro/weekly-report-batches`
  - Weekly Report batch run 목록/상세, 전체 batch 실행, retry failed 확인
- `/admin/pro/weekly-report-deliveries`
  - Delivery preview, in-app mock delivery, unread reminder 실행 및 delivery run 확인
- `/admin/pro/operations/audit-logs`
  - 운영 액션 audit log 탐색, 필터, CSV export, purge preview/execute
- `/admin/pro/operations/health-alerts`
  - Health Check 기반 내부 alert 목록, 확인, 해결 처리

### 점주 화면

- `/merchant/pro`
  - 점주용 BreadGo Pro 대시보드
- `/merchant/pro/weekly-report-notifications`
  - Weekly Report 내부 알림 목록, 개별 읽음, 전체 읽음 처리

## Weekly Report Snapshot 흐름

1. 관리자 또는 scheduler가 Weekly Report batch를 실행한다.
2. 전체 merchant를 대상으로 최근 7일 Weekly Report snapshot을 생성하거나 동일 기간 snapshot을 업데이트한다.
3. 실행 결과는 `pro_weekly_report_batch_runs`, `pro_weekly_report_batch_run_items`에 기록된다.
4. 관리자 Batch Monitor에서 run 상태와 merchant별 item 결과를 확인한다.

관련 문서: `docs/weekly-report-batch-runbook.md`

## Scheduler CLI 실행 흐름

Weekly Report 자동 생성 준비용 CLI:

```bash
cd backend
python scripts/run_weekly_report_batch.py
```

- `run_type=SCHEDULED`로 batch run을 기록한다.
- 동일 기간에 이미 `COMPLETED` 상태의 SCHEDULED run이 있으면 중복 실행하지 않고 `SKIPPED`로 종료한다.
- 실제 cron 등록은 운영자가 별도로 수행한다.

## Retry Failed 흐름

1. Batch Monitor에서 실패 item이 있는 batch run을 확인한다.
2. `retry-failed` API 또는 화면 버튼으로 실패 merchant만 재실행한다.
3. 기존 batch run은 수정하지 않고 새 retry batch run을 생성한다.
4. 새 run의 item에는 재시도 대상 merchant 결과만 기록한다.

## Delivery Preview 흐름

1. 관리자 Delivery Preview 화면 또는 Pro Operations Quick Action에서 delivery preview를 생성한다.
2. snapshot이 있는 merchant는 `READY`, 없는 merchant는 `SKIPPED`로 기록한다.
3. preview 결과는 `pro_weekly_report_delivery_runs`, `pro_weekly_report_delivery_run_items`에 저장된다.

## In-app Mock Delivery 흐름

1. READY item이 있는 delivery preview run을 대상으로 mock-send를 실행한다.
2. 실제 이메일/카카오/Push는 발송하지 않는다.
3. BreadGo 내부 Weekly Report notification을 생성한다.
4. 결과 delivery run은 `IN_APP_MOCK`, `IN_APP` 성격으로 기록된다.

## Merchant Notification 흐름

1. 점주는 `/merchant/pro/weekly-report-notifications`에서 Weekly Report 알림을 확인한다.
2. 알림은 `UNREAD` 또는 `READ` 상태를 가진다.
3. 점주는 개별 읽음 처리 또는 전체 읽음 처리를 할 수 있다.
4. 점주는 본인 merchant의 알림만 조회/수정할 수 있다.

## Notification Analytics 흐름

관리자는 Weekly Report in-app notification의 전체, 읽음, 미확인, 읽음률, 최근 생성일, 최근 읽음일을 확인할 수 있다.

알림 통계에는 reminder 알림도 포함된다. 단, 외부 수신자 정보는 저장하거나 표시하지 않는다.

## Unread Reminder 흐름

1. 관리자는 미확인 Weekly Report 알림을 대상으로 reminder를 생성한다.
2. 이미 동일 merchant/snapshot에 reminder가 있으면 중복 생성하지 않고 `SKIPPED` 처리한다.
3. reminder도 BreadGo 내부 알림이며 외부 발송은 없다.

## Pro Operations Dashboard 흐름

`/admin/pro/operations`는 운영자가 가장 먼저 보는 통합 점검 화면이다.

표시 항목:

- Weekly Report batch 상태
- Delivery 상태
- Weekly Report notification 상태
- Attention messages
- Health Check
- Health Alerts
- Quick Actions
- 최근 Audit Trail

## Quick Actions 흐름

Pro Operations Dashboard에서 다음 액션을 바로 실행할 수 있다.

- 전체 Weekly Report batch 실행
- Delivery preview 생성
- In-app mock delivery 실행
- 미확인 reminder 생성
- Batch Monitor 이동
- Delivery Preview 이동

Quick Action 실행 후 operations summary, health, alert, audit log를 다시 불러온다.

## Audit Trail / Audit Log Explorer 흐름

관리자 주요 운영 액션은 `pro_operations_audit_logs`에 기록된다.

주요 action type:

- `RUN_WEEKLY_REPORT_BATCH`
- `CREATE_DELIVERY_PREVIEW`
- `RUN_IN_APP_MOCK_DELIVERY`
- `RUN_UNREAD_REMINDER`
- `RETRY_FAILED_BATCH_ITEMS`
- `EXPORT_AUDIT_LOG_CSV`
- `PURGE_AUDIT_LOGS`
- `GENERATE_HEALTH_ALERTS`
- `ACKNOWLEDGE_HEALTH_ALERT`
- `RESOLVE_HEALTH_ALERT`
- `RUN_HEALTH_ALERT_CHECK_CLI`

`/admin/pro/operations/audit-logs`에서 필터링, 상세 확인, CSV export, purge preview/execute를 수행할 수 있다.

## CSV Export 흐름

Audit Log Explorer에서 현재 필터 조건으로 CSV를 내려받을 수 있다.

CSV 컬럼:

- `id`
- `created_at`
- `actor_user_id`
- `actor_role`
- `action_type`
- `target_type`
- `target_id`
- `status`
- `message`

`metadata_json`은 CSV에서 제외한다. 개인정보, 연락처, 주소, 토큰은 포함하지 않는다.

## Audit Log Purge 흐름

1. 관리자가 retention days를 입력한다.
2. 삭제 대상 미리보기를 먼저 실행한다.
3. preview 결과에서 대상 수, cutoff date, status/action count를 확인한다.
4. `confirm=true`일 때만 실제 삭제한다.
5. purge 결과는 `PURGE_AUDIT_LOGS` audit log로 남긴다.

기본 보관 기간은 180일, 최소 보관 기간은 30일이다.

관련 문서: `docs/pro-audit-log-retention-policy.md`

## Health Check 흐름

`GET /api/v1/admin/pro/operations/health`는 다음 항목을 실시간 점검한다.

- scheduler health
- batch health
- delivery health
- notification health
- audit log health
- purge policy health

전체 상태는 `OK`, `WARNING`, `CRITICAL` 중 하나다. 가장 높은 위험도를 가진 세부 상태를 overall status로 사용한다.

## Health Alert 흐름

1. Health Check 결과에서 `WARNING` 또는 `CRITICAL` 항목을 찾는다.
2. 해당 항목을 내부 관리자 alert로 저장한다.
3. 같은 `source_key`의 `OPEN` 또는 `ACKNOWLEDGED` alert가 있으면 중복 생성하지 않는다.
4. 관리자는 alert를 확인 처리하거나 해결 처리할 수 있다.
5. 생성/확인/해결 액션은 audit log에 기록된다.

실제 Slack/Discord/Email/Webhook 발송은 없다.

## Health Alert CLI Scheduler 흐름

Health Alert 자동 점검 준비용 CLI:

```bash
cd backend
python scripts/run_pro_health_alert_check.py
```

- Health `OK`: alert를 만들지 않고 종료
- Health `WARNING` 또는 `CRITICAL`: 내부 Health Alert 생성
- 중복 `source_key`는 skip
- CLI 실행 결과는 `RUN_HEALTH_ALERT_CHECK_CLI` audit log로 기록

관련 문서: `docs/pro-health-alert-scheduler-runbook.md`

## 주요 API 목록

### Admin API

- `POST /api/v1/admin/pro/weekly-report/batch-runs/preview`
- `POST /api/v1/admin/pro/weekly-report/batch-runs`
- `GET /api/v1/admin/pro/weekly-report/batch-runs`
- `GET /api/v1/admin/pro/weekly-report/batch-runs/{batch_run_id}`
- `POST /api/v1/admin/pro/weekly-report/batch-runs/{batch_run_id}/retry-failed`
- `POST /api/v1/admin/pro/weekly-report/delivery-runs/preview`
- `GET /api/v1/admin/pro/weekly-report/delivery-runs`
- `GET /api/v1/admin/pro/weekly-report/delivery-runs/{delivery_run_id}`
- `POST /api/v1/admin/pro/weekly-report/delivery-runs/{delivery_run_id}/mock-send`
- `GET /api/v1/admin/pro/weekly-report/notifications/summary`
- `GET /api/v1/admin/pro/weekly-report/notifications`
- `POST /api/v1/admin/pro/weekly-report/notifications/remind-unread`
- `GET /api/v1/admin/pro/operations/summary`
- `GET /api/v1/admin/pro/operations/health`
- `GET /api/v1/admin/pro/operations/audit-logs`
- `GET /api/v1/admin/pro/operations/audit-logs/{audit_log_id}`
- `GET /api/v1/admin/pro/operations/audit-logs/summary`
- `GET /api/v1/admin/pro/operations/audit-logs/export.csv`
- `POST /api/v1/admin/pro/operations/audit-logs/purge/preview`
- `POST /api/v1/admin/pro/operations/audit-logs/purge`
- `POST /api/v1/admin/pro/operations/health/alerts/generate`
- `GET /api/v1/admin/pro/operations/health/alerts`
- `GET /api/v1/admin/pro/operations/health/alerts/{alert_id}`
- `POST /api/v1/admin/pro/operations/health/alerts/{alert_id}/acknowledge`
- `POST /api/v1/admin/pro/operations/health/alerts/{alert_id}/resolve`

### Merchant API

- `GET /api/v1/merchant/pro/weekly-report/notifications`
- `GET /api/v1/merchant/pro/weekly-report/notifications/unread-count`
- `POST /api/v1/merchant/pro/weekly-report/notifications/{notification_id}/read`
- `POST /api/v1/merchant/pro/weekly-report/notifications/read-all`

### CLI

- `python scripts/run_weekly_report_batch.py`
- `python scripts/run_pro_health_alert_check.py`

## 데모 순서

1. 관리자 계정으로 로그인한다.
2. `/admin/pro/operations`에 접속한다.
3. Pro Health Check의 overall status와 세부 상태를 확인한다.
4. `전체 Weekly Report batch 실행` Quick Action을 실행한다.
5. `/admin/pro/weekly-report-batches`에서 batch 결과를 확인한다.
6. Pro Operations 또는 Delivery Preview 화면에서 Delivery preview를 생성한다.
7. READY item이 있으면 In-app mock delivery를 실행한다.
8. 점주 계정으로 로그인해 `/merchant/pro/weekly-report-notifications`에서 알림을 확인한다.
9. 점주가 알림을 개별 또는 전체 읽음 처리한다.
10. 관리자 화면에서 notification summary/list를 확인한다.
11. 미확인 알림이 남아 있으면 unread reminder를 실행한다.
12. `/admin/pro/operations/audit-logs`에서 운영 액션 audit log를 확인한다.
13. Audit Log CSV export를 실행한다.
14. Audit Log purge preview를 실행해 삭제 대상만 확인한다.
15. Pro Operations에서 Health Alert를 생성한다.
16. Health Alert를 확인 처리하고 해결 처리한다.
17. `python scripts/run_pro_health_alert_check.py` CLI 실행 방법과 cron 예시를 설명한다.

## 최종 검증 체크리스트

권장 검증 명령:

```bash
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/seed_demo.py
python scripts/smoke_test.py
python scripts/run_weekly_report_batch.py
python scripts/run_pro_health_alert_check.py

cd ../frontend
npm run lint
npm run build
```

추가 화면 확인:

- Admin Pro Operations 화면 접속 가능
- Batch Monitor 화면 접속 가능
- Delivery Preview 화면 접속 가능
- Audit Log Explorer 화면 접속 가능
- Health Alerts 화면 접속 가능
- Merchant Weekly Report notification 화면 접속 가능

## 개인정보 및 민감정보 원칙

BreadGo Pro 운영 기능은 merchant id, snapshot id, run id, status, count, reason 중심으로 기록한다. 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않는다.

CSV export 파일을 외부에 보관하거나 공유할 경우 별도 보안 관리 기준이 필요하다.

## 현재 한계

- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송 없음
- 외부 발송 API 연동 없음
- 실제 서버 cron 등록은 운영자가 별도로 수행
- 자동 복구 없음
- 자동 purge scheduler 없음
- 세부 관리자 권한 분리 없음
- 대량 비동기 큐 없음
