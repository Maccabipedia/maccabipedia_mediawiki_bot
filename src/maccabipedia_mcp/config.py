from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    url: str
    username: str | None
    password: str | None

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            url=os.environ.get("MACCABIPEDIA_URL", "https://www.maccabipedia.co.il"),
            username=os.environ.get("MACCABIPEDIA_BOT_USERNAME"),
            password=os.environ.get("MACCABIPEDIA_BOT_PASSWORD"),
        )

    @property
    def api_url(self) -> str:
        return f"{self.url}/api.php"
