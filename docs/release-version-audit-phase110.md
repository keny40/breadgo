# Phase 110 Release Version Audit

## 목적

다음 릴리스 또는 다음 개발 단계로 넘어가기 전에 현재 저장소의 `v0.1.1-demo-ready` Release와 `v0.1.2-demo-published` tag 상태를 점검했다.

이번 Phase는 버전/태그/릴리스 상태 정리 문서화 중심이며 기능 코드, DB schema, migration은 변경하지 않았다.

## 로컬 상태

- 현재 브랜치: `main`
- 작업트리: clean 상태에서 점검 시작
- 새 tag 생성 없음
- 기존 tag 삭제/이동 없음
- 새 GitHub Release 생성 없음

## 존재하는 tag 목록

```text
v0.1.0-local-demo
v0.1.0-mvp
v0.1.1-demo-ready
v0.1.2-demo-published
```

## 최근 커밋 / tag 위치

`git log --oneline --decorate -10` 기준:

```text
48c596f (HEAD -> main, origin/main) Document v0.1.1 release push verification
08dce40 Document v0.1.1 release verification
e2fbbcd Document published GitHub release link
083c114 Finalize v0.1.1 release note
cc1baa3 (tag: v0.1.2-demo-published) Document GitHub release publication
c6613c6 Document GitHub demo release draft
f62363d Document demo release handoff
60da18d (tag: v0.1.1-demo-ready) Document final demo run-through
a7bc810 (tag: v0.1.0-mvp) Prepare final MVP release package
e7c3de0 Add missing Pro audit trail files
```

## v0.1.2-demo-published tag 상태

- Tag name: `v0.1.2-demo-published`
- Tag object: `68d1b77c830fea215e1e1e93b4d7d0639dae43ad`
- Tag subject: `BreadGo MVP demo published package`
- Tagger date: `2026-06-27 17:55:15 +0900`
- Target commit: `cc1baa34953ca7cab38046ee491cd67a6fa6ac52`
- Target commit subject: `Document GitHub release publication`

`v0.1.2-demo-published`는 annotated tag이며, 기능 릴리스 커밋이 아니라 GitHub Release publication 문서화 커밋을 가리킨다.

## v0.1.1-demo-ready tag / Release 상태

- Tag name: `v0.1.1-demo-ready`
- Tag object: `12ee80ea198bc32a0d924b56b0e983a80b141ac7`
- Tag subject: `BreadGo MVP demo-ready release`
- Tagger date: `2026-06-27 17:25:41 +0900`
- Target commit: `60da18d62ac7d5f5e9104b78b85c92c1308572ab`
- Target commit subject: `Document final demo run-through`
- GitHub Release: 존재함
- Release title: `BreadGo MVP Demo Ready Release v0.1.1`
- Release URL: `https://github.com/keny40/breadgo/releases/tag/v0.1.1-demo-ready`
- Target branch: `main`
- Draft: `false`
- Prerelease: `false`

GitHub API `releases/tags/v0.1.1-demo-ready` 조회 결과 정상 Release로 확인되었다.

## GitHub Releases 목록 확인

GitHub Releases API 기준 현재 등록된 Release는 아래 1건이다.

```text
v0.1.1-demo-ready | BreadGo MVP Demo Ready Release v0.1.1
```

`v0.1.2-demo-published`에 대한 GitHub Release 조회 결과:

```text
HTTP 404
```

따라서 `v0.1.2-demo-published`는 로컬/원격 tag일 수는 있으나 GitHub Release로 등록된 상태는 아니다.

## v0.1.1 Release와 v0.1.2 tag 관계

- `v0.1.1-demo-ready`는 실제 GitHub Release가 연결된 데모 릴리스 tag다.
- `v0.1.2-demo-published`는 `v0.1.1-demo-ready` 이후의 문서화 커밋 `cc1baa3`에 붙은 tag다.
- `v0.1.1-demo-ready..v0.1.2-demo-published` 사이에는 release handoff / GitHub release draft / publication 관련 문서 커밋이 포함된다.
- `v0.1.2-demo-published` 이후에도 v0.1.1 release verification, release link, release note, push verification 문서 커밋이 추가되어 현재 `main`은 `v0.1.2-demo-published`보다 앞서 있다.

## v0.1.2 실제 릴리스 여부 판단

판단: `v0.1.2-demo-published`는 실제 GitHub Release용 버전이라기보다 release publication 과정에서 만들어진 문서/운영 상태 tag로 보는 것이 안전하다.

판단 근거:

- GitHub Releases 목록에 `v0.1.2-demo-published` Release가 없다.
- GitHub API `releases/tags/v0.1.2-demo-published`가 `HTTP 404`를 반환했다.
- tag 대상 커밋이 기능 릴리스나 배포 단위가 아니라 `Document GitHub release publication` 문서화 커밋이다.
- 현재 공식 데모 Release는 `v0.1.1-demo-ready`로 등록되어 있고 Release title도 `BreadGo MVP Demo Ready Release v0.1.1`로 정리되어 있다.
- 현재 `main`은 `v0.1.2-demo-published`보다 이후의 v0.1.1 검증 문서 커밋까지 포함한다.

권장:

- 다음 실제 릴리스 전까지 `v0.1.1-demo-ready`를 공식 데모 Release 기준으로 유지한다.
- `v0.1.2-demo-published`는 삭제/이동하지 않고, 임시 또는 문서성 tag로 기록만 남긴다.
- 다음 릴리스가 필요할 때는 기능/문서 범위를 새로 정의한 뒤 별도 tag와 GitHub Release를 명확히 생성한다.

## 검증 결과

- `git status`: PASS
- `git branch --show-current`: PASS
  - `main`
- `git tag --list`: PASS
- `git log --oneline --decorate -10`: PASS
- `python -m compileall app scripts`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## DB / 기능 코드 / migration 변경 여부

- 기능 코드 변경 없음
- DB schema 변경 없음
- migration 추가 없음

## 남은 한계

- `v0.1.2-demo-published` tag 자체는 남아 있으므로, 향후 release history를 볼 때 공식 GitHub Release가 아닌 tag임을 문서로 구분해야 한다.
- `gh` CLI가 설치되어 있지 않아 GitHub Release 확인은 REST API와 공개 URL 기준으로 수행했다.
- 다음 실제 릴리스 전에는 tag naming과 Release naming 규칙을 먼저 확정하는 것이 좋다.

## Suggested commit message

`Document v0.1.2 release version audit`
