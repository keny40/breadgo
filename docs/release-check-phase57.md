# BreadGo Phase 57 릴리즈 체크

## 작업 목적

Phase 57은 BreadGo Pro 추천으로 생성된 `HIDDEN` 초안 상품이 실제 고객 노출 상품으로 전환되었는지 추적하는 단계입니다.
추천 → 초안 생성 → 상품 노출 → 예약 → 결제 → 픽업까지 이어지는 추천 퍼널을 점주가 확인할 수 있게 하는 것이 목표입니다.

## 변경 내용

- `recommendation_usages` 테이블에 추천 퍼널 필드 추가
  - `draft_product_status`
  - `published_at`
  - `first_reserved_at`
  - `first_paid_at`
  - `first_picked_up_at`
- 추천 초안 생성 시 초기 상태 저장
  - 숨김 초안: `HIDDEN_DRAFT`
  - 바로 노출 생성: `PUBLISHED`
- 상품 수정/숨김 흐름에 추천 초안 상태 동기화 연결
  - 추천 생성 상품이 `ACTIVE`가 되면 `PUBLISHED`
  - 다시 숨김 처리되면 `ARCHIVED`
- 추천 성과 API에 퍼널 지표 추가
  - `draft_created_count`
  - `published_from_recommendation_count`
  - `publish_conversion_rate`
  - `reserved_after_publish_count`
  - `paid_after_publish_count`
  - `picked_up_after_publish_count`
  - `average_time_to_publish_minutes`
  - `recent_funnel_usages`
- `/merchant/pro/recommendation-performance` 화면에 추천 퍼널 카드와 최근 이력 상태 표시 추가
- `/merchant/pro/recommendations` 초안 생성 성공 안내 문구 보강
- `/merchant/pro` 대시보드 CTA를 추천 퍼널 확인 문구로 보강

## DB 변경 여부

있음.

Alembic migration `202606180010_add_recommendation_funnel_fields.py`를 추가해 기존 `recommendation_usages` 테이블에 nullable 컬럼을 추가했습니다.
기존 추천 사용 이력은 응답 계산 시 현재 상품 상태와 예약/결제/픽업 데이터를 기준으로 가능한 범위에서 fallback 처리됩니다.

## 추천 퍼널 계산 기준

- 초안 생성 수 = `DRAFT_CREATED` 추천 사용 이력 수
- 실제 노출 전환 수 = `published_at`이 있거나, 추천 생성 상품이 현재 `ACTIVE`이거나, `draft_product_status = PUBLISHED`인 이력 수
- 노출 전환율 = 실제 노출 전환 수 / 초안 생성 수
- 노출 후 예약 수 = 추천 생성 상품에 예약이 1건 이상 발생한 이력 수
- 노출 후 결제 수 = 추천 생성 상품에 `PAID` 결제가 1건 이상 발생한 이력 수
- 노출 후 픽업 수 = 추천 생성 상품에 `PICKED_UP` 예약이 1건 이상 발생한 이력 수
- 평균 노출 소요 시간 = `published_at - recommendation_usage.created_at` 평균 분 단위

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
- PASS: 추천 초안 생성 직접 검증
  - 생성 상품 상태 `HIDDEN` 확인
- PASS: 생성 상품 `ACTIVE` 전환 직접 검증
  - 추천 사용 이력 `draft_product_status = PUBLISHED` 확인
  - `published_at` 기록 확인
  - 추천 성과 API의 `published_from_recommendation_count`, `publish_conversion_rate` 반영 확인

직접 검증 과정에서 로컬 DB에 추천 기반 `HIDDEN` 상품 초안과 `ACTIVE` 전환 상품, 추천 사용 이력이 생성되었습니다.

## 한계

- 추천 노출 이후 실제 예약/결제/픽업 전환은 생성 상품 ID 기준으로 집계합니다.
- 상품이 여러 번 숨김/재노출되는 세부 이력은 아직 별도 이벤트 로그로 분리하지 않습니다.
- 고객이 추천 상품을 본 노출 수, 클릭 수, 장바구니 같은 행동 데이터는 아직 없습니다.
- 실제 AI 모델은 아직 연결하지 않았습니다.

## 다음 단계

- 추천 상품 노출/숨김 이벤트 히스토리 분리
- 상품 카드 조회/클릭 이벤트 추적
- 추천 조회 → 초안 생성 → 노출 → 예약 → 픽업 전환 퍼널 시각화 강화
- 점주가 추천을 무시한 경우와 수정 후 노출한 경우 비교
- AI 추천 모델 학습용 피드백 데이터셋 정리
