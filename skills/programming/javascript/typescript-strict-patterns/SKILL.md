---
name: typescript-strict-patterns
description: Implement strictly typed TypeScript designs utilizing discriminated unions, exhaustiveness checks, branded types, and zero-runtime-cost schemas.
---

# TypeScript Strict Type Patterns

## 1. Discriminated Unions & Exhaustiveness Checking
Model state machines and polymorphic payloads with an explicit discriminator field (e.g. `status` or `type`).
Enforce compile-time exhaustiveness using the `never` type:

```typescript
type PaymentState =
  | { status: 'idle' }
  | { status: 'processing'; transactionId: string }
  | { status: 'succeeded'; receiptUrl: string }
  | { status: 'failed'; errorCode: string };

function assertUnreachable(x: never): never {
  throw new Error(`Unhandled union variant: ${JSON.stringify(x)}`);
}

export function renderPaymentBanner(state: PaymentState): string {
  switch (state.status) {
    case 'idle':
      return 'Ready to pay';
    case 'processing':
      return `Processing transaction ${state.transactionId}...`;
    case 'succeeded':
      return `Payment confirmed! Receipt: ${state.receiptUrl}`;
    case 'failed':
      return `Payment failed: ${state.errorCode}`;
    default:
      return assertUnreachable(state); // Compile error if a new state is added but not handled
  }
}
```

## 2. Branded Types for Safe Identifiers
Prevent mixing up primitive strings (e.g. accidentally passing an `AccountId` where an `OrderId` was expected):

```typescript
type Brand<K, T> = K & { readonly __brand: T };

export type OrderId = Brand<string, 'OrderId'>;
export type UserId = Brand<string, 'UserId'>;

export function makeOrderId(id: string): OrderId {
  return id as OrderId;
}
```

