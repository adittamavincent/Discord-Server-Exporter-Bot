from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import timestamp_to_iso

logger = logging.getLogger(__name__)


async def export_bots(guild: discord.Guild, members_data: list[dict[str, Any]]) -> dict[str, Any]:
    bot_members = [m for m in members_data if m.get("bot")]

    bot_details: list[dict[str, Any]] = []
    for bot in bot_members:
        bot_details.append({
            "id": bot["id"],
            "name": bot["name"],
            "display_name": bot.get("display_name", bot["name"]),
            "discriminator": bot.get("discriminator", "0"),
            "joined_at": bot.get("joined_at"),
            "roles": bot.get("roles", []),
            "role_ids": bot.get("role_ids", []),
            "top_role": bot.get("top_role"),
            "top_role_position": bot.get("top_role_position", 0),
        })

    total_webhooks = 0
    webhook_data: list[dict[str, Any]] = []
    try:
        webhooks = await guild.webhooks()
        for wh in webhooks:
            webhook_data.append({
                "id": wh.id,
                "name": wh.name,
                "channel_id": wh.channel_id,
                "channel_name": wh.channel.name if wh.channel else None,
                "type": str(wh.type),
                "application_id": getattr(wh, "application_id", None),
                "user_id": wh.user.id if wh.user else None,
                "user_name": wh.user.name if wh.user else None,
                "token": wh.token if hasattr(wh, "token") else None,
                "url": wh.url,
                "created_at": timestamp_to_iso(wh.created_at) if hasattr(wh, "created_at") else None,
            })
        total_webhooks = len(webhook_data)
    except discord.Forbidden:
        logger.warning("No permission to fetch webhooks")
    except discord.HTTPException as e:
        logger.warning("Failed to fetch webhooks: %s", e)

    data = {
        "total_bots": len(bot_details),
        "bot_percentage": round((len(bot_details) / len(members_data) * 100) if members_data else 0, 2),
        "bots": bot_details,
        "total_webhooks": total_webhooks,
        "webhooks": webhook_data,
    }

    logger.info("Exported %d bots and %d webhooks", len(bot_details), total_webhooks)
    return data
