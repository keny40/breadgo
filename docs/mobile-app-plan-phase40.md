# BreadGo Phase 40 Flutter 모바일 앱 계획

## 시작 목적

Phase 40은 BreadGo 웹 MVP와 FastAPI 백엔드를 바탕으로 고객용 Flutter 모바일 앱의 첫 골격을 만드는 단계입니다.
이번 Phase의 목표는 전체 기능 완성이 아니라, 기존 백엔드와 연결 가능한 앱 구조를 만들고 고객 조회 흐름을 검증하는 것입니다.

## 현재 포함된 화면

Flutter 앱 폴더:

```text
mobile/
```

포함 화면:

- 로그인 화면
- 상품 목록 화면
- 상품 상세 화면
- 내 예약 화면
- 알림 화면 메뉴 skeleton

이번 Phase에서 제외한 기능:

- 예약 생성
- Mock 결제
- Mock 환불
- 픽업 확인
- 배송 상태 변경
- 지도 SDK
- Push 알림
- Firebase
- 앱스토어 배포 설정

## API 연결 구조

핵심 파일:

```text
mobile/lib/core/app_config.dart
mobile/lib/core/api_client.dart
mobile/lib/core/session_store.dart
```

기본 API 주소:

```text
http://10.0.2.2:8000
```

Android emulator에서는 `localhost`가 emulator 자기 자신을 의미하므로, 호스트 PC의 로컬 FastAPI 서버에 접근하려면 `10.0.2.2`를 사용합니다.

실행 시 API 주소를 바꾸려면:

```powershell
flutter run --dart-define=BREADGO_API_BASE_URL=https://breadgo-api.onrender.com
```

현재 연결된 API:

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/regions/products`
- `GET /api/v1/reservations/me`

## 상태 관리 구조

복잡한 상태관리 패키지는 도입하지 않았습니다.

현재 사용 구조:

- `ChangeNotifier`
- `AuthController`
- `ProductController`
- `ReservationController`

JWT access token은 `SessionStore`에 저장하는 구조만 준비했습니다.
이번 Phase에서는 보안 저장소 연동을 하지 않았으며, 다음 Phase에서 `flutter_secure_storage` 같은 패키지 도입을 검토할 수 있습니다.

## 로컬 실행 방법

백엔드 실행:

```powershell
cd backend
python -m alembic upgrade head
python scripts/seed_demo.py
python -m uvicorn app.main:app --reload --port 8000
```

Flutter 앱 실행:

```powershell
cd mobile
flutter pub get
flutter run
```

Android emulator에서 로컬 백엔드에 붙을 때:

```powershell
flutter run --dart-define=BREADGO_API_BASE_URL=http://10.0.2.2:8000
```

Render 배포 백엔드에 붙을 때:

```powershell
flutter run --dart-define=BREADGO_API_BASE_URL=https://breadgo-api.onrender.com
```

실제 Android 기기에서 테스트할 때는 `10.0.2.2` 대신 PC의 LAN IP를 사용합니다.

```powershell
flutter run --dart-define=BREADGO_API_BASE_URL=http://192.168.0.10:8000
```

이 경우 FastAPI는 다음처럼 외부 접근이 가능한 host로 실행합니다.

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Android emulator 주의사항

- `http://localhost:8000`은 emulator 내부 주소입니다.
- 로컬 PC에서 실행 중인 FastAPI는 `http://10.0.2.2:8000`으로 접근합니다.
- 실제 Android 기기에서 테스트할 경우 PC와 같은 네트워크에 연결한 뒤 PC의 LAN IP를 사용해야 합니다.
- HTTP cleartext 통신은 개발용으로만 사용하고, 운영 배포에서는 HTTPS 백엔드를 사용해야 합니다.

## 다음 Phase에서 할 일

- 상품 예약 생성 연결
- 수령 방식 선택 연결
- Mock 결제 연결
- 인앱 알림 API 연결
- JWT 보안 저장소 적용
- 고객 취소/Mock 환불 UI 연결
- 지도 기반 탐색 UX 검토
- Android/iOS 앱 아이콘과 splash 정리
