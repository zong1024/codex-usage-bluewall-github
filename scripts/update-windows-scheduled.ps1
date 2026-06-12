param(
    [string]$WorkDir = "$HOME\codex-bluewall-scan",
    [string]$Device = "windows-main",
    [string]$LinuxHost = "zongrui@192.168.0.161",
    [string]$LinuxRepo = "/home/zongrui/Projects/codex-usage-bluewall-github",
    [int]$Days = 365
)

$ErrorActionPreference = "Stop"
$Python = "C:\Python314\python.exe"
$Key = "$HOME\.ssh\id_ed25519_bluewall_lan"
$Scanner = Join-Path $WorkDir "scan_all_tools.py"
$Snapshot = Join-Path $WorkDir "ai-usage-windows-main.json"

& $Python $Scanner `
    --days $Days `
    --tools codex `
    --device-name $Device `
    --output $Snapshot
if ($LASTEXITCODE -ne 0) { throw "Windows usage scan failed" }

& scp.exe `
    -i $Key `
    -o BatchMode=yes `
    $Snapshot `
    "${LinuxHost}:${LinuxRepo}/data/ai-usage-windows-main.json"
if ($LASTEXITCODE -ne 0) { throw "Snapshot upload failed" }

& ssh.exe `
    -i $Key `
    -o BatchMode=yes `
    $LinuxHost `
    "cd '$LinuxRepo' && ./scripts/import-windows-snapshot.sh"
if ($LASTEXITCODE -ne 0) { throw "Linux merge and push failed" }
