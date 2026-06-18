# BreadGo MVP 통합 데모 시나리오 v0.3.0

## 데모 목적

BreadGo MVP는 동네 빵집의 마감 할인 상품을 고객이 예약하고, Mock 결제 후 픽업 또는 배송 요청까지 진행하는 로컬 푸드 리스큐 서비스 흐름을 보여줍니다.

이 데모는 다음을 확인하는 데 목적이 있습니다.

- 고객의 상품 탐색, 예약, 결제, 취소 흐름
- 가맹점의 상품/주문/픽업/배송/정산 관리 흐름
- 관리자의 운영 현황 및 정산 관리 흐름
- Flutter 고객 앱의 핵심 고객 경험
- 알림, 상태 이력, 정산 등 운영에 필요한 보조 흐름

## 데모 URL

- 웹 프론트엔드: [https://breadgo.vercel.app](https://breadgo.vercel.app)
- 백엔드 API: [https://breadgo-api.onrender.com](https://breadgo-api.onrender.com)
- Health Check: [https://breadgo-api.onrender.com/health](https://breadgo-api.onrender.com/health)
- 데모 가이드: [https://breadgo.vercel.app/demo](https://breadgo.vercel.app/demo)

Render 무료 인스턴스는 sleep 상태일 수 있습니다. 첫 API 요청은 느릴 수 있으므로 데모 시작 전에 `/health`를 한 번 열어두는 것을 권장합니다.

## 데모 계정

```text
customer@breadgo.test / 12345678
merchant@breadgo.test / 12345678
admin@breadgo.test / 12345678
```

## 웹 고객 데모 흐름

1. `customer@breadgo.test`로 로그인합니다.
2. `/products`에서 지역을 선택합니다.
   - 서울특별시 강남구 역삼동
   - 서울특별시 강남구 삼성동
   - 경기도 안산시 고잔동
3. 상품 목록과 상품 이미지를 확인합니다.
4. 상품을 선택합니다.
5. 수령 방식을 선택합니다.
   - 매장 직접 픽업
   - 퀵배달 요청
   - 택배 배송
6. 예약을 생성합니다.
7. Mock 결제를 진행합니다.
8. 결제 완료 후 픽업 코드 또는 배송 요청 정보를 확인합니다.
9. `/my-reservations`에서 예약 상태, 결제 상태, 픽업 코드, 상태 이력을 확인합니다.
10. `/my-payments`에서 결제 내역을 확인합니다.
11. 예약 취소가 가능한 상태라면 예약 취소와 Mock 환불 상태를 확인합니다.
12. `/notifications`에서 결제/취소/환불 알림을 확인하고 읽음 처리합니다.

## 웹 가맹점 데모 흐름

1. `merchant@breadgo.test`로 로그인합니다.
2. `/merchant`에서 가맹점 대시보드를 확인합니다.
3. `/merchant/stores`에서 매장과 지역 정보를 확인합니다.
4. `/merchant/products`에서 상품을 등록하거나 기존 상품을 수정합니다.
5. 상품 이미지 URL 또는 Vercel Blob 업로드를 확인합니다.
6. 상품별 수령 가능 방식과 배송비를 확인합니다.
7. `/merchant/orders`에서 주문 목록을 확인합니다.
8. 픽업 주문은 픽업 코드를 확인하고 픽업 확정합니다.
9. 배송 주문은 배송 상태를 `REQUESTED → PREPARING → SENT → DELIVERED` 흐름으로 변경합니다.
10. `/merchant/settlement-account`에서 정산 계좌 등록 상태를 확인합니다.
11. `/merchant/settlements`에서 정산 예정/가능/완료 금액을 확인합니다.
12. `/notifications`에서 신규 결제 예약, 픽업 완료, 정산 알림을 확인합니다.

## 웹 관리자 데모 흐름

1. `admin@breadgo.test`로 로그인합니다.
2. `/admin`에서 전체 요약 카드와 운영 테이블을 확인합니다.
3. 사용자, 가맹점, 매장, 상품, 예약, 결제 목록을 확인합니다.
4. 가맹점 승인 상태 변경을 확인합니다.
5. 예약 테이블에서 수령 방식과 배송 상태를 확인합니다.
6. `/admin/settlements`에서 정산 목록과 수수료 구조를 확인합니다.
7. 정산 상태를 `PAID` 또는 `HOLD`로 변경합니다.
8. `/admin/ops`에서 DB, 결제 Provider, 알림 Channel, 장애 Notifier 상태를 확인합니다.

## Flutter 고객 앱 데모 흐름

로컬 백엔드 연결:

```powershell
cd mobile
flutter run --dart-define=BREADGO_API_BASE_URL=http://10.0.2.2:8000
```

Render 백엔드 연결:

```powershell
cd mobile
flutter run --dart-define=BREADGO_API_BASE_URL=https://breadgo-api.onrender.com
```

데모 흐름:

1. 고객 계정으로 로그인합니다.
2. 상품 탭에서 지역별 상품을 확인합니다.
3. 상품 상세에서 수령 방식을 선택합니다.
4. 예약 생성 후 Mock 결제를 진행합니다.
5. 내 예약 탭에서 예약 상태, 결제 상태, 픽업 코드를 확인합니다.
6. 상태 이력 보기로 예약 생성/결제/취소/환불 이력을 확인합니다.
7. 예약 취소가 가능한 주문을 취소합니다.
8. 알림 탭에서 알림을 확인하고 읽음 처리합니다.

## 확인 포인트

알림:

- 결제 완료 알림
- 예약 취소 알림
- Mock 환불 알림
- 픽업 완료 알림
- 배송 상태 변경 알림

상태 이력:

- 예약 생성
- 결제 완료
- 픽업 완료
- 배송 상태 변경
- 예약 취소
- Mock 환불 처리
- 정산 상태 변경

정산:

- 고객 결제금액
- 플랫폼 수수료
- Mock PG 수수료
- 점주 정산금
- 정산 상태 `PENDING`, `READY`, `PAID`, `HOLD`, `CANCELLED`

## 데모 시 주의사항

- 실제 PG 결제는 연결되어 있지 않습니다.
- 실제 카드 환불은 발생하지 않습니다.
- 실제 퀵배달/택배 API는 연결되어 있지 않습니다.
- 실제 SMS, 이메일, 카카오 알림톡, Push는 연결되어 있지 않습니다.
- Flutter 앱은 고객 앱만 구현되어 있습니다.
- Vercel Blob 이미지 업로드는 Vercel 환경 변수 `BLOB_READ_WRITE_TOKEN`이 필요합니다.
- Render 무료 인스턴스는 sleep 상태일 수 있습니다.
- 데모 계정은 운영 환경에서 사용하면 안 됩니다.
