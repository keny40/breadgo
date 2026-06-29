# Phase 117 Release Preparation

## 목적

v0.1.2 정식 릴리스 후보 범위를 기준으로, 실제 릴리스 전에 필요한 checklist와 post-release verification 템플릿을 정리했다.

이번 Phase는 문서화 중심이며 기능 코드, DB schema, migration은 변경하지 않는다.

## 현재 기준

- 공식 공개 데모 Release: `v0.1.1-demo-ready`
- Release URL: `https://github.com/keny40/breadgo/releases/tag/v0.1.1-demo-ready`
- `v0.1.2-demo-published`: GitHub Release가 없는 문서성/임시 tag로 유지
- v0.1.2 정식 Release: 아직 준비 단계
- 새 tag 생성 없음
- 새 GitHub Release 생성 없음
- 기존 tag 삭제/이동 없음

## 작성 문서

- `docs/release-checklist-v0.1.2.md`
- `docs/post-release-verification-v0.1.2.md`
- `docs/release-prep-phase117.md`

## v0.1.2 포함 범위

추천 포함 범위:

- Pro Operations smoke coverage 추가 확대
- Demo walkthrough와 README 실행 순서 정리
- Environment reference / troubleshooting guide 정리
- Admin Batch / Delivery / Health Alert 상태 help text 보강
- Mock payment / in-app mock delivery / Health Alert mock 문구 보강
- v0.1.2 release checklist와 post-release verification 템플릿 정리

## v0.1.2 제외 범위

- 실제 PG 결제 연동
- 실제 카드 환불 연동
- 실제 배송 provider 연동
- 실제 POS API 연동
- 실제 이메일/카카오/Push 발송
- Slack/Discord/Webhook 발송
- 자동 복구
- 자동 purge scheduler
- 대량 비동기 큐
- 세부 관리자 권한 분리
- 실제 AI 모델 연결
- 기존 tag 삭제/이동
- `v0.1.2-demo-published`를 공식 Release로 승격

## v0.1.1 Release와 v0.1.2 준비 상태의 관계

- `v0.1.1-demo-ready`는 현재 공식 공개 데모 Release다.
- v0.1.2는 v0.1.1 이후 운영 안정화, 데모 UX, 문서 정리, 검증 범위 확대를 묶는 후보 릴리스다.
- `v0.1.2-demo-published`는 이름은 v0.1.2를 포함하지만 공식 GitHub Release가 아니며, 문서성/임시 tag로 유지한다.
- v0.1.2 정식 Release를 만들려면 별도 Phase에서 release tag 이름과 GitHub Release body를 확정해야 한다.

## 검증 결과

- `git status`: PASS
- `git branch --show-current`: PASS
  - `main`
- `git tag --list`: PASS
  - `v0.1.1-demo-ready`, `v0.1.2-demo-published` 존재 확인
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS
  - 동일 기간 완료된 SCHEDULED batch run이 있어 중복 실행 방지 로직으로 `SKIPPED` 처리됨.
- `python scripts/run_pro_health_alert_check.py`: PASS
  - `overall_status=WARNING`, 기존 OPEN/ACKNOWLEDGED alert 중복으로 `generated_count=0`, `skipped_count=2`.
- `npm run lint`: PASS
- `npm run build`: PASS

## DB / 기능 코드 / migration 변경 여부

- 기능 코드 변경 없음
- DB schema 변경 없음
- migration 추가 없음

## Suggested commit message

`Prepare v0.1.2 release checklist`
