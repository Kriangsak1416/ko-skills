# Third-party notices

skills ใน repo นี้บางตัวคัดลอกมาจากที่อื่น ไฟล์ถูกเก็บตามต้นฉบับ (ยกเว้นที่ระบุ)
และอยู่ภายใต้ license ของต้นทาง

| skill | ที่มา | license | แก้จากต้นฉบับ |
|---|---|---|---|
| `skills/doc-coauthoring` | [anthropics/skills](https://github.com/anthropics/skills) | Apache 2.0 | — |
| `skills/frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) | Apache 2.0 (`LICENSE.txt` ในโฟลเดอร์) | — |
| `skills/mcp-builder` | [anthropics/skills](https://github.com/anthropics/skills) | Apache 2.0 (`LICENSE.txt` ในโฟลเดอร์) | — |
| `skills/skill-creator` | [anthropics/skills](https://github.com/anthropics/skills) | Apache 2.0 (`LICENSE.txt` ในโฟลเดอร์) | — |
| `skills/webapp-testing` | [anthropics/skills](https://github.com/anthropics/skills) | Apache 2.0 (`LICENSE.txt` ในโฟลเดอร์) | — |
| `skills/karpathy-guidelines` | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) โดย forrestchang ดัดแปลงจาก[โพสต์ของ Andrej Karpathy](https://x.com/karpathy/status/2015883857489522876) | MIT | — |
| `skills/debug-mantra` | [thananon/9arm-skills](https://github.com/thananon/9arm-skills) | ตามต้นทาง | — |
| `skills/scrutinize` | [thananon/9arm-skills](https://github.com/thananon/9arm-skills) | ตามต้นทาง | — |
| `skills/post-mortem` | [thananon/9arm-skills](https://github.com/thananon/9arm-skills) | ตามต้นทาง | ลิงก์ `../../productivity/management-talk/` → `../management-talk/` เพราะที่นี่วาง skill เรียงแบน |
| `skills/management-talk` | [thananon/9arm-skills](https://github.com/thananon/9arm-skills) | ตามต้นทาง | — |
| `skills/security-audit` | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) (commit `c1c8a8c`) | MIT (`LICENSE` ในโฟลเดอร์ ก๊อปจาก root ของต้นทาง) | `validate-findings.cjs` และ `validate-coverage-ledger.cjs`: บน Windows (ไม่มี `O_NOFOLLOW`/`O_NONBLOCK`) ต้นฉบับปฏิเสธทุกไฟล์ จึงเพิ่มทางสำรองที่ใช้ `lstat` ปฏิเสธ symlink/ไฟล์ที่ไม่ใช่ไฟล์ปกติ แล้วเทียบ `dev`+`ino` กับ `fstat` หลังเปิด ส่วน `*.test.cjs` ให้ `HAS_SAFE_INPUT_OPEN` เป็นจริงบน win32 ทุกจุดที่แก้มี comment `ko-skills patch:` บน Linux/macOS ยังทำงานเหมือนต้นฉบับทุกอย่าง |

ที่เหลือ (`boss`, `ship`, `qa`, `next-static-pack`, `agents/`, `rules/`) เขียนขึ้นเองใน repo นี้
