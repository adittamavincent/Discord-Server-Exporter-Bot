from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import permissions_to_dict, timestamp_to_iso

logger = logging.getLogger(__name__)


async def export_roles(guild: discord.Guild) -> list[dict[str, Any]]:
    roles = sorted(guild.roles, key=lambda r: r.position, reverse=True)

    roles_data: list[dict[str, Any]] = []
    for role in roles:
        role_data = {
            "id": role.id,
            "name": role.name,
            "color": role.color.value,
            "color_hex": str(role.color),
            "hoist": role.hoist,
            "position": role.position,
            "mentionable": role.mentionable,
            "managed": role.managed,
            "bot_id": role.tags.bot_id if role.tags and role.tags.bot_id else None,
            "integration_id": role.tags.integration_id if role.tags and role.tags.integration_id else None,
            "premium_subscriber": role.is_premium_subscriber(),
            "permissions": permissions_to_dict(role.permissions),
            "permissions_bitfield": role.permissions.value,
            "tags": _role_tags(role),
            "created_at": timestamp_to_iso(role.created_at),
            "mention": role.mention,
        }
        roles_data.append(role_data)

    logger.info("Exported %d roles", len(roles_data))
    return roles_data


def _role_tags(role: discord.Role) -> dict[str, Any] | None:
    if role.tags is None:
        return None
    tags: dict[str, Any] = {}
    if role.tags.bot_id:
        tags["bot_id"] = role.tags.bot_id
    if role.tags.integration_id:
        tags["integration_id"] = role.tags.integration_id
    if getattr(role.tags, "guild_connections", False) or getattr(role.tags, "is_guild_connection", False):
        tags["guild_connections"] = True
    if getattr(role.tags, "available_for_purchase", False) or getattr(role.tags, "is_available_for_purchase", False):
        tags["available_for_purchase"] = True
    if role.is_premium_subscriber():
        tags["premium_subscriber"] = True
    return tags if tags else None
