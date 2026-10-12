# AI Maintenance Framework — 설치용 안내

버전 0.2.0 · PATCH 우선 · 실용형

설치 결과는 루트 `CLAUDE.md`, `AGENTS.md`와 `.ai/`다. 일반 사용자는 직접 파일을 편집하지 않고 프로젝트 AI에게 적용을 맡긴다. 설치 시 지침을 함께 커밋할지 로컬/별도 비공개로 관리할지 선택한다.

```text
프로젝트/
  CLAUDE.md
  AGENTS.md
  .ai/
    PROJECT.md
    FRAMEWORK.md
    PRIVACY.md
    LICENSE
    rules/
    modules/
    templates/
    verification/
    changes/
    docs/
    examples/
```

[적용 안내](APPLY.md) · [요청문](PROMPTS.md) · [출처](SOURCES.md) · [관리 방식](../PRIVACY.md) · [검증 기준](../verification/CHECKLIST.md)

공통 규칙은 rules에, 프로젝트 정보는 PROJECT.md에, 업무 계약·설명은 modules에, 프레임워크 작업 기록은 changes에 모은다. 실제 제품 코드·실행 테스트·API 스키마는 프로젝트 기존 경로를 유지한다.

지침과 양식은 실행 차단 장치가 아니다. 테스트·CI·DB 권한은 실제 프로젝트와 연결해야 한다. 비공개 방식으로 `.ai/`를 제외하면 다른 환경에 자동 전달되지 않아 재설치 또는 승인된 동기화가 필요하다.
