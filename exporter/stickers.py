from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import timestamp_to_iso

logger = logging.getLogger(__name__)


async def export_stickers(guild: discord.Guild) -> list[dict[str, Any]]:
    stickers_data: list[dict[str, Any]] = []

    try:
        stickers = await guild.fetch_stickers()
        for sticker in stickers:
            sticker_data = {
                "id": sticker.id,
                "name": sticker.name,
                "description": sticker.description,
                "type": str(sticker.type),
                "format": str(sticker.format),
                "available": getattr(sticker, "available", True),
                "tags": sticker.tags if hasattr(sticker, "tags") else None,
                "emoji": sticker.emoji if hasattr(sticker, "emoji") else None,
                "url": sticker.url if hasattr(sticker, "url") else None,
                "created_at": timestamp_to_iso(sticker.created_at) if hasattr(sticker, "created_at") else None,
            }
            stickers_data.append(sticker_data)
    except discord.Forbidden:
        logger.warning("No permission to fetch stickers")
    except discord.HTTPException as e:
        logger.warning("Failed to fetch stickers: %s", e)

    logger.info("Exported %d stickers", len(stickers_data))
    return stickers_data
