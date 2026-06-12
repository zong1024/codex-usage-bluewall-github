#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"
git pull --ff-only

python3 scripts/merge_devices.py \
    --inputs \
    data/ai-usage-ZONGRUICHD.json \
    data/ai-usage-windows-main.json \
    --output data/ai-usage.json

python3 scripts/render_blue_wall.py \
    --data data/ai-usage.json \
    --output assets/ai-blue-wall.svg \
    --username zong1024 \
    --days 365

git add \
    data/ai-usage-windows-main.json \
    data/ai-usage.json \
    assets/ai-blue-wall.svg

if ! git diff --cached --quiet; then
    git commit -m "Update usage from Windows"
    git push
fi
