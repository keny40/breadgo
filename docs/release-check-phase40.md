# BreadGo Phase 40 릴리스 체크

## 작업 목적

Phase 40은 BreadGo 고객용 Flutter 모바일 앱 MVP skeleton을 추가하는 단계입니다.
기존 FastAPI 백엔드와 연결 가능한 구조를 만들고, 로그인, 상품 조회, 상품 상세, 내 예약 조회 중심으로 앱 흐름을 시작했습니다.

## 변경 내용

### Flutter 프로젝트

새 폴더:

```text
mobile/
```

Flutter 기본 프로젝트를 생성하고 앱 이름을 BreadGo로 설정했습니다.

### 모바일 앱 화면

추가된 고객 앱 화면:

- 로그인
- 상품 목록
- 상품 상세
- 내 예약
- 알림 메뉴 skeleton

### API client

추가된 구조:

- `ApiClient`
- `SessionStore`
- `AuthController`
- `ProductController`
- `ReservationController`

연결된 API:

- 로그인
- 내 정보 조회
- 지역 상품 조회
- 내 예약 조회

### UI

- BreadGo green tone 기반 Material theme 적용
- 모바일 카드형 상품 목록
- 상품 이미지 placeholder 처리
- 픽업 코드가 보이는 예약 카드
- 알림 화면은 다음 Phase 연동 안내만 표시

## DB 변경 여부

없음.

백엔드 DB/API 스키마 변경 없이 Flutter 앱 skeleton만 추가했습니다.

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

Flutter:

```powershell
cd mobile
flutter pub get
flutter analyze
```

## Flutter 검증 가능 여부

이 환경에서는 Flutter SDK가 `C:\flutter\bin\flutter`에서 확인되었습니다.
확인된 버전:

```text
Flutter 3.41.6
Dart 3.11.4
```

`flutter create`로 프로젝트를 생성했고 `flutter pub get`은 정상 완료되었습니다.
다만 `flutter analyze`, `flutter analyze lib test --no-pub`, `dart analyze`는 출력 없이 제한 시간 안에 완료되지 않아 정적 분석 완료 여부를 확인하지 못했습니다.
앱 코드는 Flutter 기본 프로젝트 구조 안에 작성되어 있으며, 다음 로컬 점검 시 분석 명령을 다시 실행해야 합니다.

## 한계

- 모바일 앱에서 예약 생성은 아직 연결하지 않음
- Mock 결제는 아직 연결하지 않음
- 알림센터 API는 아직 연결하지 않음
- JWT는 보안 저장소가 아닌 skeleton `SessionStore` 구조만 준비
- Android/iOS 앱스토어 배포 설정 없음
- Firebase, Push, 지도 SDK 연동 없음
- 모바일 UI는 고객 조회 흐름 중심의 MVP skeleton

## 다음 단계

- Phase 41: 모바일 예약 생성 및 수령 방식 선택
- Phase 42: 모바일 Mock 결제 연결
- Phase 43: 모바일 내 예약 취소/Mock 환불 연결
- Phase 44: 모바일 인앱 알림센터 연결
- Phase 45: 모바일 지도 탐색 UX 개선
