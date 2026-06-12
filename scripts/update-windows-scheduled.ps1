param(
    [string]$Repo = "$HOME\Projects\codex-usage-bluewall-github",
    [string]$Device = "windows-main",
    [int]$Days = 365
)

$ErrorActionPreference = "Stop"
$Python = "C:\Python314\python.exe"
$LinuxSnapshot = Join-Path $Repo "data\ai-usage-ZONGRUICHD.json"
$WindowsSnapshot = Join-Path $Repo "data\ai-usage-windows-main.json"
$MergedData = Join-Path $Repo "data\ai-usage.json"
$Svg = Join-Path $Repo "assets\ai-blue-wall.svg"

git -C $Repo pull --ff-only
if ($LASTEXITCODE -ne 0) { throw "git pull failed" }

& $Python "$Repo\scripts\scan_all_tools.py" `
    --days $Days `
    --tools codex `
    --device-name $Device `
    --output $WindowsSnapshot
if ($LASTEXITCODE -ne 0) { throw "Windows usage scan failed" }

& $Python "$Repo\scripts\merge_devices.py" `
    --inputs $LinuxSnapshot $WindowsSnapshot `
    --output $MergedData
if ($LASTEXITCODE -ne 0) { throw "Device merge failed" }

& $Python "$Repo\scripts\render_blue_wall.py" `
    --data $MergedData `
    --output $Svg `
    --username zong1024 `
    --days $Days
if ($LASTEXITCODE -ne 0) { throw "SVG render failed" }

git -C $Repo add `
    data/ai-usage-windows-main.json `
    data/ai-usage.json `
    assets/ai-blue-wall.svg

$staged = git -C $Repo diff --cached --name-only
if ($staged) {
    git -C $Repo commit -m "Update usage from Windows"
    if ($LASTEXITCODE -ne 0) { throw "git commit failed" }
    git -C $Repo push
    if ($LASTEXITCODE -ne 0) { throw "git push failed" }
}
