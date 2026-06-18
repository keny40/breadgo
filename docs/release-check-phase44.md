# BreadGo Phase 44 릴리스 체크

## 작업 목적

Phase 44는 Flutter 고객 앱을 데모 가능한 수준으로 마감 정리하는 단계입니다.
신규 기능을 크게 추가하지 않고 UX 문구, 빈 화면, 오류 안내, 로그아웃, 실행 문서를 개선했습니다.

## 변경 내용

### Flutter UX 마감

- 로그인 오류 메시지를 더 쉬운 한국어로 정리
- 상품 목록 오류/빈 상태에 재시도 버튼 추가
- 내 예약 오류 상태에 재시도 버튼 추가
- 알림 오류 상태에 재시도 버튼 추가
- 로그인 필요 안내 문구 정리
- 네트워크/API 주소 오류 안내 개선

### Flutter 공통 UI

- `EmptyState`에 액션 버튼 지원 추가
- 입력 필드 공통 스타일 정리
- BreadGo green tone 유지
- 상단 이메일 말줄임 처리
- 긴 텍스트/작은 화면에서 overflow 가능성을 줄이도록 카드/버튼 배치 점검

### 로그아웃/세션 UX

- 상단 AppBar에 로그아웃 버튼 추가
- 로그아웃 후 로그인 탭으로 이동
- token이 없거나 401 응답이 발생하는 경우 로그인 필요 안내 유지

### 문서

- `mobile/README.md`를 BreadGo 모바일 앱 전용 문서로 교체
- `docs/mobile-release-summary-phase44.md` 추가
- Android emulator, 실제 기기, Render API 연결 방법 문서화

## DB 변경 여부

없음.

이번 Phase는 Flutter 앱 UX/문서 마감 작업이며 백엔드 DB/API 구조를 변경하지 않았습니다.

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

- 실제 PG 결제/환불 없음
- Push/Firebase/SMS/이메일/카카오 알림톡 미연동
- 지도 SDK 미연동
- JWT 보안 저장소 미적용
- 앱스토어 배포 설정 없음
- 가맹점/관리자 모바일 앱 없음

## 다음 단계

- Phase 45: Flutter 내 결제 화면 연결
- Phase 46: Flutter JWT 보안 저장소 적용 검토
- Phase 47: Flutter 앱 아이콘/스플래시 정리
- Phase 48: Flutter 지도/위치 탐색 UX 확장
