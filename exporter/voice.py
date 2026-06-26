from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import overwrite_to_dict, timestamp_to_iso

logger = logging.getLogger(__name__)


async def export_voice(guild: discord.Guild) -> dict[str, Any]:
    voice_channels_list: list[dict[str, Any]] = []

    for channel in guild.channels:
        if isinstance(channel, discord.VoiceChannel):
            vc_data = _export_voice_channel_data(channel)
            voice_channels_list.append(vc_data)

    data = {
        "total_voice_channels": len(voice_channels_list),
        "voice_channels": voice_channels_list,
        "total_bitrate": sum(vc.get("bitrate", 0) or 0 for vc in voice_channels_list),
        "max_user_limit": max((vc.get("user_limit", 0) or 0) for vc in voice_channels_list) if voice_channels_list else 0,
    }

    logger.info("Exported %d voice channels", len(voice_channels_list))
    return data


def _export_voice_channel_data(channel: discord.VoiceChannel) -> dict[str, Any]:
    overwrites = []
    for target, overwrite in channel.overwrites.items():
        overwrites.append(overwrite_to_dict(target, overwrite))

    return {
        "id": channel.id,
        "name": channel.name,
        "position": channel.position,
        "bitrate": channel.bitrate,
        "user_limit": channel.user_limit,
        "rtc_region": str(channel.rtc_region) if channel.rtc_region else None,
        "video_quality_mode": str(channel.video_quality_mode) if hasattr(channel, "video_quality_mode") and channel.video_quality_mode else None,
        "category_id": channel.category_id,
        "category_name": channel.category.name if channel.category else None,
        "permission_overwrites": overwrites,
        "created_at": timestamp_to_iso(channel.created_at),
    }
