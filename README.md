# AI Coding Blue Wall

Track your token usage across multiple AI coding tools (Codex, Claude Code, MimoCode) and display it as a beautiful blue wall on your GitHub Profile.

## Features

- 📊 Scan token usage from Codex, Claude Code, MimoCode
- 🎨 Generate GitHub-style blue heatmap SVG
- ☁️ Deploy to Vercel for automatic updates
- 🔒 Secure: only aggregated data, no secrets

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Windows PC     │     │  Linux PC       │     │  macOS          │
│  - Codex        │     │  - Codex        │     │  - Codex        │
│  - Claude Code  │     │  - Claude Code  │     │  - Claude Code  │
│  - MimoCode     │     │  - MimoCode     │     │  - MimoCode     │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   GitHub Repository    │
                    │  data/ai-usage.json    │
                    │  assets/ai-blue-wall.svg│
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Vercel Deployment    │
                    │  /api/svg (SVG API)    │
                    │  / (Preview Page)      │
                    └────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  GitHub Profile README │
                    │  <img src="vercel/svg">│
                    └────────────────────────┘
```

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/zongrui/codex-usage-bluewall-github.git
cd codex-usage-bluewall-github
```

### 2. Scan Your Tools

```bash
# Scan all tools on current device
python3 scripts/scan_all_tools.py --days 365 --output data/ai-usage.json

# Or use the update script
./scripts/update-full.sh --commit --push
```

### 3. Deploy to Vercel

1. Push to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your repository
4. Set environment variables:
   - `GITHUB_USERNAME`: your-github-username
   - `GITHUB_REPO`: codex-usage-bluewall-github
5. Deploy!

### 4. Embed in GitHub Profile

Add to your GitHub Profile README:

```markdown
## AI Coding Activity

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://your-project.vercel.app/api/svg">
  <img alt="AI Coding Blue Wall" src="https://your-project.vercel.app/api/svg">
</picture>
```

## Multi-Device Setup

### Windows

```powershell
# Scan and push
.\scripts\update.ps1 --commit --push
```

### Linux/macOS

```bash
# Scan and push
./scripts/update-full.sh --commit --push
```

### Cron Job (Linux)

```bash
# Add to crontab
0 0 * * * cd /path/to/project && ./scripts/update-full.sh --commit --push
```

### Task Scheduler (Windows)

Create a scheduled task to run `update.ps1` daily.

## Supported Tools

| Tool | Data Source | Status |
|------|------------|--------|
| Codex | `~/.codex/state_5.sqlite` | ✅ Supported |
| Claude Code | `~/.claude/projects/*.jsonl` | ✅ Supported |
| MimoCode | `~/.local/share/mimocode/mimocode.db` | ⚠️ Limited |
| Hermes Agent | `~/.hermes/` | 🔜 Planned |

## Configuration

Edit `config.json`:

```json
{
  "username": "your-github-username",
  "days": 365,
  "output_svg": "assets/ai-blue-wall.svg",
  "output_data": "data/ai-usage.json"
}
```

## Security

- ✅ Only aggregated token counts are stored
- ✅ No API keys or secrets in repository
- ✅ No source code or prompts uploaded
- ✅ `.gitignore` blocks sensitive files

## Requirements

- Python 3.8+
- Git
- Vercel account (free)

## License

MIT
