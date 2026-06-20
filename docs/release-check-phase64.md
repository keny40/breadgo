# Phase 64 Release Check

## 작업 목적

실제 POS API 연동 전 단계로, 점주가 엑셀에서 저장한 CSV 파일을 업로드해 마감 상품을 일괄 등록할 수 있는 MVP 기능을 추가했다.

## 변경 내용

- `POST /api/v1/merchant/products/import-csv/preview` 추가
  - CSV 파일을 실제 저장하지 않고 검증 결과만 반환
- `POST /api/v1/merchant/products/import-csv` 추가
  - 검증 성공 행을 상품으로 생성
  - 생성 상품 기본 상태는 `HIDDEN`
- CSV row별 오류 응답 추가
  - `row_number`
  - `field`
  - `message`
- `/merchant/products/import` 화면 추가
  - 매장 선택
  - CSV 파일 선택
  - 업로드 전 검증
  - CSV 일괄 등록
  - 샘플 CSV 다운로드
  - 성공/실패 결과 표시
- `/merchant/products`에 `CSV 일괄 등록` CTA 추가
- NavBar에 `CSV 등록` 메뉴 추가
- Pro 플랜 기능 플래그에 `csv_product_import` 추가
- `/merchant/pro/plan`에 `CSV 일괄 등록 / POS 연동 준비` 항목 반영

## DB 변경 여부

없음.

기존 `products` 테이블을 사용하며, 업로드 성공 상품은 `HIDDEN` 상태로 생성한다.

## CSV 컬럼 기준

필수 컬럼:

- `name`
- `original_price`
- `discount_price`
- `stock_quantity`
- `sale_starts_at`
- `sale_ends_at`

선택 컬럼:

- `description`
- `image_url`
- `pickup_available`
- `quick_delivery_available`
- `parcel_delivery_available`
- `quick_delivery_fee`
- `parcel_delivery_fee`

검증 기준:

- 상품명은 비어 있으면 안 된다.
- 정가/할인가는 0보다 커야 한다.
- 할인가가 정가보다 크면 실패한다.
- 재고는 0 이상의 정수여야 한다.
- 판매 시작 시간은 판매 종료 시간보다 빨라야 한다.
- 수령 방식은 최소 하나 이상 가능해야 한다.
- timezone 없는 날짜는 KST로 해석해 저장한다.
- UTF-8 BOM 또는 엑셀 CSV(cp949) 파일을 지원한다.

## 검증 결과

- PASS: `cd backend && python -m compileall app scripts`
- PASS: `cd backend && python -m alembic upgrade head`
- PASS: `cd backend && python scripts/smoke_test.py`
- PASS: 정상 CSV preview 직접 호출
- PASS: 정상 CSV import 직접 호출
  - 확인 결과: `created=1`
- PASS: 오류 CSV preview 직접 호출
  - 확인 결과: `bad_errors=1`
- PASS: `cd frontend && npm run lint`
- PASS: `cd frontend && npm run build`

## 한계

- 실제 POS API 연동은 아직 없다.
- 대용량 CSV 비동기 처리나 작업 큐는 없다.
- 중복 상품 감지는 아직 하지 않는다.
- 업로드 성공 상품은 바로 판매되지 않고 `HIDDEN` 상태로 생성되며, 점주가 상품관리에서 확인 후 노출해야 한다.

## 다음 단계

- POS/CSV 매핑 템플릿 저장
- 중복 상품 감지
- CSV import 이력 테이블 추가
- 대용량 업로드 비동기 처리
- 실제 POS API 연동 준비
