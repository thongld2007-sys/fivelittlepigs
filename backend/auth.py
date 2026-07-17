"""Small dependency-free API-key/JWT security layer for production mode."""

import base64
import hashlib
import hmac
import json
import time

from fastapi import Header, HTTPException, Request

from backend.config import APP_API_KEYS, APP_AUTH_REQUIRED, APP_JWT_SECRET, APP_JWT_TTL_SECONDS


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_access_token(subject: str) -> str:
    if not APP_JWT_SECRET:
        raise HTTPException(status_code=503, detail="JWT secret is not configured")
    header = _encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _encode(json.dumps({"sub": subject, "exp": int(time.time()) + APP_JWT_TTL_SECONDS}, separators=(",", ":")).encode())
    signature = _encode(hmac.new(APP_JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"


def verify_access_token(token: str) -> dict:
    try:
        header, payload, signature = token.split(".")
        expected = _encode(hmac.new(APP_JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
        if not APP_JWT_SECRET or not hmac.compare_digest(signature, expected):
            raise ValueError("signature")
        claims = json.loads(_decode(payload))
        if int(claims.get("exp", 0)) < int(time.time()):
            raise ValueError("expired")
        return claims
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc


def exchange_api_key(api_key: str | None) -> str:
    if not api_key or api_key not in APP_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return create_access_token("vgap-api-client")


def require_auth(request: Request, x_api_key: str | None = Header(default=None)) -> dict:
    if not APP_AUTH_REQUIRED:
        return {"sub": "demo-mode"}
    if x_api_key and x_api_key in APP_API_KEYS:
        return {"sub": "api-key-client"}
    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        return verify_access_token(authorization[7:].strip())
    raise HTTPException(status_code=401, detail="Authentication required")
