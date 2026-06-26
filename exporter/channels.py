from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import overwrite_to_dict, timestamp_to_iso

logger = logging.getLogger(__name__)


async def export_channels(guild: discord.Guild) -> dict[str, Any]:
    categories: list[dict[str, Any]] = []
    text_channels: list[dict[str, Any]] = []
    voice_channels: list[dict[str, Any]] = []
    forum_channels: list[dict[str, Any]] = []
    media_channels: list[dict[str, Any]] = []
    stage_channels: list[dict[str, Any]] = []
    announcement_channels: list[dict[str, Any]] = []
    uncategorized: list[dict[str, Any]] = []

    for channel in guild.channels:
        if isinstance(channel, discord.CategoryChannel):
            categories.append(await _export_category(channel))
        elif isinstance(channel, discord.TextChannel):
            data = _export_text_channel(channel)
            if channel.is_news():
                announcement_channels.append(data)
            else:
                text_channels.append(data)
        elif isinstance(channel, discord.VoiceChannel):
            voice_channels.append(_export_voice_channel(channel))
        elif isinstance(channel, discord.ForumChannel):
            forum_channels.append(await _export_forum_channel(channel))
        elif isinstance(channel, discord.StageChannel):
            stage_channels.append(_export_stage_channel(channel))
        else:
            uncategorized.append(_export_unknown_channel(channel))

    for thread in guild.threads:
        parent_id = thread.parent_id
        parent_found = False
        for lst in [text_channels, announcement_channels, forum_channels]:
            for ch in lst:
                if ch["id"] == parent_id:
                    ch.setdefault("active_threads", []).append(_export_thread(thread))
                    parent_found = True
                    break
            if parent_found:
                break

    data = {
        "categories": categories,
        "text_channels": text_channels,
        "voice_channels": voice_channels,
        "forum_channels": forum_channels,
        "media_channels": media_channels,
        "stage_channels": stage_channels,
        "announcement_channels": announcement_channels,
        "uncategorized": uncategorized,
        "total_channels": len(guild.channels),
        "total_categories": len(categories),
        "total_text": len(text_channels) + len(announcement_channels),
        "total_voice": len(voice_channels),
        "total_forum": len(forum_channels),
        "total_stage": len(stage_channels),
    }

    logger.info("Exported %d channels", data["total_channels"])
    return data


async def _export_category(channel: discord.CategoryChannel) -> dict[str, Any]:
    overwrites = []
    for target, overwrite in channel.overwrites.items():
        overwrites.append(overwrite_to_dict(target, overwrite))

    return {
        "id": channel.id,
        "name": channel.name,
        "position": channel.position,
        "type": "category",
        "permission_overwrites": overwrites,
        "created_at": timestamp_to_iso(channel.created_at),
    }


def _export_text_channel(channel: discord.TextChannel) -> dict[str, Any]:
    overwrites = []
    for target, overwrite in channel.overwrites.items():
        overwrites.append(overwrite_to_dict(target, overwrite))

    return {
        "id": channel.id,
        "name": channel.name,
        "position": channel.position,
        "type": "text",
        "topic": channel.topic,
        "slowmode_delay": channel.slowmode_delay,
        "nsfw": channel.is_nsfw(),
        "is_news": channel.is_news(),
        "category_id": channel.category_id,
        "category_name": channel.category.name if channel.category else None,
        "default_auto_archive_duration": channel.default_auto_archive_duration,
        "default_thread_slowmode_delay": channel.default_thread_slowmode_delay,
        "permission_overwrites": overwrites,
        "created_at": timestamp_to_iso(channel.created_at),
        "mention": channel.mention,
    }


def _export_voice_channel(channel: discord.VoiceChannel) -> dict[str, Any]:
    overwrites = []
    for target, overwrite in channel.overwrites.items():
        overwrites.append(overwrite_to_dict(target, overwrite))

    return {
        "id": channel.id,
        "name": channel.name,
        "position": channel.position,
        "type": "voice",
        "bitrate": channel.bitrate,
        "user_limit": channel.user_limit,
        "rtc_region": str(channel.rtc_region) if channel.rtc_region else None,
        "video_quality_mode": str(channel.video_quality_mode) if hasattr(channel, "video_quality_mode") and channel.video_quality_mode else None,
        "category_id": channel.category_id,
        "category_name": channel.category.name if channel.category else None,
        "permission_overwrites": overwrites,
        "created_at": timestamp_to_iso(channel.created_at),
        "mention": channel.mention,
    }


async def _export_forum_channel(channel: discord.ForumChannel) -> dict[str, Any]:
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
        "default_thread_rate_limit_per_user": channel.default_thread_slowmode_delay,
        "available_tags": tags,
        "permission_overwrites": overwrites,
        "created_at": timestamp_to_iso(channel.created_at),
    }


def _export_stage_channel(channel: discord.StageChannel) -> dict[str, Any]:
    overwrites = []
    for target, overwrite in channel.overwrites.items():
        overwrites.append(overwrite_to_dict(target, overwrite))

    return {
        "id": channel.id,
        "name": channel.name,
        "position": channel.position,
        "type": "stage",
        "topic": channel.topic,
        "bitrate": channel.bitrate,
        "user_limit": channel.user_limit,
        "rtc_region": str(channel.rtc_region) if channel.rtc_region else None,
        "category_id": channel.category_id,
        "category_name": channel.category.name if channel.category else None,
        "permission_overwrites": overwrites,
        "created_at": timestamp_to_iso(channel.created_at),
    }


def _export_thread(thread: discord.Thread) -> dict[str, Any]:
    return {
        "id": thread.id,
        "name": thread.name,
        "type": str(thread.type),
        "owner_id": thread.owner_id,
        "parent_id": thread.parent_id,
        "message_count": thread.message_count,
        "member_count": thread.member_count,
        "slowmode_delay": thread.slowmode_delay,
        "auto_archive_duration": thread.auto_archive_duration,
        "archived": thread.archived,
        "locked": thread.locked,
        "nsfw": thread.is_nsfw(),
        "created_at": timestamp_to_iso(thread.created_at),
        "archived_at": timestamp_to_iso(thread.archived_at) if hasattr(thread, "archived_at") else None,
    }


def _export_unknown_channel(channel: discord.abc.GuildChannel) -> dict[str, Any]:
    return {
        "id": channel.id,
        "name": channel.name,
        "type": str(channel.type),
        "position": channel.position,
        "created_at": timestamp_to_iso(channel.created_at),
    }
