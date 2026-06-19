# BreadGo Phase 52 릴리즈 체크

## 작업 목적

Phase 52는 점주가 자주 올리는 마감 상품 묶음을 요일별 템플릿으로 저장하고, 오늘 판매 상품으로 한 번에 등록할 수 있게 하는 단계입니다.
Phase 51의 상품 복제 로직을 재사용해 점주의 반복 상품 등록 부담을 더 줄였습니다.

## 변경 내용

- `product_templates` 테이블 추가
- 백엔드 가맹점 전용 템플릿 API 추가
  - `GET /api/v1/merchant/product-templates`
  - `POST /api/v1/merchant/product-templates`
  - `PATCH /api/v1/merchant/product-templates/{template_id}`
  - `DELETE /api/v1/merchant/product-templates/{template_id}`
  - `POST /api/v1/merchant/product-templates/{template_id}/create-product`
  - `POST /api/v1/merchant/product-templates/create-today-products`
- 템플릿에서 Phase 51 상품 복제 로직을 재사용해 실제 상품 생성
- `/merchant/product-templates` 페이지 추가
- 가맹점 NavBar에 `상품 템플릿` 메뉴 추가
- `/merchant/pro`에 `오늘 템플릿으로 한 번에 등록` CTA 추가

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

검증 결과:

- 백엔드 `python -m compileall app scripts` 통과
- 백엔드 `python -m alembic upgrade head` 통과
- 백엔드 `python scripts/smoke_test.py` 통과
- 백엔드 라우트 확인 통과
  - `GET /api/v1/merchant/product-templates`
  - `POST /api/v1/merchant/product-templates`
  - `PATCH /api/v1/merchant/product-templates/{template_id}`
  - `DELETE /api/v1/merchant/product-templates/{template_id}`
  - `POST /api/v1/merchant/product-templates/{template_id}/create-product`
  - `POST /api/v1/merchant/product-templates/create-today-products`
- 템플릿 API 직접 호출 통과
  - 템플릿 생성
  - 템플릿 수정
  - 템플릿 기반 상품 생성
  - 오늘 요일 템플릿 전체 등록
- 프론트엔드 `npm run lint` 통과
- 프론트엔드 `npm run build` 통과

참고: 직접 검증 중 생성한 상품은 `HIDDEN` 상태로 생성해 고객 상품 목록 노출을 피했습니다.

## DB 변경 여부

있음.

Alembic migration `202606180007_create_product_templates.py`를 추가해 `product_templates` 테이블을 생성했습니다.

## 한계

- 실제 POS 재고 데이터와 아직 연동하지 않았습니다.
- 템플릿은 상품 1개 기준이며, 여러 상품을 묶은 세트 템플릿은 아직 없습니다.
- 자동 스케줄 등록은 아직 없고 점주가 버튼으로 실행합니다.
- 템플릿별 추천 수량은 아직 AI가 아니라 점주 기본값을 사용합니다.

## 다음 단계

- 요일별 상품 묶음 템플릿
- 전일 미판매 상품 자동 추천
- POS 기반 기본 재고 자동 입력
- 판매율 기반 추천 재고 수량
- AI 수요 예측과 할인 추천 연결

