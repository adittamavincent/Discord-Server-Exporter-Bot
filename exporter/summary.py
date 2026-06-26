from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


async def generate_summary(server_data: dict[str, Any], roles_data: list[dict[str, Any]], channels_data: dict[str, Any], members_data: list[dict[str, Any]], permissions_data: dict[str, Any], statistics_data: dict[str, Any], automod_data: dict[str, Any]) -> str:
    lines: list[str] = []
    score = _calculate_health_score(server_data, roles_data, channels_data, members_data, permissions_data, statistics_data, automod_data)

    _add_line(lines, "=" * 60)
    _add_line(lines, "AI SUMMARY - DISCORD SERVER ANALYSIS")
    _add_line(lines, "=" * 60)
    _add_line(lines, f"Server: {server_data.get('name', 'Unknown')}")
    _add_line(lines, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    _add_line(lines, f"Overall Health Score: {score['health_score']}/100")
    _add_line(lines, f"Risk Level: {score['risk_level']}")
    _add_line(lines, "=" * 60)
    _add_line(lines)

    _add_line(lines, "--- OVERALL HEALTH ---")
    _add_line(lines, f"Score: {score['health_score']}/100 - {score['risk_level']}")
    _add_line(lines)

    _add_line(lines, "--- ORGANIZATION ---")
    org_score = score.get("organization", 50)
    _add_line(lines, f"Score: {org_score}/100")
    _add_line(lines, f"Categories: {channels_data.get('total_categories', 0)}")
    _add_line(lines, f"Total Channels: {statistics_data.get('total_channels', 0)}")
    _add_line(lines, f"Uncategorized Channels: {_count_uncategorized(channels_data)}")
    _add_line(lines, f"Text:Voice Ratio: {statistics_data.get('text_to_voice_ratio', 'N/A')}")
    _add_line(lines)

    _add_line(lines, "--- SECURITY ---")
    sec_score = score.get("security", 50)
    _add_line(lines, f"Score: {sec_score}/100")
    _add_line(lines, f"Verification Level: {server_data.get('verification_level', 'N/A')}")
    _add_line(lines, f"MFA Level: {server_data.get('mfa_level', 'N/A')}")
    _add_line(lines, f"NSFW Level: {server_data.get('nsfw_level', 'N/A')}")
    _add_line(lines, f"Explicit Content Filter: {server_data.get('explicit_content_filter', 'N/A')}")
    _add_line(lines, f"AutoMod Rules: {automod_data.get('total_rules', 0)}")
    _add_line(lines)

    _add_line(lines, "--- PERMISSIONS ---")
    perm_score = score.get("permissions", 50)
    _add_line(lines, f"Score: {perm_score}/100")
    _add_line(lines, f"Total Roles: {statistics_data.get('total_roles', 0)}")
    _add_line(lines, f"Administrator Roles: {permissions_data.get('total_admin_roles', 0)}")
    _add_line(lines, f"Roles with Hoist: {statistics_data.get('hoisted_roles', 0)}")
    _add_line(lines, f"Managed Roles: {statistics_data.get('managed_roles', 0)}")
    _add_line(lines)

    _add_line(lines, "--- MODERATION ---")
    mod_score = score.get("moderation", 50)
    _add_line(lines, f"Score: {mod_score}/100")
    _add_line(lines, f"AutoMod: {'Configured' if automod_data.get('has_automod') else 'Not configured'}")
    _add_line(lines, f"NSFW Channels: {statistics_data.get('nsfw_channels', 0)}")
    _add_line(lines, f"Timeout Users: {_count_timed_out(members_data)}")
    _add_line(lines)

    _add_line(lines, "--- COMMUNITY STRUCTURE ---")
    com_score = score.get("community", 50)
    _add_line(lines, f"Score: {com_score}/100")
    _add_line(lines, f"Total Members: {statistics_data.get('total_members', 0)}")
    _add_line(lines, f"Humans: {statistics_data.get('total_humans', 0)}")
    _add_line(lines, f"Bots: {statistics_data.get('total_bots', 0)} ({statistics_data.get('bot_percentage', 0)}%)")
    _add_line(lines, f"Boost Count: {statistics_data.get('boost_count', 0)}")
    _add_line(lines, f"Boost Tier: {statistics_data.get('boost_tier', 0)}")
    _add_line(lines, f"Is Community: {'Yes' if server_data.get('is_community', False) else 'No'}")
    _add_line(lines)

    _add_line(lines, "--- SCALABILITY ---")
    scal_score = score.get("scalability", 50)
    _add_line(lines, f"Score: {scal_score}/100")
    _add_line(lines, f"Members per Channel: {statistics_data.get('members_per_channel', 0)}")
    _add_line(lines, f"Role Count: {statistics_data.get('total_roles', 0)}")
    _add_line(lines, f"Bot Percentage: {statistics_data.get('bot_percentage', 0)}%")
    _add_line(lines)

    _add_line(lines, "--- DETECTED ISSUES ---")
    issues = _collect_issues(server_data, roles_data, channels_data, members_data, permissions_data, statistics_data, automod_data)
    if issues:
        for i, issue in enumerate(issues, 1):
            _add_line(lines, f"{i}. {issue}")
    else:
        _add_line(lines, "No significant issues detected.")
    _add_line(lines)

    _add_line(lines, "--- RECOMMENDATIONS ---")
    recommendations = _collect_recommendations(server_data, statistics_data, permissions_data, automod_data, channels_data)
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            _add_line(lines, f"{i}. {rec}")
    _add_line(lines)

    _add_line(lines, "=" * 60)
    _add_line(lines, "END OF AI SUMMARY")
    _add_line(lines, "=" * 60)

    return "\n".join(lines)


def _calculate_health_score(server_data: dict[str, Any], roles_data: list[dict[str, Any]], channels_data: dict[str, Any], members_data: list[dict[str, Any]], permissions_data: dict[str, Any], statistics_data: dict[str, Any], automod_data: dict[str, Any]) -> dict[str, Any]:
    org_score = 0
    total_cats = channels_data.get("total_categories", 0)
    total_channels = statistics_data.get("total_channels", 0)
    uncategorized = _count_uncategorized(channels_data)

    if total_cats >= 3:
        org_score += 40
    elif total_cats >= 1:
        org_score += 20
    if uncategorized == 0 and total_channels > 0:
        org_score += 30
    elif uncategorized <= total_channels * 0.2:
        org_score += 15
    if total_channels >= 5:
        org_score += 30
    elif total_channels >= 3:
        org_score += 15

    sec_score = 0
    vl = str(server_data.get("verification_level", "")).lower()
    if vl in ["high", "very_high"]:
        sec_score += 35
    elif vl == "medium":
        sec_score += 25
    elif vl == "low":
        sec_score += 15
    if automod_data.get("has_automod"):
        sec_score += 35
    if server_data.get("mfa_level") and "HIGH" in str(server_data.get("mfa_level", "")).upper():
        sec_score += 30

    perm_score = 0
    admin_roles = permissions_data.get("total_admin_roles", 0)
    if admin_roles == 0:
        perm_score += 30
    elif admin_roles <= 2:
        perm_score += 20
    elif admin_roles <= 5:
        perm_score += 10
    total_roles = statistics_data.get("total_roles", 0)
    if 5 <= total_roles <= 15:
        perm_score += 30
    elif total_roles < 5:
        perm_score += 15
    else:
        perm_score += 10
    default_perms = permissions_data.get("default_permissions", {})
    if not default_perms.get("administrator", False):
        perm_score += 40

    mod_score = 0
    if automod_data.get("has_automod"):
        mod_score += 40
    if server_data.get("explicit_content_filter") and "ALL_MEMBERS" in str(server_data.get("explicit_content_filter", "")).upper():
        mod_score += 30
    elif server_data.get("explicit_content_filter") and "MEMBERS_WITHOUT_ROLES" in str(server_data.get("explicit_content_filter", "")).upper():
        mod_score += 15
    if statistics_data.get("nsfw_channels", 0) > 0:
        mod_score += 30

    com_score = 0
    member_count = statistics_data.get("total_members", 0)
    if member_count >= 100:
        com_score += 25
    elif member_count >= 50:
        com_score += 15
    elif member_count >= 10:
        com_score += 5
    if statistics_data.get("boost_count", 0) >= 1:
        com_score += 20
    if server_data.get("is_community", False):
        com_score += 25
    if statistics_data.get("total_forum", 0) > 0:
        com_score += 15
    if statistics_data.get("total_stage", 0) > 0:
        com_score += 15

    scal_score = 0
    if statistics_data.get("members_per_channel", 0) <= 50:
        scal_score += 30
    elif statistics_data.get("members_per_channel", 0) <= 100:
        scal_score += 15
    bot_pct = statistics_data.get("bot_percentage", 0)
    if bot_pct <= 20:
        scal_score += 35
    elif bot_pct <= 40:
        scal_score += 20
    if total_channels <= 50:
        scal_score += 35
    elif total_channels <= 100:
        scal_score += 20

    health_score = int((org_score + sec_score + perm_score + mod_score + com_score + scal_score) / 6)

    if health_score >= 80:
        risk = "Low"
    elif health_score >= 50:
        risk = "Medium"
    else:
        risk = "High"

    return {
        "health_score": health_score,
        "risk_level": risk,
        "organization": org_score,
        "security": sec_score,
        "permissions": perm_score,
        "moderation": mod_score,
        "community": com_score,
        "scalability": scal_score,
    }


def _count_uncategorized(channels_data: dict[str, Any]) -> int:
    count = 0
    for ch_list_key in ["text_channels", "voice_channels", "forum_channels", "stage_channels", "announcement_channels"]:
        for ch in channels_data.get(ch_list_key, []):
            if ch.get("category_id") is None:
                count += 1
    return count


def _count_timed_out(members_data: list[dict[str, Any]]) -> int:
    return sum(1 for m in members_data if m.get("timed_out_until") or m.get("communication_disabled_until"))


def _collect_issues(server_data: dict[str, Any], roles_data: list[dict[str, Any]], channels_data: dict[str, Any], members_data: list[dict[str, Any]], permissions_data: dict[str, Any], statistics_data: dict[str, Any], automod_data: dict[str, Any]) -> list[str]:
    issues: list[str] = []

    if str(server_data.get("verification_level", "")).lower() in ["none"]:
        issues.append("CRITICAL: No verification level - server is vulnerable to raids.")

    if not server_data.get("description"):
        issues.append("LOW: No server description.")

    admin_roles = permissions_data.get("total_admin_roles", 0)
    if admin_roles > 5:
        issues.append(f"CRITICAL: {admin_roles} roles have Administrator - excessive.")

    if not automod_data.get("has_automod"):
        issues.append("HIGH: No AutoMod rules configured.")

    if _count_uncategorized(channels_data) > 5:
        issues.append(f"MEDIUM: {_count_uncategorized(channels_data)} channels are uncategorized.")

    timed_out = _count_timed_out(members_data)
    if timed_out > 5:
        issues.append(f"INFO: {timed_out} members currently timed out.")

    default_perms = permissions_data.get("default_permissions", {})
    if default_perms.get("administrator", False):
        issues.append("CRITICAL: @everyone has Administrator permission!")

    return issues


def _collect_recommendations(server_data: dict[str, Any], statistics_data: dict[str, Any], permissions_data: dict[str, Any], automod_data: dict[str, Any], channels_data: dict[str, Any]) -> list[str]:
    recs: list[str] = []

    if not server_data.get("description"):
        recs.append("Add a server description to improve discoverability.")

    if not server_data.get("is_community"):
        recs.append("Enable Community features for better moderation and organization.")

    if statistics_data.get("total_forum", 0) == 0 and statistics_data.get("total_members", 0) > 50:
        recs.append("Add forum channels to encourage structured discussions.")

    if not automod_data.get("has_automod"):
        recs.append("Configure AutoMod to filter spam and unwanted content.")

    if _count_uncategorized(channels_data) > 3:
        recs.append("Organize uncategorized channels into categories.")

    if statistics_data.get("total_stage", 0) == 0:
        recs.append("Consider adding stage channels for voice events.")

    return recs


def _add_line(lines: list[str], content: str = "") -> None:
    lines.append(content)
