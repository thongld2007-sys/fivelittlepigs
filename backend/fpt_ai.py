"""Minimal server-side client for FPT AI Marketplace Chat Completions."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from backend.config import (
    FPT_AI_API_KEY,
    FPT_AI_BASE_URL,
    FPT_AI_MAX_TOKENS,
    FPT_AI_MODEL,
    FPT_AI_TEMPERATURE,
    FPT_AI_TIMEOUT_SECONDS,
)


class FPTAIError(RuntimeError):
    """Safe provider error that never includes credentials."""


@dataclass(frozen=True)
class FPTAIResult:
    content: str
    model: str
    usage: dict | None


class FPTAIClient:
    def __init__(
        self,
        *,
        api_key: str = FPT_AI_API_KEY,
        model: str = FPT_AI_MODEL,
        base_url: str = FPT_AI_BASE_URL,
        timeout: float = FPT_AI_TIMEOUT_SECONDS,
    ) -> None:
        self.api_key = api_key.strip()
        self.model = model.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.model and self.base_url)

    def complete(self, *, system_prompt: str, user_prompt: str, history: list[dict] = None) -> FPTAIResult:
        if not self.configured:
            raise FPTAIError("FPT AI chưa được cấu hình đầy đủ.")
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": FPT_AI_TEMPERATURE,
            "max_tokens": FPT_AI_MAX_TOKENS,
            "stream": False,
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "AdaptiveTutoringSystem/1.0 (+https://github.com/thongld2007-sys/fivelittlepigs)",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            provider_detail = ""
            try:
                error_body = json.loads(exc.read(4096).decode("utf-8"))
                candidate = error_body.get("detail") or error_body.get("message") or error_body.get("error")
                if isinstance(candidate, dict):
                    candidate = candidate.get("message") or candidate.get("detail")
                if candidate:
                    provider_detail = str(candidate).replace(self.api_key, "[redacted]")[:300]
            except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
                pass
            if exc.code in (401, 403):
                message = "FPT AI từ chối API key hoặc model chưa được cấp quyền."
            elif exc.code == 429:
                message = "FPT AI đang giới hạn tần suất; vui lòng thử lại sau."
            else:
                message = f"FPT AI trả về HTTP {exc.code}."
            if provider_detail:
                message = f"{message} Chi tiết: {provider_detail}"
            raise FPTAIError(message) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise FPTAIError("Không thể kết nối FPT AI; đang sử dụng chế độ offline.") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise FPTAIError("Phản hồi FPT AI không đúng định dạng JSON.") from exc

        try:
            content = body["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise FPTAIError(f"Phản hồi FPT AI không chứa nội dung trả lời. Dữ liệu gốc: {body}") from exc
        if not content:
            raise FPTAIError("FPT AI trả về nội dung rỗng.")
        return FPTAIResult(content=content, model=body.get("model", self.model), usage=body.get("usage"))


fpt_ai_client = FPTAIClient()
