# Phase 72 Release Check - Daily Pro Brief History

## 작업 목적

Daily Pro Brief의 주요 지표와 할 일 목록을 날짜별 snapshot으로 저장해 점주가 어제 대비 운영 이슈가 줄었는지 확인할 수 있게 했다.

## 변경 내용

- `pro_daily_brief_snapshots`, `pro_daily_brief_tasks` 테이블 추가
- `POST /api/v1/merchant/pro/daily-brief/snapshot` 추가
- `GET /api/v1/merchant/pro/daily-brief/history` 추가
- `GET /api/v1/merchant/pro/daily-brief/history/{snapshot_id}` 추가
- 같은 가맹점의 같은 날짜 snapshot은 중복 생성하지 않고 최신 Daily Brief 값으로 업데이트
- `/merchant/pro/daily-brief` 화면에 `오늘 브리프 저장`, `브리프 이력` CTA 추가
- `/merchant/pro/daily-brief/history` 화면 추가
- `/merchant/pro` Daily Brief 카드에 이력 CTA 추가

## DB 변경 여부

- DB 변경 있음
- Alembic migration: `202606180017_create_daily_brief_snapshots.py`

## Daily Brief Snapshot 저장 기준

- 저장은 명시적으로 `POST /daily-brief/snapshot` 호출 시에만 수행한다.
- 하루 1개 snapshot 원칙: `merchant_id + brief_date` unique.
- 저장 시 기존 실시간 Daily Brief 계산 결과를 snapshot에 반영한다.
- 같은 날짜 snapshot이 이미 있으면 수치와 task 목록을 최신 값으로 업데이트한다.
- task 목록은 저장 시점의 브리프 할 일 목록으로 교체 저장한다.
- 개인정보, 연락처, 주소, 토큰은 저장하지 않는다.

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- 백엔드 서버 실행 후 `cd backend && python scripts/seed_demo.py && python scripts/smoke_test.py`: PASS
- Daily Brief snapshot 생성 API 직접 호출: PASS
  - `POST /api/v1/merchant/pro/daily-brief/snapshot` 호출 성공
  - 저장된 task 4건 확인
- History API 직접 호출: PASS
  - `GET /api/v1/merchant/pro/daily-brief/history` 호출 성공
  - `GET /api/v1/merchant/pro/daily-brief/history/{snapshot_id}` 호출 성공
- 같은 날짜 중복 snapshot 처리 검증: PASS
  - 같은 날짜에 snapshot API를 2회 호출했을 때 동일 snapshot id 반환
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- snapshot은 수동 저장 API/버튼으로만 생성된다.
- 자동 매일 저장, 예약 작업, 외부 알림 발송은 아직 없다.
- 운영 개선 비교는 최신 snapshot과 바로 이전 snapshot의 단순 증감만 제공한다.
- 실제 AI 요약 모델은 사용하지 않는다.

## 다음 단계

- 아침 자동 브리프 저장 및 알림 발송
- 브리프 task별 조치 완료율 연결
- 주간/월간 운영 개선 리포트 확장
