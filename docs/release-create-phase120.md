# Release Create Phase 120

## 목적

`origin/main` 기준으로 v0.1.2 공식 Release 후보 tag를 생성하고, GitHub Release 등록 가능 상태를 확인했다.

이번 Phase에서는 기능 코드, DB schema, migration을 변경하지 않았다.

## 사전 상태

- Branch: `main`
- Sync status: `main...origin/main`
- Working tree: clean
- 기존 `v0.1.1-demo-ready` tag / Release 변경 없음
- 기존 `v0.1.2-demo-published` tag 삭제/이동 없음

## 생성한 tag

- Tag: `v0.1.2-demo-stabilized`
- Type: annotated tag
- Tag message: `BreadGo Demo Stabilized Release v0.1.2`
- Tagger: `henry <henry@example.com>`
- Tag target commit: `1238fdb5b8ab17b3ef5b25dd4e58dfcc1f8e45a1`
- Target commit message: `Document v0.1.2 release sync readiness`
- Remote push: `v0.1.2-demo-stabilized -> v0.1.2-demo-stabilized`

원격 확인:

- `git ls-remote --tags origin v0.1.2-demo-stabilized`: PASS

## GitHub Release 정보

- Release title: `BreadGo Demo Stabilized Release v0.1.2`
- Tag: `v0.1.2-demo-stabilized`
- Target branch: `main`
- Release body source: `docs/release-note-v0.1.2.md`

## GitHub Release 생성 여부

GitHub CLI `gh`가 현재 환경에 설치되어 있지 않아 CLI로 Release를 생성하지 않았다.

확인 결과:

- `gh --version`: command not found
- `gh auth status`: command not found
- GitHub Release 생성: 미수행

## GitHub 웹 UI 등록 입력값

`gh` CLI를 사용할 수 없는 환경에서는 GitHub 웹 UI에서 아래 값으로 등록한다.

1. GitHub repository 접속
2. `Releases` 메뉴 이동
3. `Draft a new release` 클릭
4. Tag 선택: `v0.1.2-demo-stabilized`
5. Target: `main`
6. Release title 입력: `BreadGo Demo Stabilized Release v0.1.2`
7. Release body: `docs/release-note-v0.1.2.md` 내용 복사/붙여넣기
8. 실제 내용 확인 후 `Publish release` 클릭

주의:

- 기존 `v0.1.1-demo-ready` Release는 변경하지 않는다.
- 기존 `v0.1.2-demo-published` tag는 삭제/이동하지 않는다.
- 실제 외부 API 연동, 실제 결제, 실제 알림 발송을 추가하지 않는다.

## 검증 결과

- `git status`: clean
- `git branch --show-current`: `main`
- `git status -sb`: `## main...origin/main`
- `git log --oneline -5`: 최신 커밋 `1238fdb Document v0.1.2 release sync readiness` 확인
- `git tag --list`: `v0.1.2-demo-stabilized` 포함 확인
- `git show v0.1.2-demo-stabilized --no-patch`: annotated tag 및 target commit 확인
- `git push origin v0.1.2-demo-stabilized`: PASS
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS (`SCHEDULED` 동일 기간 중복 실행 방지로 `SKIPPED`)
- `python scripts/run_pro_health_alert_check.py`: PASS (`WARNING`, 기존 health alert 중복 skip)
- `npm run lint`: PASS
- `npm run build`: PASS

## 변경 여부

- 기능 코드 변경: 없음
- DB schema 변경: 없음
- migration 추가: 없음
- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송 추가: 없음
- 외부 발송 API 연동 추가: 없음

## 남은 작업

- GitHub 웹 UI 또는 gh CLI가 있는 환경에서 Release 생성
- Release 생성 후 URL 확인
- Release page에서 title/tag/body가 의도대로 표시되는지 확인

## Suggested commit message

`Document v0.1.2 release creation`
