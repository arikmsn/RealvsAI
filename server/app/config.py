"""Application configuration."""

import os
from pathlib import Path

# Project root is server/
SERVER_DIR = Path(__file__).resolve().parent.parent

# SQLite database file lives next to the server package
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{SERVER_DIR / 'realvsai.db'}")

# Secret key for signing session tokens (HMAC)
# In production, set SECRET_KEY env var to a long random string.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production")

# Game defaults
DEFAULT_ROUND_COUNT = 10
MAX_ROUND_COUNT = 20
