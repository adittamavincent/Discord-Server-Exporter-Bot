from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


async def generate_markdown(server_data: dict[str, Any], roles_data: list[dict[str, Any]], channels_data: dict[str, Any], members_data: list[dict[str, Any]], permissions_data: dict[str, Any], statistics_data: dict[str, Any], threads_data: list[dict[str, Any]], emojis_data: dict[str, Any], stickers_data: list[dict[str, Any]], automod_data: dict[str, Any], bots_data: dict[str, Any], invites_data: dict[str, Any]) -> str:
    lines: list[str] = []
    _add_line(lines, f"# Discord Server Export: {server_data.get('name', 'Unknown')}")
    _add_line(lines, f"*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*")
    _add_line(lines, "---")
    _add_line(lines)
    _add_line(lines, f"## Server Overview")
    _add_line(lines, f"- **Name:** {server_data.get('name', 'N/A')}")
    _add_line(lines, f"- **ID:** {server_data.get('id', 'N/A')}")
    _add_line(lines, f"- **Description:** {server_data.get('description', 'None')}")
    _add_line(lines, f"- **Owner ID:** {server_data.get('owner_id', 'N/A')}")
    _add_line(lines, f"- **Created:** {server_data.get('created_at', 'N/A')}")
    _add_line(lines, f"- **Verification Level:** {server_data.get('verification_level', 'N/A')}")
    _add_line(lines, f"- **MFA Level:** {server_data.get('mfa_level', 'N/A')}")
    _add_line(lines, f"- **NSFW Level:** {server_data.get('nsfw_level', 'N/A')}")
    _add_line(lines, f"- **Premium Tier:** {server_data.get('premium_tier', 0)}")
    _add_line(lines, f"- **Boost Count:** {server_data.get('boost_count', 0)}")
    _add_line(lines, f"- **Vanity URL:** {server_data.get('vanity_url', 'None')}")
    _add_line(lines, f"- **Community:** {'Yes' if server_data.get('is_community', False) else 'No'}")
    _add_line(lines, f"- **Verified:** {'Yes' if server_data.get('is_verified', False) else 'No'}")
    _add_line(lines, f"- **Partnered:** {'Yes' if server_data.get('is_partnered', False) else 'No'}")
    _add_line(lines, f"- **Features:** {', '.join(server_data.get('features', []))}")
    _add_line(lines)
    _add_line(lines, "## Statistics")
    _add_line(lines, f"- **Total Members:** {statistics_data.get('total_members', 0)}")
    _add_line(lines, f"- **Humans:** {statistics_data.get('total_humans', 0)}")
    _add_line(lines, f"- **Bots:** {statistics_data.get('total_bots', 0)} ({statistics_data.get('bot_percentage', 0)}%)")
    _add_line(lines, f"- **Total Roles:** {statistics_data.get('total_roles', 0)}")
    _add_line(lines, f"- **Total Channels:** {statistics_data.get('total_channels', 0)}")
    _add_line(lines, f"-  Text: {statistics_data.get('text_channels', 0)}")
    _add_line(lines, f"-  Voice: {statistics_data.get('voice_channels', 0)}")
    _add_line(lines, f"-  Forum: {statistics_data.get('forum_channels', 0)}")
    _add_line(lines, f"-  Stage: {statistics_data.get('stage_channels', 0)}")
    _add_line(lines, f"- **NSFW Channels:** {statistics_data.get('nsfw_channels', 0)}")
    _add_line(lines, f"- **Text:Voice Ratio:** {statistics_data.get('text_to_voice_ratio', 'N/A')}")
    _add_line(lines)
    _add_line(lines, "## Role Hierarchy")
    _add_line(lines)
    _add_line(lines, "| # | Role | Color | Members | Permissions | Hoist | Mentionable | Managed |")
    _add_line(lines, "|---|------|-------|---------|-------------|-------|-------------|---------|")

    admin_count = 0
    for role in reversed(roles_data):
        perms = role.get("permissions", {})
        perm_count = sum(1 for k, v in perms.items() if v and k != "value")
        is_admin = perms.get("administrator", False)
        if is_admin:
            admin_count += 1
        color_str = role.get("color_hex", "#000000")
        _add_line(lines, f"| {role.get('position', 0)} | {role.get('name', '')} | {color_str} | - | {perm_count} | {'Yes' if role.get('hoist') else 'No'} | {'Yes' if role.get('mentionable') else 'No'} | {'Yes' if role.get('managed') else 'No'} |")

    _add_line(lines)
    _add_line(lines, f"**Administrator Roles: {admin_count}**")
    _add_line(lines)
    _add_line(lines, "## Categories")
    _add_line(lines)
    for cat in channels_data.get("categories", []):
        _add_line(lines, f"### 📁 {cat.get('name', 'Unnamed')} (ID: {cat.get('id', 'N/A')})")
        cat_channels = [
            ch for ch_list in [
                channels_data.get("text_channels", []),
                channels_data.get("voice_channels", []),
                channels_data.get("forum_channels", []),
                channels_data.get("stage_channels", []),
                channels_data.get("announcement_channels", []),
            ]
            for ch in ch_list
            if ch.get("category_id") == cat.get("id")
        ]
        for ch in cat_channels:
            ch_type = ch.get("type", "unknown")
            icon = {"text": "#", "voice": "🔊", "forum": "💬", "stage": "🎤", "announcement": "📢"}.get(ch_type, "•")
            nsfw = " 🔞" if ch.get("nsfw") else ""
            topic = f" - {ch.get('topic', '')[:80]}" if ch.get("topic") else ""
            _add_line(lines, f"  - {icon} **{ch.get('name', '')}**{nsfw}{topic}")
        _add_line(lines)

    _add_line(lines, "## Uncategorized Channels")
    _add_line(lines)
    uncategorized = [
        ch for ch_list in [
            channels_data.get("text_channels", []),
            channels_data.get("voice_channels", []),
            channels_data.get("forum_channels", []),
            channels_data.get("stage_channels", []),
            channels_data.get("announcement_channels", []),
        ]
        for ch in ch_list
        if ch.get("category_id") is None
    ]
    if uncategorized:
        for ch in uncategorized:
            ch_type = ch.get("type", "unknown")
            icon = {"text": "#", "voice": "🔊", "forum": "💬", "stage": "🎤", "announcement": "📢"}.get(ch_type, "•")
            nsfw = " 🔞" if ch.get("nsfw") else ""
            topic = f" - {ch.get('topic', '')[:80]}" if ch.get("topic") else ""
            _add_line(lines, f"- {icon} **{ch.get('name', '')}**{nsfw}{topic}")
    else:
        _add_line(lines, "- All channels are categorized.")
    _add_line(lines)

    _add_line(lines, "## Threads")
    _add_line(lines)
    active_threads = [t for t in threads_data if not t.get("archived")]
    archived_threads = [t for t in threads_data if t.get("archived")]
    _add_line(lines, f"- **Active Threads:** {len(active_threads)}")
    _add_line(lines, f"- **Archived Threads:** {len(archived_threads)}")
    _add_line(lines, f"- **Total:** {len(threads_data)}")
    _add_line(lines)
    if active_threads:
        _add_line(lines, "### Active Threads")
        _add_line(lines, "| Name | Parent | Messages | Members |")
        _add_line(lines, "|------|--------|----------|---------|")
        for t in active_threads[:20]:
            _add_line(lines, f"| {t.get('name', '')} | {t.get('parent_name', 'N/A')} | {t.get('message_count', 0)} | {t.get('member_count', 0)} |")
        if len(active_threads) > 20:
            _add_line(lines, f"*... and {len(active_threads) - 20} more active threads*")
        _add_line(lines)

    _add_line(lines, "## Emojis")
    _add_line(lines, f"- **Total:** {emojis_data.get('total_emojis', 0)}")
    _add_line(lines, f"- **Animated:** {emojis_data.get('animated_emojis', 0)}")
    _add_line(lines, f"- **Static:** {emojis_data.get('static_emojis', 0)}")
    _add_line(lines, f"- **Limit:** {emojis_data.get('emoji_limit', 0)}")
    _add_line(lines)

    _add_line(lines, "## Stickers")
    _add_line(lines, f"- **Total:** {len(stickers_data)}")
    _add_line(lines)

    _add_line(lines, "## AutoMod Rules")
    _add_line(lines, f"- **Rules:** {automod_data.get('total_rules', 0)}")
    if automod_data.get("rules"):
        for rule in automod_data["rules"]:
            _add_line(lines, f"  - {rule.get('name', 'Unnamed')} ({'Enabled' if rule.get('enabled') else 'Disabled'})")
    _add_line(lines)

    _add_line(lines, "## Bots & Webhooks")
    _add_line(lines, f"- **Bots:** {bots_data.get('total_bots', 0)}")
    if bots_data.get("bots"):
        for bot in bots_data["bots"]:
            _add_line(lines, f"  - 🤖 {bot.get('name', 'Unnamed')} (ID: {bot.get('id', 'N/A')})")
    _add_line(lines, f"- **Webhooks:** {bots_data.get('total_webhooks', 0)}")
    _add_line(lines)

    _add_line(lines, "## Invites")
    _add_line(lines, f"- **Total Invites:** {invites_data.get('total_invites', 0)}")
    _add_line(lines, f"- **Total Uses:** {invites_data.get('total_uses', 0)}")
    _add_line(lines)

    _add_line(lines, "## Permissions Summary")
    _add_line(lines)
    _add_line(lines, f"- **Administrator Roles:** {permissions_data.get('total_admin_roles', 0)}")
    _add_line(lines, f"- **Roles with Permissions:** {permissions_data.get('total_roles_with_permissions', 0)}")
    _add_line(lines)
    if permissions_data.get("administrator_roles"):
        _add_line(lines, "### Roles with Administrator")
        for role_name in permissions_data["administrator_roles"]:
            _add_line(lines, f"- ⚠️ `{role_name}`")
    _add_line(lines)

    _add_line(lines, "## Potential Issues")
    _add_line(lines)
    issues = _find_issues(server_data, roles_data, channels_data, members_data, statistics_data, permissions_data, automod_data)
    if issues:
        for issue in issues:
            _add_line(lines, f"- ⚠️ {issue}")
    else:
        _add_line(lines, "- No significant issues detected.")
    _add_line(lines)

    _add_line(lines, "## Suggestions")
    _add_line(lines)
    suggestions = _find_suggestions(server_data, roles_data, channels_data, statistics_data, permissions_data, automod_data)
    if suggestions:
        for sug in suggestions:
            _add_line(lines, f"- 💡 {sug}")
    else:
        _add_line(lines, "- No suggestions at this time.")
    _add_line(lines)

    _add_line(lines, "---")
    _add_line(lines, f"*Export generated by Discord Server Exporter*")

    return "\n".join(lines)


def _find_issues(server_data: dict[str, Any], roles_data: list[dict[str, Any]], channels_data: dict[str, Any], members_data: list[dict[str, Any]], statistics_data: dict[str, Any], permissions_data: dict[str, Any], automod_data: dict[str, Any]) -> list[str]:
    issues: list[str] = []

    if server_data.get("verification_level") in ["none", "NONE"]:
        issues.append("Server has no verification level set - vulnerable to raids.")

    if not server_data.get("description"):
        issues.append("Server has no description set.")

    if not server_data.get("vanity_url") and server_data.get("is_community"):
        issues.append("Community server without a vanity URL.")

    admin_roles = permissions_data.get("administrator_roles", [])
    if len(admin_roles) > 3:
        issues.append(f"Too many roles with Administrator permission ({len(admin_roles)}). Consider reducing.")

    default_perms = permissions_data.get("default_permissions", {})
    if default_perms.get("send_messages", True) is False:
        issues.append("@everyone cannot send messages - server may be too restrictive.")
    if default_perms.get("read_messages", True) is False:
        issues.append("@everyone cannot read messages - server may be invisible to new users.")

    if not automod_data.get("has_automod"):
        issues.append("No AutoMod rules configured - server may be vulnerable to spam and raids.")

    nsfw_channels = statistics_data.get("nsfw_channels", 0)
    if nsfw_channels == 0 and server_data.get("nsfw_level") in ["safe", "SAFE"]:
        pass

    uncategorized = [
        ch for ch_list in [
            channels_data.get("text_channels", []),
            channels_data.get("voice_channels", []),
            channels_data.get("forum_channels", []),
            channels_data.get("stage_channels", []),
            channels_data.get("announcement_channels", []),
        ]
        for ch in ch_list
        if ch.get("category_id") is None
    ]
    if uncategorized:
        issues.append(f"{len(uncategorized)} channels are uncategorized.")

    roles_with_many_perms = [r for r in roles_data if len([k for k, v in r.get("permissions", {}).items() if v and k != "value"]) > 20]
    if roles_with_many_perms:
        for r in roles_with_many_perms[:3]:
            issues.append(f"Role '{r.get('name')}' has excessive permissions ({len([k for k, v in r.get('permissions', {}).items() if v and k != 'value'])} enabled).")

    return issues


def _find_suggestions(server_data: dict[str, Any], roles_data: list[dict[str, Any]], channels_data: dict[str, Any], statistics_data: dict[str, Any], permissions_data: dict[str, Any], automod_data: dict[str, Any]) -> list[str]:
    suggestions: list[str] = []

    if not server_data.get("description"):
        suggestions.append("Add a server description to help users understand the community.")

    if not server_data.get("is_community"):
        suggestions.append("Enable Community features for better moderation tools and organization.")

    if statistics_data.get("total_forum", 0) == 0 and statistics_data.get("total_members", 0) > 100:
        suggestions.append("Consider adding forum channels for Q&A and discussions.")

    if statistics_data.get("total_stage", 0) == 0:
        suggestions.append("Stage channels enable voice discussions and events - consider adding one.")

    if not automod_data.get("has_automod"):
        suggestions.append("Configure AutoMod rules to filter spam, unwanted content, and mentions.")

    text_count = statistics_data.get("text_channels", 0)
    voice_count = statistics_data.get("voice_channels", 0)
    if voice_count == 0 and text_count > 0:
        suggestions.append("No voice channels found - consider adding voice channels for community engagement.")

    total_categories = channels_data.get("total_categories", 0)
    if total_categories == 0 and statistics_data.get("total_channels", 0) > 5:
        suggestions.append("Channels are not organized into categories - consider grouping them.")

    member_count = statistics_data.get("total_members", 0)
    bot_count = statistics_data.get("total_bots", 0)
    if bot_count == 0 and member_count > 50:
        suggestions.append("No bots detected - consider adding moderation, music, or utility bots.")

    admin_roles = permissions_data.get("administrator_roles", [])
    if not admin_roles:
        suggestions.append("No roles with Administrator permission - this may be intentional but verify.")

    if statistics_data.get("text_to_voice_ratio", 0) != float("inf") and statistics_data.get("text_to_voice_ratio", 0) > 10:
        suggestions.append("Very high text-to-voice ratio - consider adding more voice channels.")

    return suggestions


def _add_line(lines: list[str], content: str = "") -> None:
    lines.append(content)
