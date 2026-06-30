# Phase 141 Admin Readiness Simple Mode

## Purpose

Simplify the `/admin` External Integration Readiness area so non-technical demo viewers can understand the status quickly, while keeping technical Mock / Noop / dry-run details available in a collapsible detail mode.

## What Changed

- `/admin` now shows a simple readiness view by default.
- Payment, Delivery, Notification, and POS are summarized in one compact table.
- Technical details are hidden behind a `상세 보기` toggle.
- Existing provider-level Mock / Noop / dry-run / `external_calls_enabled=false` information remains available in detail mode.
- The existing External Integration Readiness API response structure was not changed.

## Default Simple Mode Copy

Title:

- `외부 연동 준비 상태`

Explanation:

- `실제 외부 연동은 꺼져 있고, 데모/점검용 adapter 준비 상태만 확인합니다.`
- `현재는 실제 운영 연동 완료가 아니라 안전한 준비 상태입니다. 외부 호출은 모두 OFF입니다.`

Default rows:

- 결제: `준비 완료 / 실제 결제 OFF`
- 배송: `준비 완료 / 실제 배송 OFF`
- 알림: `준비 완료 / 실제 발송 OFF`
- POS: `준비 완료 / 실제 POS OFF`

## Detail Mode

The `상세 보기` button opens the technical view with:

- overall readiness status
- readiness item count
- dry-run check count
- external calls ON/OFF
- provider별 status
- provider mode
- Mock / Noop dry-run result
- `external_calls_enabled=false`
- status guide for `MOCK_READY`, `NOT_ENABLED`, and `NOT_CONFIGURED`
- next-step notes before real external integration

## Boundaries

- DB schema changed: No
- Migration added: No
- External Integration Readiness API response changed: No
- Real PG, delivery, POS, email, Kakao, Push, Slack, Discord, or Webhook API calls added: No
- API key, secret, token, webhook URL added: No

## Validation

Phase 141 validation:

- `git status`: PASS
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## Remaining Notes

This phase intentionally improves presentation only. Real external integrations remain disabled and should only be introduced after credential boundary, audit, failure handling, and sandbox verification are implemented.
