# Release Checklist v0.1.4

## 목적

`v0.1.4` Release 생성 전에 readiness / UX / credential boundary 범위, 검증 결과, tag / GitHub Release 준비 상태를 확인한다.

현재 공식 최신 Release는 `v0.1.3-adapter-readiness`이며, v0.1.4는 아직 Release Candidate 준비 단계다.

## Release 후보 정보

- 추천 tag: `v0.1.4-readiness-ux-boundary`
- 추천 Release title: `BreadGo Readiness UX Boundary Release v0.1.4`
- Release body source: `docs/release-note-v0.1.4.md`
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
- 새 tag 생성 전 기존 tag 확인

## 전체 검증 명령어

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

## 기능 범위 확인

포함:

- Provider adapter unit tests
- Adapter readiness admin UI 상세화
- POS / CSV import UX 고도화
- Merchant inventory ledger report 개선
- Credential boundary 설계 문서
- v0.1.4 release note / checklist / post-release verification template

제외:

- 실제 PG 승인 / 환불
- 실제 배송 접수 / 추적
- 실제 POS API 호출
- 실제 이메일 / 카카오 / Push / Slack / Discord / Webhook 발송
- API key / secret / token / webhook URL 추가
- DB schema 변경
- migration 추가
- credential 저장 table 추가

## Credential Boundary 확인

- 실제 credential이 repository에 추가되지 않았는지 확인
- `.env.example`에 실제 값이나 실제처럼 보이는 secret이 추가되지 않았는지 확인
- Release note와 README에 실제 secret이 포함되지 않았는지 확인
- 로그/audit/CSV export에 secret을 포함하지 않는 원칙 유지

## 실제 외부 API 호출 없음 확인

확인 기준:

- readiness 결과는 `external_calls_enabled=false`
- smoke test와 unit test가 mock/noop 기준으로 통과
- 실제 provider API 호출 코드 path가 feature flag 없이 실행되지 않음
- API key / secret / token / webhook URL 추가 없음

## DB / Migration 확인

확인 기준:

- 신규 migration 없음
- DB schema 변경 없음
- credential 저장 table 없음
- 실제 provider token 저장 없음

## Tag 생성 전 확인 항목

- `git status` clean
- `main` branch
- origin/main에 v0.1.4 RC 문서와 코드가 push되어 있음
- 기존 `v0.1.3-adapter-readiness` Release 유지
- 기존 `v0.1.2-demo-published` 임시 tag 삭제/이동 없음
- tag 이름 확정: `v0.1.4-readiness-ux-boundary`
- annotated tag 사용 권장

예상 tag 명령:

```powershell
git tag -a v0.1.4-readiness-ux-boundary -m "BreadGo Readiness UX Boundary Release v0.1.4"
git push origin v0.1.4-readiness-ux-boundary
```

## GitHub 웹 UI 등록 입력값

- Tag: `v0.1.4-readiness-ux-boundary`
- Target: `main`
- Release title: `BreadGo Readiness UX Boundary Release v0.1.4`
- Release body: `docs/release-note-v0.1.4.md` 내용
- Draft: 상황에 맞게 선택
- Prerelease: 보통 false

## GitHub CLI 예시

`gh` CLI가 설치/인증되어 있을 때만 실행한다.

```powershell
gh release create v0.1.4-readiness-ux-boundary `
  --title "BreadGo Readiness UX Boundary Release v0.1.4" `
  --notes-file docs/release-note-v0.1.4.md
```

## Release Gate

Release 생성 전 아래가 모두 충족되어야 한다.

- 전체 검증 PASS
- DB/migration 변경 없음
- 실제 외부 API 호출 없음
- credential 값 추가 없음
- README에 v0.1.4 문서 링크 반영
- release note / checklist / post-release verification 문서 존재
- push 완료 후 원격 문서 확인

## 현재 Phase 138 확인 결과

- `git status`: clean에서 시작, RC 문서/README 변경만 추가
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## Suggested commit message

`Prepare v0.1.4 release candidate docs`

