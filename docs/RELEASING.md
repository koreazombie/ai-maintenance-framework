# 공개 등록과 버전 배포

이 문서는 저장소 관리자를 위한 순서다. 첫 등록 전에는 로컬 후보를 검증하고, 실제 등록·CI 실행·태그 생성을 순서대로 진행한다.

## 첫 등록

1. GitHub의 새 저장소 화면에서 개인 또는 허가된 조직 계정, 이름 `ai-maintenance-framework`, 공개 범위를 선택한다.
2. 이미 준비한 README·LICENSE·.gitignore를 올릴 것이므로 서버의 자동 생성 옵션은 비워 둔다.
3. 현재 배포 폴더의 **내용**이 저장소 루트가 되도록 등록한다. ZIP 파일만 저장소에 올리는 방식은 사용 안내와 지침 경로를 제공하지 못한다.
4. 숨김 `.ai/`와 `.github/`, `.gitignore`, `.gitattributes`가 포함됐는지 확인한다. 특히 Mac 파일 선택에서 숨김 파일 누락을 점검한다. 파일이 완전하게 포함되는 Git 업로드를 우선 사용한다.
5. GitHub Actions의 Package checks 결과를 확인한다. 이 검사는 문서·구성 검사이며 실제 제품 테스트가 아니다.
6. README·INSTALL.md·LICENSE와 설치용 폴더가 올바르게 표시되는지 확인한다.
7. 승인된 공개 커밋을 기준으로 `v0.3.0` 태그와 릴리스를 만든다. 로컬 검증과 GitHub 검증의 범위를 릴리스 설명에 적는다.

웹 화면에서 첫 등록을 진행하는 방법은 [GitHub 공식 저장소 생성 안내](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository), 파일 등록은 [공식 파일 추가 안내](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)를 참고한다. 저장소 생성·업로드·태그 생성은 실제 공개 작업 범위를 확인한 뒤 수행한다.

## 공개 상태 기록

`release.json`의 publication_status는 로컬 후보 단계에서 `local-candidate`다. 공개를 실행할 때 `published`로 변경하고 실제 저장소 주소와 확인한 커밋을 별도 릴리스 기록에 남긴다. CHANGELOG의 후보 표시도 공개 상태에 맞게 바꾼다. 저장소가 만들어지기 전에 존재하는 것으로 안내하지 않는다.

## 다음 버전

- 규칙의 의미·경로·설치 절차 변경은 기존 적용 프로젝트에 미치는 영향을 설명한다.
- VERSION, release.json과 CHANGELOG를 함께 갱신한다.
- 검사 두 종류를 실행한 뒤 검토된 커밋에 태그를 만든다. 이미 배포한 태그를 다른 커밋으로 이동하지 않는다.
- 배포 ZIP의 원본 커밋과 SHA-256을 기록한다.
- 적용 프로젝트에는 최신 버전을 자동 덮어쓰지 않고 비교·병합하도록 안내한다.

## 첫 릴리스 설명 양식

```text
AI Maintenance Framework v0.3.0

기존 프로젝트의 AI 유지보수·리팩토링을 위한 한국어 작업 지침입니다.
Claude Code/Codex 진입점, 공통 규칙, AI 적용 절차,
프로젝트·모듈·계약 양식, 검증 체크리스트와 가상 예시를 제공합니다.
기본 정책은 PATCH 우선과 실용형 절차이며 MIT 라이선스로 배포합니다.

실행한 검사: <실제 결과>
미실행: <실제 제품 적용·도구 세션 등>
시작 방법: README의 적용 요청문을 프로젝트 AI에게 전달하세요.
```

배포 전 profiles.json·VERSION·설치 검사기 버전을 일치시키고, 검토한 원본으로 generate_catalog를 갱신한 뒤 --check를 실행한다. 사용자 프로젝트에는 선택한 프로파일 파일만 설치한다.
