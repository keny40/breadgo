# Credential Boundary Phase 138

## 목적

Phase 138은 실제 PG, 배송 provider, POS API, 외부 알림 연동을 구현하기 전에 credential boundary를 문서로 정리하는 단계다.

이번 Phase에서는 실제 API key, secret, token, webhook URL을 코드, DB, `.env.example`에 추가하지 않았다. 모든 내용은 향후 연동 후보와 보관 원칙에 대한 설계 문서다.

## 공통 원칙

- 실제 credential은 Git repository에 저장하지 않는다.
- `.env.example`에는 실제 값이나 실제처럼 보이는 dummy secret을 넣지 않는다.
- production secret은 배포 플랫폼 secret manager 또는 운영 환경변수에만 둔다.
- DB에 credential을 저장해야 하는 경우에는 별도 암호화/rotation/audit 설계를 먼저 완료한다.
- 로그, audit log, error message, CSV export, release note에 credential 값을 남기지 않는다.
- webhook URL, token, provider account id는 민감정보로 취급한다.
- 실제 외부 API 호출은 sandbox 검증, rollback 계획, 장애 대응 runbook이 준비된 뒤에만 켠다.

## 환경변수 이름 후보

아래 이름은 후보일 뿐이며, Phase 138에서는 실제 값을 추가하지 않는다.

### Payment

- `PAYMENT_PROVIDER`
- `PAYMENT_PROVIDER_MODE`
- `PAYMENT_TOSS_CLIENT_KEY`
- `PAYMENT_TOSS_SECRET_KEY`
- `PAYMENT_WEBHOOK_SECRET`

### Delivery

- `DELIVERY_PROVIDER`
- `DELIVERY_PROVIDER_MODE`
- `DELIVERY_API_BASE_URL`
- `DELIVERY_API_KEY`
- `DELIVERY_WEBHOOK_SECRET`

### POS

- `POS_PROVIDER`
- `POS_PROVIDER_MODE`
- `POS_API_BASE_URL`
- `POS_CLIENT_ID`
- `POS_CLIENT_SECRET`
- `POS_WEBHOOK_SECRET`

### Notification

- `NOTIFICATION_PROVIDER_MODE`
- `EMAIL_PROVIDER`
- `EMAIL_API_KEY`
- `KAKAO_API_KEY`
- `PUSH_PROVIDER_KEY`
- `SLACK_WEBHOOK_URL`
- `DISCORD_WEBHOOK_URL`

주의:

- 위 값들은 `.env.example`에 실제 값으로 추가하지 않는다.
- 필요하면 placeholder는 `not-used-in-demo` 수준으로만 사용한다.
- v0.1.4 Release Candidate 기준으로는 외부 호출이 비활성화되어야 한다.

## Provider별 credential 경계

### Payment

사용 전 필요한 경계:

- 결제 ready/confirm/cancel/refund 책임 분리
- provider secret 접근 계층 분리
- 결제 실패/환불 audit log 기준
- webhook signature 검증
- sandbox / production key 분리
- 결제 금액 위변조 방지 검증

현재 상태:

- Mock payment만 사용
- 실제 PG 승인/환불 호출 없음
- credential 저장 없음

### Delivery

사용 전 필요한 경계:

- 배송 접수/취소/추적 adapter 분리
- 배송 fee quote와 create 책임 분리
- provider external delivery id 저장 정책
- 배송 webhook 검증
- 주소/연락처 최소 보관 원칙 재검토
- 실패 시 점주 수동 처리 fallback

현재 상태:

- Mock/noop delivery adapter만 사용
- 실제 배송 provider 호출 없음
- 배송 API credential 저장 없음

### POS

사용 전 필요한 경계:

- store별 credential boundary
- external_store_code와 BreadGo store_id mapping
- external_sku 중복 정책
- sync 실패 재시도와 rollback 기준
- CSV fallback 유지 정책
- POS webhook replay 방지
- token rotation과 access scope 제한

현재 상태:

- CSV import와 Mock POS sync만 사용
- 실제 POS API 호출 없음
- POS token / credential / API key 저장 없음

### Notification

사용 전 필요한 경계:

- 수신 동의 및 unsubscribe 정책
- channel별 provider adapter 분리
- retry / rate limit / bounce handling
- Slack/Discord/Webhook URL 보호
- message template에서 개인정보/토큰 노출 방지
- 발송 audit log와 외부 provider message id 저장 기준

현재 상태:

- BreadGo 내부 in-app mock notification만 사용
- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송 없음
- 외부 발송 token 저장 없음

## 실제 연동 전 체크리스트

- [ ] provider별 sandbox 계약/계정 준비
- [ ] secret manager 또는 운영 환경변수 저장 방식 확정
- [ ] local/dev/staging/prod secret 분리
- [ ] credential rotation 절차 정리
- [ ] webhook signature 검증 구현 계획
- [ ] error log / audit log masking 정책 확정
- [ ] DB 저장 필요 여부와 암호화 방식 결정
- [ ] smoke test에서 mock mode와 live mode 분리
- [ ] live mode는 명시적 feature flag 없이는 켜지지 않도록 설계
- [ ] 실제 외부 호출 전 rollback 및 장애 대응 runbook 준비

## v0.1.4 기준 결정

v0.1.4는 실제 운영 연동 Release가 아니다.

- 실제 credential 추가 없음
- 실제 외부 API 호출 없음
- DB schema / migration 변경 없음
- readiness / UX / boundary 개선 Release Candidate

## 남은 과제

- provider별 sandbox adapter 설계
- secret manager 연동 방식 확정
- external webhook verification skeleton
- live mode feature flag 설계
- credential audit policy 문서화

