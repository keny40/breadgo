# Merchant Inventory UX Phase 125

## 목적

점주가 상품 등록, 재고 확인, 예약/픽업 상태를 더 쉽게 이해하도록 Merchant 화면의 안내 문구와 진입 동선을 정리했다.

이번 Phase에서는 DB schema, migration, 실제 POS/배송/외부 알림 연동을 변경하지 않았다.

## 점주 화면 목적

점주 화면은 아래 세 가지 운영 행동을 빠르게 수행하도록 돕는다.

1. 오늘 판매할 상품과 재고를 등록한다.
2. 결제 완료 예약과 픽업/배송 요청 상태를 확인한다.
3. BreadGo Pro에서 재고 이력, Weekly Report 알림, POS 준비 흐름을 확인한다.

## 상품 / 재고 / 예약 / 픽업 흐름

권장 운영 흐름:

1. `/merchant`
   - 오늘 확정 예약, 픽업 완료, 취소 예약을 확인한다.
   - `상품/재고 관리`, `주문 관리`, `픽업 확인`, `BreadGo Pro`로 이동한다.

2. `/merchant/products`
   - 상품명, 가격, 할인 가격, 재고, 판매 시간을 입력한다.
   - 반복 상품은 `그대로 다시 올리기`로 빠르게 재등록한다.
   - CSV 일괄 등록은 POS 연동 전 단계의 BreadGo Pro 고급 기능으로 설명한다.

3. `/merchant/orders`
   - 결제 완료 예약, 픽업 주문, 퀵/택배 요청을 확인한다.
   - 픽업 주문은 픽업 확인 화면으로 이어서 처리한다.
   - 배송 요청은 실제 배송 provider 없이 점주가 수동으로 상태를 변경한다.

4. `/merchant/pickup`
   - 고객이 제시한 6자리 픽업 코드를 조회한다.
   - 예약 상태와 결제 상태를 확인한 뒤 픽업을 확정한다.
   - 픽업 확정은 BreadGo 내부 예약 상태와 재고 이력에 반영된다.

5. `/merchant/pro`
   - Daily Brief, Weekly Report, Inventory Ledger, POS 준비 흐름을 확인한다.

## Mock 배송 / POS / 외부 알림 미연동 경계

이번 Phase에서도 아래 항목은 실제 연동이 아니다.

- POS sync: 실제 POS API 호출 없음
- 배송 상태 변경: 실제 배송 provider 호출 없음
- 외부 알림: 이메일/카카오/Push 발송 없음
- Weekly Report 알림: BreadGo 내부 in-app mock notification
- 결제: 실제 PG 승인이나 카드 청구 없음

점주 화면에는 POS, 배송, 외부 알림이 실제 연동 전 단계라는 안내를 유지/보강했다.

## 관리자 화면과의 연결 관계

- 점주가 상품/재고와 예약/픽업을 처리하면 관리자 Dashboard에서 상품, 예약, Mock 결제 현황으로 확인할 수 있다.
- Weekly Report batch와 delivery preview는 관리자 Pro Operations에서 점검한다.
- 점주 Weekly Report notification은 관리자 delivery preview / mock delivery 흐름과 연결된다.
- Health Alert와 Audit Log는 관리자 내부 운영 관점에서 점검한다.

## 점주 시연 순서

1. `/demo`에서 merchant 계정 확인
2. `merchant@breadgo.test / 12345678`로 로그인
3. `/merchant`에서 오늘 확정 예약, 픽업 완료, 취소 예약 확인
4. `/merchant/products`에서 상품/재고 관리와 CSV/POS 준비 안내 설명
5. `/merchant/orders`에서 예약/결제/배송 요청 상태 확인
6. `/merchant/pickup`에서 픽업 코드 조회와 픽업 확정 설명
7. `/merchant/pro`에서 Daily Brief, Weekly Report, 재고 이력, POS 준비 흐름 확인
8. `/merchant/pro/weekly-report-notifications`에서 내부 Weekly Report 알림 확인

## 화면 변경 요약

- `/merchant`
  - 오늘 먼저 확인할 점주 운영 흐름 카드 추가
  - 상품/재고, 주문/픽업, BreadGo Pro로 이어지는 버튼 추가

- `/merchant/products`
  - 예약/주문 확인, 재고 이력 바로가기 추가
  - 상품 등록 / 재고 확인 / 예약 연결 안내 카드 추가
  - POS, 배송 provider, 외부 알림 미연동 안내 보강

- `/merchant/orders`
  - 상품/재고 관리, 픽업 확인 바로가기 추가
  - 실제 배송 provider와 외부 알림 미호출 안내 보강

- `/merchant/pickup`
  - 주문 관리, 상품/재고 관리 바로가기 추가
  - 픽업 확정과 재고 이력 반영, 배송 수동 관리 안내 추가

- `README.md`
  - Phase 125 문서 링크 추가

## 향후 v0.1.3 후보

1. 상품별 재고 이력 drill-down
   - 상품 카드에서 해당 상품의 Inventory Ledger만 필터링해 볼 수 있게 한다.

2. 주문/픽업 운영 요약
   - 오늘 픽업 예정, 지연 가능 주문, 취소 복구 재고를 점주 대시보드에 표시한다.

3. CSV/POS import UX 강화
   - import 결과, 업데이트/스킵 사유, external_sku 매칭 상태를 더 명확히 보여준다.

4. 실제 POS 연동 사전 설계
   - provider adapter, token 저장 금지, 실패/재시도 정책을 문서화한다.

5. 배송 provider 연동 준비
   - 실제 배송 연동 전 상태값, 수동 처리, 알림 경계 기준을 정리한다.

## 검증 결과

- `git status`: 변경 파일 확인
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## 변경 여부

- 기능 코드 변경: 화면 안내 / 버튼 / 문구 중심
- DB schema 변경: 없음
- migration 추가: 없음
- 신규 API 추가: 없음
- 실제 POS API 연동 추가: 없음
- 실제 배송 provider 연동 추가: 없음
- 실제 외부 알림 발송 추가: 없음
- 새 tag / 새 Release 생성: 없음
- 기존 tag 삭제/이동: 없음

## Suggested commit message

`Improve merchant inventory UX`
