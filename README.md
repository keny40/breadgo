# BreadGo MVP

BreadGo는 동네 빵집의 마감 할인 상품을 고객이 예약하고, 결제하고, 픽업 또는 배송 요청까지 할 수 있는 로컬 푸드 리스큐 마켓플레이스 MVP입니다.

현재 프로젝트는 데모 가능한 수준의 MVP 기능을 구현한 상태입니다. 실제 결제, 실제 배송, 실제 알림 채널 연동은 아직 포함하지 않고, 서비스 흐름 검증을 위한 Mock 기능과 운영 화면 중심으로 구성되어 있습니다.

## 현재 진행 상태

### 완료된 핵심 기능

- 회원가입, 로그인, 로그아웃
- JWT 인증
- 사용자 역할 구분
  - CUSTOMER
  - MERCHANT
  - ADMIN
- 역할별 로그인 후 리다이렉트
- 역할별 NavBar 메뉴 분리
- 로그인 사용자 이메일 NavBar 표시
- 역할 기반 페이지 접근 제한
- 데모 계정 및 데모 데이터 seed
- 백엔드 smoke test 스크립트

### 고객 기능

- 지역 기반 상품 탐색
- 브라우저 현재 위치 기반 근처 상품 탐색
- 상품 카드 이미지 표시
- 상품별 수령 방식 선택
  - 매장 직접 픽업
  - 퀵배달 요청
  - 택배 배송
- 상품별 수령 가능 방식 제한
- 상품별 퀵배달비, 택배 배송비 설정 반영
- 예약 생성
- Mock 결제
  - 카드 모의결제
  - 카카오페이 모의결제
  - 네이버페이 모의결제
- 내 예약 확인
- 내 결제 확인
- 픽업 코드 확인
- 예약 취소
- Mock 환불 상태 처리
- 예약/주문 상태 이력 확인
- 인앱 알림 확인 및 읽음 처리

### 가맹점 기능

- 가맹점 등록
- 가맹점 대시보드
- 매장 등록 및 관리
- 매장 지역 정보 등록
  - 시/도
  - 시/군/구
  - 동/읍/면
  - 위도/경도
- 상품 등록
- 상품 대표 이미지 URL 등록
- Vercel Blob 기반 상품 이미지 업로드
- 상품 수정
- 재고 수정
- 상품 숨김 처리
- 숨김 상품 다시 판매
- 상품별 수령 가능 방식 설정
- 퀵배달비, 택배 배송비 설정
- 픽업 코드 조회
- 픽업 확정
- 주문 관리
- 픽업/퀵배달/택배 주문 필터링
- 배송 상태 수동 변경
- 정산 내역 확인
- 정산 계좌 등록 및 수정
- 주문 상태 이력 확인
- 인앱 알림 확인 및 읽음 처리

### 관리자 기능

- 관리자 대시보드
- 사용자 목록 확인
- 가맹점 목록 확인
- 가맹점 승인 상태 변경
- 매장 목록 확인
- 상품 목록 확인
- 예약 목록 확인
- 결제 목록 확인
- 배송 상태 변경
- 정산 관리
- 정산 상태 변경
  - 정산 완료
  - 정산 보류
- 예약 상태 이력 확인
- 인앱 알림 확인 및 읽음 처리

### 운영/정산 기능

- Mock 결제 상태 관리
- 예약 취소 시 재고 복구
- 예약 취소 시 Mock 환불 상태 반영
- 결제 완료 후 정산 데이터 생성
- 픽업 완료 후 정산 가능 상태 전환
- 관리자 정산 완료/보류 처리
- 플랫폼 수수료 계산
- Mock PG 수수료 계산
- 점주 정산금 계산
- 정산 계좌 정보 등록

### 감사 이력 및 알림

- 예약 상태 이력 저장
- 결제 완료 이력 저장
- 픽업 완료 이력 저장
- 배송 상태 변경 이력 저장
- 예약 취소 이력 저장
- Mock 환불 이력 저장
- 정산 상태 변경 이력 저장
- 인앱 알림 센터
- 알림 읽음 처리
- 알림 모두 읽음 처리
- NavBar 미읽음 알림 개수 표시

## 얼마나 남았나

현재 상태는 `로컬/데모용 MVP` 기준으로 약 85~90% 완료된 상태입니다.

남은 작업은 주로 실제 운영 전환을 위한 기능입니다.

### 남은 주요 과제

- 실제 PG 결제 연동
  - Toss Payments, KakaoPay, NaverPay, Stripe 등
  - 결제 승인, 취소, 환불 webhook 처리
- 실제 배송/퀵배달 연동
  - 배달 대행 API
  - 송장/택배사 API
  - 배송비 정책 고도화
- 실시간 알림 연동
  - 이메일
  - SMS
  - 카카오 알림톡
  - 모바일 push
- 지도 기반 UX
  - 지도 표시
  - 거리순 정렬 고도화
  - 위치 권한 UX 개선
- 운영 보안 강화
  - 이메일 인증
  - 비밀번호 재설정
  - 관리자 계정 생성 프로세스
  - 정산 계좌 정보 암호화
- 프로덕션 운영 준비
  - 로깅
  - 모니터링
  - 장애 알림
  - 백업/복구 정책
  - 배포 자동화
- 모바일 앱
  - Flutter 고객 앱
  - Flutter 가맹점 앱
- 리뷰/평점/포인트/쿠폰
- AI 기능
  - 수요 예측
  - 동적 할인 추천
  - 폐기 예측
  - 개인화 추천

## 배포 URL

- 프론트엔드: [https://breadgo.vercel.app](https://breadgo.vercel.app)
- 백엔드: [https://breadgo-api.onrender.com](https://breadgo-api.onrender.com)
- 백엔드 Health Check: [https://breadgo-api.onrender.com/health](https://breadgo-api.onrender.com/health)
- 백엔드 Swagger: [https://breadgo-api.onrender.com/docs](https://breadgo-api.onrender.com/docs)
- 데모 가이드: [https://breadgo.vercel.app/demo](https://breadgo.vercel.app/demo)

Render 무료 인스턴스는 일정 시간 요청이 없으면 sleep 상태가 될 수 있습니다. 첫 요청은 느릴 수 있습니다.

## 데모 계정

```text
customer@breadgo.test / 12345678
merchant@breadgo.test / 12345678
admin@breadgo.test / 12345678
```

## 추천 데모 흐름

### 고객

1. `customer@breadgo.test`로 로그인
2. `/products`에서 지역 선택 또는 `내 위치로 찾기`
3. 상품 선택
4. 수령 방식 선택
5. 예약 생성
6. Mock 결제
7. `/my-reservations`에서 픽업 코드와 상태 확인
8. `/my-payments`에서 결제 상태 확인
9. `/notifications`에서 알림 확인

### 가맹점

1. `merchant@breadgo.test`로 로그인
2. `/merchant`에서 대시보드 확인
3. `/merchant/stores`에서 매장 확인 또는 등록
4. `/merchant/products`에서 상품 등록/수정/숨김 처리
5. 상품 이미지 업로드
6. `/merchant/orders`에서 주문 확인
7. 픽업 주문은 픽업 확정
8. 배송 주문은 배송 상태 변경
9. `/merchant/settlements`에서 정산 내역 확인
10. `/notifications`에서 알림 확인

### 관리자

1. `admin@breadgo.test`로 로그인
2. `/admin`에서 전체 운영 현황 확인
3. 사용자, 가맹점, 매장, 상품, 예약, 결제 확인
4. `/admin/settlements`에서 정산 관리
5. 예약 상태 이력 확인
6. `/notifications`에서 알림 확인

## 로컬 개발 실행

Docker 없이 로컬 Windows PostgreSQL 기준으로 실행합니다.

### 백엔드

```powershell
cd backend
.\.venv\Scripts\activate
python -m alembic upgrade head
python scripts/seed_demo.py
python -m uvicorn app.main:app --reload --port 8000
```

가상환경을 사용하지 않는 경우에도 `backend` 폴더에서 동일한 Python 명령을 실행하면 됩니다.

### 백엔드 Smoke Test

백엔드 서버가 실행 중인 상태에서 다른 터미널에서 실행합니다.

```powershell
cd backend
python scripts/smoke_test.py
```

기대 결과:

```text
[PASS] Health check
[PASS] Customer login
[PASS] Region products found
[PASS] Reservation created
[PASS] Mock payment confirmed
[PASS] Pickup confirmed
[PASS] Admin summary loaded
[PASS] BreadGo MVP smoke test completed
```

### 프론트엔드

```powershell
cd frontend
npm install
npm run dev
```

브라우저에서 엽니다.

[http://localhost:3000/demo](http://localhost:3000/demo)

## 검증 명령

### 백엔드

```powershell
cd backend
python -m compileall app scripts
python -m alembic upgrade head
python scripts/smoke_test.py
```

### 프론트엔드

```powershell
cd frontend
npm run lint
npm run build
```

## 환경 변수

### 백엔드

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
JWT_SECRET_KEY=replace-with-secure-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
PYTHON_VERSION=3.12.8
```

배포 환경에서는 `BACKEND_CORS_ORIGINS`에 Vercel 프론트엔드 URL을 포함해야 합니다.

```text
BACKEND_CORS_ORIGINS=["https://breadgo.vercel.app"]
```

### 프론트엔드

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
BLOB_READ_WRITE_TOKEN=replace-with-vercel-blob-token
```

배포 환경:

```text
NEXT_PUBLIC_API_BASE_URL=https://breadgo-api.onrender.com
BLOB_READ_WRITE_TOKEN=replace-with-vercel-blob-token
```

`BLOB_READ_WRITE_TOKEN`은 Vercel Blob 이미지 업로드에만 필요합니다. 토큰이 없어도 직접 이미지 URL을 입력하는 방식은 사용할 수 있습니다.

## 배포 개요

### Render 백엔드

- Root directory: `backend`
- Install command:

```bash
pip install -r requirements.txt
```

또는:

```bash
pip install -e .
```

- Build command 예시:

```bash
pip install -r requirements.txt && python -m alembic upgrade head
```

- Start command:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Vercel 프론트엔드

- Root directory: `frontend`
- Install command:

```bash
npm install
```

- Build command:

```bash
npm run build
```

- 필수 환경 변수:

```text
NEXT_PUBLIC_API_BASE_URL=https://breadgo-api.onrender.com
BLOB_READ_WRITE_TOKEN=replace-with-vercel-blob-token
```

## 현재 한계

- 실제 결제 PG 연동 없음
- Mock 결제만 지원
- 실제 카드 환불 없음
- Mock 환불 상태만 처리
- 실제 퀵배달/택배 API 연동 없음
- 실제 SMS, 카카오톡, 이메일, push 알림 없음
- 인앱 알림만 지원
- 지도 UI 없음
- 현재 위치 기반 검색은 브라우저 geolocation과 단순 거리 계산 기반
- 운영용 이메일 인증 없음
- 비밀번호 재설정 없음
- 정산 계좌 암호화 미적용
- 실제 송금 없음
- Render 무료 인스턴스 sleep 가능
- 데모 계정은 운영 환경에서 사용하면 안 됨

## 다음 추천 단계

1. Phase 34: README, 릴리즈 문서, 데모 시나리오 최종 정리
2. Phase 35: 모바일 반응형 UX 추가 점검
3. Phase 36: 지도 기반 상품 탐색 UI
4. Phase 37: 실제 PG 결제 연동 설계
5. Phase 38: 실제 알림 채널 연동 설계
6. Phase 39: 운영 모니터링/로깅/알림 구성
7. Phase 40: Flutter 모바일 앱 MVP 시작

## 관련 문서

- [로컬 데모 릴리즈 체크 v0.1.0](docs/release-check-v0.1.0.md)
- [배포 체크리스트 v0.1.0](docs/deployment-checklist-v0.1.0.md)
- [릴리즈 체크 v0.2.0](docs/release-check-v0.2.0.md)
