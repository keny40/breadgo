# Demo Handoff Pack

## 데모 목적

BreadGo MVP가 단순 마감 할인 상품 예약 앱을 넘어, 점주용 BreadGo Pro / Yield Engine으로 확장될 수 있음을 보여준다. 소비자 예약 흐름, 점주 운영 흐름, 관리자 운영 흐름, Weekly Report 기반 Pro Operations 흐름을 하나의 제품 이야기로 연결한다.

## 핵심 메시지

- BreadGo는 한국판 Too Good To Go를 지향하는 로컬 마감할인 푸드 플랫폼이다.
- 소비자는 남는 빵과 식품을 할인된 가격에 예약하고 픽업/배송 요청 흐름을 경험한다.
- 점주는 상품/재고/예약/픽업/정산을 관리한다.
- BreadGo Pro는 점주가 남는 재고를 줄이고 운영 의사결정을 할 수 있게 돕는 수율 관리 엔진이다.
- 관리자 Pro Operations는 Weekly Report, delivery preview, audit trail, health alert를 통해 운영 상태를 추적한다.

## 관리자 데모 순서

1. `admin@breadgo.test / 12345678`로 로그인
2. `/admin`에서 Admin Dashboard 확인
3. `/admin/pro/operations`로 이동
4. Health Check와 attention messages 확인
5. `전체 Weekly Report 생성` Quick Action 실행
6. `/admin/pro/weekly-report-batches`에서 batch run 결과 확인
7. `/admin/pro/weekly-report-deliveries`에서 Delivery 미리보기 생성
8. READY item이 있으면 내부 알림 Mock 발송 실행
9. Notification summary와 최근 알림 목록 확인
10. `/admin/pro/operations/audit-logs`에서 운영 액션 기록 확인
11. 감사 로그 CSV 다운로드 설명
12. Audit Log purge preview 설명
13. `/admin/pro/operations/health-alerts`에서 alert 확인/해결 처리 설명

## 점주 데모 순서

1. `merchant@breadgo.test / 12345678`로 로그인
2. `/merchant`에서 점주 대시보드 확인
3. `/merchant/products`에서 상품 운영 흐름 확인
4. `/merchant/orders` 또는 `/merchant/pickup`에서 주문/픽업 흐름 확인
5. `/merchant/pro`에서 BreadGo Pro 대시보드 확인
6. `/merchant/pro/weekly-report-notifications`에서 Weekly Report 내부 알림 확인
7. 알림 개별 읽음 또는 모두 읽음 처리 확인

## 소비자 데모 순서

1. `customer@breadgo.test / 12345678`로 로그인
2. `/products`에서 지역 상품 조회
3. 상품 수령 방식 선택
4. 예약 생성
5. Mock 결제 진행
6. `/my-reservations`에서 예약 상태와 픽업 코드 확인
7. `/my-payments`에서 결제 상태 확인
8. `/notifications`에서 인앱 알림 확인

## Pro Operations 데모 순서

1. `/admin/pro/operations`에서 현재 Pro 운영 상태 확인
2. Health `OK/WARNING/CRITICAL` 의미 설명
3. Batch summary와 Delivery summary 설명
4. Quick Actions 실행
5. Batch Monitor에서 SCHEDULED/RETRY/SKIPPED/COMPLETED 설명
6. Delivery Preview에서 READY/SENT/SKIPPED/FAILED 설명
7. 점주 알림 화면으로 넘어가 내부 알림 확인
8. Audit Log Explorer에서 방금 실행한 운영 액션 확인
9. Health Alert 화면에서 OPEN/ACKNOWLEDGED/RESOLVED 설명

## 강조할 차별화 포인트

- BreadGo Pro는 단순 할인 판매가 아니라 점주용 운영 코치다.
- 추천/성과/퍼널/알림/리포트가 누적되어 향후 AI 추천 모델 검증 데이터가 된다.
- Weekly Report와 Daily Brief로 점주가 매일/매주 운영 상태를 복기할 수 있다.
- Delivery preview와 in-app mock delivery는 외부 발송 전 운영 안전장치다.
- Audit Trail과 Health Alert는 SaaS 운영 신뢰도를 보여주는 기능이다.
- CSV/POS/Inventory Ledger는 실제 매장 운영 데이터 연동을 준비하는 기반이다.

## 예상 질문과 답변 예시

Q. 실제 결제가 되나요?

A. 현재는 Mock 결제/Mock 환불입니다. PG 연동 전 고객 예약과 결제 후속 흐름을 검증하기 위한 MVP입니다.

Q. 실제 이메일이나 카카오 알림이 발송되나요?

A. 아닙니다. 현재는 BreadGo 내부 알림만 생성합니다. 이메일, 카카오, Push, Slack, Discord, Webhook 발송은 아직 연결하지 않았습니다.

Q. Health Check가 WARNING이면 데모가 실패한 건가요?

A. 아닙니다. WARNING은 운영자가 확인할 항목이 있다는 뜻입니다. Health Alert와 Audit Trail로 운영 대응 흐름을 보여주기 위한 상태입니다.

Q. Weekly Report scheduler가 SKIPPED면 문제가 있나요?

A. 동일 기간에 이미 완료된 SCHEDULED batch가 있으면 중복 생성을 막기 위해 SKIPPED로 종료합니다. 중복 방지 로직이 작동한 것입니다.

Q. Audit Log purge는 실제 삭제되나요?

A. Preview는 삭제하지 않습니다. Execute를 누르면 실제 삭제되므로 데모에서는 preview까지만 보여주는 것을 권장합니다.

Q. 개인정보나 발송 토큰이 저장되나요?

A. Pro 운영 로그와 delivery/health/audit 기능에는 이메일, 전화번호, 주소, 외부 발송 토큰을 저장하거나 노출하지 않습니다.

## Mock 기능 설명

- Mock 결제/환불: 실제 PG 없이 결제 상태 흐름만 검증
- Mock POS sync: 외부 POS API 없이 external_sku 기반 동기화 구조 검증
- In-app mock delivery: 실제 외부 발송 없이 BreadGo 내부 notification 생성
- Health Alert mock flow: Slack/Discord/Webhook 없이 내부 관리자 alert 생성

## 실제 서비스화 시 남은 과제

- 실제 PG 결제/환불 연동
- 실제 퀵배송/택배 API 연동
- 실제 이메일/SMS/카카오/Push 발송 연동
- Slack/Discord/Webhook 운영 알림 연동
- 외부 POS API 연동
- 실서버 cron 등록
- 자동 복구와 자동 purge scheduler
- 세부 관리자 권한 분리
- 대량 merchant 비동기 batch queue
- 실제 AI 추천 모델
- 보안/개인정보/정산 계좌 암호화 고도화
