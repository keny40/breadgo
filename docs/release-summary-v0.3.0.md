# BreadGo MVP 릴리즈 요약 v0.3.0

## BreadGo MVP 개요

BreadGo는 동네 빵집의 남은 마감 할인 상품을 고객이 예약하고 픽업 또는 배송 요청할 수 있는 로컬 푸드 리스큐 마켓플레이스 MVP입니다.

v0.3.0 기준으로 웹 고객/가맹점/관리자 플로우와 Flutter 고객 앱 핵심 플로우가 데모 가능한 수준으로 정리되었습니다.

## Phase 33~45 주요 변경 요약

- Phase 33: 인앱 알림센터 추가
- Phase 35: 웹 모바일 반응형 UX 개선
- Phase 36: 지도 기반 상품 탐색 UI 추가
- Phase 37: 결제 Provider 구조 준비
- Phase 38: 알림 Channel 구조 준비
- Phase 39: 운영 모니터링/로깅/장애 알림 준비
- Phase 40: Flutter 고객 앱 MVP skeleton 추가
- Phase 41: Flutter 예약 생성/Mock 결제 연결
- Phase 42: Flutter 알림센터/예약 취소 연결
- Phase 43: Flutter 예약 상태 이력 연결
- Phase 44: Flutter 릴리즈 품질 마감
- Phase 45: 통합 릴리즈 문서와 데모 시나리오 정리

## 현재 가능한 사용자 흐름

고객:

- 상품 탐색
- 지역/근처 상품 확인
- 상품 상세 확인
- 수령 방식 선택
- 예약 생성
- Mock 결제
- 내 예약/결제 확인
- 예약 취소
- Mock 환불 상태 확인
- 알림 확인
- 상태 이력 확인

가맹점:

- 가맹점/매장 관리
- 상품 등록/수정/숨김/재판매
- 이미지 업로드
- 주문 관리
- 픽업 확정
- 배송 상태 변경
- 정산 내역 확인
- 정산 계좌 관리

관리자:

- 전체 운영 현황 확인
- 사용자/가맹점/매장/상품/예약/결제 관리
- 가맹점 승인 상태 변경
- 정산 관리
- 운영 상태 점검

## 웹/모바일 지원 범위

웹:

- 고객, 가맹점, 관리자 플로우 지원
- 예약, 결제, 취소, 환불, 픽업, 배송, 정산, 알림, 이력 지원

Flutter:

- 고객 플로우 지원
- 로그인, 상품 조회, 예약, Mock 결제, 내 예약, 취소, 알림, 이력 지원
- 가맹점/관리자 모바일 앱은 아직 없음

## 기술 구조

백엔드:

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- JWT 인증

웹 프론트엔드:

- Next.js
- TypeScript
- Vercel 배포
- Vercel Blob 이미지 업로드

모바일:

- Flutter
- ChangeNotifier 기반 단순 상태 관리
- FastAPI API client

배포:

- Vercel: 웹 프론트엔드
- Render: FastAPI 백엔드
- Neon: PostgreSQL

운영 준비:

- `/health`
- `/api/v1/ops/status`
- `/admin/ops`
- 결제 Provider skeleton
- 알림 Channel skeleton
- 장애 알림 Notifier skeleton
- smoke test

## 운영 전환 전 남은 과제

- 실제 PG 결제 승인/취소/환불 연동
- PG webhook 검증
- 실제 배송/퀵배달/택배 API 연동
- 이메일/SMS/카카오 알림톡/Push 연동
- Sentry/Slack 실제 운영 연동
- 이메일 인증
- 비밀번호 재설정
- 관리자 계정 생성/권한 관리 정책
- 정산 계좌 암호화
- 백업/복구 정책
- 개인정보 처리/보안 점검

## 기술적 한계

- Mock 결제/Mock 환불만 지원
- 실제 송금 없음
- 실제 지도 SDK 없음
- Flutter JWT 보안 저장소 미적용
- Flutter 앱스토어 배포 설정 없음
- Render 무료 인스턴스 sleep 가능
- 운영 규모 부하 테스트 미수행

## 다음 로드맵

1. Flutter 내 결제 화면 연결
2. Flutter JWT 보안 저장소 적용
3. Toss Payments 실제 연동
4. PG webhook 및 환불 플로우 구현
5. Push/Firebase 또는 외부 알림 채널 연동
6. 지도 SDK 기반 위치 탐색 고도화
7. 가맹점 모바일 앱 시작
8. 운영 모니터링 실제 연동
9. 정산 보안 강화
10. 리뷰/평점/포인트/쿠폰
11. AI 할인 추천/수요 예측
