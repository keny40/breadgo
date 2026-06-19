# BreadGo Phase 60 릴리즈 체크

## 작업 목적

Phase 60은 BreadGo Pro 추천 화면을 점주가 바로 이해하고 행동할 수 있는 운영 코치형 화면으로 강화하는 단계입니다.
추천 재고/할인가 숫자만 보여주는 것이 아니라, 왜 추천이 나왔는지와 지금 무엇을 해야 하는지를 함께 제공합니다.

## 변경 내용

- 추천 API 응답 설명 필드 추가
  - `explanation_title`
  - `explanation_reasons`
  - `suggested_actions`
  - `primary_action_label`
  - `action_priority`
  - `risk_label`
- 추천 설명 생성 로직 추가
  - 판매율
  - 픽업 완료율
  - 취소율
  - 고객 조회/예약 전환 신호
  - 현재 재고
  - 추천 재고/추천 할인가
- `/merchant/pro/recommendations` 화면 개선
  - 추천 이유
  - 지금 할 일
  - 주의 신호
  - 우선순위
  - 고객 반응 신호
- 추천 초안 생성 버튼 문구를 추천 액션에 맞게 표시
- `/merchant/pro` 대시보드에 `오늘의 추천 액션` 영역 추가
  - 우선순위 높은 추천 상위 3개 표시
  - 상품명, 추천 액션, 이유, 추천 재고/할인가, 추천 화면 이동 버튼 표시

## DB 변경 여부

없음.

기존 추천/고객 전환/예약 데이터를 활용해 rule-based 설명을 생성합니다.

## 설명/액션 생성 기준

- 조회는 많지만 예약 전환이 낮음
  - 설명: 관심은 있지만 예약 전환이 낮음
  - 액션: 할인가, 배송비, 수령 조건, 상품명/이미지 점검
  - 리스크: `LOW_CONVERSION_RISK`
- 판매율과 픽업 완료율이 높음
  - 설명: 수요가 안정적으로 확인됨
  - 액션: 재고 소폭 증가
  - 우선순위: 높음
- 판매율이 낮음
  - 설명: 현재 재고가 남을 가능성 있음
  - 액션: 재고 축소 또는 할인 강화
- 데이터가 적음
  - 설명: 아직 판단 데이터 부족
  - 액션: 소량 테스트 등록
  - 리스크: `DATA_TOO_SMALL`
- 취소율이 높음
  - 설명: 예약 후 이탈이 높음
  - 액션: 픽업 시간/배송 조건 확인
  - 리스크: `HIGH_CANCEL_RISK`

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

- PASS: `python -m compileall app scripts`
- PASS: `python -m alembic upgrade head`
- PASS: `npm run lint`
- PASS: `npm run build`
- PASS: 임시 uvicorn 실행 후 `python scripts/smoke_test.py`
- PASS: 추천 API에서 `explanation_title`, `explanation_reasons`, `suggested_actions`, `primary_action_label`, `action_priority`, `risk_label` 반환 확인

## 한계

- 실제 AI 모델은 아직 사용하지 않습니다.
- 설명과 액션은 MVP rule-based 로직입니다.
- 점주가 추천 설명을 읽었는지, 액션 카드를 클릭했는지는 아직 별도 이벤트로 추적하지 않습니다.
- 추천 액션 우선순위는 현 단계에서 판매/전환/리스크 신호 기반의 단순 점수화입니다.

## 다음 단계

- 점주 액션 카드 클릭/채택 이벤트 추적
- 추천 이유별 실제 채택률과 판매 성과 비교
- 점주 피드백 입력 기능
- 추천 설명 문구 A/B 테스트
- 실제 AI 추천 모델의 설명 가능성 설계
