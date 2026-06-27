# Phase 82 Release Check - Weekly Report Scheduler MVP

## 작업 목적

운영 서버 cron에서 관리자 버튼 없이 Weekly Report batch를 자동 실행할 수 있도록 CLI scheduler MVP를 추가했다.

## 변경 내용

- `backend/scripts/run_weekly_report_batch.py` 추가
- CLI 실행 시 전체 merchant 대상 Weekly Report snapshot 생성/업데이트 실행
- 기존 Phase 80 전체 batch service를 재사용
- scheduler 실행은 `run_type=SCHEDULED`로 기록
- 동일 기간에 이미 `COMPLETED` 상태의 `SCHEDULED` batch run이 있으면 새 snapshot 작업을 수행하지 않고 `SKIPPED` batch run으로 안전 종료
- 관리자 Batch Monitor에서 `SCHEDULED`, `SKIPPED` 필터 확인 가능

## DB 변경 여부

- DB 스키마 변경 없음
- 기존 `pro_weekly_report_batch_runs`, `pro_weekly_report_batch_run_items` 재사용

## 실행 방법

```powershell
cd backend
python scripts/run_weekly_report_batch.py
```

## Scheduler 실행 기준

- 대상은 `merchants` 테이블의 전체 가맹점
- 기본 기간은 기존 Weekly Report 기본 기간과 같은 최근 7일 기준
- 첫 실행은 `SCHEDULED` + `COMPLETED`로 batch run/item 기록
- 같은 기간 재실행은 기존 `COMPLETED` `SCHEDULED` 실행을 감지하고 `SKIPPED`로 종료
- 수동 관리자 실행 API는 기존처럼 `SCHEDULE_PREP`로 실행되며 snapshot 업데이트 가능
- 개인정보, 연락처, 주소, 토큰은 저장/노출하지 않음

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- `cd backend && python scripts/seed_demo.py`: PASS
- `cd backend && python scripts/smoke_test.py`: PASS
- `cd backend && python scripts/run_weekly_report_batch.py`: PASS
  - 첫 실행: `SCHEDULED` / `COMPLETED`
  - 같은 기간 두 번째 실행: `SCHEDULED` / `SKIPPED`
- admin batch-runs 목록/상세에서 SCHEDULED 실행 건 확인: PASS
  - 목록 필터 `run_type=SCHEDULED` 확인
  - 상세에서 완료 실행 item 확인
- 동일 기간 중복 scheduler 실행 방지 확인: PASS
  - 기존 완료 실행 감지 후 snapshot 생성/업데이트 없이 `SKIPPED`
- 기존 admin preview/execute 유지 확인: PASS
  - 수동 실행은 `SCHEDULE_PREP` / `COMPLETED`
- merchant/customer admin API 접근 차단 유지 확인: PASS
  - merchant 실행 API 접근: `403`
  - customer preview API 접근: `403`
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 남은 한계

- 실제 cron 설정 파일은 추가하지 않음
- 실패 item 재시도는 아직 없음
- 대량 merchant 비동기 큐는 아직 없음
- 외부 이메일/카카오/Push 발송은 아직 없음
