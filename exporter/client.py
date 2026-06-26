from __future__ import annotations

import asyncio
import logging
from typing import Any

import discord

logger = logging.getLogger(__name__)


class DiscordClient(discord.Client):
    def __init__(self, config: Any, **kwargs: Any) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.message_content = True
        intents.moderation = True
        intents.guild_typing = False
        intents.guild_messages = True

        super().__init__(intents=intents, **kwargs)

        self.config = config
        self._ready_event = asyncio.Event()
        self._guild_data: dict[str, Any] | None = None

    async def on_ready(self) -> None:
        logger.info("Logged in as %s (ID: %s)", self.user, self.user.id)
        self._ready_event.set()

    async def wait_until_ready(self) -> None:
        await self._ready_event.wait()

    async def fetch_guild_data(self, guild_id: int | None = None) -> dict[str, Any] | None:
        await self.wait_until_ready()

        if guild_id:
            guild = self.get_guild(guild_id)
            if guild is None:
                try:
                    guild = await self.fetch_guild(guild_id)
                except discord.Forbidden:
                    logger.error("No permission to access guild %s", guild_id)
                    raise
                except discord.HTTPException as e:
                    logger.error("Failed to fetch guild %s: %s", guild_id, e)
                    raise
        else:
            guilds = self.guilds
            if not guilds:
                logger.error("Bot is not in any guilds.")
                return None
            guild = guilds[0]
            if len(guilds) > 1:
                logger.info(
                    "Multiple guilds found. Use --guild to specify one. "
                    "Using first: %s (%s)",
                    guild.name,
                    guild.id,
                )

        self._guild_data = {"guild": guild, "guild_id": guild.id}
        return self._guild_data

    async def close(self) -> None:
        await super().close()

    @property
    def guild(self) -> discord.Guild | None:
        if self._guild_data:
            return self._guild_data.get("guild")
        return None
