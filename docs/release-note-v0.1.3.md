# Release Note Draft v0.1.3

## 상태

`v0.1.3`은 아직 Release Candidate 준비 단계다.

- 현재 공식 최신 Release: `v0.1.2-demo-stabilized`
- v0.1.3 공식 tag: 아직 생성 전
- v0.1.3 GitHub Release: 아직 생성 전
- 새 tag 생성 없음
- 새 GitHub Release 생성 없음
- 기존 tag 삭제/이동 없음

## v0.1.3 목적

v0.1.3의 목적은 실제 PG, 배송, POS, 외부 알림 연동을 바로 붙이는 것이 아니라, 이후 실제 연동을 안전하게 붙일 수 있는 adapter readiness 기반을 준비하는 것이다.

핵심 방향:

- Payment / Delivery / Notification / POS provider skeleton을 준비한다.
- 실제 외부 API 호출 없이 mock/noop dry-run으로 검증한다.
- 관리자 화면에서 외부 연동 전 adapter 준비 상태를 read-only로 확인한다.
- smoke test에서 adapter readiness와 권한 차단을 자동 검증한다.
- API key, secret, token, webhook URL은 추가하지 않는다.

## v0.1.2 대비 변경 요약

- Payment provider readiness / mock dry-run service 추가
- Delivery provider base / mock / noop skeleton 추가
- Notification provider base / mock / noop skeleton 추가
- POS provider readiness / mock dry-run service 추가
- External Integration Readiness 통합 service 추가
- ADMIN read-only readiness API 추가
- Admin Dashboard에 External Integration Readiness 카드 추가
- smoke test에 Payment / Delivery / Notification / POS adapter mock dry-run 검증 추가
- merchant 권한으로 admin readiness API 접근 시 403 검증 추가
- v0.1.3 scope / adapter skeleton / readiness 문서 정리

## Payment Provider Adapter Skeleton

- 기존 `app/services/payments` provider 구조를 유지한다.
- `MockPaymentProvider` dry-run으로 ready / confirm 상태를 검증한다.
- `TOSS` 등 실제 provider는 skeleton / not enabled 상태로 유지한다.
- 실제 PG 승인, 카드 청구, 환불 API 호출은 하지 않는다.

## Delivery Provider Adapter Skeleton

- `delivery_provider` base / mock / noop 구조를 추가했다.
- `MockDeliveryProvider`는 quote / create dry-run만 수행한다.
- `NoopDeliveryProvider`는 실제 연동이 비활성화되었음을 명확히 반환한다.
- 실제 배송 접수, 배송 추적, 배송 취소 API 호출은 하지 않는다.

## Notification Provider Adapter Skeleton

- `notification_provider` base / mock / noop 구조를 추가했다.
- `IN_APP_MOCK`은 BreadGo 내부 mock notification 기준이다.
- `NOOP_EXTERNAL_NOTIFICATION`은 Email / Kakao / Push / Slack / Discord / Webhook 비활성 상태를 반환한다.
- 실제 외부 발송은 하지 않는다.

## POS Provider Readiness

- 기존 `pos_providers` 구조를 유지한다.
- `MOCK_POS`는 mock readiness / normalization dry-run을 검증한다.
- `GENERIC_POS`는 not configured / noop 상태로 유지한다.
- 실제 POS API 호출과 token 저장은 하지 않는다.

## External Integration Readiness API

추가 API:

- `GET /api/v1/admin/pro/operations/external-integrations/readiness`

특징:

- ADMIN 전용
- read-only
- DB 변경 없음
- Payment / Delivery / Notification / POS readiness와 dry-run 결과 반환
- 모든 항목에 `external_calls_enabled=false` 포함
- merchant 접근은 403

## Admin External Integration Readiness Card

Admin Dashboard에 adapter 준비 상태 카드를 추가했다.

표시 항목:

- Payment readiness
- Delivery readiness
- Notification readiness
- POS readiness
- mock/noop dry-run 결과
- `외부 호출 없음` 상태

이 카드는 실제 외부 연동 상태가 아니라 실제 연동 전 adapter 준비 상태를 보여준다.

## Smoke Test 확장

추가 검증:

- Payment adapter mock dry-run
- Delivery adapter mock dry-run
- Notification adapter mock dry-run
- POS adapter mock dry-run
- External integration readiness dry-run
- Admin readiness API 조회
- Merchant readiness API 접근 차단 403
- `external_calls_enabled=false` 확인

## Mock / Noop 처리 원칙

- Mock provider는 내부 dry-run만 수행한다.
- Noop provider는 실제 연동이 비활성화되었음을 명확히 반환한다.
- 실제 provider API 호출은 하지 않는다.
- 실패 메시지와 readiness message에는 mock/noop 상태를 드러낸다.
- smoke test는 외부 네트워크 없이 통과해야 한다.

## external_calls_enabled=false 원칙

v0.1.3 RC 기준 모든 adapter readiness와 dry-run 결과는 외부 호출 비활성 상태여야 한다.

- `external_calls_enabled=false`
- API key / secret / token / webhook URL 없음
- provider webhook 처리 없음
- 실결제 / 실배송 / 실발송 없음

## 포함 범위

- Payment adapter skeleton / readiness
- Delivery adapter skeleton / readiness
- Notification adapter skeleton / readiness
- POS readiness
- External Integration Readiness service / schema / API
- Admin Dashboard readiness card
- smoke test 확장
- 문서 / release checklist / verification template

## 제외 범위

- 실제 PG 승인 / 환불
- 실제 배송 접수 / 추적
- 실제 POS API 호출
- 실제 이메일 / 카카오 / Push / Slack / Discord / Webhook 발송
- API key / secret / token / webhook URL 저장
- DB schema 변경
- migration 추가
- 대량 비동기 큐
- 실시간 AI 모델
- 운영용 secret manager 구현

## 검증 결과

Release Candidate 준비 기준으로 아래 명령이 통과했다.

- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS
- `python scripts/run_pro_health_alert_check.py`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## Release 생성 전 주의사항

- v0.1.3 tag는 아직 만들지 않는다.
- GitHub Release는 아직 만들지 않는다.
- `origin/main` push는 별도 Phase에서 수행한다.
- 실제 외부 연동이 아니라 adapter readiness Release임을 Release title/body에 명확히 적는다.
- 기존 `v0.1.2-demo-stabilized` Release는 공식 최신 Release로 유지한다.

## 추천 Release 정보

- 추천 tag: `v0.1.3-adapter-readiness`
- 대안 tag: `v0.1.3-mock-integrations`, `v0.1.3-external-readiness`
- 추천 Release title: `BreadGo Adapter Readiness Release v0.1.3`

## Suggested commit message

`Prepare v0.1.3 release candidate docs`
