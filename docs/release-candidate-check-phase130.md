# Release Candidate Check Phase 130

## 목적

Phase 130은 v0.1.3 adapter readiness 기능 구현 이후 Release Candidate 문서, 검증 체크리스트, post-release verification 템플릿, push/tag/Release 직전 상태를 정리하는 단계다.

이번 Phase에서는 새 tag를 만들지 않았고, GitHub Release를 만들지 않았으며, origin/main push도 실행하지 않았다.

## Release Candidate 상태

- 현재 공식 최신 Release: `v0.1.2-demo-stabilized`
- v0.1.3 상태: Release Candidate 준비 단계
- v0.1.3 공식 tag: 아직 생성 전
- GitHub Release: 아직 생성 전
- 기존 tag 삭제/이동: 없음
- origin/main push: 실행하지 않음

## 작성 / 수정 파일

- `README.md`
- `docs/release-note-v0.1.3.md`
- `docs/release-checklist-v0.1.3.md`
- `docs/post-release-verification-v0.1.3.md`
- `docs/release-candidate-check-phase130.md`

## Phase 128~129 반영 내용

- Payment provider adapter skeleton / mock dry-run
- Delivery provider adapter skeleton / mock dry-run
- Notification provider adapter skeleton / mock dry-run
- POS provider readiness / mock dry-run
- External Integration Readiness service
- Admin read-only readiness API
- Admin Dashboard External Integration Readiness 카드
- smoke test adapter readiness 범위 확장
- 모든 외부 연동은 mock/noop이며 `external_calls_enabled=false` 원칙 유지

## main / origin/main 상태

Phase 130 시작 시점 확인:

- branch: `main`
- `git status -sb`: `## main...origin/main [ahead 8]`
- working tree: clean에서 시작

Phase 130 문서 추가 후에는 README 및 RC 문서 변경이 생긴다. push는 다음 Phase에서 실행한다.

## Push 필요 여부

필요하다.

이유:

- Phase 128~129 구현 커밋이 origin/main보다 앞서 있음
- Phase 130 RC 문서가 추가됨
- v0.1.3 Release tag 생성 전 원격 main에 문서와 구현 결과를 먼저 반영해야 함

## 공식 tag 후보

추천:

1. `v0.1.3-adapter-readiness`

대안:

2. `v0.1.3-mock-integrations`
3. `v0.1.3-external-readiness`

추천 기준:

- 실제 외부 연동이 아니라 adapter readiness 단계임이 드러남
- 기존 `v0.1.2-demo-published`와 혼동되지 않음
- GitHub Release로 사용하기 적절함

## 추천 Release title

`BreadGo Adapter Readiness Release v0.1.3`

## 다음 Phase 실행 절차

1. `git status`로 working tree clean 확인
2. `git branch --show-current`로 `main` 확인
3. Phase 128~130 커밋이 포함된 main을 `origin/main`에 push
4. 원격 README와 v0.1.3 문서 링크 확인
5. annotated tag `v0.1.3-adapter-readiness` 생성
6. tag를 origin에 push
7. `docs/release-note-v0.1.3.md`를 body로 GitHub Release 생성
8. `docs/post-release-verification-v0.1.3.md` 기준으로 등록 후 검증

## DB / Migration 변경 여부

- DB schema 변경: 없음
- migration 추가: 없음
- credential 저장 구조 추가: 없음

## 실제 외부 API 호출 여부

없음.

- 실제 PG API 호출 없음
- 실제 배송 provider API 호출 없음
- 실제 POS API 호출 없음
- 실제 이메일 / 카카오 / Push / Slack / Discord / Webhook 호출 없음
- API key / secret / token / webhook URL 추가 없음

## 검증 결과

- `git status`: PASS, `main`이 `origin/main`보다 8 commits ahead이며 Phase 130 문서/README 변경만 존재
- `git branch --show-current`: PASS, `main`
- `git status -sb`: PASS, `## main...origin/main [ahead 8]` 및 Phase 130 변경 파일 표시
- `git log --oneline -10`: PASS, Phase 128~129 adapter readiness 커밋 포함 확인
- `git tag --list`: PASS, 기존 tag만 확인 (`v0.1.0-local-demo`, `v0.1.0-mvp`, `v0.1.1-demo-ready`, `v0.1.2-demo-published`, `v0.1.2-demo-stabilized`)
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS, demo users/stores/products 재생성 확인
- `python scripts/smoke_test.py`: PASS, Payment / Delivery / Notification / POS adapter readiness와 Admin readiness API, merchant 403 확인 포함
- `python scripts/run_weekly_report_batch.py`: PASS, 동일 기간 완료 batch 존재로 `SCHEDULED` run이 안전하게 `SKIPPED`
- `python scripts/run_pro_health_alert_check.py`: PASS, `overall_status=WARNING`, 기존 OPEN/ACKNOWLEDGED alert 중복 방지로 `generated_count=0`, `skipped_count=2`
- `npm run lint`: PASS
- `npm run build`: PASS

## 남은 한계

- v0.1.3 tag는 아직 생성 전
- GitHub Release는 아직 생성 전
- origin/main push는 아직 실행 전
- adapter는 mock/noop readiness 단계이며 실제 외부 연동은 아님
- 실제 credential 저장, webhook, 대량 비동기 큐는 제외됨

## Suggested commit message

`Prepare v0.1.3 release candidate docs`
