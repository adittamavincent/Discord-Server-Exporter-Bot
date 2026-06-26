# Discord Server Exporter

Export every piece of information available through the Discord API about a Discord server into structured files for analysis by AI models (ChatGPT, Claude, Gemini, DeepSeek) or human review.

## Features

- **Full Server Export** - Server metadata, roles, channels, members, permissions, threads, forums, voice, stage
- **Rich JSON Outputs** - Machine-readable structured data for every component
- **Markdown Report** - Human-readable `server.md` with overview, hierarchy, issues, and suggestions
- **AI Summary** - Health score (0-100) with risk assessment across 6 dimensions
- **AI Audit Prompt** - Pre-built prompt for LLMs to analyze and improve your server
- **ZIP Archive** - Everything compressed into `ServerName_YYYY-MM-DD.zip`
- **Rich CLI** - Progress indicators and colored output
- **Error Resilience** - Partial exports on failure, comprehensive logging
- **Async Architecture** - Non-blocking API calls for performance

## Installation

### Prerequisites

- Python 3.12+
- A Discord Bot Token with appropriate permissions

### Setup

```bash
# Clone the repository
git clone https://github.com/youngcoder45/discord-server-exporter.git
cd discord-server-exporter

# Install dependencies
pip install -r requirements.txt

# Configure your bot token
cp .env.example .env
# Edit .env and add your DISCORD_TOKEN
```

## Bot Permissions

Your Discord bot needs the following permissions in the server:

| Permission | Purpose |
|-----------|---------|
| `View Channels` | Read channel list and metadata |
| `Read Message History` | Access thread content |
| `Manage Webhooks` | Fetch webhook information |
| `Manage Guild` | Access guild settings and invites |
| `View Audit Log` | Access moderation settings |

### Required Intents

Enable these in the Discord Developer Portal under "Bot" > "Privileged Gateway Intents":

- **Server Members Intent** - Required for member list export
- **Message Content Intent** - Required for thread information

These are configured in `exporter/client.py`:
```python
intents.guilds = True
intents.members = True
intents.message_content = True
intents.moderation = True
```

## Usage

### Basic

```bash
python export.py
```

Exports the first available guild the bot has access to.

### Specific Guild

```bash
python export.py --guild 123456789012345678
```

### Custom Output Directory

```bash
python export.py --guild YOUR_GUILD_ID --output ./my-exports
```

### Selective Export

```bash
python export.py --no-zip --no-markdown
python export.py --guild YOUR_GUILD_ID --no-summary --no-prompt
```

### Large Servers

```bash
python export.py --guild YOUR_GUILD_ID --max-members 5000 --request-delay 1.0
```

### Debug Mode

```bash
python export.py --log-level DEBUG --log-file export.log
```

### All Options

```
python export.py --help
```

## Output Structure

### Per-server files (inside `output/` or your custom directory)

```
ServerName_2026-06-26.zip
├── server.json          # Server metadata, settings, features
├── roles.json           # Complete role hierarchy with permissions
├── members.json         # Member list with roles and metadata
├── channels.json        # All channels with permission overwrites
├── permissions.json     # Permission matrix across all roles
├── statistics.json      # Server statistics and metrics
├── threads.json         # Active and archived threads
├── emojis.json          # Custom emoji list
├── stickers.json        # Custom sticker list
├── voice.json           # Voice channel details
├── stage.json           # Stage channel details
├── forums.json          # Forum channel details with tags
├── automod.json         # AutoMod rule configuration
├── bots.json            # Bot accounts and webhooks
├── invites.json         # Active invites
├── server.md            # Human-readable Markdown report
├── ai_summary.txt       # AI-ready summary with health score
├── ai_prompt.txt        # LLM prompt for server audit
└── README.txt           # Archive contents description
```

Additionally, `export.json` is saved in the output directory containing all data merged.

## AI Analysis

### AI Summary (`ai_summary.txt`)

The summary includes:
- **Health Score** (0-100) aggregated from 6 dimensions
- **Organization** - Channel structure, categories, naming
- **Security** - Verification level, MFA, AutoMod
- **Permissions** - Role hierarchy, admin distribution
- **Moderation** - AutoMod rules, content filtering
- **Community** - Member count, boosts, engagement features
- **Scalability** - Growth capacity, channel density
- **Risk Level** - Low / Medium / High
- **Detected Issues** - Sorted by severity
- **Recommendations** - Actionable improvements

### AI Prompt (`ai_prompt.txt`)

A structured prompt designed to be fed into any LLM for a comprehensive server audit covering:
- Critical Issues
- Important Improvements
- Optional Improvements
- Improved Channel Layout
- Improved Role Hierarchy
- Recommended Bots
- Community Growth Plan
- Security Audit

## Project Structure

```
discord-server-exporter/
├── export.py              # CLI entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── .gitignore
├── LICENSE
├── README.md
├── output/                # Generated exports
└── exporter/
    ├── __init__.py
    ├── client.py          # Discord client setup
    ├── server.py          # Server metadata export
    ├── roles.py           # Role hierarchy export
    ├── channels.py        # Channel export (text, voice, forum, stage)
    ├── members.py         # Member export
    ├── permissions.py     # Permission matrix export
    ├── statistics.py      # Server statistics
    ├── threads.py         # Thread export
    ├── forums.py          # Forum channel export
    ├── voice.py           # Voice channel export
    ├── stage.py           # Stage channel export
    ├── stickers.py        # Sticker export
    ├── emojis.py          # Emoji export
    ├── automod.py         # AutoMod rules export
    ├── bots.py            # Bot and webhook export
    ├── invites.py         # Invite export
    ├── markdown.py        # Markdown report generator
    ├── summary.py         # AI summary generator
    ├── ai_prompt.py       # AI audit prompt generator
    ├── zipper.py          # ZIP archive creator
    └── utils.py           # Shared utilities
```

## Architecture

The application follows SOLID principles with:

- **Single Responsibility** - Each module handles one export domain
- **Open/Closed** - New exporters can be added without modifying existing code
- **Liskov Substitution** - Consistent data structures across all exports
- **Interface Segregation** - Clean function signatures with typed parameters
- **Dependency Inversion** - High-level orchestrator depends on abstractions

All I/O operations use async/await for non-blocking execution.

## Error Handling

- Invalid tokens are caught with descriptive messages
- Missing intents are reported with guidance
- Permission errors allow partial exports to continue
- Network failures are retry-friendly
- Rate limits are handled by configurable delays
- Every error is logged with full traceback
- The export continues even if individual modules fail

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DISCORD_TOKEN` | - | Bot token (required) |
| `GUILD_ID` | - | Target guild ID |
| `OUTPUT_DIR` | `output` | Export directory |
| `MAX_MEMBERS` | `1000` | Max members to fetch |
| `REQUEST_DELAY` | `0.5` | API request delay (seconds) |
| `EXPORT_MARKDOWN` | `true` | Generate Markdown report |
| `EXPORT_AI_SUMMARY` | `true` | Generate AI summary |
| `EXPORT_ZIP` | `true` | Create ZIP archive |
| `EXPORT_AI_PROMPT` | `true` | Generate AI prompt |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FILE` | - | Log file path |

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
