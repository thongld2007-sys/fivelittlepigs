"""Server-side FPT AI Marketplace client for text and vision completions."""

from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from backend.config import (
    FPT_AI_API_KEY, FPT_AI_BASE_URL, FPT_AI_MAX_TOKENS, FPT_AI_MODEL,
    FPT_AI_TEMPERATURE, FPT_AI_TIMEOUT_SECONDS, FPT_AI_VISION_MODEL,
)


class FPTAIError(RuntimeError):
    """Safe provider error that never includes credentials."""


@dataclass(frozen=True)
class FPTAIResult:
    content: str
    model: str
    usage: dict | None
    latency_ms: float = 0.0


class FPTAIClient:
    def __init__(self, *, api_key: str = FPT_AI_API_KEY, model: str = FPT_AI_MODEL,
                 vision_model: str = FPT_AI_VISION_MODEL, base_url: str = FPT_AI_BASE_URL,
                 timeout: float = FPT_AI_TIMEOUT_SECONDS) -> None:
        self.api_key = api_key.strip()
        self.model = model.strip()
        self.vision_model = vision_model.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.model and self.base_url)

    @property
    def vision_configured(self) -> bool:
        return bool(self.api_key and self.vision_model and self.base_url)

    def complete(self, *, system_prompt: str, user_prompt: str, history: list[dict] | None = None) -> FPTAIResult:
        if not self.configured:
            raise FPTAIError("FPT AI chưa được cấu hình đầy đủ.")
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_prompt})
        return self._send({
            "model": self.model,
            "messages": messages,
            "temperature": FPT_AI_TEMPERATURE,
            "max_tokens": FPT_AI_MAX_TOKENS,
            "stream": False,
        }, self.model)

    def complete_vision(self, *, image_bytes: bytes, mime_type: str,
                        system_prompt: str, user_prompt: str) -> FPTAIResult:
        if not self.vision_configured:
            raise FPTAIError("FPT AI Vision chưa được cấu hình model.")
        encoded = base64.b64encode(image_bytes).decode("ascii")
        return self._send({
            "model": self.vision_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{encoded}"}},
                    {"type": "text", "text": user_prompt},
                ]},
            ],
            "temperature": 0.0,
            "max_tokens": FPT_AI_MAX_TOKENS,
            "stream": False,
        }, self.vision_model)

    def _send(self, payload: dict, fallback_model: str) -> FPTAIResult:
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}", "api-key": self.api_key,
                "Content-Type": "application/json", "Accept": "application/json",
                "User-Agent": "VGapAI/2.0 (+https://github.com/thongld2007-sys/fivelittlepigs)",
            },
        )
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                error_body = json.loads(exc.read(4096).decode("utf-8"))
                candidate = error_body.get("detail") or error_body.get("message") or error_body.get("error")
                if isinstance(candidate, dict):
                    candidate = candidate.get("message") or candidate.get("detail")
                detail = str(candidate or "").replace(self.api_key, "[redacted]")[:300]
            except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
                pass
            message = {401: "FPT AI từ chối API key.", 403: "Model FPT AI chưa được cấp quyền.",
                       429: "FPT AI đang giới hạn tần suất."}.get(exc.code, f"FPT AI trả về HTTP {exc.code}.")
            raise FPTAIError(f"{message}{' Chi tiết: ' + detail if detail else ''}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise FPTAIError("Không thể kết nối FPT AI.") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise FPTAIError("Phản hồi FPT AI không đúng định dạng JSON.") from exc
        try:
            message = body["choices"][0]["message"]
            raw_content = message.get("content") or message.get("reasoning_content") or ""
            content = raw_content.strip()
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise FPTAIError(f"Phản hồi FPT AI không chứa nội dung trả lời. Dữ liệu gốc: {body}") from exc
        if not content:
            raise FPTAIError("FPT AI trả về nội dung rỗng.")
        return FPTAIResult(content, body.get("model", fallback_model), body.get("usage"),
                           round((time.perf_counter() - started) * 1000, 2))


fpt_ai_client = FPTAIClient()
