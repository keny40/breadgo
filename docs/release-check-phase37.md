# BreadGo Phase 37 결제 Provider 구조 준비

## 작업 목적

Phase 37은 실제 PG 결제를 바로 연동하지 않고, 현재 Mock 결제와 향후 실제 PG 결제를 분리할 수 있는 provider 구조를 준비하는 단계입니다.

## 변경 내용

- `payments.provider` 컬럼 추가
- 기존 결제 데이터는 `provider=MOCK`으로 채움
- 신규 Mock 결제 생성 시 `provider=MOCK` 저장
- 결제 응답에 `provider` 포함
- 결제 provider adapter 구조 추가
  - `PaymentProviderAdapter`
  - `MockPaymentProvider`
  - `TossPaymentProvider`
- Toss provider는 실제 API 호출 없이 skeleton으로만 추가
- 기존 Mock 결제 API endpoint 유지
- `/my-payments`에서 결제 Provider 표시
- Toss Payments 연동 설계 문서 추가

## 변경하지 않은 것

- 실제 Toss API 호출 없음
- 실제 PG API key 요구 없음
- 기존 Mock 결제 endpoint 변경 없음
- 기존 예약, 픽업, 배송, 환불, 정산 비즈니스 규칙 변경 없음
- 프론트엔드 결제 화면의 기본 흐름 변경 없음

## DB 변경

마이그레이션:

```text
202606180006_add_payment_provider.py
```

추가 컬럼:

```text
payments.provider VARCHAR(32) NOT NULL
```

기존 row는 모두:

```text
MOCK
```

으로 업데이트됩니다.

## 검증 명령

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/smoke_test.py

cd frontend
npm run lint
npm run build
```

## 확인 항목

1. 기존 Mock 결제 ready API가 정상 동작하는지
2. 기존 Mock 결제 confirm API가 정상 동작하는지
3. 결제 응답에 `provider=MOCK`이 포함되는지
4. `/my-payments`에서 Provider가 표시되는지
5. 예약 → Mock 결제 → 픽업 → 정산 smoke test가 통과하는지
6. Toss provider가 실제 외부 API를 호출하지 않는지

## 한계

- 실제 Toss 결제창은 아직 연결하지 않았습니다.
- Toss 승인/취소/webhook API는 아직 없습니다.
- PG 수수료는 여전히 Mock 계산값을 사용합니다.
- 실제 결제 실패/부분 환불/idempotency 정책은 다음 단계에서 설계해야 합니다.

## 다음 단계

- Toss 테스트 키 환경 변수 설계
- Toss 결제창 프론트엔드 연동
- Toss confirm API 구현
- Toss webhook 검증
- 실제 PG 취소/환불 처리
- 결제/정산 운영 모니터링 추가
