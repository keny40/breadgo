# Release Checklist v0.1.3

## 목적

`v0.1.3` Release 생성 전에 adapter readiness 범위, 검증 결과, tag / GitHub Release 준비 상태를 확인한다.

현재 공식 최신 Release는 `v0.1.2-demo-stabilized`이며, v0.1.3은 아직 Release Candidate 준비 단계다.

## Release 후보 정보

- 추천 tag: `v0.1.3-adapter-readiness`
- 대안 tag:
  - `v0.1.3-mock-integrations`
  - `v0.1.3-external-readiness`
- 추천 Release title: `BreadGo Adapter Readiness Release v0.1.3`
- Release body source: `docs/release-note-v0.1.3.md`
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
- `origin/main`과 동기화 또는 push 직전 ahead 상태 명확히 기록
- 새 tag 생성 전 기존 tag 확인
- 기존 tag 삭제/이동 없음

## 전체 검증 명령어

Backend:

```powershell
cd backend
python -m compileall app scripts
python scripts/seed_demo.py
python scripts/smoke_test.py
python scripts/run_weekly_report_batch.py
python scripts/run_pro_health_alert_check.py
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

## 기능 범위 확인

포함:

- Payment provider adapter skeleton / readiness
- Delivery provider adapter skeleton / readiness
- Notification provider adapter skeleton / readiness
- POS provider readiness
- External Integration Readiness service / schema / ADMIN read-only API
- Admin Dashboard readiness card
- smoke test adapter dry-run 검증
- 문서 / Release Note / checklist / post-release verification template

제외:

- 실제 PG 승인 / 환불
- 실제 배송 접수 / 추적
- 실제 POS API 호출
- 실제 이메일 / 카카오 / Push / Slack / Discord / Webhook 발송
- API key / secret / token / webhook URL 저장
- DB schema 변경
- migration 추가
- 대량 비동기 큐
- 실시간 AI 모델

## 실제 외부 API 호출 없음 확인

확인 기준:

- readiness API 응답의 `external_calls_enabled`가 `false`
- smoke test에서 Payment / Delivery / Notification / POS dry-run PASS
- repository에 API key / secret / token / webhook URL 추가 없음
- 외부 provider webhook 처리 없음
- `.env.example`에 실제 secret 없음

## DB / Migration 확인

확인 기준:

- 신규 migration 없음
- DB schema 변경 없음
- adapter readiness는 service/schema/API/read-only UI 중심
- 실제 credential 저장 table 없음

## Tag 생성 전 확인 항목

- `git status` clean
- `main` branch
- `origin/main`에 push 완료 여부 확인
- 기존 `v0.1.2-demo-stabilized` Release 유지 확인
- 기존 `v0.1.2-demo-published` 임시 tag 삭제/이동 없음
- tag 이름 확정: 권장 `v0.1.3-adapter-readiness`
- annotated tag 사용 권장

예상 tag 명령:

```powershell
git tag -a v0.1.3-adapter-readiness -m "BreadGo Adapter Readiness Release v0.1.3"
git push origin v0.1.3-adapter-readiness
```

## GitHub 웹 UI 등록 입력값

- Tag: `v0.1.3-adapter-readiness`
- Target: `main`
- Release title: `BreadGo Adapter Readiness Release v0.1.3`
- Release body: `docs/release-note-v0.1.3.md` 내용
- Draft: 상황에 맞게 선택
- Prerelease: 보통 false, RC 성격으로 유지하려면 true 여부 별도 결정

## GitHub CLI 예시

`gh` CLI가 설치/인증되어 있을 때만 실행한다.

```powershell
gh release create v0.1.3-adapter-readiness `
  --title "BreadGo Adapter Readiness Release v0.1.3" `
  --notes-file docs/release-note-v0.1.3.md
```

## Release Gate

Release 생성 전 아래가 모두 충족되어야 한다.

- 전체 검증 PASS
- `external_calls_enabled=false`
- DB/migration 변경 없음
- 실제 외부 API 호출 없음
- README에 v0.1.3 문서 링크 반영
- release note / checklist / post-release verification 문서 존재
- push 완료 후 원격 문서 확인

## 현재 Phase 130 확인 결과

- `git status`: clean에서 시작, RC 문서/README 변경만 추가
- `git branch --show-current`: `main`
- `git status -sb`: `main...origin/main [ahead 8]`에서 시작
- `git tag --list`: 기존 tag 확인
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS, adapter readiness smoke 포함
- `python scripts/run_weekly_report_batch.py`: PASS, 동일 기간 중복 방지로 `SKIPPED`
- `python scripts/run_pro_health_alert_check.py`: PASS, 중복 health alert 방지로 `generated_count=0`, `skipped_count=2`
- `npm run lint`: PASS
- `npm run build`: PASS

## Suggested commit message

`Prepare v0.1.3 release candidate docs`
