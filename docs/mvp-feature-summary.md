# BreadGo MVP Feature Summary

## 개요

BreadGo는 한국판 Too Good To Go를 지향하는 로컬 마감할인 푸드 플랫폼 MVP다. 소비자 예약/Mock 결제/픽업 흐름, 점주 상품/주문 운영, 관리자 운영 확인, BreadGo Pro 수율 관리 기능을 포함한다.

## 소비자 기능

- 회원가입, 로그인, 로그아웃
- 지역 기반 상품 조회
- 브라우저 현재 위치 기반 근처 상품 조회
- 상품 이미지와 할인 가격 확인
- 수령 방식 선택
  - 매장 픽업
  - 퀵배송 요청
  - 택배 배송
- 예약 생성
- Mock 결제 ready/confirm
- 내 예약, 내 결제 확인
- 픽업 코드 확인
- 예약 취소와 Mock 환불 상태 확인
- 예약 상태 이력 확인
- 인앱 알림 목록, 개별 읽음, 모두 읽음 처리

## 점주 기능

- 가맹점 등록
- 매장 등록 및 관리
- 상품 등록, 수정, 숨김, 다시 판매
- 상품 이미지 업로드
- 상품별 픽업/퀵배송/택배 가능 여부와 배송비 설정
- 주문/예약 관리
- 픽업 코드 조회와 픽업 확정
- 배송 상태 수동 변경
- 정산 내역 확인
- 정산 계좌 등록/수정
- CSV 상품 일괄 등록
- POS Mock 동기화

## 관리자 기능

- 관리자 대시보드
- 사용자, 가맹점, 매장, 상품, 예약, 결제 목록 확인
- 가맹점 승인 상태 변경
- 배송 상태 변경
- 정산 관리
- 운영 상태 확인
- Weekly Report batch/delivery/audit/health 운영 화면

## BreadGo Pro 기능

- 수율 대시보드
- 반복 상품 등록
- 요일별 상품 템플릿
- ESG/폐기 절감 리포트
- 추천 재고/할인가 MVP
- 추천 사용/채택/성과/퍼널 추적
- 고객 상품 조회/예약 전환 퍼널
- 다중 매장 통합 대시보드
- Free/Pro/Enterprise 플랜 MVP
- CSV import, 중복 감지, import 이력
- Mock POS integration, provider adapter, sync policy
- Inventory Ledger
- 재고 이상 감지와 조치 이력
- Daily Pro Brief, Daily Brief history

## Weekly Report 운영 기능

- Weekly Pro Report
- Weekly Report export
- Weekly Report snapshot/history/export
- Auto snapshot preview/execute
- Batch run/item log
- Admin 전체 merchant batch preview/execute
- Scheduler CLI
- Failed item retry
- Delivery preview/log
- In-app mock delivery
- Merchant Weekly Report notification
- Notification summary/list/unread count/read-all
- Unread reminder

## Audit / Health / Alert 운영 기능

- Admin Pro Operations Dashboard
- Operations Quick Actions
- Pro Operations Audit Trail
- Audit Log Explorer
- Audit Log CSV export
- Audit Log purge preview/execute
- Pro Operations Health Check
- Health Alert mock flow
- Health Alert list/detail/acknowledge/resolve
- Health Alert CLI scheduler

## Mock 처리된 기능

- Mock 결제
- Mock 환불
- Mock POS 동기화
- In-app mock delivery
- Health Alert 내부 alert
- Weekly Report scheduler CLI
- Health Alert scheduler CLI

## 아직 실제 연동되지 않은 기능

- 실제 PG 결제
- 실제 카드 환불
- 실제 퀵배송/택배 API
- 실제 이메일, SMS, 카카오, Push 발송
- Slack, Discord, Webhook 발송
- 외부 POS API
- 실제 AI 모델
- 실서버 cron 등록
- 자동 복구
- 자동 purge scheduler
- 세부 관리자 권한 분리
- 대량 비동기 큐

## 개인정보/토큰 원칙

Pro 운영 로그, delivery log, health alert, audit log에는 이메일, 전화번호, 주소, 외부 발송 토큰을 저장하거나 노출하지 않는다.
