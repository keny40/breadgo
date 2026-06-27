# GitHub Release Draft: v0.1.1 Demo Ready

## Release Metadata

- Release title: `BreadGo MVP Demo Ready Release v0.1.1`
- Tag: `v0.1.1-demo-ready`
- Target branch: `main`

## Release Body

아래 내용을 GitHub Release 본문에 그대로 붙여넣을 수 있다.

```markdown
# BreadGo MVP Demo Ready Release v0.1.1

## Overview

This release marks BreadGo MVP as demo-ready. BreadGo is a Korean Too Good To Go-style local food rescue marketplace for discounted end-of-day bakery and food products.

It includes the consumer reservation flow, merchant operations, admin operations, and the BreadGo Pro / Yield Engine demo path. BreadGo Pro adds weekly reporting, in-app mock delivery, notification analytics, audit trail, health check, and internal health alert workflows for SaaS-style operations demos.

No real email, Kakao, Push, Slack, Discord, Webhook, external POS, PG payment, or delivery API integration is included in this release.

## Included in this release

### BreadGo MVP

- Consumer account, login, region product browsing
- Product reservation with pickup/delivery method selection
- Mock payment and Mock refund state flow
- My reservations, my payments, pickup code, notification views
- Merchant store/product/order/pickup/settlement management
- Admin user/merchant/store/product/reservation/payment/settlement monitoring

### BreadGo Pro

- Merchant Pro dashboard
- Yield dashboard and ESG/waste reduction reporting
- Product templates, recurring product setup, CSV import
- Recommendation stock/discount MVP
- Recommendation usage, adoption, performance, and funnel tracking
- Product view/reservation funnel tracking
- Inventory Ledger and inventory anomaly alerts
- Daily Pro Brief and Weekly Pro Report

### Pro Operations

- Weekly Report snapshot/history/export
- Weekly Report batch logs and scheduler CLI
- Admin batch preview/execute and failed item retry
- Delivery preview and BreadGo in-app mock delivery
- Weekly Report notification analytics and unread reminder
- Pro Operations Dashboard and Quick Actions
- Pro Operations Audit Trail
- Audit Log Explorer, CSV Export, and Purge preview/execute
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

The following checks passed for the demo-ready package:

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS
- `python scripts/run_pro_health_alert_check.py`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## What is mocked

- Mock payment
- Mock refund state
- Mock POS sync
- In-app mock delivery
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
- No Slack/Discord/Webhook delivery
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

## Documentation links

- [README](README.md)
- [Pro Demo Quickstart](docs/pro-demo-quickstart.md)
- [Pro Operations Demo Readiness](docs/pro-operations-demo-readiness.md)
- [Demo Handoff Pack](docs/demo-handoff-pack.md)
- [Release Notes v0.1.1 Demo Ready](docs/release-notes-v0.1.1-demo-ready.md)
- [Final Release Checklist](docs/final-release-checklist.md)
- [Health Alert Scheduler Runbook](docs/pro-health-alert-scheduler-runbook.md)
- [Audit Log Retention Policy](docs/pro-audit-log-retention-policy.md)

## Next steps

- Add real PG payment/refund integration
- Add real delivery provider integration
- Add real email/Kakao/Push notification channels
- Connect Slack/Discord/Webhook operations alerts
- Register production cron jobs for Weekly Report and Health Alert checks
- Add external POS provider integrations
- Add production-grade async batch queue
- Add fine-grained admin permission model
- Add real AI recommendation model
```

## 주요 기능 요약

- 소비자 MVP: 지역 상품 탐색, 예약, Mock 결제, 내 예약/결제/알림 확인
- 점주 MVP: 매장/상품/주문/픽업/정산 관리, CSV import, Mock POS sync
- 관리자 MVP: 사용자/가맹점/상품/예약/결제/정산/운영 상태 확인
- BreadGo Pro: 수율 관리, 추천, 고객 전환, 재고 이력, Daily/Weekly report
- Pro Operations: batch, delivery preview, notification, audit, health, alert 운영 흐름

## GitHub Release 등록 방법

1. GitHub repository의 Releases 화면으로 이동한다.
2. `Draft a new release`를 선택한다.
3. Tag에 `v0.1.1-demo-ready`를 선택한다.
4. Target이 `main`인지 확인한다.
5. Release title에 `BreadGo MVP Demo Ready Release v0.1.1`을 입력한다.
6. 위 `Release Body` 내용을 붙여넣는다.
7. 실제 첨부 artifact가 없으면 binary upload 없이 release를 저장한다.
8. `Publish release` 전에 README, demo handoff, final checklist 링크가 열리는지 확인한다.

## 주의사항

- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송은 없다.
- 외부 발송 API 토큰, 수신자 이메일, 전화번호, 주소는 저장하거나 노출하지 않는다.
- 실서버 cron 등록은 이 release에 포함하지 않는다.
- Audit Log purge는 데모에서는 preview까지만 보여주는 것을 권장한다.
