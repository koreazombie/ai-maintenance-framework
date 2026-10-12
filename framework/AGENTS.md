# AI Maintenance Framework — 프로젝트 진입점

프로젝트 루트에서 `.ai/PROJECT.md`, `.ai/rules/CORE.md`, `.ai/rules/WORKFLOW.md`를 직접 읽는다. `.ai/installation.json`의 프로파일·관리 방식을 확인한다. 파일이 없으면 재설치·동기화 필요를 알리고 내용을 지어내지 않는다. Git에서 제외된 파일도 명시적 경로로 읽는다.

solo는 위 세 문서만 사용한다. modular이면 `.ai/FRAMEWORK.md`, `.ai/PRIVACY.md`와 작업에 필요한 `.ai/rules/` 문서, `.ai/modules/` 계약·검증 기준을 추가로 읽는다. 설치되지 않은 모듈 규칙을 만들거나 '해당없음' 문서를 생성하지 않는다.

관련 실제 코드·테스트·적용되는 하위 지침을 확인한다. 짧은 요청도 저장된 절차에 따라 조사·구현·검증한다. 확인이 필요한 업무 결정만 질문한다. 비공개 선택을 보존하고 제외된 파일을 임의로 스테이징·커밋·푸시하지 않는다.

설치 검증: `python3 .ai/tools/validate_installation.py`. 이 검사는 설치 상태이며 제품 동작 검증은 별도로 수행한다. 실제 도구의 상위 지침·권한·승인 정책을 따른다.
