# Release Checklist v0.1.2

## 목적

`v0.1.2` 정식 릴리스를 만들기 전에 확인해야 할 작업 범위, 검증 명령, tag / GitHub Release 생성 조건을 정리한다.

현재 공식 공개 데모 Release 기준은 `v0.1.1-demo-ready`이며, `v0.1.2`는 아직 준비 단계다.

## 현재 버전 상태

- Official public demo release: `v0.1.1-demo-ready`
- Official release URL: `https://github.com/keny40/breadgo/releases/tag/v0.1.1-demo-ready`
- `v0.1.2-demo-published`: GitHub Release가 없는 문서성/임시 tag로 유지
- v0.1.2 정식 Release: 아직 생성 전
- 새 tag / 새 Release 생성 조건: 이 checklist 통과 후 별도 Phase에서 결정

## v0.1.2 추천 포함 범위

v0.1.2는 외부 연동 릴리스가 아니라, v0.1.1 공개 데모 이후 운영 안정화와 데모 전달력을 높이는 안정화 릴리스로 준비한다.

포함 후보:

- Pro Operations smoke coverage 추가 확대
- Demo walkthrough와 README 실행 순서 정리
- Environment reference / troubleshooting guide 정리
- Admin Batch / Delivery / Health Alert 상태 help text 보강
- Mock payment / in-app mock delivery / Health Alert mock 문구 보강
- v0.1.2 release checklist와 post-release verification 템플릿 정리

## v0.1.2 제외 범위

v0.1.2에서는 아래를 하지 않는다.

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

## DB / migration 기준

추천 v0.1.2 범위에서는 DB schema 변경이 없어야 한다.

아래 항목이 필요해지면 v0.1.2 범위에서 제외하고 별도 릴리스로 분리한다.

- provider credential 저장 구조
- notification consent 관리
- 외부 delivery webhook log
- 장기 audit archive
- 실제 결제/배송/POS credential 테이블

## 외부 연동 기준

v0.1.2에서는 실제 외부 API를 호출하지 않는다.

아래는 모두 mock 또는 문서/adapter 준비 수준으로만 유지한다.

- PG payment
- delivery provider
- POS provider
- email
- Kakao
- Push
- Slack / Discord / Webhook

## Release 전 필수 검증

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

## 화면 확인 체크리스트

Admin:

- `/admin`
- `/admin/pro/operations`
- `/admin/pro/weekly-report-batches`
- `/admin/pro/weekly-report-deliveries`
- `/admin/pro/operations/audit-logs`
- `/admin/pro/operations/health-alerts`

Merchant:

- `/merchant/pro`
- `/merchant/pro/weekly-report`
- `/merchant/pro/weekly-report-notifications`
- `/merchant/pro/pos`

Customer:

- `/demo`
- `/products`
- `/my-reservations`
- `/my-payments`

## 문서 확인 체크리스트

- `README.md`
- `docs/demo-walkthrough-v0.1.1.md`
- `docs/operations-troubleshooting-guide.md`
- `docs/environment-reference.md`
- `docs/v0.1.2-scope-candidate.md`
- `docs/release-checklist-v0.1.2.md`
- `docs/post-release-verification-v0.1.2.md`

## Release 생성 전 결정 사항

아래를 결정하기 전에는 새 tag나 GitHub Release를 만들지 않는다.

- 실제 release tag 이름
  - 후보: `v0.1.2`
  - 또는 demo 안정화 성격이면 `v0.1.2-demo-ready`
- Release title
- Release body source 문서
- `v0.1.2-demo-published`와의 관계 설명 방식
- v0.1.2에 포함한 변경 파일 목록
- DB/migration 없음 여부
- 외부 연동 없음 여부

## Release 생성 금지 조건

아래 중 하나라도 해당하면 Release 생성 전 중단한다.

- `git status`가 의도하지 않은 코드 변경을 포함
- backend compile 실패
- smoke test 실패
- frontend lint/build 실패
- DB migration이 필요한 변경이 섞임
- 실제 외부 API token이 문서나 env example에 들어감
- Mock/실제 연동 경계가 모호함

## 권장 Release 준비 순서

1. v0.1.2 범위 확정
2. 변경 파일 검토
3. 검증 명령 실행
4. release note draft 작성
5. post-release verification 기준 확정
6. tag 생성 여부 결정
7. GitHub Release 생성
8. README 원격 반영 확인

## 결론

v0.1.2는 아직 준비 단계이며, 현재 기준으로는 새 tag나 GitHub Release를 만들지 않는다.
