# Phase 86 Release Check

## 작업 목적

Weekly Report를 실제 이메일/카카오/Push로 발송하기 전, Phase 85 delivery preview의 `READY` item을 BreadGo 내부 알림으로 mock delivery 처리하는 MVP를 추가했다.

## 변경 사항

- Weekly Report 전용 in-app notification 테이블 추가
- ADMIN 전용 mock-send API 추가
- MERCHANT 전용 Weekly Report 알림 목록/읽음 API 추가
- 관리자 delivery 화면에 `In-app mock delivery 실행` 버튼 추가
- 점주 화면 `/merchant/pro/weekly-report-notifications` 추가
- 점주 NavBar와 Pro 대시보드에 리포트 알림 링크 추가
- 실제 이메일/카카오/Push/외부 API 호출은 구현하지 않음
- 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않음

## DB 변경 여부

- DB 변경 있음
- Migration: `backend/alembic/versions/202606180021_create_weekly_report_in_app_notifications.py`
- 추가 테이블:
  - `pro_weekly_report_in_app_notifications`
- 기존 delivery run/item, batch run/item 테이블은 변경하지 않음

## API 목록

- `POST /api/v1/admin/pro/weekly-report/delivery-runs/{delivery_run_id}/mock-send`
- `GET /api/v1/admin/pro/weekly-report/delivery-runs`
- `GET /api/v1/admin/pro/weekly-report/delivery-runs/{delivery_run_id}`
- `GET /api/v1/merchant/pro/weekly-report/notifications`
- `POST /api/v1/merchant/pro/weekly-report/notifications/{notification_id}/read`

## 화면 경로

- Admin: `/admin/pro/weekly-report-deliveries`
- Merchant: `/merchant/pro/weekly-report-notifications`

## Mock Delivery 기준

- 원본 delivery preview run의 `READY` item만 대상
- `SKIPPED`, `FAILED` item은 발송 대상에서 제외
- mock delivery 실행 시 새 delivery run 생성
  - `run_type=IN_APP_MOCK`
  - `channel=IN_APP`
- 처리 성공 item은 `SENT`
- snapshot 누락 등 대상 부적절 item은 `SKIPPED`
- 예외 발생 item은 `FAILED`
- 성공 item마다 `pro_weekly_report_in_app_notifications`에 점주 내부 알림 생성
- 알림 message는 Weekly Report 확인 안내 수준으로만 작성

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- admin delivery preview 생성: PASS
- READY item이 있는 delivery run에서 mock-send 직접 호출: PASS
- 새 `IN_APP_MOCK` delivery run 생성 확인: PASS
- mock delivery item `SENT` 기록 확인: PASS
- in-app notification 생성 확인: PASS
- merchant notification 목록 조회 확인: PASS
- merchant notification 읽음 처리 확인: PASS
- customer의 merchant notification API 접근 차단 확인: PASS
- merchant/customer admin mock-send API 접근 차단 403 확인: PASS
- 기존 scheduler CLI 유지 확인: PASS
- 기존 retry failed 유지 확인: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

검증 메모:

- preview `READY` 2건 기준 mock delivery run `IN_APP_MOCK`, `IN_APP`, `SENT` 2건 확인
- merchant notification 목록에서 내부 알림 생성 확인 후 `READ` 처리 확인
- READY item이 없는 preview run에 mock-send 요청 시 400으로 안전 차단 확인
- scheduler CLI는 동일 기간 중복 실행 방지로 `SKIPPED` 정상 종료 확인
- retry failed fixture 기준 새 `RETRY` batch run 생성 확인

## 남은 한계

- 실제 이메일/카카오/Push 발송은 아직 없다.
- 외부 발송 실패 webhook, 수신 동의 관리, 재발송 정책은 아직 없다.
- 일반 사용자 알림센터와는 분리된 Weekly Report 전용 점주 알림 MVP다.
