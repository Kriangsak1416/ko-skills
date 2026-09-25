#!/usr/bin/env bash
# ดึง repo ล่าสุดแล้วก๊อป skills/agents/rules ทับลง ~/.claude
# (ขั้นเดียวกับ "ติดตั้งแบบที่ 2" ใน README — ทับเฉพาะไฟล์ชื่อเดียวกัน ของอื่นในเครื่องไม่หาย)
set -eu

repo="$(cd "$(dirname "$0")/.." && pwd)"
dest="$HOME/.claude"
cd "$repo"

GIT_TERMINAL_PROMPT=0 git pull -q --ff-only origin main \
  || echo "pull ไม่สำเร็จ (ออฟไลน์ หรือมีแก้ค้างใน repo) — ก๊อปจากที่มีในเครื่องแทน"

mkdir -p "$dest/agents" "$dest/skills" "$dest/rules"
cp -R agents/. "$dest/agents/"
cp -R skills/. "$dest/skills/"
cp    rules/*.md "$dest/rules/"
# บันทึก version หลักที่ติดตั้ง ให้ skill update-skill-ko เทียบกับ GitHub ได้
sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' .claude-plugin/marketplace.json | head -n 1 > "$dest/ko-skills.version"

echo "อัปเดต skills/agents/rules ลง $dest แล้ว — ถ้าเซสชันนี้ยังเห็นของเก่า ให้รีสตาร์ต Claude Code"
