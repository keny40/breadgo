# Phase 79 Release Check - Admin Weekly Report Batch Monitor

## 작업 목적

관리자/운영자가 Weekly Report 자동 생성 준비 작업의 실행 이력, 성공/실패 수, merchant별 item 상태를 확인할 수 있는 Batch Monitor MVP를 추가했다.

## 변경 내용

- 관리자용 Weekly Report batch run 조회 API 추가
  - `GET /api/v1/admin/pro/weekly-report/batch-runs`
  - `GET /api/v1/admin/pro/weekly-report/batch-runs/{batch_run_id}`
- 목록 응답에 최근 batch run 요약 포함
  - 전체 실행 수
  - 완료/실패/부분 성공 수
  - 최근 실행 상태/시각
- 필터 지원
  - `status`
  - `run_type`
  - `start_date`
  - `end_date`
- 관리자 화면 추가
  - `/admin/pro/weekly-report-batches`
  - 요약 카드, batch run 목록, merchant별 item 결과 표시
- Admin Dashboard와 NavBar에 Batch Monitor 진입 링크 추가

## DB 변경 여부

- DB 스키마 변경 없음
- Phase 78의 `pro_weekly_report_batch_runs`, `pro_weekly_report_batch_run_items`를 조회

## 관리자 조회 기준

- ADMIN 권한만 전체 batch run 조회 가능
- MERCHANT/CUSTOMER 권한으로 admin batch API 접근 시 차단
- item에는 `merchant_id`, `snapshot_id`, `status`, `message`만 표시
- 개인정보, 연락처, 주소, 토큰은 노출하지 않음

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- 백엔드 서버 실행 후 `cd backend && python scripts/seed_demo.py && python scripts/smoke_test.py`: PASS
- admin batch-runs 목록/상세 API 직접 호출: PASS
  - 목록 summary, 필터, 상세 item 조회 확인
- merchant/customer 권한으로 admin API 접근 차단: PASS
  - merchant token: `403`
  - customer token: `403`
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- 실제 cron/scheduler는 아직 없다.
- 전체 merchant 자동 생성 실행은 아직 없다.
- 관리자 화면에서 batch 재실행/재시도는 아직 지원하지 않는다.
- 외부 이메일/카카오/Push 발송은 아직 없다.

## 다음 단계

- 전체 merchant batch 실행 API 또는 scheduler 연결
- 실패 item 재시도 기능
- 관리자 운영 점검 화면과 batch monitor 통합
