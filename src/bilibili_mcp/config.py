"""Configuration for bilibili-mcp.

Single source of truth for environment variables. One .env file at the repo
root is loaded when present; env vars always win (no multi-file fallback
chain - see fleet rule: one .env, one source of truth).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"


def _load_dotenv() -> None:
    env_file = REPO_ROOT / ".env"
    if not env_file.exists():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"')


_load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    api_base: str = field(
        default_factory=lambda: os.environ.get(
            "BILIBILI_API_BASE", "https://api.bilibili.com"
        ).rstrip("/")
    )
    # Optional login cookie. Most content-intelligence endpoints work without
    # it; account-tier tools (following feed, favorites) require a logged-in
    # SESSDATA. Provide the full Cookie header value, e.g.
    #   BILIBILI_COOKIE="SESSDATA=...;bili_jct=..."
    cookie: str = field(default_factory=lambda: os.environ.get("BILIBILI_COOKIE", "").strip())
    llm_base_url: str = field(
        default_factory=lambda: os.environ.get(
            "BILIBILI_LLM_BASE_URL", "http://127.0.0.1:11434/v1"
        ).rstrip("/")
    )
    llm_model: str = field(
        default_factory=lambda: os.environ.get("BILIBILI_LLM_MODEL", "qwen2.5:7b").strip()
    )
    cache_ttl: int = field(default_factory=lambda: int(os.environ.get("BILIBILI_CACHE_TTL", "600")))
    backend_port: int = field(
        default_factory=lambda: int(os.environ.get("BILIBILI_BACKEND_PORT", "11185"))
    )
    frontend_port: int = field(
        default_factory=lambda: int(os.environ.get("BILIBILI_FRONTEND_PORT", "11186"))
    )
    request_timeout: float = 15.0
    # Bilibili rate-limits aggressive scraping. Default small page sizes and a
    # TTL cache are the polite default; raise this only if you have a cookie.
    anonymous_rate_budget: int = 100

    @property
    def configured(self) -> bool:
        """True when a login cookie is present (account tier)."""
        return bool(self.cookie)

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_base_url) and bool(self.llm_model)

    @property
    def user_agent(self) -> str:
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )


settings = Settings()
