---
name: fastapi-rest-patterns
description: Design and implement high-performance, production-ready REST APIs using FastAPI, Pydantic v2 schemas, dependency injection, and async database connections.
---

# FastAPI Production REST API Patterns

## Core Design Principles
1. **Pydantic v2 Schemas**: Separate input DTOs (`OrderCreateRequest`), output responses (`OrderResponse`), and internal DB models.
2. **Dependency Injection**: Use `Depends()` for database sessions, authenticated user contexts, and configuration access.
3. **Async / Await Disciplined Execution**: Use `async def` only when awaiting IO (database queries, HTTP calls). Use standard `def` for synchronous, CPU-bound tasks so FastAPI dispatches them to a threadpool.

## Standard Router Architecture

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated

router = APIRouter(prefix="/v1/users", tags=["users"])

# DTO Schemas
class UserCreateRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool

    class Config:
        from_attributes = True

# Route Implementation
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    db: Annotated[any, Depends(get_db_session)],
    current_admin: Annotated[any, Depends(get_current_admin_user)],
):
    existing = await db.users.find_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists."
        )
    user = await db.users.create(payload)
    return user
```

