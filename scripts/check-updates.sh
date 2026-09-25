#!/usr/bin/env bash
# SessionStart hook: เช็คว่า skills/agents/rules ที่ติดตั้งใน ~/.claude ตรงกับ repo นี้ไหม
# ถ้าไม่ตรง พิมพ์รายการออก stdout เพื่อให้ Claude ถามผู้ใช้ว่าจะอัปเดตหรือไม่
# อ่านอย่างเดียว — ไม่ pull ไม่ก๊อปอะไรทั้งนั้น (นั่นคือหน้าที่ของ update-skills.sh)
set -u

repo="$(cd "$(dirname "$0")/.." && pwd)"
dest="$HOME/.claude"
# path ที่ส่งให้ git ทาง stdin ต้องเป็นแบบ Windows (C:/...) — บน Git Bash ใช้ cygpath แปลง
dest_git="$(cygpath -m "$dest" 2>/dev/null || printf '%s' "$dest")"
repo_show="$(cygpath -m "$repo" 2>/dev/null || printf '%s' "$repo")"
cd "$repo" || exit 0

# ดึงของใหม่จาก GitHub ถ้าออนไลน์ — ไม่ได้ก็ไม่เป็นไร เทียบกับที่มีในเครื่องแทน
if command -v timeout >/dev/null; then
  GIT_TERMINAL_PROMPT=0 timeout 10 git fetch -q origin main 2>/dev/null
else
  GIT_TERMINAL_PROMPT=0 git fetch -q origin main 2>/dev/null
fi

# รายการ path ทั้งหมดใน repo (HEAD) พร้อม blob hash
tree="$(git ls-tree -r --format='%(objectname) %(path)' HEAD skills agents rules)"

# ไฟล์ที่ติดตั้งแล้ว → hash ทีเดียวทั้งชุด (git จะแปลง CRLF ให้ตาม .gitattributes เหมือนตอน commit)
existing="$(printf '%s\n' "$tree" | while read -r _ path; do
  [ -f "$dest/$path" ] && printf '%s\n' "$path"
done)"
installed=""
if [ -n "$existing" ]; then
  installed="$(paste -d' ' \
    <(printf '%s\n' "$existing" | sed "s#^#$dest_git/#" | git hash-object --stdin-paths) \
    <(printf '%s\n' "$existing"))"
fi

# ต่างกัน = ไม่มีในเครื่อง, hash ไม่ตรง หรือ GitHub มี commit ใหม่ที่แตะไฟล์นั้น
changed="$(
  {
    printf '%s\n' "$tree" | awk -v inst="$installed" '
      BEGIN { n = split(inst, lines, "\n"); for (i = 1; i <= n; i++) { split(lines[i], f, " "); have[f[2]] = f[1] } }
      { if (!($2 in have) || have[$2] != $1) print $2 }'
    git diff --name-only HEAD origin/main -- skills agents rules 2>/dev/null
  } | sed -E 's#^((skills|agents|rules)/[^/]+).*#\1#' | sort -u
)"
[ -z "$changed" ] && exit 0

behind="$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)"

echo "[ko-skills] มี skill/agent/rule ใน repo ที่ต่างจากที่ติดตั้งใน ~/.claude:"
printf '%s\n' "$changed" | sed 's/^/  - /'
[ "$behind" -gt 0 ] && echo "(GitHub ใหม่กว่าเครื่องนี้ $behind commit — update-skills.sh จะ pull ให้)"
echo "ให้ถามผู้ใช้หนึ่งครั้งด้วย AskUserQuestion ว่าจะอัปเดต skills ตอนนี้ไหม"
echo "ถ้าตอบว่าอัปเดต ให้รัน: bash \"$repo_show/scripts/update-skills.sh\""
echo "ถ้าตอบว่าไม่ ไม่ต้องถามซ้ำอีกในเซสชันนี้"
