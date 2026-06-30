# Release Note Draft v0.1.4

## 상태

`v0.1.4`는 아직 Release Candidate 준비 단계다.

- 현재 공식 최신 Release: `v0.1.3-adapter-readiness`
- v0.1.4 공식 tag: 아직 생성 전
- v0.1.4 GitHub Release: 아직 생성 전
- 새 tag 생성 없음
- 새 GitHub Release 생성 없음
- 기존 tag 삭제/이동 없음

## v0.1.4 목적

v0.1.4는 실제 외부 연동을 켜는 Release가 아니라, v0.1.3 adapter readiness 기반을 운영자가 이해하고 검증하기 쉽게 만드는 readiness / UX / boundary 개선 Release다.

## v0.1.3 대비 변경 요약

- Provider adapter unit tests 추가
- Adapter readiness admin UI 상세화
- POS / CSV import UX 고도화
- Merchant inventory ledger report 개선
- Credential boundary 설계 문서화
- v0.1.4 Release Candidate 문서 준비

## Provider Adapter Unit Tests

- Payment provider readiness / dry-run 테스트
- Delivery provider readiness / dry-run 테스트
- Notification provider readiness / dry-run 테스트
- POS provider readiness / dry-run 테스트
- External Integration Readiness summary 테스트
- 모든 provider의 `external_calls_enabled=false` 원칙 확인

## Adapter Readiness Admin UI 상세화

Admin Dashboard에서 External Integration Readiness 카드를 상세화했다.

- overall status 표시
- provider별 status / mode / message 표시
- dry-run 결과 표시
- `MOCK_READY`, `NOT_ENABLED`, `NOT_CONFIGURED` 상태 설명
- 실제 외부 연동 완료 상태가 아니라 adapter 준비 상태임을 명확히 표시

## POS / CSV Import UX 고도화

- 점주 상품관리에서 CSV import와 Mock POS sync 진입 경로 보강
- CSV import preview / HIDDEN 생성 / 상품관리 검토 흐름 안내
- Mock POS sync와 CSV fallback의 관계 설명
- external_sku 기반 중복 판단 안내
- 실제 POS API / token / credential 미사용 경계 표시

## Merchant Inventory Ledger Report 개선

- 점주 재고 이력 화면을 리포트형으로 개선
- CSV import / Mock POS sync / 예약 / 픽업의 재고 변화 의미 안내
- 상품별 최근 재고 변화 요약 추가
- smoke test에 merchant inventory-events read-only 조회 추가

## Credential Boundary 설계

- Payment / Delivery / POS / Notification credential boundary 문서화
- 향후 env 이름 후보와 보관 원칙 정리
- 실제 API key / secret / token / webhook URL을 코드나 env에 추가하지 않는 원칙 명시
- provider별 실제 연동 전 필요한 checklist 정리

## 실제 외부 API 미호출

v0.1.4 Release Candidate 기준으로 아래 외부 호출은 없다.

- 실제 PG 승인 / 환불 호출 없음
- 실제 배송 provider 접수 / 추적 호출 없음
- 실제 POS API 호출 없음
- 실제 이메일 / 카카오 / Push / Slack / Discord / Webhook 발송 없음
- 실제 webhook URL 저장 없음

## DB Schema / Migration

- DB schema 변경 없음
- migration 추가 없음
- credential 저장 table 추가 없음

## 포함 범위

- adapter readiness 테스트
- 관리자 readiness UI 개선
- 점주 CSV / Mock POS UX 개선
- 점주 재고 이력 리포트 UX 개선
- credential boundary 문서
- release note / checklist / post-release verification template

## 제외 범위

- 실제 PG 결제 승인/환불
- 실제 배송 provider 연동
- 실제 POS API 연동
- 실제 이메일/카카오/Push/Slack/Discord/Webhook 발송
- API key / secret / token / webhook URL 추가
- DB credential 저장
- webhook 검증 구현
- 대량 비동기 큐
- production secret manager 연동

## 검증 결과

Release Candidate 준비 기준으로 아래 명령이 통과했다.

- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python -m pytest tests -q`: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

## 추천 Release 정보

- 추천 tag: `v0.1.4-readiness-ux-boundary`
- 추천 Release title: `BreadGo Readiness UX Boundary Release v0.1.4`
- Release body source: `docs/release-note-v0.1.4.md`
- Target branch: `main`

## Release 생성 전 주의사항

- v0.1.4 tag는 아직 만들지 않는다.
- GitHub Release는 아직 만들지 않는다.
- 실제 외부 연동 Release가 아니라 readiness / UX / boundary 개선 Release임을 본문에 명확히 적는다.
- 현재 공식 최신 Release는 `v0.1.3-adapter-readiness`로 유지한다.

## Suggested commit message

`Prepare v0.1.4 release candidate docs`

