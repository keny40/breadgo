# BreadGo Phase 47 릴리즈 체크

## 작업 목적

Phase 47은 BreadGo v0.3.0 운영 URL 기준 smoke test 수행 결과를 문서로 남기는 단계입니다.
기능 코드는 변경하지 않고, 실제로 확인한 운영 URL과 API 결과를 PASS/FAIL/SKIP/NOT TESTED 형태로 기록했습니다.

## 변경 파일

- `README.md`
- `docs/production-smoke-result-v0.3.0.md`
- `docs/release-check-phase47.md`

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

다음 항목을 실행했습니다.

- 백엔드 `python -m compileall app scripts` 통과
- 백엔드 `python -m alembic upgrade head` 통과
- 백엔드 `python scripts/smoke_test.py` 1차 실패 후 조치하여 재실행 통과
- 웹 `npm run lint` 통과
- 웹 `npm run build` 통과
- Flutter `flutter pub get` 통과
- Flutter `dart format lib test` 통과
- Flutter `flutter analyze --no-pub` 통과
- Flutter `flutter test --no-pub` 통과

Smoke test 1차 실패 기록:

- 실패 항목: `Region products found`
- 실패 원인: 로컬 데모 상품 목록이 비어 있음
- 조치: `python scripts/seed_demo.py` 실행으로 로컬 데모 데이터 복구
- 재실행 결과: 전체 PASS

## 운영 URL 점검 수행 여부

수행함.

직접 확인한 항목:

- `https://breadgo.vercel.app`
- `https://breadgo.vercel.app/demo`
- `https://breadgo-api.onrender.com/health`
- `https://breadgo-api.onrender.com/docs`
- 고객/가맹점/관리자 API 로그인
- 지역 상품 API
- 고객 내 예약 API
- 고객 알림 API
- 가맹점 예약/주문 API
- 관리자 summary API
- 관리자 ops API

운영 DB 변경을 피하기 위해 실행하지 않은 항목:

- 예약 생성
- Mock 결제
- 픽업 확정
- 배송 상태 변경
- 정산 상태 변경

## DB 변경 여부

없음.

이번 Phase는 문서 중심 작업이며 백엔드 DB/API 구조를 변경하지 않았습니다.

## 배포 영향

- 배포 런타임 동작 변경 없음
- 기능 코드 변경 없음
- 운영 URL smoke test 결과 문서와 README 링크만 추가

## 남은 한계

- 브라우저 UI 전체 수동 smoke test는 별도로 수행 필요
- 운영 DB를 변경하는 쓰기 작업은 이번 결과 기록에서 SKIP
- 실제 secret 값은 확인하거나 기록하지 않음
- 실제 PG 결제/환불은 아직 연결되어 있지 않음
- 실제 배송/외부 알림/Push/Firebase는 아직 연결되어 있지 않음

## 다음 단계

- 브라우저 기반 운영 URL 수동 smoke test 전체 수행
- v0.3.0 데모 릴리즈 태그 생성 검토
- Flutter 내 결제 화면 연결
- Flutter JWT 보안 저장소 적용
- 실제 PG 연동 준비
