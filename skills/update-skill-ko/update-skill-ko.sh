#!/usr/bin/env bash
# เทียบ version หลักของ ko-skills ที่ติดตั้งใน ~/.claude กับบน GitHub
#   check (ค่าเริ่มต้น) — อ่านอย่างเดียว พิมพ์ local= remote= status=
#   apply             — clone repo ล่าสุด ก๊อป skills/agents/rules ทับลง ~/.claude แล้วบันทึก version
# version หลักคือ metadata.version ใน .claude-plugin/marketplace.json
set -eu

repo_url="https://github.com/Kriangsak1416/ko-skills.git"
manifest_url="https://raw.githubusercontent.com/Kriangsak1416/ko-skills/main/.claude-plugin/marketplace.json"
dest="$HOME/.claude"
stamp="$dest/ko-skills.version"

version_of() { sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' | head -n 1; }

case "${1:-check}" in
  check)
    local_v="$(cat "$stamp" 2>/dev/null || true)"
    remote_v="$(curl -fsSL --max-time 15 "$manifest_url" 2>/dev/null | version_of)"
    if [ -z "$remote_v" ]; then status=unknown      # ออฟไลน์ หรือ GitHub ตอบไม่ได้
    elif [ "$local_v" = "$remote_v" ]; then status=same
    else status=different; fi                       # รวมกรณียังไม่เคยบันทึก version ในเครื่อง
    echo "local=${local_v:-none}"
    echo "remote=${remote_v:-unknown}"
    echo "status=$status"
    ;;
  apply)
    tmp="$(mktemp -d)"
    trap 'rm -rf "$tmp"' EXIT
    git clone -q --depth 1 "$repo_url" "$tmp/ko-skills"
    src="$tmp/ko-skills"
    v="$(version_of < "$src/.claude-plugin/marketplace.json")"
    # ทับเฉพาะไฟล์ชื่อเดียวกัน ของอื่นในเครื่องไม่หาย (เหมือน "ติดตั้งแบบที่ 2" ใน README)
    mkdir -p "$dest/agents" "$dest/skills" "$dest/rules"
    cp -R "$src/agents/." "$dest/agents/"
    cp -R "$src/skills/." "$dest/skills/"
    cp    "$src/rules/"*.md "$dest/rules/"
    printf '%s\n' "$v" > "$stamp"
    echo "อัปเดต ko-skills เป็น $v ลง $dest แล้ว — รีสตาร์ต Claude Code เพื่อโหลดของใหม่"
    ;;
  *)
    echo "ใช้: $0 [check|apply]" >&2
    exit 2
    ;;
esac
