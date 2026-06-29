# Phase 108 Release Check

## 목적

GitHub Release `v0.1.1-demo-ready` 등록 완료 상태를 최종 확인하고, v0.1.1 데모 릴리스 완료 검증 결과를 정리했다.

이번 Phase는 release publication verification 문서화 중심이며 기능 코드, DB schema, migration은 변경하지 않았다.

## Release 최종 상태

- Release URL: `https://github.com/keny40/breadgo/releases/tag/v0.1.1-demo-ready`
- GitHub API release 조회: PASS
- Release title: `BreadGo MVP Demo Ready Release v0.1.1`
- Tag: `v0.1.1-demo-ready`
- Target branch: `main`
- Draft: `false`
- Prerelease: `false`
- Published at: `2026-06-29T00:08:28Z`
- Latest 표시: PASS
  - `https://api.github.com/repos/keny40/breadgo/releases/latest` 결과가 `v0.1.1-demo-ready`를 반환함.
  - Release HTML에서도 `Latest` 문자열을 확인함.
- `3 commits to main since this release` 표시: NOT DISPLAYED
  - Release HTML 확인 시 해당 문자열은 감지되지 않음.
  - 향후 화면에 표시된다면 태그 이후 문서성 커밋이 존재하는 상태로 해석하고 기록하면 됨.

## gh CLI 상태

- `gh` CLI는 현재 로컬 환경에 설치되어 있지 않음.
- `gh release view v0.1.1-demo-ready`는 실행 불가.
- 대신 GitHub REST API와 공개 Release URL로 release 상태를 검증함.

## README Release 링크 확인

- 로컬 `README.md`에는 다음 Release 링크가 존재함.
  - `https://github.com/keny40/breadgo/releases/tag/v0.1.1-demo-ready`
- Release URL 자체는 정상 접속됨.
- GitHub 원격 `main`의 README 화면에서는 Phase 107/108 기준 최신 release 링크 문구가 아직 감지되지 않음.
  - 원격 `main`에 README 변경 커밋/푸시가 반영된 뒤 다시 확인 필요.

## 변경 파일 목록

- `docs/release-check-phase108.md`

## DB 변경 여부

DB 변경 없음.

Migration 추가 없음.

## 기능 코드 변경 여부

기능 코드 변경 없음.

## 검증 결과

- `git status`: PASS
  - 문서 추가 전에는 clean 상태 확인.
  - Phase 108 문서 작성 후에는 `docs/release-check-phase108.md`만 변경됨.
- `git tag --list`: PASS
  - `v0.1.1-demo-ready` 태그 존재 확인.
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

## 등록 후 확인 체크리스트

- Release URL 정상 접속: PASS
- Release title 일치: PASS
- Tag 일치: PASS
- Target branch `main`: PASS
- Latest release 확인: PASS
- README 로컬 Release 링크 존재: PASS
- README Release URL 정상 접속: PASS
- GitHub 원격 README 최신 링크 반영: NEEDS FOLLOW-UP
- Mock / 미연동 항목 명시: PASS
- 개인정보/연락처/주소/외부 발송 토큰 미노출 원칙 유지: PASS

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
- `gh` CLI 미설치로 CLI 기반 release 조회는 불가

## Suggested commit message

`Document v0.1.1 release verification`
