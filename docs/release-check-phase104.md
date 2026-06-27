# Phase 104 Release Check

## 목적

GitHub에서 `v0.1.1-demo-ready` 태그 기준 Release를 생성할 때 바로 사용할 수 있는 최종 Release Title / Release Body / 등록 가이드를 문서화했다.

이번 Phase는 기능 추가가 아니라 GitHub Release 등록용 문안 정리 중심이다.

## 변경 파일 목록

- `README.md`
- `docs/github-release-v0.1.1-demo-ready.md`
- `docs/release-check-phase104.md`

## DB 변경 여부

DB 변경 없음.

Migration 추가 없음.

## 기능 코드 변경 여부

기능 코드 변경 없음.

## 추가 문서 목록

- `docs/github-release-v0.1.1-demo-ready.md`
- `docs/release-check-phase104.md`

## GitHub Release 문안 요약

- Release title: `BreadGo MVP Demo Ready Release v0.1.1`
- Tag: `v0.1.1-demo-ready`
- Target branch: `main`
- Release body 섹션:
  - Overview
  - Included in this release
  - BreadGo MVP
  - BreadGo Pro
  - Pro Operations
  - Demo run-through
  - Validation
  - What is mocked
  - Known limitations
  - How to run locally
  - Documentation links
  - Next steps

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS
  - 동일 기간 완료된 SCHEDULED batch run이 있어 중복 실행 방지 로직으로 `SKIPPED` 처리됨.
- `python scripts/run_pro_health_alert_check.py`: PASS
  - `overall_status=WARNING`, 기존 OPEN/ACKNOWLEDGED alert 중복으로 `generated_count=0`, `skipped_count=2`.
- `npm run lint`: PASS
- `npm run build`: PASS
- `git status`: PASS
  - Phase 104 변경 파일만 표시됨: `README.md`, `docs/github-release-v0.1.1-demo-ready.md`, `docs/release-check-phase104.md`.
- `git log --oneline -10`: PASS
  - 최신 커밋: `f62363d Document demo release handoff`.
- `git tag --list`: PASS
  - `v0.1.1-demo-ready` 태그 존재 확인.

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

`Document GitHub demo release draft`
