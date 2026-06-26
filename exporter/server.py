from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import timestamp_to_iso

logger = logging.getLogger(__name__)


async def export_server(guild: discord.Guild) -> dict[str, Any]:
    data = {
        "id": guild.id,
        "name": guild.name,
        "description": guild.description,
        "icon_url": guild.icon.url if guild.icon else None,
        "icon_hash": str(guild.icon) if guild.icon else None,
        "splash_url": guild.splash.url if guild.splash else None,
        "banner_url": guild.banner.url if guild.banner else None,
        "vanity_url": guild.vanity_url,
        "vanity_url_code": guild.vanity_url_code,
        "features": list(guild.features),
        "verification_level": str(guild.verification_level),
        "mfa_level": str(guild.mfa_level),
        "nsfw_level": str(guild.nsfw_level),
        "preferred_locale": str(guild.preferred_locale) if guild.preferred_locale else None,
        "premium_tier": guild.premium_tier,
        "premium_subscription_count": guild.premium_subscription_count,
        "boost_count": guild.premium_subscription_count,
        "boost_progress": _boost_progress(guild),
        "approximate_member_count": guild.approximate_member_count,
        "approximate_presence_count": guild.approximate_presence_count,
        "member_count": guild.member_count,
        "large": guild.large,
        "max_members": guild.max_members,
        "max_presences": guild.max_presences,
        "max_video_channel_users": guild.max_video_channel_users,
        "max_stage_video_users": getattr(guild, "max_stage_video_users", None),
        "owner_id": guild.owner_id,
        "rules_channel_id": guild.rules_channel.id if guild.rules_channel else None,
        "public_updates_channel_id": guild.public_updates_channel.id if guild.public_updates_channel else None,
        "safety_alerts_channel_id": guild.safety_alerts_channel.id if guild.safety_alerts_channel else None,
        "system_channel_id": guild.system_channel.id if guild.system_channel else None,
        "system_channel_flags": _system_channel_flags(guild),
        "afk_channel_id": guild.afk_channel.id if guild.afk_channel else None,
        "afk_timeout": guild.afk_timeout,
        "widget_enabled": guild.widget_enabled,
        "widget_channel_id": guild.widget_channel.id if guild.widget_channel else None,
        "explicit_content_filter": str(guild.explicit_content_filter),
        "default_notifications": str(guild.default_notifications),
        "premium_progress_bar_enabled": guild.premium_progress_bar_enabled,
        "created_at": timestamp_to_iso(guild.created_at),
        "is_community": "COMMUNITY" in guild.features,
        "is_discoverable": "DISCOVERABLE" in guild.features,
        "is_verified": "VERIFIED" in guild.features,
        "is_partnered": "PARTNERED" in guild.features,
    }

    logger.info("Exported server: %s (%s)", guild.name, guild.id)
    return data


def _boost_progress(guild: discord.Guild) -> dict[str, Any] | None:
    try:
        return {
            "tier_1": guild.premium_progress_bar_enabled,
            "current_boosts": guild.premium_subscription_count,
        }
    except Exception:
        return None


def _system_channel_flags(guild: discord.Guild) -> list[str]:
    flags: list[str] = []
    try:
        if guild.system_channel_flags:
            if guild.system_channel_flags.join_notifications:
                flags.append("join_notifications")
            if guild.system_channel_flags.premium_subscriptions:
                flags.append("premium_subscriptions")
            if guild.system_channel_flags.guild_reminder_notifications:
                flags.append("reminder_notifications")
            if guild.system_channel_flags.join_notification_replies:
                flags.append("join_notification_replies")
            if guild.system_channel_flags.role_subscription_purchase_notifications:
                flags.append("role_subscription_purchase")
            if guild.system_channel_flags.role_subscription_purchase_notification_replies:
                flags.append("role_subscription_purchase_replies")
    except Exception:
        pass
    return flags
