from __future__ import annotations

import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATHS: Final[list[Path]] = [
    Path(".env"),
    Path.home() / ".config" / "discord-exporter" / ".env",
]


@dataclass(frozen=True)
class Config:
    token: str = field(repr=False)
    guild_id: int | None = None
    output_dir: Path = Path("output")
    export_ai_summary: bool = True
    export_markdown: bool = True
    export_zip: bool = True
    export_ai_prompt: bool = True
    max_members: int = 1000
    request_delay: float = 0.5
    log_level: str = "INFO"
    log_file: str | None = None

    @property
    def int_token(self) -> str:
        return self.token

    @classmethod
    def from_env(cls, env_file: str | None = None) -> Config:
        paths = [Path(env_file)] if env_file else DEFAULT_CONFIG_PATHS
        loaded = False
        for p in paths:
            if p.exists():
                load_dotenv(p, override=True)
                logger.info("Loaded config from %s", p.resolve())
                loaded = True
                break

        token = os.getenv("DISCORD_TOKEN", "")
        if not token:
            raise ConfigError(
                "DISCORD_TOKEN is not set. "
                "Create a .env file or set the environment variable."
            )

        guild_raw = os.getenv("GUILD_ID")
        guild_id: int | None = None
        if guild_raw:
            try:
                guild_id = int(guild_raw.strip())
            except ValueError:
                raise ConfigError(f"Invalid GUILD_ID: {guild_raw!r}")

        output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
        export_ai_summary = os.getenv("EXPORT_AI_SUMMARY", "true").lower() == "true"
        export_markdown = os.getenv("EXPORT_MARKDOWN", "true").lower() == "true"
        export_zip = os.getenv("EXPORT_ZIP", "true").lower() == "true"
        export_ai_prompt = os.getenv("EXPORT_AI_PROMPT", "true").lower() == "true"

        max_members_raw = os.getenv("MAX_MEMBERS", "1000")
        try:
            max_members = int(max_members_raw)
        except ValueError:
            max_members = 1000

        request_delay_raw = os.getenv("REQUEST_DELAY", "0.5")
        try:
            request_delay = float(request_delay_raw)
        except ValueError:
            request_delay = 0.5

        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_file = os.getenv("LOG_FILE") or None

        return cls(
            token=token,
            guild_id=guild_id,
            output_dir=output_dir,
            export_ai_summary=export_ai_summary,
            export_markdown=export_markdown,
            export_zip=export_zip,
            export_ai_prompt=export_ai_prompt,
            max_members=max_members,
            request_delay=request_delay,
            log_level=log_level,
            log_file=log_file,
        )


class ConfigError(Exception):
    pass
