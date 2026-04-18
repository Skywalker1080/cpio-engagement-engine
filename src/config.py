"""
Centralized configuration loader.
Reads environment variables from .env and exposes them as module-level constants.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")

# ── Discord ───────────────────────────────────────────────
DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "").strip(' "')
APP_ID: str = os.getenv("APP_ID", "").strip(' "')
PUBLIC_KEY: str = os.getenv("PUBLIC_KEY", "").strip(' "')

# ── LLM ───────────────────────────────────────────────────
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

# ── Apify ───────────────────────────────────────────────────
APIFY_TOKEN: str = os.getenv("APIFY_TOKEN", "").strip(' "')

# ── Reddit API (PRAW) ─────────────────────────────────────
REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "").strip(' "')
REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "").strip(' "')
REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "CryptoPrism/1.0").strip(' "')
REDDIT_USERNAME: str = os.getenv("REDDIT_USERNAME", "").strip(' "')
REDDIT_PASSWORD: str = os.getenv("REDDIT_PASSWORD", "").strip(' "')


# ── LinkedIn API ────────────────────────────────────────────
LINKEDIN_CLIENT_ID: str = os.getenv("LINKEDIN_CLIENT_ID", "").strip(' "')
LINKEDIN_CLIENT_SECRET: str = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip(' "')
LINKEDIN_REDIRECT_URI: str = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8080/callback").strip(' "')

# ── Paths ─────────────────────────────────────────────────
KEYWORDS_PATH: Path = Path(__file__).resolve().parent / "keywords.json"
LOG_DIR: Path = _project_root / "logs"
INTERACTIONS_LOG: Path = LOG_DIR / "interactions.json"
LINKEDIN_TOKEN_PATH: Path = _project_root / ".linkedin_token.json"

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)


def load_keywords() -> dict:
    """Load keyword definitions from keywords.json."""
    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
