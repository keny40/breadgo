# Pro Operations Audit Log Retention Policy

## 기본 원칙

Pro Operations Audit Log는 관리자 운영 액션의 추적을 위해 저장한다. 로그에는 이메일, 전화번호, 주소, 외부 발송 토큰 등 개인정보성/민감정보를 저장하지 않는다.

## 보관 기간

- 기본 보관 기간: 180일
- 최소 보관 기간: 30일
- 30일 미만의 purge 요청은 거부한다.

## Purge 절차

1. Admin이 Audit Log 화면에서 retention day를 입력한다.
2. `삭제 대상 미리보기`로 대상 건수, cutoff date, status/action별 count를 확인한다.
3. 미리보기 결과를 확인한 뒤 `확인 후 삭제 실행`을 누른다.
4. purge execute는 ADMIN만 가능하다.
5. purge 결과 자체는 `PURGE_AUDIT_LOGS` audit log로 남긴다.

## CSV Export 주의

Audit Log CSV export는 외부 점검/보고용으로 사용할 수 있다. CSV에는 `metadata_json`을 포함하지 않으며 이메일, 전화번호, 주소, 외부 발송 토큰을 포함하지 않는다.

CSV 파일을 외부에 보관하거나 공유할 경우 별도 보안 관리 기준에 따라 접근 권한, 보관 위치, 삭제 주기를 관리해야 한다.

## 이번 MVP 범위 밖

- 자동 스케줄 purge
- 장기 보관용 archive 테이블
- S3 백업
- CSV 자동 백업
- 세부 관리자 권한 분리
