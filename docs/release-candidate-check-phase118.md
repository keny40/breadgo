# Phase 118 Release Candidate Check

## 목적

v0.1.2 정식 릴리스 후보 상태를 최종 점검하고, Release Note 초안과 Release 생성 전 남은 작업을 정리했다.

이번 Phase는 Release Candidate 준비 문서화 중심이며 기능 코드, DB schema, migration은 변경하지 않는다.

## 현재 상태

- 현재 브랜치: `main`
- 로컬/원격 상태: `main...origin/main [ahead 10]`
- 공식 공개 데모 Release 기준: `v0.1.1-demo-ready`
- `v0.1.2-demo-published`: GitHub Release가 없는 문서성/임시 tag로 유지
- v0.1.2: Release Candidate 준비 단계
- 새 tag 생성 없음
- 새 GitHub Release 생성 없음
- 기존 tag 삭제/이동 없음

## 최근 커밋 상태

`git log --oneline -8` 기준:

```text
4fc3699 Prepare v0.1.2 release checklist
01ec322 Polish demo UX and document v0.1.2 scope
08845dc Add operations stabilization package
99e6624 Expand smoke test Pro Operations coverage
d266c80 Expand smoke test Pro Operations coverage
a8b5f6b Document operations stabilization review
4cb0da2 Document v0.1.1 release completion
665e283 Document release tag policy
```

## 작성 파일

- `docs/release-note-v0.1.2.md`
- `docs/release-candidate-check-phase118.md`

## README 정리

README에 아래 링크를 추가했다.

- `docs/release-note-v0.1.2.md`
- `docs/release-candidate-check-phase118.md`

## v0.1.2 Release Note 요약

Release Note 초안에는 아래를 포함했다.

- v0.1.2 목적
- v0.1.1 대비 변경 요약
- 운영 안정화 개선
- Pro Operations smoke test 보강
- Demo UX 개선
- Environment / troubleshooting 문서 정리
- Mock/실제 연동 경계 명확화
- 포함 범위
- 제외 범위
- 검증 결과
- Release 생성 전 주의사항

## 남은 작업

v0.1.2 실제 Release 생성 전 아래가 남아 있다.

1. Phase 113~118 문서/안내 변경을 commit한다.
2. `origin/main`에 push하여 현재 `ahead 10` 상태를 해소한다.
3. 원격 README에 v0.1.2 준비 문서 링크가 반영되는지 확인한다.
4. v0.1.2 실제 tag 이름을 결정한다.
   - 후보: `v0.1.2`
   - 또는 안정화 성격을 드러내려면 `v0.1.2-demo-stabilization`
5. GitHub Release title과 body source를 확정한다.
6. `v0.1.2-demo-published`가 공식 Release가 아니라는 설명을 유지한다.
7. release 생성 직전 전체 검증을 재실행한다.

## 검증 결과

- `git status`: PASS
- `git branch --show-current`: PASS
  - `main`
- `git status -sb`: PASS
  - `main...origin/main [ahead 10]`
- `git log --oneline -8`: PASS
- `git tag --list`: PASS
  - `v0.1.1-demo-ready`, `v0.1.2-demo-published` 존재 확인
- `python -m compileall app scripts`: PASS
- `python scripts/seed_demo.py`: PASS
- `python scripts/smoke_test.py`: PASS
- `python scripts/run_weekly_report_batch.py`: PASS
  - 동일 기간 완료된 SCHEDULED batch run이 있어 중복 실행 방지 로직으로 `SKIPPED` 처리됨.
- `python scripts/run_pro_health_alert_check.py`: PASS
  - `overall_status=WARNING`, 기존 OPEN/ACKNOWLEDGED alert 중복으로 `generated_count=0`, `skipped_count=2`.
- `npm run lint`: PASS
- `npm run build`: PASS

## 기능 코드 / DB / migration 변경 여부

- 기능 코드 변경 없음
- DB schema 변경 없음
- migration 추가 없음
- 실제 외부 API 연동 없음
- 실제 결제/알림 발송 없음

## Suggested commit message

`Draft v0.1.2 release candidate notes`
