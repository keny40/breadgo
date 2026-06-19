# BreadGo Phase 53 릴리즈 체크

## 작업 목적

Phase 53은 BreadGo Pro의 차별화 기능인 가맹점용 폐기 감소·ESG 리포트를 추가하는 단계입니다.
점주가 BreadGo를 통해 판매로 전환한 마감 상품 수량과 폐기 방지 금액을 확인할 수 있게 했습니다.

## 변경 내용

- 백엔드 가맹점 전용 ESG 리포트 API 추가
  - `GET /api/v1/merchant/pro/esg-report`
- 오늘, 최근 7일, 이번 달 절감 수량과 폐기 방지 금액 집계
- 상품별 폐기 절감 기여도 제공
- 최근 7일 폐기 감소 trend 제공
- `/merchant/pro/esg` 페이지 추가
- 가맹점 NavBar에 `ESG 리포트` 메뉴 추가
- `/merchant/pro`에 `ESG 리포트 보기` CTA 추가

## 계산 기준

- 절감 수량 = `PICKED_UP` 상태이며 결제가 `PAID`인 예약의 상품 수량
- 폐기 방지 금액 = 픽업 완료 예약의 상품 금액 `product_amount`
- 취소된 예약은 절감 수량과 폐기 방지 금액에서 제외
- 최근 7일/오늘 집계는 예약의 `updated_at` 기준으로 픽업 완료 시점을 추정
- 탄소 절감량은 실제 상품 중량과 품목별 배출계수 데이터가 없어 이번 Phase에서는 확정값으로 표시하지 않음

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
- 백엔드 라우트 확인: `GET /api/v1/merchant/pro/esg-report` 확인
- ESG API 직접 호출 통과
  - 데모 가맹점 기준 `daily_esg_trend=7` 응답 확인
  - 상품별 ESG 요약 응답 확인
  - 탄소 절감량은 `추정 준비 중` 문구로 반환 확인
- 프론트엔드 `npm run lint` 통과
- 프론트엔드 `npm run build` 통과

## DB 변경 여부

없음.

기존 예약, 결제, 상품, 매장 데이터를 읽어 집계하며 새 테이블이나 컬럼을 추가하지 않았습니다.

## 한계

- 실제 POS 폐기량 데이터와 아직 연동하지 않았습니다.
- 상품별 중량 정보가 없어 실제 폐기 중량은 계산하지 않습니다.
- 탄소 배출 절감량은 근거 데이터 확보 전까지 `추정 준비 중`으로 표시합니다.
- 픽업 완료 시점은 별도 timestamp가 없어 예약 `updated_at`으로 추정합니다.

## 다음 단계

- 상품 중량/카테고리 데이터 추가
- POS 실제 폐기 데이터 연동
- 품목별 폐기 비용과 탄소 배출계수 적용
- 월간 ESG PDF 리포트 다운로드
- BreadGo Pro AI 수율/할인 추천과 연결
