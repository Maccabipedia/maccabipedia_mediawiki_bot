from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
CONFIG_DIR = Path.home() / ".config/maccabipedia"
CLIENT_SECRET = CONFIG_DIR / "youtube_client_secret.json"
TOKEN_FILE = CONFIG_DIR / "youtube_token.json"


def run_auth_flow() -> None:
    """Run OAuth flow against MaccabiPedia's Google project and save the token.

    Prints the auth URL; approve in a browser on the same machine (port 8080 must be
    accessible from the browser). The token is refreshable for ~7 days while the OAuth
    app stays in Testing mode.

    Important: MaccabiPedia is a Google Brand Account. At the consent screen, select the
    MaccabiPedia brand (not the default personal account) — otherwise the token will be
    bound to an account with no channel and uploads will fail with "Channel not found".
    """
    if not CLIENT_SECRET.is_file():
        raise SystemExit(
            f"Client secret not found at {CLIENT_SECRET}. Download the OAuth 2.0 Desktop "
            f"client credentials from Google Cloud Console and save them there."
        )
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(
        port=8080,
        open_browser=False,
        prompt="select_account consent",
    )
    TOKEN_FILE.write_text(creds.to_json())
    print(f"Token saved to {TOKEN_FILE}")


if __name__ == "__main__":
    run_auth_flow()
