# AI Maintenance Framework — 저장소 관리 지침

이 저장소는 제품 앱이 아니라 재사용할 AI 유지보수 지침을 배포한다.

- `framework/`는 사용자 프로젝트에 적용하는 양식이다. 미설정 값은 의도적이다.
- 루트 README와 INSTALL.md는 쉬운 사용 안내와 AI 적용 절차다.
- `framework/.ai/rules/CORE.md` 등 설계 문서를 읽고 관련 규칙을 일관되게 유지한다.
- 이 저장소를 특정 서비스로 오인해 템플릿 설정을 채우거나 제품 코드·DB를 생성하지 않는다.
- 개인 대화 원문·비밀·사용자의 로컬 경로를 공개 파일에 포함하지 않는다.
- 파일 이동 시 실제 링크·Claude 가져오기·진입점 참조를 수정한다.
- 검사: `python3 scripts/check_package.py`와 `python3 -m unittest discover -s tests -v`.
- 설치 양식과 배포 저장소 관리 지침을 혼합하지 않는다.
- 문서/양식 수정의 검증과 실제 제품의 검증을 구분해 보고한다.
- 라이선스·핵심 기본 정책 변경은 사용자의 허가 범위를 확인한다.
