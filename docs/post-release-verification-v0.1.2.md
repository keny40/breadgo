# Post-release Verification v0.1.2

## 목적

향후 v0.1.2 정식 Release를 생성한 뒤 확인할 사후 검증 템플릿이다.

현재 v0.1.2는 준비 단계이며, 이 문서는 실제 Release 생성 전 템플릿이다. 새 tag나 GitHub Release를 만들지 않는다.

## Release 기본 정보

Release 생성 후 아래 값을 채운다.

- Release tag: `TBD`
- Release title: `TBD`
- Release URL: `TBD`
- Target branch: `main`
- Published at: `TBD`
- Draft: `false`
- Prerelease: `false` 또는 필요 시 별도 기록

## v0.1.1과의 관계 확인

- `v0.1.1-demo-ready`는 공식 공개 데모 Release 기준으로 유지한다.
- v0.1.2는 v0.1.1 이후 운영 안정화 / 데모 UX 개선 / 문서 정리를 포함하는 후보 릴리스다.
- `v0.1.2-demo-published`는 GitHub Release가 없는 문서성/임시 tag로 유지하며, v0.1.2 정식 Release로 간주하지 않는다.

## GitHub Release 확인

Release 생성 후 확인한다.

- Release URL이 열린다.
- Release title이 의도한 제목과 일치한다.
- Release tag가 의도한 tag와 일치한다.
- Target branch가 `main`이다.
- Release body에 포함/제외 범위가 명확히 적혀 있다.
- Mock / 미연동 항목이 명확히 적혀 있다.
- 실제 외부 발송/결제/POS 연동이 된 것처럼 표현하지 않는다.

## README 확인

- README에 v0.1.2 Release 링크가 있다.
- README의 공식 demo 기준 설명이 최신 상태다.
- v0.1.1과 v0.1.2 관계가 혼동되지 않는다.
- Troubleshooting / environment / demo walkthrough 문서 링크가 유지된다.

## 검증 명령 재확인

Backend:

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
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
git log --oneline --decorate -10
```

## 주요 화면 확인

Admin:

- `/admin/pro/operations`
- `/admin/pro/weekly-report-batches`
- `/admin/pro/weekly-report-deliveries`
- `/admin/pro/operations/audit-logs`
- `/admin/pro/operations/health-alerts`

Merchant:

- `/merchant/pro`
- `/merchant/pro/weekly-report`
- `/merchant/pro/weekly-report-notifications`

Customer:

- `/demo`
- `/products`
- `/my-reservations`
- `/my-payments`

## Mock / 미연동 확인

아래가 실제 연동이 아님을 확인한다.

- PG 결제
- 카드 환불
- 배송 provider
- POS API
- 이메일
- 카카오
- Push
- Slack / Discord / Webhook
- 실제 AI 모델

## 개인정보 / token 확인

- Release body에 실제 email/phone/address/token이 없다.
- env example에 실제 provider token이 없다.
- audit/delivery/health alert 문서에 외부 발송 token 저장을 안내하지 않는다.

## Post-release 결과 기록

Release 후 아래를 채운다.

```text
Release URL:
Release tag:
Release title:
README remote link:
Validation result:
Known follow-up:
```

## 실패 시 조치

- Release URL 404: tag push 여부와 GitHub Release 생성 여부 확인
- README 링크 누락: README 수정/커밋/push 후 재확인
- smoke test 실패: seed_demo 재실행 후 backend server 상태 확인
- scheduler `SKIPPED`: 동일 기간 completed scheduled run 여부 확인
- health alert skip: OPEN/ACKNOWLEDGED alert 중복 여부 확인
