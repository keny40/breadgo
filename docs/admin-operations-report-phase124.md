# Admin Operations Report Phase 124

## 목적

v0.1.2 이후 우선순위였던 관리자 운영 리포트 화면을 고도화해, 외부 시연자가 관리자 화면에서 BreadGo MVP 운영 현황과 BreadGo Pro Operations 흐름을 더 쉽게 이해하도록 정리했다.

이번 Phase에서는 DB schema, migration, 실제 외부 API 연동을 변경하지 않았다.

## 관리자 Dashboard에서 확인할 항목

관리자 Dashboard는 두 단계로 설명한다.

1. MVP 운영 지표
   - 사용자, 가맹점, 매장, 상품 수
   - 활성 상품 수
   - 예약, 픽업 완료, 취소 수
   - Mock 결제 완료/실패/취소 수
   - Mock 결제 금액

2. Pro Operations 연결
   - Weekly Report Batch Monitor
   - Delivery Preview / 내부 알림 Mock
   - Health Alerts
   - Audit Log / 운영 이력

Dashboard 상단에는 `오늘 먼저 확인할 운영 현황` 카드를 추가해, 시연자가 MVP 지표를 본 뒤 Pro Operations로 자연스럽게 이동할 수 있게 했다.

## Weekly Report Batch 의미

Weekly Report Batch는 각 가맹점의 Weekly Report snapshot을 생성하거나 업데이트하는 운영 작업이다.

- `SCHEDULE_PREP`: 자동 생성 준비 또는 관리자 수동 테스트 흐름
- `SCHEDULED`: scheduler CLI 또는 운영 scheduler가 실행한 흐름
- `RETRY`: 실패한 merchant item만 재실행한 흐름
- `MANUAL_TEST`: 단일 merchant 테스트성 실행

관리자 Batch Monitor는 batch run 단위의 성공/실패/스킵 수와 merchant별 item 상태를 보여준다.

## Health Alert 의미

Health Alert는 Pro Operations Health Check 결과가 `WARNING` 또는 `CRITICAL`일 때 생성되는 관리자 내부 알림이다.

- 실제 Slack, Discord, Email, Webhook 발송은 하지 않는다.
- 동일 원인의 OPEN 또는 ACKNOWLEDGED alert는 중복 생성하지 않는다.
- 관리자는 alert를 확인 처리하거나 해결 처리할 수 있다.

## 상태 해석

- `PASS`
  - smoke test나 검증 명령이 정상 종료된 상태다.
  - 기능 흐름이 기대한 API 응답을 받았음을 의미한다.

- `SKIPPED`
  - 항상 실패가 아니다.
  - Weekly Report scheduler에서는 동일 기간에 이미 완료된 `SCHEDULED` batch가 있으면 중복 생성을 막기 위해 `SKIPPED`가 정상적으로 나올 수 있다.
  - Delivery나 notification 흐름에서는 대상 snapshot 또는 unread notification이 없을 때 제외 처리될 수 있다.

- `WARNING`
  - Health Check에서 주의가 필요한 항목이 있다는 뜻이다.
  - 기존 OPEN/ACKNOWLEDGED alert가 있으면 health alert CLI가 새 alert를 만들지 않고 중복 skip할 수 있다.
  - 데모에서는 `WARNING` 상태를 통해 내부 Health Alert 흐름을 설명할 수 있다.

## Mock / 실제 연동 경계

이번 Phase에서도 아래 항목은 실제 외부 연동이 아니다.

- Mock payment: 실제 PG 승인, 카드 청구 없음
- Mock refund: 실제 카드 환불 없음
- Mock delivery: 실제 배송 provider 호출 없음
- In-app mock delivery: 실제 이메일/카카오/Push 발송 없음
- Health Alert mock: 실제 Slack/Discord/Webhook 발송 없음
- POS sync: 실제 POS API 호출 없음

관리자 화면에는 실제 PG, 배송 provider, 이메일/카카오/Push 발송을 호출하지 않는다는 안내를 유지/보강했다.

## 시연 순서

권장 관리자 시연 순서:

1. `/admin` 접속
2. `오늘 먼저 확인할 운영 현황` 카드 설명
3. 활성 상품 / 예약 / Mock 결제 수치 확인
4. `Pro Operations`로 이동
5. Health Check와 Quick Actions 설명
6. `Weekly Batch Monitor`에서 `SCHEDULED`, `RETRY`, `SKIPPED` 상태 설명
7. `Delivery Preview`에서 내부 알림 Mock과 실제 외부 발송 없음 설명
8. `Health Alerts`에서 WARNING/CRITICAL alert 확인/해결 흐름 설명
9. 필요하면 Audit Log Explorer로 운영 액션 추적 설명

## 화면 변경 요약

- `/admin`
  - 운영 리포트 체크포인트 카드 추가
  - Pro Operations / Batch Monitor / Delivery Preview / Health Alerts 연결 강화
  - Mock 결제와 실제 외부 연동 없음 안내 보강

- `/admin/pro/weekly-report-batches`
  - Pro Operations와 Health Alerts 이동 링크 추가
  - SCHEDULED / RETRY / SKIPPED 의미 안내 보강

- `README.md`
  - Phase 124 관리자 운영 리포트 문서 링크 추가

## 향후 v0.1.3 후보

1. 관리자 운영 리포트 drill-down
   - batch run, delivery run, health alert, audit log를 하나의 timeline으로 연결한다.

2. 점주별 운영 상태 요약
   - merchant별 Weekly Report 생성 상태, unread notification, health issue 요약을 추가한다.

3. 운영 리포트 export
   - 관리자용 운영 summary CSV export 또는 snapshot 저장을 검토한다.

4. 실제 외부 연동 사전 설계
   - PG, 배송, POS, 외부 알림 연동 전 보안/토큰/실패 재시도 정책을 정리한다.

5. Pro Operations read-only API 확장
   - DB 변경 없이 관리자 summary에서 batch/delivery/health/audit 요약을 더 자세히 제공하는 방식을 검토한다.

## 검증 결과

- `git status`: 변경 파일 확인
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS
- `python scripts/run_pro_health_alert_check.py`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## 변경 여부

- 기능 코드 변경: 화면 안내 / 링크 / 운영 리포트 설명 중심
- DB schema 변경: 없음
- migration 추가: 없음
- 신규 API 추가: 없음
- 실제 외부 API 연동 추가: 없음
- 실제 결제 추가: 없음
- 실제 알림 발송 추가: 없음
- 새 tag / 새 Release 생성: 없음
- 기존 tag 삭제/이동: 없음

## Suggested commit message

`Improve admin operations report UX`
