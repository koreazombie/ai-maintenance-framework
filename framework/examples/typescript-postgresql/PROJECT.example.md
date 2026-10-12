# 가상 프로젝트 설정 — 실제 적용 전에 수정

- 목적: 회원권을 사용하는 수업 예약 서비스.
- 스택: TypeScript / PostgreSQL. 프레임워크·런타임·ORM·패키지 관리자·버전은 실제 저장소에서 확인.
- 기본 정책: PATCH 우선 / 실용형.
- 명령: 설치·빌드·타입·린트·테스트·마이그레이션 모두 미확인. 실제 package scripts에서 확인.
- 테스트 환경: 운영과 분리된 PostgreSQL DB와 합성 fixture. 실제 격리 방법은 미설정.

| 모듈 | 책임 | 공개 경로(예시) | 소유 테이블(가정) |
|---|---|---|---|
| reservations | 예약·정원·대기 | `src/modules/reservations/public/` | reservations, class_capacity |
| memberships | 횟수·차감·복구 | `src/modules/memberships/public/` | memberships, membership_ledger |
| payments | 결제·환불 | `src/modules/payments/public/` | payments, refunds |

- 원자성: 예약 생성 + 회원권 차감은 같은 트랜잭션. 실제 인프라 연결은 미구현.
- 시간: 저장·전달은 UTC 시각, 사용자 표시 시간대는 프로젝트에서 확인. 수업 날짜 해석은 별도 명세 필요.
- 권한: actor가 같은 tenant에서 해당 회원을 예약할 수 있어야 함. 세부 역할은 미확인.
- 경계 예외: 없음으로 가정. 실제 코드에서 조사 필요.
- 성능·복구·운영 적용 허가·CI 완료 기준: 미설정.

이 파일을 그대로 실제 설정으로 복사해서 확인 완료로 표시하지 않는다.
