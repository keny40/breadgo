# BreadGo Phase 35 모바일 반응형 UX 점검

## 목표

Phase 35는 기존 기능을 변경하지 않고, 모바일 화면에서 BreadGo MVP가 깨지지 않도록 공통 레이아웃과 주요 화면의 반응형 UX를 정리하는 단계입니다.

## 점검 범위

### 고객 화면

- `/products`
- `/my-reservations`
- `/my-payments`
- `/notifications`

확인 항목:

- 상품 카드가 작은 화면에서 1열로 자연스럽게 표시되는지
- 지역 선택, 내 위치 찾기, 예약/결제 버튼이 겹치지 않는지
- 픽업 코드가 모바일 화면 폭을 넘지 않는지
- 예약/결제/알림 카드의 메타 정보가 줄바꿈되는지

### 가맹점 화면

- `/merchant`
- `/merchant/stores`
- `/merchant/products`
- `/merchant/orders`
- `/merchant/settlements`
- `/merchant/settlement-account`

확인 항목:

- 상품 등록/수정 폼이 모바일에서 1열로 접히는지
- 상품 이미지, 업로드 영역, 버튼 그룹이 넘치지 않는지
- 주문 카드와 상태 이력 타임라인이 폭을 넘지 않는지
- 정산 카드와 정산 계좌 정보가 줄바꿈되는지

### 관리자 화면

- `/admin`
- `/admin/settlements`

확인 항목:

- 사용자/가맹점/매장/상품/예약/결제 테이블이 모바일에서 가로 스크롤되는지
- 테이블 내부 버튼과 입력 필드가 셀 폭 안에서 잘리는지
- 정산 관리 테이블의 보류 사유, 관리 메모, 상태 버튼이 모바일에서도 조작 가능한지

## 적용한 개선

- NavBar 모바일 메뉴 정리
- 로그인 이메일 영역 줄바꿈 및 말줄임 안정화
- 모바일 NavBar 링크를 2열 또는 자동 그리드로 표시
- 카드, 패널, 요약 카드의 모바일 padding 축소
- 상품/계정/데모/기능 그리드를 모바일 1열로 전환
- 상세 정보 그리드를 모바일 1열로 전환
- 버튼 그룹이 작은 화면에서 겹치지 않도록 폭 처리 개선
- 칩 버튼이 작은 화면에서 2열 형태로 자연스럽게 접히도록 개선
- 픽업 코드 블록이 모바일에서 화면 폭에 맞게 표시되도록 개선
- 테이블 컨테이너에 `overflow-x: auto` 및 모바일 스크롤 안내 문구 적용
- 테이블 내부 버튼/입력 필드가 셀 너비 안에서 조작 가능하도록 개선
- 긴 이메일, 주소, ID, 메모가 카드 폭을 넘지 않도록 줄바꿈 보강

## 변경하지 않은 것

- 백엔드 API
- 데이터베이스 스키마
- 예약/결제/환불/정산 비즈니스 로직
- 기존 route 구조
- 기존 타입 구조

## 검증 명령

```powershell
cd frontend
npm run lint
npm run build
```

## 수동 확인 권장 화면

모바일 폭에서 다음 화면을 확인합니다.

1. `/`
2. `/products`
3. `/my-reservations`
4. `/my-payments`
5. `/notifications`
6. `/merchant`
7. `/merchant/stores`
8. `/merchant/products`
9. `/merchant/orders`
10. `/merchant/settlements`
11. `/merchant/settlement-account`
12. `/admin`
13. `/admin/settlements`

## 남은 UX 과제

- 실제 모바일 기기 Safari/Chrome에서 터치 영역 재점검
- 관리자 테이블을 모바일 전용 카드 리스트로 전환할지 검토
- 지도 UI 도입 시 `/products` 모바일 화면 재설계
- Flutter 앱 시작 전 모바일 웹 UX 기준 확정
