# Phase 66 Release Check

## 작업 목적

BreadGo Pro를 실제 POS API 연동 전 단계로 확장하기 위해 POS 연동 설정과 Mock POS 동기화 MVP를 추가했다.

## 변경 내용

- 가맹점 POS 연동 설정 테이블 추가
- Mock POS 동기화 이력 테이블 추가
- 가맹점 API 추가
  - `GET /api/v1/merchant/pro/pos-integration`
  - `POST /api/v1/merchant/pro/pos-integration`
  - `POST /api/v1/merchant/pro/pos-integration/mock-sync`
  - `GET /api/v1/merchant/pro/pos-integration/sync-batches`
  - `GET /api/v1/merchant/pro/pos-integration/sync-batches/{batch_id}`
- `/merchant/pro/pos` 화면 추가
- NavBar, Pro 대시보드, Pro 플랜 화면에 POS/API 연동 준비 흐름 연결

## DB 변경 여부

변경 있음.

- `pos_integrations`
- `pos_sync_batches`
- `pos_sync_rows`

실제 POS API key/token 같은 민감정보는 저장하지 않는다.

## POS 동기화 기준

- `external_sku` 기준으로 기존 상품을 찾는다.
- 기존 상품이 없으면 `HIDDEN` 상태 상품을 새로 생성한다.
- 기존 상품이 있고 예약이 없으면 가격, 재고, 판매 시간, 수령 방식 등을 업데이트한다.
- 기존 상품에 예약이 있으면 안전하게 `SKIPPED` 처리한다.
- 실제 외부 POS API 호출은 하지 않는다.

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- `cd backend && python scripts/smoke_test.py`: PASS
- POS 설정 저장 직접 호출: PASS
- Mock POS sync 신규 생성 직접 호출: PASS
- Mock POS sync `external_sku` 중복 업데이트 직접 호출: PASS
- POS sync 이력 목록/상세 직접 호출: PASS
- 예약 있는 상품 `SKIPPED` 직접 검증: NOT TESTED, 로직 구현 후 수동 검증 필요
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- 실제 POS API 호출은 아직 없다.
- 대용량 동기화, 비동기 큐, 재시도 정책은 아직 없다.
- POS 인증 토큰 저장/암호화 구조는 다음 단계에서 별도 설계가 필요하다.

## 다음 단계

- 실제 POS provider adapter 구조 추가
- POS 동기화 스케줄링 또는 수동 재시도 기능
- 예약 있는 상품 업데이트 정책 세분화
