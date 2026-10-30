# Third-party notices

skills ใน repo นี้บางตัวคัดลอกมาจากที่อื่น ไฟล์ถูกเก็บตามต้นฉบับ (ยกเว้นที่ระบุ)
และอยู่ภายใต้ license ของต้นทาง

เทียบกับต้นทางล่าสุดเมื่อ 2026-10-30 — commit ในตารางคือรุ่นที่ก๊อปมา อัปเดตครั้งหน้าให้ diff
จาก commit นี้ แล้วใส่ส่วนที่แก้ (คอลัมน์ขวาสุด) กลับเข้าไปใหม่

| skill | ที่มา | license | แก้จากต้นฉบับ |
|---|---|---|---|
| `skills/doc-coauthoring` | [anthropics/skills](https://github.com/anthropics/skills) (commit `ca45fc4`) | Apache 2.0 | — |
| `skills/frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) (commit `ca45fc4`) | Apache 2.0 (`LICENSE.txt` ในโฟลเดอร์) | — |
| `skills/mcp-builder` | [anthropics/skills](https://github.com/anthropics/skills) (commit `ca45fc4`) | Apache 2.0 (`LICENSE.txt` ในโฟลเดอร์) | — |
| `skills/skill-creator` | [anthropics/skills](https://github.com/anthropics/skills) (commit `ca45fc4`) | Apache 2.0 (`LICENSE.txt` ในโฟลเดอร์) | — |
| `skills/webapp-testing` | [anthropics/skills](https://github.com/anthropics/skills) (commit `ca45fc4`) | Apache 2.0 (`LICENSE.txt` ในโฟลเดอร์) | — |
| `skills/karpathy-guidelines` | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) (commit `2c60614`) โดย forrestchang ดัดแปลงจาก[โพสต์ของ Andrej Karpathy](https://x.com/karpathy/status/2015883857489522876) | MIT | — |
| `skills/debug-mantra` | [thananon/9arm-skills](https://github.com/thananon/9arm-skills) (commit `a1fc303`) | ตามต้นทาง | — |
| `skills/scrutinize` | [thananon/9arm-skills](https://github.com/thananon/9arm-skills) (commit `a1fc303`) | ตามต้นทาง | — |
| `skills/post-mortem` | [thananon/9arm-skills](https://github.com/thananon/9arm-skills) (commit `a1fc303`) | ตามต้นทาง | ลิงก์ `../../productivity/management-talk/` → `../management-talk/` เพราะที่นี่วาง skill เรียงแบน |
| `skills/management-talk` | [thananon/9arm-skills](https://github.com/thananon/9arm-skills) (commit `a1fc303`) | ตามต้นทาง | — |
| `skills/security-audit` | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) (commit `c1c8a8c`) | MIT (`LICENSE` ในโฟลเดอร์ ก๊อปจาก root ของต้นทาง) | `validate-findings.cjs` และ `validate-coverage-ledger.cjs`: บน Windows (ไม่มี `O_NOFOLLOW`/`O_NONBLOCK`) ต้นฉบับปฏิเสธทุกไฟล์ จึงเพิ่มทางสำรองที่ใช้ `lstat` ปฏิเสธ symlink/ไฟล์ที่ไม่ใช่ไฟล์ปกติ แล้วเทียบ `dev`+`ino` กับ `fstat` หลังเปิด ส่วน `*.test.cjs` ให้ `HAS_SAFE_INPUT_OPEN` เป็นจริงบน win32 ทุกจุดที่แก้มี comment `ko-skills patch:` บน Linux/macOS ยังทำงานเหมือนต้นฉบับทุกอย่าง |
| `skills/brainstorming` | [obra/superpowers](https://github.com/obra/superpowers) v7.0.1 (commit `2ce8aa1`) | MIT (`LICENSE` ในโฟลเดอร์ ก๊อปจาก root ของต้นทาง) | `SKILL.md`: description แคบลง (เรียกเมื่อสั่งหรือโจทย์ยังไม่ชัด ไม่ใช่ทุกงานสร้าง) + คำ trigger ภาษาไทย, design doc เก็บนอก repo ที่ `~/.claude/brainstorming/<repo>/` ไม่ commit (ต้นทาง commit ลง `docs/superpowers/specs/`), หลังอนุมัติส่งต่อให้ `boss` แทน `superpowers:writing-plans`, เพิ่มหัวข้อผู้ใช้งาน/ข้อมูลผู้ป่วย (PDPA) — `scripts/server.cjs`: ปิด telemetry ถาวร หน้า visual companion จะไม่โหลดโลโก้จาก primeradiant.com ทุกจุดที่แก้มี comment `ko-skills patch:` |
| `skills/verification-before-completion` | [obra/superpowers](https://github.com/obra/superpowers) v7.0.1 (commit `2ce8aa1`) | MIT (`LICENSE` ในโฟลเดอร์) | — |
| `skills/receiving-code-review` | [obra/superpowers](https://github.com/obra/superpowers) v7.0.1 (commit `2ce8aa1`) | MIT (`LICENSE` ในโฟลเดอร์) | — |

ที่เหลือ (`boss`, `ship`, `qa`, `next-static-pack`, `agents/`, `rules/`) เขียนขึ้นเองใน repo นี้
