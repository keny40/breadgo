# Phase 78 Release Check - Weekly Report Batch Run Logs

## 작업 목적

실제 cron/scheduler를 붙이기 전, Weekly Report 자동 생성 작업의 실행 결과를 기록하고 점주가 확인할 수 있는 batch run log MVP를 추가했다.

## 변경 내용

- `pro_weekly_report_batch_runs`, `pro_weekly_report_batch_run_items` 테이블 추가
- `POST /api/v1/merchant/pro/weekly-report/batch-test-run` 추가
  - 현재 로그인한 MERCHANT 1명에 대해 auto snapshot 생성 실행
  - batch run과 item 결과 기록
- `GET /api/v1/merchant/pro/weekly-report/batch-runs` 추가
- `GET /api/v1/merchant/pro/weekly-report/batch-runs/{batch_run_id}` 추가
- `/merchant/pro/weekly-report`에 자동 생성 테스트 실행 버튼과 최근 batch run 이력 표시 추가

## DB 변경 여부

- DB 스키마 변경 있음
- 신규 테이블:
  - `pro_weekly_report_batch_runs`
  - `pro_weekly_report_batch_run_items`
- 개인정보, 연락처, 주소, 토큰은 저장하지 않음

## Batch Log 기록 기준

- MVP에서는 단일 merchant `MANUAL_TEST` 실행만 기록한다.
- batch run은 실행 단위이며 대상 기간, 대상 merchant 수, 성공/실패/건너뜀 수를 저장한다.
- batch item은 merchant별 결과이며 snapshot id, 성공/실패 상태, 메시지를 저장한다.
- 같은 기간 snapshot이 이미 있으면 기존 auto snapshot 기준대로 업데이트하고, batch log는 새 실행 이력으로 남긴다.
- 실제 cron, 전체 merchant 일괄 실행, 외부 발송은 아직 하지 않는다.

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- 백엔드 서버 실행 후 `cd backend && python scripts/seed_demo.py && python scripts/smoke_test.py`: PASS
- batch-test-run API 직접 호출: PASS
  - `COMPLETED`, item `SUCCESS`, snapshot id 기록 확인
- batch-runs 목록/상세 API 직접 호출: PASS
  - 목록에서 batch run 2건 확인
  - 상세에서 item 1건 확인
- 같은 기간 중복 실행 시 snapshot 업데이트와 batch log 기록 확인: PASS
  - 같은 기간 재실행 시 동일 snapshot id 유지
  - batch run은 별도 실행 이력으로 추가 기록
- 기존 weekly-report history/export/auto-snapshot 동작 유지 확인: PASS
  - auto-snapshot 재실행 결과 `UPDATED`
  - history 조회와 저장 snapshot JSON export `200` 확인
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- 실제 cron/scheduler는 아직 없다.
- 전체 merchant 일괄 생성은 아직 없다.
- 운영자 전용 전체 batch 관리 화면은 아직 없다.
- 외부 이메일/카카오/Push 발송은 아직 없다.

## 다음 단계

- scheduler에서 전체 merchant batch 실행
- batch 실패 재시도 정책
- 관리자 운영 화면에서 전체 batch run 모니터링
