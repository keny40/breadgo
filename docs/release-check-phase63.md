# Phase 63 Release Check

## 작업 목적

BreadGo Pro를 실제 과금 없이 Free / Pro / Enterprise 플랜 구조로 설명할 수 있게 만들고, 향후 SaaS 구독 수익 모델로 확장할 수 있는 MVP 권한/플랜 API와 화면을 추가했다.

## 변경 내용

- `GET /api/v1/merchant/pro/plan` 추가
- MVP 기본 플랜을 `PRO`로 설정
- 플랜 응답에 기능별 사용 가능 여부 포함
  - `yield_dashboard`
  - `relist_products`
  - `product_templates`
  - `esg_report`
  - `recommendations`
  - `recommendation_performance`
  - `product_funnel`
  - `multi_store_dashboard`
- `/merchant/pro/plan` 화면 추가
- NavBar에 `Pro 플랜` 메뉴 추가
- `/merchant/pro`에 현재 플랜 카드와 `Pro 플랜 보기` CTA 추가
- 주요 Pro 화면에 Pro/Enterprise 기능 배지 추가
  - `/merchant/pro`
  - `/merchant/pro/recommendations`
  - `/merchant/pro/esg`
  - `/merchant/pro/product-funnel`
  - `/merchant/pro/stores`

## DB 변경 여부

없음.

현재 Phase에서는 DB 컬럼이나 구독 결제 테이블을 만들지 않고, `DEFAULT_MERCHANT_PRO_PLAN = "PRO"` 기반으로 플랜 상태를 반환한다.

## 플랜 구분 기준

- `FREE`
  - 기본 상품 등록/예약 확인 중심
  - Pro 기능은 미리보기 또는 제한 안내 대상으로 정의
- `PRO`
  - 수율 대시보드
  - 반복 상품 등록
  - 요일별 템플릿
  - ESG 리포트
  - 추천 재고/할인가
  - 추천 성과
  - 고객 전환 퍼널
- `ENTERPRISE`
  - Pro 기능 전체
  - 다중 매장 통합
  - 프랜차이즈/본사 리포트
  - 향후 POS/CSV/API 연동

## 검증 결과

- PASS: `cd backend && python -m compileall app scripts`
- PASS: `cd backend && python -m alembic upgrade head`
- PASS: `cd backend && python scripts/smoke_test.py`
- PASS: `GET /api/v1/merchant/pro/plan` 직접 호출
  - 확인 결과: `plan=PRO`, `label=BreadGo Pro`, `is_pro_active=True`
- PASS: `cd frontend && npm run lint`
- PASS: `cd frontend && npm run build`

## 한계

- 실제 결제/구독 과금은 아직 연동하지 않았다.
- 플랜 상태는 DB 저장값이 아니라 MVP 기본값으로 반환한다.
- 기능 접근을 강하게 차단하지 않고, 데모 안정성을 위해 UI 안내와 기능 배지 중심으로 적용했다.
- Enterprise 권한/브랜드 본사 권한 모델은 아직 없다.

## 다음 단계

- merchant plan 저장 테이블 또는 subscription 테이블 설계
- Free/Pro/Enterprise 기능 접근 정책 고도화
- 실제 SaaS 결제/청구 연동 전환 설계
- Enterprise 본사/브랜드 계정 권한 모델 추가
