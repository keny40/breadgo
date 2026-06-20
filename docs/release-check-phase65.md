# Phase 65 Release Check

## 작업 목적

CSV 상품 일괄 등록을 실제 POS 연동 전 운영 도구로 한 단계 고도화했다. 같은 상품을 반복 업로드해도 무조건 중복 생성되지 않도록 중복 감지/업데이트 옵션을 추가하고, 업로드 배치/row 이력을 남겨 점주가 결과를 나중에 다시 확인할 수 있게 했다.

## 변경 내용

- `products.external_sku` 추가
- `product_import_batches` 테이블 추가
- `product_import_rows` 테이블 추가
- CSV 선택 컬럼 추가
  - `external_sku`
  - `sku`
  - `import_action`
- `import_action` 지원
  - `CREATE_ONLY`
  - `UPDATE_OR_CREATE`
  - `SKIP_DUPLICATE`
- CSV preview/import 응답 확장
  - `batch_id`
  - `created_count`
  - `updated_count`
  - `skipped_count`
  - `rows`
  - `duplicate_detected`
  - `action_candidate`
- 업로드 이력 API 추가
  - `GET /api/v1/merchant/products/import-batches`
  - `GET /api/v1/merchant/products/import-batches/{batch_id}`
- `/merchant/products/import` 화면 개선
  - 중복 시 처리 방식 선택
  - preview row별 예정 액션 표시
  - import 결과 row별 액션 표시
  - 최근 업로드 이력 표시
  - 업로드 이력 상세 표시

## DB 변경 여부

있음.

마이그레이션:

- `backend/alembic/versions/202606180013_create_product_import_history.py`

추가/변경:

- `products.external_sku`
- `product_import_batches`
- `product_import_rows`

## 중복 감지/업데이트 기준

- `external_sku` 또는 `sku`가 있으면 같은 merchant/store 내 SKU 기준으로 중복 판단
- SKU가 없으면 같은 merchant/store 내 `name + sale_starts_at` 기준으로 중복 후보 판단
- `CREATE_ONLY`
  - 중복이 없으면 생성
  - 중복이면 `SKIPPED`
- `SKIP_DUPLICATE`
  - 중복이 없으면 생성
  - 중복이면 `SKIPPED`
- `UPDATE_OR_CREATE`
  - 중복이 없으면 생성
  - 중복이 있고 예약이 없으면 기존 상품 업데이트
  - 중복이 있지만 예약이 있으면 `SKIPPED`

업데이트 가능 필드:

- description
- image_url
- original_price
- discount_price
- stock_quantity
- sale_starts_at
- sale_ends_at
- 수령 방식
- 배송비

## 검증 결과

- PASS: `cd backend && python -m compileall app scripts`
- PASS: `cd backend && python -m alembic upgrade head`
- PASS: `cd backend && python scripts/smoke_test.py`
- PASS: 정상 CSV 신규 생성 직접 검증
- PASS: 중복 CSV `SKIP_DUPLICATE` preview/import 직접 검증
- PASS: 중복 CSV `UPDATE_OR_CREATE` import 직접 검증
- PASS: 업로드 이력 목록/상세 API 직접 검증
- PASS: `cd frontend && npm run lint`
- PASS: `cd frontend && npm run build`

직접 검증 결과:

- `created=1`
- `skipped=1`
- `updated=1`
- `batches=3`

## 한계

- 실제 POS API 연동은 아직 없다.
- 대용량 비동기 큐는 없다.
- SKU가 없는 데이터는 `name + sale_starts_at` 기준이라 완전한 중복 식별은 아니다.
- 예약이 있는 상품은 CSV 업데이트를 건너뛴다.
- 업로드 이력은 MVP 수준이며 파일 원본은 저장하지 않는다.

## 다음 단계

- CSV/POS 매핑 템플릿 저장
- import batch 상세 필터/검색
- 대용량 업로드 비동기 처리
- POS API 연동 전용 connector skeleton
- Enterprise 본사/다중 매장 CSV import 정책
