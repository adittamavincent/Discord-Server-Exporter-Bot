#!/usr/bin/env python3
"""
Discord Server Exporter - Export every piece of Discord server information
into structured JSON files, Markdown reports, and AI-ready summaries.

Usage:
    python export.py
    python export.py --guild 123456789
    python export.py --guild 123456789 --output ./exports
    python export.py --no-zip --no-markdown --no-summary
"""

from __future__ import annotations

import asyncio
import logging
import sys
import traceback
from pathlib import Path
from typing import Any

try:
    import orjson
except ImportError:
    orjson = None

try:
    import rich
    from rich.console import Console
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TextColumn,
        TimeRemainingColumn,
    )
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from config import Config, ConfigError
from exporter.client import DiscordClient
from exporter.server import export_server
from exporter.roles import export_roles
from exporter.channels import export_channels
from exporter.members import export_members
from exporter.permissions import export_permissions
from exporter.statistics import export_statistics
from exporter.threads import export_threads
from exporter.forums import export_forums
from exporter.voice import export_voice
from exporter.stage import export_stage
from exporter.stickers import export_stickers
from exporter.emojis import export_emojis
from exporter.automod import export_automod
from exporter.bots import export_bots
from exporter.invites import export_invites
from exporter.markdown import generate_markdown
from exporter.summary import generate_summary
from exporter.ai_prompt import generate_ai_prompt
from exporter.zipper import create_zip
from exporter.utils import LOG_FORMAT, dict_to_json_safe


console = Console() if RICH_AVAILABLE else None
logger = logging.getLogger("export")


def setup_logging(config: Config) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if config.log_file:
        log_path = Path(config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))

    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format=LOG_FORMAT,
        handlers=handlers,
    )


def log_status(message: str, status: str = "info") -> None:
    if RICH_AVAILABLE and console:
        style = {
            "info": "bold cyan",
            "success": "bold green",
            "error": "bold red",
            "warning": "bold yellow",
        }.get(status, "bold cyan")
        icon = {
            "info": "ℹ",
            "success": "✔",
            "error": "✘",
            "warning": "⚠",
        }.get(status, "ℹ")
        console.print(f"  {icon} {message}", style=style)
    else:
        level_map = {
            "info": logging.INFO,
            "success": logging.INFO,
            "error": logging.ERROR,
            "warning": logging.WARNING,
        }
        logger.log(level_map.get(status, logging.INFO), "%s", message)


def parse_args() -> Any:
    """Simple argument parser without external dependencies."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Discord Server Exporter - Export Discord server data to structured files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python export.py
  python export.py --guild 123456789
  python export.py --guild 123456789 --output ./exports --no-zip
  python export.py --env .env.production --log-file export.log
        """,
    )
    parser.add_argument(
        "--guild",
        type=int,
        default=None,
        help="Guild/server ID to export (uses first available guild if not specified).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory (default: ./output).",
    )
    parser.add_argument(
        "--env",
        type=str,
        default=None,
        help="Path to .env file.",
    )
    parser.add_argument(
        "--max-members",
        type=int,
        default=None,
        help="Maximum members to fetch (default: 1000).",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Path to log file.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO).",
    )
    parser.add_argument(
        "--no-zip",
        action="store_true",
        help="Skip ZIP archive creation.",
    )
    parser.add_argument(
        "--no-markdown",
        action="store_true",
        help="Skip Markdown report generation.",
    )
    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Skip AI summary generation.",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Skip AI prompt generation.",
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=None,
        help="Delay between API requests in seconds (default: 0.5).",
    )
    return parser.parse_args()


async def run_export(config: Config) -> int:
    log_status("Connecting to Discord...", "info")

    client = DiscordClient(config=config)

    try:
        await client.login(config.token)
    except discord.LoginFailure:
        log_status("Invalid Discord bot token.", "error")
        logger.error("Login failed: invalid token")
        return 1
    except Exception as e:
        log_status(f"Failed to login: {e}", "error")
        logger.error("Login failed: %s", traceback.format_exc())
        return 1

    connect_task = asyncio.create_task(client.connect())

    exit_code = 1
    try:
        try:
            await client.wait_until_ready()
        except Exception as e:
            log_status(f"Failed to connect: {e}", "error")
            logger.error("Connection failed: %s", traceback.format_exc())
            return 1

        log_status("Connected", "success")

        try:
            guild_data = await client.fetch_guild_data(config.guild_id)
        except discord.Forbidden:
            log_status("No permission to access the guild.", "error")
            return 1
        except discord.HTTPException as e:
            log_status(f"Failed to fetch guild: {e}", "error")
            return 1

        if guild_data is None:
            log_status("Bot is not in any guilds.", "error")
            return 1

        guild = guild_data["guild"]
        guild_id = guild_data["guild_id"]

        log_status(f"Exporting server: {guild.name} (ID: {guild_id})", "info")

        all_data: dict[str, Any] = {}

        try:
            all_data["server"] = await export_server(guild)
            log_status("Exported server metadata", "success")
        except Exception as e:
            log_status(f"Failed to export server: {e}", "error")
            logger.error("Server export failed: %s", traceback.format_exc())

        try:
            all_data["roles"] = await export_roles(guild)
            log_status(f"Exported {len(all_data['roles'])} roles", "success")
        except Exception as e:
            log_status(f"Failed to export roles: {e}", "error")
            logger.error("Roles export failed: %s", traceback.format_exc())
            all_data["roles"] = []

        try:
            all_data["channels"] = await export_channels(guild)
            log_status(f"Exported {all_data['channels'].get('total_channels', 0)} channels", "success")
        except Exception as e:
            log_status(f"Failed to export channels: {e}", "error")
            logger.error("Channels export failed: %s", traceback.format_exc())
            all_data["channels"] = {}

        try:
            all_data["members"] = await export_members(guild, config.max_members)
            log_status(f"Exported {len(all_data['members'])} members", "success")
        except Exception as e:
            log_status(f"Failed to export members: {e}", "error")
            logger.error("Members export failed: %s", traceback.format_exc())
            all_data["members"] = []

        try:
            all_data["permissions"] = await export_permissions(guild)
            log_status("Exported permissions", "success")
        except Exception as e:
            log_status(f"Failed to export permissions: {e}", "error")
            logger.error("Permissions export failed: %s", traceback.format_exc())
            all_data["permissions"] = {}

        try:
            all_data["threads"] = await export_threads(guild)
            log_status(f"Exported {len(all_data['threads'])} threads", "success")
        except Exception as e:
            log_status(f"Failed to export threads: {e}", "error")
            logger.error("Threads export failed: %s", traceback.format_exc())
            all_data["threads"] = []

        try:
            all_data["forums"] = await export_forums(guild)
            log_status(f"Exported {len(all_data['forums'])} forum channels", "success")
        except Exception as e:
            log_status(f"Failed to export forums: {e}", "error")
            logger.error("Forums export failed: %s", traceback.format_exc())
            all_data["forums"] = []

        try:
            all_data["voice"] = await export_voice(guild)
            log_status(f"Exported {all_data['voice'].get('total_voice_channels', 0)} voice channels", "success")
        except Exception as e:
            log_status(f"Failed to export voice: {e}", "error")
            logger.error("Voice export failed: %s", traceback.format_exc())
            all_data["voice"] = {}

        try:
            all_data["stage"] = await export_stage(guild)
            log_status(f"Exported {all_data['stage'].get('total_stage_channels', 0)} stage channels", "success")
        except Exception as e:
            log_status(f"Failed to export stage: {e}", "error")
            logger.error("Stage export failed: %s", traceback.format_exc())
            all_data["stage"] = {}

        try:
            all_data["emojis"] = await export_emojis(guild)
            log_status(f"Exported {all_data['emojis'].get('total_emojis', 0)} emojis", "success")
        except Exception as e:
            log_status(f"Failed to export emojis: {e}", "error")
            logger.error("Emojis export failed: %s", traceback.format_exc())
            all_data["emojis"] = {}

        try:
            all_data["stickers"] = await export_stickers(guild)
            log_status(f"Exported {len(all_data['stickers'])} stickers", "success")
        except Exception as e:
            log_status(f"Failed to export stickers: {e}", "error")
            logger.error("Stickers export failed: %s", traceback.format_exc())
            all_data["stickers"] = []

        try:
            all_data["automod"] = await export_automod(guild)
            log_status(f"Exported {all_data['automod'].get('total_rules', 0)} AutoMod rules", "success")
        except Exception as e:
            log_status(f"Failed to export AutoMod: {e}", "error")
            logger.error("AutoMod export failed: %s", traceback.format_exc())
            all_data["automod"] = {}

        try:
            all_data["bots"] = await export_bots(guild, all_data.get("members", []))
            log_status(f"Exported {all_data['bots'].get('total_bots', 0)} bots and {all_data['bots'].get('total_webhooks', 0)} webhooks", "success")
        except Exception as e:
            log_status(f"Failed to export bots: {e}", "error")
            logger.error("Bots export failed: %s", traceback.format_exc())
            all_data["bots"] = {}

        try:
            all_data["invites"] = await export_invites(guild)
            log_status(f"Exported {all_data['invites'].get('total_invites', 0)} invites", "success")
        except Exception as e:
            log_status(f"Failed to export invites: {e}", "error")
            logger.error("Invites export failed: %s", traceback.format_exc())
            all_data["invites"] = {}

        try:
            all_data["statistics"] = await export_statistics(
                guild,
                all_data.get("members", []),
                all_data.get("roles", []),
                all_data.get("channels", {}),
            )
            log_status("Exported statistics", "success")
        except Exception as e:
            log_status(f"Failed to export statistics: {e}", "error")
            logger.error("Statistics export failed: %s", traceback.format_exc())
            all_data["statistics"] = {}

        output_dir = config.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        server_name = all_data.get("server", {}).get("name", "Unknown")

        markdown_content = ""
        if config.export_markdown:
            try:
                markdown_content = await generate_markdown(
                    all_data.get("server", {}),
                    all_data.get("roles", []),
                    all_data.get("channels", {}),
                    all_data.get("members", []),
                    all_data.get("permissions", {}),
                    all_data.get("statistics", {}),
                    all_data.get("threads", []),
                    all_data.get("emojis", {}),
                    all_data.get("stickers", []),
                    all_data.get("automod", {}),
                    all_data.get("bots", {}),
                    all_data.get("invites", {}),
                )
                md_path = output_dir / "server.md"
                md_path.write_text(markdown_content, encoding="utf-8")
                log_status("Generated Markdown report", "success")
            except Exception as e:
                log_status(f"Failed to generate Markdown: {e}", "error")
                logger.error("Markdown generation failed: %s", traceback.format_exc())

        ai_summary_content = ""
        if config.export_ai_summary:
            try:
                ai_summary_content = await generate_summary(
                    all_data.get("server", {}),
                    all_data.get("roles", []),
                    all_data.get("channels", {}),
                    all_data.get("members", []),
                    all_data.get("permissions", {}),
                    all_data.get("statistics", {}),
                    all_data.get("automod", {}),
                )
                summary_path = output_dir / "ai_summary.txt"
                summary_path.write_text(ai_summary_content, encoding="utf-8")
                log_status("Generated AI summary", "success")
            except Exception as e:
                log_status(f"Failed to generate AI summary: {e}", "error")
                logger.error("AI summary generation failed: %s", traceback.format_exc())

        ai_prompt_content = ""
        if config.export_ai_prompt:
            try:
                ai_prompt_content = await generate_ai_prompt(
                    all_data.get("server", {}),
                    all_data.get("statistics", {}),
                    all_data.get("permissions", {}),
                    all_data.get("channels", {}),
                    all_data.get("roles", []),
                    all_data.get("automod", {}),
                )
                prompt_path = output_dir / "ai_prompt.txt"
                prompt_path.write_text(ai_prompt_content, encoding="utf-8")
                log_status("Generated AI prompt", "success")
            except Exception as e:
                log_status(f"Failed to generate AI prompt: {e}", "error")
                logger.error("AI prompt generation failed: %s", traceback.format_exc())

        if config.export_zip:
            try:
                zip_path = create_zip(
                    server_name,
                    output_dir,
                    all_data,
                    markdown_content,
                    ai_summary_content,
                    ai_prompt_content,
                )
                log_status(f"Created ZIP archive: {zip_path}", "success")
            except Exception as e:
                log_status(f"Failed to create ZIP: {e}", "error")
                logger.error("ZIP creation failed: %s", traceback.format_exc())

        _save_raw_json(output_dir, all_data)

        log_status("Finished! All exports complete.", "success")
        exit_code = 0
        return exit_code
    finally:
        if not client.is_closed():
            await client.close()
        connect_task.cancel()


def _save_raw_json(output_dir: Path, all_data: dict[str, Any]) -> None:
    try:
        safe_data = dict_to_json_safe(all_data)
        json_path = output_dir / "export.json"
        if orjson:
            content = orjson.dumps(
                safe_data,
                option=orjson.OPT_INDENT_2 | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_UTC_Z,
            )
        else:
            import json
            content = json.dumps(safe_data, indent=2, default=str, ensure_ascii=False).encode("utf-8")
        json_path.write_bytes(content)
        logger.info("Saved raw JSON export to %s", json_path)
    except Exception as e:
        logger.warning("Failed to save raw JSON: %s", e)


def main() -> int:
    args = parse_args()

    try:
        config = Config.from_env(args.env)
    except ConfigError as e:
        log_status(str(e), "error")
        return 1

    if args.output:
        config = Config(
            token=config.token,
            guild_id=config.guild_id,
            output_dir=Path(args.output),
            export_ai_summary=config.export_ai_summary,
            export_markdown=config.export_markdown,
            export_zip=config.export_zip,
            export_ai_prompt=config.export_ai_prompt,
            max_members=config.max_members,
            request_delay=config.request_delay,
            log_level=config.log_level,
            log_file=config.log_file,
        )

    if args.guild is not None:
        object.__setattr__(config, "guild_id", args.guild)
    if args.max_members is not None:
        object.__setattr__(config, "max_members", args.max_members)
    if args.log_file is not None:
        object.__setattr__(config, "log_file", args.log_file)
    if args.log_level is not None:
        object.__setattr__(config, "log_level", args.log_level)
    if args.request_delay is not None:
        object.__setattr__(config, "request_delay", args.request_delay)
    if args.no_zip:
        object.__setattr__(config, "export_zip", False)
    if args.no_markdown:
        object.__setattr__(config, "export_markdown", False)
    if args.no_summary:
        object.__setattr__(config, "export_ai_summary", False)
    if args.no_prompt:
        object.__setattr__(config, "export_ai_prompt", False)

    setup_logging(config)

    logger.info("Discord Server Exporter starting")
    logger.info("Config: token=%s..., guild_id=%s, output=%s",
                config.token[:8] if config.token else "None",
                config.guild_id, config.output_dir)

    loop: asyncio.AbstractEventLoop | None = None
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        exit_code = loop.run_until_complete(run_export(config))
    except KeyboardInterrupt:
        log_status("Export cancelled by user.", "warning")
        exit_code = 130
    except Exception as e:
        log_status(f"Unexpected error: {e}", "error")
        logger.error("Fatal error: %s", traceback.format_exc())
        exit_code = 1
    finally:
        if loop is not None:
            loop.close()

    return exit_code


if __name__ == "__main__":
    try:
        import discord
    except ImportError as e:
        log_status(f"Missing dependency: {e}. Install with: pip install -r requirements.txt", "error")
        sys.exit(1)

    sys.exit(main())
