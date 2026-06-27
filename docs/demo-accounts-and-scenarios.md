# Demo Accounts and Scenarios

## 데모 계정

`backend/scripts/seed_demo.py` 기준 데모 계정은 아래와 같다.

```text
admin@breadgo.test / 12345678
merchant@breadgo.test / 12345678
customer@breadgo.test / 12345678
```

역할:

- admin: 관리자
- merchant: 점주
- customer: 소비자

`seed_demo.py`는 데모 매장 3개와 ACTIVE 상품 7개를 생성한다. 데모 계정은 운영 환경에서 사용하면 안 된다.

## 관리자 데모 시나리오

1. `admin@breadgo.test`로 로그인
2. `/admin`에서 전체 운영 현황 확인
3. 가맹점, 매장, 상품, 예약, 결제 목록 확인
4. `/admin/settlements`에서 정산 관리 확인
5. `/admin/ops`에서 기본 운영 상태 확인
6. `/admin/pro/operations`에서 Pro 운영 상태 확인

## 점주 데모 시나리오

1. `merchant@breadgo.test`로 로그인
2. `/merchant`에서 점주 대시보드 확인
3. `/merchant/stores`에서 매장 확인
4. `/merchant/products`에서 상품 등록/수정/숨김/다시 판매 확인
5. `/merchant/products/import`에서 CSV import 흐름 확인
6. `/merchant/orders`에서 주문 관리 확인
7. `/merchant/pickup`에서 픽업 코드 확인과 픽업 확정
8. `/merchant/settlements`에서 정산 내역 확인

## 소비자 데모 시나리오

1. `customer@breadgo.test`로 로그인
2. `/products`에서 지역 상품 조회
3. 상품 수령 방식 선택
4. 예약 생성
5. Mock 결제 진행
6. `/my-reservations`에서 예약, 픽업 코드, 상태 이력 확인
7. `/my-payments`에서 결제 상태 확인
8. `/notifications`에서 알림 확인 및 읽음 처리

## BreadGo Pro 운영 데모 시나리오

1. 관리자 로그인
2. `/admin/pro/operations` 접속
3. Health Check 확인
4. `전체 Weekly Report 생성` 실행
5. `/admin/pro/weekly-report-batches`에서 batch 결과 확인
6. Delivery 미리보기 생성
7. `/admin/pro/weekly-report-deliveries`에서 READY/SKIPPED 대상 확인
8. READY item이 있으면 내부 알림 Mock 발송 실행
9. 점주로 로그인해 `/merchant/pro/weekly-report-notifications`에서 알림 확인
10. 점주가 알림 읽음 또는 모두 읽음 처리
11. 관리자로 돌아와 notification analytics 확인
12. 필요 시 미확인 알림 리마인드 생성
13. `/admin/pro/operations/audit-logs`에서 운영 액션 audit log 확인
14. 감사 로그 CSV 다운로드
15. Audit Log purge preview 확인
16. `/admin/pro/operations/health-alerts`에서 alert 확인/해결 처리

## 리허설 결과 기준 설명 포인트

- Pro Operations의 `needs_attention=true` 또는 Health `WARNING`은 데모 실패가 아니라 운영 주의 신호가 있는 상태다.
- Weekly Report scheduler CLI가 `SKIPPED`를 반환하면 동일 기간에 이미 완료된 SCHEDULED run이 있어 중복 실행을 막은 것이다.
- Delivery preview에서 READY 대상이 있으면 내부 알림 Mock 발송을 실행할 수 있다.
- 점주 알림 화면에서 UNREAD 알림은 개별 읽음 또는 모두 읽음 처리가 가능하다.
- Audit Log CSV export는 운영 액션 보고용이며 개인정보, 연락처, 주소, 토큰은 포함하지 않는다.
- Audit Log purge는 반드시 preview로 대상 범위를 설명한 뒤, 실제 삭제는 데모 상황에서는 실행하지 않는 편이 안전하다.

## CLI 데모

```bash
cd backend
python scripts/run_weekly_report_batch.py
python scripts/run_pro_health_alert_check.py
```

## 주의사항

- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송은 없다.
- 외부 발송 API 토큰, 수신자 이메일, 전화번호, 주소는 Pro 운영 로그에 저장하지 않는다.
- Mock 결제/환불/배송/POS/내부 알림은 서비스 흐름 검증용이다.
- 실서버 cron 등록은 별도 운영 작업이다.
