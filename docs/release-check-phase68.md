# Phase 68 Release Check

## 작업 목적

BreadGo Pro에서 상품 재고가 어떤 원인으로 바뀌었는지 추적할 수 있도록 Inventory Ledger MVP를 추가했다.

## 변경 내용

- `product_inventory_events` 테이블 추가
- 재고 이벤트 기록 서비스 추가
- 주요 재고 변경 지점 연결
  - 수동 상품 생성/수정
  - CSV import 생성/업데이트
  - Mock POS sync 생성/업데이트
  - BreadGo Pro 추천 초안 생성
  - 예약 생성 재고 차감
  - 예약 취소 재고 복구
  - 픽업 완료 운영 이벤트
- 가맹점 API 추가
  - `GET /api/v1/merchant/pro/inventory-events`
  - `GET /api/v1/merchant/products/{product_id}/inventory-events`
- `/merchant/pro/inventory-ledger` 화면 추가
- NavBar, Pro 대시보드, Pro 플랜 화면에 재고 이력 연결

## DB 변경 여부

변경 있음.

- `product_inventory_events`

개인정보, 고객 연락처, 주소, 토큰은 저장하지 않는다.

## 재고 이벤트 기록 기준

- `MANUAL_CREATE`: 상품관리 수동 생성 또는 반복 등록
- `MANUAL_UPDATE`: 상품관리 재고 수정
- `CSV_IMPORT_CREATE`, `CSV_IMPORT_UPDATE`: CSV 일괄 등록/업데이트
- `POS_SYNC_CREATE`, `POS_SYNC_UPDATE`: Mock POS 동기화 생성/업데이트
- `RECOMMENDATION_DRAFT_CREATE`: Pro 추천 초안 생성
- `RESERVATION_CREATED`: 예약 생성으로 재고 차감
- `RESERVATION_CANCELLED`: 예약 취소 및 Mock 환불로 재고 복구
- `PICKUP_COMPLETED`: 픽업 완료 운영 이벤트, 재고 차감은 예약 생성 시점에 이미 반영

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- `cd backend && python scripts/smoke_test.py`: PASS
- CSV import 후 재고 이벤트 기록 확인: PASS
- Mock POS sync 후 재고 이벤트 기록 확인: PASS
- 예약 생성 후 재고 이벤트 기록 확인: PASS
- 예약 취소 후 재고 복구 이벤트 기록 확인: PASS
- inventory-events API 직접 호출 검증: PASS
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- 과거 이벤트는 소급 생성하지 않는다.
- 이번 Phase 이후 발생하는 재고 변경부터 기록한다.
- 대량 이벤트 분석, 재고 조정 승인 워크플로우, POS 원천 데이터 대조는 아직 없다.

## 다음 단계

- 재고 조정 수동 입력 기능
- POS sync batch와 Inventory Ledger 상세 연결 UI
- 재고 이상 변동 감지 및 점주 알림
