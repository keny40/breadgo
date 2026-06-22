# Phase 77 Release Check - Weekly Report Auto Snapshot MVP

## 작업 목적

Weekly Pro Report를 향후 스케줄러가 매주 자동 저장할 수 있도록, 실제 cron 없이 자동 snapshot 미리보기와 실행 API를 준비했다.

## 변경 내용

- 자동 snapshot service 함수 추가
  - `preview_auto_weekly_snapshot`
  - `create_current_week_snapshot`
  - 기존 weekly report 계산과 snapshot 저장 로직 재사용
- `POST /api/v1/merchant/pro/weekly-report/auto-snapshot-preview` 추가
  - 저장 없이 기간, 생성/업데이트 여부, 요약 지표, 인사이트 미리보기 반환
- `POST /api/v1/merchant/pro/weekly-report/auto-snapshot` 추가
  - 같은 기간 snapshot이 없으면 생성, 있으면 최신 값으로 업데이트
- `/merchant/pro/weekly-report`에 자동 저장 준비 영역 추가
  - 자동 저장 미리보기
  - 이번 주 리포트 자동 저장
  - 저장될 기간과 요약 지표 표시
- `/merchant/pro/weekly-report/history` 안내 문구 보강
  - 수동/자동 공통 저장 이력으로 표시

## DB 변경 여부

- DB 스키마 변경 없음
- Phase 75의 `pro_weekly_report_snapshots`, `pro_weekly_report_insights`를 재사용
- snapshot source(`MANUAL`, `AUTO`)는 이번 Phase에서 저장하지 않음

## 자동 Snapshot 기준

- 기본 기간은 기존 Weekly Report 기본 기간과 동일하게 최근 7일 기준을 사용한다.
- `start_date`, `end_date` query를 넘기면 해당 기간 기준으로 미리보기/저장한다.
- 같은 `merchant_id + start_date + end_date` snapshot이 있으면 새로 만들지 않고 업데이트한다.
- 실제 cron, 외부 이메일, 카카오, Push 발송은 하지 않는다.
- 실제 AI 요약이 아닌 기존 rule-based weekly report 인사이트를 사용한다.

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- 백엔드 서버 실행 후 `cd backend && python scripts/seed_demo.py && python scripts/smoke_test.py`: PASS
- auto-snapshot-preview API 직접 호출: PASS
  - 신규 기간 미리보기에서 `would_create_new=true` 확인
  - 기존 기간 미리보기에서 `would_create_new=false`, `existing_snapshot_id` 확인
- auto-snapshot API 직접 호출: PASS
  - 신규 기간은 `CREATED`
  - 같은 기간 재실행은 `UPDATED`
- 같은 기간 중복 생성/업데이트 처리: PASS
  - 동일 기간 재실행 시 같은 `snapshot_id` 유지 확인
- 저장된 snapshot history/export 동작 유지 확인: PASS
  - history 조회와 저장 snapshot text export `200` 확인
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- 실제 스케줄러/cron은 아직 없다.
- 모든 merchant 일괄 자동 생성은 아직 없다.
- 수동 저장과 자동 저장 준비 흐름의 source 구분은 DB에 저장하지 않는다.
- PDF 생성과 외부 발송은 아직 없다.

## 다음 단계

- 운영 스케줄러에서 merchant별 자동 snapshot 생성
- snapshot source 필드 추가 검토
- 자동 저장 결과 알림센터 연동
