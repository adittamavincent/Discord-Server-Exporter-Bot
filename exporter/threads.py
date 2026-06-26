from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import timestamp_to_iso

logger = logging.getLogger(__name__)


async def export_threads(guild: discord.Guild) -> list[dict[str, Any]]:
    threads_data: list[dict[str, Any]] = []

    for thread in guild.threads:
        thread_data = {
            "id": thread.id,
            "name": thread.name,
            "type": str(thread.type),
            "owner_id": thread.owner_id,
            "parent_id": thread.parent_id,
            "parent_name": _get_parent_name(guild, thread.parent_id),
            "message_count": thread.message_count,
            "member_count": thread.member_count,
            "slowmode_delay": thread.slowmode_delay,
            "auto_archive_duration": thread.auto_archive_duration,
            "archived": thread.archived,
            "locked": thread.locked,
            "nsfw": thread.is_nsfw(),
            "created_at": timestamp_to_iso(thread.created_at),
            "archived_at": timestamp_to_iso(thread.archived_at) if hasattr(thread, "archived_at") and thread.archived_at else None,
            "total_messages_sent": getattr(thread, "total_message_sent", None),
            "applied_tags": _get_thread_tags(thread),
        }
        threads_data.append(thread_data)

    logger.info("Exported %d threads", len(threads_data))
    return threads_data


def _get_parent_name(guild: discord.Guild, parent_id: int | None) -> str | None:
    if parent_id is None:
        return None
    channel = guild.get_channel(parent_id)
    if channel:
        return channel.name
    return str(parent_id)


def _get_thread_tags(thread: discord.Thread) -> list[dict[str, Any]]:
    tags: list[dict[str, Any]] = []
    try:
        for tag in thread.applied_tags:
            tags.append({
                "id": tag.id,
                "name": tag.name,
                "moderated": tag.moderated,
                "emoji": str(tag.emoji) if tag.emoji else None,
            })
    except Exception:
        pass
    return tags
