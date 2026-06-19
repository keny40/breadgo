# BreadGo Phase 50 릴리즈 체크

## 작업 목적

Phase 50은 BreadGo를 단순 마감 할인 앱에서 점주용 BreadGo Pro 수율 관리 도구로 확장하는 첫 단계입니다.
점주가 매일 확인할 수 있는 오늘의 판매율, 남은 재고, 픽업 완료율, 취소율, 예상 정산금, 폐기 절감 추정치를 제공하는 가맹점 전용 대시보드를 추가했습니다.

## 변경 내용

- 백엔드 가맹점 전용 API 추가
  - `GET /api/v1/merchant/pro/dashboard`
- 기존 매장, 상품, 예약, 결제, 정산 데이터 기반 집계 서비스 추가
- 오늘 기준 요약 지표 추가
- 최근 7일 수율 요약 추가
- 상품별 판매율, 남은 재고, 예약 수량, 픽업 완료 수량, 예상 정산금 제공
- 프론트엔드 `/merchant/pro` BreadGo Pro 대시보드 추가
- 가맹점 NavBar에 `Pro 대시보드` 메뉴 추가

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
- 백엔드 라우트 확인: `GET /api/v1/merchant/pro/dashboard` 확인
- 백엔드 Pro API 직접 호출 통과
  - 데모 가맹점 기준 `product_summaries=7`, `recent_7_days=7` 응답 확인
- 프론트엔드 `npm run lint` 통과
- 프론트엔드 `npm run build` 통과

## DB 변경 여부

없음.

이번 Phase는 기존 상품, 예약, 결제, 정산 데이터를 읽어서 집계하며 새 테이블이나 컬럼을 추가하지 않았습니다.

## 한계

- 오늘 등록 수량은 `현재 재고 + 오늘 유효 예약 수량` 기준의 MVP 추정치입니다.
- POS 실제 생산량/폐기량과 아직 연동하지 않았습니다.
- 폐기 절감 수량은 픽업 완료 수량 기준입니다.
- 폐기 방지 금액은 픽업 완료 예약의 할인 판매 금액 기준입니다.
- 탄소 배출 절감량은 실제 중량/품목 데이터가 없어 이번 Phase에서는 제공하지 않습니다.

## 다음 단계

- POS 또는 점주 입력 기반 실제 생산량/폐기량 연동
- 상품군별 수율 트렌드
- 시간대별 판매 속도 분석
- AI 할인 추천과 수요 예측 연결
- 점주 모바일 앱 BreadGo Pro 화면 확장
