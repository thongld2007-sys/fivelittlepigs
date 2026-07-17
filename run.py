"""Convenient local/LAN entry point: py -3 run.py"""

import os

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "backend.app:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "8000")),
        reload=os.getenv("APP_RELOAD", "false").lower() in {"1", "true", "yes"},
    )
