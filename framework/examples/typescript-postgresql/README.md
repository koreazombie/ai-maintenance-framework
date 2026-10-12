# TypeScript/PostgreSQL 적용 예시

운동 수업 예약 서비스의 **가상 설계 예시**다. 실제 제품 저장소·스키마·업무 규칙을 확인한 결과가 아니다. 제품 구현·DB 마이그레이션·실행 테스트는 포함하지 않는다. `contracts.ts`는 최소 타입 양식이며, 테스트 시나리오는 실제 프로젝트의 테스트 도구에 구현해야 한다.

## 권장 출발 구조

```text
src/
  composition/reservation-transaction.ts
  modules/
    reservations/{public,domain,application,infrastructure}/
    memberships/{public,domain,application,infrastructure}/
    payments/{public,domain,application,infrastructure}/
contracts/reservations.md
```

- reservations: 예약 생성·취소·정원·대기자 상태를 책임진다.
- memberships: 사용 가능 횟수·유효기간·차감·복구 원장을 책임진다.
- payments: 승인·환불·결제 제공자 부작용을 책임진다.
- composition: 원자성이 필요한 유스케이스의 조립과 트랜잭션 범위를 조정한다.

예시 `contracts.ts`를 사용하려면 모듈별 공개 디렉터리에 타입을 나누고 조립부에서 연결한다. 폴더 이름은 프로젝트 구조에 맞춘다.

## 예약 + 회원권 차감

가정: 하나의 PostgreSQL 트랜잭션으로 예약 저장과 차감을 처리할 수 있으며, 예약 완료는 둘 다 성공한 상태다. 예약 모듈이 회원권 테이블을 직접 UPDATE하지 않는다. 조정자가 트랜잭션을 시작하고 예약·회원권의 공개 작업에 같은 작업 범위를 전달한다. 각 어댑터가 내부적으로 같은 DB 연결을 사용한다.

`TransactionScope`는 ORM 객체를 공개 계약으로 노출하지 않는 불투명 토큰이다. 이 타입만으로 트랜잭션이 보장되지는 않는다. 어댑터가 토큰을 실제 트랜잭션에 연결하는 구현과 PostgreSQL 통합 검증이 필요하다. 모듈 작업은 전달된 트랜잭션을 임의로 commit하지 않는다.

## DB 구현 시 확인할 내용

- 예약과 회원권 원장에 테넌트 식별을 포함한다. 서버 권한 확인과 데이터 제약을 함께 검토한다.
- 사용 가능 횟수는 0 아래로 내려가지 않도록 제약과 조건부 갱신 또는 적절한 잠금으로 보호한다.
- 회원권 차감 원장은 동일 예약의 중복 차감을 막는 UNIQUE 키를 갖는다. 예: `(tenant_id, reservation_id, operation_kind)`.
- 성공 요청의 멱등키는 테넌트·작업·요청 내용과 연결한다. 키 충돌, 다른 payload, 동시 중복, 보관 기간을 계약으로 정한다.
- 같은 마지막 좌석이나 잔여 1회를 두 요청이 경쟁하는 경우 한 요청만 성공하도록 실제 DB에서 검증한다.
- 트랜잭션 내 DB 처리 후 결제 API를 호출하는 것만으로 외부 결제 원자성이 생기지 않는다. 결제가 추가되면 별도 계약·실패 상태·보상/재시도를 설계한다.
- 이벤트를 발행하면 DB 기록과 outbox를 같은 트랜잭션에 저장하고 소비자는 중복 전달을 처리한다.

## 예시 사용 순서

[프로젝트 설정 예시](PROJECT.example.md) → [예약 계약](reservations.contract.md) → [타입 양식](contracts.ts) → [독립 검증 시나리오](verification-scenarios.md)를 실제 프로젝트에 맞게 수정한다. 타입과 시나리오가 있다는 이유만으로 예약 원자성이나 재생성 준비가 검증됐다고 보고하지 않는다.
