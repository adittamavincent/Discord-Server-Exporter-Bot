from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import timestamp_to_iso

logger = logging.getLogger(__name__)


async def export_invites(guild: discord.Guild) -> dict[str, Any]:
    invites_data: list[dict[str, Any]] = []

    try:
        invites = await guild.invites()
        for invite in invites:
            invite_entry = {
                "code": invite.code,
                "url": invite.url,
                "channel_id": invite.channel.id if invite.channel else None,
                "channel_name": invite.channel.name if invite.channel else None,
                "inviter_id": invite.inviter.id if invite.inviter else None,
                "inviter_name": invite.inviter.name if invite.inviter else None,
                "uses": invite.uses,
                "max_uses": invite.max_uses,
                "max_age": invite.max_age,
                "temporary": invite.temporary,
                "created_at": timestamp_to_iso(invite.created_at) if hasattr(invite, "created_at") else None,
                "expires_at": timestamp_to_iso(invite.expires_at) if hasattr(invite, "expires_at") and invite.expires_at else None,
                "is_revoked": getattr(invite, "revoked", False),
            }
            invites_data.append(invite_entry)
    except discord.Forbidden:
        logger.warning("No permission to fetch invites")
    except discord.HTTPException as e:
        logger.warning("Failed to fetch invites: %s", e)

    total_uses = sum(i.get("uses", 0) for i in invites_data)

    data = {
        "total_invites": len(invites_data),
        "total_uses": total_uses,
        "invites": invites_data,
    }

    logger.info("Exported %d invites", len(invites_data))
    return data
