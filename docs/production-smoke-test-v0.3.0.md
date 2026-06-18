# BreadGo v0.3.0 운영 URL Smoke Test

## 목적

이 문서는 운영 배포 URL에서 사람이 직접 따라 할 수 있는 BreadGo v0.3.0 데모 smoke test 체크리스트입니다.
자동 테스트 코드를 새로 만들지 않고, 브라우저와 Swagger/웹 UI 기준으로 핵심 흐름을 확인합니다.

## 사전 준비

Render free instance가 sleep 상태일 수 있으므로 먼저 다음 URL을 엽니다.

[https://breadgo-api.onrender.com/health](https://breadgo-api.onrender.com/health)

데모 계정:

```text
customer@breadgo.test / 12345678
merchant@breadgo.test / 12345678
admin@breadgo.test / 12345678
```

## 1. Backend Health 확인

URL:

[https://breadgo-api.onrender.com/health](https://breadgo-api.onrender.com/health)

기대 결과:

```json
{"status":"ok"}
```

## 2. Swagger 확인

URL:

[https://breadgo-api.onrender.com/docs](https://breadgo-api.onrender.com/docs)

확인 항목:

- Swagger UI가 열린다.
- `auth`, `regions`, `reservations`, `payments`, `notifications`, `admin`, `ops` API가 보인다.

## 3. 고객 로그인

URL:

[https://breadgo.vercel.app/login](https://breadgo.vercel.app/login)

계정:

```text
customer@breadgo.test / 12345678
```

기대 결과:

- 로그인 성공
- `/products`로 이동
- NavBar에 고객 이메일 표시

## 4. 상품 목록 확인

URL:

[https://breadgo.vercel.app/products](https://breadgo.vercel.app/products)

확인 항목:

- 지역 선택 버튼 동작
- 상품 카드 표시
- 상품 이미지 또는 placeholder 표시
- 수량, 가격, 할인 가격 표시

## 5. 예약 생성

확인 흐름:

1. 상품 선택
2. 수령 방식 선택
3. 수량 선택
4. 예약 생성

기대 결과:

- 예약 생성 성공 메시지 표시
- 결제를 완료하면 수령 정보가 확정된다는 안내 표시

## 6. Mock 결제

확인 흐름:

1. Mock 결제 수단 선택
2. 결제 진행

기대 결과:

- 결제 완료 메시지 표시
- PICKUP이면 픽업 코드 표시
- 배송 방식이면 배송 요청 정보 표시

## 7. 내 예약 확인

URL:

[https://breadgo.vercel.app/my-reservations](https://breadgo.vercel.app/my-reservations)

확인 항목:

- 예약 카드 표시
- 예약 상태 표시
- 결제 상태 표시
- 수령 방식 표시
- 픽업 코드 또는 배송 요청 정보 표시
- 상태 이력 버튼 동작
- 취소 가능한 예약은 예약 취소 가능

## 8. 알림 확인

URL:

[https://breadgo.vercel.app/notifications](https://breadgo.vercel.app/notifications)

확인 항목:

- 결제 완료 알림 표시
- 예약 취소 시 취소/Mock 환불 알림 표시
- 개별 읽음 처리 가능
- 모두 읽음 처리 가능

## 9. 가맹점 주문 확인

로그아웃 후 가맹점 계정으로 로그인:

```text
merchant@breadgo.test / 12345678
```

URL:

[https://breadgo.vercel.app/merchant/orders](https://breadgo.vercel.app/merchant/orders)

확인 항목:

- 고객이 생성한 주문 표시
- PICKUP 주문은 픽업 코드 확인 가능
- 배송 주문은 배송 상태 확인 가능
- 취소된 주문은 취소 상태로 표시

## 10. 픽업 확인

URL:

[https://breadgo.vercel.app/merchant/pickup](https://breadgo.vercel.app/merchant/pickup)

확인 항목:

- 픽업 코드 조회 가능
- 예약 상세 표시
- 결제 상태 표시
- 픽업 확정 가능
- 이미 취소/픽업 완료된 예약은 적절히 차단

## 11. 관리자 /admin/ops 확인

로그아웃 후 관리자 계정으로 로그인:

```text
admin@breadgo.test / 12345678
```

URL:

[https://breadgo.vercel.app/admin/ops](https://breadgo.vercel.app/admin/ops)

확인 항목:

- 운영 상태 카드 표시
- DB 상태 `OK` 또는 정상 메시지 표시
- 결제 Provider 상태 표시
- 알림 Channel 상태 표시
- 장애 Notifier skeleton 상태 표시

## 12. 정산 확인

URL:

[https://breadgo.vercel.app/admin/settlements](https://breadgo.vercel.app/admin/settlements)

확인 항목:

- 결제 완료 또는 픽업 완료된 예약의 정산 데이터 표시
- 총 결제금액, 플랫폼 수수료, PG 수수료, 점주 정산금 표시
- 정산 상태 변경 가능

## 13. 상태 이력 확인

확인 위치:

- 고객: `/my-reservations`
- 가맹점: `/merchant/orders`
- 관리자: `/admin`

확인 항목:

- 예약 생성
- 결제 완료
- 픽업 완료
- 배송 상태 변경
- 예약 취소
- Mock 환불 처리

## 실패 시 1차 확인

1. [https://breadgo-api.onrender.com/health](https://breadgo-api.onrender.com/health) 확인
2. Render cold start 대기 후 재시도
3. 브라우저 Network 탭에서 API base URL 확인
4. CORS 오류 여부 확인
5. 데모 데이터 seed 여부 확인
6. 로그인 계정 role 확인
7. `/admin/ops`에서 DB/API 상태 확인

## 완료 기준

- 고객 예약/Mock 결제 흐름이 완료된다.
- 내 예약에서 상태와 픽업 코드 또는 배송 정보가 보인다.
- 알림이 생성되고 읽음 처리된다.
- 가맹점 주문 화면에서 주문이 보인다.
- 관리자 운영/정산 화면이 열린다.
