# Changelog

## v0.3.0 Demo Release

BreadGo v0.3.0은 웹 MVP와 Flutter 고객 앱 MVP를 함께 데모할 수 있는 릴리즈 후보입니다.
Phase 33부터 Phase 47까지의 주요 작업을 정리했습니다.

### Web MVP

- 고객/가맹점/관리자 역할 기반 웹 플로우 정리
- 지역 기반 상품 탐색과 현재 위치 기반 근처 상품 탐색
- 지도 기반 상품 탐색 UI 추가
- 상품 대표 이미지 URL 및 Vercel Blob 업로드 지원
- 상품별 수령 가능 방식 설정
  - 매장 직접 픽업
  - 퀵배달 요청
  - 택배 배송
- 상품별 퀵배달비/택배 배송비 설정
- 고객 예약, Mock 결제, 예약 취소, Mock 환불 흐름
- 가맹점 주문 관리, 픽업 확정, 배송 상태 수동 변경
- 관리자 대시보드, 정산 관리, 운영 점검 화면
- 웹 모바일 반응형 UX 개선

### Backend/API

- 예약, 결제, 취소, 환불, 배송 상태, 정산 흐름 유지
- 예약 상태 이력 API 제공
- 고객/가맹점/관리자 권한 기반 API 유지
- 지역/근처 상품 탐색 API 제공
- 운영 상태 API 추가
  - `GET /api/v1/ops/status`

### Notifications

- 인앱 알림센터 추가
- 알림 읽음/모두 읽음 처리
- 예약, 결제, 픽업, 배송, 취소, 환불, 정산 이벤트 알림 생성
- 외부 알림 Channel skeleton 준비
  - Email
  - SMS
  - Kakao Alimtalk
  - Push

### Payments

- Mock 결제 흐름 유지
- Mock 환불 상태 처리
- 결제 Provider 구조 준비
- Toss Payments provider skeleton 추가
- 실제 PG API 호출은 아직 없음

### Operations

- Python logging 기반 공통 로깅 준비
- `/health` 유지
- `/api/v1/ops/status` 추가
- `/admin/ops` 운영 점검 UI 추가
- Slack/Sentry incident notifier skeleton 준비
- Render/Vercel/Neon 배포 문서 정리
- 운영 URL smoke test 결과 문서 추가

### Flutter Mobile App

- Flutter 고객 앱 MVP skeleton 추가
- 고객 로그인
- 상품 목록/상세 조회
- 수령 방식 선택
- 예약 생성
- Mock 결제
- 내 예약 조회
- 예약 취소 및 Mock 환불 상태 확인
- 인앱 알림 조회/읽음 처리
- 예약 상태 이력 bottom sheet 표시
- 모바일 릴리즈 품질 문구와 실행 문서 정리

### Documentation

- README Phase 44 기준 최신화
- 통합 데모 시나리오 v0.3.0 추가
- 통합 릴리즈 요약 v0.3.0 추가
- 배포 체크리스트 v0.3.0 추가
- 운영 URL smoke test 문서와 결과 문서 추가
- Flutter 모바일 앱 README 정리

### Known Limitations

- 실제 PG 결제/환불 미구현
- 실제 배송/퀵배달/택배 API 미연동
- 실제 Push/Firebase/SMS/이메일/카카오 알림톡 미연동
- 실제 지도 SDK 미연동
- Flutter 고객 앱만 구현
- Flutter JWT 보안 저장소 미적용
- 앱스토어 배포 설정 없음
- 정산 계좌 암호화와 실제 송금 미구현
- Render 무료 인스턴스 sleep 가능
