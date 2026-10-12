# AI Maintenance Framework — 프로젝트 진입점

@.ai/PROJECT.md
@.ai/rules/CORE.md
@.ai/rules/WORKFLOW.md

`.ai/installation.json`의 프로파일·관리 방식을 확인한다. solo는 위 세 문서만 사용한다. modular이면 FRAMEWORK.md·PRIVACY.md와 작업에 필요한 `.ai/rules/`, `.ai/modules/`, 검증 기준을 직접 읽는다. 설치되지 않은 지침에 대한 가져오기를 추가하지 않는다.

관련 실제 코드·테스트·적용되는 하위 지침을 확인한다. 짧은 요청도 저장된 절차에 따라 조사·구현·검증한다. 필요한 업무 결정만 질문한다. Git에서 제외된 `.ai/`도 명시적 경로로 읽는다. 파일 누락은 설치·동기화 필요로 보고한다.

비공개 선택을 보존하고 제외된 파일을 임의로 스테이징·커밋·푸시하지 않는다. 설치 검증: `python3 .ai/tools/validate_installation.py`. 실제 도구의 상위 지침·권한·승인 정책을 따른다.
