# Phase 149 Site Performance Diagnosis

## Purpose

Diagnose and improve perceived slow navigation on `https://breadgo.vercel.app`, especially when clicking menu links and moving between customer, merchant, and admin pages.

## Summary

The delay is not mainly caused by a large repository folder.

Observed contributors:

1. Render backend cold/sleep latency can delay API-dependent pages.
2. Protected pages waited for `/api/v1/auth/me` before rendering even when a valid role was already stored in localStorage.
3. `saveStoredUser()` dispatched auth change events even when the stored user did not change, which could trigger NavBar notification refreshes.
4. Admin and Pro pages intentionally load several APIs; most heavy pages already use `Promise.all`, but backend response latency still affects perceived speed.

## Frontend Build / Bundle Check

`npm run build` completed successfully.

The build produced 46 app routes. The largest observed local static chunks after build were approximately:

| Chunk size | Note |
| --- | --- |
| 222 KB | largest JS chunk |
| 138 KB | second largest JS chunk |
| 110 KB | third largest JS chunk |
| 53 KB | medium JS chunk |
| 20 KB | largest CSS chunk observed |

This does not point to a single unusually large route bundle as the main cause of 3+ second navigation.

## Production Timing Check

Measured from local development machine:

| URL | Status | Approx time |
| --- | --- | --- |
| `https://breadgo.vercel.app/login` | 200 | 3890 ms |
| `https://breadgo.vercel.app/products` | 200 | 1343 ms |
| `https://breadgo.vercel.app/merchant` | 200 | 1209 ms |
| `https://breadgo.vercel.app/admin` | 200 | 1002 ms |

Render backend:

| URL | Status | Approx time |
| --- | --- | --- |
| `https://breadgo-api.onrender.com/health` first retry after previous timeout | 200 | 3204 ms |
| `https://breadgo-api.onrender.com/health` warm retry | 200 | 389 ms |
| `https://breadgo-api.onrender.com/api/v1/auth/google/status` | 200 | 517 ms |

Earlier checks also saw two consecutive 30 second timeouts for `/health`, which is consistent with Render free instance cold/sleep behavior or temporary backend wake-up delay.

## API Call Audit

### NavBar

Before this phase:

- NavBar used localStorage role first.
- If role/email was missing, it fetched `/api/v1/auth/me`.
- It fetched `/api/v1/notifications/me` on auth change events.
- Merchant users also fetched Weekly Report unread count.

Potential problem:

- Protected pages call `saveStoredUser()` after `/auth/me`.
- `saveStoredUser()` always dispatched `breadgo-auth-changed`.
- That could cause NavBar to refresh notifications again even when user data had not changed.

Fix:

- `saveStoredUser()` now compares the stored user JSON and dispatches `breadgo-auth-changed` only when user data actually changes.

### Role Guard

Before this phase:

- Every protected page waited for `/api/v1/auth/me` before setting `allowed=true`.
- On Render cold/sleep, this made page navigation feel blocked.

Fix:

- `useRoleGuard()` now uses localStorage role first.
- If stored role matches the required role, the page can render immediately.
- Backend `/auth/me` still runs afterward to validate the session and correct stale roles.
- If stored role mismatches, the user is redirected immediately without waiting for backend.

### Products Page

The products page already uses `Promise.all` for initial region products and stores.

It also uses stored user role first and calls `/auth/me` only when token exists but stored role is missing.

### Heavy Admin / Pro Pages

Admin and Pro Operations pages already use `Promise.all` for multiple read-only APIs.

Remaining perceived slowness on these pages is mostly tied to backend response latency and the number of intentionally loaded operational summaries.

## Render Cold Start

Render cold/sleep is confirmed as a likely contributor.

Evidence:

- `/health` timed out twice at 30 seconds in earlier checks.
- A later first successful `/health` response took about 3.2 seconds.
- Warm retry took about 0.39 seconds.

Recommended options:

1. Move backend to an always-on Render plan.
2. Use a lightweight uptime monitor pinging `/health`.
3. Keep operational pages resilient with loading text/skeletons.
4. Avoid unnecessary auth and notification refreshes during route changes.

## Changes Made

- `frontend/lib/api.ts`
  - `saveStoredUser()` now avoids emitting auth change events when the stored user has not changed.
- `frontend/lib/authGuard.ts`
  - Uses stored role first for immediate role-based page rendering.
  - Keeps backend `/auth/me` validation in the background.
  - Redirects immediately when stored role does not match required role.
- `README.md`
  - Added performance diagnosis doc link.

## Behavior Kept

- Google OAuth callback remains customer-compatible.
- Customer / merchant / admin role redirects remain unchanged.
- NavBar still avoids customer fallback when role is unknown.
- Backend endpoints still enforce real access control.
- DB schema unchanged.
- No migration added.
- No secret/token/key values documented.

## Validation Results

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS after starting local FastAPI on `127.0.0.1:8000`.
- `python -m pytest tests -q`: PASS, 15 passed.
- `npm run lint`: PASS
- `npm run build`: PASS

## Remaining Limits

- Browser network request count was audited primarily through code paths and endpoint timing checks in this environment.
- Render cold/sleep cannot be fully fixed in frontend code.
- First backend-dependent action after backend sleep may still be slow unless the backend is kept warm.

## Suggested Commit Message

`Reduce auth navigation latency`
