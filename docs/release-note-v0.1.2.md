# Release Note Draft v0.1.2

## 상태

`v0.1.2`는 아직 Release Candidate 준비 단계다.

- 공식 공개 데모 Release 기준: `v0.1.1-demo-ready`
- `v0.1.2-demo-published`: GitHub Release가 없는 문서성/임시 tag로 유지
- 새 tag 생성 없음
- 새 GitHub Release 생성 없음
- 기존 tag 삭제/이동 없음

이 문서는 향후 v0.1.2 정식 Release를 만들 때 사용할 release note 초안이다.

## v0.1.2 목적

v0.1.2의 목적은 v0.1.1 공개 데모 이후 기능을 크게 늘리는 것이 아니라, 운영 안정화와 데모 전달력을 높이는 것이다.

핵심 방향:

- 운영자가 문제를 빠르게 확인할 수 있게 한다.
- 외부 시연자가 고객/점주/관리자/Pro Operations 흐름을 쉽게 이해하게 한다.
- Mock/실제 연동 경계를 화면과 문서에서 명확히 한다.
- 실제 외부 API 연동 없이 release-ready documentation과 smoke coverage를 강화한다.

## v0.1.1 대비 변경 요약

- Pro Operations read-only smoke test 범위 확대
- Operations troubleshooting guide 추가
- Environment reference 문서 추가
- `.env.example`, `backend/.env.example`, `frontend/.env.example` 안내 보강
- `/demo` 페이지의 역할별 데모 흐름과 Mock 안내 강화
- README 데모 실행 순서와 v0.1.2 준비 문서 링크 정리
- Admin Batch / Health Alert / 고객 Mock 결제 화면 안내 문구 보강
- v0.1.2 scope candidate, checklist, post-release verification template 추가

## 운영 안정화 개선

- troubleshooting guide에 상황별 증상, 확인 명령어, 정상/비정상 판단 기준, 다음 조치 순서를 정리했다.
- Weekly Report batch `SKIPPED` 상태가 동일 기간 중복 실행 방지에 따른 정상 안전장치일 수 있음을 명시했다.
- Health Alert check의 `skipped_count`가 같은 source_key의 OPEN/ACKNOWLEDGED alert 중복 방지일 수 있음을 문서화했다.
- 환경변수 누락 의심 시 확인 위치와 민감정보 저장 금지 원칙을 정리했다.

## Pro Operations smoke test 보강

`scripts/smoke_test.py`가 기존 MVP 거래 흐름 외에 아래 read-only / 권한 검증을 추가로 확인한다.

- Admin Pro Operations summary 조회
- Admin Pro Operations health 조회
- Admin Pro Health Alerts 목록 조회
- Admin Weekly Report batch run 목록 조회
- batch run이 존재하는 경우 batch 상세 조회
- merchant 권한으로 Admin Pro Operations summary 접근 시 `403` 확인

## Demo UX 개선

- `/demo` 페이지에 고객/점주/관리자별 데모 목적과 계정 정보를 보강했다.
- 권장 시연 흐름을 고객 예약 → 가맹점 픽업 → 관리자 Pro Operations → 점주 Weekly Report 알림 흐름으로 정리했다.
- 실제 결제, 배송, POS, 이메일/카카오/Push/Slack/Webhook이 포함되지 않는다는 점을 데모 시작 전에 명시했다.

## Environment / troubleshooting 문서 정리

추가/보강 문서:

- `docs/operations-troubleshooting-guide.md`
- `docs/environment-reference.md`
- `docs/demo-walkthrough-v0.1.1.md`
- `docs/v0.1.2-scope-candidate.md`
- `docs/release-checklist-v0.1.2.md`
- `docs/post-release-verification-v0.1.2.md`

## Mock / 실제 연동 경계 명확화

v0.1.2 RC 기준 아래는 실제 연동이 아니다.

- Mock payment: 실제 PG 승인 없음
- Mock refund: 실제 카드 환불 없음
- Mock POS sync: 실제 POS API 호출 없음
- In-app mock delivery: 이메일/카카오/Push 발송 없음
- Health Alert mock flow: Slack/Discord/Webhook 발송 없음
- Rule-based insights/recommendations: 실제 AI 모델 없음

## 포함 범위

- 운영 안정화 문서
- 환경변수 reference
- demo walkthrough
- v0.1.2 release checklist
- v0.1.2 post-release verification template
- smoke test read-only coverage 확대
- Mock/실제 연동 경계 안내 문구 보강

## 제외 범위

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
- DB schema 변경
- migration 추가
- 기존 tag 삭제/이동
- `v0.1.2-demo-published` 공식 Release 승격

## 검증 결과

Release Candidate 준비 단계에서 아래 검증을 수행한다.

- `git status`: PASS
- `git branch --show-current`: PASS
- `git status -sb`: PASS
- `git log --oneline -8`: PASS
- `git tag --list`: PASS
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS
- `python scripts/run_pro_health_alert_check.py`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## Release 생성 전 주의사항

- 이 문서는 release note 초안이며 실제 GitHub Release를 생성하지 않는다.
- v0.1.2 tag 이름과 Release title을 별도 Phase에서 확정해야 한다.
- `v0.1.2-demo-published`는 공식 Release로 승격하지 않는다.
- `main`과 `origin/main` 동기화 상태를 확인하고 필요한 문서 커밋을 push한 뒤 release 작업을 진행한다.
- 실제 외부 API token, 이메일, 전화번호, 주소, Webhook URL을 문서나 env example에 넣지 않는다.
