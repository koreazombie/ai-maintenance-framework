# 프로젝트 설정 — 스크립트/솔로 예시

- 프레임워크 버전: 0.3.0
- 프로파일: solo
- 지침 관리 방식: local-all
- 목적: UTF-8 텍스트 파일에서 공백이 아닌 줄의 수를 출력한다.
- 언어·런타임: Python 3.9 이상, 표준 라이브러리만 사용.
- 진입 파일: count_lines.py
- 실행 명령: python3 count_lines.py sample.txt
- 검증 명령: python3 -m unittest discover -v
- 보존할 동작: 공백 줄 제외, 빈 입력은 0, 입력 파일 내용 보존.
