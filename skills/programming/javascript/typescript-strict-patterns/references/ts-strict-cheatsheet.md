# TypeScript Strict Mode Cheat Sheet

## 1. Type Guards & Narrowing
```typescript
interface Cat { kind: 'cat'; meow(): void; }
interface Dog { kind: 'dog'; bark(): void; }
type Pet = Cat | Dog;

function isCat(pet: Pet): pet is Cat {
  return pet.kind === 'cat';
}
```

## 2. Template Literal Types
```typescript
type HTTPMethod = 'GET' | 'POST' | 'DELETE';
type APIPath = `/v1/${string}`;
type Endpoint = `${HTTPMethod} ${APIPath}`;

const validEndpoint: Endpoint = 'GET /v1/users'; // Valid
```

## 3. Recommended `tsconfig.json` Strict Flags
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

