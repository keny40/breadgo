# BreadGo Flutter Mobile MVP

BreadGo 고객용 Flutter 모바일 앱 MVP입니다.

현재 앱은 기존 FastAPI 백엔드와 연결해 고객 데모 흐름을 확인하는 용도입니다. 실제 앱스토어 배포, Firebase, Push, 지도 SDK, 실제 PG 결제는 아직 포함하지 않습니다.

## 포함된 고객 기능

- 고객 로그인
- 지역 기반 상품 목록 조회
- 상품 상세 조회
- 수령 방식 선택
  - 매장 직접 픽업
  - 퀵배달 요청
  - 택배 배송
- 예약 생성
- Mock 결제
- 내 예약 조회
- 예약 취소 및 Mock 환불 상태 확인
- 알림 조회
- 알림 개별 읽음 처리
- 알림 모두 읽음 처리
- 예약 상태 이력 확인

## 테스트 계정

```text
customer@breadgo.test / 12345678
```

데모 데이터를 먼저 생성해야 합니다.

```powershell
cd backend
python scripts/seed_demo.py
```

## 로컬 백엔드 실행

```powershell
cd backend
python -m alembic upgrade head
python scripts/seed_demo.py
python -m uvicorn app.main:app --reload --port 8000
```

## Android Emulator 실행

Android emulator에서 호스트 PC의 `localhost`에 접근하려면 `10.0.2.2`를 사용합니다.

```powershell
cd mobile
flutter pub get
flutter run --dart-define=BREADGO_API_BASE_URL=http://10.0.2.2:8000
```

앱 기본 API 주소도 개발 편의를 위해 다음 값으로 설정되어 있습니다.

```text
http://10.0.2.2:8000
```

## 실제 Android 기기 테스트

실제 기기에서는 `10.0.2.2`가 동작하지 않습니다.
PC와 휴대폰을 같은 네트워크에 연결한 뒤 PC의 LAN IP를 사용합니다.

예:

```powershell
flutter run --dart-define=BREADGO_API_BASE_URL=http://192.168.0.10:8000
```

FastAPI 서버도 외부 접근이 가능하도록 실행해야 합니다.

```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Render 배포 API 사용

배포된 Render 백엔드를 사용하려면 다음처럼 실행합니다.

```powershell
cd mobile
flutter run --dart-define=BREADGO_API_BASE_URL=https://breadgo-api.onrender.com
```

Render free instance는 잠들 수 있으므로 첫 요청이 느릴 수 있습니다.

## 검증 명령

```powershell
cd mobile
flutter pub get
dart format lib test
flutter analyze --no-pub
flutter test --no-pub
```

## 현재 한계

- 실제 PG 결제 없음
- 실제 PG 환불 없음
- Push/Firebase/SMS/이메일/카카오 알림톡 없음
- 지도 SDK 없음
- JWT 보안 저장소 미적용
- 앱 아이콘과 스플래시는 Flutter 기본값 기반
- 가맹점/관리자 모바일 앱은 아직 없음
