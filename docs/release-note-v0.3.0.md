# BreadGo v0.3.0 Demo Release Note

## 릴리즈 개요

BreadGo v0.3.0은 웹 MVP와 Flutter 고객 앱 MVP를 함께 시연할 수 있는 데모 릴리즈 후보입니다.
고객은 마감 할인 상품을 탐색하고 예약/Mock 결제를 진행할 수 있으며, 가맹점은 상품과 주문, 정산을 관리할 수 있습니다.
관리자는 전체 운영 상태와 정산, 시스템 점검 화면을 확인할 수 있습니다.

## 배포 URL

- Frontend: [https://breadgo.vercel.app](https://breadgo.vercel.app)
- Backend: [https://breadgo-api.onrender.com](https://breadgo-api.onrender.com)
- Health: [https://breadgo-api.onrender.com/health](https://breadgo-api.onrender.com/health)
- Swagger: [https://breadgo-api.onrender.com/docs](https://breadgo-api.onrender.com/docs)
- Demo: [https://breadgo.vercel.app/demo](https://breadgo.vercel.app/demo)

## 데모 계정

```text
customer@breadgo.test / 12345678
merchant@breadgo.test / 12345678
admin@breadgo.test / 12345678
```

## 데모 가능한 주요 기능

- 고객 상품 탐색, 예약, Mock 결제, 예약 취소
- 픽업 코드 기반 픽업 확인
- 퀵배달/택배 요청 정보 저장
- 배송 상태 수동 변경
- 결제 완료 후 정산 데이터 생성
- 플랫폼 수수료, Mock PG 수수료, 점주 정산금 계산
- 예약 상태 이력 확인
- 인앱 알림 확인과 읽음 처리
- 운영 상태 점검

## 웹 고객 기능

- 회원가입/로그인/로그아웃
- 지역 기반 상품 탐색
- 현재 위치 기반 근처 상품 탐색
- 지도 기반 상품 탐색 UI
- 상품 상세 확인
- 수령 방식 선택
- 예약 생성
- Mock 결제
- 내 예약/내 결제 확인
- 예약 취소와 Mock 환불 상태 확인
- 알림센터와 상태 이력 확인

## 웹 가맹점 기능

- 가맹점/매장 관리
- 상품 등록/수정/숨김/재판매
- Vercel Blob 상품 이미지 업로드
- 상품별 수령 가능 방식과 배송비 설정
- 주문 관리
- 픽업 확정
- 배송 상태 변경
- 정산 계좌 등록
- 정산 내역 확인

## 웹 관리자 기능

- 관리자 대시보드
- 사용자/가맹점/매장/상품/예약/결제 목록 확인
- 가맹점 승인 상태 변경
- 정산 관리
- 운영 점검 화면
- 예약 상태 이력과 알림 확인

## Flutter 고객 앱 기능

- 고객 로그인
- 상품 목록/상세 조회
- 수령 방식 선택
- 예약 생성
- Mock 결제
- 내 예약 조회
- 예약 취소와 Mock 환불 상태 확인
- 알림 조회와 읽음 처리
- 예약 상태 이력 bottom sheet 확인

## 운영 점검/배포 문서

- [배포 환경 점검 체크리스트 v0.3.0](deployment-checklist-v0.3.0.md)
- [운영 URL Smoke Test v0.3.0](production-smoke-test-v0.3.0.md)
- [운영 URL Smoke Test 결과 v0.3.0](production-smoke-result-v0.3.0.md)
- [통합 데모 시나리오 v0.3.0](demo-scenario-v0.3.0.md)

## 아직 미구현인 기능

- 실제 PG 결제
- 실제 카드 환불
- 실제 배송/퀵배달/택배 API
- 실제 Push/Firebase/SMS/이메일/카카오 알림톡
- 실제 지도 SDK
- Flutter 가맹점/관리자 앱
- Flutter JWT 보안 저장소
- 앱스토어 배포 설정
- 정산 계좌 암호화와 실제 송금

## 주의사항

- Render 무료 인스턴스는 sleep 상태일 수 있어 첫 요청이 느릴 수 있습니다.
- 데모 전 [https://breadgo-api.onrender.com/health](https://breadgo-api.onrender.com/health)를 먼저 열어두는 것을 권장합니다.
- 데모 계정은 운영 서비스에 사용하면 안 됩니다.
- 실제 secret 값은 문서나 Git에 포함하지 않습니다.

## 다음 로드맵

1. Flutter 내 결제 화면 연결
2. Flutter JWT 보안 저장소 적용
3. 실제 Toss Payments 연동
4. 외부 알림 채널 연동
5. 지도 SDK 기반 위치 탐색 고도화
6. 가맹점 모바일 앱 시작
7. 정산 보안 강화
