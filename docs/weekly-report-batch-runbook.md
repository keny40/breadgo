# BreadGo Pro Weekly Report Batch Runbook

## 목적

BreadGo Pro Weekly Report batch는 가맹점별 주간 운영 리포트 snapshot을 생성하거나 업데이트하는 운영 작업이다.
현재는 실제 외부 발송 없이 DB에 Weekly Report snapshot과 batch run/item 실행 이력을 저장한다.

이 문서는 운영자가 수동 실행, scheduler CLI 실행, 실패 item 재실행을 안전하게 처리하기 위한 기준이다.

## 전체 흐름

1. Weekly Report 계산
   - 최근 7일 또는 지정 기간 기준으로 Daily Brief snapshot과 실시간 데이터를 집계한다.
   - 매출, 예약, 픽업, 취소, 폐기 절감, 재고 알림, 추천 액션, POS/CSV 상태를 요약한다.

2. Weekly Report snapshot 저장
   - 같은 `merchant_id + start_date + end_date` snapshot이 없으면 새로 생성한다.
   - 이미 있으면 최신 값으로 업데이트한다.

3. Batch run 기록
   - 실행 단위는 `pro_weekly_report_batch_runs`에 저장한다.
   - merchant별 결과는 `pro_weekly_report_batch_run_items`에 저장한다.
   - 개인정보, 연락처, 주소, 토큰은 저장하지 않는다.

4. Admin Batch Monitor 확인
   - `/admin/pro/weekly-report-batches`에서 실행 상태와 item 결과를 확인한다.

## Admin 수동 실행 흐름

관리자 화면에서 전체 가맹점 주간 리포트를 수동으로 생성/업데이트할 수 있다.

1. 관리자 계정으로 로그인한다.
2. `/admin/pro/weekly-report-batches`로 이동한다.
3. `전체 배치 미리보기`를 눌러 대상 기간과 가맹점 수를 확인한다.
4. `전체 가맹점 리포트 생성 테스트`를 누른다.
5. Batch Monitor 목록에서 새 실행 건을 확인한다.

수동 실행은 `run_type=SCHEDULE_PREP`로 기록된다.
동일 기간 snapshot이 있어도 업데이트할 수 있다.

## Scheduler CLI 실행 흐름

운영 서버 cron 또는 작업 스케줄러에서는 CLI를 실행한다.

```powershell
cd backend
python scripts/run_weekly_report_batch.py
```

CLI 실행은 전체 merchant를 대상으로 최근 7일 Weekly Report snapshot을 생성/업데이트한다.
실행 결과는 `run_type=SCHEDULED`로 기록된다.

동일 기간에 이미 `COMPLETED` 상태의 `SCHEDULED` batch run이 있으면 중복 실행하지 않고 `SKIPPED`로 종료한다.

## Linux cron 예시

아래 예시는 Linux 운영 서버에서 매주 월요일 오전 8시에 실행하는 cron 예시다.
실제 `/app/backend`, `/usr/bin/python`, 로그 경로는 배포 환경에 맞게 수정해야 한다.

```cron
# BreadGo Weekly Report batch - adjust paths for your deployment environment.
0 8 * * MON cd /app/backend && /usr/bin/python scripts/run_weekly_report_batch.py >> /var/log/breadgo-weekly-report.log 2>&1
```

운영 적용 전 확인할 것:

- `DATABASE_URL`이 운영 DB를 가리키는지 확인한다.
- Python 가상환경을 사용한다면 cron 명령에서 해당 Python 경로를 사용한다.
- 로그 파일 경로에 쓰기 권한이 있는지 확인한다.
- 최초 1회 수동 실행으로 정상 동작을 확인한다.

## Windows Task Scheduler 예시

Windows 개발/운영 환경에서는 작업 스케줄러에서 아래처럼 등록할 수 있다.

- Program/script: `python`
- Add arguments: `scripts/run_weekly_report_batch.py`
- Start in: `C:\Users\keny4\Documents\breadgo\backend`

권장 설정:

- Trigger: 매주 월요일 오전 8시
- Run whether user is logged on or not: 운영 환경 정책에 맞게 선택
- History: 작업 기록 활성화
- 로그가 필요하면 PowerShell 래퍼 또는 별도 로그 리다이렉션을 사용한다.

## Retry Failed 흐름

일부 merchant item이 실패하면 전체 batch를 다시 돌리지 않고 실패 item만 재실행할 수 있다.

1. `/admin/pro/weekly-report-batches`에 접속한다.
2. `PARTIAL` 또는 `FAILED` batch run을 찾는다.
3. item 목록에서 `FAILED` merchant가 있는지 확인한다.
4. `실패 건 재실행` 버튼을 누른다.
5. 새 `run_type=RETRY` batch run이 생성되는지 확인한다.
6. Retry batch run의 item 결과가 `SUCCESS`인지 확인한다.

Retry는 원본 batch run을 수정하지 않는다.
원본 batch run id는 새 retry batch run의 message에 기록한다.

## Batch Run 상태값

| 상태 | 의미 |
| --- | --- |
| `PENDING` | 향후 예약/대기 상태를 표현하기 위한 상태다. 현재 MVP에서는 주로 사용하지 않는다. |
| `RUNNING` | 향후 비동기 실행 중 상태를 표현하기 위한 상태다. 현재 MVP에서는 `STARTED` 또는 즉시 완료 흐름을 사용한다. |
| `STARTED` | batch run이 시작되어 결과 집계 전인 상태다. |
| `COMPLETED` | 대상 merchant item이 모두 성공했다. |
| `PARTIAL` | 일부 merchant item은 성공했고 일부는 실패했다. |
| `FAILED` | 대상 merchant item이 모두 실패했거나 실행 자체가 실패했다. |
| `SKIPPED` | 동일 기간 중복 SCHEDULED 실행 등 안전 조건에 의해 실행하지 않았다. |

## Run Type 의미

| run_type | 의미 |
| --- | --- |
| `MANUAL_TEST` | 가맹점 화면에서 단일 merchant 대상으로 자동 생성 테스트를 실행한 기록이다. |
| `SCHEDULE_PREP` | 관리자 화면에서 전체 merchant 대상으로 수동 실행한 기록이다. |
| `SCHEDULED` | cron 또는 Task Scheduler에서 CLI로 자동 실행한 기록이다. |
| `RETRY` | 실패 item만 다시 실행한 기록이다. |

## 운영자 장애 대응 순서

1. Admin Batch Monitor 접속
   - `/admin/pro/weekly-report-batches`를 연다.

2. 최근 batch run 상태 확인
   - 최신 실행의 `status`, `run_type`, 기간, 성공/실패/스킵 수를 확인한다.

3. `SKIPPED`인 경우
   - 동일 기간에 이미 `COMPLETED` 상태의 `SCHEDULED` batch run이 있는지 확인한다.
   - 중복 방지라면 정상 동작으로 본다.

4. `PARTIAL`인 경우
   - item 목록에서 `FAILED` merchant를 확인한다.
   - `실패 건 재실행` 버튼으로 `RETRY`를 실행한다.
   - Retry 결과가 `COMPLETED`인지 확인한다.

5. `FAILED`인 경우
   - 서버 로그와 cron/Task Scheduler 로그를 확인한다.
   - DB 연결, migration 상태, 환경 변수, 실행 경로를 확인한다.
   - 필요하면 관리자 화면에서 수동 batch를 다시 실행한다.

6. 반복 실패 merchant 확인
   - 해당 merchant의 상품, Daily Brief snapshot, Weekly Report 계산에 필요한 데이터 상태를 확인한다.
   - 특정 merchant만 반복 실패하면 전체 batch보다 개별 데이터 상태를 먼저 본다.

7. 외부 발송 확인
   - 현재 MVP에는 이메일/카카오/Push 발송 기능이 없다.
   - 운영 확인 범위는 snapshot 생성/업데이트와 batch run/item 기록까지다.

## 개인정보/민감정보 원칙

Weekly Report batch run과 item에는 운영 상태를 확인하는 데 필요한 최소 정보만 저장한다.

저장하거나 노출하지 않는 정보:

- 고객 연락처
- 고객 주소
- 계좌번호 전체
- JWT/access token
- 비밀번호
- 외부 API key
- 결제 민감정보

운영 로그에도 위 정보를 남기지 않는다.

## 빠른 점검 명령

```powershell
cd backend
python -m alembic upgrade head
python scripts/run_weekly_report_batch.py
```

실행 후 관리자 화면에서 `run_type=SCHEDULED`로 필터링해 결과를 확인한다.
