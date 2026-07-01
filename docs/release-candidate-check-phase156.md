# Phase 156 Release Candidate Check

## Purpose

Phase 156 documents the `v0.1.6` Release Candidate in a Codex usage-saving mode. It does not change feature code, DB schema, migrations, tags, or GitHub Releases.

## Scope

This RC collects improvements made after `v0.1.5-google-oauth-live`:

1. Vercel Blob OIDC product image upload support
2. Merchant product registration feedback UI cleanup
3. Image upload fallback preservation
4. Navigation latency documentation and Render cold/sleep caveat

## Recommended Release Information

- Recommended tag: `v0.1.6-blob-upload-performance`
- Recommended Release title: `BreadGo Blob Upload Performance Release v0.1.6`
- Release body source: `docs/release-note-v0.1.6.md`
- Target branch: `main`

No tag or Release was created in this phase.

## Included Improvements

### Vercel Blob OIDC Upload

Confirmed from Phase 155:

- Vercel Blob OIDC mode is supported without committing `BLOB_READ_WRITE_TOKEN`.
- Vercel OIDC deployment can use `BLOB_STORE_ID` plus Vercel runtime context.
- Status endpoint confirmed `enabled=true`, `backend=vercel_blob`, `auth_mode=oidc`.
- Live PNG upload succeeded.
- Blob public URL was returned.
- Product registration and lookup exposed `image_url` normally.

### Product Registration Feedback

Confirmed from commit `90c1e92 Fix merchant product form feedback`:

- Product creation success no longer displays a red empty error box.
- Success message is `상품이 등록되었습니다.`
- Red error message appears only on failures.
- Empty or whitespace messages are not rendered.
- Blob URL and direct image URL product creation flows are preserved.

### Image Upload Fallback

- Storage-disabled state still blocks file upload safely.
- Direct image URL input remains available.
- No secret or token value is exposed in UI or docs.

### Navigation Latency

- Role-based local session behavior is used to reduce unnecessary navigation work.
- Render cold/sleep latency remains documented as an operational caveat.
- The delay is not primarily documented as a repository-folder-size problem.

## Excluded Scope

Phase 156 excludes:

- Functional code changes
- DB schema changes
- Alembic migration changes
- New tags
- New GitHub Releases
- Actual external payment, delivery, POS, or notification integration
- Secret/token/key value documentation

## Existing Validation Results Reflected

The following results were already completed during Phase 155 and the product registration feedback fix:

- `npm run lint`: PASS
- `npm run build`: PASS
- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS, 15 tests passed

Phase 156 did not repeat the heavy test suite because it is documentation-only.

## Phase 156 Verification

Executed in this phase:

- `git status`
- Recent commit check
- Existing v0.1.x release document check
- Secret/token/key exposure review for newly written docs by content discipline: only variable names are included, no actual values

## DB / Migration Status

- DB schema changed: No
- Migration changed: No
- New migration added: No

## Feature Code Status

- Feature code changed: No
- Frontend code changed: No
- Backend code changed: No

## Secret Handling

- Secret/token/key values added: No
- Environment variable names documented: Yes
- Actual values documented: No

## Remaining Work Before v0.1.6 Release

1. Commit and push the Phase 156 docs.
2. Confirm remote README/docs visibility.
3. Create tag `v0.1.6-blob-upload-performance` only after the working tree is clean.
4. Register the GitHub Release using `docs/release-note-v0.1.6.md`.
5. Run post-release verification with `docs/post-release-verification-v0.1.6.md`.

## Suggested Commit Message

`Document v0.1.6 blob upload RC`
