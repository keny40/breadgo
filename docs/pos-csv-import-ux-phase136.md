# POS / CSV Import UX Phase 136

## 목적

Phase 136은 실제 POS API 호출 없이, 현재 CSV import / Mock POS sync / POS readiness 흐름을 점주와 관리자가 더 쉽게 이해하도록 UX와 문서를 개선하는 단계다.

이번 Phase에서는 DB schema와 migration을 변경하지 않았고, 실제 POS credential / token / API key를 추가하지 않았다.

## 현재 POS / CSV 상태

- CSV import: 점주가 CSV 파일을 업로드해 상품명, 가격, 재고, 판매 시간을 BreadGo 내부에 일괄 등록
- Mock POS sync: 샘플 JSON을 BreadGo 내부 Mock POS adapter로 정규화해 상품 생성/업데이트 정책을 검증
- POS readiness: 실제 POS 연동 완료 상태가 아니라 adapter 준비 상태를 관리자 화면에서 read-only로 표시
- 실제 POS API 호출: 없음
- POS token / credential / API key 저장: 없음

## CSV Import 흐름

1. 점주가 `/merchant/products/import`로 이동
2. 매장을 선택하고 CSV 파일을 선택
3. `업로드 전 검증`으로 row별 생성/업데이트/건너뜀/실패 후보 확인
4. `CSV 일괄 등록` 실행
5. 상품은 기본적으로 HIDDEN 상태로 생성
6. 점주가 `/merchant/products`에서 가격, 재고, 판매 시간을 확인한 뒤 ACTIVE로 변경

UX 보강:

- preview 단계에서는 상품을 만들지 않는다는 안내 추가
- HIDDEN 생성 후 상품관리에서 검토한다는 안내 추가
- POS token, credential, 외부 POS 서버 호출을 사용하지 않는다는 안내 추가
- Mock POS sync 화면으로 이동하는 CTA 추가

## Mock POS Sync 흐름

1. 점주가 `/merchant/pro/pos`로 이동
2. provider를 `MOCK_POS`로 유지
3. 샘플 JSON 또는 점주가 입력한 mock item JSON을 확인
4. update mode와 기본 생성 상태를 선택
5. `Mock POS 동기화 실행`
6. BreadGo 내부에서 external_sku 기준으로 생성/업데이트/건너뜀/실패 결과를 기록
7. 동기화 이력과 row 결과를 확인

UX 보강:

- 실제 POS API, token, credential을 저장하거나 호출하지 않는다는 안내 강화
- CSV import와 Mock POS sync가 모두 `external_sku` 기준으로 중복을 판단한다는 설명 추가
- 실제 POS 전에도 CSV fallback을 유지한다는 안내 추가
- 외부 POS 호출 상태를 `OFF`로 명확히 표시

## POS Readiness 의미

관리자 `/admin`의 External Integration Readiness 카드는 실제 외부 연동 상태가 아니라 adapter 준비 상태를 보여준다.

- `MOCK_POS`: 내부 dry-run 기준 준비 완료
- `GENERIC_POS`: 실제 POS provider skeleton / noop 상태
- `NOT_CONFIGURED`: 실제 provider 설정과 credential boundary가 아직 없음
- `external_calls_enabled=false`: 정상 상태

## 실제 POS API 미연동 경계

현재 단계에서 하지 않는 것:

- 실제 POS API 호출
- 실제 POS token 저장
- 실제 POS credential 저장
- 외부 POS webhook 처리
- 실시간 POS sync scheduler
- store credential mapping 운영화

현재 단계에서 하는 것:

- CSV fallback 유지
- Mock POS JSON dry-run
- external_sku 기반 중복 처리 검증
- readiness API와 관리자 화면에서 POS adapter 준비 상태 표시
- smoke/unit test에서 POS mock readiness 확인

## 점주 시연 순서

1. `/merchant/products` 접속
2. 상품관리 상단에서 CSV import / Mock POS sync 진입 경로 확인
3. `/merchant/products/import`에서 샘플 CSV 다운로드
4. 업로드 전 검증 흐름 설명
5. CSV 등록 시 기본 HIDDEN 생성 설명
6. `/merchant/pro/pos`로 이동
7. Mock POS JSON dry-run 실행
8. 동기화 결과와 row별 메시지 확인
9. 상품관리와 재고 이력으로 돌아가 결과 확인

## 관리자 시연 순서

1. `/admin` 접속
2. External Integration Readiness 카드 확인
3. POS area에서 `MOCK_POS`와 `GENERIC_POS` 상태 확인
4. POS dry-run 결과가 `READY/ITEMS_*`로 표시되는지 설명
5. `external_calls_enabled=false`가 정상 상태임을 강조
6. 실제 POS 연동 전 필요한 항목으로 credential boundary, CSV fallback, external_sku mapping 기준 설명

## v0.1.4 이후 실제 POS 연동 전 필요한 항목

- POS provider별 sandbox 계약과 API 명세 확인
- store credential boundary 설계
- API key / secret / token 저장 방식 결정
- external_sku / store code mapping 정책
- sync 실패 재시도와 rollback 기준
- CSV fallback 유지 정책
- POS sync audit log 기준
- webhook 수신 검증과 replay 방지
- 개인정보/연락처/주소/토큰 미노출 원칙 재확인

## 테스트 보강

`backend/tests/test_adapter_readiness.py`에 POS 통합 readiness boundary 테스트를 보강했다.

확인 항목:

- `MOCK_POS` status가 `READY`
- `GENERIC_POS` status가 `NOT_CONFIGURED`
- POS dry-run status가 `READY/ITEMS_*`
- POS dry-run `external_calls_enabled=false`
- POS dry-run message에 `No external POS API calls` 포함

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## 기능 코드 / DB / Migration 변경 여부

- 기능 코드 변경: UI 문구/안내와 테스트 보강 중심
- DB schema 변경: 없음
- migration 추가: 없음
- POS credential 저장 구조 추가: 없음

## 실제 POS API 호출 여부

없음.

- 실제 POS API 호출 없음
- 실제 POS token / credential / API key 추가 없음
- 외부 POS webhook 처리 없음

## Suggested commit message

`Improve POS CSV import UX`

