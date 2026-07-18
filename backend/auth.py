"""Small dependency-free API-key/JWT security layer for production mode."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Optional

from fastapi import Header, HTTPException, Request

from backend.config import APP_API_KEYS, APP_AUTH_REQUIRED, APP_JWT_SECRET, APP_JWT_TTL_SECONDS


_RUNTIME_JWT_SECRET = APP_JWT_SECRET or secrets.token_urlsafe(48)


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_access_token(subject: str, claims: Optional[dict] = None) -> str:
    if APP_AUTH_REQUIRED and not APP_JWT_SECRET:
        raise HTTPException(status_code=503, detail="JWT secret is not configured")
    header = _encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    issued_at = int(time.time())
    token_claims = {
        "sub": subject,
        "exp": issued_at + APP_JWT_TTL_SECONDS,
        "iat": issued_at,
        "jti": secrets.token_urlsafe(12),
        "type": "access",
    }
    token_claims.update(claims or {})
    payload = _encode(json.dumps(token_claims, separators=(",", ":")).encode())
    signature = _encode(hmac.new(_RUNTIME_JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"


def verify_access_token(token: str) -> dict:
    try:
        header, payload, signature = token.split(".")
        expected = _encode(hmac.new(_RUNTIME_JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("signature")
        claims = json.loads(_decode(payload))
        if int(claims.get("exp", 0)) < int(time.time()):
            raise ValueError("expired")
        return claims
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc


def exchange_api_key(api_key: Optional[str]) -> str:
    if not api_key or api_key not in APP_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return create_access_token("vgap-api-client")


def require_auth(request: Request, x_api_key: Optional[str] = Header(default=None)) -> dict:
    if not APP_AUTH_REQUIRED:
        return {"sub": "demo-mode"}
    if x_api_key and x_api_key in APP_API_KEYS:
        return {"sub": "api-key-client"}
    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        claims = verify_access_token(authorization[7:].strip())
        requested_student = request.path_params.get("student_id")
        if claims.get("role") == "student" and requested_student and claims.get("student_id") != requested_student:
            raise HTTPException(status_code=403, detail="You cannot access another student's data")
        return claims
    raise HTTPException(status_code=401, detail="Authentication required")


def require_student_session(request: Request) -> dict:
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Student authentication required")
    claims = verify_access_token(authorization[7:].strip())
    if claims.get("type") != "access" or claims.get("role") != "student" or not claims.get("student_id"):
        raise HTTPException(status_code=403, detail="Student account required")
    return claims


def require_staff_auth(request: Request, x_api_key: Optional[str] = Header(default=None)) -> dict:
    if not APP_AUTH_REQUIRED:
        return {"sub": "demo-staff", "role": "teacher"}
    if x_api_key and x_api_key in APP_API_KEYS:
        return {"sub": "api-key-staff", "role": "admin"}
    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        claims = verify_access_token(authorization[7:].strip())
        if claims.get("role") in {"teacher", "admin"}:
            return claims
    raise HTTPException(status_code=403, detail="Teacher or administrator access required")
