# Changelog

มีอะไรเปลี่ยนในแต่ละ version หลัก (`metadata.version` ใน `.claude-plugin/marketplace.json`)
ใหม่สุดอยู่บน — `update-skill-ko` และสคริปต์อัปเดตอ่านไฟล์นี้เพื่อบอกผู้ใช้ว่าได้อะไรใหม่

**คนดูแล repo:** bump version เมื่อไหร่ เพิ่มหัวข้อ `## X.Y.Z — YYYY-MM-DD` บนสุดทุกครั้ง
เขียนจากมุมคนใช้ (อะไรเปลี่ยนในพฤติกรรม / ต้องทำอะไรเพิ่ม) ไม่ใช่รายการไฟล์

## 2.16.0 — 2026-11-28

- `ship`: งานหน้าบ้านที่ต้องแก้ API **ไม่สร้าง `git worktree` แล้ว** แตก branch เลขเดียวกันใน checkout ของ API repo เอง
  API ที่รันบนเครื่องเสิร์ฟ branch นั้นเลย ไม่ต้องเปิด `php -S` / port `8000 + N` / ก๊อป `.env` / `composer install` แยก
- ก่อนสลับ branch ของ API จะเช็คว่างานเดิม commit และ push แล้ว ถ้ายังค้างจะถามก่อน ; แตกด้วย `--no-track`
  ไม่ให้ branch ผูก upstream กับ develop ; stage ทีละไฟล์ (ไม่ `git add -A`) เพราะ checkout มีไฟล์ config ของเครื่องค้าง
- push งาน API ทุกครั้งที่จบช่วงงาน เสร็จแล้วกลับไป develop และ pull ; ตอนขึ้น PRD ลบ branch API ด้วย `branch -d`
- ถ้ายังมี worktree แบบเก่าค้าง Claude จะรายงานว่ามีตัวไหนและมีงานที่ยังไม่ push ไหม แต่จะไม่ลบเองโดยไม่ถาม
- `settings.json` ตัวอย่างปิด skill ในตัวของ Claude Code 2 ตัวด้วย `skillOverrides`: `ship-local` (รับชื่อ `/ship` ซ้ำกับ
  `ship` ของ repo นี้) และ `steward` — **ต้องก๊อป `skillOverrides` ไปไว้ใน `~/.claude/settings.json` แล้วรีสตาร์ต** `/ship` จึงจะเป็น flow ของทีม

## 2.15.0 — 2026-11-25

- เพิ่ม `react-best-practices` (จาก vercel-labs/agent-skills): กฎ performance ของ React/Next.js ใช้เองตอนเขียน
  หรือรีวิว React กฎกลุ่ม `server-*` ใช้ไม่ได้กับเว็บที่ static export ขึ้น Apache
- เพิ่ม `web-design-guidelines` (จาก vercel-labs/agent-skills): สั่ง "ตรวจ UI" / "check accessibility" แล้วรายงานเป็น
  `ไฟล์:บรรทัด` ใช้ตรวจอย่างเดียว การเลือกดีไซน์ยังเป็นของ `ko-design`
- ลงแบบ plugin: ทั้งสองตัวอยู่ใน `/plugin install vercel-skills@ko-skills`
- **เปลี่ยนชื่อ plugin** `anthropic-example-skills` เป็น `example-skills` เพราะ Claude Code สงวนชื่อที่ขึ้นต้นด้วย
  `anthropic-` ใครลงแบบ plugin ไว้ต้องถอนชื่อเดิม แล้ว `/plugin install example-skills@ko-skills`
  คนที่ใช้แบบก๊อปลง `~/.claude` ไม่ต้องทำอะไร
- แนะนำ plugin เพิ่ม 4 ตัว (จาก claude-plugins-official): `php-lsp`, `typescript-lsp`, `context7` และ
  `security-guidance` มีวิธีติดตั้งใน README และใส่ไว้ใน `settings.json` ตัวอย่าง
- **ต้องติดตั้งเองครั้งเดียวต่อเครื่อง** (`update-skill-ko` ไม่ได้ลงให้): ลง language server ด้วย
  `npm i -g intelephense typescript-language-server typescript@5.9.3` แล้วรัน
  `claude plugin install <ชื่อ>@claude-plugins-official` ทีละตัว
- อย่าใช้ TypeScript 7 กับ `typescript-lsp` เพราะไม่มี `tsserver.js`
- `context7` ต้อง login ผ่าน `/mcp` หรือตั้ง `CONTEXT7_API_KEY` และห้ามใส่ข้อมูลคนไข้ในคำค้น
- `security-guidance` รีวิว diff ด้วย Opus ตอนจบ turn และตอน commit/push จึงใช้โควตาเพิ่ม

## 2.14.0 — 2026-11-24

- แนะนำ plugin `chrome-devtools-mcp` (จาก claude-plugins-official): ให้ Claude เปิด Chrome จริงมาดู
  console, network, performance, Lighthouse และ a11y มีวิธีติดตั้งใน README และใส่ไว้ใน `settings.json` ตัวอย่าง
- **ต้องติดตั้งเองครั้งเดียวต่อเครื่อง** (`update-skill-ko` ไม่ได้ลงให้):
  `/plugin marketplace add anthropics/claude-plugins-official` แล้ว
  `/plugin install chrome-devtools-mcp@claude-plugins-official`
- ต้องมี Chrome รุ่น stable ปัจจุบัน และ Node.js 20.19+ / 22.12+ / 23+
- Google เก็บสถิติการใช้งานเป็นค่าเริ่มต้น ปิดได้ด้วย `CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS=1`

## 2.13.0 — 2026-11-21

- เพิ่ม `find-skills` (จาก vercel-labs/skills): ถาม "มี skill สำหรับ X ไหม" แล้วมันจะค้นใน
  [skills.sh](https://skills.sh/) ผ่าน `npx skills find` เช็คยอดติดตั้งกับแหล่งที่มาก่อนแนะนำ
  และติดตั้งให้ด้วย `npx skills add <owner/repo@skill> -g -y`
- **ต้องมี Node.js 22.20 ขึ้นไป** (CLI `skills` รันผ่าน npx ไม่ต้องติดตั้งแยก)
- skill ที่ลงผ่าน `npx skills add -g` จะไปอยู่ใน `~/.claude/skills` ตรง ๆ ไม่ได้เข้า repo นี้
  และ `update-skill-ko` จะไม่อัปเดตให้ ใช้ `npx skills update` แทน
- ลงแบบ plugin: `/plugin install vercel-skills@ko-skills`

## 2.12.0 — 2026-11-21

- `ship` อ่านธรรมเนียมของแต่ละ repo ให้ครบขึ้นก่อนเริ่ม: นอกจาก dev/develop และชื่อ feature
  branch แล้ว ดูด้วยว่า production เป็น `main` หรือ `master`, release branch เป็น
  `v.X.Y.Z` หรือ `release/X.Y.Z`, tag มี `v.` หรือไม่ และตั้งชื่อ PR ตาม release ก่อน ๆ
  - บันทึกธรรมเนียมของ PMEC ไว้: `develop` / `master`, `feature/<slug>` ไม่มี `#N`,
    `release/X.Y.Z`, tag `X.Y.Z` และ flow finish release เข้า develop แล้วเปิด PR
    develop → master ก่อน tag และ build จาก master
- `ship` ห้าม merge feature branch เข้า main/master ตรง ๆ และบอกวิธีแก้ถ้าเกิดไปแล้ว
  (ทำ release ย้อนหลังจาก dev ไม่ revert ไม่แก้ประวัติ)
- `ship` build และ deploy ได้เฉพาะจาก commit บน main/master ที่ติด tag แล้ว
- `ship` บอกวิธี push เมื่อ git ขึ้น "Repository not found" เพราะ repo ย้ายไป organization
  (ใช้ login ของ `gh` เฉพาะคำสั่งนั้น ไม่แก้ config ของเครื่อง)
- เทมเพลต PR ของ `ship`: ตั้งชื่อตาม PR release ก่อน ๆ ของ repo และต้องเขียนใน PR
  ถ้ามีอะไรขึ้นผิดลำดับ

## 2.11.1 — 2026-11-21

- `ship` + rule `branch-before-work`: repo `ko-skills` เองไม่ต้องแตก branch แล้ว
  แก้ commit และ push บน `main` ได้เลย ไม่มี release branch, PR หรือ tag
  การ bump `metadata.version` + `CHANGELOG.md` ใน commit เดียวกันถือเป็นการ release
  repo อื่นยังใช้ flow เดิมทุกอย่าง

## 2.11.0 — 2026-11-21

- เพิ่ม `framer-motion`: ถามว่า "ใช้ framer-motion ได้ไหม" แล้วมันจะเช็ค peer dependency,
  เวอร์ชัน React, animation library ที่มีอยู่ และ CSP ตอน deploy ก่อนแนะนำ
  (โปรเจกต์ Vue / Laravel ใช้ไม่ได้ จะบอกแล้วหยุด) ถ้าใช้ได้ก็ใส่ animation แบบที่ทีมใช้:
  `motion/react` + `LazyMotion` ให้ bundle เล็ก, `MotionConfig reducedMotion="user"`
  และไม่ให้ animation เล่นซ้ำทุกรอบที่ dashboard ดึงข้อมูล
- อยู่ใน `team-skills` (`/plugin install team-skills@ko-skills`)

## 2.10.0 — 2026-11-09

- เพิ่ม `thai-voiceover`: แปลงบทพากย์ภาษาไทยเป็น WAV แยกตาม frame พร้อม `audio_meta.json`
  ที่มีเวลาของแต่ละคำ เอาไปใช้ทำวิดีโอกับ HyperFrames ได้ทันที (engine เสียงของ HyperFrames เองพูดไทยไม่ได้)
  - ค่าเริ่มต้นใช้ PyThaiTTS บน CPU ไม่ต้องติดตั้งอะไรเพิ่มนอกจาก `uv` กับ ffmpeg
    ครั้งแรกที่รันจะดาวน์โหลดโมเดลให้เอง
  - เครื่องที่มี GPU (CUDA) และส่งไฟล์เสียงต้นแบบมา จะใช้ ThonburianTTS โคลนเสียงแทน
    น้ำหนักโมเดลเป็น CC BY-NC-SA 4.0 **ห้ามใช้เชิงพาณิชย์** และทางนี้ยังไม่ได้ทดสอบบนเครื่องจริง

## 2.9.0 — 2026-10-30

- `update-skill-ko` บอกว่ามีอะไรเปลี่ยนบ้าง ทั้งตอนถามและหลังอัปเดต โดยดึงจากไฟล์นี้
  เฉพาะ version ที่ใหม่กว่าในเครื่อง
- เพิ่ม `CHANGELOG.md` (ไฟล์นี้)
- **ลบ `scripts/check-updates.sh` และ `scripts/update-skills.sh`** — อัปเดตผ่าน `update-skill-ko`
  ทางเดียว ถ้าเคยใส่ hook `SessionStart` ที่ชี้ไป `check-updates.sh` ใน `~/.claude/settings.json`
  **ต้องลบ hook นั้นออกเอง** ไม่อย่างนั้นจะ error ทุกครั้งที่เปิด Claude Code หลัง pull repo

## 2.8.1 — 2026-10-30

- `mcp-builder` อัปเดตตาม anthropics/skills ล่าสุด: server ใหม่ใช้ TypeScript SDK v2
  (`@modelcontextprotocol/server`) โปรเจกต์เดิมที่เป็น v1 ทำต่อด้วย v1 และบอกวิธี migrate
- `THIRD_PARTY_NOTICES.md` บันทึก commit ต้นทางของทุก skill ที่รวมมาจากภายนอก

## 2.8.0 — 2026-10-30

- `coder` / `fixer` / `reviewer` โหลด skill ของตัวเองตอนเริ่มงาน (ฟิลด์ `skills:`)
  — coder: karpathy-guidelines + verification-before-completion,
  fixer: debug-mantra + verification-before-completion, reviewer: scrutinize
- `boss` ห้ามใช้ built-in agent (`Explore`, `general-purpose`) แทนทีม
- `settings.json` ตัวอย่างเพิ่ม `CLAUDE_CODE_SUBAGENT_MODEL=sonnet`
  **ต้องก๊อปส่วน `env` ไปใส่ `~/.claude/settings.json` เอง** และต้องใช้ Claude Code v2.1.251 ขึ้นไป
- ลงแบบ plugin: ลง `9arm-skills` และ `superpowers-skills` ด้วย agent จึงจะได้ skill ครบ

## 2.7.0 — 2026-10-30

- เพิ่ม `brainstorming` (จาก obra/superpowers): โจทย์ยังไม่ชัดหรือสั่ง "ช่วยคิด" จะถามทีละข้อ
  เสนอ 2-3 ทาง เขียน design doc ให้อนุมัติ (เก็บนอก repo) แล้วส่งต่อ `boss`
- เพิ่ม `verification-before-completion` และ rule `verify-before-done.md`:
  ห้ามบอกว่าเสร็จ/ผ่านถ้ายังไม่ได้รันพิสูจน์ รวมงานเล็กที่ lead ทำเอง
- เพิ่ม `receiving-code-review`: ตรวจ feedback กับโค้ดจริงก่อนแก้
- `boss`: pre-flight scan, ledger กันหลงหลัง compaction, เลือก model ตามงาน
- `reviewer`: รีวิว 2 ขั้น ตรงสเปกก่อน แล้วค่อยคุณภาพโค้ด
- plugin ใหม่ `superpowers-skills`

## 2.6.0 — 2026-10-28

- `ship`: กฎแตก branch กลับเป็นแบบ 2.2.0, เลข `#N` นับจาก origin, ขึ้น PRD แล้วลบ feature branch ใน local
- งานหน้าบ้านที่ต้องแก้ API: แตก branch เลขเดียวกันใน API repo เป็น `git worktree` รันที่ port `8000 + N`
  แก้ API แบบเพิ่มอย่างเดียว และตอนขึ้น PRD ฝั่ง API ขึ้นก่อน

## 2.5.0 — 2026-10-27

- เพิ่ม `security-audit` (จาก cloudflare/security-audit-skill) แก้ validator ให้รันบน Windows ได้
- plugin ใหม่ `cloudflare-skills`

## 2.4.0 — 2026-10-26

- เพิ่ม `thai-memo`: ร่างบันทึกข้อความราชการเป็น .docx ตามแบบสารบรรณ
  ค่าประจำหน่วยงานเก็บใน `~/.claude/thai-memo.json`

## 2.3.0 — 2026-10-26

- `ship`: ใช้ feature branch เดิมต่อจนกว่าจะขึ้น PRD (ยกเลิกใน 2.6.0)

## 2.2.0 — 2026-10-20

- เพิ่ม rule `branch-before-work.md`: แตก feature branch ก่อนแก้โค้ด และห้าม commit ลง dev/main

## 2.1.0 — 2026-09-25

- เพิ่ม `update-skill-ko` เช็ค version กับ GitHub แล้วอัปเดตให้
- hook `check-updates.sh` ตอนเปิดเซสชัน + `update-skills.sh`

## 2.0.0 — 2026-09-16

- จัดโครงสร้างใหม่ตาม anthropics/skills และลงผ่าน `/plugin marketplace add` ได้
- เพิ่ม skill จาก Anthropic และ rules `karpathy-by-default`, `skills-explain-in-thai`
