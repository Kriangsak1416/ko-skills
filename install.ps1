# Installs the boss-mode crew (agents + skill) into this machine's user-level
# Claude Code config, so it is available in every project.
#
#   powershell -ExecutionPolicy Bypass -File .\install.ps1
#
# Per-project install instead: just copy the .claude folder into the project root.

$ErrorActionPreference = 'Stop'

$src = Join-Path $PSScriptRoot '.claude'
$dst = Join-Path $env:USERPROFILE '.claude'

if (-not (Test-Path $src)) { throw "Cannot find $src - run this script from the repo it shipped in." }

New-Item -ItemType Directory -Force -Path (Join-Path $dst 'agents') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $dst 'skills') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $dst 'rules')  | Out-Null

Copy-Item -Path (Join-Path $src 'agents\*') -Destination (Join-Path $dst 'agents') -Recurse -Force
Copy-Item -Path (Join-Path $src 'skills\boss') -Destination (Join-Path $dst 'skills') -Recurse -Force
# One rule file only - leaves any other rules you already have untouched.
Copy-Item -Path (Join-Path $src 'rules\delegate-by-default.md') -Destination (Join-Path $dst 'rules') -Force

Write-Host "Installed to $dst"
Write-Host "  agents: coder, reviewer, scout, fixer  (model: sonnet)"
Write-Host "  skill:  boss                            (/boss)"
Write-Host "  rule:   delegate-by-default             (auto-delegates, no /boss needed)"
Write-Host ""

# Make sure the lead model is opus, without clobbering other settings.
$settingsPath = Join-Path $dst 'settings.json'
if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
    if ($settings.model -ne 'opus') {
        Write-Host "NOTE: $settingsPath has model = '$($settings.model)'."
        Write-Host "      Boss mode expects the lead to be Opus. Set it with /model opus or edit that file."
    } else {
        Write-Host "Lead model is already 'opus' in $settingsPath - good."
    }
} else {
    '{ "model": "opus" }' | Out-File -FilePath $settingsPath -Encoding utf8
    Write-Host "Created $settingsPath with model = opus"
}

Write-Host ""
Write-Host "Restart Claude Code, then run:  /boss <your task>"
