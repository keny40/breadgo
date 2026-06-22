# Phase 71 Release Check - BreadGo Pro Daily Brief

## 작업 목적

점주가 BreadGo Pro에 접속하자마자 오늘 확인해야 할 운영 이슈, 추천 액션, POS/CSV 상태를 한 화면에서 볼 수 있는 Daily Pro Brief MVP를 추가했다.

## 변경 내용

- `GET /api/v1/merchant/pro/daily-brief` 가맹점 전용 API 추가
- 오늘 매출, 예약 수량, 픽업 완료, 취소, 폐기 절감 수량, 재고 변경 이력 수 집계
- 미해결 재고 알림, 조치 중 알림, HIGH 알림, 추천 액션, POS/CSV 상태 기반 task 생성
- `/merchant/pro/daily-brief` 화면 추가
- `/merchant/pro` 대시보드 상단에 Daily Brief 요약 카드 추가
- NavBar 가맹점 메뉴에 `오늘 브리프` 추가

## DB 변경 여부

- DB 스키마 변경 없음
- 기존 대시보드, 추천, 재고 알림, POS, CSV import, 재고 이력 데이터를 실시간으로 집계

## Daily Brief 계산 기준

- 오늘 기준: Asia/Seoul 날짜의 시작부터 다음 날 시작 전까지
- 오늘 결제금액: 기존 Pro 수율 대시보드의 `today_gross_sales`
- 오늘 예약 수량: 기존 Pro 수율 대시보드의 `today_reserved_quantity`
- 폐기 절감 수량: 기존 Pro 수율 대시보드의 `today_estimated_saved_items`
- 미해결 알림: `MARKED_RESOLVED`, `DISMISSED`가 아닌 재고 알림
- 추천 액션: 최근 7일 추천 결과 중 우선순위가 높은 상위 항목
- POS 확인 task: 마지막 동기화가 없거나 24시간 이상 오래됐거나 실패 상태인 경우 생성
- CSV 확인 task: 오늘 CSV import 중 실패 행 또는 오류 상태가 있는 경우 생성

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- `cd backend && python scripts/smoke_test.py`: FAIL
  - 로컬 서버를 띄운 뒤 실행했으나 기존 smoke test의 지역 상품 조회 항목 중 하나가 `200 []`로 실패했다.
  - Health check, Customer login, 첫 번째 Region products found는 PASS.
  - 이번 Phase의 Daily Brief API 직접 호출은 별도로 PASS했으며, 실패 원인은 로컬/운영 데이터셋의 지역 상품 존재 여부로 보인다.
- Daily Brief API 직접 호출: PASS
  - `merchant@breadgo.test` 로그인 후 `/api/v1/merchant/pro/daily-brief` 호출 성공
  - `date`, 오늘 매출/예약/픽업/취소, 미해결 알림, 추천 액션, POS 상태, CSV 상태, 재고 이벤트 수, `tasks` 응답 확인
  - 추천 액션, 재고 알림, POS sync 확인 task가 응답에 포함됨
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- 실제 AI 요약 모델은 사용하지 않고 rule-based task 생성만 제공한다.
- 알림 원본을 별도 저장하지 않고 기존 실시간 재고 알림 계산 결과를 사용한다.
- POS/CSV 상태는 현재 동기화/업로드 기록 기반이며 외부 POS API는 호출하지 않는다.

## 다음 단계

- Daily Brief task 클릭/해결 전환 추적
- 아침 브리프 자동 알림 발송 준비
- 추천 액션과 재고 알림 조치 결과를 연결한 운영 개선 리포트 고도화
