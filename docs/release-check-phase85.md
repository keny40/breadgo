# Phase 85 Release Check

## 작업 목적

Weekly Report를 실제 외부 발송하기 전, 관리자 화면에서 발송 가능한 snapshot과 제외 대상을 미리 확인하고 preview/dry-run 로그를 남길 수 있는 MVP를 추가했다.

## 변경 사항

- Weekly Report delivery preview/log 테이블 추가
- 관리자 전용 delivery preview 생성 API 추가
- 관리자 전용 delivery run 목록/상세 조회 API 추가
- 관리자 화면 `/admin/pro/weekly-report-deliveries` 추가
- 관리자 NavBar와 Admin Dashboard에 Delivery Preview 진입 링크 추가
- 실제 이메일/카카오/Push/외부 API 발송은 구현하지 않음
- 수신자 이메일, 전화번호, 주소, 토큰은 저장하거나 노출하지 않음

## DB 변경 여부

- DB 변경 있음
- Migration: `backend/alembic/versions/202606180020_create_weekly_report_delivery_runs.py`
- 추가 테이블:
  - `pro_weekly_report_delivery_runs`
  - `pro_weekly_report_delivery_run_items`
- 기존 Weekly Report batch run/item 테이블은 변경하지 않음

## API 목록

- `POST /api/v1/admin/pro/weekly-report/delivery-runs/preview`
- `GET /api/v1/admin/pro/weekly-report/delivery-runs`
- `GET /api/v1/admin/pro/weekly-report/delivery-runs/{delivery_run_id}`

## Delivery Preview 기준

- 대상 기간의 Weekly Report snapshot이 있는 merchant는 `READY`
- 대상 기간의 Weekly Report snapshot이 없는 merchant는 `SKIPPED`
- preview 처리 중 예외가 발생한 merchant는 `FAILED`
- run status는 item 결과에 따라 `COMPLETED`, `PARTIAL`, `FAILED`로 기록
- channel은 `IN_APP_PREVIEW`로 기록하며 실제 외부 발송은 수행하지 않음

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- admin delivery preview API 직접 호출: PASS
- delivery run 목록/상세 조회: PASS
- snapshot 있는 merchant `READY` 확인: PASS
- snapshot 없는 merchant `SKIPPED` 확인: PASS
- merchant/customer delivery API 접근 차단 403 확인: PASS
- 기존 weekly report batch preview/execute 유지 확인: PASS
- 기존 scheduler CLI 유지 확인: PASS
- 기존 retry failed 유지 확인: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

검증 메모:

- 현재 기간 snapshot 생성 후 delivery preview에서 `ready_count=2` 확인
- snapshot이 없는 과거 기간 preview에서 `skipped_count=2` 확인
- merchant/customer token으로 delivery preview/list 접근 시 각각 403 확인
- 기존 scheduler CLI는 동일 기간 완료된 `SCHEDULED` run이 있어 `SKIPPED`로 안전 종료 확인
- FAILED item fixture 기준 retry 호출 시 새 `RETRY` batch run 생성 및 `COMPLETED` 확인

## 남은 한계

- 실제 이메일/카카오/Push 발송은 아직 없다.
- 수신 동의, 발송 실패 webhook, 재발송 정책은 아직 없다.
- 현재는 snapshot 존재 여부 기반 preview/dry-run 로그만 기록한다.
