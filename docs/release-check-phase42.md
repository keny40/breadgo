# BreadGo Phase 42 릴리스 체크

## 작업 목적

Phase 42는 Flutter 고객 앱에서 알림센터 API와 예약 취소/Mock 환불 흐름을 연결하는 단계입니다.
기존 백엔드 API를 그대로 사용하고, 백엔드 DB/API 구조는 변경하지 않았습니다.

## 변경 내용

### Flutter 알림센터

- 알림 skeleton 화면을 실제 API 기반 화면으로 변경
- `GET /api/v1/notifications/me` 연결
- 읽지 않은 알림 강조 표시
- 개별 읽음 처리 연결
- 모두 읽음 처리 연결
- 빈 목록, 로딩, 오류 상태 처리
- 하단 알림 탭에 읽지 않은 알림 개수 badge 표시

### Flutter 예약 취소

- 내 예약 카드에 취소 가능한 예약만 `예약 취소` 버튼 표시
- 취소 전 확인 다이얼로그 표시
- `POST /api/v1/reservations/{reservation_id}/cancel` 연결
- 취소 성공 후 내 예약 목록 자동 갱신
- 취소 불가 상태 안내 문구 표시

### 상태 관리

- `NotificationController` 추가
- 알림 목록, 읽음 처리, 모두 읽음 처리 상태 관리
- `ReservationController`에 예약 취소 처리 상태 추가
- 중복 클릭 방지
- API 실패 시 사용자 친화적 메시지 표시

## DB 변경 여부

없음.

이번 Phase는 Flutter 앱 API 연결 작업이며 백엔드 스키마와 API 구조를 변경하지 않았습니다.

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

- 실제 PG 환불 없음
- 모바일 알림은 인앱 알림만 표시
- Push/Firebase/SMS/이메일/카카오 알림톡 연동 없음
- 모바일 예약 상태 이력 화면은 아직 없음
- JWT 보안 저장소는 아직 미적용

## 다음 단계

- Phase 43: Flutter 예약 상태 이력 화면 연결
- Phase 44: Flutter 내 결제 화면 연결
- Phase 45: Flutter 알림 badge/refresh UX 고도화
- Phase 46: Flutter JWT 보안 저장소 적용 검토
