from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import timestamp_to_iso

logger = logging.getLogger(__name__)


async def export_statistics(guild: discord.Guild, members_data: list[dict[str, Any]], roles_data: list[dict[str, Any]], channels_data: dict[str, Any]) -> dict[str, Any]:
    member_count = len(members_data)
    bot_count = sum(1 for m in members_data if m.get("bot"))
    human_count = member_count - bot_count
    online_count = sum(1 for m in members_data if m.get("status") and m["status"] != "offline")

    roles_by_position = sorted(roles_data, key=lambda r: r.get("position", 0), reverse=True)
    managed_roles = [r for r in roles_data if r.get("managed")]
    hoisted_roles = [r for r in roles_data if r.get("hoist")]

    total_text = channels_data.get("total_text", 0)
    total_voice = channels_data.get("total_voice", 0)
    total_forum = channels_data.get("total_forum", 0)
    total_stage = channels_data.get("total_stage", 0)
    total_categories = channels_data.get("total_categories", 0)

    nsfw_channels = 0
    for ch_type in ["text_channels", "announcement_channels", "forum_channels"]:
        for ch in channels_data.get(ch_type, []):
            if ch.get("nsfw"):
                nsfw_channels += 1

    data = {
        "server_name": guild.name,
        "server_id": guild.id,
        "total_members": member_count,
        "total_humans": human_count,
        "total_bots": bot_count,
        "bot_percentage": round((bot_count / member_count * 100) if member_count else 0, 2),
        "online_members": online_count,
        "total_roles": len(roles_data),
        "managed_roles": len(managed_roles),
        "hoisted_roles": len(hoisted_roles),
        "roles_with_administrator": sum(1 for r in roles_data if r.get("permissions", {}).get("administrator", False)),
        "total_channels": channels_data.get("total_channels", 0),
        "text_channels": total_text,
        "voice_channels": total_voice,
        "forum_channels": total_forum,
        "stage_channels": total_stage,
        "categories": total_categories,
        "nsfw_channels": nsfw_channels,
        "boost_count": guild.premium_subscription_count,
        "boost_tier": guild.premium_tier,
        "channel_distribution": {
            "text": total_text,
            "voice": total_voice,
            "forum": total_forum,
            "stage": total_stage,
            "categories": total_categories,
        },
        "text_to_voice_ratio": round(total_text / total_voice, 2) if total_voice else float("inf"),
        "members_per_channel": round(member_count / (total_text + total_voice + total_forum + total_stage), 2) if (total_text + total_voice + total_forum + total_stage) else 0,
    }

    logger.info("Exported server statistics")
    return data
