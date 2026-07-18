"""Private object storage abstraction with a safe local default."""

from __future__ import annotations

import os
import re
from pathlib import Path
from uuid import uuid4

from backend.config import Config


_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class LocalObjectStorage:
    """Stores private uploads outside the public frontend directory."""

    def __init__(self, root: str):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes, mime_type: str, original_name: str | None = None) -> dict:
        extension = _EXTENSIONS.get(mime_type, "")
        if not extension and original_name:
            suffix = Path(original_name).suffix.lower()
            extension = suffix if re.fullmatch(r"\.[a-z0-9]{1,8}", suffix) else ""
        object_key = f"student-work/{uuid4().hex}{extension}"
        destination = (self.root / object_key).resolve()
        if self.root not in destination.parents:
            raise ValueError("Invalid object key")
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_bytes(content)
        os.replace(temporary, destination)
        return {"object_key": object_key, "size_bytes": len(content)}


object_storage = LocalObjectStorage(Config.UPLOAD_DIR)
