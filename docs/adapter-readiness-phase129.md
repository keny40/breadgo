# Adapter Readiness Phase 129

## 목적

v0.1.3 adapter skeleton 범위 중 남은 Notification / POS adapter skeleton을 추가하고, Payment / Delivery / Notification / POS 전체 readiness를 관리자 화면에서 read-only로 확인할 수 있게 했다.

이번 Phase에서는 DB schema, migration, 실제 외부 API 호출을 변경하지 않았다.

## 추가한 adapter skeleton

### Notification provider

추가 파일:

- `backend/app/services/notification_provider/base.py`
- `backend/app/services/notification_provider/mock.py`
- `backend/app/services/notification_provider/noop.py`
- `backend/app/services/notification_provider/__init__.py`
- `backend/app/services/notification_provider_service.py`

상태:

- `IN_APP_MOCK`: `READY`, `IN_APP_MOCK_ONLY`, external calls disabled
- `NOOP_EXTERNAL_NOTIFICATION`: `NOT_ENABLED`, `NOOP_ONLY`, external calls disabled

실제 이메일/카카오/Push/Slack/Discord/Webhook 발송은 하지 않는다.

### POS provider

추가 파일:

- `backend/app/services/pos_provider_service.py`

상태:

- `MOCK_POS`: `READY`, `MOCK_ONLY`, external calls disabled
- `GENERIC_POS`: `NOT_CONFIGURED`, `NOOP_ONLY`, external calls disabled

기존 `pos_providers` 구조와 Mock POS sync 흐름은 유지한다. 실제 POS API 호출과 token 저장은 하지 않는다.

## 통합 readiness service / API

추가 파일:

- `backend/app/services/external_integration_readiness_service.py`
- `backend/app/schemas/external_integration.py`

추가 API:

- `GET /api/v1/admin/pro/operations/external-integrations/readiness`

특징:

- ADMIN 전용 read-only API
- DB 변경 없음
- Payment / Delivery / Notification / POS readiness와 mock dry-run 결과 반환
- 모든 item과 dry-run에 `external_calls_enabled: false` 포함
- merchant 권한 접근은 403

응답 핵심 필드:

- `overall_status`
- `external_calls_enabled`
- `message`
- `items[]`
- `dry_runs[]`

## 관리자 화면 변경

수정 파일:

- `frontend/app/admin/page.tsx`
- `frontend/lib/types.ts`

변경 내용:

- Admin Dashboard에 `External Integration Readiness` 카드 추가
- Payment / Delivery / Notification / POS adapter 상태 표시
- mock dry-run 결과 표시
- 실제 외부 연동 상태가 아니라 실제 연동 전 adapter 준비 상태임을 명확히 표시
- `외부 호출 없음` badge 표시

## smoke test 추가 범위

수정 파일:

- `backend/scripts/smoke_test.py`

추가 검증:

- Payment adapter readiness / dry-run
- Delivery adapter readiness / dry-run
- Notification adapter readiness / dry-run
- POS adapter readiness / dry-run
- External integration readiness dry-run
- Admin external integration readiness API 조회
- merchant 권한으로 admin readiness API 접근 시 403
- readiness 응답에서 `external_calls_enabled=false` 확인
- PAYMENT / DELIVERY / NOTIFICATION / POS 영역 포함 확인

## 기존 흐름 유지

아래 흐름은 변경하지 않았다.

- 기존 Mock payment ready / confirm / cancel
- 기존 수동 배송 상태 변경
- 기존 in-app notification
- 기존 CSV import
- 기존 Mock POS sync
- 기존 Pro Operations / Weekly Report / Health Alert 흐름

## 실제 외부 API 호출 여부

호출하지 않음:

- PG API
- 배송 provider API
- POS API
- Email API
- Kakao API
- Push API
- Slack / Discord / Webhook

추가하지 않음:

- API key
- secret
- token
- webhook URL

## 검증 결과

- `git status`: 변경 파일 확인
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS
- `python scripts/run_pro_health_alert_check.py`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## 변경 여부

- DB schema 변경: 없음
- migration 추가: 없음
- 신규 DB table 없음
- 신규 API: ADMIN read-only readiness API만 추가
- 실제 외부 API 호출: 없음
- 새 tag / 새 Release 생성: 없음
- 기존 tag 삭제/이동: 없음

## Suggested commit message

`Add adapter readiness dashboard`
