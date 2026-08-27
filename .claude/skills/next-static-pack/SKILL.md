---
name: next-static-pack
description: Build a Next.js App Router project as a static export and pack it into a drop-in folder for Apache — `next build` to `out/`, fix the Windows RSC segment filenames, then emit `.htaccess` (RewriteBase + security headers + CSP locked to the backend origin) and a deploy README. Use when setting up or running the build/deploy of a Next.js site that Apache serves from a sub-path (no Node on the server), when the user says "build โปรเจกต์นี้", "แพ็กขึ้นเซิร์ฟเวอร์", "ขึ้น PRD" for a Next site, or when starting a new Next.js project that will be deployed this way.
---

# Next.js → static export → Apache

โรงพยาบาลเสิร์ฟเว็บด้วย **Apache + PHP รัน Node ไม่ได้** เว็บ Next ทุกตัวจึงต้อง
build เป็น static export แล้ววางทั้งโฟลเดอร์ใน DocumentRoot ใต้ path ย่อย
(เช่น `/phrae_icu_refer/`, `/phrae_icu_dashboard/`)

ทำแบบนี้มาแล้ว 2 โปรเจกต์ — `icu refer` (9000) กับ `ICU Dashboard` (9300)
สคริปต์ใน `references/` ก๊อปจากของจริงที่รันผ่านแล้ว

## ต้องมีครบ 5 อย่าง

1. **`next.config.ts`** — `output: "export"`, `trailingSlash: true`, `basePath`
2. **`src/lib/basePath.ts`** — แหล่งความจริงที่เดียวของ basePath ที่ config import ไปใช้
3. **`scripts/flatten-segments.mjs`** — ก๊อปจาก `references/` ตรง ๆ ไม่ต้องแก้
4. **`scripts/pack-deploy.mjs`** — ก๊อปจาก `references/` แล้วแก้ 3 ค่าบนหัวไฟล์
5. **`package.json`** — ต่อสคริปต์ 2 บรรทัด

```json
"build": "next build && node scripts/flatten-segments.mjs",
"pack": "npm run build && node scripts/pack-deploy.mjs",
```

`basePath.ts` ที่ควรเป็น:

```ts
export const BASE_PATH = "/phrae_xxx";
export function appPath(path: string): string {
  return `${BASE_PATH}${path}`;
}
```

Next เติม prefix ให้เองเฉพาะ `next/link`, `next/router`, asset ใน `.next/static`
และ `redirect()` — **`<a href>`, `<form action>`, `fetch()` ต้องเติมเองด้วย `appPath()`**

## บั๊ก RSC segment บน Windows — อย่าข้าม

`next build` บน Windows เขียนชื่อไฟล์ prefetch payload (`__next.*.txt`) ผิดรูป:
`collectSegmentPaths` คืน path ที่คั่นด้วย `\` ตัวแทนที่ `/`→`.` ไม่ได้แตะ
`path.join` เลยตีความเป็นตัวคั่นโฟลเดอร์แล้วสร้างไดเรกทอรีซ้อนออกมาแทนไฟล์แบน

```
ที่ build ได้     out/ward/__next.!KGFwcCk/ward/__PAGE__.txt
ที่เบราว์เซอร์ขอ  out/ward/__next.ward.__PAGE__.txt   -> 404
```

อาการที่ผู้ใช้เจอ: **ชี้เมนูแล้ว prefetch 404** เว็บยังกดเข้าได้ แต่ช้ากว่าที่ควร
`flatten-segments.mjs` ยุบโฟลเดอร์กลับเป็นชื่อไฟล์แบน — build บน Linux ไม่มีปัญหานี้
สคริปต์จะไม่เจออะไรให้ทำแล้วจบเงียบ ๆ **ต้องต่อท้าย `next build` เสมอ ไม่ใช่รันมือ**

## `.htaccess` ที่สคริปต์เขียนให้

- `RewriteBase` + fallback ทุก URL ที่ไม่ตรงไฟล์ไหนไปหน้าแรก (ให้ client router ต่อ)
- `<FilesMatch "^\.">` ปิดไฟล์ซ่อน
- security headers: nosniff, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`,
  Permissions-Policy ปิดกล้อง/ไมค์/GPS
- **CSP ที่ `connect-src` ล็อกไว้ที่ origin ของ `NEXT_PUBLIC_API_URL` เจ้าเดียว** —
  สคริปต์อ่าน `.env.local` เองแล้วยัดค่าลงไป **เปลี่ยน backend แล้วต้องแพ็กใหม่**
  ไม่งั้นเบราว์เซอร์บล็อกคำขอทั้งหมด
- HSTS คอมเมนต์ไว้ — มีผลทั้งโดเมน ไม่ใช่แค่โฟลเดอร์นี้ ถ้าโดเมนยังมีเว็บที่ต้องเข้าทาง
  http อยู่จะพังเป็นวงกว้างและแก้กลับยาก

**CSP ต้องตรงกับสิ่งที่แอปใช้จริง — เช็คก่อนแพ็ก:**

| แอปใช้อะไร | ต้องมีใน CSP |
| --- | --- |
| Next hydration (ทุกโปรเจกต์) | `script-src 'self' 'unsafe-inline'` — static export ใช้ nonce ไม่ได้ |
| recharts / ไลบรารีที่เขียน inline style | `style-src 'self' 'unsafe-inline'` |
| `next/font` | `font-src 'self'` พอ (ฟอนต์อบมากับ bundle) |
| ฟอนต์/ไอคอนจาก Google | เติม `https://fonts.googleapis.com` ที่ style-src และ `https://fonts.gstatic.com` ที่ font-src |

## ก่อนแพ็กขึ้น PRD — ถาม QA ก่อน

`npm run pack` คือการ build ขึ้น production กฎ `qa-before-prd` จึงมีผล —
ถามก่อนหนึ่งครั้งว่าจะรัน `qa` ก่อนไหม แล้วค่อยเริ่มจากขั้นต่อไปนี้
ผลตัดสิน **NO-GO แปลว่าห้ามแพ็ก** — รายงาน blocker แล้วหยุด

สิ่งที่ `qa` ตรวจแล้วสกัดกับเว็บ static เป็นพิเศษ: secret ที่ติดไปกับ bundle
ผ่าน `NEXT_PUBLIC_*`, source map ที่หลุดขึ้น prod, และ CSP/headers ใน `.htaccess`
ที่สคริปต์เขียนให้ — ดู `references/web-security-checklist.md` ของ skill `qa` หมวด 1, 6, 7

## ลำดับที่รัน

```bash
npm run pack                            # build + flatten + แพ็กไป ../<ชื่อโปรเจกต์>-deploy
node scripts/pack-deploy.mjs <ปลายทาง>   # แพ็กจาก build เดิม ไปที่อื่น
```

แล้ว rsync ทั้งโฟลเดอร์ไปที่ DocumentRoot ให้ได้ path ตรงกับ basePath

```bash
rsync -av --delete ../xxx-deploy/  www4:/var/www/html/phrae_xxx/
```

ฝั่งเซิร์ฟเวอร์ตั้งครั้งเดียว: `a2enmod rewrite headers` + `AllowOverride All`

## ตรวจก่อนบอกว่าเสร็จ

รันจริงแล้วดูผล อย่าเชื่อว่า build ผ่านแปลว่าใช้ได้

- [ ] `find out -type d -name "__next.*" | wc -l` ต้องได้ **0**
- [ ] มีไฟล์แบน `out/<route>/__next.<route>.__PAGE__.txt` ครบทุก route
- [ ] `.htaccess` มี `RewriteBase <basePath>/` ตรงกับ `basePath.ts`
- [ ] `connect-src` ใน CSP ตรงกับ origin ของ `NEXT_PUBLIC_API_URL` ที่จะใช้จริง
- [ ] `npm test` / `npx tsc --noEmit` ผ่าน

## กับดักที่เคยเจอ

- **อย่า hardcode basePath ลงใน pack-deploy** — อ่านจาก `basePath.ts` ด้วย regex
  ถ้าเขียนค่าซ้ำ วันหลังมีคนแก้ basePath แล้ว `RewriteBase` จะเพี้ยนแบบเงียบ ๆ
- **ค่า fallback ของ API ในสคริปต์ต้องตรงกับ `src/lib/env.ts` เป๊ะ ๆ** ไม่งั้นเวลาไม่มี
  `.env.local` CSP จะบล็อกปลายทางที่แอปยิงจริง
- **ปลายทางแพ็กอยู่นอกโปรเจกต์** (`../xxx-deploy`) จะได้ไม่ปนซอร์สและไม่หลุดเข้า git
  สคริปต์ลบปลายทางก่อนแพ็กใหม่ และกันลบผิดที่ด้วยการเช็คว่ามี `index.html` อยู่ก่อน
- **ไม่มี `npm run start`** — เป็นคำสั่งของ Next ที่รันเซิร์ฟเวอร์ ซึ่ง static export ไม่มี
  อยากลองผลลัพธ์ให้เสิร์ฟ `out/` ด้วย static server ตัวไหนก็ได้
- **พอร์ต dev ผูกตายใน `package.json`** ห้ามชนกัน — icu refer 9000, ICU Dashboard 9300
  โปรเจกต์ใหม่เลือกพอร์ตที่ยังว่างแล้วจดไว้ใน README
