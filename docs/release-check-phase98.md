# Phase 98 Release Check

## 작업 목적

BreadGo Pro Health Check와 Health Alert 생성을 운영 서버 cron에서 실행할 수 있도록 CLI mock scheduler와 운영 runbook을 추가했다.

이번 Phase에서도 실제 이메일, 카카오, Push, Slack, Discord, Webhook 발송과 외부 발송 API 연동은 수행하지 않는다. 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않는다.

## 변경 사항

- Health Alert CLI 스크립트 추가
  - `backend/scripts/run_pro_health_alert_check.py`
- CLI 실행 결과를 Pro Operations Audit Log로 기록
  - `action_type=RUN_HEALTH_ALERT_CHECK_CLI`
  - `target_type=HEALTH_ALERT`
- 운영 runbook 추가
  - `docs/pro-health-alert-scheduler-runbook.md`
- `/admin/pro/operations/health-alerts` 화면에 cron 실행 안내 문구 추가

## DB 변경 여부

DB 변경 없음.

기존 `pro_health_alerts`와 `pro_operations_audit_logs` 테이블을 재사용한다.

## CLI 실행 방법

```bash
cd backend
python scripts/run_pro_health_alert_check.py
```

동작 기준:

- Health `OK`: alert를 생성하지 않고 안전하게 종료
- Health `WARNING`/`CRITICAL`: 기존 Health Alert 생성 로직 재사용
- 같은 `source_key`의 `OPEN`/`ACKNOWLEDGED` alert는 중복 생성하지 않고 skip

## Cron 예시

```cron
*/30 * * * * cd /app/backend && /usr/bin/python scripts/run_pro_health_alert_check.py >> /var/log/breadgo-pro-health-alert.log 2>&1
```

## Audit Log 기록 여부

CLI 실행 결과는 가능하면 항상 audit log로 남긴다.

- 성공: `RUN_HEALTH_ALERT_CHECK_CLI` / `SUCCESS`
- 실패: `RUN_HEALTH_ALERT_CHECK_CLI` / `FAILED`
- actor는 CLI 실행이므로 `SYSTEM`으로 기록
- metadata에는 `overall_status`, `generated_count`, `skipped_count`만 저장

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
  - 최초 1회 로컬 서버 미기동으로 health check 연결 거부
  - 백엔드 서버 실행 후 재검증 PASS
- `python scripts/run_weekly_report_batch.py`: PASS
  - 동일 기간 SCHEDULED 중복 실행 방지 `SKIPPED` 확인
- `python scripts/run_pro_health_alert_check.py`: PASS
- health가 OK일 때 alert 미생성 확인: PASS
  - 스크립트 모듈의 health 계산 결과를 OK로 대체한 직접 호출에서 `generated_count=0`, `exit_code=0` 확인
- health가 WARNING/CRITICAL일 때 alert 생성 확인: PASS
  - 로컬 데이터 기준 `overall_status=WARNING`, alert 생성 확인
- 동일 source_key OPEN/ACKNOWLEDGED alert 중복 생성 방지 확인: PASS
  - 반복 실행 시 `generated_count=0`, `skipped_count=2`
- CLI 실행 결과 콘솔 출력 확인: PASS
- CLI 실행 audit log 생성 확인: PASS
  - `RUN_HEALTH_ALERT_CHECK_CLI`, `actor_role=SYSTEM`, `status=SUCCESS`
- 기존 health alert API 유지 확인: PASS
- 기존 health check API 유지 확인: PASS
- 기존 audit list/export/purge 유지 확인: PASS
- 기존 scheduler CLI 유지 확인: PASS
- 기존 retry failed 유지 확인: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## 남은 한계

- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송은 없다.
- 외부 발송 API 연동은 없다.
- 자동 복구는 없다.
- 실제 서버 cron 등록은 운영자가 별도로 수행해야 한다.
- 세부 관리자 권한 분리는 아직 없다.
