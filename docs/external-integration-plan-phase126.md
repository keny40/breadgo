# External Integration Plan Phase 126

## 목적

`v0.1.2-demo-stabilized` 이후 실제 PG 결제, 배송 provider, POS API, 외부 알림 연동을 바로 구현하지 않고, 향후 v0.1.3 이후 안전하게 붙일 수 있도록 사전 설계를 정리한다.

이번 Phase에서는 기능 코드, DB schema, migration, 실제 외부 API 호출을 변경하지 않는다.

## 현재 상태: Mock / 미연동 목록

현재 BreadGo 데모는 아래 외부 연동을 실제로 호출하지 않는다.

- 결제
  - Mock payment ready / confirm만 사용
  - 실제 PG 승인, 카드 청구, 카드 환불 없음

- 배송
  - 고객 배송 요청 정보와 점주/관리자 수동 배송 상태 변경만 제공
  - 실제 배송 provider API 호출 없음

- POS
  - CSV import, Mock POS sync, provider adapter 구조만 제공
  - 실제 POS API 호출 없음
  - API key / token 저장 없음

- 외부 알림
  - Weekly Report in-app mock notification만 제공
  - 실제 이메일, 카카오, Push, Slack, Discord, Webhook 발송 없음
  - 외부 발송 token / webhook URL 저장 없음

## 결제 연동 후보 구조

### 후보 흐름

1. 고객이 예약 생성
2. 결제 ready API 호출
3. PG provider 결제창 또는 승인 준비 응답 수신
4. 결제 confirm / webhook 검증
5. Payment 상태 업데이트
6. Reservation 상태 확정
7. 실패 / 취소 / 환불 이벤트 기록

### Adapter 구조 후보

- `PaymentProviderAdapter`
  - `provider_name`
  - `create_payment_intent(...)`
  - `confirm_payment(...)`
  - `cancel_payment(...)`
  - `refund_payment(...)`
  - `verify_webhook(...)`

### 우선 고려사항

- 결제 승인과 예약 확정의 원자성
- idempotency key
- webhook signature 검증
- 결제 실패 시 재고 복구 기준
- 환불과 예약 취소의 순서
- 결제 provider별 응답 normalization

## 배송 provider 연동 후보 구조

### 후보 흐름

1. 고객이 퀵/택배 배송 요청
2. 배송 가능 지역 / 운임 조회
3. 예약 결제 확정 후 배송 접수
4. 운송장 또는 배송 job id 저장
5. 배송 상태 webhook 또는 polling 반영
6. 고객/점주/관리자에게 상태 노출

### Adapter 구조 후보

- `DeliveryProviderAdapter`
  - `provider_name`
  - `quote_delivery(...)`
  - `create_delivery(...)`
  - `cancel_delivery(...)`
  - `track_delivery(...)`
  - `normalize_status(...)`

### 우선 고려사항

- 주소 / 연락처 등 개인정보 최소 저장
- 배송 가능 지역 검증
- 배송비 변경 시 고객 결제 금액과의 정합성
- 배송 취소 / 실패 / 반송 상태
- 외부 provider 장애 시 수동 처리 fallback

## POS / CSV / 재고 연동 후보 구조

### 현재 기반

- CSV import
- external_sku 기반 중복 감지
- Product Import Batch / Row 이력
- POS provider adapter
- Mock POS sync
- Inventory Ledger

### 실제 POS 후보 흐름

1. merchant가 POS provider 선택
2. external_store_code와 인증 설정 저장
3. POS item fetch
4. external_sku 기준 상품 매칭
5. update policy 적용
6. 상품 생성/업데이트/스킵 결과 기록
7. Inventory Ledger 이벤트 기록

### Adapter 구조 후보

- 기존 `pos_providers` 구조 확장
  - `validate_connection()`
  - `fetch_items()`
  - `normalize_item()`
  - `map_stock_policy()`

### 우선 고려사항

- API key / token 암호화 저장 또는 외부 secret manager 사용
- provider별 rate limit
- 전체 sync와 증분 sync 구분
- 예약 있는 상품 업데이트 제한
- HIDDEN / ACTIVE 기본 상태 정책
- external_sku 변경 이력

## 외부 알림 연동 후보 구조

### 대상 채널 후보

- Email
- Kakao 알림톡
- Push
- Slack
- Discord
- Webhook

### 후보 흐름

1. 내부 notification event 생성
2. 채널별 발송 eligibility 확인
3. provider adapter로 발송 요청
4. delivery log 기록
5. 실패 / 재시도 / webhook 결과 반영

### Adapter 구조 후보

- `NotificationProviderAdapter`
  - `provider_name`
  - `validate_connection()`
  - `send_message(...)`
  - `normalize_delivery_result(...)`
  - `verify_webhook(...)`

### 우선 고려사항

- 수신 동의 / opt-out
- 발송 retry 정책
- 중복 발송 방지
- provider별 template id 관리
- 민감정보 미노출
- 외부 발송 실패 webhook 처리

## 필요한 환경변수 후보

실제 값은 `.env`나 문서에 저장하지 않는다. 아래는 후보 이름이며 현재 demo에서는 사용하지 않는다.

```text
# 현재 demo에서는 사용하지 않음. 실제 연동 전 secret manager 또는 안전한 배포 환경 변수로만 설정한다.
PAYMENT_PROVIDER=
PAYMENT_API_BASE_URL=
PAYMENT_CLIENT_ID=
PAYMENT_CLIENT_SECRET=
PAYMENT_WEBHOOK_SECRET=

DELIVERY_PROVIDER=
DELIVERY_API_BASE_URL=
DELIVERY_CLIENT_ID=
DELIVERY_CLIENT_SECRET=
DELIVERY_WEBHOOK_SECRET=

POS_PROVIDER=
POS_API_BASE_URL=
POS_CLIENT_ID=
POS_CLIENT_SECRET=

EMAIL_PROVIDER=
EMAIL_API_KEY=
KAKAO_PROVIDER=
KAKAO_API_KEY=
PUSH_PROVIDER=
PUSH_SERVER_KEY=
SLACK_WEBHOOK_URL=
DISCORD_WEBHOOK_URL=
```

주의:

- 실제 API key, secret, token, webhook URL은 repository에 commit하지 않는다.
- 운영 환경에서는 secret manager 또는 배포 플랫폼 secret 기능을 사용한다.
- webhook secret은 provider signature 검증 외 용도로 노출하지 않는다.

## 필요한 DB 변경 후보

실제 구현 전 아래 변경이 필요할 수 있다.

- 결제
  - provider_payment_id
  - idempotency_key
  - payment_attempts
  - payment_webhook_events
  - refund_events

- 배송
  - delivery_provider
  - external_delivery_id
  - tracking_number
  - delivery_quote_amount
  - delivery_webhook_events

- POS
  - encrypted credential reference
  - provider account id
  - sync cursor / last external updated at
  - external_sku history

- 알림
  - notification_channel_preferences
  - external_delivery_id
  - delivery_attempts
  - webhook delivery events

- 감사 / 운영
  - provider action audit logs
  - failure reason code
  - retry_count
  - last_retry_at

## 필요한 보안 / 감사 로그 후보

- 외부 API credential은 평문 DB 저장 금지
- token rotation 기준 필요
- webhook signature 검증 필수
- provider request / response에 개인정보 마스킹 적용
- audit log에는 count, provider, status, external id 정도만 저장
- 이메일, 전화번호, 주소, token, webhook secret은 audit log에 저장하지 않음
- 관리자 수동 재시도와 scheduler 자동 실행을 구분
- 실패 재시도 횟수와 최종 실패 사유 기록

## 실제 연동 전 체크리스트

- provider별 sandbox 계정 준비
- API 계약서 / rate limit / timeout 확인
- webhook signature 검증 방식 확인
- 개인정보 저장 범위와 보존 기간 확인
- idempotency 정책 확정
- 장애 / timeout / 부분 실패 처리 기준 확정
- 관리자 retry / 운영 모니터링 화면 설계
- seed / smoke test에서 실제 외부 호출을 하지 않는 mock mode 유지
- local / staging / production 환경변수 분리
- rollback 절차 정리

## v0.1.3에서 할 수 있는 최소 범위

추천 MVP 범위:

1. Payment provider adapter skeleton
   - 실제 PG 호출 없이 interface, mock provider, 상태 전이 기준만 정리

2. Delivery provider adapter skeleton
   - 실제 배송 접수 없이 quote/create/cancel interface와 상태 mapping만 정의

3. POS provider credential boundary 설계
   - token 저장 방식은 구현하지 않고, secret manager 사용 원칙과 schema 후보만 문서화

4. Notification provider adapter skeleton
   - 외부 발송 없이 channel preference / delivery log 설계와 mock provider 유지

5. External integration smoke mode
   - 외부 호출 없이 adapter mock response를 검증하는 read-only 또는 local-only smoke 추가

## v0.1.3에서 하지 말아야 할 범위

- 실제 PG 승인 / 실결제
- 실제 카드 환불
- 실제 배송 접수
- 실제 POS API token 저장
- 실제 POS 상품 전체 동기화
- 실제 이메일 / 카카오 / Push 발송
- Slack / Discord / Webhook 실발송
- 민감정보가 포함된 provider payload 저장
- 대량 merchant 비동기 큐
- 자동 재시도 scheduler
- 운영자 세부 권한 분리

## 현재 Mock에서 실제 연동으로 전환하는 기준

실제 연동 전환은 아래 조건을 만족한 뒤 별도 Release로 분리한다.

- sandbox에서 provider별 happy path / failure path 검증 완료
- 개인정보 / token 저장 정책 승인
- webhook signature 검증 완료
- audit log 민감정보 미저장 검증 완료
- 장애 시 수동 fallback 절차 문서화
- smoke test가 외부 호출 없이 안정적으로 유지됨
- 실제 호출 테스트는 staging에서만 수행

## 검증 결과

- `git status`: 변경 파일 확인
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## 변경 여부

- 기능 코드 변경: 없음
- DB schema 변경: 없음
- migration 추가: 없음
- 실제 PG API 호출: 없음
- 실제 배송 API 호출: 없음
- 실제 POS API 호출: 없음
- 실제 외부 알림 API 호출: 없음
- API key / secret / token / webhook URL 추가: 없음
- 새 tag / 새 Release 생성: 없음
- 기존 tag 삭제/이동: 없음

## Suggested commit message

`Document external integration plan`
