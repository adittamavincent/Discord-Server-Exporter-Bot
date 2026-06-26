from __future__ import annotations

import logging
from typing import Any

import discord

from exporter.utils import permissions_to_dict

logger = logging.getLogger(__name__)


async def export_permissions(guild: discord.Guild) -> dict[str, Any]:
    roles = sorted(guild.roles, key=lambda r: r.position, reverse=True)

    permission_matrix: dict[str, dict[str, bool]] = {}
    for role in roles:
        role_perms = permissions_to_dict(role.permissions)
        permission_matrix[role.name] = role_perms
        for perm_name in list(role_perms.keys()):
            if isinstance(role_perms[perm_name], bool):
                continue

    role_permissions_flat: list[dict[str, Any]] = []
    for role in roles:
        perms = permissions_to_dict(role.permissions)
        enabled = [k for k, v in perms.items() if v and k != "value"]
        disabled = [k for k, v in perms.items() if not v and k != "value"]
        role_permissions_flat.append({
            "role_id": role.id,
            "role_name": role.name,
            "role_position": role.position,
            "enabled_permissions": enabled,
            "disabled_permissions": disabled,
            "permissions_bitfield": role.permissions.value,
        })

    admin_roles = [
        r.name for r in roles
        if r.permissions.administrator and not r.managed
    ]

    all_perms = set()
    for r in roles:
        for perm_name in permissions_to_dict(r.permissions):
            if perm_name != "value":
                all_perms.add(perm_name)

    data = {
        "permission_matrix": permission_matrix,
        "role_permissions": role_permissions_flat,
        "administrator_roles": admin_roles,
        "total_admin_roles": len(admin_roles),
        "total_roles_with_permissions": len(role_permissions_flat),
        "unique_permissions": sorted(all_perms),
        "guild_permissions_bitfield": guild.default_role.permissions.value,
        "default_permissions": permissions_to_dict(guild.default_role.permissions),
    }

    logger.info("Exported permissions for %d roles", len(role_permissions_flat))
    return data
