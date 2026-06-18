# BreadGo Phase 39 릴리스 체크

## 작업 목적

Phase 39는 BreadGo MVP를 운영 환경으로 전환하기 전에 필요한 관측성 기반을 준비하는 단계입니다.
실제 Sentry, Slack, 외부 모니터링 서비스는 아직 연동하지 않고, 백엔드 로깅, 운영 상태 확인 API, 관리자 운영 점검 UI, 장애 알림 adapter skeleton을 추가했습니다.

## 변경 내용

### 백엔드

- Python `logging` 기반 공통 logger 설정 추가
- 처리되지 않은 서버 오류를 공통 handler에서 안전하게 로깅
- 기존 `/health` endpoint 유지
- 신규 관리자 전용 운영 상태 API 추가

```text
GET /api/v1/ops/status
```

운영 상태 API에서 확인하는 항목:

- 앱 상태
- DB 연결 상태
- 결제 Provider 준비 상태
- 알림 Channel 준비 상태
- 장애 알림 Notifier 준비 상태

추가된 장애 알림 adapter skeleton:

- `LogIncidentNotifier`
- `SlackIncidentNotifier`
- `SentryIncidentNotifier`

현재 외부 API 호출은 하지 않습니다.

### 프론트엔드

- 관리자 전용 운영 점검 화면 추가

```text
/admin/ops
```

- 관리자 NavBar에 `운영 점검` 링크 추가
- 운영 상태 카드와 Provider/Channel/Notifier 상태 카드 표시
- 모바일에서도 카드가 1열로 정리되도록 스타일 보강

### 문서

- 운영 모니터링 설계 문서 추가

```text
docs/ops-monitoring-design-phase39.md
```

## DB 변경 여부

없음.

이번 Phase는 운영 점검 구조와 문서 보강 중심이며, Alembic migration 또는 데이터베이스 스키마 변경은 없습니다.

## 검증 항목

백엔드:

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/smoke_test.py
```

프론트엔드:

```powershell
cd frontend
npm run lint
npm run build
```

수동 확인:

- `/health` 정상 응답
- 관리자 계정으로 `/admin/ops` 접근 가능
- 고객/가맹점 계정은 `/admin/ops` 접근 불가
- 운영 점검 화면에서 DB, 결제 Provider, 알림 Channel, 장애 Notifier 상태 표시
- 기존 예약, 결제, 알림, 정산 흐름 유지

## 한계

- Sentry 실제 연동 없음
- Slack 실제 webhook 발송 없음
- 외부 모니터링 서비스 연동 없음
- 로그 수집/검색 인프라 없음
- 장애 알림 재시도, 중복 방지, severity 정책은 아직 없음
- 운영 대시보드는 현재 상태 확인 중심이며 장기 지표 추이는 제공하지 않음

## 다음 단계

- Phase 40: Sentry 연동 준비 또는 실제 staging 환경 연동
- Phase 41: Slack 장애 알림 연동
- Phase 42: 운영 로그 수집/검색 구조 정리
- Phase 43: 관리자 운영 지표 대시보드 확장
- Phase 44: 배포 후 synthetic monitoring 또는 scheduled smoke check 준비
