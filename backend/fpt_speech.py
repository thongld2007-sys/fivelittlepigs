"""FPT.AI Console Speech adapters (TTS v5 and general ASR)."""

import json
import urllib.error
import urllib.request

from backend.config import FPT_SPEECH_API_KEY, FPT_STT_URL, FPT_TTS_URL, FPT_TTS_VOICE
from backend.fpt_ai import FPTAIError


class FPTSpeechClient:
    @property
    def configured(self) -> bool:
        return bool(FPT_SPEECH_API_KEY)

    def text_to_speech(self, text: str, *, voice: str = FPT_TTS_VOICE, speed: int = 0) -> dict:
        if not self.configured:
            raise FPTAIError("FPT Speech chưa được cấu hình API key riêng.")
        request = urllib.request.Request(FPT_TTS_URL, data=text.encode("utf-8"), method="POST", headers={
            "api-key": FPT_SPEECH_API_KEY, "voice": voice, "speed": str(speed),
            "format": "mp3", "Content-Type": "text/plain; charset=utf-8",
        })
        body = self._json_request(request)
        if body.get("error") not in (0, "0", None) or not body.get("async"):
            raise FPTAIError("FPT TTS không tạo được tệp âm thanh.")
        return {"audio_url": body["async"], "request_id": body.get("request_id"), "voice": voice}

    def speech_to_text(self, audio: bytes, content_type: str) -> dict:
        if not self.configured:
            raise FPTAIError("FPT Speech chưa được cấu hình API key riêng.")
        request = urllib.request.Request(FPT_STT_URL, data=audio, method="POST", headers={
            "api-key": FPT_SPEECH_API_KEY, "Content-Type": content_type,
        })
        body = self._json_request(request)
        hypotheses = body.get("hypotheses") or []
        text = hypotheses[0].get("utterance", "").strip() if hypotheses else ""
        if body.get("status") not in (0, "0") or not text:
            raise FPTAIError("FPT STT không nhận dạng được nội dung âm thanh.")
        return {"text": text, "request_id": body.get("id")}

    @staticmethod
    def _json_request(request: urllib.request.Request) -> dict:
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            raise FPTAIError("Không thể gọi dịch vụ FPT Speech.") from exc


fpt_speech_client = FPTSpeechClient()
