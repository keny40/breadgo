# BreadGo Phase 51 릴리즈 체크

## 작업 목적

Phase 51은 점주가 매일 반복하는 마감 상품 등록 부담을 줄이기 위한 기능입니다.
기존 상품 정보를 복제하고 오늘 재고와 판매 시간만 입력해 빠르게 다시 판매할 수 있는 `어제 남은 빵 그대로 올리기` 흐름을 추가했습니다.

## 변경 내용

- 백엔드 상품 복제 API 추가
  - `POST /api/v1/merchant/products/{product_id}/duplicate`
- 가맹점 본인 소유 상품만 복제 가능
- 원본 상품의 이름, 설명, 가격, 이미지 URL, 수령 방식, 배송비 설정 복사
- 복제 시 재고 수량, 판매 시작/종료 시간, 노출 여부, 이름 suffix 입력 가능
- 원본 상품은 변경하지 않고 새 상품 ID로 생성
- `/merchant/products`에 `그대로 다시 올리기` 버튼과 반복 등록 폼 추가
- `/merchant/pro`에 반복 상품 등록 CTA 추가

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
- 백엔드 라우트 확인: `POST /api/v1/merchant/products/{product_id}/duplicate` 확인
- 상품 복제 API 직접 호출 통과
  - 원본 상품과 다른 새 상품 ID 생성 확인
  - 검증용 복제 상품은 `HIDDEN` 상태로 생성해 고객 상품 목록 노출을 피했습니다.
- 프론트엔드 `npm run lint` 통과
- 프론트엔드 `npm run build` 통과

## DB 변경 여부

없음.

기존 `products` 테이블 구조를 재사용하며 새 테이블이나 컬럼을 추가하지 않았습니다.

## 한계

- 실제 POS의 전일 폐기/재고 데이터를 자동으로 읽지는 않습니다.
- 복제 대상 추천은 아직 수동 선택 방식입니다.
- 반복 등록 일정 예약이나 자동 등록은 아직 없습니다.
- 상품명 suffix와 재고/시간 입력은 MVP 수준의 단순 폼입니다.

## 다음 단계

- BreadGo Pro 대시보드에서 판매율 낮은 상품 자동 추천
- 전일 미판매 상품 기반 재등록 추천
- 요일별 반복 상품 템플릿
- POS 재고 데이터 연동
- AI 수요 예측과 할인 추천 연결
