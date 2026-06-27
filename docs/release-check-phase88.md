# Phase 88 Release Check

## 작업 목적

Weekly Report 내부 알림 중 아직 읽지 않은 알림을 대상으로, 관리자 화면에서 BreadGo 내부 리마인드 mock delivery를 실행할 수 있게 했다.

## 변경 사항

- ADMIN 전용 미확인 Weekly Report 알림 리마인드 API 추가
- 리마인드 실행 시 새 delivery run 생성
  - `run_type=IN_APP_REMINDER`
  - `channel=IN_APP`
- reminder 대상별 delivery run item 기록
  - 리마인드 생성 성공: `SENT`
  - 중복 리마인드 존재: `SKIPPED`
  - 예외 발생: `FAILED`
- 관리자 delivery 화면 `/admin/pro/weekly-report-deliveries`에 `미확인 리마인드 생성` 버튼 추가
- 점주 Weekly Report 알림 화면은 기존 목록에서 reminder 알림을 자연스럽게 표시
- 실제 이메일/카카오/Push/외부 발송 API는 추가하지 않음
- 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않음

## DB 변경 여부

- DB 변경 없음
- 기존 `pro_weekly_report_in_app_notifications`와 delivery run/item 구조 재사용
- Alembic migration 추가 없음

## API 목록

- `POST /api/v1/admin/pro/weekly-report/notifications/remind-unread`
- 기존 유지:
  - `GET /api/v1/admin/pro/weekly-report/notifications/summary`
  - `GET /api/v1/admin/pro/weekly-report/notifications`
  - `GET /api/v1/admin/pro/weekly-report/delivery-runs`
  - `GET /api/v1/admin/pro/weekly-report/delivery-runs/{delivery_run_id}`
  - `POST /api/v1/admin/pro/weekly-report/delivery-runs/{delivery_run_id}/mock-send`
  - `GET /api/v1/merchant/pro/weekly-report/notifications`
  - `GET /api/v1/merchant/pro/weekly-report/notifications/unread-count`
  - `POST /api/v1/merchant/pro/weekly-report/notifications/read-all`

## 화면 변경 사항

- Admin: `/admin/pro/weekly-report-deliveries`
  - `미확인 리마인드 생성` 버튼 추가
  - 실행 결과를 기존 delivery run 목록에서 `IN_APP_REMINDER`로 확인 가능
  - `SENT`, `SKIPPED`, `FAILED` item 상태 표시
- Merchant: `/merchant/pro/weekly-report-notifications`
  - `Weekly Report 확인 리마인드` 알림도 기존 알림 목록에 표시
  - reminder 알림도 unread count와 read-all 대상에 포함

## Reminder 중복 방지 기준

- 대상은 `status=UNREAD`이고 snapshot이 있는 Weekly Report 내부 알림
- title/message에 `리마인드`가 포함된 reminder 알림은 원본 reminder 대상으로 보지 않음
- 동일 `merchant_id + snapshot_id`에 아직 읽지 않은 reminder notification이 있으면 새 reminder 생성 없이 `SKIPPED`
- READ 처리된 알림은 reminder 대상에서 제외

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS
- admin remind-unread API 직접 호출: PASS
- UNREAD notification 대상 reminder 생성 확인: PASS
- READ notification은 로그인 merchant 기준 read-all 후 unread count 0으로 제외 확인: PASS
- 이미 reminder가 있는 대상은 중복 생성 없이 `SKIPPED` 확인: PASS
- 새 delivery run이 `IN_APP_REMINDER`, `IN_APP`으로 기록되는지 확인: PASS
- reminder item `SENT`, `SKIPPED` 기록 확인: PASS
- merchant 알림 목록에서 reminder 알림 확인: PASS
- merchant unread count에 reminder 알림 반영 확인: PASS
- merchant read-all 유지 확인: PASS
- merchant/customer admin reminder API 접근 차단 403 확인: PASS
- 기존 delivery preview/mock-send 유지 확인: PASS
- 기존 scheduler CLI 유지 확인: PASS
- 기존 retry failed 유지 확인: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

검증 메모:

- fresh unread original notification 1건 기준 reminder 실행 시 `IN_APP_REMINDER` run 생성 및 `SENT` 1건 확인
- reminder 생성 후 merchant unread count가 증가하는 것 확인
- 동일 대상 재실행 시 기존 unread reminder 때문에 `SKIPPED` 처리 확인
- 로그인 merchant read-all 후 해당 merchant unread count 0 확인
- scheduler CLI는 동일 기간 중복 실행 방지로 `SKIPPED` 정상 종료 확인
- retry failed fixture 기준 새 `RETRY` batch run 생성 확인

## 남은 한계

- 실제 이메일/카카오/Push 발송은 아직 없다.
- 수신 동의 관리, 외부 발송 실패 webhook, 실제 재발송 정책은 아직 없다.
- reminder 중복 방지는 DB 컬럼 없이 title/message와 merchant/snapshot 기준으로 처리하는 MVP 방식이다.
