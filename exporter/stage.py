from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import overwrite_to_dict, timestamp_to_iso

logger = logging.getLogger(__name__)


async def export_stage(guild: discord.Guild) -> dict[str, Any]:
    stage_channels_list: list[dict[str, Any]] = []
    stage_instances_list: list[dict[str, Any]] = []

    for channel in guild.channels:
        if isinstance(channel, discord.StageChannel):
            stage_data = _export_stage_channel_data(channel)
            stage_channels_list.append(stage_data)

    for channel in guild.stage_channels:
        try:
            if hasattr(channel, "instance") and channel.instance:
                stage_instances_list.append({
                    "channel_id": channel.id,
                    "channel_name": channel.name,
                    "topic": channel.instance.topic,
                    "privacy_level": str(channel.instance.privacy_level) if hasattr(channel.instance, "privacy_level") else None,
                    "discoverable_disabled": channel.instance.discoverable_disabled if hasattr(channel.instance, "discoverable_disabled") else None,
                    "guild_scheduled_event_id": channel.instance.guild_scheduled_event_id if hasattr(channel.instance, "guild_scheduled_event_id") else None,
                })
        except Exception:
            pass

    data = {
        "total_stage_channels": len(stage_channels_list),
        "stage_channels": stage_channels_list,
        "active_stage_instances": stage_instances_list,
        "total_active_instances": len(stage_instances_list),
    }

    logger.info("Exported %d stage channels", len(stage_channels_list))
    return data


def _export_stage_channel_data(channel: discord.StageChannel) -> dict[str, Any]:
    overwrites = []
    for target, overwrite in channel.overwrites.items():
        overwrites.append(overwrite_to_dict(target, overwrite))

    return {
        "id": channel.id,
        "name": channel.name,
        "position": channel.position,
        "topic": channel.topic,
        "bitrate": channel.bitrate,
        "user_limit": channel.user_limit,
        "rtc_region": str(channel.rtc_region) if channel.rtc_region else None,
        "category_id": channel.category_id,
        "category_name": channel.category.name if channel.category else None,
        "permission_overwrites": overwrites,
        "created_at": timestamp_to_iso(channel.created_at),
    }
