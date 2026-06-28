# BreadGo MVP Demo Ready Release v0.1.1

Tag: `v0.1.1-demo-ready`

Target branch: `main`

This document is the final GitHub Release note body for `v0.1.1-demo-ready`. Copy this Markdown into GitHub Releases when publishing the demo-ready release.

## Overview

BreadGo MVP is now ready for demo review. BreadGo is a Korean Too Good To Go-style local food rescue marketplace where customers reserve discounted end-of-day bakery and food products, merchants manage inventory and orders, and admins monitor operations.

This release also packages BreadGo Pro as a demo-ready merchant operating coach and yield management engine. BreadGo Pro includes Weekly Report operations, internal in-app mock delivery, notification analytics, audit trail, health check, and health alert mock workflows.

No real email, Kakao, Push, Slack, Discord, Webhook, external POS, PG payment, or delivery API integration is included in this release.

## Included in this release

### BreadGo MVP

- Consumer login, regional product browsing, reservation, and pickup code flow
- Mock payment and mock refund state flow
- Customer reservations, payments, and notification views
- Merchant store, product, order, pickup, settlement, CSV import, and POS-ready mock sync flows
- Admin user, merchant, product, reservation, payment, settlement, and operation monitoring

### BreadGo Pro

- Merchant Pro dashboard
- Yield dashboard and ESG / waste reduction reporting
- Product templates and recurring product setup
- Recommendation stock / discount MVP
- Recommendation usage, adoption, performance, and funnel tracking
- Product view / reservation funnel tracking
- Inventory Ledger and inventory anomaly alerts
- Daily Pro Brief and Weekly Pro Report

### Pro Operations

- Weekly Report snapshot, history, export, archive, and scheduler CLI
- Weekly Report batch run logs, admin batch execution, and failed item retry
- Delivery preview and BreadGo internal in-app mock delivery
- Merchant Weekly Report notification list, unread count, read, and read-all flows
- Weekly Report notification analytics and unread reminder mock flow
- Pro Operations Dashboard and Quick Actions
- Pro Operations Audit Trail and Audit Log Explorer
- Audit Log CSV export and purge preview / execute flow
- Pro Operations Health Check
- Health Alert mock flow and Health Alert CLI scheduler

## Demo run-through

Recommended admin demo screens:

- `/admin`
- `/admin/pro/operations`
- `/admin/pro/weekly-report-batches`
- `/admin/pro/weekly-report-deliveries`
- `/admin/pro/operations/audit-logs`
- `/admin/pro/operations/health-alerts`

Recommended merchant demo screens:

- `/merchant/pro`
- `/merchant/pro/weekly-report-notifications`

Recommended demo accounts after running `seed_demo.py`:

```text
admin@breadgo.test / 12345678
merchant@breadgo.test / 12345678
customer@breadgo.test / 12345678
```

## Validation

The following checks were run for the demo-ready package:

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS
- `python scripts/run_pro_health_alert_check.py`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS
- `git tag --list`: `v0.1.1-demo-ready` exists

## What is mocked

- Mock payment
- Mock refund state
- Mock POS sync
- BreadGo internal in-app mock delivery
- Internal Health Alert mock flow
- Weekly Report scheduler CLI
- Health Alert scheduler CLI

## Known limitations

- No real PG payment integration
- No real card refund integration
- No real delivery API integration
- No real email delivery
- No real Kakao delivery
- No real Push delivery
- No Slack / Discord / Webhook delivery
- No external POS API integration
- No production cron registration
- No automatic recovery
- No automatic purge scheduler
- No fine-grained admin permission split
- No large-scale async queue
- No real AI model

## How to run locally

Backend:

```bash
cd backend
python -m alembic upgrade head
python scripts/seed_demo.py
python scripts/smoke_test.py
python scripts/run_weekly_report_batch.py
python scripts/run_pro_health_alert_check.py
```

Backend server:

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
npm run dev
```

## GitHub Release publication

Use the GitHub web UI unless GitHub CLI is already installed and authenticated.

Web UI:

1. Open the GitHub repository.
2. Go to `Releases`.
3. Click `Draft a new release`.
4. Select tag `v0.1.1-demo-ready`.
5. Confirm target branch `main`.
6. Enter title `BreadGo MVP Demo Ready Release v0.1.1`.
7. Paste this release note body into the description.
8. Publish the release.

Optional GitHub CLI example only. Do not run unless the environment is ready:

```bash
gh release create v0.1.1-demo-ready ^
  --title "BreadGo MVP Demo Ready Release v0.1.1" ^
  --notes-file docs/release-note-v0.1.1.md
```

## Post-release verification

After publishing, confirm:

- Release URL opens correctly.
- Release title is `BreadGo MVP Demo Ready Release v0.1.1`.
- Tag is `v0.1.1-demo-ready`.
- Target branch is `main`.
- README release links open correctly.
- Release notes, demo quickstart, handoff, and final checklist links open correctly.
- GitHub repository shows `docs/release-note-v0.1.1.md`.
- Local and remote `main` are synchronized.
- `git status` is clean.
- `git tag --list` includes `v0.1.1-demo-ready`.
- Mock / not-yet-integrated features are clearly described.
- No email, phone number, address, or external delivery token is exposed.

## Documentation links

- [README](../README.md)
- [GitHub Release Publish Guide](github-release-publish-guide.md)
- [Post-release Verification v0.1.1](post-release-verification-v0.1.1.md)
- [Pro Demo Quickstart](pro-demo-quickstart.md)
- [Pro Operations Demo Readiness](pro-operations-demo-readiness.md)
- [Demo Handoff Pack](demo-handoff-pack.md)
- [Release Notes v0.1.1 Demo Ready](release-notes-v0.1.1-demo-ready.md)
- [Final Release Checklist](final-release-checklist.md)
- [Health Alert Scheduler Runbook](pro-health-alert-scheduler-runbook.md)
- [Audit Log Retention Policy](pro-audit-log-retention-policy.md)

## Next steps

- Add real PG payment and refund integration
- Add real delivery provider integration
- Add real email / Kakao / Push notification channels
- Connect Slack / Discord / Webhook operations alerts
- Register production cron jobs for Weekly Report and Health Alert checks
- Add external POS provider integrations
- Add production-grade async batch queue
- Add fine-grained admin permission model
- Add real AI recommendation model
