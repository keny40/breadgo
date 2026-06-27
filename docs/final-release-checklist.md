# Final Release Checklist

## Backend

- [ ] `cd backend`
- [ ] `python -m compileall app scripts`
- [ ] `python -m alembic upgrade head`
- [ ] `python scripts/seed_demo.py`
- [ ] 백엔드 서버 실행
- [ ] `python scripts/smoke_test.py`
- [ ] `python scripts/run_weekly_report_batch.py`
- [ ] `python scripts/run_pro_health_alert_check.py`

## Frontend

- [ ] `cd frontend`
- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] `npm run dev`

## 주요 화면 접속

- [ ] `/`
- [ ] `/demo`
- [ ] `/products`
- [ ] `/my-reservations`
- [ ] `/merchant`
- [ ] `/merchant/products`
- [ ] `/merchant/orders`
- [ ] `/merchant/pro`
- [ ] `/merchant/pro/weekly-report-notifications`
- [ ] `/admin`
- [ ] `/admin/pro/operations`
- [ ] `/admin/pro/weekly-report-batches`
- [ ] `/admin/pro/weekly-report-deliveries`
- [ ] `/admin/pro/operations/audit-logs`
- [ ] `/admin/pro/operations/health-alerts`

## 개인정보/토큰 확인

- [ ] Pro delivery/audit/health log에 이메일, 전화번호, 주소, 외부 발송 토큰 미저장 확인
- [ ] CSV export에 metadata_json과 개인정보성 값 미포함 확인
- [ ] 화면에 외부 발송 수신 정보 미표시 확인

## Mock / 미연동 구분

- [ ] Mock 결제/Mock 환불임을 설명
- [ ] Mock POS sync임을 설명
- [ ] In-app mock delivery임을 설명
- [ ] 실제 이메일/카카오/Push/Slack/Discord/Webhook 미연동임을 설명
- [ ] 실서버 cron 등록은 별도임을 설명

## Git 확인

- [ ] `git status`
- [ ] `git log --oneline -10`
- [ ] 작업 의도와 무관한 파일이 섞이지 않았는지 확인
- [ ] 커밋 메시지 확인
- [ ] push 전 원격/브랜치 확인

## 참고 문서

- [README](../README.md)
- [MVP 기능 요약](mvp-feature-summary.md)
- [데모 계정과 시나리오](demo-accounts-and-scenarios.md)
- [Pro 운영 데모 준비 문서](pro-operations-demo-readiness.md)
- [Pro Demo Quickstart](pro-demo-quickstart.md)
- [Weekly Report batch runbook](weekly-report-batch-runbook.md)
- [Health Alert scheduler runbook](pro-health-alert-scheduler-runbook.md)
- [Audit Log 보관 정책](pro-audit-log-retention-policy.md)
