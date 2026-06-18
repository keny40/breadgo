# BreadGo Phase 46 릴리즈 체크

## 작업 목적

Phase 46은 BreadGo v0.3.0 데모 릴리즈를 실제 배포 환경 기준으로 점검하기 위한 문서를 추가하는 단계입니다.
Vercel, Render, Neon 환경 변수와 운영 URL 기준 smoke test 절차를 정리했습니다.

## 변경 파일

- `README.md`
- `docs/deployment-checklist-v0.3.0.md`
- `docs/production-smoke-test-v0.3.0.md`
- `docs/release-check-phase46.md`

## 검증 명령

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

## 검증 결과

다음 항목을 모두 실행했고 통과했습니다.

- 백엔드 `python -m compileall app scripts` 통과
- 백엔드 `python -m alembic upgrade head` 통과
- 백엔드 `python scripts/smoke_test.py` 통과
- 웹 `npm run lint` 통과
- 웹 `npm run build` 통과
- Flutter `flutter pub get` 통과
- Flutter `dart format lib test` 통과
- Flutter `flutter analyze --no-pub` 통과
- Flutter `flutter test --no-pub` 통과

## DB 변경 여부

없음.

이번 Phase는 문서 중심 작업이며 백엔드 DB/API 구조를 변경하지 않았습니다.

## 배포 영향

- 배포 런타임 동작 변경 없음
- 기능 코드 변경 없음
- 운영 URL 점검 문서와 배포 체크리스트만 추가

## 남은 한계

- 실제 운영 URL smoke test는 사람이 배포 환경에서 직접 수행해야 합니다.
- 실제 secret 값은 문서에 포함하지 않습니다.
- 실제 PG 결제/환불은 아직 연결되어 있지 않습니다.
- 실제 배송/외부 알림/Push/Firebase는 아직 연결되어 있지 않습니다.

## 다음 단계

- v0.3.0 데모 릴리즈 태그 생성 검토
- 운영 URL smoke test 수동 수행
- Flutter 내 결제 화면 연결
- Flutter JWT 보안 저장소 적용
- 실제 PG 연동 준비
