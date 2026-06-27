# Phase 80 Release Check - Admin Weekly Report Batch Jobs

## 작업 목적

ADMIN이 실제 cron/scheduler 없이 버튼으로 전체 가맹점 Weekly Report snapshot 생성을 실행하고, batch run/item 로그에서 결과를 확인할 수 있게 했다.

## 변경 내용

- 관리자용 전체 batch preview API 추가
  - `POST /api/v1/admin/pro/weekly-report/batch-runs/preview`
- 관리자용 전체 batch 실행 API 추가
  - `POST /api/v1/admin/pro/weekly-report/batch-runs`
- 전체 batch 실행은 기존 auto snapshot service를 재사용
- merchant별 batch item 기록
- 전체 성공 시 `COMPLETED`, 일부 실패 시 `PARTIAL`, 전체 실패 시 `FAILED`
- `/admin/pro/weekly-report-batches` 화면에 전체 배치 미리보기/실행 패널 추가

## DB 변경 여부

- DB 스키마 변경 없음
- Phase 78의 `pro_weekly_report_batch_runs`, `pro_weekly_report_batch_run_items`를 재사용

## 전체 Batch 실행 기준

- 대상은 `merchants` 테이블의 전체 가맹점
- 기본 기간은 기존 Weekly Report 기본 기간과 같은 최근 7일 기준
- 같은 기간 snapshot이 있으면 기존 snapshot을 업데이트
- batch run은 실행마다 새로 기록
- item은 merchant별 `SUCCESS` 또는 `FAILED`로 기록
- 개인정보, 연락처, 주소, 토큰은 저장/노출하지 않음

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- 백엔드 서버 실행 후 `cd backend && python scripts/seed_demo.py && python scripts/smoke_test.py`: PASS
- admin 전체 batch preview API 직접 호출: PASS
  - 대상 가맹점 수와 생성/업데이트 예정 수 반환 확인
- admin 전체 batch 실행 API 직접 호출: PASS
  - `COMPLETED`, 성공/실패 수, item 기록 확인
- batch-runs 목록/상세에서 item 기록 확인: PASS
- merchant/customer 권한으로 admin 실행 API 접근 차단: PASS
  - merchant preview 접근: `403`
  - customer 실행 접근: `403`
- 기존 merchant batch-test-run 유지 확인: PASS
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- 실제 cron/scheduler는 아직 없다.
- 외부 이메일/카카오/Push 발송은 아직 없다.
- 실패 item 재시도 기능은 아직 없다.
- 대량 merchant 처리용 비동기 큐는 아직 없다.

## 다음 단계

- scheduler 기반 주간 자동 실행
- 실패 item 재시도
- batch 완료 알림센터 연동
