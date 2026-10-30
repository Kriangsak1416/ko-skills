# ko-skills

> รวม skills, agents และ rules สำหรับ [Claude Code](https://code.claude.com) ที่ใช้งานจริงในเครื่องของ ko
> จัดโครงสร้างตามแบบ [anthropics/skills](https://github.com/anthropics/skills) — skill ละโฟลเดอร์ มี `SKILL.md` เป็นหัวใจ

Skill คือโฟลเดอร์ที่มีคำสั่ง สคริปต์ และไฟล์อ้างอิง ซึ่ง Claude โหลดขึ้นมาเองเมื่องาน
ตรงกับที่ `description` บอกไว้ ทำให้สั่งงานซ้ำ ๆ ได้ผลเหมือนเดิมทุกครั้ง — ตั้งแต่
วิธีแตกงานให้ subagent, git flow ของทีม, การตรวจก่อนขึ้น PRD ไปจนถึงสูตร build Next.js ขึ้น Apache

อ่านเพิ่ม:
- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Agent Skills specification](http://agentskills.io)

# เกี่ยวกับ repo นี้

แกนหลักคือ **ทีม AI ที่แบ่งงานกันเอง** — **Opus** เป็น tech lead (คิด วางแผน แตกงาน
รีวิว รวมงาน) และ **Sonnet** เป็น engineer ที่ลงมือเขียนโค้ดจริง — ครอบด้วย skill สำหรับ
git flow, QA ก่อน release และ deploy ส่วนที่เหลือเป็น skill ที่รวบรวมมาจากภายนอก
(Anthropic, 9arm, Karpathy, Cloudflare, superpowers) ซึ่งเก็บไว้ตามต้นฉบับ ดูที่มาและ license ได้ที่
[THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)

ทุก skill อยู่ในโฟลเดอร์ของตัวเองใต้ [`skills/`](./skills) และมี `SKILL.md`
เป็นไฟล์เดียวที่ Claude ต้องอ่าน ไฟล์อื่นในโฟลเดอร์ (references, scripts) ถูกอ้างจาก
`SKILL.md` ตามต้องการ

# โครงสร้าง

```
.claude-plugin/marketplace.json   # ลงผ่าน /plugin marketplace add ได้เลย
skills/                           # skill ละโฟลเดอร์ (SKILL.md + references/scripts)
agents/                           # subagent ที่ boss ใช้: coder / fixer / reviewer / scout
rules/                            # กฎที่โหลดทุกเซสชัน (ต้องก๊อปมือ — plugin ไม่รองรับ rules)
settings.json                     # ตัวอย่าง settings: lead = opus, effort = high, permission พื้นฐาน
scripts/                          # check-updates.sh (hook เช็คของใหม่ตอนเปิดเซสชัน) + update-skills.sh (pull แล้วก๊อปทับ)
template/SKILL.md                 # เทมเพลตเริ่ม skill ใหม่
THIRD_PARTY_NOTICES.md            # ที่มาและ license ของ skill ที่รวมมาจากที่อื่น
```

# Skills ใน repo นี้

## ทีมงาน & workflow (เขียนเอง)

| skill | ใช้ตอนไหน |
|---|---|
| [`boss`](./skills/boss) | playbook ของ lead: plan → dispatch ให้ `coder` ขนานกัน → verify ด้วยการรัน test เอง → integrate ใช้กับงานที่ทำหลายขั้นหรือแตะ 3 ไฟล์ขึ้นไป |
| [`ship`](./skills/ship) | git flow ของทีม: branch `#N_slug` → commit ภาษาไทย → push → release `v.X.Y.Z` → เปิด PR dev → main ("อัพงาน", "ขึ้น PRD", "เปิด PR") |
| [`qa`](./skills/qa) | ตรวจก่อนขึ้น PRD 4 เฟส: build readiness → bug audit → web security (OWASP + PDPA) → migrations แล้วตัดสิน GO / NO-GO |
| [`next-static-pack`](./skills/next-static-pack) | build Next.js เป็น static export แก้ชื่อไฟล์ RSC บน Windows แล้วแพ็กพร้อม `.htaccess` (CSP/headers) ขึ้น Apache ที่ไม่มี Node |
| [`ollama-worker`](./skills/ollama-worker) | โยนงานเว็บชิ้นเล็ก ๆ (HTML fragment, CSS class, Tailwind component, ฟังก์ชันสั้น ๆ, mock data) ให้โมเดล local บน Ollama ทำฟรี Claude เป็นคนเขียน brief เรียก API แล้วตรวจผลเอง ใช้ครั้งแรกในเครื่องจะถามก่อนว่าจะใช้ไหม / host / model แล้วจำไว้ใน `~/.claude/ollama-worker.json` ("ให้ ollama ทำ", "ใช้ qwen", "ประหยัด token") |
| [`thai-memo`](./skills/thai-memo) | ร่างบันทึกข้อความราชการเป็น .docx ตามแบบสารบรรณ (ตราครุฑ, TH SarabunIT๙, ช่องความเห็น ผอ., สิ่งที่ส่งมาด้วย) ทั้งแบบขออนุมัติฉบับเดียว หนังสือถึง สสจ. และคู่หนังสือ + ใบเสนอ ผอ. ค่าประจำหน่วยงานเก็บใน `~/.claude/thai-memo.json` ("บันทึกข้อความ", "ใบเสนอ ผอ.", "ขอลงนาม") |
| [`update-skill-ko`](./skills/update-skill-ko) | เทียบ version หลักของ skills/agents/rules ที่ติดตั้งใน `~/.claude` กับ repo บน GitHub ถ้าไม่ตรงจะถามก่อนแล้วอัปเดตให้ ("update-skill-ko", "อัปเดต skill") |

## วินัยวิศวกร (รวมจากภายนอก)

| skill | ที่มา | ใช้ตอนไหน |
|---|---|---|
| [`karpathy-guidelines`](./skills/karpathy-guidelines) | multica-ai (MIT) | กันนิสัยเสียของ LLM: อย่าเดาแล้วลุย อย่าเขียนเกิน แก้เฉพาะจุด กำหนดเกณฑ์ "เสร็จ" ก่อนทำ |
| [`debug-mantra`](./skills/debug-mantra) | 9arm | เริ่มไล่บั๊ก — บังคับลำดับ repro → fail path → falsify สมมติฐาน → ไล่ทวนทุกการทดลอง |
| [`scrutinize`](./skills/scrutinize) | 9arm | รีวิว plan / PR / diff แบบคนนอก ถามก่อนว่าจำเป็นไหม มีทางง่ายกว่าไหม แล้วไล่ code path จริง |
| [`post-mortem`](./skills/post-mortem) | 9arm | เขียนบันทึกบั๊กหลังแก้เสร็จ (root cause / fix / validation / หลุดมาได้ยังไง) |
| [`management-talk`](./skills/management-talk) | 9arm | แปลงเรื่อง technical เป็นภาษาผู้บริหาร แยกทรงตามช่องทาง JIRA / Slack / standup / email |

## จาก superpowers (MIT)

คัดมาจาก [obra/superpowers](https://github.com/obra/superpowers) เฉพาะตัวที่ไม่ทับ `boss`/`ship`
ไม่ได้ลง SessionStart hook ของต้นทาง และไม่เอาตัวคุมงาน (subagent-driven-development, writing-plans,
worktrees, finishing-a-development-branch) มาด้วย

| skill | ใช้ตอนไหน |
|---|---|
| [`brainstorming`](./skills/brainstorming) | งานใหม่ที่โจทย์ยังไม่ชัด (เช่น requirement จากฝ่ายคลินิก/ฝ่ายบริหาร) หรือสั่ง "ช่วยคิด" / "ออกแบบก่อน" — ถามทีละข้อ ทวนความเข้าใจ เสนอ 2-3 ทางให้เลือก แล้วเขียน design doc ให้อนุมัติก่อนสร้าง จากนั้นส่งต่อให้ `boss` (doc เก็บนอก repo ที่ `~/.claude/brainstorming/<repo>/` ไม่ commit) |
| [`verification-before-completion`](./skills/verification-before-completion) | ก่อนบอกว่าเสร็จ / แก้แล้ว / test ผ่าน หรือก่อน commit / PR — ต้องมีผลคำสั่งที่รันในรอบนี้ยืนยัน |
| [`receiving-code-review`](./skills/receiving-code-review) | ได้ feedback จาก `reviewer` หรือคอมเมนต์ใน PR — ตรวจกับโค้ดจริงก่อนแก้ แย้งได้ถ้าผิด ไม่รับมาแก้ทันทีแบบไม่คิด |

## ความปลอดภัย (รวมจากภายนอก)

| skill | ที่มา | ใช้ตอนไหน |
|---|---|---|
| [`security-audit`](./skills/security-audit) | Cloudflare (MIT) | ถามเรื่องความปลอดภัย / รีวิวเฉพาะจุดใช้แบบ guidance ถ้าสั่ง "security audit โค้ดนี้" แบบเต็มจะรัน 6 เฟส: recon → hunting ตาม coverage ledger → ให้ agent อีกตัวพิสูจน์ซ้ำ → `findings.json` → ตรวจซ้ำ → `REPORT.md` ผลเขียนไว้นอก repo ที่ `~/security-audit-skill/<repo>/run-N` ต้องมี Node สำหรับ validator (แก้ให้รันบน Windows ได้แล้ว ดู [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)) |

## ตัวอย่างจาก Anthropic (Apache 2.0)

| skill | ใช้ตอนไหน |
|---|---|
| [`skill-creator`](./skills/skill-creator) | สร้าง skill ใหม่ ปรับ skill เดิม รัน eval วัดผล และจูน description ให้ trigger แม่นขึ้น |
| [`mcp-builder`](./skills/mcp-builder) | สร้าง MCP server คุณภาพดี ทั้ง Python (FastMCP) และ Node/TypeScript (MCP SDK) |
| [`webapp-testing`](./skills/webapp-testing) | ทดสอบเว็บแอปในเครื่องด้วย Playwright — ตรวจ UI, ถ่าย screenshot, ดู console log |
| [`frontend-design`](./skills/frontend-design) | ทิศทางดีไซน์ UI ให้ดูตั้งใจ ไม่ใช่หน้าตา template เริ่มต้น |
| [`doc-coauthoring`](./skills/doc-coauthoring) | เขียนเอกสาร / proposal / spec / decision doc แบบมีขั้นตอน ส่ง context → ปรับซ้ำ → ตรวจว่าคนอ่านเข้าใจ |

## Agents ([`agents/`](./agents))

subagent ที่ `boss` ส่งงานให้ — ทุกตัวเป็น Sonnet

| agent | หน้าที่ |
|---|---|
| `coder` | เขียน/แก้โค้ดตามสเปกที่ lead ตัดสินใจแล้ว |
| `fixer` | ดีบัก หาสาเหตุจริง แก้แบบน้อยที่สุด พร้อมพิสูจน์ |
| `reviewer` | รีวิว diff หาบั๊ก (อ่านอย่างเดียว ไม่แก้) |
| `scout` | สำรวจโค้ดเบส หา call site ก่อนวางแผน |

## Rules ([`rules/`](./rules))

กฎที่ถูกโหลดทุกเซสชันอัตโนมัติ ทำให้ไม่ต้องพิมพ์ `/skill` เอง

| rule | ผล |
|---|---|
| `delegate-by-default.md` | งานหลายขั้นหรือแตะ 3 ไฟล์ขึ้นไปเข้าโหมด `boss` เอง งานเล็ก lead ทำเอง |
| `karpathy-by-default.md` | ใช้ `karpathy-guidelines` ทุกครั้งที่เขียน/แก้/รีวิวโค้ด |
| `branch-before-work.md` | ก่อนแก้โค้ดและก่อน commit เช็ค branch ถ้าอยู่บน dev/develop/main จะแตก feature branch ผ่าน `ship` ก่อนเสมอ |
| `verify-before-done.md` | ก่อนบอกว่างานเสร็จ / ก่อน commit ใช้ `verification-before-completion` เสมอ รวมงานเล็กที่ lead ทำเอง |
| `qa-before-prd.md` | ก่อน build/แพ็ก/release ขึ้น production ถามหนึ่งครั้งว่าจะรัน `qa` ก่อนไหม |
| `skills-explain-in-thai.md` | ทุก skill สื่อสารกับผู้ใช้เป็นภาษาไทย แม้ `SKILL.md` เป็นอังกฤษ |

# ติดตั้ง

## แบบที่ 1 — plugin marketplace (Claude Code)

```
/plugin marketplace add Kriangsak1416/ko-skills
```

แล้วเลือกลงเป็นชุด:

```
/plugin install team-skills@ko-skills               # boss + agents, karpathy-guidelines, ship, qa, next-static-pack, ollama-worker, update-skill-ko
/plugin install 9arm-skills@ko-skills               # debug-mantra, scrutinize, post-mortem, management-talk
/plugin install anthropic-example-skills@ko-skills  # skill-creator, mcp-builder, webapp-testing, frontend-design, doc-coauthoring
/plugin install cloudflare-skills@ko-skills         # security-audit
/plugin install superpowers-skills@ko-skills        # brainstorming, verification-before-completion, receiving-code-review
```

plugin ไม่รองรับ `rules/` — ถ้าอยากได้พฤติกรรมอัตโนมัติ (แตกงานเอง, ถาม QA ก่อน build)
ก๊อป rules ลงเครื่องเพิ่มตามแบบที่ 2

## แบบที่ 2 — ก๊อปมือทั้งเครื่อง

```bash
git clone https://github.com/Kriangsak1416/ko-skills.git
cd ko-skills
mkdir -p ~/.claude/agents ~/.claude/skills ~/.claude/rules
cp -R agents/. ~/.claude/agents/
cp -R skills/. ~/.claude/skills/
cp    rules/*.md ~/.claude/rules/
```

ทับเฉพาะไฟล์ชื่อเดียวกัน agent/skill/rule อื่นที่มีอยู่ไม่หาย
แล้วเช็คว่า `~/.claude/settings.json` มี `"model": "opus"` หรือยัง — `boss` คาดว่า lead
เป็น opus ถ้ายังไม่ตรงตั้งด้วย `/model opus` หรือเทียบกับ [`settings.json`](./settings.json)
จากนั้นรีสตาร์ต Claude Code

## อัปเดต — ให้ Claude ถามเองเมื่อมีของใหม่ (สำหรับแบบที่ 2)

เพิ่ม hook ใน `~/.claude/settings.json` ชี้ไปที่ clone ของ repo นี้ (เปลี่ยน path ให้ตรงเครื่อง):

```json
"hooks": {
  "SessionStart": [
    {
      "matcher": "startup",
      "hooks": [
        { "type": "command", "command": "bash \"D:/path/to/ko-skills/scripts/check-updates.sh\"", "timeout": 30 }
      ]
    }
  ]
}
```

ทุกครั้งที่เปิด Claude Code `check-updates.sh` จะ `git fetch` แล้วเทียบ `skills/` `agents/` `rules/`
ใน repo กับที่ติดตั้งใน `~/.claude` ทีละไฟล์ ถ้ามีอะไรต่างกัน Claude จะบอกว่า skill ไหนเปลี่ยน
แล้วถามหนึ่งครั้งว่าจะอัปเดตไหม — ตอบว่าอัปเดตแล้ว Claude จะรัน `update-skills.sh`
(`git pull --ff-only` + ก๊อปทับเหมือนขั้นติดตั้ง) ตอบว่าไม่ก็ไม่ถามซ้ำจนกว่าจะเปิดเซสชันใหม่
ไม่มีอะไรต่างกันหรือออฟไลน์ก็เงียบ ๆ ไม่รบกวน

อัปเดตเองโดยไม่รอถามก็ได้: `bash scripts/update-skills.sh`

แบบที่ 1 (plugin) ไม่ต้องใช้ตัวนี้ — อัปเดตผ่าน `/plugin` ได้เลย

## เช็ค version กับ GitHub — skill `update-skill-ko`

พิมพ์ `update-skill-ko` ในเซสชันไหนก็ได้ ไม่ต้องมี clone ของ repo ในเครื่อง Claude จะเทียบ
version หลัก (`metadata.version` ใน [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json))
บน GitHub กับที่บันทึกไว้ใน `~/.claude/ko-skills.version` ถ้าไม่ตรงกันจะถามก่อน แล้วค่อย clone
ของล่าสุดมาก๊อปทับให้

**คนดูแล repo:** แก้อะไรใน `skills/` `agents/` `rules/` แล้วต้อง bump `metadata.version` ทุกครั้ง
ไม่อย่างนั้นเครื่องอื่นเช็คไม่เจอว่ามีของใหม่

## แบบที่ 3 — เฉพาะโปรเจกต์

ก๊อป `skills/`, `agents/`, `rules/` ไปไว้ใต้ `.claude/` ของโปรเจกต์นั้น
(`.claude/skills/`, `.claude/agents/`, `.claude/rules/`) แล้ว commit เข้า git
ทีมทั้งทีมได้ใช้เหมือนกันโดยไม่ต้องติดตั้งอะไร

## GitHub CLI (สำหรับ `/ship`)

`ship` ใช้ `gh` ตอนเปิด PR รันครั้งเดียวต่อเครื่อง:

```powershell
winget install --id GitHub.cli --accept-source-agreements --accept-package-agreements
gh auth login --hostname github.com --git-protocol https --web
```

ข้ามได้ — ถ้าตอน `/ship` ถึงขั้นเปิด PR แล้วยังไม่มี `gh` skill จะติดตั้งและพา login ให้เองตอนนั้น

# วิธีใช้

**สั่งงานตามปกติ ไม่ต้องพิมพ์อะไรพิเศษ**

```
เพิ่มระบบ login ด้วย JWT พร้อม test
```

`rules/delegate-by-default.md` ทำให้งานที่ต้องทำหลายขั้นหรือแตะตั้งแต่ 3 ไฟล์ขึ้นไป
เข้าโหมด lead + engineers เอง งานเล็กแค่ไม่กี่บรรทัด lead ทำเองเลย และจะบอกคุณ
1 บรรทัดก่อนเริ่มว่าเลือกทางไหน พิมพ์ `/boss <งาน>` ถ้าอยากบังคับให้แตกงานแน่ ๆ
หรือบอกว่า "ทำเองเลย ไม่ต้องใช้ subagent" ถ้าอยากปิดโหมดนี้เป็นครั้ง ๆ

Opus จะ: สำรวจโค้ด → ตัดสินใจดีไซน์เอง → แตกเป็นงานย่อยที่**ไม่แก้ไฟล์ทับกัน** →
ส่ง `coder` หลายตัวขนานกัน → **รัน test เองเพื่อตรวจ** (ไม่เชื่อรายงานของ engineer ลอย ๆ) →
สั่งแก้ถ้าไม่ผ่าน → รวมงานและสรุปให้คุณ

## `/ship` — อัพงานขึ้น git

เรียกด้วย `/ship` หรือพิมพ์ธรรมดาว่า "commit ให้หน่อย" / "อัพงาน" / "ทำ release v.1.1.0" / "ขึ้น PRD"

```
งานปกติ   dev → แตก branch '#1_add_text_builder' → ทำงาน → commit (ภาษาไทย สั้น ๆ) → push
ขึ้น PRD   dev → แตก branch 'v.1.0.0' → merge feature → รัน test →
           finish release (merge main + merge กลับ dev + ลบ branch + tag) →
           ลบ feature branch ที่ขึ้น PRD แล้ว (เฉพาะ local) → เปิด PR dev → main
```

ไม่ต้องสั่งแตก branch เอง — `rules/branch-before-work.md` ทำให้ทุกครั้งที่สั่งงานแก้โค้ด
ขณะอยู่บน dev/develop/main Claude จะแตก `#N_slug` ก่อนเริ่มงาน และไม่ commit ลง dev/main ตรง ๆ

งานหน้าบ้านที่ต้องแก้ API ด้วย — ทุกโปรเจคใช้ API repo เดียวกัน (ถาม path ครั้งแรกแล้วจำไว้ใน
`~/.claude/ship.json`) Claude จะแตก branch เลขเดียวกันใน API เป็น `git worktree` แยกโฟลเดอร์
(`<api>.wt/57`) รันที่ port `8000 + N` ทำให้หลายโปรเจครัน API ของตัวเองพร้อมกันได้ แก้ API
แบบเพิ่มอย่างเดียว (จะแก้/ลบ endpoint เดิมต้องถามก่อน) และตอนขึ้น PRD ฝั่ง API ขึ้นก่อนหน้าบ้าน

PR ตั้ง title เป็น `v.1.0.0 - 2026-08-01` และ description ไล่ว่าอัพอะไร ทดสอบอะไร
มีผลกระทบอะไร — เทมเพลตอยู่ที่ [`skills/ship/references/pr-template.md`](./skills/ship/references/pr-template.md)

สิ่งที่ skill จะไม่ทำเด็ดขาด: force push, rewrite history ที่ push ไปแล้ว,
merge PR ของตัวเอง, เขียนใน PR ว่าทดสอบผ่านทั้งที่ไม่ได้รัน

## `/qa` — ตรวจก่อนขึ้น PRD

1. **Build readiness** — รัน build/typecheck/lint จริง, env ครบไหม, dev-only code หลุดไหม
2. **Bug audit** — logic / error handling / DB / concurrency พร้อม severity และ `file:line`
3. **Web security audit** — 10 หมวดตาม OWASP Top 10 + API Security Top 10: secret ใน bundle,
   auth/session, **IDOR**, injection/XSS, CSRF/CORS/SSRF, headers+CSP, upload/rate limit,
   supply chain, **ข้อมูลผู้ป่วย/PDPA**, endpoint ที่ไม่ควรเปิด
4. **Migrations** — fresh + production-like, rollback, MariaDB 5.5 (utf8mb4 index 191)

จบด้วยตาราง severity, รายการ blocker, migration runbook และ **GO / NO-GO** —
มี blocker แม้ข้อเดียว = NO-GO แล้ว**หยุดรออนุมัติก่อนแก้**

`rules/qa-before-prd.md` ทำให้ทุกครั้งที่สั่ง build/แพ็ก/release ขึ้น production ถามก่อน
หนึ่งครั้งว่าจะรัน QA ไหม — คำว่า "เลย" ไม่ข้ามคำถามนี้ ต้องสั่ง "ไม่ต้อง QA" หรือ "build เลย"

## `next-static-pack` — build เว็บ Next ขึ้น Apache

เว็บ Next รันบน Apache ที่ **ไม่มี Node** จึงต้อง build เป็น static export แล้ววางใต้ path ย่อย

```
npm run pack   =   next build  →  flatten-segments  →  pack-deploy
```

- **`flatten-segments.mjs`** — `next build` บน Windows เขียนชื่อไฟล์ prefetch (`__next.*.txt`)
  เป็นโฟลเดอร์ซ้อน ทำให้ prefetch 404 สคริปต์ยุบกลับให้ถูก
- **`pack-deploy.mjs`** — ก๊อป `out/` ไปปลายทาง แล้วเขียน `.htaccess` (RewriteBase, security
  headers, **CSP ที่ล็อก `connect-src` ไว้ที่ origin ของ `NEXT_PUBLIC_API_URL`**) กับ `README.txt`

basePath อ่านจาก `src/lib/basePath.ts` ที่เดียว เปลี่ยน path แล้ว `RewriteBase` ตามให้เอง

# สร้าง skill ใหม่

skill คือโฟลเดอร์ที่มี `SKILL.md` มี YAML frontmatter แล้วตามด้วยคำสั่ง
เริ่มจาก [`template/SKILL.md`](./template/SKILL.md) หรือให้ `/skill-creator` ช่วยร่างและรัน eval

```markdown
---
name: my-skill-name
description: skill นี้ทำอะไร และควรถูกเรียกตอนไหน (ใส่คำที่ผู้ใช้มักพิมพ์ด้วย)
---

# My Skill Name

[คำสั่งที่ Claude จะทำตามเมื่อ skill นี้ทำงาน]
```

frontmatter บังคับแค่ 2 ฟิลด์:
- `name` — ตัวพิมพ์เล็ก คั่นด้วย `-` ต้องตรงกับชื่อโฟลเดอร์
- `description` — ทำอะไร + ใช้ตอนไหน (ส่วนนี้คือสิ่งที่ Claude ใช้ตัดสินว่าจะโหลดหรือไม่)

ถ้า skill ต้องคุยกับผู้ใช้ `rules/skills-explain-in-thai.md` จะบังคับให้ตอบเป็นภาษาไทย
อยู่แล้ว เขียน `SKILL.md` เป็นอังกฤษได้ตามสะดวก

# หลักการที่ฝังไว้ในชุดนี้

- **lead ตัดสินใจ engineer ลงมือ** — ดีไซน์ สัญญา API ชื่อ โครงสร้าง เป็นงานของ Opus
  เท่านั้น engineer ห้ามคิดเอง ถ้าใบสั่งงานกำกวมเรื่องใหญ่ให้หยุดแล้วรายงานกลับ
- **ใบสั่งงานต้องครบ** — subagent เริ่มจากศูนย์ ไม่เห็นบทสนทนา ใบสั่งงานที่ขาด context
  = engineer เดาเอง ซึ่งแพงกว่าการเขียนใบสั่งงานให้ดีตั้งแต่แรก
- **ตรวจก่อนรับงานเสมอ** — Opus ต้องอ่าน diff จริงและรัน test เอง รายงานของ engineer
  ถือเป็น "คำกล่าวอ้าง" ไม่ใช่หลักฐาน
- **ห้ามทำ test ผ่านแบบปลอม ๆ** — ห้าม skip test, ห้าม catch ทิ้ง, ห้าม hardcode ให้เขียว
- **งานขนานห้ามแตะไฟล์เดียวกัน** — เขียนทับกันพัง เป็นความรับผิดชอบของ lead ที่จะแยกไฟล์
- **ไม่ commit / push / deploy** ถ้าผู้ใช้ไม่ได้สั่ง
- **งานเล็ก lead ทำเอง** — แก้ 2-3 บรรทัดไม่คุ้มค่าเขียนใบสั่งงาน

# License

skill ที่เขียนเองใน repo นี้ใช้ได้อิสระ skill ที่รวมมาจากที่อื่นอยู่ภายใต้ license ของต้นทาง —
ดู [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)
