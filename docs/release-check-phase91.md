# Phase 91 Release Check

## 작업 목적

관리자 Pro Operations Dashboard에서 실행되는 Weekly Report 운영 Quick Actions와 주요 관리자 운영 액션에 대해 Audit Trail을 남기는 MVP를 추가했다.

이번 Phase에서도 실제 이메일, 카카오, Push, 외부 발송 API 연동은 수행하지 않는다. 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 노출하지 않는다.

## 변경 내용

- `pro_operations_audit_logs` 테이블 추가
- 관리자 운영 액션 감사 로그 모델, 스키마, 서비스 추가
- 주요 관리자 POST 액션 성공/실패 감사 로그 기록
  - 전체 Weekly Report batch 실행
  - Delivery preview 생성
  - In-app mock delivery 실행
  - 미확인 리마인드 생성
  - 실패 batch item 재실행
- 관리자 감사 로그 조회 API 추가
  - `GET /api/v1/admin/pro/operations/audit-logs`
  - `GET /api/v1/admin/pro/operations/audit-logs/summary`
- `/admin/pro/operations` 화면에 최근 운영 액션 이력, 성공/실패 요약, 최근 실패 액션 표시 추가

## DB 변경 여부

DB 변경 있음.

- Migration: `backend/alembic/versions/202606180022_create_pro_operations_audit_logs.py`
- 추가 테이블: `pro_operations_audit_logs`

기존 batch, delivery, notification 테이블은 변경하지 않았다.

## Audit Log 기록 기준

- 성공한 관리자 운영 액션은 `status=SUCCESS`로 기록한다.
- 예외 또는 실패 응답으로 끝난 액션은 가능한 범위에서 `status=FAILED`로 기록한다.
- `target_id`에는 생성된 batch run 또는 delivery run id를 우선 기록한다.
- `metadata_json`에는 run id, status, success/failed/skipped count 등 운영 확인용 최소 정보만 저장한다.
- 이메일, 전화번호, 주소, 토큰 등 개인정보성/민감정보는 저장하지 않는다.

## 검증 결과

- `python -m compileall app scripts`: PASS
- `python -m alembic upgrade head`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
  - 최초 1회는 로컬 서버 미기동으로 health check 연결 거부
  - 백엔드 서버 실행 후 재검증 PASS
- `python scripts/run_weekly_report_batch.py`: PASS
  - 동일 기간 완료된 SCHEDULED run이 있어 중복 실행 방지 `SKIPPED` 확인
- admin batch 실행 후 audit log 생성 확인: PASS
- delivery preview 실행 후 audit log 생성 확인: PASS
- mock delivery 실행 후 audit log 생성 확인: PASS
- unread reminder 실행 후 audit log 생성 확인: PASS
- retry failed 실행 후 audit log 생성 확인: PASS
  - 실패 item 없는 batch run에 대해 `400`으로 안전 차단되고 `FAILED` audit log 기록 확인
- audit logs 목록/summary API 확인: PASS
  - 직접 호출 결과 `total_count=5`, `success_count=4`, `failed_count=1`
- merchant/customer audit log API 접근 차단 확인: PASS
  - 각각 `403`
- `/admin/pro/operations` 최근 audit log 표시 확인: PASS
  - 프론트 build/TypeScript 검증으로 화면 연결 확인
- Quick Action 실행 후 audit log 새로고침 확인: PASS
  - 화면의 `loadSummary`가 operations summary, audit summary, audit log list를 함께 재조회
- `npm run lint`: PASS
- `npm run build`: PASS

## 남은 한계

- 감사 로그 CSV 다운로드와 장기 보관 정책은 아직 없다.
- 세부 관리자 권한 분리는 아직 없다.
- 실제 외부 발송 및 발송 실패 webhook은 이번 Phase 범위가 아니다.
