# Tech lead + engineers — ทีม AI ที่แบ่งงานกันเอง

ชุด config แบบพกพาสำหรับ Claude Code: **Opus 5** เป็น tech lead (คิด วางแผน
แตกงาน รีวิว รวมงาน) และ **Sonnet** เป็น engineer ที่ลงมือเขียนโค้ดจริง

## ไฟล์ในชุดนี้

```
.claude/
  settings.json                     # ตั้ง lead model = opus, effort = high, permission พื้นฐาน
  agents/
    coder.md                        # sonnet — เขียน/แก้โค้ดตามสเปกที่ lead ตัดสินใจแล้ว
    fixer.md                        # sonnet — ดีบัก หาสาเหตุจริง แก้แบบน้อยที่สุด พร้อมพิสูจน์
    reviewer.md                     # sonnet — รีวิว diff หาบั๊ก (อ่านอย่างเดียว ไม่แก้)
    scout.md                        # sonnet — สำรวจโค้ดเบส หา call site ก่อนวางแผน
  skills/boss/
    SKILL.md                        # playbook ของ lead: วนลูป plan → dispatch → verify → integrate
    references/brief-template.md    # เทมเพลตใบสั่งงาน + checklist ก่อนส่ง + วิธีสั่งแก้งาน
  skills/ship/
    SKILL.md                        # git flow ของทีม: branch #N → commit/push → release → PR
    references/pr-template.md       # เทมเพลต description ของ PR (version + วันที่ + งาน + การทดสอบ)
  skills/karpathy-guidelines/
    SKILL.md                        # กันนิสัยเสียของ LLM: อย่าเดา อย่าเขียนเกิน แก้เฉพาะจุด (MIT)
  skills/qa/
    SKILL.md                        # ตรวจก่อนขึ้น PRD: build → bug → web security → migrations → GO/NO-GO
    references/web-security-checklist.md  # เช็คลิสต์ความปลอดภัยเว็บ 10 หมวด + คำสั่งสแกนจริง
  skills/next-static-pack/
    SKILL.md                        # Next.js -> static export -> ชุดพร้อมวางบน Apache
    references/flatten-segments.mjs # แก้บั๊กชื่อไฟล์ RSC segment ที่ next build บน Windows เขียนผิด
    references/pack-deploy.mjs      # เทมเพลตแพ็ก out/ + เขียน .htaccess (CSP/headers) ให้
  skills/debug-mantra/              # 9arm — วินัยดีบัก 4 ข้อ: repro → fail path → falsify → breadcrumb
  skills/scrutinize/                # 9arm — รีวิว plan/PR แบบคนนอก ไล่ code path จริง ไม่ดูแค่ diff
  skills/post-mortem/               # 9arm — เขียนบันทึกบั๊กหลังแก้เสร็จ (root cause / fix / validation)
  skills/management-talk/           # 9arm — แปลงเรื่อง eng เป็นภาษาผู้บริหาร แยกตามช่องทาง
  rules/
    delegate-by-default.md          # กฎที่ทำให้แตกงานอัตโนมัติ ไม่ต้องพิมพ์ /boss
    qa-before-prd.md                # ก่อน build ขึ้น PRD ต้องถามก่อนว่าจะรัน /qa ไหม
install.sh                          # ติดตั้งลงเครื่องอื่น (ระดับ user, ใช้ได้ทุกโปรเจกต์)
```

## เอาไปใช้เครื่องอื่น

**แบบที่ 1 — เฉพาะโปรเจกต์:** ก๊อป `.claude/` ทั้งโฟลเดอร์ไปวางที่ root ของโปรเจกต์นั้น
จบ ไม่ต้องติดตั้งอะไรเพิ่ม (commit เข้า git ได้เลย ทีมทั้งทีมได้ใช้เหมือนกัน)

**แบบที่ 2 — ทั้งเครื่อง:** ก๊อปโฟลเดอร์นี้ไป แล้วรัน

```bash
bash ./install.sh
```

สคริปต์จะก๊อป agents + skill ทุกตัว + rule ไปที่ `~/.claude/` (ทับเฉพาะไฟล์ชื่อ
เดียวกัน ของเดิมที่คุณมีอยู่ไม่หาย) และเช็คให้ว่า lead model เป็น opus
(ไม่ทับ settings เดิมของคุณ — แค่เตือนถ้าไม่ตรง) จากนั้นรีสตาร์ต Claude Code

## วิธีสั่งงาน

**สั่งงานตามปกติ ไม่ต้องพิมพ์อะไรพิเศษ**

```
เพิ่มระบบ login ด้วย JWT พร้อม test
```

`rules/delegate-by-default.md` ถูกโหลดทุกเซสชันอัตโนมัติ (ทั้งแบบวางใน
โปรเจกต์และแบบติดตั้งที่ `~/.claude/rules/`) งานที่ต้องทำหลายขั้นหรือแตะตั้งแต่
3 ไฟล์ขึ้นไปจะเข้าโหมด lead + engineers เอง งานเล็กแค่ไม่กี่บรรทัด lead ทำเองเลย
ไม่แตกงานให้เปลืองรอบ — และจะบอกคุณ 1 บรรทัดก่อนเริ่มว่าเลือกทางไหน

พิมพ์ `/boss <งาน>` ได้อยู่ ถ้าอยากบังคับให้แตกงานแน่ ๆ หรือบอกว่า "ทำเองเลย
ไม่ต้องใช้ subagent" ถ้าอยากปิดโหมดนี้เป็นครั้ง ๆ

Opus จะ: สำรวจโค้ด → ตัดสินใจดีไซน์เอง → แตกเป็นงานย่อยที่**ไม่แก้ไฟล์ทับกัน** →
ส่ง `coder` หลายตัวขนานกัน → **รัน test เองเพื่อตรวจ** (ไม่เชื่อรายงานของ engineer ลอย ๆ) →
สั่งแก้ถ้าไม่ผ่าน → รวมงานและสรุปให้คุณ

## อัพงานขึ้น git — `/ship`

git flow ของทีมถูกฝังไว้ใน skill `ship` เรียกด้วย `/ship` หรือพิมพ์ธรรมดาว่า
"commit ให้หน่อย" / "อัพงาน" / "ทำ release v.1.1.0" / "ขึ้น PRD" ก็ได้

**งานปกติ (feature)**

```
dev → แตก branch '#1_add_text_builder' → ทำงาน → commit (ภาษาไทย สั้น ๆ) → push
```

**ตอนจะขึ้น PRD (release)**

```
dev → แตก branch 'v.1.0.0' → merge feature ที่จะอัพ → รัน test →
finish release (merge เข้า main + merge กลับ dev + ลบ branch + tag) →
เปิด PR dev → main ให้คนอื่น approve
```

PR ตั้ง title เป็น `v.1.0.0 - 2026-08-01` (version + วันที่) และ description
ไล่ว่าอัพอะไรขึ้นไปบ้าง ทดสอบอะไรไปแล้ว มีผลกระทบอะไรต้องเตรียมก่อน deploy —
ดูเทมเพลตที่ `skills/ship/references/pr-template.md`

ต้องมี [GitHub CLI](https://cli.github.com) ถึงจะเปิด PR ให้อัตโนมัติได้
(`winget install --id GitHub.cli` แล้ว `gh auth login`) ถ้าไม่มี skill จะพิมพ์
title + description + ลิงก์ compare ให้ไปกดเอง

สิ่งที่ skill จะไม่ทำเด็ดขาด: force push, rewrite history ที่ push ไปแล้ว,
merge PR ของตัวเอง, เขียนใน PR ว่าทดสอบผ่านทั้งที่ไม่ได้รัน

## `/qa` — ตรวจก่อนขึ้น PRD

Release engineer audit ก่อนเอาของขึ้น production 4 เฟส

1. **Build readiness** — รัน build/typecheck/lint จริง, env ครบไหม, dev-only code หลุดไหม
2. **Bug audit** — logic / error handling / DB / concurrency พร้อม severity และ `file:line`
3. **Web security audit** — 10 หมวดตาม OWASP Top 10 (2021) + API Security Top 10 (2023):
   secret ที่ติดไปกับ bundle, auth/session, **IDOR** (เปลี่ยนเลขใน URL แล้วเห็นของคนอื่น),
   injection/XSS, CSRF/CORS/SSRF, headers+CSP, upload/rate limit, supply chain,
   **ข้อมูลผู้ป่วย/PDPA**, endpoint ที่ไม่ควรเปิด
4. **Migrations must-run-immediately** — fresh + production-like, rollback, MariaDB 5.5 (utf8mb4 index 191)

จบด้วยตาราง severity, รายการ blocker, migration runbook และคำตัดสิน
**GO / NO-GO** — มี blocker แม้ข้อเดียว = NO-GO แล้ว**หยุดรออนุมัติก่อนแก้**

รันเองด้วย `/qa` ก็ได้ แต่ไม่ต้องจำ — `rules/qa-before-prd.md` ทำให้ทุกครั้งที่สั่ง
build/แพ็ก/release ขึ้น production (รวมถึง `/ship` Flow B กับ `npm run pack` ของ
`next-static-pack`) ถามก่อนหนึ่งครั้งว่าจะรัน QA ก่อนไหม

คำว่า "เลย" ไม่ข้ามคำถามนี้ — "อัพขึ้น PRD เลย" แปลว่าไม่ต้องขออนุมัติเป็นขั้น ๆ
ไม่ได้แปลว่าไม่ต้องทดสอบ สั่ง "ไม่ต้อง QA" หรือ "build เลย" ถึงจะข้าม

## `karpathy-guidelines` — กันนิสัยเสียของ LLM

Skill จากภายนอกที่รวมไว้ด้วย: 4 หลักการสั้น ๆ ที่ตัดปัญหาที่โมเดลชอบทำ —
เดาแทนเราแล้วลุยต่อ, เขียนเกินความจำเป็น, ไปแก้โค้ดข้าง ๆ ที่ไม่เกี่ยว,
และทำงานโดยไม่มีเกณฑ์ว่า "เสร็จ" คืออะไร

เรียกเองด้วย `/karpathy-guidelines` หรือปล่อยให้ถูกเรียกอัตโนมัติตอนเขียน/รีวิว/
refactor โค้ด — ใช้คู่กับ `boss` ได้ดี เพราะ engineer ที่รับใบสั่งงานจะได้ไม่
"ปรับปรุงเพิ่มให้" นอกสโคป

ที่มา: [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)
โดย forrestchang (MIT) — ดัดแปลงจาก
[โพสต์ของ Andrej Karpathy](https://x.com/karpathy/status/2015883857489522876)
ไฟล์ถูกคัดลอกมาตามต้นฉบับ ไม่ได้แก้เนื้อหา

## `next-static-pack` — build เว็บ Next ขึ้น Apache

เว็บ Next ของเรารันบน Apache ที่ **ไม่มี Node** ทุกตัวจึงต้อง build เป็น static
export แล้ววางทั้งโฟลเดอร์ใน DocumentRoot ใต้ path ย่อย skill นี้เก็บสูตรทั้งชุด
ที่ใช้จริงกับ `icu refer` และ `ICU Dashboard` มาแล้ว

```
npm run pack   =   next build  →  flatten-segments  →  pack-deploy
```

- **`flatten-segments.mjs`** — `next build` บน Windows เขียนชื่อไฟล์ prefetch
  (`__next.*.txt`) เป็นโฟลเดอร์ซ้อนแทนไฟล์แบน ทำให้ชี้เมนูแล้ว prefetch ได้ 404
  สคริปต์ยุบกลับให้ถูก (บน Linux ไม่มีปัญหานี้ มันจะจบเงียบ ๆ)
- **`pack-deploy.mjs`** — ก๊อป `out/` ไปปลายทางนอกโปรเจกต์ แล้วเขียน `.htaccess`
  (RewriteBase, security headers, **CSP ที่ล็อก `connect-src` ไว้ที่ origin ของ
  `NEXT_PUBLIC_API_URL` เจ้าเดียว**) กับ `README.txt` วิธีวางให้ทีมเซิร์ฟเวอร์

basePath ถูกอ่านจาก `src/lib/basePath.ts` ที่เป็นแหล่งความจริงที่เดียว ไม่ได้
hardcode ไว้ในสคริปต์ — เปลี่ยน path แล้ว `RewriteBase` ตามให้เอง

ใน SKILL.md มี checklist ก่อนบอกว่าเสร็จ (ต้องไม่เหลือโฟลเดอร์ `__next.*`,
CSP ต้องตรงกับที่แอปยิงจริง) และตารางว่าแอปใช้อะไรแล้วต้องเปิด CSP ตัวไหน

## skills ของ 9arm

รวมมาจาก [thananon/9arm-skills](https://github.com/thananon/9arm-skills) เอามา 4 ตัว
(ก๊อปตามต้นฉบับ)

| skill | ใช้ตอนไหน |
|---|---|
| `/debug-mantra` | เริ่มไล่บั๊ก — บังคับลำดับ repro ให้ได้ก่อน → หา fail path → พยายามล้มสมมติฐานตัวเอง → ไล่ทวนทุกการทดลอง |
| `/scrutinize` | รีวิว plan / PR / diff แบบคนนอก ถามก่อนว่า "จำเป็นต้องทำไหม มีทางที่ง่ายกว่าไหม" แล้วค่อยไล่ code path จริง ห้ามตอบ LGTM ลอย ๆ |
| `/post-mortem` | บั๊กแก้เสร็จและ validate แล้ว เขียนบันทึกให้คนอื่น (ถ้ายังไม่มี repro / ยังไม่รู้ root cause มันจะปฏิเสธไม่เขียนให้) |
| `/management-talk` | แปลงเรื่อง technical เป็นภาษาผู้บริหาร แยกทรงตามช่องทาง (JIRA / Slack / standup / email) |

ต้นฉบับมีอีก 2 ตัวที่ไม่ได้เอามา — `qwen-agent` (โยนงานจำเจให้ qwen ผ่านคำสั่ง
`claude-9arm` ซึ่งเป็น gateway ส่วนตัวของเจ้าของ repo) และ `qwenchance`
(กันวนลูป/เฝ้า context) การโยนงานให้โมเดลถูกกว่าทำอยู่แล้วผ่าน `/boss` + agent
`coder` ที่เป็น sonnet เลยไม่ต้องมีอีกตัว

แก้จากต้นฉบับจุดเดียว: ลิงก์ใน `post-mortem` ที่ชี้ไป `../../productivity/management-talk/`
เปลี่ยนเป็น `../management-talk/` เพราะที่นี่วาง skill เรียงแบนไม่ได้แยก bucket

## หลักการที่ฝังไว้ในชุดนี้

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
