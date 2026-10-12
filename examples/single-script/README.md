# 단일 스크립트 예시 — 솔로 프로파일

작은 텍스트 줄 수 계산 도구다. DB·모듈 계약·운영 배포가 없으므로 그런 지침을 설치하지 않는다. 이 예시는 공개 배포 저장소의 참고 자료이며 사용자 프로젝트에 자동 복사하지 않는다.

이 폴더에서 실행:

```sh
python3 count_lines.py sample.txt
python3 -m unittest discover -v
```

출력은 2다. 테스트는 공백 줄 제외·빈 입력·입력 파일 보존을 확인한다.

[최소 프로젝트 설정](PROJECT.example.md)을 참고한다. 실제 설치 지침은 원본 INSTALL.md를 따른다.

```text
작은 프로젝트/
  count_lines.py
  test_count_lines.py
  sample.txt
  AGENTS.md
  CLAUDE.md
  .ai/
    PROJECT.md
    rules/CORE.md
    rules/WORKFLOW.md
    installation.json
    release-catalog.json
    tools/validate_installation.py
    LICENSE
```

지침 Markdown은 PROJECT·CORE·WORKFLOW 세 개뿐이다. metadata/검사기/라이선스는 기술 보조 파일이다. `.ai/modules/`, templates/, verification/, docs/, DB·아키텍처 규칙은 설치하지 않는다.

예시는 local-all을 선택했다. 실제 프로젝트에서 다른 관리 방식도 선택할 수 있다. local-all이면 `.ai/`와 두 진입점의 ignore·추적 상태를 확인한다. 설치 검사는 입력 파일 계산 기능의 테스트를 대체하지 않는다.
