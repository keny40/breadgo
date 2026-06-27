# Phase 83 Release Check - Retry Failed Weekly Report Batch Items

## 작업 목적

Weekly Report batch run 중 실패한 merchant item만 ADMIN이 새 retry batch run으로 재실행할 수 있게 했다.

## 변경 사항

- 실패 item 재시도 API 추가
  - `POST /api/v1/admin/pro/weekly-report/batch-runs/{batch_run_id}/retry-failed`
- 원본 batch run은 수정하지 않고 새 batch run 생성
- 새 batch run의 `run_type=RETRY`
- 원본 batch run id는 새 batch run `message`에 기록
- 실패 item의 merchant만 대상으로 Weekly Report snapshot 재생성/업데이트
- retry 결과를 merchant별 item으로 기록
- 관리자 Batch Monitor 화면에 `실패 건 재실행` 버튼 추가
- `RETRY` run type 필터 추가

## DB 변경 여부

- DB 스키마 변경 없음
- 기존 `pro_weekly_report_batch_runs`, `pro_weekly_report_batch_run_items` 재사용

## Retry 실행 방법

```http
POST /api/v1/admin/pro/weekly-report/batch-runs/{batch_run_id}/retry-failed
Authorization: Bearer <ADMIN_TOKEN>
```

## Retry 기준

- ADMIN 권한만 실행 가능
- 원본 batch run의 `status=FAILED` item만 대상
- 실패 item이 없으면 `400` 반환
- retry batch run은 `RETRY`로 기록
- 전체 성공이면 `COMPLETED`
- 일부 실패면 `PARTIAL`
- 전체 실패면 `FAILED`
- 개인정보, 연락처, 주소, 토큰은 저장/노출하지 않음

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- `cd backend && python scripts/seed_demo.py`: PASS
- `cd backend && python scripts/smoke_test.py`: PASS
- 실패 item이 있는 batch run에 대해 retry API 직접 호출: PASS
- retry 실행 후 새 batch run 생성 확인: PASS
  - `run_type=RETRY`
  - 상태 `COMPLETED`
- retry batch run의 item이 실패 merchant만 포함하는지 확인: PASS
  - 대상 merchant 1개만 retry item으로 기록
- retry 결과 상태 기록 확인: PASS
  - 성공 retry item은 `SUCCESS`
- 실패 item이 없는 batch run에서 retry 요청 시 차단 확인: PASS
  - `400`
- merchant/customer retry API 접근 차단 확인: PASS
  - merchant: `403`
  - customer: `403`
- 기존 admin preview/execute 유지 확인: PASS
- 기존 scheduler CLI 유지 확인: PASS
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 남은 한계

- retry 원본 batch run id를 별도 컬럼으로 저장하지 않고 message에 기록한다.
- 실패 원인별 자동 분류는 아직 없다.
- retry 대상 item 선택 UI는 아직 없고, 모든 실패 item을 한 번에 재실행한다.
