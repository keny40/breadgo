# Phase 69 Release Check

## 작업 목적

BreadGo Pro에서 점주가 문제가 될 수 있는 재고 상태를 빠르게 확인할 수 있도록 재고 이상 감지 / 운영 알림 MVP를 추가했다.

## 변경 내용

- 실시간 재고 이상 감지 서비스 추가
- 가맹점 API 추가
  - `GET /api/v1/merchant/pro/inventory-alerts`
- `/merchant/pro/inventory-alerts` 화면 추가
- NavBar에 `재고 알림` 메뉴 추가
- Pro 대시보드에 재고 이상 알림 CTA 추가
- Inventory Ledger 화면에 재고 이상 알림 CTA 추가
- Pro 플랜 화면에 `재고 이상 감지 / 운영 알림` 기능 표시

## DB 변경 여부

DB 변경 없음.

기존 `products`, `reservations`, `product_events`, `product_inventory_events` 데이터를 실시간 계산에 사용한다.

## 이상 감지 기준

- `NEGATIVE_STOCK`: 상품 재고가 0보다 작음
- `EXPIRED_WITH_STOCK`: 판매 종료 시간이 지났는데 활성 상품에 재고가 남아 있음
- `HIGH_VIEW_LOW_RESERVATION`: 최근 7일 조회가 많지만 예약 전환이 낮음
- `LARGE_STOCK_CHANGE`: 최근 Inventory Ledger에서 큰 폭의 재고 변동이 있음
- `CANCEL_RESTORED_HIDDEN`: 예약 취소로 재고가 복구됐지만 상품이 숨김 상태임
- `LOW_STOCK_HIGH_DEMAND`: 조회/판매 흐름이 좋은데 재고가 낮음

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- `cd backend && python scripts/smoke_test.py`: PASS
- `GET /api/v1/merchant/pro/inventory-alerts` 직접 호출: PASS
- `EXPIRED_WITH_STOCK` 케이스 직접 검증: PASS
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- 실제 SMS, Kakao, Push, 이메일 발송은 하지 않는다.
- 알림 저장/읽음 처리 없이 실시간 계산 결과만 보여준다.
- 임계값은 MVP용 rule-based 기준이다.
- 과도한 알림 억제, 알림 snooze, 담당자 배정은 아직 없다.

## 다음 단계

- 재고 이상 알림 저장 및 읽음/조치 완료 상태
- 인앱 알림센터와 운영 알림 연결
- 알림 임계값 점주 설정
- POS sync/추천 액션과 연계한 자동 조치 제안 고도화
