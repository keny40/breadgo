# Phase 75 Release Check - Weekly Pro Report Archive

## 작업 목적

Weekly Pro Report를 저장하고 과거 리포트를 다시 확인할 수 있는 Report Archive MVP를 추가했다.

## 변경 내용

- `pro_weekly_report_snapshots`, `pro_weekly_report_insights` 테이블 추가
- `POST /api/v1/merchant/pro/weekly-report/snapshot` 추가
- `GET /api/v1/merchant/pro/weekly-report/history` 추가
- `GET /api/v1/merchant/pro/weekly-report/history/{snapshot_id}` 추가
- 같은 `merchant_id + start_date + end_date` 기간은 중복 생성하지 않고 최신 값으로 업데이트
- 저장된 snapshot에 공유용 text summary와 운영 인사이트 저장
- `/merchant/pro/weekly-report`에 `이번 주 리포트 저장`, `저장 이력 보기` 버튼 추가
- `/merchant/pro/weekly-report/history` 화면 추가
- `/merchant/pro` 대시보드에 `리포트 이력 보기` CTA 추가

## DB 변경 여부

- DB 변경 있음
- Alembic migration: `202606180018_create_weekly_report_snapshots.py`

## Weekly Report Snapshot 저장 기준

- 저장은 명시적으로 `POST /weekly-report/snapshot` 호출 시에만 수행한다.
- 동일 기간 1개 snapshot 원칙: `merchant_id + start_date + end_date` unique.
- 같은 기간 snapshot이 이미 있으면 주요 지표, text summary, insights를 최신 값으로 업데이트한다.
- 저장된 리포트에서도 현재 기간으로 다시 열 수 있도록 기간 정보를 보관한다.
- 개인정보, 연락처, 주소, 토큰은 저장하지 않는다.

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- 백엔드 서버 실행 후 `cd backend && python scripts/seed_demo.py && python scripts/smoke_test.py`: PASS
- Weekly Report snapshot 생성 API 직접 호출: PASS
- history 목록/상세 API 직접 호출: PASS
- 같은 기간 중복 snapshot 처리 검증: PASS
  - 같은 기간 snapshot API를 2회 호출했을 때 동일 snapshot id 반환
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- 실제 PDF 생성은 하지 않는다.
- 외부 메일/카카오 발송은 하지 않는다.
- 저장된 리포트의 CSV/text export는 이번 Phase에서 별도 endpoint로 만들지 않고, `현재 기간으로 열기` CTA로 실시간 리포트 export를 재사용한다.

## 다음 단계

- 저장된 리포트 기준 CSV/text/PDF export
- 리포트 공유 링크 생성
- 주간 리포트 자동 저장 및 알림
