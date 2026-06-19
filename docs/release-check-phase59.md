# BreadGo Phase 59 릴리즈 체크

## 작업 목적

Phase 59는 Phase 58에서 수집하기 시작한 고객 상품 행동 데이터를 BreadGo Pro 추천 엔진에 반영하는 단계입니다.
단순 판매율 기반 추천에서 벗어나, 고객이 많이 봤지만 예약하지 않은 상품과 조회 대비 예약 전환이 높은 상품을 추천 재고/할인가 판단에 활용합니다.

## 변경 내용

- `GET /api/v1/merchant/pro/recommendations` 추천 계산에 최근 7일 `product_events` 데이터 반영
- 추천 응답 스키마 확장
  - `detail_views`
  - `reservation_started_count`
  - `reservation_count`
  - `view_to_reservation_rate`
  - `started_to_created_rate`
  - `funnel_signal_label`
  - `funnel_message`
- 추천 rule 확장
  - 조회는 많지만 예약 전환이 낮으면 `LOWER_PRICE` 또는 `DECREASE_STOCK` 후보
  - 조회 대비 예약 전환이 높고 판매율도 높으면 `INCREASE_STOCK` 후보
  - 조회 데이터가 적으면 `INSUFFICIENT_DATA`와 낮은 신뢰도 메시지 유지
  - 예약 시작은 많지만 예약 생성이 낮으면 가격/배송비/수령 조건 점검 메시지 표시
- `/merchant/pro/recommendations` 화면 개선
  - 상품 조회 수
  - 예약 시작 수
  - 예약 생성 수
  - 조회→예약 전환율
  - 시작→생성 전환율
  - 고객 반응 신호 배지
  - 고객 행동 기반 추천 메시지 표시
- 추천 화면에서 `고객 전환 보기` 링크 보강

## DB 변경 여부

없음.

기존 Phase 58의 `product_events` 테이블을 활용했습니다.

## 추천 계산 기준

- 기간: 최근 7일
- `detail_views` = `product_events.event_type = DETAIL_VIEW`
- `reservation_started_count` = `product_events.event_type = RESERVATION_STARTED`
- `reservation_count` = 최근 7일 예약 생성 수
- `view_to_reservation_rate` = 예약 생성 수 / 상품 상세 조회 수
- `started_to_created_rate` = 예약 생성 수 / 예약 시작 수
- `funnel_signal_label`
  - `INSUFFICIENT_DATA`: 고객 반응 데이터 부족
  - `HIGH_INTEREST_LOW_CONVERSION`: 조회나 예약 시작은 있으나 예약 생성 전환이 낮음
  - `HIGH_CONVERSION`: 조회 대비 예약 전환과 판매율이 높음
  - `LOW_INTEREST`: 고객 관심 데이터가 낮은 후보
- 전환율은 기존 예약 데이터가 먼저 쌓인 경우를 고려해 최대 100%로 보정합니다.

## 검증 결과

아래 명령으로 검증했습니다.

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/smoke_test.py

cd frontend
npm run lint
npm run build
```

- PASS: `python -m compileall app scripts`
- PASS: `python -m alembic upgrade head`
- PASS: `npm run lint`
- PASS: `npm run build`
- PASS: 임시 uvicorn 실행 후 `python scripts/smoke_test.py`
- PASS: 추천 초안 상품에 `DETAIL_VIEW` 4건 기록 후 추천 API 반영 확인
- PASS: 추천 초안 상품에 `RESERVATION_STARTED` 3건 기록 후 추천 API 반영 확인
- PASS: 예약 전환이 낮은 상품에 `HIGH_INTEREST_LOW_CONVERSION` 신호와 `LOWER_PRICE` 추천 반영 확인

직접 검증 과정에서 로컬 DB에 추천 기반 `HIDDEN` 상품 초안과 고객 행동 이벤트가 생성되었습니다.

## 한계

- 실제 AI 모델은 아직 사용하지 않습니다.
- 이벤트 수집 초기에는 기존 예약 데이터와 신규 이벤트 데이터의 수집 시작 시점이 달라 전환율 해석에 주의가 필요합니다.
- 상품 목록 노출 `LIST_VIEW`는 아직 추천 계산에 반영하지 않습니다.
- 고객 클릭/체류 시간/장바구니 같은 더 세밀한 행동 데이터는 아직 없습니다.
- 추천 rule은 MVP용이며, 향후 실제 데이터로 조정이 필요합니다.

## 다음 단계

- 상품 목록 노출과 상세 진입을 분리해 더 정교한 퍼널 구성
- 고객 행동 기반 추천 rule 튜닝
- 추천 신호별 실제 채택률/판매율 비교
- 가격, 배송비, 수령 방식별 전환율 분석
- 실제 AI 추천 모델 학습 데이터셋 설계
