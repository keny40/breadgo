# GitHub Release Publish Guide

## 목적

`v0.1.1-demo-ready` 태그 기준으로 BreadGo MVP / BreadGo Pro 데모 릴리즈를 GitHub Releases에 등록하기 위한 운영 가이드다.

이번 문서는 GitHub Release publication 절차만 다룬다. 기능 코드, DB schema, migration, 실제 외부 발송 연동은 변경하지 않는다.

## Release 정보

- Tag: `v0.1.1-demo-ready`
- Target: `main`
- Release title: `BreadGo MVP Demo Ready Release v0.1.1`
- Release body source: `docs/github-release-v0.1.1-demo-ready.md`

## GitHub 웹 UI 등록 절차

1. GitHub repository에 접속한다.
2. 오른쪽 또는 상단의 `Releases` 메뉴로 이동한다.
3. `Draft a new release`를 클릭한다.
4. Tag에서 `v0.1.1-demo-ready`를 선택한다.
5. Target이 `main`인지 확인한다.
6. Title에 `BreadGo MVP Demo Ready Release v0.1.1`을 입력한다.
7. `docs/github-release-v0.1.1-demo-ready.md`를 열고 `Release Body` 섹션의 Markdown 본문을 복사한다.
8. GitHub Release description에 붙여넣는다.
9. 첨부할 binary artifact가 없다면 파일 업로드 없이 진행한다.
10. `Publish release`를 클릭한다.

## GitHub CLI 예시

GitHub CLI가 설치되어 있고 로그인되어 있다면 아래 명령으로 등록할 수 있다.

PowerShell 또는 Windows CMD 예시:

```bash
gh release create v0.1.1-demo-ready ^
  --title "BreadGo MVP Demo Ready Release v0.1.1" ^
  --notes-file docs/github-release-v0.1.1-demo-ready.md
```

macOS/Linux shell 예시:

```bash
gh release create v0.1.1-demo-ready \
  --title "BreadGo MVP Demo Ready Release v0.1.1" \
  --notes-file docs/github-release-v0.1.1-demo-ready.md
```

GitHub CLI가 설치되어 있지 않거나 `gh auth login`이 완료되지 않았다면 웹 UI 방식을 사용한다. 이 Phase에서는 CLI 명령을 실제로 실행하지 않는다.

## 등록 후 확인 항목

- Release title이 `BreadGo MVP Demo Ready Release v0.1.1`인지 확인한다.
- Tag가 `v0.1.1-demo-ready`에 연결되어 있는지 확인한다.
- Target branch가 `main`인지 확인한다.
- Release body의 주요 섹션이 깨지지 않았는지 확인한다.
- `README.md`, demo quickstart, release notes, handoff 문서 링크가 열리는지 확인한다.
- Mock 처리 항목과 실제 미연동 항목이 명확히 표시되는지 확인한다.
- 외부 이메일/카카오/Push/Slack/Discord/Webhook 발송이 포함된 것처럼 보이지 않는지 확인한다.

## 문제가 생겼을 때 확인할 항목

- `git tag --list`에서 `v0.1.1-demo-ready`가 보이는지 확인한다.
- GitHub 원격 repository에 해당 tag가 push되어 있는지 확인한다.
- Release body를 전체 문서가 아니라 `Release Body` 섹션 기준으로 복사했는지 확인한다.
- Markdown code fence가 닫혀 있는지 확인한다.
- GitHub CLI 사용 시 `gh auth status`로 로그인 상태를 확인한다.
- 이미 같은 tag의 release가 있으면 새 release 생성 대신 기존 release edit이 필요한지 확인한다.
- 등록 후에는 `docs/post-release-verification-v0.1.1.md` 기준으로 사후 검증을 수행한다.

## 개인정보 / 외부 발송 원칙

- Release 문서에는 이메일, 전화번호, 주소, 외부 발송 토큰을 포함하지 않는다.
- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송 기능은 포함하지 않는다.
- 외부 발송 API 연동 또는 토큰 설정 절차를 Release 문서에 포함하지 않는다.
