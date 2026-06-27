# Phase 89 Release Check

## 작업 목적

BreadGo Pro Weekly Report 운영 상태를 관리자가 한눈에 볼 수 있도록 Pro Operations Dashboard MVP를 추가했다.

## 변경 사항

- ADMIN 전용 Pro Operations Summary API 추가
- 관리자 화면 `/admin/pro/operations` 추가
- 관리자 NavBar와 Admin Dashboard에 `Pro 운영` / `Pro Operations` 링크 추가
- Weekly Report batch, delivery, notification, attention summary를 한 화면에 표시
- 실제 이메일/카카오/Push/외부 발송 API는 추가하지 않음
- 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않음

## DB 변경 여부

- DB 변경 없음
- 기존 batch run/item, delivery run/item, notification 테이블을 조회해 집계
- Alembic migration 추가 없음

## API 목록

- `GET /api/v1/admin/pro/operations/summary`

응답 요약:

- Weekly Report batch 요약
- delivery run 요약
- Weekly Report notification 읽음/미확인 요약
- 운영 경고 요약

## 화면 경로

- `/admin/pro/operations`

화면 구성:

- Weekly Report 운영 상태 카드
- Delivery 상태 카드
- 알림 읽음률 카드
- 주의 필요 항목 카드
- 최근 batch run 요약
- 최근 delivery run 요약
- notification summary 요약
- attention message 목록
- Batch Monitor / Delivery Preview 이동 링크

## 운영 경고 기준

아래 조건 중 하나라도 해당하면 `needs_attention=true`:

- 최근 batch status가 `FAILED` 또는 `PARTIAL`
- 최근 delivery status가 `FAILED` 또는 `PARTIAL`
- 미확인 Weekly Report notification이 1개 이상
- 최근 7일 내 failed batch run이 1개 이상
- 최근 reminder 이후에도 UNREAD notification이 남아 있음

attention message 예:

- `최근 Weekly Report batch에 실패 또는 부분 실패가 있습니다.`
- `미확인 Weekly Report 알림이 남아 있습니다.`
- `최근 delivery run에 실패 항목이 있습니다.`

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS
- admin operations summary API 직접 호출: PASS
- 최근 batch summary 표시 확인: PASS
- 최근 delivery summary 표시 확인: PASS
- notification summary 표시 확인: PASS
- `needs_attention` 및 `attention_messages` 동작 확인: PASS
- merchant/customer admin operations API 접근 차단 403 확인: PASS
- 기존 delivery preview/mock-send/remind-unread 유지 확인: PASS
- 기존 scheduler CLI 유지 확인: PASS
- 기존 retry failed 유지 확인: PASS
- `npm run lint`: PASS
- `npm run build`: PASS

검증 메모:

- 운영 요약 API에서 `batch`, `delivery`, `notifications`, `attention` 응답 확인
- 최근 delivery run `IN_APP_REMINDER` 기준 delivery summary 확인
- notification total/unread/read_rate 확인
- 미확인 알림과 최근 실패 batch 이력 기준 `needs_attention=true` 및 attention messages 확인
- `/admin/pro/operations` 라우트가 Next build 결과에 포함됨

## 남은 한계

- 실제 이메일/카카오/Push 발송은 아직 없다.
- 외부 발송 실패 webhook, 수신 동의 관리, 재발송 정책은 아직 없다.
- 현재 운영 경고는 rule-based MVP 집계이며, 별도 incident 저장/알림 발송은 하지 않는다.
