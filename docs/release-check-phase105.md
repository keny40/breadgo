# Phase 105 Release Check

## 목적

`v0.1.1-demo-ready` 태그 기준 GitHub Release 등록 절차와 등록 후 검증 체크리스트를 문서화했다.

이번 Phase는 기능 추가가 아니라 GitHub Release publication / post-release verification 문서화 중심이다.

## 변경 파일 목록

- `README.md`
- `docs/github-release-publish-guide.md`
- `docs/post-release-verification-v0.1.1.md`
- `docs/release-check-phase105.md`

## DB 변경 여부

DB 변경 없음.

Migration 추가 없음.

## 기능 코드 변경 여부

기능 코드 변경 없음.

## 추가 문서 목록

- `docs/github-release-publish-guide.md`
- `docs/post-release-verification-v0.1.1.md`
- `docs/release-check-phase105.md`

## GitHub Release 등록 가이드 요약

- Tag: `v0.1.1-demo-ready`
- Target: `main`
- Release title: `BreadGo MVP Demo Ready Release v0.1.1`
- Release body source: `docs/github-release-v0.1.1-demo-ready.md`
- GitHub 웹 UI 등록 절차를 정리함.
- GitHub CLI 사용 가능 시 `gh release create` 예시를 추가함.
- CLI 미설치/미로그인 환경에서는 웹 UI 등록을 권장함.

## Post-release verification 요약

- Release URL 확인
- tag / target branch 연결 확인
- README, release notes, demo quickstart, handoff 문서 링크 확인
- 최종 backend/frontend/git 검증 명령 재확인
- 로컬과 원격 `main` 동기화 확인
- `git status` clean 확인
- `git tag --list`에서 `v0.1.1-demo-ready` 확인
- Mock / 미연동 항목과 개인정보/토큰 미노출 원칙 확인

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
  - Phase 105 변경 파일만 표시됨: `README.md`, `docs/github-release-publish-guide.md`, `docs/post-release-verification-v0.1.1.md`, `docs/release-check-phase105.md`.
- `git log --oneline -10`: PASS
  - 최신 커밋: `c6613c6 Document GitHub demo release draft`.
- `git tag --list`: PASS
  - `v0.1.1-demo-ready` 태그 존재 확인.

## 남은 한계

- 실제 PG 결제/환불 없음
- 실제 퀵배송/택배 API 없음
- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송 없음
- 외부 POS API 연동 없음
- 실서버 cron 등록 없음
- 자동 복구 없음
- 자동 purge scheduler 없음
- 세부 관리자 권한 분리 없음
- 대량 비동기 큐 없음

## Suggested commit message

`Document GitHub release publication`
