# Phase 73 Release Check - Weekly Pro Report

## 작업 목적

Daily Brief snapshot을 활용해 최근 7일 운영 흐름을 한눈에 보는 Weekly Pro Report MVP를 추가했다.

## 변경 내용

- `GET /api/v1/merchant/pro/weekly-report` API 추가
- 기본 최근 7일 집계 제공
- `start_date`, `end_date` query parameter 지원
- Daily Brief snapshot 기반 주간 매출, 예약, 픽업, 취소, 폐기 절감, 미해결 알림, 추천 액션, 재고 변경, POS/CSV 이슈 집계
- snapshot이 없는 날짜는 0 처리
- 오늘 snapshot이 없으면 실시간 Daily Brief를 임시 반영
- rule-based 운영 인사이트 생성
- `/merchant/pro/weekly-report` 화면 추가
- NavBar에 `주간 리포트` 메뉴 추가
- `/merchant/pro`, `/merchant/pro/daily-brief/history`에서 주간 리포트 CTA 추가

## DB 변경 여부

- DB 스키마 변경 없음
- Phase 72의 `pro_daily_brief_snapshots`, `pro_daily_brief_tasks` 데이터를 활용

## 주간 리포트 계산 기준

- 기본 기간: 오늘 포함 최근 7일
- 지정 기간: `start_date`, `end_date`, 최대 31일
- 매출/예약/픽업/취소/폐기 절감: Daily Brief snapshot의 일자별 값 합산
- 평균 미해결 알림: 일자별 미해결 알림 수 평균
- HIGH 알림, 추천 액션, 재고 변경, POS/CSV 이슈: 일자별 값 합산
- snapshot 없는 날짜는 0으로 표시
- 오늘 snapshot이 없으면 저장하지 않고 실시간 Daily Brief 값을 임시로 반영
- 인사이트는 실제 AI가 아닌 rule-based 문구

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- 백엔드 서버 실행 후 `cd backend && python scripts/seed_demo.py && python scripts/smoke_test.py`: PASS
- Weekly Report API 직접 호출: PASS
  - `GET /api/v1/merchant/pro/weekly-report` 호출 성공
  - 기본 최근 7일 응답에서 `daily_trends` 7건, `insights` 응답 확인
- snapshot 있는 경우/없는 경우 안전 응답 확인: PASS
  - snapshot 있는 기본 최근 7일: `snapshot_days_count=1`, `daily_trends=7`
  - snapshot 없는 과거 기간 `2020-01-01~2020-01-07`: `daily_trends=7`, 총 매출 `0.00`
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- snapshot이 부족한 과거 날짜는 0으로 표시된다.
- 오늘은 snapshot이 없어도 실시간 Daily Brief를 임시 반영하지만 저장하지 않는다.
- 인사이트는 단순 rule-based이며 실제 AI 요약은 아니다.
- 주간 리포트 저장/공유/다운로드 기능은 아직 없다.

## 다음 단계

- 주간 리포트 저장 및 PDF/공유 기능
- 주간 리포트 자동 생성 및 알림
- Daily Brief task 조치율과 Weekly Report 연결
