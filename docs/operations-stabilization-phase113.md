# Phase 113 Operations Stabilization Review

## 목적

`v0.1.1-demo-ready` 공식 공개 데모 릴리스 이후, 다음 개발 단계로 넘어가기 전에 운영 안정화 관점의 리스크, 점검 항목, 개선 우선순위를 정리한다.

이번 Phase는 점검/문서화 중심이며 기능 코드, DB schema, migration은 변경하지 않는다.

## 현재 기준

- 공식 공개 데모 Release: `v0.1.1-demo-ready`
- Release URL: `https://github.com/keny40/breadgo/releases/tag/v0.1.1-demo-ready`
- `v0.1.2-demo-published`: GitHub Release가 없는 문서성/임시 tag로 유지
- 새 tag 생성 없음
- 새 GitHub Release 생성 없음
- 기존 tag 삭제/이동 없음

## 운영 안정화 점검 요약

| 점검 항목 | 현재 상태 | 안정성 판단 | 개선 필요 |
| --- | --- | --- | --- |
| 로컬 실행 안정성 | backend compile, frontend lint/build 반복 통과 | 양호 | 실행 순서 문서 통합 |
| `seed_demo.py` 재실행 안정성 | 반복 실행 시 데모 계정/매장/상품 seed 정상 | 양호 | seed 후 생성/갱신 기준 명시 |
| `smoke_test.py` 범위 | 핵심 고객 예약/Mock 결제/픽업/admin summary 확인 | 보통 | Pro Operations API 일부 추가 필요 |
| 배치 스크립트 중복 실행 방지 | Weekly Report scheduler가 동일 기간 완료 run을 `SKIPPED` 처리 | 양호 | SKIPPED 의미를 운영 문서에 더 강조 |
| mock 처리 항목 명확성 | README/release note/runbook에 mock 항목 정리 | 양호 | 화면 내 mock 배지/문구 추가 검토 |
| README 실행 가이드 충분성 | backend/frontend/CLI/demo 계정/문서 링크 존재 | 양호 | 에러 상황별 troubleshooting 링크 보강 |
| 데모 계정/권한 설명 충분성 | README에 admin/merchant/customer 계정 정리 | 양호 | 역할별 가능한 화면 목록 보강 |
| 환경변수 안내 충분성 | 기본 실행 문서는 있으나 env 변수별 설명은 분산됨 | 보통 | `.env.example` 또는 env reference 문서 권장 |
| 에러 발생 시 확인 위치 | health, Swagger, smoke, runbook 존재 | 보통 | "문제 발생 시 확인 순서" 단일 문서 권장 |

## 항목별 상세 점검

## 1. 로컬 실행 안정성

확인 내용:

- `python -m compileall app scripts` 통과
- `npm run lint` 통과
- `npm run build` 통과
- smoke test 실행에는 backend server가 필요하며, 서버가 내려가 있으면 `uvicorn` 실행 후 재시도해야 한다.

판단:

- 로컬 실행 안정성은 데모 기준으로 충분하다.
- 다만 backend server 실행 여부에 따라 smoke test가 실패할 수 있으므로, smoke test 전 확인 절차를 문서 상단에 더 눈에 띄게 둘 필요가 있다.

개선 후보:

- `docs/pro-demo-quickstart.md`에 smoke test 전 backend server 실행 여부 확인 명령 추가
- README에 `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` 위치를 더 명확히 표시

## 2. seed_demo 재실행 안정성

확인 내용:

- `python scripts/seed_demo.py` 반복 실행 통과
- 데모 계정 3종, merchant, stores, products seed 결과 정상 출력
- smoke test가 기대하는 지역 상품 조건도 유지됨

판단:

- 데모 데이터 재생성 안정성은 양호하다.
- 이전 Phase에서 지역 상품 부족으로 smoke test가 실패했던 케이스를 보강한 상태로 보인다.

개선 후보:

- seed 결과로 보장하는 데이터 조건을 문서화
  - active product with stock
  - region product list
  - merchant/admin/customer accounts
- seed 실행 후 기존 운영성 데이터(batch/audit/health alert)가 남는지 여부와 영향 정리

## 3. smoke_test 범위

현재 smoke test가 확인하는 흐름:

- Health check
- Customer login
- Region products found
- Active product with stock found
- Reservation created
- Mock payment ready/confirmed
- My reservations loaded
- Merchant login
- Pickup confirmed
- Admin login
- Admin summary loaded

판단:

- MVP 핵심 거래 흐름을 잘 커버한다.
- BreadGo Pro / Pro Operations 범위는 현재 별도 CLI와 화면 검증 중심이고 smoke test 자동 검증에는 충분히 포함되어 있지 않다.

개선 후보:

- smoke test에 가벼운 Pro API 확인 추가
  - merchant daily brief
  - weekly report
  - admin operations summary
  - health check API
- 단, smoke test가 너무 무거워지지 않도록 read-only API 중심으로 추가

## 4. 배치 스크립트 중복 실행 방지

확인 내용:

- `python scripts/run_weekly_report_batch.py` 실행 시 동일 기간 완료된 SCHEDULED batch run이 있으면 `SKIPPED` 처리
- 중복 snapshot 생성을 피하는 안전장치가 동작함

판단:

- 중복 실행 방지는 안정적으로 동작한다.
- 운영자가 `SKIPPED`를 실패로 오해하지 않도록 문서와 화면에서 의미를 명확히 보여야 한다.

개선 후보:

- runbook에 `SKIPPED = 동일 기간 중복 실행 방지` 문구 보강
- Admin Batch Monitor에서 `SKIPPED` help text 추가
- scheduler CLI exit code와 메시지 정책 문서화

## 5. mock 처리 항목 명확성

현재 명시된 mock / 미연동 항목:

- Mock payment
- Mock refund state
- Mock POS sync
- BreadGo internal in-app mock delivery
- Health Alert mock flow
- Weekly Report scheduler CLI
- Health Alert scheduler CLI
- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송 없음
- 실제 PG/배송/POS API 연동 없음

판단:

- README와 release 문서에서는 충분히 명확하다.
- 데모 화면에서는 사용자가 외부 발송으로 오해하지 않도록 in-app mock 문구를 계속 유지해야 한다.

개선 후보:

- Admin delivery 화면에 "외부 발송 없음" 배지 유지/강화
- Merchant notification 화면에 "BreadGo 내부 알림" 문구 유지
- Mock payment 화면에 실제 결제가 아님을 더 명확히 표시

## 6. README 실행 가이드 충분성

판단:

- README에 배포 URL, demo account, 기술 스택, Pro 운영 기능, 관련 문서 링크가 있다.
- v0.1.1 Release 관련 링크도 충분하다.
- 다만 운영자가 에러 상황에서 어떤 문서를 먼저 봐야 하는지는 더 명확히 정리하면 좋다.

개선 후보:

- README에 "문제 발생 시 확인 순서" 짧은 섹션 추가
- `docs/pro-demo-quickstart.md`, `docs/weekly-report-batch-runbook.md`, `docs/pro-health-alert-scheduler-runbook.md`를 troubleshooting 순서로 연결

## 7. 데모 계정/권한 설명 충분성

현재 README 계정:

```text
customer@breadgo.test / 12345678
merchant@breadgo.test / 12345678
admin@breadgo.test / 12345678
```

판단:

- 기본 계정 정보는 충분하다.
- 역할별 접근 가능한 화면과 불가능한 화면을 더 명확히 보여주면 권한 데모가 쉬워진다.

개선 후보:

- demo accounts 문서에 역할별 주요 경로 추가
- admin API에 merchant/customer 접근 시 403이 나는 점을 데모 시나리오에 명시

## 8. 환경변수 안내 충분성

판단:

- 기본 실행 흐름은 문서화되어 있다.
- 다만 환경변수 목록과 "필수/선택/로컬 기본값" 구분은 별도 문서나 `.env.example`로 정리하면 더 안정적이다.

개선 후보:

- backend `.env.example` 정리
- frontend `.env.local.example` 정리
- DB URL, JWT secret, blob/upload 관련 변수, API base URL 구분
- 실제 외부 발송 token은 아직 사용하지 않으며 저장하지 않는다는 원칙 명시

## 9. 에러 발생 시 확인 위치

현재 확인 가능한 위치:

- Backend health: `/health`
- Swagger: `/docs`
- smoke test: `backend/scripts/smoke_test.py`
- Weekly Report batch runbook
- Pro health alert scheduler runbook
- Audit log retention policy
- Admin Pro Operations screen
- Admin Batch Monitor
- Admin Delivery Preview
- Admin Audit Log Explorer
- Admin Health Alerts

판단:

- 확인 지점은 충분하지만 분산되어 있다.
- 운영자가 처음 보는 경우 "어디부터 봐야 하는지"가 부족할 수 있다.

개선 후보:

- `docs/operations-troubleshooting-guide.md` 추가
- 장애 유형별 확인 순서 정리
  - backend down
  - seed/smoke failure
  - scheduler skipped/failed
  - delivery mock failure
  - health alert warning/critical
  - audit purge/export 문제

## 발견된 리스크

1. Pro Operations 자동 검증 범위 부족
   - smoke test가 MVP 거래 흐름 중심이라 Pro Operations API 회귀를 충분히 잡지 못할 수 있다.
2. 환경변수 문서 분산
   - 로컬/배포 환경에서 필요한 env 값을 한눈에 확인하기 어렵다.
3. `SKIPPED` 상태 오해 가능성
   - scheduler 중복 실행 방지 결과가 운영자에게 실패처럼 보일 수 있다.
4. mock / 실제 연동 경계의 화면 의존성
   - 문서에는 명확하지만 화면에서 일부 사용자가 실제 발송/결제로 오해할 수 있다.
5. troubleshooting 단일 진입점 부족
   - runbook은 많지만 장애 발생 시 첫 확인 순서가 하나로 묶여 있지 않다.

## 개선 우선순위

1. smoke test에 Pro Operations read-only API 추가
   - admin operations summary, health check, merchant weekly report notification count 등 가벼운 API 중심
2. operations troubleshooting guide 추가
   - 에러 발생 시 확인 순서를 단일 문서로 정리
3. 환경변수 reference / example 정리
   - 로컬 실행 안정성과 신규 환경 재현성 개선
4. Admin Batch / Delivery 화면의 상태 help text 보강
   - `SKIPPED`, `IN_APP_MOCK`, `IN_APP_REMINDER` 의미를 화면에서 더 명확히 표시
5. 데모 UX 문구 보강
   - Mock payment, in-app mock delivery, Health Alert mock flow를 화면에서 계속 명확히 표시

## Phase 113 결정

- 기능 수정 없이 운영 안정화 점검 결과만 문서화한다.
- 공식 공개 데모 Release 기준은 `v0.1.1-demo-ready`로 유지한다.
- `v0.1.2-demo-published`는 문서성/임시 tag로 유지한다.
- 다음 개발 단계 후보 중 1순위는 Pro Operations smoke coverage 확대와 troubleshooting guide 정리다.

## Phase 114 반영 메모

Phase 113의 1순위 개선 항목인 Pro Operations smoke coverage 확대를 Phase 114에서 일부 반영했다.

추가된 smoke test 범위:

- Admin Pro Operations summary read-only 조회
- Admin Pro Operations health read-only 조회
- Admin Pro Health Alerts 목록 조회
- Admin Weekly Report batch run 목록 조회
- batch run이 존재하는 경우 Admin Weekly Report batch 상세 조회
- merchant 권한으로 Admin Pro Operations summary 접근 시 `403` 차단 확인

아직 남은 후보:

- delivery preview 목록 read-only 검증
- audit log summary read-only 검증
- merchant weekly report notification unread count 검증
- troubleshooting guide 별도 문서화

## 검증 결과

- `git status`: PASS
- `git branch --show-current`: PASS
  - `main`
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

`Document operations stabilization review`
