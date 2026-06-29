# Release Sync Phase 119

## 목적

Phase 113~118에서 정리한 운영 안정화 / 데모 UX / v0.1.2 Release Candidate 준비 문서를 `origin/main`에 동기화하고, v0.1.2 공식 Release 생성 직전 상태를 확인했다.

이번 Phase에서는 기능 코드, DB schema, migration을 변경하지 않았다.

## Git / branch 상태

- Local branch: `main`
- Push 전 상태: `main...origin/main [ahead 11]`
- Push 대상: `origin/main`
- Push 결과: `48c596f..e4fef0d main -> main`
- Push 후 상태: `main...origin/main`
- 새 tag 생성 없음
- 새 GitHub Release 생성 없음
- 기존 tag 삭제/이동 없음

## 원격 README / v0.1.2 문서 확인

GitHub raw `main` 기준으로 아래 항목을 확인했다.

- `README.md`에 `docs/release-note-v0.1.2.md` 링크 반영 확인
- `README.md`에 `docs/release-checklist-v0.1.2.md` 링크 반영 확인
- `README.md`에 `docs/post-release-verification-v0.1.2.md` 링크 반영 확인
- `README.md`에 `v0.1.1-demo-ready` 공식 공개 데모 Release 기준 표시 확인
- `docs/release-note-v0.1.2.md` 원격 조회 확인
- `docs/release-checklist-v0.1.2.md` 원격 조회 확인

## v0.1.1 Release 상태

- Release tag: `v0.1.1-demo-ready`
- Release title: `BreadGo MVP Demo Ready Release v0.1.1`
- Release URL: `https://github.com/keny40/breadgo/releases/tag/v0.1.1-demo-ready`
- Target: `main`
- Draft: `false`
- Prerelease: `false`
- 공식 공개 데모 Release 기준은 계속 `v0.1.1-demo-ready`로 유지한다.

## v0.1.2-demo-published 상태

- Local tag 목록에 `v0.1.2-demo-published` 존재 확인
- GitHub Releases API에서 `v0.1.2-demo-published` release 조회 시 `404` 확인
- 따라서 `v0.1.2-demo-published`는 GitHub Release가 없는 문서성/임시 tag로 유지한다.
- 이번 Phase에서 tag 삭제/이동/Release 승격은 하지 않았다.

## v0.1.2 공식 tag 이름 후보

추천 후보:

1. `v0.1.2-demo-stabilized`
2. `v0.1.2-operations-ready`
3. `v0.1.2-demo-rc`

추천 기준:

- 기존 `v0.1.2-demo-published`와 혼동되지 않을 것
- 실제 GitHub Release에 사용할 수 있을 것
- v0.1.1 이후 운영 안정화 / 데모 개선 성격이 드러날 것

최우선 추천은 `v0.1.2-demo-stabilized`다. v0.1.1 공식 데모 이후 smoke coverage, troubleshooting, environment reference, demo UX 문서화를 보강한 성격을 가장 직접적으로 설명한다.

## 검증 결과

- `git status`: clean
- `git branch --show-current`: `main`
- `git status -sb`: push 후 `## main...origin/main`
- `git log --oneline -10`: Phase 113~118 문서/안정화 커밋 확인
- `git push origin main`: PASS
- 원격 README v0.1.2 링크 확인: PASS
- 원격 `docs/release-note-v0.1.2.md` 확인: PASS
- 원격 `docs/release-checklist-v0.1.2.md` 확인: PASS
- v0.1.1 Release URL 확인: PASS
- `v0.1.2-demo-published` Release 없음 확인: PASS
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS (`SCHEDULED` 중복 실행 방지로 `SKIPPED`)
- `python scripts/run_pro_health_alert_check.py`: PASS (`WARNING`, 기존 alert 중복 skip)
- `npm run lint`: PASS
- `npm run build`: PASS

## 변경 여부

- 기능 코드 변경: 없음
- DB schema 변경: 없음
- migration 추가: 없음
- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송 추가: 없음
- 외부 발송 API 연동 추가: 없음
- 새 tag / 새 Release 생성: 없음

## 남은 작업

- v0.1.2 공식 Release tag 이름 확정
- 확정된 tag 기준 Release note 최종화
- 새 tag 생성 및 GitHub Release 등록은 별도 Phase에서 수행
- `v0.1.2-demo-published`는 공식 Release로 승격하지 않고 문서성/임시 tag로 유지

## Suggested commit message

`Document v0.1.2 release sync readiness`
