# Merchant Inventory Report Phase 137

## 목적

Phase 137은 점주가 상품별 재고 변화, CSV import, Mock POS sync, 예약/픽업 반영 결과를 더 쉽게 이해할 수 있도록 재고 이력 리포트 화면과 문서를 개선하는 단계다.

이번 Phase에서는 기존 재고 이력 API를 유지하고, 화면 안내/링크/문서/smoke test를 중심으로 개선했다.

## 점주 재고 이력 리포트 목적

재고 이력 리포트는 점주가 "왜 재고가 늘거나 줄었는지"를 확인하는 운영 화면이다.

확인 대상:

- 상품 등록 또는 수동 수정
- CSV import
- Mock POS sync
- 추천 초안 생성
- 예약 생성
- 예약 취소
- 픽업 완료
- 수동 재고 조정

## 재고 변화 원인 구분

### CSV

- 엑셀/CSV 파일 업로드로 생성 또는 업데이트된 재고
- POS token 없이 BreadGo 서버에서만 처리
- 실제 POS API 호출 아님

### POS

- Mock POS sync dry-run으로 반영된 재고
- external_sku 기준으로 상품 생성/업데이트/건너뜀 판단
- 실제 POS API, credential, token은 저장하거나 호출하지 않음

### RESERVATION

- 예약 생성, 예약 취소, 픽업 확정 흐름에서 발생한 재고 변화
- 예약 생성은 판매 가능 재고를 줄이고 예약 취소는 재고를 복구
- 픽업 완료는 주문 상태와 운영 리포트에 연결

### MANUAL / RECOMMENDATION

- 상품관리에서 직접 등록/수정한 재고
- BreadGo Pro 추천 초안으로 생성된 상품 재고

## 상품 등록 / CSV import / Mock POS sync / 예약 / 픽업 관계

1. 상품 등록 또는 CSV import / Mock POS sync로 상품과 초기 재고가 만들어진다.
2. 상품이 ACTIVE가 되면 고객 예약 대상이 된다.
3. 고객 예약 생성 시 재고가 감소한다.
4. 예약 취소 시 재고가 복구된다.
5. 픽업 완료 시 주문 상태와 운영 리포트에 반영된다.
6. 재고 이력은 위 과정을 상품별/출처별로 추적한다.

## 화면 개선 내용

대상 화면:

- `/merchant/pro/inventory-ledger`
- `/merchant/products`
- `/merchant/pro/pos`

개선 사항:

- 재고 이력 화면 상단에 CSV / Mock POS / 예약 흐름 설명 카드 추가
- CSV import와 Mock POS sync 진입 CTA 추가
- source별 최근 이력 count 표시
- 상품별 최근 50건 기준 net delta 요약 추가
- 이벤트 note가 없을 때 source별 의미 설명 표시
- 상품관리에서 재고 알림과 재고 이력 진입 경로 보강
- POS 화면에서 Mock POS sync 결과가 재고 이력에 원인을 남긴다는 설명 추가

## 실제 POS API 미연동 경계

현재 하지 않는 것:

- 실제 POS API 호출
- 실제 POS token 저장
- 실제 POS credential 저장
- 외부 POS webhook 처리
- POS scheduler 기반 자동 sync

현재 하는 것:

- CSV import
- Mock POS JSON dry-run
- external_sku 기반 중복 판단
- 재고 이력에 CSV/POS/예약 원인 기록
- 관리자 readiness 화면에서 POS adapter 준비 상태 표시

## 점주 시연 순서

1. `/merchant/products`에서 상품관리 진입
2. CSV import / Mock POS sync / 재고 이력 / 재고 알림 링크 확인
3. `/merchant/products/import`에서 CSV preview와 HIDDEN 생성 흐름 설명
4. `/merchant/pro/pos`에서 Mock POS sync dry-run 설명
5. `/merchant/pro/inventory-ledger`에서 출처별 재고 변화 확인
6. 상품별 최근 변화 요약 확인
7. 예약/픽업이 재고와 운영 리포트에 연결된다는 점 설명

## 관리자 readiness 화면과의 연결

관리자 `/admin`의 External Integration Readiness 카드는 POS adapter가 실제 연동 완료 상태가 아니라 준비 상태임을 보여준다.

- `MOCK_POS`: 내부 dry-run 기준 준비 완료
- `GENERIC_POS`: 실제 provider 설정 전
- `external_calls_enabled=false`: 정상 상태

점주 재고 이력에서는 Mock POS sync 결과가 실제 POS API가 아니라 BreadGo 내부 dry-run으로 기록된 재고 변화임을 확인한다.

## 테스트 보강

`backend/scripts/smoke_test.py`에 merchant inventory-events read-only 조회를 추가했다.

확인 항목:

- 점주 token으로 `/api/v1/merchant/pro/inventory-events?limit=10` 조회
- 응답이 list인지 확인
- smoke test에서 생성한 예약 상품에 대해 `source_type=RESERVATION` 재고 이벤트가 존재하는지 확인

## v0.1.4 이후 개선 후보

- 상품별 재고 이력 상세 페이지
- 재고 이력 CSV export
- Inventory Ledger와 Inventory Alert의 원인-조치 연결 강화
- Mock POS sync batch와 inventory event 상호 링크
- 실제 POS 연동 전 credential boundary 설계 심화

## DB / Migration 변경 여부

- DB schema 변경: 없음
- migration 추가: 없음
- 신규 저장 테이블 추가: 없음

## 실제 POS API 호출 여부

없음.

- 실제 POS API 호출 없음
- 실제 POS token / credential / API key 추가 없음
- 외부 POS webhook 처리 없음

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## Suggested commit message

`Improve merchant inventory report UX`

