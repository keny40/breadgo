# Post-release Verification v0.1.1

## 목적

GitHub Release `v0.1.1-demo-ready` 등록 후, 릴리즈 링크와 문서, 로컬 검증 상태가 데모 제출 기준에 맞게 유지되는지 확인한다.

## GitHub Release 확인

- Release URL이 열리는지 확인한다.
- Release title이 `BreadGo MVP Demo Ready Release v0.1.1`인지 확인한다.
- Tag가 `v0.1.1-demo-ready`인지 확인한다.
- Target branch가 `main`인지 확인한다.
- Release body에 Overview, Included in this release, Validation, Known limitations, How to run locally 섹션이 있는지 확인한다.

## 문서 링크 확인

- `README.md`에서 release 관련 문서 링크가 열리는지 확인한다.
- `docs/github-release-v0.1.1-demo-ready.md`가 repository에서 보이는지 확인한다.
- `docs/release-notes-v0.1.1-demo-ready.md` 링크가 열리는지 확인한다.
- `docs/pro-demo-quickstart.md` 링크가 열리는지 확인한다.
- `docs/demo-handoff-pack.md` 링크가 열리는지 확인한다.
- `docs/final-release-checklist.md` 링크가 열리는지 확인한다.
- `docs/pro-health-alert-scheduler-runbook.md` 링크가 열리는지 확인한다.
- `docs/pro-audit-log-retention-policy.md` 링크가 열리는지 확인한다.

## 최종 실행 명령 재확인

Backend:

```bash
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/seed_demo.py
python scripts/smoke_test.py
python scripts/run_weekly_report_batch.py
python scripts/run_pro_health_alert_check.py
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

Git:

```bash
git status
git log --oneline -10
git tag --list
```

## 로컬 / 원격 동기화 확인

- 로컬 `main`이 원격 `main`과 동기화되어 있는지 확인한다.
- `git status`가 clean인지 확인한다.
- `git tag --list`에서 `v0.1.1-demo-ready`가 보이는지 확인한다.
- GitHub repository에서도 `v0.1.1-demo-ready` tag가 보이는지 확인한다.
- 문서 파일이 원격 GitHub repository에서 보이는지 확인한다.

## 주요 화면 확인

Admin:

- `/admin`
- `/admin/pro/operations`
- `/admin/pro/weekly-report-batches`
- `/admin/pro/weekly-report-deliveries`
- `/admin/pro/operations/audit-logs`
- `/admin/pro/operations/health-alerts`

Merchant:

- `/merchant/pro`
- `/merchant/pro/weekly-report-notifications`

## Mock / 미연동 표시 확인

Release body와 README에서 아래 항목이 실제 연동이 아님을 확인한다.

- PG 결제 실연동 없음
- 배송 실연동 없음
- 실제 이메일 발송 없음
- 실제 카카오 발송 없음
- 실제 Push 발송 없음
- Slack/Discord/Webhook 발송 없음
- POS API 실연동 없음
- 실서버 cron 등록 없음
- 자동 복구 없음
- 자동 purge scheduler 없음
- 세부 관리자 권한 분리 없음
- 대량 비동기 큐 없음

## 개인정보 / 토큰 노출 확인

- Release body에 이메일, 전화번호, 주소, 외부 발송 토큰이 포함되지 않았는지 확인한다.
- Audit/Health/Delivery 관련 문서가 merchant_id, snapshot_id, run_id 중심으로 설명되어 있는지 확인한다.
- 실제 외부 발송 API credential 설정값을 문서에 포함하지 않았는지 확인한다.

## 문제가 생겼을 때

- Release tag가 보이지 않으면 tag push 여부를 확인한다.
- Release body가 깨져 보이면 `docs/github-release-v0.1.1-demo-ready.md`의 `Release Body` 섹션을 다시 복사한다.
- 문서 링크가 깨지면 GitHub repository의 파일 경로와 branch가 `main`인지 확인한다.
- smoke test가 실패하면 먼저 `python scripts/seed_demo.py`를 다시 실행하고 백엔드 서버 상태를 확인한다.
- scheduler CLI가 `SKIPPED`를 반환하면 동일 기간 중복 실행 방지 정책에 따른 정상 동작일 수 있다.
