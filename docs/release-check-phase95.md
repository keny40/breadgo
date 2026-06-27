# Phase 95 Release Check

## 작업 목적

Pro Operations Audit Log가 계속 누적되는 것을 방지하기 위해 오래된 감사 로그를 preview 후 안전하게 삭제하는 purge old audit logs MVP를 추가했다.

이번 Phase에서도 실제 이메일, 카카오, Push, 외부 발송 API 연동은 수행하지 않는다. 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않는다.

## 변경 사항

- Audit Log purge preview API 추가
  - `POST /api/v1/admin/pro/operations/audit-logs/purge/preview`
- Audit Log purge execute API 추가
  - `POST /api/v1/admin/pro/operations/audit-logs/purge`
- purge execute 결과를 `PURGE_AUDIT_LOGS` audit log로 기록
- `/admin/pro/operations/audit-logs` 화면에 `오래된 감사 로그 정리` 섹션 추가
- Audit Log retention policy 문서 추가
  - `docs/pro-audit-log-retention-policy.md`

## DB 변경 여부

DB 변경 없음.

기존 `pro_operations_audit_logs` 테이블에서 조건에 맞는 오래된 로그를 삭제한다.

## API 목록

### Preview

`POST /api/v1/admin/pro/operations/audit-logs/purge/preview`

요청 필드:

- `retention_days`: 기본 180, 최소 30
- `date_to`: 선택
- `status`: 선택, `SUCCESS` 또는 `FAILED`
- `action_type`: 선택

응답:

- `retention_days`
- `cutoff_date`
- `matched_count`
- `oldest_created_at`
- `newest_created_at`
- `status_counts`
- `action_type_counts`
- `message`

### Execute

`POST /api/v1/admin/pro/operations/audit-logs/purge`

요청 필드:

- `retention_days`: 기본 180, 최소 30
- `confirm`: 반드시 `true`
- `status`: 선택
- `action_type`: 선택

응답:

- preview 응답 필드
- `deleted_count`

## Purge 기준

- 기본 cutoff 기준은 현재 시점에서 `retention_days` 이전이다.
- `date_to`가 지정되면 해당 날짜의 KST 00:00 이전 로그가 대상이다.
- 삭제 조건은 `created_at < cutoff_date`이다.
- `status`, `action_type`이 지정되면 해당 조건에 맞는 로그만 대상이다.
- purge 실행 audit log는 오래된 로그 삭제 이후 생성하여 자기 자신이 삭제되지 않게 처리한다.

## 최소 보관일

- 최소 보관일은 30일이다.
- 30일 미만 요청은 백엔드에서 `400`으로 거부한다.
- 프론트에서도 30일 미만 입력 시 실행을 막는다.

## 개인정보 제외 기준

- purge preview/execute 응답에는 이메일, 전화번호, 주소, 외부 발송 토큰을 포함하지 않는다.
- purge audit metadata에는 retention days, cutoff date, deleted count, filter status/action만 저장한다.

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
  - 최초 1회 로컬 서버 미기동으로 health check 연결 거부
  - 백엔드 서버 실행 후 재검증 PASS
- `python scripts/run_weekly_report_batch.py`: PASS
  - 동일 기간 SCHEDULED 중복 실행 방지 `SKIPPED` 확인
- purge preview API 직접 호출: PASS
- retention_days 기본값 180 확인: PASS
- retention_days 30 미만 요청 시 400 확인: PASS
- purge preview에서 실제 삭제되지 않는지 확인: PASS
- purge execute confirm=false 시 400 확인: PASS
- purge execute confirm=true 시 오래된 audit log 삭제 확인: PASS
- purge execute 결과가 `PURGE_AUDIT_LOGS` audit log로 기록되는지 확인: PASS
- purge 후 audit logs summary count 감소 확인: PASS
  - 오래된 로그 2건 삭제 케이스에서 purge audit log 1건 생성 후에도 total count 감소 확인
- purge 후 audit logs list 정상 조회 확인: PASS
- purge 후 CSV export 정상 동작 확인: PASS
- merchant/customer purge API 접근 차단 확인: PASS
  - 각각 `403`
- `/admin/pro/operations/audit-logs` purge preview/execute UI 빌드 확인: PASS
- 기존 quick actions 실행 시 audit log 생성 유지 확인: PASS
- 기존 CSV export 유지 확인: PASS
- 기존 scheduler CLI 유지 확인: PASS
- 기존 retry failed 유지 확인: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## 남은 한계

- 자동 스케줄 purge는 아직 없다.
- 장기 보관용 archive 테이블은 아직 없다.
- S3 백업과 CSV 자동 백업은 아직 없다.
- 세부 관리자 권한 분리는 아직 없다.
- metadata_json 내부 검색은 아직 없다.
