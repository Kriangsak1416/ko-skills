---
name: qa
description: Pre-production release audit — verify the project builds for PRD, passes a modern web-security audit (OWASP Top 10, secrets in the client bundle, authz/IDOR, injection, CSRF/CORS/SSRF, security headers + CSP, supply chain, PDPA/patient-data exposure), and that migrations can run immediately after the build without breaking. Runs the real build/typecheck/lint and real scanners, audits critical-path files, then audits every migration for ordering, fresh + production-like runs, rollback, and MariaDB 5.5 compatibility. Ends with a severity table, blocker list, migration runbook, and a GO / NO-GO verdict — then stops for approval before fixing. Trigger on /qa, "ตรวจก่อน build", "pre-build audit", "ขึ้น PRD ได้ยัง", "audit migrations", "ตรวจความปลอดภัย", "security audit", "GO/NO-GO", or before any production deploy.
---

# QA — Pre-production audit

บทบาท: **Release Engineer** ทำ pre-production audit
เป้าหมาย: ยืนยัน 3 ข้อ — build ลง production (PRD) ได้, **ไม่มีช่องโหว่ระดับ Blocker
หลุดขึ้นเว็บจริง**, และ **รัน migrations ได้ทันทีหลัง build** โดยไม่พัง

## กติกา

1. อ่านโครงสร้างโปรเจคทั้งหมดก่อน — `package.json` / `composer.json`, scripts, Dockerfile,
   CI workflow, `.env.example`, `.htaccess` / nginx conf, โฟลเดอร์ migrations
2. **ห้ามเดา** — ไม่แน่ใจให้เปิดไฟล์จริงมาอ่าน ทุกข้อที่รายงานต้องมี `file:line` อ้างอิงได้
3. **รันของจริง** — คำสั่ง build, scanner, grep ต้องรันจริงแล้วเอา output มาสรุป
   ห้ามเขียนว่า "ผ่าน" จากการอ่านโค้ดเฉย ๆ
4. **ยังไม่ต้องแก้โค้ด** จนกว่าจะรายงานเสร็จและผู้ใช้อนุมัติ
5. **ตัดเฟสที่ไม่เกี่ยวออกได้** — โปรเจกต์ static export ไม่มี migrations ก็ข้ามเฟส 4
   แต่ต้องเขียนในรายงานว่าข้ามเพราะอะไร ห้ามเงียบ

## เฟส 1 — Build readiness

- รัน typecheck / lint / build **จริง** (เช่น `npm run build`, `npx tsc --noEmit`,
  `php artisan config:cache`) แล้วสรุป error/warning ทุกตัว พร้อม `file:line`
- **Env**: ตัวแปรที่โค้ดเรียกใช้ มีใน `.env.example` ครบไหม / มี hardcode secret, URL,
  IP ของ dev ค้างอยู่ไหม / ค่า default ตอนไม่มี `.env` ชี้ไปที่ไหน
- **Dev-only code หลุด prod**: `console.log`, `dd()`, `debugger`, debug flag,
  mock data, seeder ที่รันอัตโนมัติ, endpoint ทดสอบที่ยังเปิด
- **สิ่งที่ติดไปกับ build artifact**: source map, `.env`, `.git`, ไฟล์ `.bak`/`.sql`,
  โฟลเดอร์ `node_modules` — ดูในผลลัพธ์ที่จะอัปจริง ไม่ใช่ในซอร์ส

## เฟส 2 — Bug audit

ไล่ทีละไฟล์ที่อยู่ใน critical path จัดกลุ่มตามนี้ พร้อม severity **Blocker / High / Medium / Low**

- **Logic**: null/undefined ที่ไม่ถูก guard, off-by-one, timezone, พ.ศ./ค.ศ. conversion,
  encoding ภาษาไทย (utf8mb4 / cp874)
- **Error handling**: try/catch ที่กลืน error, promise ที่ไม่ await, transaction ที่ไม่ rollback
- **DB**: N+1, query ที่ไม่มี index, connection pool leak, cursor/stream ที่ไม่ปิด
  (ส่วน SQL injection อยู่ในเฟส 3)
- **Concurrency**: race condition, ตัวแปร global ที่แชร์ข้าม request,
  โมดูล-level cache ที่ปนข้ามผู้ใช้ (บั๊กนี้กลายเป็นช่องโหว่ทันทีถ้าแคชคำตอบที่ผูกกับสิทธิ์)

## เฟส 3 — Web security audit ← ห้ามข้าม

รายละเอียดทั้งหมด ทั้งสิ่งที่ต้องดู สัญญาณอันตราย และคำสั่งสแกน อยู่ใน
`references/web-security-checklist.md` — **เปิดอ่านแล้วไล่ให้ครบทุกหมวด**
ที่โปรเจกต์นี้มีจริง หมวดไหนไม่มีในโปรเจกต์ให้เขียนว่า "ไม่มี" ไม่ใช่เว้นว่าง

10 หมวดในเช็คลิสต์:

| # | หมวด | หัวใจ |
| --- | --- | --- |
| 1 | Secrets & build artifact | `NEXT_PUBLIC_*` / `VITE_*` ที่ไม่ควรเป็น public, secret ใน git history, source map ขึ้น prod |
| 2 | AuthN / session | JWT verify + exp/iss/aud, ที่เก็บ token, password hash, rate limit ตอน login, logout ที่ไม่ทำลาย session |
| 3 | AuthZ / IDOR | ทุก endpoint ที่รับ id ต้องเช็คว่า "คนนี้ดูของคนนี้ได้ไหม" — เช็คสิทธิ์ฝั่ง client ไม่นับ |
| 4 | Injection & XSS | parameterized query ทุกที่, `dangerouslySetInnerHTML` / `v-html` / `innerHTML`, path traversal, command injection |
| 5 | CSRF / CORS / SSRF | SameSite + CSRF token, CORS ที่สะท้อน Origin กลับ, URL จากผู้ใช้ที่เซิร์ฟเวอร์ยิงต่อ |
| 6 | Headers / transport / CSP | CSP ที่ล็อกจริง, HSTS, nosniff, frame-ancestors, cookie flags, mixed content |
| 7 | Input, upload, rate limit | ตรวจไฟล์จาก magic bytes ไม่ใช่นามสกุล, `?limit=` ที่ผู้ใช้คุมได้, open redirect, ReDoS |
| 8 | Dependency & supply chain | `npm audit` / `composer audit` จริง, lockfile + `npm ci`, script ภายนอกไม่มี SRI, CI ที่ pin ไม่แน่น |
| 9 | ข้อมูลผู้ป่วย / PDPA | HN-ชื่อ-เลขบัตรใน log/URL/error, response ที่ส่ง field เกินหน้าจอ, export ที่ไม่เช็คสิทธิ์, audit trail |
| 10 | API & endpoint ที่ไม่ควรเปิด | mass assignment, verbose error, `/phpinfo.php` `/.env` `/actuator`, directory listing, endpoint เวอร์ชันเก่า |

**เกณฑ์ severity ของช่องโหว่** — ใช้เกณฑ์นี้ ไม่ใช่ความรู้สึก:

- **Blocker** — คนนอกที่ไม่ล็อกอิน หรือผู้ใช้ธรรมดาหนึ่งคน ทำได้เลยโดยไม่ต้องมีเงื่อนไขพิเศษ
  แล้วได้ข้อมูลของคนอื่น / เขียนข้อมูลได้ / ยึดบัญชีได้ **ห้าม build จนกว่าจะแก้**
- **High** — ต้องมีเงื่อนไขบางอย่าง (ต้องมี token, ต้องหลอกให้ผู้ใช้กดลิงก์) แต่ผลกระทบยังหนัก
- **Medium** — ทำให้โจมตีจริงง่ายขึ้น หรือรั่วข้อมูลที่ไม่ใช่ตัวข้อมูลผู้ป่วยโดยตรง
- **Low** — hardening ที่ควรทำ แต่ยังไม่มีทางโจมตีที่เห็นชัด

**ทุกข้อที่รายงานต้องเขียน "ทำยังไงถึงเจอ/ถึงโดน" ได้เป็นขั้น ๆ** ถ้าเขียนไม่ได้
แปลว่ายังไม่เข้าใจดีพอ — ให้ไปอ่าน code path ต่อ อย่าเดาแล้วปั่นจำนวนข้อ

## เฟส 4 — Migrations must-run-immediately

ตรวจทุกไฟล์ใน migrations แล้วตอบให้ครบทุกข้อ:

1. ลำดับ/ชื่อไฟล์ถูกต้อง ไม่มี timestamp ชนกัน ไม่มี dependency ย้อนหลัง (FK ชี้ไปตารางที่ยังไม่ถูกสร้าง)
2. รันบน DB เปล่า (fresh) ได้ครบทุกไฟล์ ไม่ error
3. รันบน DB ที่มีข้อมูลจริงอยู่แล้ว (production-like) ได้ ไม่ทำ data loss
4. มี rollback / `down()` ที่ใช้งานได้จริงทุกไฟล์
5. ความเข้ากันได้ของ DB เป้าหมาย:
   - **MariaDB 5.5**: VARCHAR + utf8mb4 index ต้องไม่เกิน **191 chars**; ห้ามใช้ syntax เฉพาะเวอร์ชันใหม่
     (JSON type, CHECK constraint, DEFAULT ที่เป็น expression, `ALTER ... ALGORITHM=INSTANT`)
   - ระบุ charset/collation ชัดเจนทุก `CREATE TABLE`
6. Migration ที่ล็อกตารางใหญ่นาน ๆ → เตือนและเสนอทางเลี่ยง
7. schema ที่ migration สร้าง ตรงกับที่โค้ดใช้จริงไหม (ชื่อคอลัมน์/ชนิดข้อมูล ตรงกับ model/query)
8. **ความปลอดภัยของ migration เอง**: seeder ที่ใส่ user default พร้อมรหัสผ่านตายตัว,
   คอลัมน์ที่เก็บข้อมูลอ่อนไหวแบบ plaintext, การ grant สิทธิ์ DB เกินจำเป็น,
   migration ที่ dump ข้อมูลจริงลงไฟล์
9. เสนอ "คำสั่งที่ต้องรันหลัง build" เป็นลำดับขั้น พร้อมคำสั่ง verify แต่ละขั้น

## ผลลัพธ์ที่ต้องส่ง

1. **ตารางสรุป**: Severity | ไฟล์:บรรทัด | ปัญหา | ผลกระทบตอน deploy | วิธีแก้
2. **ตารางช่องโหว่แยกอีกใบ**: Severity | หมวด (1–10) | จุดที่เจอ | ทำยังไงถึงโดน | วิธีแก้
3. **รายการ Blocker** ที่ "ห้าม build จนกว่าจะแก้"
4. **Migration runbook**: คำสั่ง deploy ทีละขั้น + คำสั่ง rollback
5. **คำตัดสิน GO / NO-GO** พร้อมเหตุผล — มี Blocker แม้ข้อเดียว = **NO-GO**
6. **สิ่งที่ยังไม่ได้ตรวจ** — เฟสที่ข้าม, ไฟล์ที่ใหญ่เกินจนอ่านไม่หมด, ของที่ตรวจได้เฉพาะบนเซิร์ฟเวอร์จริง
   (เช่น TLS, header ที่ Apache ใส่ให้) เขียนให้ครบ อย่าปล่อยให้คนอ่านเข้าใจว่าตรวจหมดแล้ว

## หลังรายงาน

จบรายงานแล้ว **หยุดรอผู้ใช้ยืนยันก่อนลงมือแก้**
เมื่ออนุมัติแล้ว แก้เรียงจาก **Blocker → High**, แก้ทีละข้อ, และรัน build/test ซ้ำหลังแก้ทุกครั้ง
แก้เสร็จแล้วรันเฟสที่เกี่ยวข้องซ้ำเพื่อยืนยัน — อย่าเปลี่ยนคำตัดสินเป็น GO จากการอ่านโค้ดที่เพิ่งแก้
