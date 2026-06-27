# BreadGo Pro Demo Quickstart

## 목적

BreadGo Pro 운영 기능을 로컬에서 데모하기 위한 빠른 실행 가이드다. Weekly Report batch, delivery preview, 내부 알림, audit log, health check, health alert 흐름을 한 번에 시연할 수 있도록 정리한다.

실제 이메일, 카카오, Push, Slack, Discord, Webhook 발송은 없다. 외부 발송 API도 호출하지 않는다. 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않는다.

## 로컬 실행 순서

### Backend 준비

```bash
cd backend
python -m alembic upgrade head
python scripts/seed_demo.py
```

### Backend 서버 실행

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Pro 운영 CLI 실행

```bash
cd backend
python scripts/run_weekly_report_batch.py
python scripts/run_pro_health_alert_check.py
```

`run_weekly_report_batch.py`는 최근 7일 Weekly Report snapshot batch를 `SCHEDULED`로 기록한다. 동일 기간에 이미 완료된 scheduler run이 있으면 중복 실행하지 않고 안전하게 종료한다.

`run_pro_health_alert_check.py`는 Pro Health Check를 수행하고 WARNING/CRITICAL 항목이 있으면 내부 Health Alert를 생성한다. 동일 원인의 OPEN/ACKNOWLEDGED alert는 중복 생성하지 않는다.

### Frontend 준비

```bash
cd frontend
npm run lint
npm run build
npm run dev
```

## 관리자 데모 화면

- `/admin`
  - 관리자 홈
- `/admin/pro/operations`
  - Pro 운영 대시보드, Health Check, Quick Actions, Health Alerts, Audit Trail 요약
- `/admin/pro/weekly-report-batches`
  - Weekly Report batch 실행 이력, SCHEDULED/RETRY/SCHEDULE_PREP 구분, 실패 건 재실행
- `/admin/pro/weekly-report-deliveries`
  - Delivery 미리보기, 내부 알림 Mock 발송, 미확인 리마인드, notification analytics
- `/admin/pro/operations/audit-logs`
  - Audit Log Explorer, 필터, CSV 다운로드, 오래된 로그 purge preview/execute
- `/admin/pro/operations/health-alerts`
  - Health Alert 목록, 확인 처리, 해결 처리

## 점주 데모 화면

- `/merchant/pro`
  - 점주 BreadGo Pro 대시보드와 Weekly Report 알림 진입
- `/merchant/pro/weekly-report-notifications`
  - Weekly Report 내부 알림 목록, 미확인 개수, 개별 읽음, 모두 읽음 처리

## 권장 데모 순서

1. 관리자 로그인 후 `/admin/pro/operations` 접속
2. `상태 다시 점검`으로 Health Check 확인
3. `전체 Weekly Report 생성` Quick Action 실행
4. `/admin/pro/weekly-report-batches`에서 batch 결과 확인
5. `Delivery 미리보기 생성` 실행
6. `/admin/pro/weekly-report-deliveries`에서 READY/SKIPPED 대상 확인
7. READY item이 있으면 `내부 알림 Mock 발송` 실행
8. 점주 화면 `/merchant/pro/weekly-report-notifications`에서 알림 확인
9. 점주가 `리포트 확인하기`와 `모두 읽음 처리` 흐름 확인
10. 관리자 Delivery 화면에서 notification analytics 확인
11. 미확인 알림이 있으면 `미확인 알림 리마인드 생성` 실행
12. `/admin/pro/operations/audit-logs`에서 운영 액션 이력 확인
13. `감사 로그 CSV 다운로드` 실행
14. `오래된 감사 로그 정리`에서 삭제 대상 미리보기 확인
15. `/admin/pro/operations/health-alerts`에서 alert 확인/해결 처리
16. CLI scheduler 명령을 설명하고 운영 cron 연결은 아직 수동 준비 단계임을 안내

## 검증 명령

```bash
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/seed_demo.py
python scripts/smoke_test.py
python scripts/run_weekly_report_batch.py
python scripts/run_pro_health_alert_check.py
```

```bash
cd frontend
npm run lint
npm run build
```

## 주의사항

- 실제 외부 발송은 하지 않는다.
- 실서버 cron 등록은 이 문서의 범위 밖이다.
- 자동 복구, 자동 purge scheduler, 세부 관리자 권한 분리, 대량 비동기 큐는 아직 없다.
- Audit Log CSV를 외부로 보관할 경우 별도 보안 관리가 필요하다.
- 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 화면에 표시하지 않는다.
