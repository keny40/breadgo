# BreadGo Phase 55 릴리즈 체크

## 작업 목적

Phase 55는 BreadGo Pro 추천이 실제로 사용되는지와 추천으로 생성한 상품의 판매/픽업 성과를 추적하는 단계입니다.
이 데이터는 향후 실제 AI 추천 모델의 검증과 학습 기반으로 활용할 수 있습니다.

## 변경 내용

- `recommendation_usages` 테이블 추가
- 추천 초안 생성 API 추가
  - `POST /api/v1/merchant/pro/recommendations/{product_id}/create-draft`
- 추천 성과 API 추가
  - `GET /api/v1/merchant/pro/recommendation-performance`
- 추천 초안 생성 시 `DRAFT_CREATED` 사용 이력 저장
- 생성된 상품 ID와 원본 상품 ID 연결
- 추천 타입, 신뢰도, 추천 재고, 추천 할인가, 기존 재고/할인가 저장
- `/merchant/pro/recommendation-performance` 화면 추가
- NavBar에 `추천 성과` 메뉴 추가
- `/merchant/pro`와 `/merchant/pro/recommendations`에 추천 성과 CTA 추가

## DB 변경 여부

있음.

Alembic migration `202606180008_create_recommendation_usages.py`를 추가해 `recommendation_usages` 테이블을 생성했습니다.

## 추천 성과 계산 기준

- 추천 조회만으로는 사용 이력을 만들지 않음
- 추천 초안 생성처럼 명확한 행동만 `DRAFT_CREATED`로 기록
- 추천으로 생성된 상품의 예약/결제/픽업 데이터를 연결해 성과 집계
- 추천 상품 픽업 수량 = 추천으로 생성된 상품의 `PICKED_UP` 예약 수량
- 추천 상품 매출 = 추천으로 생성된 상품의 결제 완료 예약 `product_amount`
- 추천 후 판매율 = 추천 생성 상품의 예약 수량 / 현재 재고 + 예약 수량

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
- PASS: `python scripts/smoke_test.py`
- PASS: 추천 성과 라우트 확인
  - `GET /api/v1/merchant/pro/recommendations`
  - `POST /api/v1/merchant/pro/recommendations/{product_id}/create-draft`
  - `GET /api/v1/merchant/pro/recommendation-performance`
- PASS: 추천 초안 생성 직접 검증
  - 추천 초안 생성 응답에 `usage_id` 반환 확인
  - 생성 상품 상태가 `HIDDEN`인 것 확인
  - 추천 성과 API의 `total_recommendation_drafts`, `recent_usages` 반영 확인
- PASS: `npm run lint`
- PASS: `npm run build`

직접 검증 과정에서 로컬 DB에 추천 기반 `HIDDEN` 상품 초안과 추천 사용 이력이 생성되었습니다.

## 한계

- 실제 AI 모델 학습은 아직 수행하지 않습니다.
- 추천을 무시한 행동은 아직 기록하지 않습니다.
- 추천 초안 생성 후 점주가 수동으로 가격을 바꾸는 경우 변경 전후 차이는 아직 추적하지 않습니다.
- 추천 성과는 생성된 상품 ID 기준이므로 상품을 다시 복제하면 별도 성과로 추적됩니다.

## 다음 단계

- 추천 무시/수정/채택 이벤트 분리
- 추천 할인가 자동 반영 옵션
- 점주 피드백 수집
- 추천 성과 기반 rule 조정
- 실제 AI 추천 모델 학습 데이터셋 생성
