# BreadGo Phase 58 릴리즈 체크

## 작업 목적

Phase 58은 고객의 상품 행동 데이터를 수집해 점주가 상품별 조회 → 예약 → 결제 → 픽업 전환 퍼널을 확인할 수 있게 하는 단계입니다.
BreadGo Pro 추천 품질을 개선하기 위한 고객 반응 데이터 기반을 만드는 것이 목표입니다.

## 변경 내용

- `product_events` 테이블 추가
  - `product_id`
  - `store_id`
  - `merchant_id`
  - `user_id`
  - `event_type`
  - `source`
  - `created_at`
- 상품 이벤트 기록 API 추가
  - `POST /api/v1/products/{product_id}/events`
  - 비로그인/로그인 모두 기록 가능
  - 로그인 토큰이 있으면 `user_id` 저장
- 예약 생성 성공 시 `RESERVATION_CREATED` 이벤트 자동 기록
- BreadGo Pro 상품 전환 퍼널 API 추가
  - `GET /api/v1/merchant/pro/product-funnel`
- `/merchant/pro/product-funnel` 화면 추가
  - 상품 조회
  - 예약 시작
  - 예약 생성
  - 결제 완료
  - 픽업 완료
  - 예약 전환율
  - 추천 상품 여부
  - 조회는 많지만 예약이 낮은 상품 표시
- `/merchant/pro` 대시보드에 고객 전환 퍼널 CTA 추가
- NavBar 가맹점 메뉴에 `고객 전환` 링크 추가
- 웹 `/products`에서 고객 행동 이벤트 기록
  - 수령 방식 선택 시 `DETAIL_VIEW`
  - 예약 버튼 클릭 시 `RESERVATION_STARTED`
- Flutter 상품 상세 화면에서 고객 행동 이벤트 기록
  - 상세 진입 시 `DETAIL_VIEW`
  - 예약 제출 시 `RESERVATION_STARTED`

## DB 변경 여부

있음.

Alembic migration `202606180011_create_product_events.py`를 추가해 `product_events` 테이블을 생성했습니다.
개인정보, 토큰, 주소, 연락처는 저장하지 않습니다.

## 고객 행동 퍼널 계산 기준

- 기간: 최근 7일
- 상품 조회 = `product_events.event_type = DETAIL_VIEW`
- 예약 시작 = `product_events.event_type = RESERVATION_STARTED`
- 예약 생성 = 예약 테이블의 최근 7일 예약 수
- 결제 완료 = 예약에 연결된 결제 상태가 `PAID`인 건수
- 픽업 완료 = 예약 상태가 `PICKED_UP`인 건수
- 예약 전환율 = 예약 생성 수 / 상품 상세 조회 수
- 기존 예약 데이터가 이벤트 추적보다 먼저 쌓인 경우를 고려해 전환율은 최대 100%로 표시
- 추천 상품 여부 = `recommendation_usages.created_product_id`와 상품 ID 연결 여부

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

cd mobile
dart format lib test
flutter analyze --no-pub
flutter test --no-pub
```

- PASS: `python -m compileall app scripts`
- PASS: `python -m alembic upgrade head`
- PASS: 임시 uvicorn 실행 후 `python scripts/smoke_test.py`
- PASS: `DETAIL_VIEW` 이벤트 직접 기록
- PASS: `RESERVATION_STARTED` 이벤트 직접 기록
- PASS: 예약 생성 후 상품 전환 API에 예약 지표 반영 확인
- PASS: `npm run lint`
- PASS: `npm run build`
- PASS: `dart format lib test`
- PASS: `flutter test --no-pub`
- SKIP/TIMEOUT: `flutter analyze --no-pub`
  - 제한 시간 내 완료되지 않아 타임아웃되었습니다.

직접 검증 과정에서 로컬 DB에 상품 이벤트와 예약 데이터가 생성되었습니다.

## 한계

- 이벤트 폭증 방지를 위한 서버 rate limit은 아직 없습니다.
- 상품 목록 렌더링마다 `LIST_VIEW`를 기록하지는 않습니다.
- 웹은 상세 페이지가 별도로 없어 수령 방식 선택을 상품 상세/관심 행동으로 기록합니다.
- 고객 클릭, 스크롤, 체류 시간 같은 세부 행동 데이터는 아직 수집하지 않습니다.
- 실제 AI 모델은 아직 연결하지 않았습니다.

## 다음 단계

- 이벤트 rate limit 또는 client/server dedupe 강화
- 상품 상세 페이지 분리 또는 modal 상세 보기 도입
- 조회/예약/결제/픽업 전환 퍼널 시각화 강화
- 고객 행동 기반 추천 rule 보정
- 추천 상품과 일반 상품의 전환율 비교 리포트 추가
