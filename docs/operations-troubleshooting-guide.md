# Operations Troubleshooting Guide

## 목적

BreadGo MVP / BreadGo Pro 운영 중 문제가 생겼을 때 가장 먼저 확인할 단일 troubleshooting guide다.

공식 공개 데모 Release 기준은 `v0.1.1-demo-ready`이며, `v0.1.2-demo-published`는 GitHub Release가 없는 문서성/임시 tag로 유지한다.

이번 문서는 운영 확인 순서만 정리한다. 기능 코드, DB schema, migration, tag, GitHub Release는 변경하지 않는다.

## 공통 확인 순서

문제가 생기면 먼저 아래 순서로 확인한다.

```powershell
git status
git branch --show-current
git tag --list
```

Backend 기본 점검:

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/seed_demo.py
```

Frontend 기본 점검:

```powershell
cd frontend
npm run lint
npm run build
```

운영 CLI 점검:

```powershell
cd backend
python scripts/run_weekly_report_batch.py
python scripts/run_pro_health_alert_check.py
```

Smoke test는 backend server가 실행 중인 상태에서 별도 터미널에서 실행한다.

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

```powershell
cd backend
python scripts/smoke_test.py
```

## 1. 로컬 서버 실행 실패

### 증상

- `python -m uvicorn app.main:app --reload --port 8000` 실행 실패
- `http://127.0.0.1:8000/health` 또는 `http://localhost:8000/health` 접속 실패
- smoke test 첫 단계 Health check 실패

### 확인 명령어

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

다른 터미널:

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing
```

### 정상 판단 기준

- compileall이 오류 없이 종료
- alembic upgrade가 오류 없이 종료
- `/health` 응답에 `{"status":"ok"}` 표시

### 비정상 판단 기준

- import error
- DB connection error
- port already in use
- health endpoint connection refused

### 다음 조치 순서

1. backend 폴더에서 실행했는지 확인한다.
2. `.env` 또는 DB 연결 환경변수가 올바른지 확인한다.
3. `python -m alembic upgrade head`를 먼저 실행한다.
4. 8000 포트를 이미 쓰는 프로세스가 있는지 확인한다.
5. 오류 메시지의 첫 traceback을 기준으로 app import 문제인지 DB 문제인지 나눈다.

## 2. DB migration 실패

### 증상

- `python -m alembic upgrade head` 실패
- 테이블/컬럼이 없다는 API 오류 발생
- seed_demo 실행 중 DB schema 관련 오류 발생

### 확인 명령어

```powershell
cd backend
python -m alembic current
python -m alembic heads
python -m alembic upgrade head
```

### 정상 판단 기준

- `upgrade head`가 오류 없이 종료
- current revision이 heads와 일치

### 비정상 판단 기준

- DB 접속 실패
- migration conflict
- relation/column does not exist
- duplicate column/table error

### 다음 조치 순서

1. DB URL 환경변수가 현재 의도한 DB를 가리키는지 확인한다.
2. `alembic current`와 `alembic heads`를 비교한다.
3. 최근 migration 파일이 누락되었는지 확인한다.
4. 로컬 DB라면 백업 후 clean seed 가능 여부를 판단한다.
5. 운영 DB라면 임의로 schema를 직접 수정하지 않는다.

## 3. seed_demo 실패

### 증상

- `python scripts/seed_demo.py` 실패
- demo account 로그인 실패
- region products가 비어 smoke test 실패

### 확인 명령어

```powershell
cd backend
python -m alembic upgrade head
python scripts/seed_demo.py
```

### 정상 판단 기준

출력 예시:

```text
BreadGo demo data seeded.
users: 3
merchant: 1
stores: 3
products: 7
```

### 비정상 판단 기준

- demo user 생성 실패
- merchant/store/product 생성 실패
- unique constraint 오류가 반복됨
- 지역 상품 조건이 충족되지 않음

### 다음 조치 순서

1. migration을 먼저 최신화한다.
2. seed_demo가 idempotent하게 동작하는지 출력값을 확인한다.
3. smoke test가 기대하는 지역 조건을 확인한다.
   - `서울특별시`
   - `강남구`
   - `역삼동`
   - `ACTIVE`
   - stock > 0
4. 여전히 실패하면 seed script의 demo product 상태와 수량을 확인한다.

## 4. smoke_test 실패

### 증상

- `python scripts/smoke_test.py` 실패
- `[FAIL] ...` step이 출력됨
- response body에 상세 오류 표시

### 확인 명령어

```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

다른 터미널:

```powershell
cd backend
python scripts/seed_demo.py
python scripts/smoke_test.py
```

### 정상 판단 기준

마지막에 아래 메시지가 출력된다.

```text
[PASS] BreadGo MVP smoke test completed
```

Phase 114 이후 smoke test는 아래도 확인한다.

- Admin Pro Operations summary
- Admin Pro Operations health
- Admin Pro Health Alerts list
- Admin Weekly Report batch list/detail
- merchant 권한으로 admin pro operations 접근 시 `403`

### 비정상 판단 기준

- Health check 실패: 서버 미실행 가능성
- Customer/Merchant/Admin login 실패: seed_demo 또는 auth 문제
- Region products found 실패: demo 지역 상품 부족
- Reservation/Payment/Pickup 실패: MVP 거래 흐름 회귀
- Admin Pro Operations 실패: Pro 운영 API 회귀
- Merchant blocked step 실패: 권한 차단 회귀

### 다음 조치 순서

1. `[FAIL]` step 이름을 먼저 확인한다.
2. response body를 확인한다.
3. health 실패면 서버 실행 상태를 확인한다.
4. login/region 실패면 `seed_demo.py`를 다시 실행한다.
5. Pro Operations 실패면 admin API router와 관련 service를 확인한다.
6. 403 권한 테스트 실패면 auth dependency와 role 검증을 확인한다.

## 5. Weekly Report batch가 SKIPPED로 나오는 경우

### 증상

`python scripts/run_weekly_report_batch.py` 결과:

```json
{
  "run_type": "SCHEDULED",
  "status": "SKIPPED",
  "message": "동일 기간에 이미 완료된 SCHEDULED batch run이 있어 중복 실행하지 않았습니다."
}
```

### 확인 명령어

```powershell
cd backend
python scripts/run_weekly_report_batch.py
```

관리자 화면:

```text
/admin/pro/weekly-report-batches
```

### 정상 판단 기준

- 동일 기간에 이미 `COMPLETED` 상태의 `SCHEDULED` batch run이 있으면 `SKIPPED`는 정상이다.
- 중복 snapshot 생성을 막는 안전장치다.

### 비정상 판단 기준

- 동일 기간 completed run이 없는데도 계속 `SKIPPED`
- `FAILED` 또는 예외 traceback 발생
- target merchant count가 비정상적으로 0

### 다음 조치 순서

1. Admin Batch Monitor에서 최근 batch run 기간과 상태를 확인한다.
2. 같은 `start_date/end_date`의 `COMPLETED` run이 있는지 확인한다.
3. 중복 실행 방지라면 조치하지 않는다.
4. 실패라면 batch run item의 merchant별 message를 확인한다.
5. 실패 item만 재실행하려면 admin retry failed flow를 사용한다.

## 6. Pro Health Alert check 결과가 skip되는 경우

### 증상

`python scripts/run_pro_health_alert_check.py` 결과:

```json
{
  "overall_status": "WARNING",
  "generated_count": 0,
  "skipped_count": 2
}
```

### 확인 명령어

```powershell
cd backend
python scripts/run_pro_health_alert_check.py
```

관리자 화면:

```text
/admin/pro/operations
/admin/pro/operations/health-alerts
```

### 정상 판단 기준

- 같은 source_key의 OPEN 또는 ACKNOWLEDGED alert가 이미 있으면 중복 생성을 막고 skip한다.
- `generated_count=0`, `skipped_count>0`는 중복 방지로 정상일 수 있다.

### 비정상 판단 기준

- health check 자체가 예외로 실패
- alert list 조회가 실패
- 동일 source_key가 없는데도 skip

### 다음 조치 순서

1. Pro Operations Health Check 상태를 확인한다.
2. Health Alerts 화면에서 OPEN/ACKNOWLEDGED alert를 확인한다.
3. 이미 열린 alert가 있다면 acknowledge 또는 resolve 처리한다.
4. 해결 후 다시 CLI를 실행해 신규 생성/skip 결과를 확인한다.

## 7. frontend build 실패

### 증상

- `npm run lint` 실패
- `npm run build` 실패
- TypeScript compile 오류
- Next.js route build 오류

### 확인 명령어

```powershell
cd frontend
npm run lint
npm run build
```

### 정상 판단 기준

- lint가 오류 없이 종료
- build가 `Compiled successfully` 출력
- route list가 출력됨

### 비정상 판단 기준

- ESLint error
- TypeScript type error
- missing env var로 build 실패
- server/client component 경계 오류

### 다음 조치 순서

1. lint 오류인지 build 오류인지 구분한다.
2. TypeScript 오류의 파일/라인을 먼저 확인한다.
3. env 관련 오류라면 frontend `.env.local` 또는 배포 환경변수를 확인한다.
4. route build 오류라면 해당 page/component의 client/server boundary를 확인한다.

## 8. 로그인 / 권한 오류

### 증상

- demo account 로그인 실패
- admin 화면 접근 시 403
- merchant/customer가 admin API 접근 가능하거나, admin이 admin API 접근 실패
- smoke test의 `Merchant blocked from Admin Pro Operations summary` 실패

### 확인 명령어

```powershell
cd backend
python scripts/seed_demo.py
python scripts/smoke_test.py
```

Demo accounts:

```text
customer@breadgo.test / 12345678
merchant@breadgo.test / 12345678
admin@breadgo.test / 12345678
```

### 정상 판단 기준

- customer는 customer flow 접근 가능
- merchant는 merchant flow 접근 가능
- admin은 admin flow 접근 가능
- merchant/customer의 admin API 접근은 `403`

### 비정상 판단 기준

- demo account token 발급 실패
- 역할별 화면 redirect가 잘못됨
- admin API가 merchant/customer에게 열림
- admin API가 admin에게도 막힘

### 다음 조치 순서

1. seed_demo를 다시 실행한다.
2. auth login response가 access token을 반환하는지 확인한다.
3. user role 값이 기대한 role인지 확인한다.
4. FastAPI dependency `get_current_admin`, `get_current_merchant` 계열을 확인한다.
5. frontend route guard와 API auth header 전달 여부를 확인한다.

## 9. Mock payment / Mock delivery / Health Alert mock 혼동

### 증상

- 실제 결제가 된 것으로 오해
- 실제 이메일/카카오/Push가 발송된 것으로 오해
- Health Alert가 외부 Slack/Discord/Webhook으로 발송된 것으로 오해

### 확인 명령어 / 확인 위치

문서:

```text
README.md
docs/release-note-v0.1.1.md
docs/pro-operations-demo-readiness.md
docs/operations-stabilization-phase113.md
```

화면:

```text
/admin/pro/weekly-report-deliveries
/merchant/pro/weekly-report-notifications
/admin/pro/operations/health-alerts
```

### 정상 판단 기준

- Mock payment는 실제 PG 결제가 아니다.
- In-app mock delivery는 BreadGo 내부 알림 기록만 생성한다.
- Health Alert mock flow는 관리자 내부 alert만 생성한다.
- 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않는다.

### 비정상 판단 기준

- 화면/문서가 실제 외부 발송처럼 보임
- 외부 token 입력/저장 UI가 존재함
- 실제 수신자 이메일/전화번호를 요구함

### 다음 조치 순서

1. 화면 문구에 "Mock", "내부 알림", "외부 발송 없음"이 보이는지 확인한다.
2. release note의 Known limitations를 확인한다.
3. 외부 연동 관련 코드를 추가하지 않았는지 확인한다.
4. 실제 외부 발송 요구가 생기면 adapter 설계와 개인정보/동의 정책부터 별도 Phase로 진행한다.

## 10. 환경변수 누락 의심

### 증상

- DB 연결 실패
- JWT/auth 오류
- frontend API 호출 base URL 오류
- 이미지 업로드 또는 blob 관련 오류
- 배포 환경에서는 되지 않고 로컬에서만 됨, 또는 반대

### 확인 명령어 / 확인 위치

Backend:

```powershell
cd backend
python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm run build
```

확인 위치:

```text
backend/.env
frontend/.env.local
Render environment variables
Vercel environment variables
Neon/PostgreSQL connection settings
```

### 정상 판단 기준

- backend가 DB에 연결 가능
- alembic migration 가능
- frontend build 가능
- frontend가 올바른 backend URL로 요청

### 비정상 판단 기준

- DB URL 누락 또는 잘못된 DB 연결
- JWT secret 누락
- frontend API base URL 누락
- blob/upload 관련 env 누락

### 다음 조치 순서

1. 로컬 env 파일이 있는지 확인한다.
2. 배포 환경이면 Render/Vercel dashboard의 env var를 확인한다.
3. DB URL이 운영/로컬 중 의도한 DB인지 확인한다.
4. secret/token 값을 문서나 git에 직접 저장하지 않는다.
5. 필요하면 다음 Phase에서 `.env.example`과 environment reference 문서를 추가한다.

## 빠른 판단표

| 증상 | 먼저 볼 곳 | 정상일 수 있는 경우 |
| --- | --- | --- |
| `SKIPPED` batch | Admin Batch Monitor | 동일 기간 completed scheduled run 존재 |
| Health alert skip | Health Alerts 화면 | 같은 source_key OPEN/ACKNOWLEDGED alert 존재 |
| smoke region empty | `seed_demo.py` | seed 재실행 후 회복 가능 |
| admin API 403 | user role / token | merchant/customer라면 정상 |
| build env error | `.env.local`, Vercel env | env 누락이면 설정 필요 |

## 다음 개선 후보

- Pro Operations smoke coverage 추가 확대
- `.env.example` / environment reference 문서 추가
- Admin Batch / Delivery 상태 help text 보강
- Mock flow 화면 문구 보강
- 운영 URL 기준 smoke test와 로컬 smoke test 분리
