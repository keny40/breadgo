# BreadGo Phase 41 릴리스 체크

## 작업 목적

Phase 41은 Flutter 고객 앱에서 상품 상세, 수령 방식 선택, 예약 생성, Mock 결제, 내 예약 갱신 흐름을 연결하는 단계입니다.
기존 FastAPI 백엔드 API를 그대로 사용하며, 백엔드 DB/API 스키마는 변경하지 않았습니다.

## 변경 내용

### Flutter 상품 상세 화면

- 상품별 가능한 수령 방식만 표시
- `PICKUP`, `QUICK_DELIVERY`, `PARCEL_DELIVERY` 백엔드 enum 값 사용
- 퀵배달비/택배비 표시
- 수량 선택 추가
- 배송 방식 선택 시 수령자, 연락처, 주소, 배송 요청사항 입력 표시
- 총 고객 결제금액 표시

### 예약 생성

- `POST /api/v1/reservations` 호출 추가
- 예약 실패 시 사용자 친화적 오류 메시지 표시
- 배송 정보 누락 시 모바일에서 먼저 검증

### Mock 결제

- `POST /api/v1/payments/mock/ready` 호출 추가
- `POST /api/v1/payments/mock/confirm` 호출 추가
- 결제 method는 MVP 기본값 `MOCK_CARD` 사용
- 결제 성공 후 내 예약 목록 새로고침

### 내 예약 화면

- 예약/결제 후 새로고침 가능
- 예약 상태, 결제 상태, 수령 방식, 배송 상태, 픽업 코드 표시 유지

### 상태 관리

- `ReservationController`에 예약/결제 처리 상태 추가
- 처리 중 버튼 비활성화
- 성공/실패 메시지 관리

## DB 변경 여부

없음.

이번 Phase는 Flutter 모바일 앱 연결 작업만 진행했으며, 백엔드 데이터베이스와 API 구조는 변경하지 않았습니다.

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
flutter analyze
```

## Flutter 검증 가능 여부

Flutter SDK:

```text
Flutter 3.41.6
Dart 3.11.4
```

`flutter pub get`과 `dart format lib test`를 실행합니다.
이번 Phase에서는 `flutter analyze --no-pub`가 정상 완료되었고 이슈가 발견되지 않았습니다.

## 한계

- 실제 PG 결제 없음
- Mock 결제 수단 선택은 아직 단일 `MOCK_CARD`
- 모바일 예약 취소/Mock 환불 미연결
- 모바일 알림센터 API 미연결
- JWT 보안 저장소 미적용
- 배송 상태 상세 조회/관리 UI는 아직 없음

## 다음 단계

- Phase 42: Flutter 내 예약 취소 및 Mock 환불 연결
- Phase 43: Flutter 알림센터 API 연결
- Phase 44: Flutter 결제 수단 선택 UI 정리
- Phase 45: Flutter 지도/위치 탐색 UX 확장
