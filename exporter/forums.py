from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import overwrite_to_dict, timestamp_to_iso

logger = logging.getLogger(__name__)


async def export_forums(guild: discord.Guild) -> list[dict[str, Any]]:
    forums_data: list[dict[str, Any]] = []

    for channel in guild.channels:
        if isinstance(channel, discord.ForumChannel):
            forum_data = await _export_forum(channel)
            forums_data.append(forum_data)

    logger.info("Exported %d forum channels", len(forums_data))
    return forums_data


async def _export_forum(channel: discord.ForumChannel) -> dict[str, Any]:
    overwrites = []
    for target, overwrite in channel.overwrites.items():
        overwrites.append(overwrite_to_dict(target, overwrite))

    tags = []
    try:
        for tag in channel.available_tags:
            tags.append({
                "id": tag.id,
                "name": tag.name,
                "moderated": tag.moderated,
                "emoji": str(tag.emoji) if tag.emoji else None,
            })
    except Exception:
        pass

    default_reaction_emoji = None
    try:
        if channel.default_reaction_emoji:
            default_reaction_emoji = str(channel.default_reaction_emoji)
    except Exception:
        pass

    return {
        "id": channel.id,
        "name": channel.name,
        "position": channel.position,
        "type": "forum",
        "topic": channel.topic,
        "nsfw": channel.is_nsfw(),
        "category_id": channel.category_id,
        "category_name": channel.category.name if channel.category else None,
        "slowmode_delay": channel.slowmode_delay,
        "default_auto_archive_duration": channel.default_auto_archive_duration,
        "default_sort_order": str(channel.default_sort_order) if hasattr(channel, "default_sort_order") and channel.default_sort_order else None,
        "default_thread_rate_limit_per_user": getattr(channel, "default_thread_slowmode_delay", None),
        "default_reaction_emoji": default_reaction_emoji,
        "available_tags": tags,
        "total_tags": len(tags),
        "permission_overwrites": overwrites,
        "created_at": timestamp_to_iso(channel.created_at),
    }
