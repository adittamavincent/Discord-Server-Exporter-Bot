from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import timestamp_to_iso

logger = logging.getLogger(__name__)


async def export_members(
    guild: discord.Guild,
    max_members: int = 1000,
) -> list[dict[str, Any]]:
    members: list[discord.Member] = []
    async for member in guild.fetch_members(limit=max_members):
        members.append(member)

    members_data: list[dict[str, Any]] = []
    for member in members:
        member_data = {
            "id": member.id,
            "name": member.name,
            "global_name": member.global_name,
            "display_name": member.display_name,
            "nick": member.nick,
            "discriminator": member.discriminator,
            "bot": member.bot,
            "system": member.system,
            "avatar_url": member.avatar.url if member.avatar else None,
            "banner_url": member.banner.url if member.banner else None,
            "accent_color": member.accent_color.value if member.accent_color else None,
            "created_at": timestamp_to_iso(member.created_at),
            "joined_at": timestamp_to_iso(member.joined_at),
            "premium_since": timestamp_to_iso(member.premium_since) if member.premium_since else None,
            "roles": [{"id": r.id, "name": r.name} for r in member.roles if r != guild.default_role],
            "role_ids": [r.id for r in member.roles if r != guild.default_role],
            "top_role": {"id": member.top_role.id, "name": member.top_role.name},
            "top_role_position": member.top_role.position,
            "pending": member.pending,
            "timed_out_until": timestamp_to_iso(member.timed_out_until) if member.timed_out_until else None,
            "communication_disabled_until": timestamp_to_iso(member.communication_disabled_until) if hasattr(member, "communication_disabled_until") and member.communication_disabled_until else None,
            "flags": _member_flags(member),
            "is_owner": member.id == guild.owner_id,
        }
        members_data.append(member_data)

    logger.info(
        "Exported %d members (requested max: %d)",
        len(members_data),
        max_members,
    )
    return members_data


def _member_flags(member: discord.Member) -> list[str]:
    flags: list[str] = []
    try:
        if member.flags:
            if member.flags.did_rejoin:
                flags.append("did_rejoin")
            if member.flags.completed_onboarding:
                flags.append("completed_onboarding")
            if member.flags.bypasses_verification:
                flags.append("bypasses_verification")
            if member.flags.started_onboarding:
                flags.append("started_onboarding")
    except Exception:
        pass
    return flags
