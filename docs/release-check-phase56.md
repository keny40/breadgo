# BreadGo Phase 56 릴리즈 체크

## 작업 목적

Phase 56은 BreadGo Pro 추천을 점주가 그대로 채택했는지, 아니면 현장 상황에 맞게 수정 후 채택했는지 추적하는 단계입니다.
이 데이터는 향후 추천 품질 개선과 실제 AI 추천 모델 검증에 사용할 수 있습니다.

## 변경 내용

- 추천 초안 생성 요청 확장
  - `accepted_stock_quantity`
  - `accepted_discount_price`
  - `accepted_sale_starts_at`
  - `accepted_sale_ends_at`
  - `note`
- `recommendation_usages` 저장 정보 확장
  - `accepted_stock_quantity`
  - `accepted_discount_price`
  - `stock_delta`
  - `discount_price_delta`
  - `adoption_type`
- 추천 성과 API 확장
  - `exact_accept_count`
  - `modified_accept_count`
  - `exact_accept_rate`
  - `modified_accept_rate`
  - `average_stock_delta`
  - `average_discount_price_delta`
- `/merchant/pro/recommendations`에서 추천 재고/할인가를 기본값으로 보여주고 점주가 수정 입력 가능하게 개선
- `/merchant/pro/recommendation-performance`에 그대로 채택/수정 후 채택 지표와 수정폭 표시 추가

## DB 변경 여부

있음.

Alembic migration `202606180009_add_recommendation_adoption_fields.py`를 추가해 기존 `recommendation_usages` 테이블에 nullable 컬럼을 추가했습니다.
기존 Phase 55 데이터는 API 응답 시 추천값 기준으로 fallback 처리해 호환됩니다.

## 추천 수정·채택 계산 기준

- 추천 재고와 실제 채택 재고가 같고, 추천 할인가와 실제 채택 할인가가 같으면 `EXACT_ACCEPTED`
- 재고 또는 할인가 중 하나라도 다르면 `MODIFIED_ACCEPTED`
- `stock_delta` = 실제 채택 재고 - 추천 재고
- `discount_price_delta` = 실제 채택 할인가 - 추천 할인가
- 기존 데이터에 채택 정보가 없으면 추천값을 그대로 채택한 것으로 계산 가능한 fallback을 적용

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
- PASS: 추천값 그대로 초안 생성 직접 검증
  - `EXACT_ACCEPTED` 이력 생성 확인
- PASS: 추천값 수정 후 초안 생성 직접 검증
  - `MODIFIED_ACCEPTED` 이력 생성 확인
- PASS: 추천 성과 API에서 `exact_accept_count`, `modified_accept_count`, 평균 수정폭 반영 확인

직접 검증 과정에서 로컬 DB에 추천 기반 `HIDDEN` 상품 초안과 추천 사용 이력이 생성되었습니다.

## 한계

- 실제 AI 모델은 아직 사용하지 않습니다.
- 추천 무시, 추천 조회, 추천 수정 후 최종 노출 여부까지의 전환 퍼널은 아직 분리 추적하지 않습니다.
- 점주가 초안 생성 후 상품관리에서 다시 수정한 값은 아직 추천 수정폭에 반영하지 않습니다.
- `note` 필드는 요청 확장용으로 열어두었지만 별도 UI 표시는 아직 없습니다.

## 다음 단계

- 추천 조회, 무시, 초안 생성, 실제 노출, 판매 성과를 퍼널로 분리
- 추천 초안 생성 후 상품관리 수정 내역 추적
- 점주 피드백 입력 기능
- 추천 조정 데이터를 기반으로 rule 개선
- 실제 AI 추천 모델 학습 데이터셋 구성
