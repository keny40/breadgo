# Pro Health Alert Scheduler Runbook

## 목적

Pro Health Alert Scheduler는 BreadGo Pro 운영 상태를 주기적으로 점검하고, Health Check 결과가 `WARNING` 또는 `CRITICAL`일 때 외부 발송 없이 BreadGo 관리자 내부 alert만 생성하는 운영 보조 흐름이다.

실제 이메일, 카카오, Push, Slack, Discord, Webhook 발송은 하지 않는다. 외부 발송 API도 호출하지 않는다.

## CLI 실행 방법

백엔드 작업 디렉터리에서 실행한다.

```bash
cd backend
python scripts/run_pro_health_alert_check.py
```

출력에는 다음 정보가 포함된다.

- `overall_status`
- `generated_count`
- `skipped_count`
- `severity_counts`
- `message`

## Linux Cron 예시

아래 경로는 예시이며 실제 배포 환경에 맞게 수정해야 한다.

```cron
*/30 * * * * cd /app/backend && /usr/bin/python scripts/run_pro_health_alert_check.py >> /var/log/breadgo-pro-health-alert.log 2>&1
```

## Windows Task Scheduler 예시

- Program/script: `python`
- Add arguments: `scripts/run_pro_health_alert_check.py`
- Start in: `C:\Users\keny4\Documents\breadgo\backend`

## Health Status 기준

- `OK`: 운영 상태가 정상이며 alert를 생성하지 않는다.
- `WARNING`: 확인이 필요한 운영 상태이며 내부 alert 생성 대상이다.
- `CRITICAL`: 즉시 확인이 필요한 운영 상태이며 내부 alert 생성 대상이다.

세부 기준은 Pro Operations Health Check API의 scheduler, batch, delivery, notification, audit log, purge policy 상태를 따른다.

## 중복 Alert 방지 기준

- Health item별 `source_key`는 `scheduler:WARNING`, `batch:CRITICAL` 같은 형식이다.
- 같은 `source_key`의 `OPEN` 또는 `ACKNOWLEDGED` alert가 이미 있으면 새 alert를 만들지 않고 `skipped_count`에 포함한다.
- `RESOLVED` alert는 중복 방지 대상이 아니므로 동일 문제가 다시 발생하면 새 alert를 만들 수 있다.

## 운영자 확인 순서

1. Admin으로 `/admin/pro/operations`에 접속한다.
2. Pro Health Check의 `overall_status`와 세부 상태를 확인한다.
3. `/admin/pro/operations/health-alerts`에서 생성된 alert를 확인한다.
4. 원인 확인을 시작하면 alert를 `확인` 처리한다.
5. 관련 Batch Monitor, Delivery Preview, Audit Log, Notification 상태를 점검한다.
6. 조치가 끝나면 alert를 `해결 처리`한다.
7. 반복적으로 같은 `source_key`가 발생하면 데이터 상태나 스케줄러 실행 주기를 별도로 점검한다.

## 개인정보 및 민감정보 원칙

Health alert와 audit log에는 이메일, 전화번호, 주소, 외부 발송 토큰을 저장하거나 노출하지 않는다.

저장 가능한 정보는 상태, count, run id, reason 같은 운영 진단용 최소 정보로 제한한다.

## 현재 한계

- 실제 외부 발송 없음
- 자동 복구 없음
- 실제 서버 cron 등록은 운영자가 별도로 수행
- 세부 관리자 권한 분리 없음
