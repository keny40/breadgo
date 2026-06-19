# BreadGo Phase 61 릴리즈 체크

## 작업 목적

Phase 61은 BreadGo Pro 추천 액션이 실제로 실행되는지 추적하는 단계입니다.
점주가 추천 액션 카드를 클릭했는지, 추천 화면에서 초안 생성을 시작했는지, 실제 초안 생성까지 이어졌는지 확인할 수 있게 합니다.

## 변경 내용

- `recommendation_action_events` 테이블 추가
  - `merchant_id`
  - `product_id`
  - `recommendation_type`
  - `action_priority`
  - `risk_label`
  - `event_type`
  - `source`
  - `created_product_id`
  - `created_at`
- 가맹점 전용 액션 이벤트 기록 API 추가
  - `POST /api/v1/merchant/pro/recommendation-action-events`
- 추천 초안 생성 성공 시 `DRAFT_CREATED` 이벤트 자동 기록
- `/merchant/pro` 오늘의 추천 액션 카드 클릭 시 `ACTION_CARD_CLICKED` 기록
- `/merchant/pro/recommendations` 초안 생성 버튼 클릭 시 `DRAFT_CREATE_STARTED` 기록
- 추천 성과 API 확장
  - `action_card_click_count`
  - `draft_create_started_count`
  - `action_draft_created_count`
  - `action_to_draft_rate`
  - `recent_action_events`
- `/merchant/pro/recommendation-performance` 화면에 액션 실행 카드와 최근 액션 이벤트 목록 추가

## DB 변경 여부

있음.

Alembic migration `202606180012_create_recommendation_action_events.py`를 추가해 `recommendation_action_events` 테이블을 생성했습니다.
개인정보, 토큰, 연락처는 저장하지 않습니다.

## 액션 실행 계산 기준

- 기간: 최근 7일
- 액션 카드 클릭 = `event_type = ACTION_CARD_CLICKED`
- 초안 생성 시작 = `event_type = DRAFT_CREATE_STARTED`
- 초안 생성 완료 = `event_type = DRAFT_CREATED`
- 액션→초안 전환율 = 초안 생성 완료 수 / 액션 카드 클릭 수
- 이벤트 source
  - `PRO_DASHBOARD`: Pro 대시보드 오늘의 추천 액션 카드
  - `RECOMMENDATIONS_PAGE`: 추천 화면 초안 생성 흐름

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
- PASS: `ACTION_CARD_CLICKED` 직접 기록 확인
- PASS: `DRAFT_CREATE_STARTED` 직접 기록 확인
- PASS: 추천 초안 생성 성공 후 `DRAFT_CREATED` 자동 기록 확인
- PASS: 추천 성과 API에서 액션 실행 지표와 최근 이벤트 반영 확인

직접 검증 과정에서 로컬 DB에 추천 액션 이벤트와 추천 기반 `HIDDEN` 상품 초안이 생성되었습니다.

## 한계

- `ACTION_CARD_VIEWED`는 이벤트 과다 기록을 피하기 위해 아직 연결하지 않았습니다.
- 점주가 추천 화면에 머문 시간이나 설명을 읽었는지는 추적하지 않습니다.
- 추천 액션 클릭 후 상품관리에서 수동으로 상품을 수정하는 후속 행동은 아직 연결하지 않습니다.
- 실제 AI 모델은 아직 사용하지 않습니다.

## 다음 단계

- 추천 액션 클릭 → 초안 생성 → 상품 노출 → 예약/픽업까지 통합 퍼널 시각화
- 추천 설명별 클릭률/채택률 비교
- 점주가 추천을 무시한 경우 기록
- 추천 액션 카드 A/B 테스트
- 실제 AI 추천 모델 학습용 피드백 이벤트 정리
