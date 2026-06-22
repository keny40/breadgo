# Phase 76 Release Check - Saved Weekly Report Export

## 작업 목적

저장된 Weekly Pro Report snapshot을 다시 CSV 또는 Text 요약으로 export해 과거 운영 리포트를 재다운로드/복사할 수 있게 했다.

## 변경 내용

- `GET /api/v1/merchant/pro/weekly-report/history/{snapshot_id}/export` 추가
- export format 지원:
  - `json`
  - `csv`
  - `text`
- 저장 리포트 CSV는 snapshot 요약 지표를 `key,value` 형태로 제공하고 insights를 하단에 포함
- 저장 리포트 Text는 저장 당시 `text_summary`를 우선 사용하고, 없으면 snapshot 지표와 insights로 rule-based 텍스트 생성
- `/merchant/pro/weekly-report/history` 각 저장 리포트 카드에 `CSV 다운로드`, `요약 복사` 버튼 추가

## DB 변경 여부

- DB 스키마 변경 없음
- Phase 75의 `pro_weekly_report_snapshots`, `pro_weekly_report_insights` 데이터를 재사용

## 저장 리포트 Export 기준

- 현재 로그인한 MERCHANT의 snapshot만 export 가능
- 없는 snapshot 또는 다른 가맹점 snapshot은 조회되지 않음
- `format=json`: snapshot 주요 지표와 insights 반환
- `format=csv`: 저장된 요약 지표와 insights를 CSV로 반환
- `format=text`: 저장 당시 `text_summary` 우선 사용, 없으면 rule-based 텍스트 생성
- 실제 PDF 생성이나 외부 발송은 하지 않음

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- 백엔드 서버 실행 후 `cd backend && python scripts/seed_demo.py && python scripts/smoke_test.py`: PASS
- 저장된 weekly report snapshot export json/csv/text 직접 호출: PASS
  - `format=json`: snapshot 주요 지표와 insights 반환 확인
  - `format=csv`: `text/csv` 응답과 `key,value` 요약 CSV 확인
  - `format=text`: `text/plain` 응답과 주간 리포트 요약 문구 확인
- 권한 없는 snapshot 접근 차단: PASS
  - 고객 계정으로 가맹점 snapshot export 호출 시 `403` 확인
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- PDF 생성은 아직 없다.
- 외부 메일/카카오 발송은 아직 없다.
- 저장 리포트 export는 snapshot 요약 중심이며 일자별 trend 원본은 저장하지 않는다.

## 다음 단계

- 저장 리포트 PDF 생성
- 공유 링크 생성
- 저장 리포트별 다운로드/복사 이벤트 추적
