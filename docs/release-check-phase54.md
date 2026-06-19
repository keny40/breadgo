# BreadGo Phase 54 릴리즈 체크

## 작업 목적

Phase 54는 BreadGo Pro 추천 재고/할인 제안 MVP를 추가하는 단계입니다.
실제 AI 모델 대신 최근 7일 판매, 픽업, 취소, 재고 데이터를 기반으로 rule-based 추천을 제공합니다.

## 변경 내용

- 백엔드 가맹점 전용 추천 API 추가
  - `GET /api/v1/merchant/pro/recommendations`
- 상품별 최근 예약 수량, 픽업 수량, 취소 수량, 현재 재고, 판매율, 픽업 완료율 집계
- 추천 재고 수량과 추천 할인가 계산
- 추천 타입 제공
  - `KEEP`
  - `INCREASE_STOCK`
  - `DECREASE_STOCK`
  - `LOWER_PRICE`
  - `RAISE_PRICE`
- 신뢰도 라벨 제공
  - `LOW`
  - `MEDIUM`
  - `HIGH`
- `/merchant/pro/recommendations` 페이지 추가
- 가맹점 NavBar에 `Pro 추천` 메뉴 추가
- `/merchant/pro`에 `오늘 추천 확인하기` CTA 추가
- `/merchant/product-templates`에 추천 재고 참고 안내 문구 추가

## 추천 계산 기준

- 최근 7일 데이터를 기준으로 계산
- 판매율 80% 이상이고 픽업 완료율 80% 이상이면 재고 증가 또는 가격 소폭 상향 후보
- 판매율 30% 이하이면 재고 감소 또는 할인 강화 후보
- 취소율 30% 이상이면 재고 증가를 추천하지 않음
- 데이터가 3건 미만이면 `LOW` 신뢰도
- 추천 할인가는 기존 할인가 기준 ±5~10% 범위에서 제안
- 실제 AI 모델이 아니므로 UI에 `AI 추천 준비 단계`와 `최근 7일 데이터 기반` 문구를 표시

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
- 백엔드 라우트 확인: `GET /api/v1/merchant/pro/recommendations` 확인
- 추천 API 직접 호출 통과
  - 데모 가맹점 기준 추천 10건 응답 확인
  - `KEEP`, `INCREASE_STOCK`, `RAISE_PRICE` 추천 타입 응답 확인
  - `LOW`, `MEDIUM`, `HIGH` 신뢰도 라벨 응답 확인
- 프론트엔드 `npm run lint` 통과
- 프론트엔드 `npm run build` 통과

## DB 변경 여부

없음.

기존 상품, 예약, 결제 데이터를 읽어 추천을 계산하며 새 테이블이나 컬럼을 추가하지 않았습니다.

## 한계

- 실제 AI 모델은 아직 사용하지 않습니다.
- 추천 가격은 참고용이며 상품 생성 시 자동 반영하지 않습니다.
- `추천 재고로 초안 생성`은 추천 재고를 반영한 `HIDDEN` 상품 초안을 만들고, 가격은 상품관리에서 확인 후 수정해야 합니다.
- 외부 요인, 날씨, 요일별 수요, POS 생산량은 아직 반영하지 않습니다.

## 다음 단계

- 추천 할인가 자동 반영 옵션
- 요일/날씨/지역 이벤트 기반 추천
- 상품 템플릿과 추천 재고 자동 연결
- AI 수요 예측 모델 연동
- 추천 결과에 대한 점주 피드백 수집
