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
  rules/
    delegate-by-default.md          # กฎที่ทำให้แตกงานอัตโนมัติ ไม่ต้องพิมพ์ /boss
install.ps1 / install.sh            # ติดตั้งลงเครื่องอื่น (ระดับ user, ใช้ได้ทุกโปรเจกต์)
```

## เอาไปใช้เครื่องอื่น

**แบบที่ 1 — เฉพาะโปรเจกต์:** ก๊อป `.claude/` ทั้งโฟลเดอร์ไปวางที่ root ของโปรเจกต์นั้น
จบ ไม่ต้องติดตั้งอะไรเพิ่ม (commit เข้า git ได้เลย ทีมทั้งทีมได้ใช้เหมือนกัน)

**แบบที่ 2 — ทั้งเครื่อง:** ก๊อปโฟลเดอร์นี้ไป แล้วรัน

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1   # Windows
```
```bash
bash ./install.sh                                        # macOS / Linux
```

สคริปต์จะก๊อป agents + skill ไปที่ `~/.claude/` และเช็คให้ว่า lead model เป็น opus
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
