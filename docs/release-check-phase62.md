# Phase 62 Release Check

## 작업 목적

BreadGo Pro를 단일 매장 운영 화면에서 다중 매장/프랜차이즈형 운영 대시보드로 확장할 수 있도록, 가맹점 보유 매장별 수율, 예약, 매출, 폐기 절감, 고객 전환 성과를 비교하는 MVP 기능을 추가했다.

## 변경 내용

- `GET /api/v1/merchant/pro/stores-dashboard` 추가
- 현재 로그인한 MERCHANT가 소유한 매장만 집계
- 최근 7일 기준 매장별 지표 제공
  - 판매중 상품 수
  - 예약/결제/픽업/취소 수
  - 총 결제금액
  - 예상 정산금
  - 폐기 절감 수량
  - 판매율
  - 상품 조회 수
  - 예약 전환율
- 매장 상태 라벨 제공
  - `GOOD`
  - `WATCH`
  - `NEED_ACTION`
  - `INSUFFICIENT_DATA`
- `/merchant/pro/stores` 화면 추가
- NavBar에 `매장 통합` 메뉴 추가
- `/merchant/pro`에 매장 통합 대시보드 CTA 추가

## DB 변경 여부

없음.

기존 `stores`, `products`, `reservations`, `payments`, `settlements`, `product_events` 데이터를 읽어 집계한다.

## 매장별 집계 기준

- 기준 기간: 최근 7일
- 판매율: 유효 예약 수량 / (현재 재고 + 유효 예약 수량)
- 예약 전환율: 예약 건수 / 상품 상세 조회 수
- 총 결제금액: 결제 완료 예약의 상품 금액 합계
- 예상 정산금: 취소되지 않은 settlement의 점주 정산금 합계
- 폐기 절감 수량: 픽업 완료 예약 수량 합계
- 상태 라벨:
  - 판매율과 픽업 완료율이 높으면 `GOOD`
  - 조회는 많지만 예약 전환이 낮으면 `WATCH`
  - 취소율이 높거나 판매율이 낮으면 `NEED_ACTION`
  - 데이터가 거의 없으면 `INSUFFICIENT_DATA`

## 검증 결과

- PASS: `cd backend && python -m compileall app scripts`
- PASS: `cd backend && python -m alembic upgrade head`
- PASS: `cd backend && python scripts/smoke_test.py`
- PASS: `GET /api/v1/merchant/pro/stores-dashboard` 직접 호출
  - 확인 결과 예시: `stores=3`, `reservations=74`, `sales=438675.00`
- PASS: `cd frontend && npm run lint`
- PASS: `cd frontend && npm run build`

## 한계

- 실제 프랜차이즈 본사/브랜드 권한 체계는 아직 없다.
- 현재는 MERCHANT 계정이 소유한 매장만 비교한다.
- 조회 이벤트는 MVP 수준으로 집계하며 rate limit이나 고급 세션 분석은 없다.
- 매장 상태 라벨은 rule-based이며 실제 AI 모델은 사용하지 않는다.

## 다음 단계

- 브랜드/본사 계정 권한 모델 설계
- 매장 그룹/지역별 비교 필터 추가
- 매장별 추천 액션 자동 생성
- POS 폐기 데이터 연동 시 수율/폐기 절감 정확도 개선
