#!/usr/bin/env bash
# เทียบ version หลักของ ko-skills ที่ติดตั้งใน ~/.claude กับบน GitHub
#   check (ค่าเริ่มต้น) — อ่านอย่างเดียว พิมพ์ local= remote= status=
#   apply             — clone repo ล่าสุด ก๊อป skills/agents/rules ทับลง ~/.claude แล้วบันทึก version
#   changes <since> [file] — พิมพ์หัวข้อใน CHANGELOG.md ที่ใหม่กว่า <since> (file ไม่ใส่ = อ่าน stdin)
# version หลักคือ metadata.version ใน .claude-plugin/marketplace.json
set -eu

repo_url="https://github.com/Kriangsak1416/ko-skills.git"
manifest_url="https://raw.githubusercontent.com/Kriangsak1416/ko-skills/main/.claude-plugin/marketplace.json"
changelog_url="https://raw.githubusercontent.com/Kriangsak1416/ko-skills/main/CHANGELOG.md"
dest="$HOME/.claude"
stamp="$dest/ko-skills.version"

version_of() { sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' | head -n 1; }

# หัวข้อ "## X.Y.Z — วันที่" ใหม่สุดอยู่บน: พิมพ์ทุกหัวข้อจนกว่าจะเจอ version ที่ติดตั้งอยู่
# ไม่รู้ version ในเครื่อง (none) หรือหาไม่เจอใน changelog → พิมพ์แค่หัวข้อล่าสุด
changes_since() {
  awk -v since="$1" '
    { lines[NR] = $0 }
    /^## [0-9]+\.[0-9]+\.[0-9]+/ { v = $2; if (v == since) found = NR; heads[++n] = NR }
    END {
      if (n == 0) exit
      stop = found ? found : (n > 1 ? heads[2] : NR + 1)
      for (i = heads[1]; i < stop; i++) print lines[i]
    }'
}

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
    if [ "$status" = different ]; then
      echo "changes:"
      curl -fsSL --max-time 15 "$changelog_url" 2>/dev/null | changes_since "${local_v:-none}" || true
    fi
    ;;
  apply)
    tmp="$(mktemp -d)"
    trap 'rm -rf "$tmp"' EXIT
    git clone -q --depth 1 "$repo_url" "$tmp/ko-skills"
    src="$tmp/ko-skills"
    v="$(version_of < "$src/.claude-plugin/marketplace.json")"
    old_v="$(cat "$stamp" 2>/dev/null || echo none)"
    # ทับเฉพาะไฟล์ชื่อเดียวกัน ของอื่นในเครื่องไม่หาย (เหมือน "ติดตั้งแบบที่ 2" ใน README)
    mkdir -p "$dest/agents" "$dest/skills" "$dest/rules"
    cp -R "$src/agents/." "$dest/agents/"
    cp -R "$src/skills/." "$dest/skills/"
    cp    "$src/rules/"*.md "$dest/rules/"
    printf '%s\n' "$v" > "$stamp"
    echo "อัปเดต ko-skills เป็น $v ลง $dest แล้ว — รีสตาร์ต Claude Code เพื่อโหลดของใหม่"
    if [ -f "$src/CHANGELOG.md" ] && [ "$old_v" != "$v" ]; then
      echo "มีอะไรเปลี่ยน (จาก $old_v):"
      changes_since "$old_v" < "$src/CHANGELOG.md"
    fi
    ;;
  changes)
    if [ -n "${3:-}" ]; then changes_since "${2:-none}" < "$3"; else changes_since "${2:-none}"; fi
    ;;
  *)
    echo "ใช้: $0 [check|apply|changes <since> [file]]" >&2
    exit 2
    ;;
esac
