# Phase 97 Release Check

## 작업 목적

Pro Operations Health Check 결과가 `WARNING` 또는 `CRITICAL`일 때 실제 외부 발송 없이 관리자 내부 alert로 기록하고, 확인/해결 처리할 수 있는 Health Alert Mock Flow MVP를 추가했다.

이번 Phase에서도 실제 이메일, 카카오, Push, Slack, Discord, Webhook 발송과 외부 발송 API 연동은 수행하지 않는다. 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않는다.

## 변경 사항

- `pro_health_alerts` 테이블 추가
- Health Check 결과 기반 alert 생성 API 추가
- Health Alert 목록/상세 API 추가
- Health Alert 확인/해결 API 추가
- Health Alert 생성/확인/해결 액션을 Pro Operations Audit Log에 기록
- `/admin/pro/operations` 화면에 `Health Alerts` 영역 추가
- `/admin/pro/operations/health-alerts` 전용 화면 추가
- Admin Dashboard/NavBar에 `Pro 상태 알림` 링크 추가

## DB 변경 여부

DB 변경 있음.

- Migration: `backend/alembic/versions/202606180023_create_pro_health_alerts.py`
- 추가 테이블: `pro_health_alerts`

기존 batch/delivery/notification/audit log 테이블은 변경하지 않았다.

## API 목록

- `POST /api/v1/admin/pro/operations/health/alerts/generate`
- `GET /api/v1/admin/pro/operations/health/alerts`
- `GET /api/v1/admin/pro/operations/health/alerts/{alert_id}`
- `POST /api/v1/admin/pro/operations/health/alerts/{alert_id}/acknowledge`
- `POST /api/v1/admin/pro/operations/health/alerts/{alert_id}/resolve`

모든 API는 ADMIN 전용이며 merchant/customer 접근은 `403`으로 차단된다.

## Alert 중복 방지 기준

- Health Check 세부 항목 중 `WARNING` 또는 `CRITICAL`만 alert 생성 대상이다.
- `source_key`는 `scheduler:WARNING`, `batch:CRITICAL` 같은 형태로 만든다.
- 같은 `source=HEALTH_CHECK`, 같은 `source_key`의 `OPEN` 또는 `ACKNOWLEDGED` alert가 있으면 새로 만들지 않고 `SKIPPED` 처리한다.
- `RESOLVED` alert는 중복 방지 대상에서 제외되어 이후 동일 상태가 다시 발생하면 새 alert를 만들 수 있다.

## Audit Log 기록 기준

아래 action을 Pro Operations Audit Log에 기록한다.

- `GENERATE_HEALTH_ALERTS`
- `ACKNOWLEDGE_HEALTH_ALERT`
- `RESOLVE_HEALTH_ALERT`

`target_type=HEALTH_ALERT`로 기록하며 metadata에는 count, alert id, severity, status 정도만 저장한다. 개인정보, 연락처, 주소, 토큰은 저장하지 않는다.

## 화면 변경 사항

- `/admin/pro/operations`
  - Health Check 아래에 최근 Health Alerts 영역 추가
  - 미해결 alert 수 표시
  - `Health Alert 생성` 버튼 추가
  - alert별 확인/해결 처리 버튼 추가
- `/admin/pro/operations/health-alerts`
  - alert 목록
  - severity/status 필터
  - 확인/해결 처리 버튼
  - Pro Operations 이동 링크

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
  - 최초 1회 로컬 서버 미기동으로 health check 연결 거부
  - 백엔드 서버 실행 후 재검증 PASS
- `python scripts/run_weekly_report_batch.py`: PASS
  - 동일 기간 SCHEDULED 중복 실행 방지 `SKIPPED` 확인
- admin health alerts generate API 직접 호출: PASS
- WARNING/CRITICAL health 항목에서 alert 생성 확인: PASS
- 동일 source_key OPEN/ACKNOWLEDGED alert 중복 생성 방지 확인: PASS
- health alerts list/detail API 직접 호출: PASS
- alert acknowledge API 직접 호출: PASS
- alert resolve API 직접 호출: PASS
- GENERATE/ACKNOWLEDGE/RESOLVE action audit log 생성 확인: PASS
- merchant/customer health alert API 접근 차단 확인: PASS
  - 각각 `403`
- `/admin/pro/operations` Health Alerts 영역 빌드 확인: PASS
- `/admin/pro/operations/health-alerts` 화면 빌드 확인: PASS
- 기존 health check 유지 확인: PASS
- 기존 quick actions 유지 확인: PASS
- 기존 audit list/export/purge 유지 확인: PASS
- 기존 scheduler CLI 유지 확인: PASS
- 기존 retry failed 유지 확인: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## 남은 한계

- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송은 없다.
- 자동 alert scheduler는 아직 없다.
- 자동 복구는 아직 없다.
- 세부 관리자 권한 분리는 아직 없다.
- alert 장기 보관/삭제 정책은 아직 없다.
