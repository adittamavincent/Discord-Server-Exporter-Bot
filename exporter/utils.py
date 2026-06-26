from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

import discord


def sanitize_filename(name: str, max_len: int = 64) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", name).strip()
    cleaned = re.sub(r"[-\s]+", "_", cleaned)
    return cleaned[:max_len].rstrip("_")


def timestamp_to_iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def permissions_to_dict(permissions: discord.Permissions) -> dict[str, bool]:
    return {
        "add_reactions": permissions.add_reactions,
        "administrator": permissions.administrator,
        "attach_files": permissions.attach_files,
        "ban_members": permissions.ban_members,
        "change_nickname": permissions.change_nickname,
        "connect": permissions.connect,
        "create_events": getattr(permissions, "create_events", False),
        "create_expressions": getattr(permissions, "create_expressions", False),
        "create_instant_invite": permissions.create_instant_invite,
        "create_private_threads": permissions.create_private_threads,
        "create_public_threads": permissions.create_public_threads,
        "deafen_members": permissions.deafen_members,
        "embed_links": permissions.embed_links,
        "external_emails": getattr(permissions, "external_emails", False),
        "external_emojis": permissions.external_emojis,
        "external_stickers": permissions.external_stickers,
        "kick_members": permissions.kick_members,
        "manage_channels": permissions.manage_channels,
        "manage_events": getattr(permissions, "manage_events", False),
        "manage_expressions": getattr(permissions, "manage_expressions", False),
        "manage_guild": permissions.manage_guild,
        "manage_messages": permissions.manage_messages,
        "manage_nicknames": permissions.manage_nicknames,
        "manage_permissions": getattr(permissions, "manage_permissions", False),
        "manage_roles": permissions.manage_roles,
        "manage_threads": permissions.manage_threads,
        "manage_webhooks": permissions.manage_webhooks,
        "mention_everyone": permissions.mention_everyone,
        "moderate_members": permissions.moderate_members,
        "move_members": permissions.move_members,
        "mute_members": permissions.mute_members,
        "priority_speaker": permissions.priority_speaker,
        "read_message_history": permissions.read_message_history,
        "read_messages": permissions.read_messages,
        "request_to_speak": permissions.request_to_speak,
        "send_messages": permissions.send_messages,
        "send_messages_in_threads": permissions.send_messages_in_threads,
        "send_tts_messages": permissions.send_tts_messages,
        "send_voice_messages": getattr(permissions, "send_voice_messages", False),
        "speak": permissions.speak,
        "stream": permissions.stream,
        "use_application_commands": getattr(permissions, "use_application_commands", False),
        "use_embedded_activities": getattr(permissions, "use_embedded_activities", False),
        "use_external_apps": getattr(permissions, "use_external_apps", False),
        "use_external_sounds": getattr(permissions, "use_external_sounds", False),
        "use_external_stickers": getattr(permissions, "use_external_stickers", False),
        "use_soundboard": getattr(permissions, "use_soundboard", False),
        "use_voice_activation": permissions.use_voice_activation,
        "value": permissions.value,
        "view_audit_log": permissions.view_audit_log,
        "view_channel": permissions.view_channel,
        "view_creator_monetization_analytics": getattr(
            permissions, "view_creator_monetization_analytics", False
        ),
        "view_guild_insights": permissions.view_guild_insights,
    }


def overwrite_to_dict(
    target: discord.abc.GuildChannel | discord.Role | discord.Member,
    overwrite: discord.PermissionOverwrite,
) -> dict[str, Any]:
    allow = overwrite.pair()[0]
    deny = overwrite.pair()[1]
    return {
        "target_id": target.id,
        "target_name": getattr(target, "name", str(target)),
        "target_type": type(target).__name__,
        "allow": permissions_to_dict(allow),
        "deny": permissions_to_dict(deny),
    }


def dict_to_json_safe(obj: Any, max_depth: int = 10) -> Any:
    if max_depth < 0:
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): dict_to_json_safe(v, max_depth - 1) for k, v in obj.items()}
    if isinstance(obj, list):
        return [dict_to_json_safe(item, max_depth - 1) for item in obj]
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if obj is None:
        return None
    if isinstance(obj, datetime):
        return timestamp_to_iso(obj)
    if isinstance(obj, discord.Permissions):
        return permissions_to_dict(obj)
    if isinstance(obj, discord.PermissionOverwrite):
        allow, deny = obj.pair()
        return {"allow": permissions_to_dict(allow), "deny": permissions_to_dict(deny)}
    if hasattr(obj, "to_dict"):
        try:
            return dict_to_json_safe(obj.to_dict(), max_depth - 1)
        except Exception:
            return str(obj)
    try:
        return str(obj)
    except Exception:
        return repr(obj)


LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
