/** 가상 최소 계약. 구현·런타임 검증·DB 원자성을 제공하지 않는다. */
export type Id = string;

declare const transactionScopeBrand: unique symbol;
/** 실제 DB 연결은 인프라 어댑터가 내부적으로 매핑한다. */
export interface TransactionScope {
  readonly [transactionScopeBrand]: true;
}

export interface ActorContext {
  readonly tenantId: Id;
  readonly actorId: Id;
}

export interface CreateReservationInput extends ActorContext {
  readonly memberId: Id;
  readonly classId: Id;
  readonly membershipId: Id;
  readonly idempotencyKey: string;
}

export type ReservationError =
  | 'VALIDATION_FAILED'
  | 'FORBIDDEN'
  | 'NO_CAPACITY'
  | 'MEMBERSHIP_UNAVAILABLE'
  | 'ALREADY_RESERVED'
  | 'IDEMPOTENCY_CONFLICT'
  | 'TEMPORARY_FAILURE';

export type CreateReservationResult =
  | { readonly ok: true; readonly reservationId: Id; readonly status: 'confirmed' }
  | { readonly ok: false; readonly code: ReservationError };

/** 외부 소비자를 위한 유스케이스. 조립부가 내부 포트를 연결한다. */
export interface ReservationUseCases {
  create(input: CreateReservationInput): Promise<CreateReservationResult>;
}

/** 회원권 소유 모듈의 공개 작업. 같은 예약의 중복 차감은 일으키지 않는다. */
export interface MembershipPort {
  consumeSession(
    input: ActorContext & { readonly membershipId: Id; readonly reservationId: Id },
    scope: TransactionScope,
  ): Promise<
    | { readonly ok: true; readonly ledgerId: Id }
    | { readonly ok: false; readonly code: 'FORBIDDEN' | 'MEMBERSHIP_UNAVAILABLE' | 'TEMPORARY_FAILURE' }
  >;
}
