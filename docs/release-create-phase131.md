# Release Create Phase 131

## 목적

Phase 131은 Phase 128~130의 v0.1.3 adapter readiness 커밋을 `origin/main`에 반영하고, 공식 v0.1.3 tag를 생성/푸시한 뒤 GitHub Release 생성 가능 여부를 확인하는 단계다.

## Push 결과

- branch: `main`
- push 대상: `origin/main`
- push 결과: PASS
- push 범위: `c9e9241..ab2a874`
- push 후 원격 README 확인: PASS
- 원격 v0.1.3 release note 확인: PASS
- 원격 v0.1.3 release checklist 확인: PASS

확인한 원격 문서:

- `README.md`
- `docs/release-note-v0.1.3.md`
- `docs/release-checklist-v0.1.3.md`

## 생성한 tag

- tag: `v0.1.3-adapter-readiness`
- tag type: annotated tag
- tag message: `BreadGo Adapter Readiness Release v0.1.3`
- tag 대상 커밋: `ab2a874f15fb53052d5e0d0b635c8943f6a47d41`
- 대상 커밋 메시지: `Prepare v0.1.3 release candidate docs`
- tag push 결과: PASS

기존 tag 처리:

- `v0.1.2-demo-stabilized`: 유지
- `v0.1.2-demo-published`: 삭제/이동 없음
- 기존 tag 삭제/이동 없음

## GitHub Release 정보

- Release title: `BreadGo Adapter Readiness Release v0.1.3`
- Release body source: `docs/release-note-v0.1.3.md`
- Target branch: `main`
- Release tag: `v0.1.3-adapter-readiness`

## GitHub Release 생성 여부

GitHub Release는 자동 생성하지 못했다.

사유:

- `gh` CLI가 설치되어 있지 않음
- `gh --version` / `gh auth status` 실행 시 `gh` command not found

따라서 GitHub 웹 UI에서 수동 등록이 필요하다.

## GitHub 웹 UI 등록 입력값

GitHub repository에서 Releases 화면으로 이동한 뒤 아래 값으로 등록한다.

- Tag: `v0.1.3-adapter-readiness`
- Target: `main`
- Release title: `BreadGo Adapter Readiness Release v0.1.3`
- Release body: `docs/release-note-v0.1.3.md` 내용 복사
- Draft: 필요 시 선택, 최종 공개 시 해제
- Prerelease: 일반 공개 release로 등록하려면 해제

웹 UI 절차:

1. GitHub repository 접속
2. `Releases` 이동
3. `Draft a new release` 클릭
4. tag `v0.1.3-adapter-readiness` 선택
5. target `main` 확인
6. title 입력
7. `docs/release-note-v0.1.3.md` 내용 붙여넣기
8. `Publish release` 클릭

## 검증 결과

- `git status`: PASS, `main` branch 확인 및 작업 상태 확인
- `git branch --show-current`: PASS, `main`
- `git status -sb`: PASS
- `git log --oneline -10`: PASS, Phase 128~130 커밋 확인
- `git push origin main`: PASS
- 원격 README 확인: PASS
- 원격 v0.1.3 release note 확인: PASS
- 원격 v0.1.3 release checklist 확인: PASS
- `git tag --list`: PASS, `v0.1.3-adapter-readiness` 생성 후 목록 확인
- `git tag -a v0.1.3-adapter-readiness -m "BreadGo Adapter Readiness Release v0.1.3"`: PASS
- `git show v0.1.3-adapter-readiness --no-patch`: PASS
- `git push origin v0.1.3-adapter-readiness`: PASS
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS, 동일 기간 완료 SCHEDULED batch 존재로 안전하게 `SKIPPED`
- `python scripts/run_pro_health_alert_check.py`: PASS, 기존 미해결 alert 중복 방지로 `generated_count=0`, `skipped_count=2`
- `npm run lint`: PASS
- `npm run build`: PASS

## 기능 코드 / DB / Migration 변경 여부

- 기능 코드 변경: 없음
- DB schema 변경: 없음
- migration 추가: 없음
- credential 저장 구조 추가: 없음

## 실제 외부 API 호출 여부

없음.

- 실제 PG API 호출 없음
- 실제 배송 provider API 호출 없음
- 실제 POS API 호출 없음
- 실제 이메일 / 카카오 / Push / Slack / Discord / Webhook 호출 없음
- API key / secret / token / webhook URL 추가 없음

## 남은 작업

- GitHub 웹 UI에서 v0.1.3 Release 등록
- 등록 후 Release URL, title, tag, Latest 표시 확인
- `docs/post-release-verification-v0.1.3.md` 기준 post-release verification 수행

## Suggested commit message

`Document v0.1.3 release creation`

