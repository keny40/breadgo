# BreadGo Phase 41 Flutter 고객 예약 흐름

## 목적

Phase 41은 Flutter 고객 앱에서 상품 상세 화면을 실제 고객 행동 흐름에 연결하는 단계입니다.
웹 MVP에서 이미 검증된 FastAPI 예약 및 Mock 결제 API를 모바일 앱에서도 호출할 수 있게 했습니다.

## 고객 예약 흐름

현재 Flutter 고객 앱 흐름:

1. 고객이 로그인합니다.
2. 상품 목록에서 지역 상품을 확인합니다.
3. 상품 상세 화면으로 이동합니다.
4. 상품별 가능한 수령 방식을 선택합니다.
5. 배송 방식이면 수령자/연락처/주소/요청사항을 입력합니다.
6. 수량을 선택합니다.
7. `예약 생성 후 Mock 결제` 버튼을 누릅니다.
8. 앱이 예약 생성 API를 호출합니다.
9. 앱이 Mock 결제 ready API를 호출합니다.
10. 앱이 Mock 결제 confirm API를 호출합니다.
11. 내 예약 목록을 새로고침합니다.
12. 고객은 내 예약 화면에서 예약 상태, 결제 상태, 수령 방식, 픽업 코드를 확인합니다.

## API 호출 순서

### 1. 예약 생성

```text
POST /api/v1/reservations
```

payload:

```json
{
  "product_id": "product-id",
  "quantity": 1,
  "fulfillment_method": "PICKUP",
  "recipient_name": null,
  "recipient_phone": null,
  "delivery_address": null,
  "delivery_request_memo": null,
  "delivery_fee": 0
}
```

### 2. Mock 결제 준비

```text
POST /api/v1/payments/mock/ready
```

payload:

```json
{
  "reservation_id": "reservation-id",
  "method": "MOCK_CARD"
}
```

### 3. Mock 결제 승인

```text
POST /api/v1/payments/mock/confirm
```

payload:

```json
{
  "payment_id": "payment-id"
}
```

### 4. 내 예약 갱신

```text
GET /api/v1/reservations/me
```

## 수령 방식 처리

백엔드 enum과 동일한 값을 사용합니다.

- `PICKUP`: 매장 직접 픽업
- `QUICK_DELIVERY`: 퀵배달 요청
- `PARCEL_DELIVERY`: 택배 배송

상품 응답의 가능 여부 필드에 따라 선택지를 제한합니다.

- `allow_pickup`
- `allow_quick_delivery`
- `allow_parcel_delivery`

배송비는 상품 응답의 값을 사용합니다.

- `quick_delivery_fee`
- `parcel_delivery_fee`

`QUICK_DELIVERY`, `PARCEL_DELIVERY` 선택 시 필수 입력:

- 받는 사람
- 받는 사람 연락처
- 주소

## Mock 결제 처리

실제 PG는 연결하지 않습니다.
모바일 앱은 기존 백엔드 Mock 결제 API만 사용합니다.

현재 결제 method:

```text
MOCK_CARD
```

결제 성공 후:

- 예약 목록을 새로고침합니다.
- PICKUP이면 픽업 코드를 보여줍니다.
- 배송 방식이면 배송 요청 접수 안내를 보여줍니다.

## Android emulator 테스트 방법

로컬 백엔드 실행:

```powershell
cd backend
python -m alembic upgrade head
python scripts/seed_demo.py
python -m uvicorn app.main:app --reload --port 8000
```

Flutter 앱 실행:

```powershell
cd mobile
flutter pub get
flutter run --dart-define=BREADGO_API_BASE_URL=http://10.0.2.2:8000
```

Android emulator에서 `localhost`는 emulator 내부를 의미합니다.
호스트 PC의 FastAPI 서버에 접근하려면 `10.0.2.2`를 사용합니다.

배포 백엔드로 테스트:

```powershell
flutter run --dart-define=BREADGO_API_BASE_URL=https://breadgo-api.onrender.com
```

## 남은 한계

- Mock 결제 수단 선택 UI는 아직 없음
- 예약 취소/Mock 환불은 아직 모바일에 연결하지 않음
- 알림센터 API는 아직 모바일에 연결하지 않음
- JWT 보안 저장소는 아직 적용하지 않음
- 배송 상태 상세 관리는 아직 모바일에 없음
- 실제 PG 결제는 아직 없음
