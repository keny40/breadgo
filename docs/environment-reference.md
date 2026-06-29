# Environment Reference

## 목적

BreadGo MVP / BreadGo Pro를 로컬 또는 데모 배포 환경에서 실행할 때 확인해야 할 환경변수와 민감정보 원칙을 정리한다.

이 문서는 운영 안정화용 reference다. 실제 외부 PG, 배송, POS, 이메일, 카카오, Push, Slack, Discord, Webhook 연동을 추가하지 않는다.

## 관련 파일

- Root example: `.env.example`
- Backend local env: `backend/.env`
- Backend example: `backend/.env.example`
- Frontend local env: `frontend/.env.local`
- Frontend example: `frontend/.env.example`

실제 secret 값은 git에 commit하지 않는다.

## Backend variables

| 변수 | 필수 | 용도 | 예시 / 비고 |
| --- | --- | --- | --- |
| `DATABASE_URL` | 필수 | SQLAlchemy / Alembic PostgreSQL 연결 | `postgresql+psycopg://user:pass@host:5432/db` |
| `JWT_SECRET_KEY` | 필수 | access token 서명 | 32자 이상 난수 권장 |
| `JWT_ALGORITHM` | 필수 | JWT 알고리즘 | 기본 `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 필수 | access token 만료 시간 | 로컬 기본 `30` |
| `BACKEND_CORS_ORIGINS` | 필수 | 허용 frontend origin | 로컬 `http://localhost:3000` 포함 |

Root `.env.example`에는 로컬 PostgreSQL helper 변수도 포함한다.

| 변수 | 용도 |
| --- | --- |
| `POSTGRES_HOST` | 로컬 DB host |
| `POSTGRES_PORT` | 로컬 DB port |
| `POSTGRES_DB` | 로컬 DB 이름 |
| `POSTGRES_USER` | 로컬 DB 사용자 |
| `POSTGRES_PASSWORD` | 로컬 DB 비밀번호 |

## Frontend variables

| 변수 | 필수 | 용도 | 예시 / 비고 |
| --- | --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | 필수 | Next.js frontend가 호출할 backend API base URL | 로컬 `http://127.0.0.1:8000` 또는 Render URL |
| `BLOB_READ_WRITE_TOKEN` | 선택 | Vercel Blob 상품 이미지 업로드 | 실제 token은 git에 저장 금지 |

## Mock / external integration policy

v0.1.1 demo-ready 기준 아래 기능은 실제 외부 연동이 아니다.

- PG 결제
- 카드 환불
- 퀵배송/택배 provider
- POS API
- 이메일 발송
- 카카오 발송
- Push 발송
- Slack / Discord / Webhook 발송
- Health Alert 외부 알림

따라서 아래 정보는 현재 env 파일에 넣지 않는다.

- 실제 PG API key
- 실제 배송 provider token
- 실제 POS credential
- 수신자 이메일/전화번호 export
- Slack/Discord/Webhook URL
- 외부 알림 provider token

## 로컬 실행 확인

Backend:

```powershell
cd backend
python -m alembic upgrade head
python scripts/seed_demo.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
npm run dev
```

Smoke test:

```powershell
cd backend
python scripts/smoke_test.py
```

## 환경변수 누락 의심 시 확인 순서

1. backend가 DB에 연결되는지 `python -m alembic upgrade head`로 확인한다.
2. backend server가 `/health`에 응답하는지 확인한다.
3. frontend `NEXT_PUBLIC_API_BASE_URL`이 실행 중인 backend를 가리키는지 확인한다.
4. 이미지 업로드만 실패하면 `BLOB_READ_WRITE_TOKEN` 설정 여부를 확인한다.
5. 실제 외부 발송 token을 요구하는 오류가 있다면, v0.1.1 기준으로는 예상 동작이 아니므로 해당 코드를 점검한다.

## 배포 환경 확인 위치

- Render backend environment variables
- Vercel frontend environment variables
- Neon / PostgreSQL connection settings
- GitHub repository secrets는 현재 v0.1.1 demo-ready 운영 흐름의 필수 조건이 아니다.

## 주의사항

- 실제 secret은 README, release note, troubleshooting guide, audit log에 적지 않는다.
- 이메일, 전화번호, 주소, 외부 발송 token은 audit/delivery/health alert 로그에 저장하지 않는다.
- 실제 외부 연동이 필요해지면 별도 Phase에서 adapter, consent, secret storage, rollback 정책을 먼저 정의한다.
