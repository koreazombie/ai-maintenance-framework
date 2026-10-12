# AI Maintenance Framework v0.3.0

- 규모/책임에 맞춘 solo와 modular 프로파일. solo는 PROJECT·CORE·WORKFLOW 지침 세 개만 설치합니다.
- ARCHITECTURE·MODULE_BOUNDARY·DATA_SAFETY·modules/ 등을 솔로에 설치하지 않습니다.
- 진입점 포함 로컬 비공개(local-all)를 4번째 선택으로 명시했습니다.
- 설치 검사기가 placeholder, 버전/프로파일, 원본·기록 파일 해시와 실제 Git 상태를 확인합니다.
- 단일 스크립트와 최소 설정·실행 테스트 예시를 추가했습니다.

버전/검사기/라이선스 등 기술 보조 파일은 최소 지침과 별도로 설치됩니다. 기존 프로젝트는 INSTALL.md와 docs/MIGRATING-0.3.md에 따라 선택한 프로파일로 보존·병합합니다. 자동으로 기존 문서를 삭제하지 않습니다.

설치 검사는 산문의 진실이나 제품의 정상 동작을 보장하지 않습니다. PATCH 우선·실용형 정책과 MIT 라이선스는 유지합니다.
