# Phase 70 Release Check

## 작업 목적

재고 이상 알림을 점주가 확인했는지, 조치를 시작했는지, 해결 처리했는지 추적할 수 있도록 알림 조치 실행 MVP를 추가했다.

## 변경 내용

- `inventory_alert_actions` 테이블 추가
- 가맹점 API 추가
  - `POST /api/v1/merchant/pro/inventory-alert-actions`
  - `GET /api/v1/merchant/pro/inventory-alert-actions`
- `GET /api/v1/merchant/pro/inventory-alerts` 응답에 최신 조치 상태 추가
  - `latest_action_type`
  - `latest_action_at`
  - `is_acknowledged`
  - `is_resolved`
- `/merchant/pro/inventory-alerts` 화면에 조치 버튼 추가
  - 확인
  - 조치 시작
  - 해결 처리
  - 숨기기
- Pro 대시보드에 운영 알림 요약 보강

## DB 변경 여부

변경 있음.

- `inventory_alert_actions`

개인정보, 연락처, 주소, 토큰은 저장하지 않는다.

## 알림 조치 기준

- `ACKNOWLEDGED`: 점주가 알림을 확인함
- `ACTION_STARTED`: 점주가 조치를 시작함
- `MARKED_RESOLVED`: 점주가 해결 처리함
- `DISMISSED`: 점주가 알림을 숨김 처리함

같은 `product_id + alert_type` 기준으로 최신 조치 상태를 실시간 알림 응답에 매칭한다.

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- `cd backend && python scripts/smoke_test.py`: PASS
- `POST /api/v1/merchant/pro/inventory-alert-actions` 직접 호출: PASS
- `GET /api/v1/merchant/pro/inventory-alert-actions` 직접 호출: PASS
- `GET /api/v1/merchant/pro/inventory-alerts` 최신 조치 상태 반영 확인: PASS
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- 알림 원본은 저장하지 않고 실시간 계산 결과에 조치 상태만 매칭한다.
- 해결 처리 후에도 실제 조건이 남아 있으면 알림은 계속 표시되고, 상태만 해결 처리로 보인다.
- 외부 알림 발송, 담당자 배정, 조치 완료 검증 자동화는 아직 없다.

## 다음 단계

- 인앱 알림센터와 재고 알림 조치 연결
- 알림별 조치 완료 조건 자동 재검증
- 알림 숨김 기간 또는 snooze 기능
