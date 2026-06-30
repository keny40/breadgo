# Post-release Verification v0.1.4

## 목적

`v0.1.4` GitHub Release 생성 후 tag, Release 본문, README 링크, credential boundary 원칙, readiness/UX 검증 상태가 정상적으로 공개되었는지 확인한다.

현재 문서는 템플릿이며, Phase 138 기준으로 v0.1.4 Release는 아직 생성 전이다.

## Release 정보

- 권장 tag: `v0.1.4-readiness-ux-boundary`
- 추천 Release title: `BreadGo Readiness UX Boundary Release v0.1.4`
- Release body source: `docs/release-note-v0.1.4.md`
- Target branch: `main`
- 현재 공식 최신 Release: `v0.1.3-adapter-readiness`

## 확인 체크리스트

### GitHub Release

- [ ] Release URL 접속 가능
- [ ] tag가 `v0.1.4-readiness-ux-boundary`로 표시됨
- [ ] title이 `BreadGo Readiness UX Boundary Release v0.1.4`와 일치함
- [ ] target branch가 `main` 기준임
- [ ] Latest 표시 여부 확인
- [ ] Release body가 `docs/release-note-v0.1.4.md`와 일치함
- [ ] 실제 외부 API 미호출과 credential 미추가 원칙이 본문에 명확히 표시됨

### 기존 Release / Tag 관계

- [ ] `v0.1.3-adapter-readiness` Release가 이전 공식 Release로 유지됨
- [ ] `v0.1.2-demo-stabilized` Release가 유지됨
- [ ] `v0.1.2-demo-published` tag는 삭제/이동되지 않음
- [ ] 기존 tag 또는 Release가 의도치 않게 수정되지 않음

### README / Docs

- [ ] README에서 v0.1.4 release note 링크가 열림
- [ ] README에서 v0.1.4 release checklist 링크가 열림
- [ ] README에서 credential boundary 문서 링크가 열림
- [ ] 원격 repository에서 아래 문서가 보임:
  - `docs/credential-boundary-phase138.md`
  - `docs/release-note-v0.1.4.md`
  - `docs/release-checklist-v0.1.4.md`
  - `docs/post-release-verification-v0.1.4.md`

## 재검증 명령어

Backend:

```powershell
cd backend
python -m compileall app scripts
python scripts/seed_demo.py
python scripts/smoke_test.py
python -m pytest tests -q
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

Git:

```powershell
git status
git branch --show-current
git tag --list
git show v0.1.4-readiness-ux-boundary --no-patch
```

## Credential Boundary 확인

- [ ] 실제 API key / secret / token / webhook URL이 repository에 추가되지 않음
- [ ] `.env.example`에 실제 값 또는 실제처럼 보이는 secret이 없음
- [ ] Release body에 credential 값이 없음
- [ ] DB schema / migration 변경 없음
- [ ] 실제 외부 provider 호출 없음

## 기능 코드 / DB / Migration 확인

- 기능 코드 변경 여부: Release 생성 과정에서는 없음
- DB schema 변경 여부: 없음
- migration 추가 여부: 없음
- actual credential 추가 여부: 없음

## 실패 시 확인 위치

- v0.1.4 범위: `docs/v0.1.4-scope-candidate-phase134.md`
- credential boundary: `docs/credential-boundary-phase138.md`
- Release note: `docs/release-note-v0.1.4.md`
- smoke test: `backend/scripts/smoke_test.py`
- adapter tests: `backend/tests/test_adapter_readiness.py`

