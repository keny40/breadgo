# BreadGo Phase 43 릴리스 체크

## 작업 목적

Phase 43은 Flutter 고객 앱 내 예약 화면에서 예약 상태 이력을 볼 수 있게 연결하는 단계입니다.
백엔드 DB/API 구조는 변경하지 않고 기존 예약 이력 API를 사용했습니다.

## 변경 내용

### ApiClient

- `GET /api/v1/reservations/{reservation_id}/history` 연결
- 예약 이력 목록 조회 함수 추가

### 모델

- `ReservationHistoryItem` 모델 추가
- 백엔드 응답 필드 반영:
  - `event_type`
  - `from_status`
  - `to_status`
  - `message`
  - `actor_role`
  - `actor_email`
  - `created_at`

### 상태 관리

- `ReservationController`에 예약별 이력 조회 상태 추가
- 예약별 이력 캐시 추가
- 이력 로딩/오류 상태 처리

### Flutter UI

- 내 예약 카드에 `상태 이력 보기` 버튼 추가
- bottom sheet 기반 상태 이력 타임라인 추가
- 이벤트 타입을 한국어 라벨로 표시
- 이력이 없거나 조회 실패 시 안내 표시

## DB 변경 여부

없음.

이번 Phase는 Flutter 모바일 앱 API 연결과 UI 추가 작업이며, 백엔드 스키마와 API 구조를 변경하지 않았습니다.

## 검증 항목

백엔드:

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/smoke_test.py
```

웹 프론트엔드:

```powershell
cd frontend
npm run lint
npm run build
```

Flutter:

```powershell
cd mobile
flutter pub get
dart format lib test
flutter analyze --no-pub
flutter test --no-pub
```

## 한계

- 상태 이력은 읽기 전용입니다.
- 모바일 관리자/가맹점 이력 화면은 아직 없습니다.
- 이력 검색/필터는 아직 없습니다.
- JWT 보안 저장소, Push, Firebase, 실제 PG는 이번 Phase에서 제외했습니다.

## 다음 단계

- Phase 44: Flutter 내 결제 화면 연결
- Phase 45: Flutter 알림/예약 refresh UX 고도화
- Phase 46: Flutter JWT 보안 저장소 적용 검토
- Phase 47: Flutter 지도/위치 탐색 UX 확장
