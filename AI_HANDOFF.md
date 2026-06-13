# AI Coding Blue Wall - AI Agent Handoff Guide

> Audience: AI coding agents and maintainers continuing work on this repository.
>
> Last reviewed: 2026-06-13, Asia/Shanghai.
>
> Repository: `https://github.com/zong1024/codex-usage-bluewall-github`
>
> Production SVG: `https://codex-usage-bluewall-github.vercel.app/api/svg`
>
> GitHub Profile: `https://github.com/zong1024`

## 1. Read This First

This is no longer a single-machine Codex counter. The project currently has
four separate responsibilities:

1. Scan token usage from multiple AI coding tools.
2. Merge snapshots from multiple devices without double-counting devices.
3. supplement missing local Codex history with account-side Codex Analytics
   activity.
4. Render and deploy a 365-day SVG calendar for a GitHub Profile README.

Do not begin by editing `scripts/scan_codex.py` or `data/codex-usage.json`.
Those are legacy artifacts. The active scanner is:

```text
scripts/scan_all_tools.py
```

The canonical merged token dataset is:

```text
data/ai-usage.json
```

The account-side Codex activity supplement is:

```text
data/codex-cloud-activity.json
```

Before changing anything:

```bash
git status --short
git fetch origin main
git log --oneline --decorate --graph --max-count=12 --all
```

The working tree may contain user experiments or generated files. Never reset,
delete, overwrite, or commit unrelated changes.

## 2. Product Requirements

The intended behavior is:

- Show a full 365-day contribution-style calendar.
- Keep dates without activity as dark empty cells.
- Color dates with local token usage.
- Also color dates confirmed by Codex Analytics when local Codex logs are
  missing.
- Never invent token counts for cloud-only activity.
- Include data from multiple devices, operating systems, tools, and agents.
- Keep token totals separate from activity-only supplementation.
- Render correctly through GitHub Camo in the Profile README.

The calendar should therefore distinguish three states:

| State | Token count | Cloud activity | Cell |
|---|---:|---:|---|
| No activity | 0 | 0 | Dark empty cell |
| Local token activity | `> 0` | any | Blue cell based on token intensity |
| Cloud-only Codex activity | 0 | `> 0` | Blue cell based on Analytics percentage |

## 3. Current Architecture

```text
Windows device
  Codex local DB + rollout JSONL
        |
        | scheduled PowerShell scan
        v
data/ai-usage-windows-main.json
        |
        | SCP over LAN
        v
Linux repository host -------------------------------+
  Codex / Claude Code / MiMo Code / OpenCode / Hermes|
        |                                             |
        v                                             |
data/ai-usage-ZONGRUICHD.json                         |
        |                                             |
        +-------------- merge_devices.py <------------+
                              |
                              v
                     data/ai-usage.json
                              |
          +-------------------+-------------------+
          |                                       |
          v                                       v
data/codex-cloud-activity.json          scripts/render_blue_wall.py
          |                                       |
          +-------------------+-------------------+
                              |
                              v
                    assets/ai-blue-wall.svg
                              |
                              v
                       GitHub repository
                              |
                 +------------+-------------+
                 |                          |
                 v                          v
       Vercel `/api/svg`           GitHub Actions SVG update
                 |
                 v
           GitHub Profile README
                 |
                 v
              GitHub Camo
```

## 4. Canonical Files

### Collection and merging

| File | Responsibility |
|---|---|
| `scripts/scan_all_tools.py` | Active multi-tool scanner |
| `scripts/merge_devices.py` | Merge device snapshots |
| `scripts/update-multi-device.sh` | Linux/macOS scan and merge helper |
| `scripts/update-multi-device.ps1` | General Windows scan and merge helper |
| `scripts/update-windows-scheduled.ps1` | Current Windows-to-Linux scheduled sync |
| `scripts/import-windows-snapshot.sh` | Linux merge, render, commit, and push after Windows upload |

### Rendering and deployment

| File | Responsibility |
|---|---|
| `scripts/render_blue_wall.py` | Offline/static SVG renderer |
| `api/svg.js` | Production dynamic SVG implementation |
| `.github/workflows/update-svg.yml` | Regenerates static SVG when usage/activity data changes |
| `data/codex-cloud-activity.json` | Codex account-side activity supplement |
| `assets/ai-blue-wall.svg` | Generated static SVG |

### Tests

| File | Responsibility |
|---|---|
| `tests/test_usage_scanners.py` | Scanner, merge, token-accounting, and Python renderer tests |
| `tests/test_api_svg.js` | Production JavaScript SVG regression test |

### Legacy or potentially stale files

Do not treat these as authoritative without first proving they are still used:

| File | Warning |
|---|---|
| `scripts/scan_codex.py` | Old scanner; estimates a 70/30 input/output split |
| `data/codex-usage.json` | Old single-tool output |
| `assets/codex-blue-wall.svg` | Old output path |
| `PROJECT_ANALYSIS.md` | Historical architecture analysis; predates multi-device and cloud activity |
| `vercel/pages/api/svg.ts` | Older Next.js implementation; currently lacks cloud activity behavior |
| `vercel-app/` | Experimental/alternate deployment tree |
| `scripts/extract_codex_usage.js` | Experimental browser-console helper |

Production behavior must be verified against the public `/api/svg` endpoint,
not inferred from a legacy implementation.

## 5. Data Model

### 5.1 Device snapshot

Each device snapshot has schema version 2:

```json
{
  "schema_version": 2,
  "generated_at": "2026-06-13T01:22:58+08:00",
  "device": "windows-main",
  "tools_scanned": ["codex"],
  "per_tool_summary": {
    "codex": 851256761
  },
  "per_agent_summary": {
    "codex:vscode": 700000000,
    "codex:cli": 151256761
  },
  "scan_status": {
    "codex": {
      "available": true,
      "warning_count": 0
    }
  },
  "statistics": {},
  "daily_usage": {}
}
```

### 5.2 Daily usage

```json
{
  "2026-06-12": {
    "input_tokens": 20429163,
    "output_tokens": 192202,
    "cache_read_tokens": 107700032,
    "cache_write_tokens": 0,
    "reasoning_tokens": 51801,
    "total_tokens": 128373198,
    "sessions": 752,
    "tools": {
      "codex": 36480077,
      "claude_code": 323308,
      "mimocode": 91569813
    },
    "agents": {
      "codex:vscode": 36480077,
      "claude_code:main": 323308,
      "mimocode:main": 85258203
    }
  }
}
```

### 5.3 Codex cloud activity

`data/codex-cloud-activity.json` intentionally contains activity percentages,
not token counts:

```json
{
  "schema_version": 1,
  "source": "Codex Analytics",
  "range": {
    "start": "2026-03-15",
    "end": "2026-06-12"
  },
  "generated_at": "2026-06-13T02:40:00+08:00",
  "daily_usage_percent": {
    "2026-03-20": 0.14,
    "2026-03-24": 19.83
  }
}
```

Rules:

- A positive percentage means the date is active.
- It may control cell color and activity streaks.
- It must not be added to `total_tokens`, `peak_tokens`, or per-tool totals.
- Local token records remain the authority for token totals.

## 6. Token Accounting Rules

### 6.1 Codex

Codex `token_count` records are cumulative within a counter segment. Match the
Codex Desktop accounting model:

```text
total = input_tokens
      + cached_input_tokens
      + output_tokens
      + reasoning_output_tokens
```

Important details:

- `cached_input_tokens` maps to the project's `cache_read_tokens`.
- `reasoning_output_tokens` maps to `reasoning_tokens`.
- The raw event's `total_tokens` does not include all categories needed to
  reproduce the Desktop card.
- Cumulative counters can decrease after context compaction or restoration.
- When the cumulative total decreases, treat the new event as a fresh segment.
- For normal cumulative growth, add only the delta from the previous event.
- If no `token_count` events exist, `threads.tokens_used` is a fallback only.

Do not revert to a global high-water-mark algorithm. It loses usage after
counter resets.

### 6.2 Claude Code

Count assistant message usage and include:

- input
- output
- cache read
- cache creation/write
- reasoning when available

Deduplicate records by stable message/request identity.

### 6.3 MiMo Code

Read the SQLite `message` table and preserve `agent_id`.

MiMo may import Claude Code sessions. If the `claude_import` table is present,
exclude imported sessions to avoid double counting Claude usage.

### 6.4 OpenCode

Support both:

- SQLite message storage.
- JSON message storage.

Only count assistant records when the role is available.

### 6.5 Hermes

Scan the main state database and profile databases:

```text
~/.hermes/state.db
~/.hermes/profiles/*/state.db
```

The `sessions` table must expose `id`, `started_at`, and at least one token
column.

## 7. Multi-Device Semantics

`scripts/merge_devices.py` uses the snapshot's `device` value as identity.

If multiple inputs have the same device:

- Compare `generated_at`.
- Keep the newest snapshot.
- Do not add both snapshots.

If two physical devices share the same device name, their data will collapse.
Use stable, unique names such as:

```text
windows-main
linux-workstation
macbook-pro
```

The merge operation sums different devices. It cannot deduplicate the same
conversation copied between different device names. Avoid scanning mirrored
Codex homes as separate devices.

## 8. Current Windows Automation

The current Windows workflow is specialized:

```text
Windows scheduled task
  -> scripts/update-windows-scheduled.ps1
  -> scan Codex only
  -> create ai-usage-windows-main.json
  -> SCP snapshot to Linux
  -> SSH to Linux
  -> scripts/import-windows-snapshot.sh
  -> merge, render, commit, push
```

Current script assumptions include:

```text
Python: C:\Python314\python.exe
Work directory: %USERPROFILE%\codex-bluewall-scan
SSH key: %USERPROFILE%\.ssh\id_ed25519_bluewall_lan
Task name: AI Coding Blue Wall Update
```

The checked-in script currently references private LAN host information. Treat
that as deployment-specific configuration, not a portable default.

Never put passwords in this repository or in this document. The scheduled task
must use SSH keys and `BatchMode=yes`.

Useful Windows checks:

```powershell
Get-ScheduledTask -TaskName "AI Coding Blue Wall Update"
Get-ScheduledTaskInfo -TaskName "AI Coding Blue Wall Update"
Start-ScheduledTask -TaskName "AI Coding Blue Wall Update"
```

Success is:

```text
LastTaskResult = 0
```

## 9. Codex Cloud Activity

### Why it exists

Local Codex data did not contain the complete account history. In the observed
environment:

- Local merged token dates began around May 2026.
- Codex Analytics showed account activity from March 2026.
- The Analytics page reported activity from Desktop, CLI, Extension/VS Code,
  Cloud, GitHub Code Review, Exec, and uncategorized clients.

Therefore a local-only heatmap incorrectly showed fewer active dates even when
its token total was otherwise correct.

### Current source

The current supplement was derived from the authenticated Codex Analytics page:

```text
https://chatgpt.com/codex/cloud/settings/analytics#usage
```

It is a manually captured snapshot. There is no stable authenticated scheduled
API integration in this repository yet.

### Update procedure

When refreshing cloud activity:

1. Open Codex Analytics while authenticated.
2. Select the intended date range and daily grouping.
3. Extract dates with positive usage.
4. Store usage percentages in `daily_usage_percent`.
5. Update `range` and `generated_at`.
6. Do not store cookies, access tokens, account IDs, raw page payloads, or
   browser profiles.
7. Run all renderer tests.
8. Commit only the aggregate activity JSON.

Future improvement: create an explicit, secure importer that accepts exported
aggregate JSON. Do not build automation around copied browser credentials.

## 10. Rendering Rules

Both renderers must stay behaviorally aligned:

```text
scripts/render_blue_wall.py
api/svg.js
```

### Calendar range

- Render a full 365-day window.
- Align the start to Sunday.
- Include the latest of:
  - current UTC date,
  - latest local data date,
  - latest cloud activity date.
- This avoids losing the current Shanghai date while UTC is still on the
  previous day.

### Empty dates

Empty dates must still have a cell:

```text
#161b22
```

Do not render only the active date range.

### Color scaling

Token days use a square-root scale with a minimum visible intensity. A simple
linear scale makes ordinary days nearly indistinguishable when one day has a
very large token spike.

Cloud-only days use the same blue palette, driven by the Analytics percentage.

### Statistics

Token statistics:

- Total tokens: local aggregated token data only.
- Peak tokens: local aggregated token data only.

Activity statistics:

- Active days: union of token-active dates and cloud-active dates.
- Current streak: calculated from the union.
- Longest streak: calculated from the union.

Tooltip rules:

```text
Token date:      YYYY-MM-DD: N tokens
Cloud-only date: YYYY-MM-DD: Codex cloud usage N%
Empty date:      YYYY-MM-DD: no activity
```

## 11. Vercel Deployment

Project metadata:

```text
Project: codex-usage-bluewall-github
Project ID: prj_2nPAgmp4IDcAutmDfSyzmUP46fLs
Team ID: team_1kZVwXKmKpyUwqNPdzOhiCWq
```

Production:

```text
https://codex-usage-bluewall-github.vercel.app/api/svg
```

The production endpoint fetches aggregate JSON from the GitHub `main` branch.
This means:

- Local uncommitted data does not affect production.
- A pushed data change may require a new Vercel deployment for code changes.
- JSON data changes are fetched dynamically, subject to caching.
- `data/codex-cloud-activity.json` fetch failure must degrade to local-only
  activity instead of returning HTTP 500.

Check deployment status:

```bash
vercel ls codex-usage-bluewall-github \
  --scope team_1kZVwXKmKpyUwqNPdzOhiCWq
```

Do not assume a Git push is live. Confirm the newest production deployment is
`Ready`, not `Queued`, `Building`, or `Error`.

## 12. GitHub Profile and Caching

The Profile repository is:

```text
https://github.com/zong1024/zong1024
```

Recommended README form:

```markdown
[![AI Coding Blue Wall](https://codex-usage-bluewall-github.vercel.app/api/svg?profile=zong1024&v=<cache-key>)](https://codex-usage-bluewall-github.vercel.app/api/svg)
```

GitHub proxies external images through `camo.githubusercontent.com`. Even when
Vercel is correct, the Profile can continue showing an old image.

After a meaningful renderer/data release, change `v=<cache-key>` to a new commit
hash or unique version. Then verify GitHub's Camo response, not just Vercel.

Example verification:

```bash
curl -fsSL "https://github.com/zong1024?refresh=<cache-key>" \
  -o /tmp/profile.html

camo_url="$(
  rg -o 'https://camo.githubusercontent.com/[^\" ]+' /tmp/profile.html |
  head -n 1
)"

curl -fsSL "$camo_url" -o /tmp/profile-camo.svg
```

Check the downloaded SVG for expected dates and statistics.

## 13. Standard Update Commands

### Scan one device

```bash
python3 scripts/scan_all_tools.py \
  --days 365 \
  --device-name linux-workstation \
  --output data/ai-usage-linux-workstation.json
```

### Scan selected tools

```bash
python3 scripts/scan_all_tools.py \
  --days 365 \
  --tools codex claude_code \
  --device-name linux-workstation \
  --output data/ai-usage-linux-workstation.json
```

### Merge devices

```bash
python3 scripts/merge_devices.py \
  --inputs \
  data/ai-usage-windows-main.json \
  data/ai-usage-ZONGRUICHD.json \
  --output data/ai-usage.json
```

Use the actual canonical snapshot filenames. Do not mix normal and experimental
`*-full.json` snapshots unless that change is intentional and reviewed.

### Render static SVG

```bash
python3 scripts/render_blue_wall.py \
  --data data/ai-usage.json \
  --output assets/ai-blue-wall.svg \
  --username zong1024 \
  --days 365
```

The renderer automatically looks for:

```text
data/codex-cloud-activity.json
```

next to the main data file.

## 14. Tests

Run both test suites:

```bash
python3 -m unittest discover -s tests -v
node tests/test_api_svg.js
node --check api/svg.js
```

Important regression coverage:

- Claude cache tokens are counted.
- Codex matches Desktop token accounting.
- Codex counter resets are counted.
- MiMo excludes imported Claude sessions.
- OpenCode and Hermes schemas are supported.
- Multi-device tool and agent breakdown survives merging.
- Cloud activity adds active dates without adding tokens.
- Production SVG includes cloud-only dates and empty dates.

## 15. End-to-End Verification

Do not stop after unit tests.

### 15.1 Inspect merged data

```bash
jq '{
  generated_at,
  merged_from,
  statistics,
  per_tool_summary
}' data/ai-usage.json
```

### 15.2 Inspect cloud activity

```bash
jq '{
  generated_at,
  range,
  active_days: (.daily_usage_percent | length)
}' data/codex-cloud-activity.json
```

### 15.3 Verify production SVG

```bash
curl -fsSL \
  "https://codex-usage-bluewall-github.vercel.app/api/svg?v=$(date +%s)" \
  -o /tmp/live-blue-wall.svg
```

Use a script to verify:

- Around 365 calendar dates are present.
- The first and last dates are expected.
- `2026-03-20: Codex cloud usage` exists while the current cloud snapshot is
  still in use.
- Empty dates contain `no activity`.
- The total token text equals the remote `data/ai-usage.json`.
- Active days reflect the union of token and cloud dates.

Example:

```bash
python3 - <<'PY'
import re

svg = open("/tmp/live-blue-wall.svg", encoding="utf-8").read()
cells = re.findall(
    r"<title>(\d{4}-\d{2}-\d{2}): (.*?)</title>",
    svg,
)
print("cells:", len(cells))
print("cloud-only:", sum("Codex cloud usage" in value for _, value in cells))
print("empty:", sum(value == "no activity" for _, value in cells))
print("range:", cells[0][0], cells[-1][0])
PY
```

### 15.4 Verify GitHub Camo

Download the image URL rendered by the Profile and inspect that SVG separately.
This is required because Vercel can be correct while Camo is stale.

## 16. Known Risks and Technical Debt

### 16.1 Cloud activity refresh is manual

The cloud activity snapshot can become stale. It needs a secure refresh design.

### 16.2 Duplicate renderer implementations

Python and JavaScript rendering logic can drift. Changes to calendar range,
color scale, tooltip semantics, or activity statistics must update both.

### 16.3 Legacy Next.js API

`vercel/pages/api/svg.ts` does not currently mirror the production cloud
activity logic. Determine the actual Vercel routing/build ownership before
deleting or updating it. Do not silently switch production to this stale path.

### 16.4 Deployment has had repeated build failures

Vercel history contains failed deployments. Confirm build dependencies and
production readiness after every deployment-related change.

### 16.5 Activity and token totals have different authorities

Codex Analytics percentages prove activity dates but do not provide token
counts. Never convert percentages into tokens.

### 16.6 Cross-device conversation duplication

Device-name deduplication does not detect the same conversation copied to two
different devices.

### 16.7 Current repository may be dirty

There may be local experiments such as:

```text
data/ai-usage-*-full.json
vercel-app/
index.html
PROJECT_ANALYSIS.md
```

Do not include them in a commit unless the task explicitly requires them.

## 17. Security Rules

Never commit:

- Passwords.
- Private SSH keys.
- Browser cookies or local storage.
- ChatGPT/Codex access tokens.
- Raw Codex, Claude, MiMo, OpenCode, or Hermes conversations.
- Prompt text or source-code transcripts.
- Full browser page dumps containing account data.
- `.codex`, `.claude`, `.hermes`, or tool database files.

Allowed public data should remain aggregate:

- Daily token counts.
- Tool/agent summaries.
- Activity percentages.
- Non-secret device labels.

Before committing:

```bash
git diff --cached
git status --short
```

Review every staged file explicitly.

## 18. Safe Git Procedure

Automated Windows imports and GitHub Actions can push while another agent is
working. Non-fast-forward push failures are expected.

Recommended procedure:

```bash
git status --short
git fetch origin main
git log --oneline --decorate --graph --max-count=12 --all
```

If local work is committed but unrelated changes remain unstaged:

```bash
git rebase --autostash origin/main
```

Generated SVG conflicts should be resolved by regenerating the SVG from the
merged data, not by manually choosing arbitrary conflict sides.

Never use destructive commands such as:

```text
git reset --hard
git checkout -- .
```

unless the user explicitly requests destruction of local work.

## 19. Acceptance Checklist

A change is complete only when all applicable items pass:

- [ ] `git status` was inspected before editing.
- [ ] Active scanner paths were used, not legacy paths.
- [ ] Codex cache and reasoning tokens remain included.
- [ ] Counter reset behavior remains covered.
- [ ] Multi-device snapshots are uniquely named.
- [ ] Cloud activity did not alter token totals.
- [ ] Empty calendar dates remain visible and uncolored.
- [ ] Python tests pass.
- [ ] JavaScript tests pass.
- [ ] Static SVG was regenerated when required.
- [ ] Changes were pushed without overwriting automated commits.
- [ ] Vercel production deployment is `Ready`.
- [ ] Production `/api/svg` contains the expected dates and totals.
- [ ] GitHub Camo contains the expected dates and totals.
- [ ] Profile README cache key was changed when needed.
- [ ] No credentials or raw conversation data were staged.

## 20. Current Behavioral Baseline

At the time of this handoff, the verified production behavior was:

- 371 rendered calendar cells for the aligned 365-day window.
- 68 combined activity days.
- 29 cloud-only Codex dates supplementing missing local history.
- Cloud history visible from 2026-03-20.
- Empty dates retained as dark cells.
- Token total unchanged by cloud activity supplementation.

These numbers are a regression baseline, not permanent constants. They will
change as new device snapshots and cloud activity snapshots are added.
