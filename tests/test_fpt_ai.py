import json
import unittest
from unittest.mock import patch

from backend.fpt_ai import FPTAIClient


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class TestFPTAIClient(unittest.TestCase):
    def test_client_sends_chat_completion_and_parses_result(self):
        client = FPTAIClient(api_key="secret-test-key", model="test-model")
        captured = {}

        def fake_urlopen(request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return _FakeResponse({
                "model": "test-model",
                "choices": [{"message": {"content": "Gợi ý từng bước"}}],
                "usage": {"total_tokens": 12},
            })

        with patch("backend.fpt_ai.urllib.request.urlopen", side_effect=fake_urlopen):
            result = client.complete(system_prompt="system", user_prompt="user")

        request = captured["request"]
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.full_url, "https://mkp-api.fptcloud.com/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-test-key")
        self.assertEqual(body["model"], "test-model")
        self.assertEqual(body["messages"][1]["content"], "user")
        self.assertEqual(result.content, "Gợi ý từng bước")
        self.assertEqual(result.usage["total_tokens"], 12)

    def test_client_reports_unconfigured_without_network_call(self):
        client = FPTAIClient(api_key="", model="")
        with patch("backend.fpt_ai.urllib.request.urlopen") as urlopen:
            with self.assertRaisesRegex(RuntimeError, "chưa được cấu hình"):
                client.complete(system_prompt="system", user_prompt="user")
        urlopen.assert_not_called()

    def test_vision_client_sends_base64_image_content(self):
        client = FPTAIClient(api_key="secret-test-key", model="text-model", vision_model="vision-model")
        captured = {}

        def fake_urlopen(request, timeout):
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return _FakeResponse({"model": "vision-model", "choices": [{"message": {"content": "Bước hai sai dấu"}}]})

        with patch("backend.fpt_ai.urllib.request.urlopen", side_effect=fake_urlopen):
            result = client.complete_vision(
                image_bytes=b"fake-image", mime_type="image/png",
                system_prompt="analyze", user_prompt="read work",
            )

        image_url = captured["body"]["messages"][1]["content"][0]["image_url"]["url"]
        self.assertTrue(image_url.startswith("data:image/png;base64,"))
        self.assertEqual(result.content, "Bước hai sai dấu")


if __name__ == "__main__":
    unittest.main()
