# Adapter Readiness UI Phase 135

## 목적

Phase 135는 v0.1.3에서 추가한 External Integration Readiness 관리자 카드를 상세화하여, 운영자가 Payment / Delivery / Notification / POS adapter 상태를 한눈에 이해할 수 있게 개선하는 단계다.

이번 Phase에서는 기존 read-only API 응답 구조를 유지하고, 관리자 화면 UX와 안내 문구 중심으로 개선했다.

## 변경 내용

- Admin Dashboard의 External Integration Readiness 카드 상세화
- `overall_status`를 한국어 상태 문구로 표시
- readiness item 수, dry-run 수, external calls ON/OFF 요약 카드 추가
- Payment / Delivery / Notification / POS area별 상세 카드 추가
- provider별 status, mode, message 표시
- provider별 `external_calls_enabled=false` 표시 강화
- area별 dry-run 결과 표시 개선
- `MOCK_READY`, `NOT_ENABLED`, `NOT_CONFIGURED` 상태 해석 안내 추가
- 실제 외부 연동 완료 상태가 아니라 adapter 준비 상태임을 명확히 표시
- 실제 연동 전 필요한 항목 안내 추가

## 화면 변경 사항

대상 화면:

- `/admin`

추가/개선 문구:

- `실제 연동 전 adapter 준비 상태`
- `이 카드는 운영 연동 완료 상태가 아니라 실제 provider 연결 전 점검 화면입니다.`
- `external_calls_enabled=false가 정상입니다.`
- `MOCK_READY`: mock/noop adapter와 dry-run이 모두 외부 호출 없이 통과
- `NOT_ENABLED`: 실제 provider skeleton은 있으나 운영 연동은 비활성
- `NOT_CONFIGURED`: 실제 provider credential 또는 store 설정이 아직 없음

## 표시 기준

### Overall

- `MOCK_READY`: 모든 adapter readiness와 dry-run이 외부 호출 없이 통과
- `CHECK_FAILED`: 외부 호출 감지 또는 readiness 실패가 있을 때 점검 필요

### Provider별 readiness

- `READY`: mock provider가 내부 dry-run으로 동작
- `NOT_ENABLED`: 실제 provider skeleton은 있으나 운영 연동은 켜지지 않음
- `NOT_CONFIGURED`: 실제 provider 설정과 credential boundary가 아직 없음

### Dry-run

- Payment: mock ready / confirm 결과
- Delivery: mock quote / create 결과
- Notification: in-app mock send 결과
- POS: mock POS item normalization 결과

## 실제 외부 API 미호출 원칙

화면에서도 아래 원칙을 명확히 표시한다.

- 실제 PG API 호출 없음
- 실제 배송 provider API 호출 없음
- 실제 POS API 호출 없음
- 실제 이메일 / 카카오 / Push / Slack / Discord / Webhook 호출 없음
- API key / secret / token / webhook URL 추가 없음
- `external_calls_enabled=false`가 데모 정상 상태

## 실제 연동 전 필요한 항목

- credential 저장 경계
- provider별 실패/재시도 정책
- audit log 기준
- webhook 검증 기준
- 운영 secret 관리 기준
- 실제 provider별 sandbox 검증 계획

## DB / Migration 변경 여부

- DB schema 변경: 없음
- migration 추가: 없음
- credential 저장 구조 추가: 없음

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## 남은 한계

- 별도 `/admin/pro/operations/external-integrations` 상세 전용 화면은 아직 없다.
- readiness UI는 read-only이며 실제 provider 연결/credential 설정 기능은 없다.
- 실제 외부 연동은 v0.1.4 이후 별도 Phase에서 sandbox 기준으로 설계해야 한다.

## Suggested commit message

`Detail adapter readiness admin UI`

