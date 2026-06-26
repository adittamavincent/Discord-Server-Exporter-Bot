from __future__ import annotations

import logging
from typing import Any

import discord

logger = logging.getLogger(__name__)


async def export_automod(guild: discord.Guild) -> dict[str, Any]:
    rules_data: list[dict[str, Any]] = []

    try:
        if not hasattr(guild, "fetch_auto_moderation_rules"):
            logger.warning("AutoMod API not available in this discord.py version")
            return {"total_rules": 0, "rules": [], "note": "AutoMod API not available"}

        rules = await guild.fetch_auto_moderation_rules()
        for rule in rules:
            rule_data = {
                "id": rule.id,
                "name": rule.name,
                "enabled": rule.enabled,
                "event_type": str(rule.event_type),
                "trigger_type": str(rule.trigger_type),
                "trigger_metadata": _trigger_metadata(rule),
                "actions": _rule_actions(rule),
                "exempt_roles": [{"id": r.id, "name": r.name} for r in rule.exempt_roles],
                "exempt_channels": [{"id": c.id, "name": c.name} for c in rule.exempt_channels],
                "creator_id": rule.creator_id,
            }
            rules_data.append(rule_data)
    except discord.Forbidden:
        logger.warning("No permission to fetch AutoMod rules")
    except discord.HTTPException as e:
        logger.warning("Failed to fetch AutoMod rules: %s", e)
    except Exception as e:
        logger.warning("Unexpected error fetching AutoMod rules: %s", e)

    data = {
        "total_rules": len(rules_data),
        "rules": rules_data,
        "has_automod": len(rules_data) > 0,
    }

    logger.info("Exported %d AutoMod rules", len(rules_data))
    return data


def _trigger_metadata(rule: Any) -> dict[str, Any]:
    try:
        meta = rule.trigger_metadata
        if meta is None:
            return {}
        return {
            "keyword_filter": list(meta.keyword_filter) if hasattr(meta, "keyword_filter") else [],
            "regex_patterns": list(meta.regex_patterns) if hasattr(meta, "regex_patterns") else [],
            "mention_total_limit": meta.mention_total_limit if hasattr(meta, "mention_total_limit") else None,
            "mention_raid_protection_enabled": meta.mention_raid_protection_enabled if hasattr(meta, "mention_raid_protection_enabled") else None,
            "presets": list(meta.presets) if hasattr(meta, "presets") else [],
            "allow_list": list(meta.allow_list) if hasattr(meta, "allow_list") else [],
        }
    except Exception:
        return {}


def _rule_actions(rule: Any) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    try:
        for action in rule.actions:
            action_data: dict[str, Any] = {
                "type": str(action.type),
            }
            if hasattr(action, "metadata") and action.metadata:
                meta = action.metadata
                meta_data: dict[str, Any] = {}
                if hasattr(meta, "channel_id") and meta.channel_id:
                    meta_data["channel_id"] = meta.channel_id
                if hasattr(meta, "duration_seconds") and meta.duration_seconds:
                    meta_data["duration_seconds"] = meta.duration_seconds
                if hasattr(meta, "custom_message") and meta.custom_message:
                    meta_data["custom_message"] = meta.custom_message
                if meta_data:
                    action_data["metadata"] = meta_data
            actions.append(action_data)
    except Exception:
        pass
    return actions
