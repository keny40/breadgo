# Post-release Verification v0.1.3

## 목적

`v0.1.3` GitHub Release 생성 후 tag, Release 본문, README 링크, adapter readiness 검증 상태가 정상적으로 공개되었는지 확인한다.

현재 문서는 템플릿이며, Phase 130 기준으로 v0.1.3 Release는 아직 생성 전이다.

## Release 정보

- 권장 tag: `v0.1.3-adapter-readiness`
- 추천 Release title: `BreadGo Adapter Readiness Release v0.1.3`
- Release body source: `docs/release-note-v0.1.3.md`
- Target branch: `main`
- 현재 공식 최신 Release: `v0.1.2-demo-stabilized`
- `v0.1.2-demo-published`: GitHub Release 없는 문서성/임시 tag로 유지

## 확인 체크리스트

### GitHub Release

- [ ] Release URL 접속 가능
- [ ] tag가 `v0.1.3-adapter-readiness`로 표시됨
- [ ] title이 `BreadGo Adapter Readiness Release v0.1.3`와 일치함
- [ ] target branch가 `main` 기준임
- [ ] Latest 표시 여부 확인
- [ ] Release body가 `docs/release-note-v0.1.3.md`와 일치함
- [ ] Mock/Noop 및 `external_calls_enabled=false` 원칙이 본문에 명확히 표시됨

### 기존 Release / Tag 관계

- [ ] `v0.1.2-demo-stabilized` Release가 유지됨
- [ ] `v0.1.1-demo-ready` 이전 공식 데모 Release가 유지됨
- [ ] `v0.1.2-demo-published` tag는 삭제/이동되지 않음
- [ ] 기존 tag 또는 Release가 의도치 않게 수정되지 않음

### README / Docs

- [ ] README에서 v0.1.3 release note 링크가 열림
- [ ] README에서 v0.1.3 release checklist 링크가 열림
- [ ] README에서 Phase 130 RC check 링크가 열림
- [ ] 원격 repository에서 아래 문서가 보임:
  - `docs/release-note-v0.1.3.md`
  - `docs/release-checklist-v0.1.3.md`
  - `docs/post-release-verification-v0.1.3.md`
  - `docs/release-candidate-check-phase130.md`

## 재검증 명령어

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

Git:

```powershell
git status
git branch --show-current
git tag --list
git show v0.1.3-adapter-readiness --no-patch
```

## Adapter Readiness 확인

- [ ] Payment adapter readiness PASS
- [ ] Delivery adapter readiness PASS
- [ ] Notification adapter readiness PASS
- [ ] POS adapter readiness PASS
- [ ] Admin external integration readiness API 조회 PASS
- [ ] merchant 권한으로 Admin readiness API 접근 시 403
- [ ] 모든 provider 응답에 `external_calls_enabled=false` 또는 동등한 값 표시
- [ ] 실제 PG / 배송 / POS / 외부 알림 API 호출 없음

## 기능 코드 / DB / Migration 확인

- 기능 코드 변경 여부: Release 생성 과정에서는 없음
- DB schema 변경 여부: 없음
- migration 추가 여부: 없음
- 실제 외부 API 호출 여부: 없음
- API key / secret / token / webhook URL 추가 여부: 없음

## 실패 시 확인 위치

- adapter readiness smoke 실패: `backend/scripts/smoke_test.py`
- provider skeleton 상태: `backend/app/services/*_provider*`
- Admin readiness API: `backend/app/api/v1/admin.py`
- Admin dashboard card: `frontend/app/admin/page.tsx`
- 운영 troubleshooting: `docs/operations-troubleshooting-guide.md`

