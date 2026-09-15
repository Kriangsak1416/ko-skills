# PR description template (dev → main)

Title is the version then the date, nothing else:

```
v.1.0.0 - 2026-08-01
```

Body starts with the same line, then what shipped and what was tested. Fill every
section — an empty section means an unanswered question for the reviewer.

````markdown
## v.1.0.0 — 2026-08-01

### งานที่อัพขึ้น
- `#1_add_text_builder` — เพิ่มตัวสร้างข้อความสำหรับหน้ารายงาน
- `#2_fix_export_encoding` — แก้ encoding ตอน export CSV เป็นภาษาไทยแล้วเพี้ยน

### การทดสอบ
- `npm test` — ผ่าน 128/128 (รันเมื่อ 2026-08-01 บน branch v.1.0.0)
- `npm run build` — ผ่าน
- ทดสอบมือ: export รายงานภาษาไทย 3 ไฟล์ เปิดด้วย Excel แล้วอ่านได้ปกติ

### ผลกระทบ / สิ่งที่ต้องทำก่อนขึ้น PRD
- ต้องตั้ง env `REPORT_TEMPLATE_PATH` เพิ่มก่อน deploy
- มี migration `2026_08_01_add_template_table` ต้องรันก่อน

### ยังไม่ได้ทำ / รู้อยู่ว่าเป็นข้อจำกัด
- ยังไม่รองรับ export เป็น PDF (แยกเป็น issue #7)
````

## Rules for filling it in

- **การทดสอบ** lists commands you actually ran and their real output. If there
  are no automated tests, write `ไม่มี test อัตโนมัติในส่วนนี้` and say what was
  checked by hand instead. Never imply coverage that does not exist.
- **ผลกระทบ** is what breaks or must be prepared: migrations, env vars, config,
  breaking API changes, order of deployment. Write `ไม่มี` if there is none.
- **ยังไม่ได้ทำ** exists so a reviewer does not have to discover the gaps. Drop
  the section only when there genuinely are none.
- Reference feature branches by their real names so the reviewer can map commits
  back to the work.
- Dates come from the system clock, not from memory.
