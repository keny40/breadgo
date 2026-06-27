# Phase 90 Release Check

## 작업 목적

관리자 Pro Operations Dashboard에서 Weekly Report 운영 상태를 확인한 뒤 필요한 조치를 바로 실행할 수 있는 quick actions MVP를 추가했다.

## 변경 사항

- `/admin/pro/operations` 화면에 운영 Quick Actions 영역 추가
- 기존 API를 재사용하는 버튼 추가
  - 전체 Weekly Report batch 실행
  - Delivery preview 생성
  - In-app mock delivery 실행
  - 미확인 리마인드 생성
  - Batch Monitor로 이동
  - Delivery Preview로 이동
- Operations summary API에 quick action 실행 가능 여부와 대상 id 추가
- 실제 이메일/카카오/Push/외부 발송 API는 추가하지 않음
- 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않음

## DB 변경 여부

- DB 변경 없음
- 기존 batch run/item, delivery run/item, notification 테이블 조회만 사용
- Alembic migration 추가 없음

## API 변경 사항

- 기존 API `GET /api/v1/admin/pro/operations/summary` 응답 필드 추가:
  - `batch.latest_batch_run_id`
  - `delivery.latest_delivery_run_id`
  - `delivery.latest_ready_delivery_run_id`
  - `can_run_mock_delivery`
  - `can_run_unread_reminder`
  - `quick_action_messages`

## 화면 변경 사항

- `/admin/pro/operations`
  - `운영 Quick Actions` 섹션 추가
  - 실행 중 loading 상태 표시
  - 성공/실패 메시지 표시
  - 실행 후 summary 재조회
  - mock delivery 불가 시 버튼 disabled
  - unread reminder 불가 시 버튼 disabled

## Quick Action별 동작 기준

- `전체 Weekly Report batch 실행`
  - `POST /api/v1/admin/pro/weekly-report/batch-runs`
  - 항상 실행 가능
- `Delivery preview 생성`
  - `POST /api/v1/admin/pro/weekly-report/delivery-runs/preview`
  - 항상 실행 가능
- `In-app mock delivery 실행`
  - `latest_ready_delivery_run_id`가 있을 때만 가능
  - `POST /api/v1/admin/pro/weekly-report/delivery-runs/{delivery_run_id}/mock-send`
- `미확인 리마인드 생성`
  - `can_run_unread_reminder=true`일 때 가능
  - `POST /api/v1/admin/pro/weekly-report/notifications/remind-unread`

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS
- admin operations summary API 직접 호출: PASS
- summary quick action 관련 필드 확인: PASS
- 전체 Weekly Report batch 실행 API 확인: PASS
- Delivery preview 생성 API 확인: PASS
- READY item 있는 delivery run에 대해 In-app mock delivery 실행 확인: PASS
- READY item 없을 때 `can_run_mock_delivery=false` 확인: PASS
- UNREAD notification이 있을 때 미확인 리마인드 생성 확인: PASS
- quick action 실행 후 summary 새로고침에 필요한 id/status 반영 확인: PASS
- merchant/customer admin operations API 접근 차단 403 확인: PASS
- 기존 delivery preview/mock-send/remind-unread 유지 확인: PASS
- 기존 scheduler CLI 유지 확인: PASS
- 기존 retry failed 유지 확인: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

검증 메모:

- summary 응답에서 `latest_batch_run_id`, `latest_delivery_run_id`, `latest_ready_delivery_run_id`, `can_run_mock_delivery`, `can_run_unread_reminder`, `quick_action_messages` 확인
- preview 생성 후 `can_run_mock_delivery=true` 확인
- READY item을 검증 fixture로 제거한 뒤 `can_run_mock_delivery=false` 확인
- batch/preview/mock/reminder API 호출 후 operations summary 재조회 기준 필드 반영 확인

## 남은 한계

- 실제 이메일/카카오/Push 발송은 아직 없다.
- 수신 동의 관리, 외부 발송 실패 webhook, 실제 재발송 정책은 아직 없다.
- quick action은 동기 API 호출 기반 MVP이며 대량 merchant 비동기 큐는 아직 없다.
