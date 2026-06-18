# BreadGo Phase 38 알림 채널 구조 준비

## 작업 목적

Phase 38은 기존 인앱 알림센터를 유지하면서, 향후 이메일, SMS, 카카오 알림톡, Push 알림을 외부 채널 adapter로 확장할 수 있는 구조를 준비하는 단계입니다.

## 변경 내용

- Notification Channel adapter 구조 추가
  - `NotificationChannelAdapter`
  - `NotificationPayload`
  - `NotificationChannelResult`
- 인앱 알림 채널 구현
  - `InAppNotificationChannel`
- 외부 알림 skeleton 추가
  - `EmailNotificationChannel`
  - `SmsNotificationChannel`
  - `KakaoAlimtalkNotificationChannel`
  - `PushNotificationChannel`
- 기존 `create_notification` 내부에서 `InAppNotificationChannel`을 사용하도록 정리
- 기존 notifications 테이블/API/프론트 알림센터 유지
- `/notifications` 페이지에 현재는 인앱 알림만 지원한다는 안내 문구 보강
- 알림 채널 설계 문서 추가

## 변경하지 않은 것

- 실제 이메일 발송 없음
- 실제 SMS 발송 없음
- 실제 카카오 알림톡 발송 없음
- 실제 Push 발송 없음
- 외부 API key 요구 없음
- notifications DB schema 변경 없음
- 기존 알림 API 응답 구조 변경 없음
- 기존 예약 → 결제 → 알림 생성 → 읽음 처리 흐름 변경 없음

## DB 변경 여부

없음.

이번 단계는 adapter 구조만 추가하며, 기존 `notifications` 테이블을 그대로 사용합니다.

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

1. 기존 인앱 알림 생성이 계속 동작하는지
2. `/api/v1/notifications/me`가 기존처럼 동작하는지
3. 알림 읽음 처리와 모두 읽음 처리가 유지되는지
4. 외부 채널 skeleton이 실제 API를 호출하지 않는지
5. `/notifications` 페이지 안내 문구가 표시되는지
6. smoke test가 기존처럼 통과하는지

## 한계

- 외부 발송 로그 테이블은 아직 없습니다.
- 재시도 큐는 아직 없습니다.
- 수신 동의 관리는 아직 없습니다.
- 이메일/SMS/알림톡/Push provider API는 아직 연결하지 않았습니다.
- Flutter 앱 push token 관리는 아직 없습니다.

## 다음 단계

- 알림 발송 로그 모델 설계
- 사용자 수신 동의 설정 추가
- 이메일 provider 후보 선정
- SMS/알림톡 provider 후보 선정
- Flutter 앱 도입 후 Push token 관리 설계
- 실제 발송 실패 재시도 큐 설계
