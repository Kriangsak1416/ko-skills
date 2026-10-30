# Changelog

มีอะไรเปลี่ยนในแต่ละ version หลัก (`metadata.version` ใน `.claude-plugin/marketplace.json`)
ใหม่สุดอยู่บน — `update-skill-ko` และสคริปต์อัปเดตอ่านไฟล์นี้เพื่อบอกผู้ใช้ว่าได้อะไรใหม่

**คนดูแล repo:** bump version เมื่อไหร่ เพิ่มหัวข้อ `## X.Y.Z — YYYY-MM-DD` บนสุดทุกครั้ง
เขียนจากมุมคนใช้ (อะไรเปลี่ยนในพฤติกรรม / ต้องทำอะไรเพิ่ม) ไม่ใช่รายการไฟล์

## 2.9.0 — 2026-10-30

- อัปเดต ko-skills แล้วจะบอกว่ามีอะไรเปลี่ยนบ้าง: `update-skill-ko`, hook ตอนเปิดเซสชัน
  และ `update-skills.sh` แสดงรายการจากไฟล์นี้ เฉพาะ version ที่ใหม่กว่าในเครื่อง
- เพิ่ม `CHANGELOG.md` (ไฟล์นี้)

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
