# Web security checklist — เฟส 3 ของ /qa

เช็คลิสต์สำหรับเว็บที่ขึ้น production ปี 2026 อ้างอิง OWASP Top 10 (2021) +
OWASP API Security Top 10 (2023) แต่เรียงตาม "ที่ที่บั๊กชอบอยู่จริง" ไม่ใช่ตามชื่อหมวดของ OWASP

**วิธีใช้**: ไล่ทีละหมวด หมวดไหนไม่มีในโปรเจกต์เขียน "ไม่มี — เพราะ..." ทุกข้อที่ตอบว่า
"ปลอดภัย" ต้องมีไฟล์:บรรทัดที่ยืนยัน หรือ output ของคำสั่งที่รันจริง

**เว็บ static (Next static export / SPA ล้วน)** — หมวด 2–5, 9, 10 ยังต้องตรวจ
แต่ตรวจที่ **API ปลายทาง** ไม่ใช่ที่หน้าเว็บ ของที่หน้าเว็บทำได้เองมีแค่หมวด 1, 6, 7

---

## 1. Secrets & build artifact

สิ่งที่รั่วบ่อยที่สุดไม่ใช่ช่องโหว่ซับซ้อน แต่คือ **ของที่ไม่ควรอยู่ในไฟล์ที่อัปขึ้นไป**

- ตัวแปรที่ขึ้นต้นด้วย `NEXT_PUBLIC_` / `VITE_` / `REACT_APP_` **ถูกฝังลง bundle ที่ทุกคนเปิดอ่านได้**
  → ต้องไม่มี API key, service token, DB credential, LINE token, secret ของ payment gateway
- secret ที่เคย commit แล้วลบทีหลัง — **ยังอยู่ใน git history** ต้องถือว่ารั่วแล้วและต้อง rotate
- source map (`.map`) ขึ้น prod → เปิดซอร์สเดิมได้ทั้งโปรเจกต์
- `.env`, `.env.local`, `.git/`, `*.sql`, `*.bak`, `docker-compose.yml` ติดไปกับโฟลเดอร์ที่ rsync ขึ้นเซิร์ฟเวอร์
- token/credential ที่ hardcode ไว้ใน source เพราะ "เดี๋ยวค่อยย้ายไป env"

```bash
grep -rInE "(api[_-]?key|secret|passwd|password|token|bearer)[[:space:]]*[:=]" src app lib --exclude-dir=node_modules | head -40
grep -rIn "NEXT_PUBLIC_\|VITE_\|REACT_APP_" src app --exclude-dir=node_modules | sort -u
git log --oneline -S "PRIVATE KEY" --all | head
find out dist build -name "*.map" 2>/dev/null | head          # ต้องว่าง
ls -a out dist build 2>/dev/null | grep -E "^[.](env|git)"     # ต้องว่าง
```

## 2. Authentication & session

- **JWT**: verify signature จริงไหม (ไม่ใช่แค่ decode), บังคับ algorithm ฝั่งเซิร์ฟเวอร์
  (กัน `alg: none` และ RS256→HS256 confusion), เช็ค `exp` / `iss` / `aud`, secret ยาวพอและไม่ใช่ค่า default
- **ที่เก็บ token**: ใน `localStorage` = XSS ตัวเดียวขโมยได้หมด — ทางที่ถูกคือ cookie ที่มี
  `HttpOnly; Secure; SameSite=Lax` (หรือ `Strict`) ถ้าเลือก localStorage เพราะข้อจำกัดจริง ให้เขียนเหตุผลไว้
- **อายุ token**: access token สั้น, refresh token หมุนเวียนและ revoke ได้, logout ต้องทำให้ token ใช้ต่อไม่ได้จริง
  (ลบฝั่ง client อย่างเดียวไม่นับ)
- **รหัสผ่าน**: hash ด้วย bcrypt / argon2id เท่านั้น — เจอ `md5(` / `sha1(` กับรหัสผ่านคือ Blocker
- **Brute force**: login / OTP / reset-password ต้องมี rate limit หรือ lockout
  และ OTP ต้องใช้ครั้งเดียว มีวันหมดอายุ สุ่มด้วย CSPRNG
- **Session fixation**: ต้องออก session id ใหม่หลังล็อกอินสำเร็จ
- **User enumeration**: ข้อความ error ตอนล็อกอินผิดต้องไม่แยกว่า "ไม่มีผู้ใช้นี้" กับ "รหัสผ่านผิด"
- SSO / OAuth: ตรวจ `state` กัน CSRF, ตรวจ `redirect_uri` แบบ exact match, ใช้ PKCE

## 3. Authorization / IDOR — จุดที่พังบ่อยที่สุดในระบบโรงพยาบาล

**ทุก endpoint ที่รับ id, HN, ward, เลขที่เอกสาร ต้องตอบให้ได้ว่า "ผู้ใช้คนนี้มีสิทธิ์เห็นแถวนี้ไหม"**

- เปลี่ยนเลขใน URL แล้วได้ข้อมูลคนอื่น = **Blocker** (OWASP: BOLA)
- เช็คสิทธิ์ฝั่ง client อย่างเดียว (ซ่อนปุ่ม / ซ่อนเมนู) ไม่นับเป็นการเช็คสิทธิ์
- route ที่ลืมใส่ middleware — ไล่ทีละ route ไม่ใช่ดูแค่ไฟล์ config โดยเฉพาะ route ที่เพิ่งเพิ่มมา,
  route `POST`/`DELETE` คู่ของ `GET` ที่ป้องกันไว้แล้ว, endpoint export/report/print
- ยกระดับสิทธิ์ผ่าน field ที่ผู้ใช้ส่งมาเอง (`role`, `is_admin`, `ward_id`, `hospital_code`)
- endpoint แอดมินที่ป้องกันด้วย "ไม่มีใครรู้ URL" อย่างเดียว
- ฟังก์ชันที่รับ `where` / filter / ชื่อคอลัมน์ จาก query string ตรง ๆ แล้วยัดเข้า query

## 4. Injection & XSS

- **SQL/NoSQL**: ต้อง parameterized ทุกจุด หา raw query ที่ต่อสตริงจาก input
  (`DB::raw`, `whereRaw`, template literal ที่มี `${` อยู่ใน SQL)
- **XSS**: `dangerouslySetInnerHTML`, `v-html`, `innerHTML`, `outerHTML`, `document.write`,
  `eval`, `new Function`, `setTimeout("string")` — ถ้าเลี่ยงไม่ได้ต้องผ่าน DOMPurify ก่อน
- **href/src ที่มาจากข้อมูล**: กัน `javascript:` และ `data:text/html`
- **Command injection**: `exec`, `shell_exec`, `child_process.exec`, `passthru` ที่มี input ปน
  → ใช้ `execFile` แบบส่ง array แทน
- **Path traversal**: endpoint ดาวน์โหลด/อ่านไฟล์ที่รับชื่อไฟล์จากผู้ใช้ ต้อง normalize แล้วเช็คว่ายังอยู่ใต้ base dir
- **Prototype pollution**: merge/`Object.assign` แบบ recursive กับ JSON จากผู้ใช้ — key `__proto__`, `constructor`

```bash
grep -rIn "dangerouslySetInnerHTML\|v-html\|innerHTML\|document.write\|eval(\|new Function(" src app --exclude-dir=node_modules
grep -rIn "whereRaw\|DB::raw\|selectRaw" src app --exclude-dir=node_modules
grep -rIn "child_process\|shell_exec\|passthru\|proc_open" src app --exclude-dir=node_modules
```

## 5. CSRF / CORS / SSRF

- **CSRF**: ถ้า auth อยู่ใน cookie ต้องมี CSRF token หรือ `SameSite=Strict/Lax` + เช็ค `Origin`
  ทุก endpoint ที่เปลี่ยนสถานะ — `GET` ห้ามเปลี่ยนข้อมูล
- **CORS**: `Access-Control-Allow-Origin: *` คู่กับ `Allow-Credentials: true` คือของที่ใช้ไม่ได้จริงและอันตราย
  ห้ามสะท้อน `Origin` ที่รับมากลับไปโดยไม่ผ่าน whitelist
  ระวัง regex ที่เขียนหลวม — `example.com` ต้องไม่ match `example.com.evil.net`
- **SSRF**: ทุกที่ที่เซิร์ฟเวอร์ยิง request ไปยัง URL ที่ผู้ใช้กำหนด (webhook, image proxy,
  PDF render, import จาก URL) ต้อง whitelist ปลายทาง และบล็อก `127.0.0.1`, `::1`,
  `169.254.169.254`, ช่วง private ทั้งหมด — และต้องเช็คซ้ำหลัง redirect ทุกครั้ง
- ระวัง endpoint ที่เชื่อ header อย่าง `X-Forwarded-For` / `X-Real-IP` เพื่อตัดสินสิทธิ์

## 6. Security headers / transport / CSP

ตรวจจาก response จริง ไม่ใช่จากไฟล์ config — `curl -sI https://<host>/<path>`

| Header | ค่าที่ควรเป็น |
| --- | --- |
| `Content-Security-Policy` | อย่างน้อย `default-src 'self'` + `connect-src` ล็อก origin ของ API + `frame-ancestors 'none'` |
| `Strict-Transport-Security` | `max-age=31536000` (มีผลทั้งโดเมน — เปิดเมื่อทุกเว็บบนโดเมนเป็น https แล้วเท่านั้น) |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` / CSP `frame-ancestors` | `DENY` หรือ `SAMEORIGIN` |
| `Referrer-Policy` | `no-referrer` หรือ `strict-origin-when-cross-origin` |
| `Permissions-Policy` | ปิด camera / microphone / geolocation ที่ไม่ได้ใช้ |
| `Cache-Control` (หน้าที่มีข้อมูลผู้ป่วย) | `no-store` |

- **CSP**: `'unsafe-eval'` ไม่ควรมี; `'unsafe-inline'` ที่ static export เลี่ยงไม่ได้ (ใช้ nonce ไม่ได้)
  → ชดเชยด้วยการล็อก `script-src` ให้เหลือ `'self'` และล็อก `connect-src` ให้แคบที่สุด
  แล้วเขียนข้อจำกัดนี้ไว้ในรายงาน
- **Cookie**: `HttpOnly`, `Secure`, `SameSite`, `Path` แคบ, ไม่ตั้ง `Domain` กว้างเกินจำเป็น
- **Transport**: บังคับ https, redirect http→https, ไม่มี mixed content, TLS ≥ 1.2
- `.htaccess` / nginx: ปิด directory listing, ปิดไฟล์ที่ขึ้นต้นด้วยจุด, ซ่อน `Server`/`X-Powered-By` ที่บอกเวอร์ชัน

## 7. Input validation / upload / rate limit

- validate ฝั่งเซิร์ฟเวอร์ทุก field ด้วย schema (zod / class-validator / FormRequest) —
  ฝั่ง client เป็นแค่ UX
- **Upload**: ตรวจชนิดไฟล์จาก magic bytes ไม่ใช่ `Content-Type` หรือนามสกุล, จำกัดขนาด,
  ตั้งชื่อไฟล์ใหม่เอง (กัน `../` และ null byte), เก็บนอก webroot หรือปิดการ execute ในโฟลเดอร์นั้น,
  **SVG = HTML** อัปได้เท่ากับ XSS ถ้าเสิร์ฟตรง
- **ผู้ใช้คุมขนาดงานได้แค่ไหน**: `?limit=`, `?page_size=`, ช่วงวันที่ของรายงาน, export ทั้งตาราง
  → ต้องมีเพดาน ไม่งั้นคนเดียวล้ม DB ได้
- **Open redirect**: `?next=` / `?redirect=` ต้องรับเฉพาะ path ภายใน
- **ReDoS**: regex ที่มี nested quantifier กับ input ที่ผู้ใช้ส่งมา
- rate limit ระดับ IP + ระดับบัญชี บน endpoint ที่แพงและบน login/OTP

## 8. Dependency & supply chain

```bash
npm audit --omit=dev                     # หรือ  composer audit / pip-audit
npm outdated | head -30
git status --short package-lock.json     # lockfile ต้องถูก commit และ CI ต้องใช้ npm ci
```

- ช่องโหว่ระดับ high/critical ใน dependency ที่อยู่ใน runtime path → อย่างน้อย High
- แพ็กเกจที่ไม่ได้อัปเดตหลายปี / ผู้ดูแลเปลี่ยนมือ / ชื่อคล้ายของดัง (typosquat)
- `postinstall` script ในแพ็กเกจที่เพิ่งเพิ่มเข้ามา
- `<script src="https://cdn...">` ในหน้าเว็บ **ต้องมี `integrity` (SRI) + `crossorigin`**
  หรือย้ายมา self-host ไปเลย
- GitHub Actions: pin เป็น commit SHA, ตั้ง `permissions:` ให้แคบ, ไม่ echo secret ลง log,
  ไม่ใช้ `pull_request_target` กับโค้ดของ fork

## 9. ข้อมูลผู้ป่วย / PDPA

หมวดนี้ "ไม่ใช่ช่องโหว่ทางเทคนิค แต่เป็นเรื่องที่โดนจริง"

- **HN, ชื่อ-นามสกุล, เลขบัตรประชาชน, วันเกิด, การวินิจฉัย** โผล่ใน:
  application log, access log (เพราะอยู่ใน query string), error message ที่ส่งถึง client,
  Referer ที่ส่งไปเว็บอื่น, analytics/third-party script, URL ที่ผู้ใช้ก๊อปไปแชร์
  → ข้อมูลระบุตัวตนควรอยู่ใน body ของ POST หรือเป็น id ที่ไม่สื่อความหมาย
- **API response ส่ง field เกินที่หน้าจอใช้** — หน้าจอไม่แสดง แต่ผู้ใช้เปิด DevTools เห็นหมด
- **Export / print / report** ต้องเช็คสิทธิ์เท่าหน้าจอปกติ
- **Audit trail**: บันทึกว่าใครเปิดดูข้อมูลของใครเมื่อไหร่ และ log นั้นต้องแก้ไม่ได้ง่าย ๆ
- **stack trace / SQL error ห้ามส่งถึง client** ใน production
- ข้อมูลผู้ป่วยจริงใน dev/staging/ไฟล์ dump ที่แชร์กัน — ต้อง mask
- backup: เข้ารหัสไหม เก็บที่ไหน ใครเข้าถึงได้ เก็บนานแค่ไหน

```bash
grep -rIn "console.log\|logger.info\|Log::info\|error_log" src app --exclude-dir=node_modules | grep -iE "hn|patient|citizen|idcard|name" | head -30
```

## 10. API & endpoint ที่ไม่ควรเปิด

- **Mass assignment**: `Model::create($request->all())`, กระจาย `req.body` ลง entity ตรง ๆ
  → กำหนด field ที่รับได้แบบ allowlist
- **Verbose error**: `APP_DEBUG=true`, Next dev overlay, whoops page บน prod
- **Endpoint ที่ไม่ควรเข้าถึงจากภายนอก**: `/phpinfo.php`, `/.env`, `/.git/config`,
  `/actuator`, `/telescope`, `/horizon`, `/swagger` ที่เปิด public พร้อม schema ทั้งระบบ,
  `/api/debug/*`, endpoint สำหรับ seed/reset
- **GraphQL**: ปิด introspection บน prod, จำกัด depth/complexity
- **HTTP method** ที่ไม่ได้ใช้ (`PUT`, `DELETE`, `TRACE`) ควรปิดที่ web server
- **เวอร์ชันเก่าของ API ที่ยังเปิดอยู่** — มักไม่ได้รับการแก้ตามตัวใหม่
- ถ้ามีการเรียก LLM/AI ภายนอก: ข้อมูลผู้ป่วยถูกส่งออกนอกองค์กรไหม, ข้อความที่ผู้ใช้พิมพ์
  (prompt injection) สั่งให้ระบบทำอะไรที่ไม่ควรทำได้ไหม

```bash
curl -sI https://<host>/.env
curl -sI https://<host>/.git/config
```

---

## สิ่งที่เช็คลิสต์นี้ตรวจแทนไม่ได้

เขียนไว้ในหัวข้อ "สิ่งที่ยังไม่ได้ตรวจ" ของรายงานเสมอ:

- การตั้งค่าบนเซิร์ฟเวอร์จริง (TLS, header ที่ Apache/nginx ใส่ทับ, firewall, สิทธิ์ไฟล์)
- ช่องโหว่ที่ต้องยิงทดสอบจริงถึงจะเห็น — การอ่านโค้ดบอกได้แค่ว่า "น่าจะ"
- ช่องโหว่ใน dependency ที่ยังไม่มีใน advisory database
- เรื่องคน: ใครมีสิทธิ์อะไรในระบบจริง, การแชร์รหัสผ่านร่วมกัน, เครื่องที่เปิดค้างไว้
