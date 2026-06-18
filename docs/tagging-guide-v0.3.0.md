# BreadGo v0.3.0 태그 생성 가이드

## 목적

이 문서는 BreadGo v0.3.0 Demo Release 태그와 GitHub Release를 준비하는 절차입니다.
이 문서는 안내용이며, 실제 태그 생성이나 push는 자동으로 수행하지 않습니다.

## 태그 생성 전 확인할 것

1. 로컬 작업 트리가 의도한 변경만 포함하는지 확인
2. README와 릴리즈 문서가 최신인지 확인
3. 검증 명령이 통과했는지 확인
4. 실제 secret 값이 문서나 Git에 포함되지 않았는지 확인
5. 운영 URL smoke result 문서가 최신인지 확인
6. main branch가 원격 최신 상태인지 확인

## Git 상태 확인

```powershell
git status
git branch --show-current
git log --oneline -5
```

## main 최신화 확인

```powershell
git fetch origin
git status
git log --oneline origin/main..HEAD
git log --oneline HEAD..origin/main
```

두 비교 명령으로 로컬과 원격 차이를 확인합니다.

## 권장 커밋

Phase 48 문서 작업 커밋 예시:

```powershell
git add README.md CHANGELOG.md docs/release-note-v0.3.0.md docs/github-release-v0.3.0.md docs/tagging-guide-v0.3.0.md docs/release-check-phase48.md
git commit -m "Prepare v0.3.0 demo release notes"
```

## 태그 생성 명령

권장 태그명:

```text
v0.3.0-demo
```

태그 생성:

```powershell
git tag -a v0.3.0-demo -m "BreadGo v0.3.0 Demo Release"
```

태그 확인:

```powershell
git tag --list
git show v0.3.0-demo
```

## 태그 push 명령

```powershell
git push origin main
git push origin v0.3.0-demo
```

## GitHub Release 작성 순서

1. GitHub repository로 이동
2. Releases 메뉴 선택
3. Draft a new release 선택
4. Tag에서 `v0.3.0-demo` 선택
5. Release title 입력

```text
BreadGo v0.3.0 Demo Release
```

6. Release body에 다음 문서 내용을 붙여넣기

```text
docs/github-release-v0.3.0.md
```

7. 링크와 데모 계정이 올바른지 확인
8. 실제 secret 값이 포함되지 않았는지 확인
9. Publish release 선택

## 주의사항

- 실제 태그 생성은 검증과 리뷰가 끝난 뒤 수동으로 수행합니다.
- GitHub Release에 실제 환경 변수 값이나 secret을 넣지 않습니다.
- 운영 URL smoke test를 한 번 더 수행한 뒤 릴리즈하는 것을 권장합니다.
