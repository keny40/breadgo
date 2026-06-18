# BreadGo v0.3.0 배포 환경 최종 점검 체크리스트

## 목적

이 문서는 BreadGo v0.3.0 데모 릴리즈를 Vercel, Render, Neon 기준으로 점검하기 위한 체크리스트입니다.
실제 secret 값은 문서에 기록하지 않고, 배포 플랫폼의 환경 변수 관리 기능에만 설정합니다.

## 배포 URL

- Frontend: [https://breadgo.vercel.app](https://breadgo.vercel.app)
- Backend: [https://breadgo-api.onrender.com](https://breadgo-api.onrender.com)
- Health: [https://breadgo-api.onrender.com/health](https://breadgo-api.onrender.com/health)
- Swagger: [https://breadgo-api.onrender.com/docs](https://breadgo-api.onrender.com/docs)
- Demo: [https://breadgo.vercel.app/demo](https://breadgo.vercel.app/demo)

## Vercel 프론트엔드 점검 항목

- GitHub repository가 올바르게 연결되어 있는지 확인
- Vercel project root directory가 `frontend`인지 확인
- Install command가 `npm install`인지 확인
- Build command가 `npm run build`인지 확인
- Production deployment URL이 `https://breadgo.vercel.app`인지 확인
- `NEXT_PUBLIC_API_BASE_URL`이 Render 백엔드 URL을 바라보는지 확인
- `BLOB_READ_WRITE_TOKEN`이 설정되어 있는지 확인
- `/`, `/demo`, `/products`, `/login`, `/admin`, `/admin/ops` 접근 확인
- 브라우저 콘솔에 CORS 또는 API base URL 오류가 없는지 확인

## Render 백엔드 점검 항목

- Render Web Service root directory가 `backend`인지 확인
- Python version이 `3.12.8` 또는 프로젝트 지원 버전인지 확인
- Install command가 `pip install -r requirements.txt` 또는 `pip install -e .`인지 확인
- Start command가 다음 형식인지 확인

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

- `python -m alembic upgrade head`가 배포 DB에 적용되었는지 확인
- `seed_demo.py`는 운영 자동 실행에 넣지 않았는지 확인
- 데모 환경에서만 필요한 경우 수동으로 `python scripts/seed_demo.py` 실행
- `/health`가 `{"status":"ok"}`를 반환하는지 확인
- `/docs`가 열리는지 확인
- `/api/v1/ops/status`는 ADMIN 인증이 필요함을 확인

## Neon DB 점검 항목

- Render `DATABASE_URL`이 Neon PostgreSQL connection string을 사용하고 있는지 확인
- DB connection string이 `postgresql+psycopg://...` 형식인지 확인
- Alembic migration이 head까지 적용되었는지 확인
- 데모 계정과 데모 상품 데이터가 필요한 환경에 seed 되었는지 확인
- 운영 DB에는 불필요한 테스트 데이터가 누적되지 않도록 주의
- 백업/복구 정책은 아직 별도 운영 과제로 남아 있음

## 필수 환경 변수

### Render Backend

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
JWT_SECRET_KEY=replace-with-secure-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["https://breadgo.vercel.app"]
PYTHON_VERSION=3.12.8
ENVIRONMENT=production
LOG_LEVEL=INFO
```

선택 또는 향후 연동용:

```text
SENTRY_DSN=
SLACK_WEBHOOK_URL=
```

### Vercel Frontend

```text
NEXT_PUBLIC_API_BASE_URL=https://breadgo-api.onrender.com
BLOB_READ_WRITE_TOKEN=replace-with-vercel-blob-token
```

`BLOB_READ_WRITE_TOKEN`은 상품 이미지 파일 업로드에 필요합니다.
토큰이 없어도 이미지 URL 직접 입력 방식은 사용할 수 있습니다.

### Flutter Mobile

로컬 Android emulator:

```text
BREADGO_API_BASE_URL=http://10.0.2.2:8000
```

Render 백엔드:

```text
BREADGO_API_BASE_URL=https://breadgo-api.onrender.com
```

Flutter는 환경 변수를 OS env로 읽는 것이 아니라 실행 시 `--dart-define`으로 전달합니다.

```powershell
flutter run --dart-define=BREADGO_API_BASE_URL=https://breadgo-api.onrender.com
```

## 데모 계정 확인 항목

```text
customer@breadgo.test / 12345678
merchant@breadgo.test / 12345678
admin@breadgo.test / 12345678
```

확인할 것:

- 고객 로그인 가능
- 가맹점 로그인 가능
- 관리자 로그인 가능
- 관리자 계정의 role이 `ADMIN`인지 확인
- 가맹점 계정에 merchant profile이 있는지 확인
- 데모 상품의 재고가 남아 있는지 확인

## Render Free Instance Sleep 주의사항

- 무료 인스턴스는 일정 시간 요청이 없으면 sleep 상태가 됩니다.
- 첫 요청은 수십 초 이상 지연될 수 있습니다.
- 데모 시작 전에 다음 URL을 먼저 열어 cold start를 깨우는 것을 권장합니다.

```text
https://breadgo-api.onrender.com/health
```

## 배포 후 확인할 URL 목록

- [https://breadgo.vercel.app](https://breadgo.vercel.app)
- [https://breadgo.vercel.app/demo](https://breadgo.vercel.app/demo)
- [https://breadgo.vercel.app/products](https://breadgo.vercel.app/products)
- [https://breadgo.vercel.app/login](https://breadgo.vercel.app/login)
- [https://breadgo.vercel.app/my-reservations](https://breadgo.vercel.app/my-reservations)
- [https://breadgo.vercel.app/merchant](https://breadgo.vercel.app/merchant)
- [https://breadgo.vercel.app/merchant/orders](https://breadgo.vercel.app/merchant/orders)
- [https://breadgo.vercel.app/admin](https://breadgo.vercel.app/admin)
- [https://breadgo.vercel.app/admin/settlements](https://breadgo.vercel.app/admin/settlements)
- [https://breadgo.vercel.app/admin/ops](https://breadgo.vercel.app/admin/ops)
- [https://breadgo-api.onrender.com/health](https://breadgo-api.onrender.com/health)
- [https://breadgo-api.onrender.com/docs](https://breadgo-api.onrender.com/docs)

## 장애 발생 시 1차 확인 순서

1. Render `/health` 확인
2. Render service log 확인
3. Neon DB connection 상태 확인
4. Render `DATABASE_URL` 확인
5. Alembic migration 적용 여부 확인
6. Vercel `NEXT_PUBLIC_API_BASE_URL` 확인
7. Render `BACKEND_CORS_ORIGINS`에 Vercel URL 포함 여부 확인
8. 브라우저 개발자도구 Network 탭에서 실패 API와 status code 확인
9. 관리자 계정으로 `/admin/ops` 확인
10. 데모 데이터가 없으면 demo seed 실행 여부 확인

## 운영 전환 전 주의

- 실제 PG 결제는 아직 연결되어 있지 않습니다.
- 실제 환불은 아직 발생하지 않습니다.
- 실제 배송/퀵배달/택배 API는 연결되어 있지 않습니다.
- 실제 Push/SMS/이메일/카카오 알림톡은 연결되어 있지 않습니다.
- 데모 계정은 운영 서비스에 사용하면 안 됩니다.
