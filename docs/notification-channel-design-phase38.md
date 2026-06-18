# BreadGo Phase 38 알림 채널 설계

## 목적

Phase 38은 기존 인앱 알림센터를 유지하면서, 향후 이메일, SMS, 카카오 알림톡, Push 알림을 분리된 채널 adapter로 확장할 수 있게 준비하는 단계입니다.

이번 단계에서는 실제 외부 발송 API를 호출하지 않습니다.

## 현재 인앱 알림 흐름

1. 예약, 결제, 픽업, 배송, 취소, 환불, 정산 이벤트가 발생합니다.
2. 백엔드 서비스가 `create_notification`을 호출합니다.
3. `InAppNotificationChannel`이 `notifications` 테이블에 알림을 저장합니다.
4. 사용자는 `/notifications`에서 알림을 확인합니다.
5. 사용자는 알림을 읽음 처리하거나 모두 읽음 처리할 수 있습니다.
6. NavBar에는 미읽음 알림 개수가 표시됩니다.

## 추가된 Channel Adapter 구조

위치:

```text
backend/app/services/notifications/
```

구성:

```text
base.py
in_app.py
email.py
sms.py
kakao_alimtalk.py
push.py
```

역할:

- `NotificationChannelAdapter`: 알림 채널 공통 인터페이스
- `NotificationPayload`: 채널에 전달할 공통 payload
- `NotificationChannelResult`: 발송 결과 표현
- `InAppNotificationChannel`: 현재 운영 중인 인앱 알림 저장
- `EmailNotificationChannel`: 이메일 발송 skeleton
- `SmsNotificationChannel`: SMS 발송 skeleton
- `KakaoAlimtalkNotificationChannel`: 카카오 알림톡 발송 skeleton
- `PushNotificationChannel`: 모바일 push 발송 skeleton

외부 채널 skeleton은 실제 발송을 하지 않고 `skipped=True` 결과를 반환합니다.

## 채널별 사용 목적

### IN_APP

- 기본 알림 채널
- 모든 이벤트의 운영 기록성 알림
- 현재 MVP에서 실제 사용 중

### EMAIL

- 회원 가입, 비밀번호 재설정
- 예약/결제 영수증
- 정산 리포트
- 운영 공지

### SMS

- 긴급성 높은 픽업/배송 알림
- 전화번호 기반 고객 알림
- 단문 상태 변경 안내

### KAKAO_ALIMTALK

- 국내 서비스에서 고객 도달률이 중요한 거래 알림
- 예약 확정
- 픽업 코드 안내
- 배송 상태 변경
- 결제/환불 안내

### PUSH

- Flutter 앱 도입 이후 실시간 앱 알림
- 근처 마감 할인 상품 추천
- 픽업 마감 임박 알림
- 가맹점 신규 주문 알림

## 이벤트별 추천 채널

| 이벤트 | 고객 | 가맹점 | 관리자 |
| --- | --- | --- | --- |
| 예약 생성 | IN_APP | IN_APP | - |
| 결제 완료 | IN_APP, KAKAO_ALIMTALK, EMAIL | IN_APP, PUSH | - |
| 픽업 완료 | IN_APP, KAKAO_ALIMTALK | IN_APP | - |
| 배송 상태 변경 | IN_APP, KAKAO_ALIMTALK, SMS | IN_APP | - |
| 예약 취소 | IN_APP, KAKAO_ALIMTALK | IN_APP, PUSH | IN_APP |
| Mock/실제 환불 | IN_APP, EMAIL, KAKAO_ALIMTALK | IN_APP | IN_APP |
| 정산 가능 | - | IN_APP, EMAIL | IN_APP |
| 정산 완료/보류 | - | IN_APP, EMAIL | IN_APP |

## 필요한 환경 변수 예시

향후 운영 전환 시 필요한 값:

```text
EMAIL_PROVIDER=
EMAIL_API_KEY=
EMAIL_FROM_ADDRESS=

SMS_PROVIDER=
SMS_API_KEY=
SMS_SENDER_NUMBER=

KAKAO_ALIMTALK_PROVIDER=
KAKAO_ALIMTALK_API_KEY=
KAKAO_ALIMTALK_SENDER_KEY=
KAKAO_ALIMTALK_TEMPLATE_RESERVATION_CONFIRMED=
KAKAO_ALIMTALK_TEMPLATE_PICKUP_CODE=
KAKAO_ALIMTALK_TEMPLATE_REFUND=

PUSH_PROVIDER=
PUSH_SERVER_KEY=
PUSH_APNS_KEY=
PUSH_FCM_PROJECT_ID=
```

실제 값은 `.env.example`에는 placeholder만 넣고, Render/Vercel/비밀 저장소에만 저장해야 합니다.

## 보안 및 개인정보 주의사항

- 전화번호, 이메일, 배송 주소는 개인정보입니다.
- 발송 로그에 민감 정보를 과도하게 남기지 않습니다.
- API key, sender key, webhook secret은 로그에 출력하지 않습니다.
- 카카오 알림톡 템플릿은 승인된 문구만 사용해야 합니다.
- 수신 동의 여부와 야간 발송 제한을 고려해야 합니다.
- 마케팅성 알림과 거래성 알림을 분리해야 합니다.
- 운영자 화면에서 개인정보 노출 범위를 제한해야 합니다.

## 실패 재시도 및 발송 로그 방향

운영 전환 시 별도 발송 로그 테이블이 필요합니다.

추천 필드:

```text
id
notification_id
channel
provider
recipient
status
attempt_count
last_error
sent_at
failed_at
created_at
updated_at
```

재시도 정책:

- 일시 실패는 제한 횟수 내 재시도
- 영구 실패는 재시도하지 않음
- 외부 provider 장애는 관리자 알림 생성
- 중복 발송 방지를 위한 idempotency key 사용

## 수신 동의 관리 방향

향후 사용자 설정에 다음 항목이 필요합니다.

- 이메일 수신 동의
- SMS 수신 동의
- 카카오 알림톡 수신 가능 여부
- Push 알림 토큰
- 마케팅 알림 동의
- 거래 알림은 법적/정책 기준에 따라 별도 처리

## 이번 Phase에서 실제 외부 API를 붙이지 않은 이유

- 실제 발송 API는 비용, 개인정보, 발송 정책, 실패 재시도 설계가 필요합니다.
- SMS/알림톡은 템플릿 승인과 발신자 등록이 필요합니다.
- Push는 모바일 앱과 device token 관리가 필요합니다.
- 현재 MVP는 인앱 알림으로 상태 변화를 확인하는 것이 충분합니다.
- 먼저 채널 구조를 분리해 이후 실제 provider를 안전하게 붙일 수 있도록 준비했습니다.
