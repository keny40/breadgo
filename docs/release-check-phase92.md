# Phase 92 Release Check

## 작업 목적

Pro Operations Audit Log를 운영자가 편하게 조회, 필터링, 추적할 수 있도록 API 필터와 전용 관리자 화면을 강화했다.

이번 Phase에서도 실제 이메일, 카카오, Push, 외부 발송 API 연동은 수행하지 않는다. 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않는다.

## 변경 내용

- Admin Audit Log 목록 API 필터 강화
  - `action_type`
  - `status`
  - `target_type`
  - `target_id`
  - `actor_user_id`
  - `date_from`
  - `date_to`
  - `limit`
  - `offset`
- Audit Log 상세 API 추가
  - `GET /api/v1/admin/pro/operations/audit-logs/{audit_log_id}`
- Audit Log summary 응답 보강
  - 최근 24시간 전체/실패 건수
  - action_type별 count
  - status별 count
- Admin Audit Log Explorer 화면 추가
  - `/admin/pro/operations/audit-logs`
  - 요약 카드, 필터 폼, 최신순 감사 로그 테이블
- `/admin/pro/operations` Audit Trail 영역에 전체 보기 링크 추가
- Admin Dashboard와 NavBar에 `Pro 감사 로그` 링크 추가

## DB 변경 여부

DB 변경 없음.

기존 `pro_operations_audit_logs` 테이블을 그대로 사용했다.

## API 변경 사항

- `GET /api/v1/admin/pro/operations/audit-logs`
  - 필터 및 offset 지원
  - `metadata_json`, `total_count` 응답 포함
- `GET /api/v1/admin/pro/operations/audit-logs/{audit_log_id}`
  - 단건 상세 조회
- `GET /api/v1/admin/pro/operations/audit-logs/summary`
  - `last_24h_count`
  - `last_24h_failed_count`
  - `action_type_counts`
  - `status_counts`

모든 API는 ADMIN 전용이며 merchant/customer 접근은 `403`으로 차단된다.

## 필터 기준

- 정렬은 기본 최신순 `created_at desc`
- `status`는 `SUCCESS`, `FAILED`만 허용
- `target_id`, `actor_user_id`는 UUID 기준
- `date_from`, `date_to`는 KST 날짜 기준으로 해당 일자의 시작부터 종료까지 포함한다.
- `limit`은 최대 200으로 제한한다.
- `metadata_json`은 run id, status, count 등 운영 확인용 정보만 노출한다.

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
  - 최초 1회 로컬 서버 미기동으로 health check 연결 거부
  - 백엔드 서버 실행 후 재검증 PASS
- `python scripts/run_weekly_report_batch.py`: PASS
  - 동일 기간 SCHEDULED 중복 실행 방지 `SKIPPED` 확인
- audit logs list API 직접 호출: PASS
- action_type 필터 확인: PASS
- status 필터 확인: PASS
- target_type/target_id 필터 확인: PASS
- date_from/date_to 필터 확인: PASS
- audit log detail API 직접 호출: PASS
- audit logs summary 보강 항목 확인: PASS
- merchant/customer audit log API 접근 차단 확인: PASS
  - 각각 `403`
- 기존 quick actions 실행 시 audit log 생성 유지 확인: PASS
- 기존 scheduler CLI 유지 확인: PASS
- `npm run lint`: PASS
- `npm run build`: PASS
  - `/admin/pro/operations/audit-logs` route 포함 확인

## 남은 한계

- 감사 로그 CSV 다운로드는 아직 없다.
- 감사 로그 장기 보관 정책은 아직 없다.
- 세부 관리자 권한 분리는 아직 없다.
- 감사 로그 metadata 검색은 아직 지원하지 않는다.
