# FastAPI Production Architecture Specification

## 1. Lifespan Events (Startup / Shutdown)
Use modern `lifespan` context managers instead of deprecated `@app.on_event`:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB connection pool, warm up caches
    db_pool = await init_db_pool()
    yield {"db_pool": db_pool}
    # Shutdown: Gracefully close active connections
    await db_pool.close()

app = FastAPI(lifespan=lifespan)
```

## 2. Standard Error Envelope
All error responses should conform to RFC 7807 (Problem Details):
```json
{
  "type": "https://api.domain.com/errors/resource-not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "User with ID 'usr_123' does not exist.",
  "instance": "/v1/users/usr_123"
}
```
