# BreadGo Phase 43 Flutter 예약 상태 이력 흐름

## 목적

Phase 43은 Flutter 고객 앱의 내 예약 화면에서 예약 상태 이력을 확인할 수 있게 연결하는 단계입니다.
웹 MVP에서 이미 제공하던 예약 이력 API를 모바일에서도 사용합니다.

## Flutter 예약 상태 이력 흐름

1. 고객이 로그인합니다.
2. 내 예약 화면을 엽니다.
3. 예약 카드에서 `상태 이력 보기`를 누릅니다.
4. 앱이 예약 이력 API를 호출합니다.
5. bottom sheet에서 상태 이력을 타임라인 형태로 표시합니다.

## API 호출 순서

```text
GET /api/v1/reservations/{reservation_id}/history
```

응답 주요 필드:

- `id`
- `reservation_id`
- `actor_user_id`
- `actor_role`
- `actor_email`
- `event_type`
- `from_status`
- `to_status`
- `message`
- `created_at`

## 표시되는 이력 종류

모바일에서 읽기 쉬운 라벨로 표시합니다.

- `RESERVATION_CREATED`: 예약 생성
- `PAYMENT_COMPLETED`: 결제 완료
- `PICKUP_CONFIRMED`: 픽업 완료
- `DELIVERY_STATUS_CHANGED`: 배송 상태 변경
- `RESERVATION_CANCELLED`: 예약 취소
- `MOCK_REFUND_PROCESSED`: Mock 환불 처리
- `SETTLEMENT_STATUS_CHANGED`: 정산 상태 변경

## 고객 앱에서의 활용 목적

- 예약이 정상 생성되었는지 확인
- Mock 결제가 완료되었는지 확인
- 픽업/배송/취소/환불 상태 변경 내역 확인
- 고객 문의 시 상태 변경 흐름을 빠르게 파악

## Android emulator 테스트 방법

백엔드 실행:

```powershell
cd backend
python -m alembic upgrade head
python scripts/seed_demo.py
python -m uvicorn app.main:app --reload --port 8000
```

Flutter 실행:

```powershell
cd mobile
flutter run --dart-define=BREADGO_API_BASE_URL=http://10.0.2.2:8000
```

테스트 흐름:

1. 고객 계정으로 로그인합니다.
2. 상품을 예약하고 Mock 결제를 완료합니다.
3. 내 예약 화면으로 이동합니다.
4. 예약 카드의 `상태 이력 보기`를 누릅니다.
5. 예약 생성과 결제 완료 이력이 표시되는지 확인합니다.
6. 예약 취소 후 다시 이력을 열어 취소/Mock 환불 이력을 확인합니다.

## 남은 한계

- 상태 이력은 읽기 전용입니다.
- 모바일에서는 관리자/가맹점 이력 화면을 제공하지 않습니다.
- 이력 상세 필터나 검색은 아직 없습니다.
- Push/Firebase/실제 PG/보안 저장소는 이번 Phase 범위가 아닙니다.
