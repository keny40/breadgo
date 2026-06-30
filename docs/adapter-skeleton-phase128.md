# Adapter Skeleton Phase 128

## 목적

v0.1.3 범위에 따라 실제 외부 API 호출 없이 Payment / Delivery provider adapter skeleton을 구현했다.

이번 Phase에서는 DB schema, migration, 실제 PG API, 실제 배송 provider API를 변경하거나 호출하지 않았다.

## Payment adapter skeleton

기존 `app/services/payments` provider 구조를 유지하면서 readiness / dry-run service를 추가했다.

추가 서비스:

- `backend/app/services/payment_provider_service.py`

구성:

- `PaymentProviderReadiness`
- `PaymentProviderDryRunResult`
- `get_payment_provider_readiness()`
- `run_mock_payment_provider_dry_run()`
- `assert_mock_payment_provider_ready()`

동작 기준:

- `MOCK`: `READY`, `MOCK_ONLY`, external calls disabled
- `TOSS`: `NOT_ENABLED`, `SKELETON_ONLY`, external calls disabled
- dry-run은 `MockPaymentProvider.ready()`와 `MockPaymentProvider.confirm()`만 호출한다.
- 실제 PG API 호출, API key, secret, token 사용은 없다.

## Delivery adapter skeleton

새 delivery provider skeleton을 추가했다.

추가 파일:

- `backend/app/services/delivery_provider/base.py`
- `backend/app/services/delivery_provider/mock.py`
- `backend/app/services/delivery_provider/noop.py`
- `backend/app/services/delivery_provider/__init__.py`
- `backend/app/services/delivery_provider_service.py`

구성:

- `DeliveryProviderAdapter`
- `DeliveryProviderReadiness`
- `DeliveryQuoteRequest`
- `DeliveryQuoteResult`
- `DeliveryCreateResult`
- `MockDeliveryProvider`
- `NoopDeliveryProvider`
- `get_delivery_provider_readiness()`
- `run_mock_delivery_provider_dry_run()`
- `assert_mock_delivery_provider_ready()`

동작 기준:

- `MOCK_DELIVERY`: `READY`, `MOCK_ONLY`, external calls disabled
- `NOOP_DELIVERY`: `NOT_ENABLED`, `NOOP_ONLY`, external calls disabled
- dry-run은 mock quote / mock create만 수행한다.
- 실제 배송 provider API 호출, token, webhook URL 사용은 없다.

## 기존 흐름 유지

- 기존 Mock payment ready / confirm / cancel 흐름은 변경하지 않았다.
- 기존 수동 배송 상태 변경 흐름은 변경하지 않았다.
- 기존 reservation / payment / delivery status DB schema는 변경하지 않았다.
- 기존 화면 UX와 Pro Operations 흐름은 그대로 유지한다.

## Smoke test 추가 범위

`backend/scripts/smoke_test.py`에 아래 검증을 추가했다.

- `Payment provider adapter mock dry-run`
  - `MockPaymentProvider.ready()` 결과가 `READY`인지 확인
  - `MockPaymentProvider.confirm()` 결과가 `PAID`인지 확인
  - external calls enabled가 아닌지 확인

- `Delivery provider adapter mock dry-run`
  - `MockDeliveryProvider.validate_connection()` 결과가 `READY`인지 확인
  - `MockDeliveryProvider.create_delivery()` 결과가 `REQUESTED`인지 확인
  - external calls enabled가 아닌지 확인

실패 시 smoke output에는 adapter 이름과 mock/noop dry-run 실패 사유가 표시된다.

## Mock / 실제 연동 경계

현재 `v0.1.2-demo-stabilized`와 v0.1.3 준비 범위에서는 아래를 하지 않는다.

- 실제 PG 승인
- 실제 PG 환불
- 실제 배송 접수
- 실제 배송 추적 API 호출
- API key / secret / token / webhook URL 저장
- 외부 provider webhook 처리
- 대량 비동기 큐

## 검증 결과

- `git status`: 변경 파일 확인
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## 변경 여부

- DB schema 변경: 없음
- migration 추가: 없음
- 실제 PG API 호출: 없음
- 실제 배송 provider API 호출: 없음
- API key / secret / token / webhook URL 추가: 없음
- 새 tag / 새 Release 생성: 없음
- 기존 tag 삭제/이동: 없음

## Suggested commit message

`Add payment delivery adapter skeletons`
