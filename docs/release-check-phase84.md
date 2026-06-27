# Phase 84 Release Check - Weekly Report Batch Operations Runbook

## 작업 목적

BreadGo Pro Weekly Report scheduler를 실제 운영 환경에서 안정적으로 사용할 수 있도록 cron 운영 문서와 runbook을 정리했다.

## 변경 사항

- `docs/weekly-report-batch-runbook.md` 추가
- Weekly Report batch 전체 흐름 정리
- admin 수동 실행 흐름 정리
- scheduler CLI 실행 흐름 정리
- retry failed 흐름 정리
- batch run 상태값과 run_type 의미 정리
- Linux cron 예시 추가
- Windows Task Scheduler 예시 추가
- 운영자 장애 대응 순서 추가
- 개인정보/연락처/주소/토큰 저장 금지 원칙 명시

## DB 변경 여부

- DB 변경 없음
- API 기능 변경 없음
- scheduler CLI 기능 변경 없음
- Admin 화면 기능 변경 없음

## 문서 추가 내용

- 운영자가 확인해야 할 화면:
  - `/admin/pro/weekly-report-batches`
- 운영 서버 CLI:
  - `python scripts/run_weekly_report_batch.py`
- Linux cron 예시:
  - 매주 월요일 오전 8시 실행 예시
- Windows Task Scheduler 예시:
  - Program/script, arguments, start in 경로 안내
- 장애 대응:
  - `SKIPPED`, `PARTIAL`, `FAILED`별 확인 순서
  - 실패 item retry 흐름

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- `cd backend && python scripts/seed_demo.py`: PASS
- `cd backend && python scripts/smoke_test.py`: PASS
- `cd backend && python scripts/run_weekly_report_batch.py`: PASS
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS
- 문서 파일 존재 확인: PASS
  - `docs/weekly-report-batch-runbook.md`
  - `docs/release-check-phase84.md`

## 남은 한계

- 실제 운영 서버 cron 설정은 문서 예시만 제공했다.
- 실제 Windows Task Scheduler 등록은 수행하지 않았다.
- 외부 이메일/카카오/Push 발송 runbook은 아직 없다.
