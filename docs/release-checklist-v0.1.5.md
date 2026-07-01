# Release Checklist v0.1.5

## 목적

`v0.1.5` Release 생성 전에 Google OAuth live 연동, 회원가입 역할 분리, 가맹점 입점 신청, role 기반 redirect/navigation 범위와 검증 결과를 확인한다.

현재 공식 최신 Release는 `v0.1.4-readiness-ux-boundary`이며, v0.1.5는 아직 Release Candidate 준비 단계다.

## Release 후보 정보

- 추천 tag: `v0.1.5-google-oauth-role-onboarding`
- 추천 Release title: `BreadGo Google OAuth Role Onboarding Release v0.1.5`
- Release body source: `docs/release-note-v0.1.5.md`
- Target branch: `main`

## Working Tree / Branch 확인

Release 생성 전 확인:

```powershell
git status
git branch --show-current
git status -sb
git log --oneline -10
git tag --list
```

기준:

- branch는 `main`
- working tree는 clean
- origin/main 동기화 상태 확인
- 기존 tag 삭제/이동 없음
- v0.1.5 tag는 생성 전

## 전체 검증 명령어

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

## 기능 범위 확인

포함:

- Google OAuth customer login/signup live verification
- Render backend `/api/v1/auth/google/status` `enabled=true` 확인
- Google 실제 로그인 성공 확인
- customer/merchant/admin 공개 가입 정책 분리
- merchant application create/list/detail/approve/reject
- `role=merchant` / `role=admin` 공개 가입 차단
- Google OAuth customer-only 정책 유지
- role 기반 redirect와 NavBar role 분기
- production 데이터 기준 `merchant3@breadgo.test` 설명

제외:

- admin Google signup
- merchant Google auto signup
- Google token DB 저장
- Google Client Secret 문서화
- 실제 결제/배송/POS/외부 알림 신규 연동
- 새 tag 생성
- GitHub Release 생성
- DB schema 추가 변경
- 추가 migration

## OAuth 설정 확인

확인 기준:

- Frontend URL: `https://breadgo.vercel.app`
- Backend API: `https://breadgo-api.onrender.com`
- Google status endpoint: `https://breadgo-api.onrender.com/api/v1/auth/google/status`
- Redirect URI: `https://breadgo-api.onrender.com/api/v1/auth/google/callback`
- Render backend에 OAuth client id/secret이 환경변수로 설정되어 있음
- `GOOGLE_CLIENT_SECRET` 값은 repository에 없음
- token/secret/key는 로그/문서/코드에 남기지 않음

## Role / Access 확인

Release 생성 전 확인:

- customer login -> `/products`
- merchant login -> `/merchant`
- admin login -> `/admin`
- Google customer login -> customer flow
- customer nav: 상품 보기, 내 예약, 내 결제
- merchant nav: 가맹점 홈, 상품관리, 주문관리, 픽업, POS, 재고 이력
- admin nav: Admin, 운영 점검, Pro 운영, Batch Monitor
- customer의 merchant 관리 화면 접근 차단 또는 안내
- merchant의 admin 화면 접근 차단
- 승인 전 merchant 신청자는 관리 화면 접근 불가

## Merchant Application 확인

- `/merchant/apply` 화면 정상
- `POST /api/v1/merchants/apply` 정상
- admin 신청 목록 조회 정상
- admin 신청 상세 조회 정상
- admin 승인 정상
- admin 반려 정상
- 승인 전 신청자는 merchant 권한 없음
- 승인 후 merchant 계정 또는 merchant profile 활성화

## DB / Migration 확인

Phase 145 migration:

- `202606180024_create_merchant_applications.py`

v0.1.5 RC 문서 준비 기준:

- 추가 DB schema 변경 없음
- 추가 migration 없음
- 기존 migration head 정상 적용

## Secret / Token 확인

- `GOOGLE_CLIENT_SECRET` 값 미노출
- Google access token / refresh token / id token DB 저장 없음
- API key / secret / token / webhook URL 추가 없음
- README/docs/test fixture/log에 민감값 없음

## Tag 생성 전 확인 항목

- 전체 검증 PASS
- README에 v0.1.5 RC 문서 링크 반영
- release note / checklist / post-release verification 문서 존재
- role redirect/navigation fix가 배포 전 main에 포함됨
- 기존 `v0.1.4-readiness-ux-boundary` Release 유지
- 기존 `v0.1.2-demo-published` 임시 tag 삭제/이동 없음
- tag 이름 확정: `v0.1.5-google-oauth-role-onboarding`
- annotated tag 사용 권장

예상 tag 명령:

```powershell
git tag -a v0.1.5-google-oauth-role-onboarding -m "BreadGo Google OAuth Role Onboarding Release v0.1.5"
git push origin v0.1.5-google-oauth-role-onboarding
```

## GitHub 웹 UI 등록 입력값

- Tag: `v0.1.5-google-oauth-role-onboarding`
- Target: `main`
- Release title: `BreadGo Google OAuth Role Onboarding Release v0.1.5`
- Release body: `docs/release-note-v0.1.5.md` 내용
- Draft: 상황에 맞게 선택
- Prerelease: 보통 false

## GitHub CLI 예시

`gh` CLI가 설치/인증되어 있을 때만 실행한다.

```powershell
gh release create v0.1.5-google-oauth-role-onboarding `
  --title "BreadGo Google OAuth Role Onboarding Release v0.1.5" `
  --notes-file docs/release-note-v0.1.5.md
```

## Release Gate

Release 생성 전 아래가 모두 충족되어야 한다.

- 전체 검증 PASS
- DB/migration 추가 변경 없음
- Google OAuth customer-only 정책 확인
- merchant/admin 자동 가입 차단 확인
- role direct assignment 차단 확인
- token/secret/key 미노출
- push 완료 후 원격 README/docs 확인

## Suggested commit message

`Prepare v0.1.5 release candidate docs`
