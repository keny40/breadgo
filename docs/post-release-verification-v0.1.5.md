# Post-release Verification v0.1.5

## 목적

`v0.1.5` GitHub Release 생성 후 tag, Release 본문, README 링크, OAuth/role/onboarding 검증 상태가 정상적으로 공개되었는지 확인한다.

현재 문서는 템플릿이며, Phase 148 기준으로 v0.1.5 Release는 아직 생성 전이다.

## Release 정보

- 권장 tag: `v0.1.5-google-oauth-role-onboarding`
- 추천 Release title: `BreadGo Google OAuth Role Onboarding Release v0.1.5`
- Release body source: `docs/release-note-v0.1.5.md`
- Target branch: `main`
- 현재 공식 최신 Release: `v0.1.4-readiness-ux-boundary`

## 확인 체크리스트

### GitHub Release

- [ ] Release URL 접속 가능
- [ ] tag가 `v0.1.5-google-oauth-role-onboarding`로 표시됨
- [ ] title이 `BreadGo Google OAuth Role Onboarding Release v0.1.5`와 일치함
- [ ] target branch가 `main` 기준임
- [ ] Latest 표시 여부 확인
- [ ] Release body가 `docs/release-note-v0.1.5.md`와 일치함
- [ ] secret/token/key 미노출 원칙이 본문에 명확히 표시됨

### 기존 Release / Tag 관계

- [ ] `v0.1.4-readiness-ux-boundary` Release가 이전 공식 Release로 유지됨
- [ ] `v0.1.3-adapter-readiness` Release가 유지됨
- [ ] `v0.1.2-demo-stabilized` Release가 유지됨
- [ ] `v0.1.2-demo-published` tag는 Release 없는 문서성/임시 tag 상태로 유지됨
- [ ] 기존 tag 또는 Release가 의도치 않게 수정되지 않음

### README / Docs

- [ ] README에서 v0.1.5 release note 링크가 열림
- [ ] README에서 v0.1.5 release checklist 링크가 열림
- [ ] README에서 v0.1.5 post-release verification 링크가 열림
- [ ] 원격 repository에서 아래 문서가 보임:
  - `docs/release-note-v0.1.5.md`
  - `docs/release-checklist-v0.1.5.md`
  - `docs/post-release-verification-v0.1.5.md`
  - `docs/release-candidate-check-phase148.md`

## Production 확인

- [ ] `https://breadgo.vercel.app/login` 접속 가능
- [ ] `/login`에서 Google로 계속하기 버튼 확인
- [ ] `https://breadgo.vercel.app/register` 접속 가능
- [ ] `/register`에서 customer signup과 merchant application CTA 확인
- [ ] `https://breadgo-api.onrender.com/api/v1/auth/google/status` 응답 `enabled=true`
- [ ] Google customer login 성공
- [ ] customer login 후 `/products`
- [ ] merchant login 후 `/merchant`
- [ ] admin login 후 `/admin`
- [ ] customer / merchant / admin role별 NavBar 확인
- [ ] `merchant3@breadgo.test`는 production role이 customer라는 설명이 문서에 남아 있음

## 재검증 명령어

Backend:

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
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
git show v0.1.5-google-oauth-role-onboarding --no-patch
```

## Security 확인

- [ ] `GOOGLE_CLIENT_SECRET` 값이 문서/코드/log/test fixture에 없음
- [ ] Google token이 DB에 저장되지 않음
- [ ] API key / secret / token / webhook URL 추가 없음
- [ ] admin/merchant Google 자동 가입 없음
- [ ] role direct assignment로 admin/merchant 생성 불가

## 기능 코드 / DB / Migration 확인

- 기능 코드 변경 여부: Release 생성 과정에서는 없음
- DB schema 변경 여부: 추가 변경 없음
- migration 추가 여부: v0.1.5 RC 문서 준비 기준 없음
- actual secret 추가 여부: 없음

## 실패 시 확인 위치

- Google OAuth signup: `docs/google-oauth-signup-phase142.md`
- Google OAuth live verification: `docs/google-oauth-live-verification-phase144.md`
- Signup role separation: `docs/signup-role-separation-phase145.md`
- Signup deployment check: `docs/signup-role-separation-deploy-check-phase146.md`
- Role based redirect/navigation: `docs/role-based-redirect-phase147.md`
- Release note: `docs/release-note-v0.1.5.md`
