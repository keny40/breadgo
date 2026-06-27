# Phase 87 Release Check

## 작업 목적

Phase 86에서 생성된 Weekly Report 내부 알림의 읽음/미확인 상태를 관리자와 점주가 더 명확히 확인할 수 있도록 통계 API와 UI를 보강했다.

## 변경 사항

- 관리자 Weekly Report notification summary API 추가
- 관리자 Weekly Report notification list API 추가
- 점주 Weekly Report notification unread count API 추가
- 점주 Weekly Report notification read-all API 추가
- 관리자 delivery 화면에 내부 알림 통계와 알림 목록 표시
- 점주 Weekly Report 알림 화면에 미확인 개수, 모두 읽음 처리, READ/UNREAD 필터 추가
- 점주 NavBar에 리포트 알림 미확인 개수 표시
- 실제 이메일/카카오/Push/외부 발송 API는 추가하지 않음
- 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않음

## DB 변경 여부

- DB 변경 없음
- 기존 `pro_weekly_report_in_app_notifications` 테이블을 재사용
- Alembic migration 추가 없음

## API 목록

- `GET /api/v1/admin/pro/weekly-report/notifications/summary`
- `GET /api/v1/admin/pro/weekly-report/notifications`
- `GET /api/v1/merchant/pro/weekly-report/notifications/unread-count`
- `POST /api/v1/merchant/pro/weekly-report/notifications/read-all`
- 기존 유지:
  - `GET /api/v1/merchant/pro/weekly-report/notifications`
  - `POST /api/v1/merchant/pro/weekly-report/notifications/{notification_id}/read`
  - `POST /api/v1/admin/pro/weekly-report/delivery-runs/{delivery_run_id}/mock-send`

## 화면 변경 사항

- Admin: `/admin/pro/weekly-report-deliveries`
  - 전체 알림 수, 읽음 수, 미확인 수, 읽음률, 최근 생성일, 최근 읽음일 표시
  - notification 목록에 merchant_id, snapshot_id, delivery_run_id, status, created_at, read_at 표시
- Merchant: `/merchant/pro/weekly-report-notifications`
  - 미확인 알림 개수 표시
  - 모두 읽음 처리 버튼 추가
  - 전체/미확인/읽음 필터 추가
  - 읽지 않은 알림 강조 표시
- NavBar:
  - merchant role에서 `리포트 알림 N` 형태로 미확인 개수 표시

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- admin notification summary API 직접 호출: PASS
- admin notification list API 직접 호출: PASS
- merchant unread count API 직접 호출: PASS
- merchant read-all API 직접 호출: PASS
- 다른 merchant 알림 개별 읽음 접근 차단 확인: PASS
- merchant/customer admin notification API 접근 차단 403 확인: PASS
- 기존 admin delivery preview 유지 확인: PASS
- 기존 mock-send 유지 확인: PASS
- 기존 scheduler CLI 유지 확인: PASS
- 기존 retry failed 유지 확인: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

검증 메모:

- mock-send로 생성된 내부 알림 기준 admin summary/list에서 total/read/unread/read_rate 확인
- merchant unread count 1건 확인 후 read-all 처리로 unread count 0건 확인
- 로그인 merchant가 아닌 notification_id 읽음 처리 요청은 404로 차단 확인
- customer의 merchant notification API 접근은 403/404로 차단 확인
- scheduler CLI는 동일 기간 중복 실행 방지로 `SKIPPED` 정상 종료 확인
- retry failed fixture 기준 새 `RETRY` batch run 생성 확인

## 남은 한계

- 실제 이메일/카카오/Push 발송은 아직 없다.
- 수신 동의 관리, 외부 발송 실패 webhook, 재발송 정책은 아직 없다.
- 알림 analytics는 현재 내부 알림 테이블 기준의 MVP 통계다.
