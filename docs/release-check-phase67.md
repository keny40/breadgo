# Phase 67 Release Check

## 작업 목적

실제 외부 POS API를 호출하지 않으면서 향후 POS 업체별 연동을 붙일 수 있도록 POS Provider Adapter 구조와 동기화 정책 옵션을 추가했다.

## 변경 내용

- `backend/app/services/pos_providers/` adapter 구조 추가
  - `base.py`: 공통 interface와 normalized item 정의
  - `mock.py`: Mock POS 입력을 normalized item으로 변환
  - `generic.py`: 실제 호출 없는 skeleton provider
- 기존 Mock POS sync가 adapter를 사용하도록 정리
- Mock POS sync 요청에 정책 옵션 추가
  - `update_mode`
  - `default_product_status`
- `/merchant/pro/pos` 화면에 업데이트 정책 선택 UI 추가
- row별 skip/fail 사유 코드 표시 보강
- Pro 플랜 화면에서 POS Provider Adapter 준비 항목 표시

## DB 변경 여부

DB 변경 없음.

Phase 66에서 추가한 `pos_integrations`, `pos_sync_batches`, `pos_sync_rows`를 그대로 사용한다.

## POS Adapter 구조

- `MOCK_POS`: 화면에서 입력한 `mock_items`를 정규화해 상품 생성/업데이트에 사용
- `GENERIC_POS`: 실제 외부 호출 없이 skeleton 상태로 유지
- API key/token 같은 민감정보는 저장하지 않음

## Sync 정책 기준

- `UPDATE_IF_NO_RESERVATIONS`: 기본값. 예약이 없는 기존 상품만 업데이트
- `SKIP_EXISTING`: 기존 상품은 생성/업데이트하지 않고 건너뜀
- `UPDATE_HIDDEN_ONLY`: 기존 상품 중 `HIDDEN` 상태만 업데이트
- `default_product_status`: MVP에서는 `HIDDEN`만 허용

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- `cd backend && python scripts/smoke_test.py`: PASS
- Mock POS sync adapter 동작 직접 검증: PASS
- `UPDATE_IF_NO_RESERVATIONS` 직접 검증: PASS
- `SKIP_EXISTING` 직접 검증: PASS
- row별 skipped reason 직접 확인: PASS
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- 실제 POS 업체 API 호출은 아직 없다.
- Generic provider는 skeleton이다.
- 대용량 동기화, 비동기 큐, 재시도 정책은 아직 없다.
- 외부 POS 인증 정보 저장/암호화는 이후 별도 설계가 필요하다.

## 다음 단계

- 실제 POS provider adapter 추가
- provider별 인증/토큰 보안 저장 구조 설계
- POS sync 예약 충돌 정책 세분화
