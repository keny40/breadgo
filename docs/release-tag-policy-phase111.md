# Phase 111 Release / Tag Policy

## 목적

`v0.1.2-demo-published` tag 처리 방침을 정리하고, 다음 개발 단계부터 사용할 Release / tag 관리 기준을 문서화한다.

이번 Phase는 운영 방침 문서화 중심이며 기능 코드, DB schema, migration은 변경하지 않는다.

## 현재 공식 Release 기준

공식 공개 데모 Release 기준은 아래로 유지한다.

- Official release tag: `v0.1.1-demo-ready`
- GitHub Release URL: `https://github.com/keny40/breadgo/releases/tag/v0.1.1-demo-ready`
- Release title: `BreadGo MVP Demo Ready Release v0.1.1`

`v0.1.1-demo-ready`는 GitHub Release가 실제로 등록되어 있고, README의 공식 데모 Release 링크도 이 tag를 가리킨다.

## v0.1.2-demo-published 처리 방침

`v0.1.2-demo-published`는 현재 GitHub Release가 없는 문서성/임시 tag로 분류한다.

운영 방침:

- 삭제하지 않는다.
- 이동하지 않는다.
- 새 Release로 승격하지 않는다.
- 공식 공개 데모 Release 기준으로 사용하지 않는다.
- 다음 릴리스에서 혼동되지 않도록 문서에서만 상태를 명확히 기록한다.

분류 근거:

- GitHub Releases API 기준 `v0.1.2-demo-published` Release가 없다.
- tag 대상 커밋은 기능 릴리스가 아니라 `Document GitHub release publication` 문서화 커밋이다.
- 공식 GitHub Release는 `v0.1.1-demo-ready`로 존재한다.
- 현재 `main`은 `v0.1.2-demo-published` 이후의 v0.1.1 검증/README 반영 문서 커밋을 포함한다.

## Tag 유형 구분

앞으로 tag는 아래 세 가지 유형으로 구분한다.

## 1. 실제 Release용 tag

실제 GitHub Release와 연결할 tag다.

사용 기준:

- 배포 또는 데모 기준점을 명확히 고정해야 할 때만 생성한다.
- GitHub Release를 함께 생성한다.
- README / release note / release checklist와 연결한다.
- 기능 범위, 검증 결과, known limitations가 문서화되어 있어야 한다.

권장 형식:

```text
vX.Y.Z
vX.Y.Z-demo-ready
vX.Y.Z-beta
```

예시:

```text
v0.1.1-demo-ready
```

필수 확인:

- tag 대상 commit이 실제 release 기준점인지 확인
- `git status` clean 확인
- `git tag --list` 확인
- GitHub Release 생성 여부 확인
- Release title / body / target branch 확인
- README release link 확인

## 2. 내부 문서/점검용 tag

내부 상태 기록이나 점검 기준점이 필요할 때 사용할 수 있으나, 가능하면 GitHub Release와 혼동되지 않게 이름을 붙인다.

사용 기준:

- 외부 공개 release가 아닌 내부 검토/운영 점검 기준점인 경우
- release note나 GitHub Release를 만들지 않을 경우
- 문서에 tag 목적을 반드시 기록할 경우

권장 형식:

```text
internal/vX.Y.Z-note
checkpoint/YYYYMMDD-short-name
```

주의:

- `vX.Y.Z-demo-published`처럼 실제 release처럼 보이는 이름은 지양한다.
- 내부 tag라도 원격에 push하기 전 목적을 문서화한다.
- GitHub Release가 없다는 점을 release audit 문서에 남긴다.

## 3. 임시 tag

임시 tag는 가능한 사용하지 않는다.

지양 이유:

- GitHub Release와 혼동될 수 있다.
- 버전 히스토리에서 공식 release처럼 보일 수 있다.
- 나중에 삭제/이동이 어려워진다.

부득이하게 사용할 경우:

- 로컬에서만 사용한다.
- 원격에 push하지 않는다.
- 이름에 `tmp/` 또는 `local/` prefix를 붙인다.

예시:

```text
tmp/demo-check-20260629
local/smoke-test-point
```

## 다음 릴리스 전 체크리스트

다음 실제 release tag를 만들기 전에 아래를 확인한다.

- 이번 release가 실제 GitHub Release로 공개될 대상인지 확인
- tag 이름이 공식 release인지 내부 checkpoint인지 명확한지 확인
- 기능 범위와 문서 범위가 release note에 정리되어 있는지 확인
- DB migration 여부가 release check에 기록되어 있는지 확인
- mock / 미연동 항목이 명확히 기록되어 있는지 확인
- `git status`가 clean인지 확인
- `git log --oneline --decorate -10`으로 기존 tag와의 관계 확인
- tag 생성 후 GitHub Release를 만들지 여부를 즉시 결정
- Release 등록 후 README와 post-release verification 문서를 갱신

## 금지 / 주의사항

- 기존 tag 삭제 금지
- 기존 tag 이동 금지
- release처럼 보이는 임시 tag 원격 push 지양
- 기능 release가 아닌 문서 커밋에 `vX.Y.Z` 공식 tag를 붙이지 않기
- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송 여부를 tag 이름만으로 암시하지 않기

## Phase 111 결정

- `v0.1.1-demo-ready`를 공식 공개 데모 Release 기준으로 유지한다.
- `v0.1.2-demo-published`는 문서성/임시 tag로 분류한다.
- `v0.1.2-demo-published`를 삭제하거나 이동하지 않는다.
- `v0.1.2-demo-published`에 새 GitHub Release를 만들지 않는다.
- 다음 실제 release는 별도 범위 정의 후 새 tag와 GitHub Release를 명확히 생성한다.

## 검증 결과

- `git status`: PASS
- `git tag --list`: PASS
- `python -m compileall app scripts`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## DB / 기능 코드 / migration 변경 여부

- 기능 코드 변경 없음
- DB schema 변경 없음
- migration 추가 없음

## Suggested commit message

`Document release tag policy`
