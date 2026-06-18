# BreadGo Phase 42 Flutter 알림센터와 예약 취소 흐름

## 목적

Phase 42는 Flutter 고객 앱에서 인앱 알림센터 API와 예약 취소/Mock 환불 흐름을 연결하는 단계입니다.
기존 웹 MVP와 동일한 FastAPI API를 사용하며, 실제 PG 환불은 연결하지 않습니다.

## Flutter 알림센터 흐름

현재 모바일 알림 흐름:

1. 고객이 로그인합니다.
2. 알림 탭을 엽니다.
3. 앱이 내 알림 목록을 조회합니다.
4. 읽지 않은 알림은 강조 카드로 표시합니다.
5. 고객은 개별 알림을 읽음 처리할 수 있습니다.
6. 고객은 모든 알림을 한 번에 읽음 처리할 수 있습니다.

## 알림 API 호출 순서

### 내 알림 조회

```text
GET /api/v1/notifications/me
```

### 개별 읽음 처리

```text
PATCH /api/v1/notifications/{notification_id}/read
```

### 모두 읽음 처리

```text
PATCH /api/v1/notifications/read-all
```

## 예약 취소/Mock 환불 흐름

현재 모바일 취소 흐름:

1. 고객이 내 예약 화면을 엽니다.
2. 취소 가능한 예약에만 `예약 취소` 버튼을 표시합니다.
3. 고객이 취소 버튼을 누르면 확인 다이얼로그를 표시합니다.
4. 고객이 확인하면 예약 취소 API를 호출합니다.
5. 백엔드는 예약 상태를 `CANCELLED`로 변경하고 Mock 환불 상태를 반영합니다.
6. 앱은 내 예약 목록을 새로고침합니다.

## 예약 취소 API

```text
POST /api/v1/reservations/{reservation_id}/cancel
```

## 취소 가능 상태 기준

모바일 앱에서는 다음 조건을 기준으로 취소 버튼을 표시합니다.

- 예약 상태가 `CONFIRMED`
- 결제 상태가 `PAID`
- 배송 상태가 `SENT` 또는 `DELIVERED`가 아님

백엔드에서도 동일한 비즈니스 규칙을 최종 검증합니다.

취소 불가 예시:

- 이미 픽업 완료된 예약
- 이미 취소된 예약
- 배송이 시작되었거나 완료된 예약
- 결제 완료 전 예약

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

테스트 흐름:

1. 고객 계정으로 로그인합니다.
2. 상품 상세에서 예약 생성 후 Mock 결제를 완료합니다.
3. 내 예약에서 예약 상태와 결제 상태를 확인합니다.
4. `예약 취소`를 누릅니다.
5. 확인 다이얼로그에서 취소를 확정합니다.
6. 예약 상태가 `CANCELLED`로 바뀌는지 확인합니다.
7. 알림 탭에서 결제/취소/환불 알림을 확인합니다.
8. 개별 읽음 처리와 모두 읽음 처리를 테스트합니다.

## 남은 한계

- 실제 PG 환불 없음
- 알림은 인앱 알림만 표시
- Push, SMS, 이메일, 카카오 알림톡 연동 없음
- 예약 상태 이력 화면은 아직 모바일에 없음
- JWT 보안 저장소 미적용
