---
name: update-skill-ko
description: เช็คว่า skills/agents/rules ของ ko-skills ที่ติดตั้งใน ~/.claude ตรงกับ repo github.com/Kriangsak1416/ko-skills หรือไม่ โดยเทียบ version หลัก (metadata.version ใน marketplace.json) ถ้าไม่ตรงจะถามก่อนแล้วอัปเดตให้ ใช้เมื่อผู้ใช้พิมพ์ "update-skill-ko", "อัปเดต skill", "เช็ค skill ตรงกับ repo ไหม", "skill ในเครื่องเก่าไหม"
---

# update-skill-ko — เทียบ version หลักของ ko-skills กับ GitHub

version หลักของทั้ง repo คือ `metadata.version` ใน `.claude-plugin/marketplace.json`
ส่วน version ที่ติดตั้งในเครื่องบันทึกไว้ที่ `~/.claude/ko-skills.version`
(สคริปต์เป็นคนเขียนไฟล์นี้ตอนอัปเดต)

สคริปต์ `update-skill-ko.sh` อยู่ในโฟลเดอร์ของ skill นี้ ซึ่งก็คือ Base directory
ที่แสดงตอนโหลด skill รันด้วย `bash` (บน Windows ใช้ Git Bash)

## ขั้นตอน

1. **เช็ค** รัน `bash "<base dir>/update-skill-ko.sh" check` จะได้ 3 บรรทัด:
   `local=` `remote=` `status=`
2. **รายงานเป็นภาษาไทย** บอก version ในเครื่องและบน GitHub แล้วทำตาม `status`:
   - `same`: บอกว่าตรงกันแล้ว จบ
   - `different`: บอกว่าไม่ตรงกัน (`local=none` แปลว่าเครื่องนี้ยังไม่เคยอัปเดตผ่าน skill นี้)
     แล้วถามหนึ่งครั้งด้วย `AskUserQuestion` ว่า **อัปเดตเลย** หรือ **ยังไม่อัปเดต**
   - `unknown`: ดึง version จาก GitHub ไม่ได้ (ออฟไลน์ หรือ GitHub ตอบไม่ได้) บอกผู้ใช้แล้วจบ
     ห้ามอัปเดตแบบเดาเอา
3. **อัปเดต** (เฉพาะเมื่อผู้ใช้ตอบว่าอัปเดตเลย) รัน `bash "<base dir>/update-skill-ko.sh" apply`
   สคริปต์จะ clone repo ล่าสุดไปไว้ในโฟลเดอร์ชั่วคราว ก๊อป `skills/` `agents/` `rules/`
   ทับลง `~/.claude` แล้วบันทึก version ใหม่ ทับเฉพาะไฟล์ชื่อเดียวกัน ส่วน skill อื่นในเครื่องยังอยู่
   รันเสร็จให้รายงานผล และบอกให้รีสตาร์ต Claude Code เพื่อโหลดของใหม่

## ข้อจำกัด

- skill นี้เทียบแค่ version หลัก ถ้ามีคนแก้ skill ใน repo แล้วไม่ bump `metadata.version`
  จะเช็คไม่เจอ คนดูแล repo ต้อง bump ทุกครั้งที่แก้ `skills/` `agents/` หรือ `rules/`
- GitHub อาจ cache ไฟล์ดิบไว้ราว 5 นาที ถ้าเพิ่ง push แล้วเช็คทันทีอาจยังเห็น version เก่า
- ถ้าติดตั้งแบบ plugin (`/plugin`) ให้อัปเดตผ่าน `/plugin` แทน skill นี้ใช้กับแบบก๊อปลง `~/.claude`
