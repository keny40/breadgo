# Phase 93 Release Check

## 작업 목적

Pro Operations Audit Log를 운영자가 외부 점검/보고용으로 내려받을 수 있도록 CSV Export MVP를 추가했다.

이번 Phase에서도 실제 이메일, 카카오, Push, 외부 발송 API 연동은 수행하지 않는다. 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않는다.

## 변경 사항

- Admin 전용 Audit Log CSV export API 추가
  - `GET /api/v1/admin/pro/operations/audit-logs/export.csv`
- 기존 Audit Log 목록과 동일한 필터 조건 지원
  - `action_type`
  - `status`
  - `target_type`
  - `target_id`
  - `actor_user_id`
  - `date_from`
  - `date_to`
- CSV export 실행 자체를 Audit Log에 기록
  - `action_type=EXPORT_AUDIT_LOG_CSV`
  - `target_type=AUDIT_LOG`
- `/admin/pro/operations/audit-logs` 화면에 `CSV 다운로드` 버튼 추가
- 현재 적용된 필터 조건을 CSV export API에 그대로 전달

## DB 변경 여부

DB 변경 없음.

기존 `pro_operations_audit_logs` 테이블을 그대로 사용했다.

## API 목록

- `GET /api/v1/admin/pro/operations/audit-logs/export.csv`
  - ADMIN 전용
  - UTF-8 BOM 포함 CSV 응답
  - 기본 최신순 `created_at desc`
  - 최대 10,000건 export

## CSV 컬럼

- `id`
- `created_at`
- `actor_user_id`
- `actor_role`
- `action_type`
- `target_type`
- `target_id`
- `status`
- `message`

`metadata_json`은 기본 CSV에서 제외했다.

## 개인정보 제외 기준

- CSV에는 이메일, 전화번호, 주소, 외부 발송 토큰을 포함하지 않는다.
- `metadata_json`은 CSV에서 제외한다.
- export 감사 로그의 `metadata_json`에는 filter 조건과 `exported_count`만 저장한다.

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
  - 최초 1회 로컬 서버 미기동으로 health check 연결 거부
  - 백엔드 서버 실행 후 재검증 PASS
- `python scripts/run_weekly_report_batch.py`: PASS
  - 동일 기간 SCHEDULED 중복 실행 방지 `SKIPPED` 확인
- audit log CSV export API 직접 호출: PASS
- 필터 없는 CSV export 확인: PASS
- `action_type`/`status`/`date_from`/`date_to` 필터 적용 CSV export 확인: PASS
- CSV UTF-8 BOM 포함 확인: PASS
- CSV에 `metadata_json`, phone/address/token/email 관련 문자열 미포함 확인: PASS
- CSV export 실행 자체가 audit log에 `EXPORT_AUDIT_LOG_CSV`/`SUCCESS`로 기록됨 확인: PASS
- merchant/customer export API 접근 차단 확인: PASS
  - 각각 `403`
- 기존 audit logs list/detail/summary 유지 확인: PASS
- 기존 quick actions 실행 시 audit log 생성 유지 확인: PASS
- 기존 scheduler CLI 유지 확인: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## 남은 한계

- 감사 로그 장기 보관 정책은 아직 없다.
- 세부 관리자 권한 분리는 아직 없다.
- `metadata_json` 전체 CSV export는 이번 Phase 범위에서 제외했다.
- 대용량 export 비동기 처리나 압축 다운로드는 아직 없다.
