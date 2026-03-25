"""Config loader — reads credentials from env vars or ~/.config/freshrss_cli/config.env."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

CONFIG_DIR = Path("~/.config/freshrss_cli").expanduser()
CONFIG_FILE = CONFIG_DIR / "config.env"


def load_config() -> tuple[str, str, str]:
    """Load FreshRSS credentials. Priority: env vars > config.env file.

    Returns:
        (url, username, password)

    Raises:
        RuntimeError: If any credential is missing.
    """
    # Load config file into env if present (won't override existing env vars)
    if CONFIG_FILE.exists():
        load_dotenv(CONFIG_FILE, override=False)

    url = os.environ.get("FRESHRSS_URL", "")
    username = os.environ.get("FRESHRSS_USERNAME", "")
    password = os.environ.get("FRESHRSS_PASSWORD", "")

    missing = [k for k, v in [("FRESHRSS_URL", url), ("FRESHRSS_USERNAME", username), ("FRESHRSS_PASSWORD", password)] if not v]
    if missing:
        raise RuntimeError(
            f"Missing credentials: {', '.join(missing)}. "
            f"Run `freshrss_cli setup` or set env vars."
        )

    return url, username, password


def credential_status() -> dict[str, str]:
    """Return masked credential status for display (no secrets)."""
    if CONFIG_FILE.exists():
        load_dotenv(CONFIG_FILE, override=False)

    def mask(val: str) -> str:
        return "✓ set" if val else "✗ missing"

    return {
        "FRESHRSS_URL": mask(os.environ.get("FRESHRSS_URL", "")),
        "FRESHRSS_USERNAME": mask(os.environ.get("FRESHRSS_USERNAME", "")),
        "FRESHRSS_PASSWORD": mask(os.environ.get("FRESHRSS_PASSWORD", "")),
        "config_file": str(CONFIG_FILE),
        "config_file_exists": str(CONFIG_FILE.exists()),
    }
