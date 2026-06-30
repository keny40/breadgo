# Release Create Phase 139

## 목적

Phase 139는 v0.1.4 Release Candidate 문서를 기준으로 공식 tag를 생성하고 origin에 push한 뒤, GitHub 웹 UI에서 Release를 등록할 수 있도록 준비 상태를 정리하는 단계다.

이번 Phase에서는 GitHub Release를 자동 생성하지 않았고, 기능 코드 / DB schema / migration을 변경하지 않았다.

## Release 대상

- Tag: `v0.1.4-readiness-ux-boundary`
- Release title: `BreadGo Readiness UX Boundary Release v0.1.4`
- Release body source: `docs/release-note-v0.1.4.md`
- Target branch: `main`

## 사전 확인

- branch: `main`
- origin/main 동기화: 확인 완료
- working tree: clean에서 시작
- 기존 tag 삭제/이동: 없음
- 현재 공식 최신 Release: `v0.1.3-adapter-readiness` 유지

## 생성한 tag

- tag: `v0.1.4-readiness-ux-boundary`
- tag type: annotated tag
- tag message: `BreadGo Readiness UX Boundary Release v0.1.4`
- tag 대상 커밋: `57bf08a26cb698c7f0088bbae5de9b5d9eef8eb9`
- 대상 커밋 메시지: `Prepare v0.1.4 release candidate docs`

## Tag push 결과

- `git push origin v0.1.4-readiness-ux-boundary`: PASS
- `git ls-remote --tags origin v0.1.4-readiness-ux-boundary`: PASS

원격 tag 확인:

```text
refs/tags/v0.1.4-readiness-ux-boundary
```

## GitHub Release 생성 여부

GitHub Release는 자동 생성하지 않았다.

사유:

- `gh` CLI가 설치되어 있지 않음
- `gh --version` / `gh auth status` 실행 시 command not found

따라서 GitHub 웹 UI에서 수동 등록이 필요하다. 이는 실패가 아니라 수동 등록 필요 상태다.

## GitHub 웹 UI 등록 입력값

GitHub repository에서 Releases 화면으로 이동한 뒤 아래 값으로 등록한다.

- Tag: `v0.1.4-readiness-ux-boundary`
- Target: `main`
- Release title: `BreadGo Readiness UX Boundary Release v0.1.4`
- Release body: `docs/release-note-v0.1.4.md` 내용 복사
- Draft: 필요 시 선택, 최종 공개 시 해제
- Prerelease: 일반 공개 release로 등록하려면 해제

웹 UI 절차:

1. GitHub repository 접속
2. `Releases` 이동
3. `Draft a new release` 클릭
4. tag `v0.1.4-readiness-ux-boundary` 선택
5. target `main` 확인
6. title 입력
7. `docs/release-note-v0.1.4.md` 내용 붙여넣기
8. `Publish release` 클릭

## 검증 결과

- `git status`: PASS, clean에서 시작
- `git branch --show-current`: PASS, `main`
- `git log --oneline -5`: PASS
- `git tag --list`: PASS
- `git show v0.1.4-readiness-ux-boundary --no-patch`: PASS
- `git ls-remote --tags origin v0.1.4-readiness-ux-boundary`: PASS
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS
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

## API Key / Secret / Token / Webhook URL 추가 여부

추가하지 않았다.

- API key 추가 없음
- secret 추가 없음
- token 추가 없음
- webhook URL 추가 없음
- `.env.example` 변경 없음

## 남은 작업

- GitHub 웹 UI에서 v0.1.4 Release 등록
- 등록 후 Release URL, title, tag, Latest 표시 확인
- `docs/post-release-verification-v0.1.4.md` 기준 post-release verification 수행

## Suggested commit message

`Document v0.1.4 release tag prep`

