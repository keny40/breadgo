# BreadGo Phase 37 결제 Provider 설계

## 목적

Phase 37의 목적은 실제 PG를 바로 붙이는 것이 아니라, 현재 Mock 결제와 향후 실제 PG 결제를 분리할 수 있는 구조를 준비하는 것입니다.

현재 MVP는 계속 Mock 결제로 동작합니다. Toss Payments, KakaoPay, NaverPay 같은 실제 결제사는 이후 단계에서 provider adapter를 통해 확장합니다.

## 현재 Mock 결제 흐름

1. 고객이 상품을 예약합니다.
2. 프론트엔드가 `POST /api/v1/payments/mock/ready`를 호출합니다.
3. 백엔드는 `Payment`를 `provider=MOCK`, `status=READY`로 생성합니다.
4. 프론트엔드가 `POST /api/v1/payments/mock/confirm`을 호출합니다.
5. 백엔드는 결제를 `PAID`로 변경합니다.
6. 정산 데이터가 생성됩니다.
7. 고객/가맹점에게 인앱 알림이 생성됩니다.
8. 예약 상태 이력에 결제 완료 이벤트가 기록됩니다.

## Provider 구분

`payments.provider` 필드를 추가해 결제 제공자를 구분합니다.

현재 값:

```text
MOCK
```

향후 확장 후보:

```text
TOSS
KAKAO_PAY
NAVER_PAY
```

`PaymentMethod`는 사용자가 선택한 결제 수단을 표현하고, `provider`는 실제 결제를 처리하는 결제사를 표현합니다.

예:

```text
provider=MOCK, method=MOCK_CARD
provider=TOSS, method=CARD
provider=KAKAO_PAY, method=KAKAO_PAY
```

## Adapter 구조

추가된 위치:

```text
backend/app/services/payments/
```

구성:

```text
base.py
mock.py
toss.py
```

역할:

- `PaymentProviderAdapter`: provider 공통 인터페이스
- `MockPaymentProvider`: 현재 MVP Mock 결제 구현
- `TossPaymentProvider`: 실제 Toss API 호출 전 설계용 skeleton

현재 `TossPaymentProvider`는 실제 외부 API를 호출하지 않습니다. 호출 시 `501 Not Implemented`를 반환하도록 설계되어 있습니다.

## 향후 Toss Payments 승인 흐름

운영 전환 시 예상 흐름:

1. 고객이 예약을 생성합니다.
2. 백엔드가 결제 준비 정보를 생성합니다.
3. 프론트엔드가 Toss Payments 결제 위젯 또는 결제창을 엽니다.
4. 사용자가 결제를 진행합니다.
5. Toss가 `paymentKey`, `orderId`, `amount`를 반환합니다.
6. 프론트엔드가 백엔드 승인 API를 호출합니다.
7. 백엔드는 Toss 승인 API를 서버 사이드에서 호출합니다.
8. 승인 성공 시 `Payment.status=PAID`로 변경합니다.
9. 승인 실패 시 `Payment.status=FAILED`로 변경합니다.
10. webhook 수신 시 결제 상태를 재검증합니다.
11. 취소/환불은 백엔드가 Toss 취소 API를 호출한 후 상태를 반영합니다.

## 예상 API 흐름

현재 유지:

```text
POST /api/v1/payments/mock/ready
POST /api/v1/payments/mock/confirm
POST /api/v1/payments/mock/fail
POST /api/v1/payments/mock/cancel
GET  /api/v1/payments/me
```

향후 추가 후보:

```text
POST /api/v1/payments/toss/ready
POST /api/v1/payments/toss/confirm
POST /api/v1/payments/toss/cancel
POST /api/v1/payments/toss/webhook
```

## 필요한 환경 변수 예시

실제 Toss 연동 시 필요한 값:

```text
TOSS_CLIENT_KEY=
TOSS_SECRET_KEY=
TOSS_WEBHOOK_SECRET=
TOSS_SUCCESS_URL=
TOSS_FAIL_URL=
```

주의:

- `TOSS_SECRET_KEY`는 반드시 백엔드 환경 변수에만 저장합니다.
- 프론트엔드에는 공개 가능한 client key만 노출합니다.
- webhook secret은 로그에 출력하지 않습니다.

## 보안 주의사항

- 결제 승인 금액은 프론트엔드 값을 신뢰하지 않습니다.
- 백엔드의 예약 금액과 Toss 승인 금액이 같은지 검증합니다.
- `paymentKey`, `orderId`, `amount`를 모두 검증합니다.
- 중복 승인, 중복 취소, 중복 webhook을 idempotent하게 처리해야 합니다.
- webhook은 서명 또는 secret 검증을 통과한 요청만 처리합니다.
- 운영 로그에 카드번호, 계좌번호, secret key를 남기지 않습니다.

## 운영 전환 시 해야 할 일

1. Toss Payments 테스트 계정 준비
2. 백엔드 환경 변수 설정
3. Toss ready/confirm/cancel API 구현
4. 프론트엔드 Toss 결제창 연동
5. webhook 검증 및 idempotency 처리
6. 결제 실패/취소/부분 환불 정책 확정
7. 정산 기준 금액과 PG 수수료 실제 값 반영
8. 운영 모니터링 및 장애 알림 설정
9. 테스트 결제 시나리오 작성

## 이번 Phase에서 실제 API를 붙이지 않은 이유

- 현재 MVP는 데모 흐름 검증이 우선입니다.
- 실제 PG 연동은 보안, webhook, idempotency, 환불 정책까지 함께 설계해야 합니다.
- 실제 결제 API key를 저장하거나 배포 환경에 추가하기 전, provider 구조를 먼저 분리하는 것이 안전합니다.
- 기존 Mock 결제, 예약, 정산, 알림, smoke test를 깨지 않는 것이 이번 단계의 핵심입니다.
