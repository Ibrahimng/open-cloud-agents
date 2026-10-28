#!/usr/bin/env python3
"""
Application Server Layer: Secure LLM Router
Framework Mapping: OWASP Top 10 for LLM Applications (LLM01 & LLM02 Hardened)
Purpose: Enforces structural input sanitization and secure role array isolation.
"""

from fastapi import FastAPI, Request, HTTPException
from src.middleware.guards import build_secure_prompt_payload

app = FastAPI()

@app.post("/v1/chat/completions")
async def secure_chat_handler(request: Request):
    body = await request.json()
    user_input = body.get("user_message", "")

    try:
        # Enforce sanitization and structural roles isolation (Mitigates OWASP LLM01)
        secure_messages_payload = build_secure_prompt_payload(user_input)
    except ValueError as e:
        # Gracefully drop execution before passing inputs to the LLM engine
        raise HTTPException(status_code=400, detail=str(e))

    # secure_messages_payload is now clean and structurally isolated
    # Pass secure_messages_payload straight to inference API (Vertex AI, Bedrock, etc.)
    return {"status": "Securely Processed", "payload": secure_messages_payload}
