# BreadGo Phase 49 릴리즈 체크

## 작업 목적

Phase 49는 BreadGo v0.3.0 Demo Release의 태그 생성 및 GitHub Release 발행 결과를 기록하는 문서화 단계입니다.
이번 작업에서는 실제 태그 생성이나 GitHub Release 발행을 수행하지 않고, 현재 확인 가능한 상태와 수동 발행 절차를 문서로 남겼습니다.

## 변경 파일

- `README.md`
- `docs/release-publish-result-v0.3.0.md`
- `docs/release-check-phase49.md`

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

태그/릴리즈 확인:

```powershell
git tag --list
git show v0.3.0-demo
git ls-remote --tags origin
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

참고: 최초 `npm run build` 확인 중 이전 빌드 타임아웃으로 `.next` 빌드 산출물 잠금이 남아 있었습니다.
생성 산출물인 `frontend/.next`만 제거한 뒤 재실행했으며, 최종 `npm run build`는 정상 통과했습니다.

## 태그/릴리즈 발행 상태

| 항목 | 상태 | 결과 |
| --- | --- | --- |
| 로컬 `v0.3.0-demo` 태그 | NOT FOUND | `git tag --list`에서 확인되지 않았습니다. |
| 로컬 태그 상세 | NOT FOUND | `git show v0.3.0-demo`에서 unknown revision 오류가 발생했습니다. |
| 원격 `v0.3.0-demo` 태그 | NOT FOUND | `git ls-remote --tags origin`에서 확인되지 않았습니다. |
| GitHub Release | NOT PUBLISHED | GitHub Releases 화면에서 아직 릴리즈가 없는 상태로 확인되었습니다. |

## DB 변경 여부

없음.

이번 Phase는 문서 중심 작업이며 백엔드 DB/API 구조를 변경하지 않았습니다.

## 배포 영향

- 배포 런타임 동작 변경 없음
- 기능 코드 변경 없음
- 실제 태그 생성 없음
- 실제 GitHub Release 발행 없음
- README와 릴리즈 발행 결과 문서만 갱신

## 남은 한계

- 실제 `v0.3.0-demo` 태그 생성은 수동으로 진행해야 합니다.
- 실제 GitHub Release 발행은 수동으로 진행해야 합니다.
- 발행 후 GitHub Release URL과 운영 URL Smoke Test 결과는 별도 확인이 필요합니다.
- 실제 PG/배송/외부 알림 연동은 아직 미구현입니다.

## 다음 단계

- Phase 49 문서 리뷰
- 검증 명령 실행 결과 확인
- 문서 변경분 커밋
- `v0.3.0-demo` 태그 수동 생성
- GitHub Release 수동 발행
- 발행 후 운영 URL Smoke Test 재확인
