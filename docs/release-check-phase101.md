# Phase 101 Release Check

## 목적

BreadGo MVP와 BreadGo Pro 운영 기능을 최종 시연/제출/백업 가능한 Release Package 형태로 정리한다.

이번 Phase는 신규 기능 추가가 아니라 최종 릴리즈 문서화, 실행 가이드, 데모 계정, 기능 목록, 한계사항, 배포 전 체크리스트 정리 중심이다.

## 변경 사항

- 루트 `README.md` 최종 릴리즈 패키지 기준 보강
- MVP 기능 목록 문서 추가
- 데모 계정 및 시나리오 문서 추가
- 최종 릴리즈 체크리스트 문서 추가
- Phase 101 release check 문서 추가

## DB 변경 여부

DB 변경 없음.

Migration 추가 없음.

## 추가/수정 문서 목록

- `README.md`
- `docs/mvp-feature-summary.md`
- `docs/demo-accounts-and-scenarios.md`
- `docs/final-release-checklist.md`
- `docs/release-check-phase101.md`

## 최종 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS
  - 동일 기간 SCHEDULED 중복 실행 방지로 `SKIPPED` 응답 확인
- `python scripts/run_pro_health_alert_check.py`: PASS
  - `overall_status=WARNING`, 기존 OPEN/ACKNOWLEDGED alert 중복 skip 확인
- `npm run lint`: PASS
- `npm run build`: PASS
- `git status`: 확인 완료
  - clean 상태는 아님
  - Phase 101 변경: `README.md`, `docs/mvp-feature-summary.md`, `docs/demo-accounts-and-scenarios.md`, `docs/final-release-checklist.md`, `docs/release-check-phase101.md`
  - 기존 미정리 untracked 파일도 존재: `backend/alembic/versions/202606180022_create_pro_operations_audit_logs.py`, `backend/app/models/pro_operations_audit.py`, `docs/release-check-phase91.md`
- `git log --oneline -10`: 확인 완료
  - 최근 커밋: `dd78b72 Polish Pro operations demo readiness`

## 최종 데모 준비 상태

- README에 프로젝트 개요, 역할, 기술 스택, 실행 방법, CLI, 데모 경로, 한계를 정리했다.
- `docs/mvp-feature-summary.md`에 소비자/점주/관리자/BreadGo Pro/운영 기능을 정리했다.
- `docs/demo-accounts-and-scenarios.md`에 seed demo 계정과 역할별 시나리오를 정리했다.
- `docs/final-release-checklist.md`에 제출 전 확인 항목을 정리했다.

## 남은 한계

- 실제 PG 결제/환불 없음
- 실제 퀵배송/택배 API 없음
- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송 없음
- 외부 POS API 연동 없음
- 실제 AI 모델 없음
- 실서버 cron 등록 없음
- 자동 복구 없음
- 자동 purge scheduler 없음
- 세부 관리자 권한 분리 없음
- 대량 비동기 큐 없음

## Suggested commit message

`Prepare final MVP release package`
