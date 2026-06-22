# Phase 74 Release Check - Weekly Pro Report Export

## 작업 목적

Weekly Pro Report를 화면에서 보는 것에 그치지 않고 CSV 다운로드와 공유용 텍스트 복사를 지원해 점주가 운영 리포트를 외부 공유 자료로 활용할 수 있게 했다.

## 변경 내용

- `GET /api/v1/merchant/pro/weekly-report/export` 추가
- export format 지원:
  - `json`
  - `csv`
  - `text`
- CSV export는 일자별 추이 데이터를 반환
- Text export는 카톡/메일에 붙여넣기 쉬운 rule-based 요약 문장 반환
- `/merchant/pro/weekly-report`에 `CSV 다운로드`, `요약 복사` 버튼 추가
- Pro 플랜 화면에 `주간 리포트 Export` 기능 안내 추가

## DB 변경 여부

- DB 스키마 변경 없음
- 기존 Weekly Report 계산 로직과 Daily Brief snapshot 데이터를 재사용

## Export 기준

- 기본 기간은 Weekly Report와 동일하게 오늘 포함 최근 7일
- `start_date`, `end_date` query parameter 지원
- `format=csv`:
  - `date`, `sales_amount`, `reservation_count`, `picked_up_count`, `cancelled_count`, `saved_quantity`, `unresolved_alert_count`, `recommendation_action_count`
- `format=text`:
  - 기간, 총 매출, 예약 수, 픽업 완료, 폐기 절감, 미해결 알림, 주요 인사이트를 공유용 문장으로 생성
- `format=json`:
  - Weekly Report 응답 구조를 JSON으로 반환
- 실제 AI 요약이 아닌 rule-based 요약임을 명시

## 검증 결과

- `cd backend && python -m compileall app scripts`: PASS
- `cd backend && python -m alembic upgrade head`: PASS
- 백엔드 서버 실행 후 `cd backend && python scripts/seed_demo.py && python scripts/smoke_test.py`: PASS
- Weekly Report export json/csv/text 직접 호출: PASS
  - `format=json`: `daily_trends` 7건 응답 확인
  - `format=csv`: `Content-Type: text/csv; charset=utf-8`, CSV header 확인
  - `format=text`: `Content-Type: text/plain; charset=utf-8`, `BreadGo Pro 주간 운영 리포트` 제목 확인
- `cd frontend && npm run lint`: PASS
- `cd frontend && npm run build`: PASS

## 한계

- 실제 PDF 생성은 하지 않는다.
- 외부 메일/카카오 발송은 하지 않는다.
- CSV는 일자별 추이 중심이며 전체 요약/인사이트는 text/json에서 확인한다.

## 다음 단계

- PDF export
- 공유 링크 생성
- 주간 리포트 자동 생성 및 알림
