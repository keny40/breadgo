# Phase 96 Release Check

## 작업 목적

BreadGo Pro 운영 상태를 한 번에 점검할 수 있도록 관리자용 Pro Operations Health Check MVP를 추가했다.

이번 Phase에서도 실제 이메일, 카카오, Push, 외부 발송 API 연동은 수행하지 않는다. 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않는다.

## 변경 사항

- Admin Pro Health Check API 추가
  - `GET /api/v1/admin/pro/operations/health`
- Health Check 스키마 추가
  - `overall_status`
  - `checked_at`
  - `summary_message`
  - `health_messages`
  - scheduler/batch/delivery/notification/audit log/purge policy health
- `/admin/pro/operations` 화면 상단에 `Pro Health Check` 영역 추가
- `상태 다시 점검` 버튼 추가
- WARNING/CRITICAL 메시지 표시

## DB 변경 여부

DB 변경 없음.

기존 Weekly Report batch/delivery/notification/audit log 테이블을 조회해 실시간으로 계산한다.

## API 목록

- `GET /api/v1/admin/pro/operations/health`
  - ADMIN 전용
  - merchant/customer 접근은 `403`

## Health Status 판단 기준

### Scheduler Health

- 최근 `SCHEDULED` batch run이 있으면 `OK`
- 최근 `SCHEDULED` batch run이 없으면 `WARNING`
- 최근 `SCHEDULED` batch run이 `FAILED`면 `CRITICAL`
- 최근 `SCHEDULED` batch run이 `SKIPPED`면 중복 실행 방지 가능성을 message에 표시하고 `OK`

### Batch Health

- 최근 batch가 `COMPLETED`면 `OK`
- 최근 batch가 `PARTIAL`이면 `WARNING`
- 최근 batch가 `FAILED`면 `CRITICAL`
- 최근 7일 내 `FAILED`/`PARTIAL` batch가 있으면 `WARNING`

### Delivery Health

- 최근 delivery가 `COMPLETED`면 `OK`
- 최근 delivery가 `PARTIAL`이면 `WARNING`
- 최근 delivery가 `FAILED`면 `CRITICAL`
- delivery run이 없으면 `WARNING`

### Notification Health

- 미확인 notification이 없으면 `OK`
- 미확인 notification이 있으면 `WARNING`
- 미확인 notification이 20건 이상이면 `CRITICAL`
- 최근 reminder 이후에도 미확인 notification이 남아 있으면 message에 표시

### Audit Log Health

- 최근 audit log가 있으면 `OK`
- audit log가 전혀 없으면 `WARNING`
- 최근 7일 내 audit log가 없으면 `WARNING`

### Purge Policy Health

- 기본 보관일 180일, 최소 보관일 30일, 수동 purge 기능 기준으로 `OK`
- 180일보다 오래된 audit log가 1,000건 초과면 `WARNING`
- 자동 purge 미구현은 `CRITICAL`로 보지 않음

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
  - 최초 1회 로컬 서버 미기동으로 health check 연결 거부
  - 백엔드 서버 실행 후 재검증 PASS
- `python scripts/run_weekly_report_batch.py`: PASS
  - 동일 기간 SCHEDULED 중복 실행 방지 `SKIPPED` 확인
- admin health check API 직접 호출: PASS
- `overall_status`가 `OK`/`WARNING`/`CRITICAL` 중 하나로 반환되는지 확인: PASS
- scheduler/batch/delivery/notification/audit log/purge policy health 반환 확인: PASS
- `/admin/pro/operations` Health Check 영역 빌드 확인: PASS
- 상태 다시 점검 버튼 TypeScript/build 확인: PASS
- merchant/customer health API 접근 차단 확인: PASS
  - 각각 `403`
- 기존 quick actions 유지 확인: PASS
- 기존 audit list/export/purge 유지 확인: PASS
- 기존 scheduler CLI 유지 확인: PASS
- 기존 retry failed 유지 확인: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## 남은 한계

- 자동 장애 알림은 아직 없다.
- Slack/Discord/Webhook 알림은 아직 없다.
- 자동 복구는 아직 없다.
- 자동 purge scheduler는 아직 없다.
- 세부 관리자 권한 분리는 아직 없다.
