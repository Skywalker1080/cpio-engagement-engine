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

# ── Paths ─────────────────────────────────────────────────
KEYWORDS_PATH: Path = Path(__file__).resolve().parent / "keywords.json"
LOG_DIR: Path = _project_root / "logs"
INTERACTIONS_LOG: Path = LOG_DIR / "interactions.json"

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)


def load_keywords() -> dict:
    """Load keyword definitions from keywords.json."""
    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
