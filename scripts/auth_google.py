"""Authorize this machine for the repository's Google Drive utilities."""
from __future__ import annotations

import os
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]
SECRETS_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))) / "MTS" / ".secrets"
CLIENT_CONFIG = Path(os.environ.get("MTS_GOOGLE_OAUTH_CLIENT", str(SECRETS_DIR / "oauth-client.json")))
TOKEN_PATH = Path(os.environ.get("MTS_GOOGLE_OAUTH_TOKEN", str(SECRETS_DIR / "oauth-token.json")))


def main() -> None:
    if not CLIENT_CONFIG.is_file():
        raise SystemExit(
            f"OAuth Desktop client JSON not found at {CLIENT_CONFIG}. "
            "Set MTS_GOOGLE_OAUTH_CLIENT or place the downloaded file there."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_CONFIG), SCOPES)
    credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(credentials.to_json(), encoding="utf-8")
    print(f"Google OAuth token saved to {TOKEN_PATH}")


if __name__ == "__main__":
    main()