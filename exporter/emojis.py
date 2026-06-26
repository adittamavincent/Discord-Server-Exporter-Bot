from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import timestamp_to_iso

logger = logging.getLogger(__name__)


async def export_emojis(guild: discord.Guild) -> dict[str, Any]:
    standard_emojis: list[dict[str, Any]] = []
    animated_emojis: list[dict[str, Any]] = []
    static_emojis: list[dict[str, Any]] = []

    for emoji in guild.emojis:
        emoji_data = {
            "id": emoji.id,
            "name": emoji.name,
            "animated": emoji.animated,
            "available": emoji.available,
            "managed": emoji.managed,
            "require_colons": emoji.require_colons,
            "roles": [{"id": r.id, "name": r.name} for r in emoji.roles] if emoji.roles else [],
            "url": emoji.url,
            "created_at": timestamp_to_iso(emoji.created_at) if hasattr(emoji, "created_at") else None,
        }

        standard_emojis.append(emoji_data)
        if emoji.animated:
            animated_emojis.append(emoji_data)
        else:
            static_emojis.append(emoji_data)

    data = {
        "total_emojis": len(standard_emojis),
        "animated_emojis": len(animated_emojis),
        "static_emojis": len(static_emojis),
        "emoji_limit": guild.emoji_limit,
        "emojis": standard_emojis,
    }

    logger.info("Exported %d emojis", data["total_emojis"])
    return data
