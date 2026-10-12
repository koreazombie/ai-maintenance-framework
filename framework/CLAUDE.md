# AI Maintenance Framework — Claude Code 진입점

@.ai/PRIVACY.md
@.ai/FRAMEWORK.md
@.ai/rules/CORE.md
@.ai/PROJECT.md
@.ai/rules/WORKFLOW.md

추가 문서는 필요할 때 직접 읽는다. 변경 대상의 `.ai/modules/` 설명·계약과 실제 코드·테스트·적용되는 하위 지침도 확인한다.

- 기능·구조·모듈 간 호출: `.ai/rules/ARCHITECTURE.md`, `.ai/rules/MODULE_BOUNDARY.md`, `.ai/rules/CONTRACT_FIRST.md`
- 영속 상태·DB: `.ai/rules/DATA_SAFETY.md`
- 검증: `.ai/rules/VERIFICATION.md`, `.ai/verification/CHECKLIST.md`
- 내부 교체: `.ai/rules/REGENERATION.md` 및 관련 문서

`.ai/`가 없거나 누락되면 설치/동기화 필요를 알리고, 미확인 지침·설정을 지어내지 않는다. Git에서 제외된 `.ai/`도 명시적 경로로 직접 읽는다.

설명·계약·양식·검증 기준·작업 기록은 `.ai/`에 모은다. 실제 제품 코드·실행 테스트·API 스키마는 프로젝트 경로를 유지한다. 지침 관리 선택을 보존하고 로컬 비공개 파일을 임의로 스테이징·커밋·푸시하지 않는다.

PATCH 우선/실용형 정책을 적용한다. 실제 도구의 상위 지침·권한·승인 정책을 따른다. 이 파일은 권한을 확대하지 않는다.
