# BreadGo Phase 39 운영 모니터링/로깅 설계

## 목적

Phase 39는 실제 Sentry, Slack, 외부 모니터링 서비스를 바로 붙이지 않고, 운영 전환을 위한 기본 로깅 구조, 운영 상태 확인 API, 관리자 운영 점검 UI, 장애 알림 adapter skeleton을 준비하는 단계입니다.

## 현재 운영 상태 확인 구조

추가된 API:

```text
GET /api/v1/ops/status
```

접근 권한:

```text
ADMIN only
```

응답에 포함되는 정보:

- 앱 이름
- API 버전
- 안전한 환경 구분
- 앱 상태
- DB 연결 상태
- 결제 provider 상태
- 알림 channel 상태
- 장애 알림 notifier 상태

민감한 환경 변수 값은 응답에 포함하지 않습니다.

## 관리자 운영 점검 UI

추가 화면:

```text
/admin/ops
```

표시 항목:

- 앱 상태
- 실행 환경
- DB 상태
- 결제 Provider 상태
- 알림 Channel 상태
- 장애 알림 Notifier 상태

현재 실제 Sentry/Slack/외부 모니터링 호출은 하지 않고, skeleton 구성 상태만 보여줍니다.

## 로깅 원칙

- Python `logging` 기반 공통 logger를 사용합니다.
- `breadgo.*` logger namespace를 사용합니다.
- 운영 이벤트와 실패 상황 중심으로 기록합니다.
- 요청/응답 전체 body를 남기지 않습니다.
- access log는 과도한 노이즈를 줄이기 위해 낮은 우선순위로 둡니다.
- unhandled exception은 공통 handler에서 기록합니다.

## 민감정보 로그 금지 원칙

로그에 남기면 안 되는 정보:

- JWT access token
- 비밀번호
- 비밀번호 hash
- 결제 카드 정보
- PG secret key
- 사용자 계좌번호 전체
- 배송 주소 전체를 포함한 과도한 개인정보
- 외부 API key
- webhook secret

현재 추가된 로그는 내부 ID와 상태값 위주로 남기며, 토큰/비밀번호/계좌번호/결제 민감정보를 기록하지 않습니다.

## 장애 알림 Adapter 구조

추가된 위치:

```text
backend/app/services/ops/
```

구성:

```text
incident_notifiers.py
```

포함 클래스:

- `IncidentNotifierAdapter`
- `IncidentNotifierResult`
- `LogIncidentNotifier`
- `SlackIncidentNotifier`
- `SentryIncidentNotifier`

현재 동작:

- `LogIncidentNotifier`: 애플리케이션 로그에 기록
- `SlackIncidentNotifier`: 실제 전송 없이 skeleton 상태
- `SentryIncidentNotifier`: 실제 전송 없이 skeleton 상태

## 향후 Sentry/Slack 연동 방향

### Sentry

목적:

- unhandled exception 수집
- 배포 버전별 오류 추적
- 성능 병목 확인

필요 작업:

- Sentry DSN 환경 변수 추가
- FastAPI integration 설정
- 개인정보 scrubber 설정
- release/version tagging
- alert rule 구성

### Slack

목적:

- 운영 장애를 팀 채널로 알림
- 결제/정산/DB 오류 등 즉시 대응 필요 이벤트 전달

필요 작업:

- Slack webhook URL 환경 변수 추가
- severity 기준 정의
- 중복 알림 방지
- rate limit 대응
- 장애 복구 알림 정책 정의

## 장애 알림 흐름

운영 전환 시 예상 흐름:

1. 서비스에서 오류 또는 중요 운영 이벤트 발생
2. 내부 logger에 안전한 내용 기록
3. incident notifier 호출
4. Log notifier는 항상 로그 기록
5. Slack/Sentry notifier는 설정된 경우 외부 전송
6. 관리자 화면에서 운영 상태 확인
7. 필요 시 운영자가 수동 대응

## 운영 배포 시 필요한 환경 변수 예시

```text
ENVIRONMENT=production
LOG_LEVEL=INFO

SENTRY_DSN=
SENTRY_ENVIRONMENT=production
SENTRY_RELEASE=

SLACK_WEBHOOK_URL=
SLACK_ALERT_CHANNEL=
```

주의:

- 실제 secret 값은 문서나 Git에 저장하지 않습니다.
- Render/Vercel/비밀 저장소에만 설정합니다.
- 로그에 secret 값을 출력하지 않습니다.

## 이번 Phase에서 실제 외부 연동을 하지 않은 이유

- 실제 Sentry/Slack 연동은 secret 관리와 개인정보 scrubber 정책이 필요합니다.
- 알림 피로도를 줄이기 위한 severity/rate limit 정책이 필요합니다.
- MVP에서는 운영 상태 구조와 관리자 확인 화면을 먼저 준비하는 것이 안전합니다.
- 기존 예약/결제/정산/알림 흐름을 깨지 않는 것이 우선입니다.
