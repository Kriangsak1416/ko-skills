// เทมเพลต — ก๊อปไปวางที่ scripts/pack-deploy.mjs ของโปรเจกต์ แล้วแก้ 3 ค่าในบล็อก "ค่าประจำโปรเจกต์"
//
// รวมไฟล์ static ที่ next build คายไว้ใน out/ เป็นชุดพร้อมวางใน DocumentRoot ของ Apache
// ใช้: npm run pack           (build ใหม่แล้วแพ็ก)
//      node scripts/pack-deploy.mjs [ปลายทาง]   (แพ็กจาก build ที่มีอยู่แล้ว)
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// ===== ค่าประจำโปรเจกต์ — แก้ 3 บรรทัดนี้ =====
const APP_NAME = "ชื่อโปรเจกต์";              // โผล่ในหัว .htaccess และ README.txt ของชุดที่แพ็ก
const DEFAULT_DEST = "../ชื่อโปรเจกต์-deploy"; // ปลายทางเริ่มต้น อยู่นอกโปรเจกต์ จะได้ไม่หลุดเข้า git
const API_FALLBACK = "https://example.go.th/api"; // ต้องตรงกับค่า default ใน src/lib/env.ts เป๊ะ ๆ
// =============================================

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");

const outDir = resolve(ROOT, process.argv[2] ?? DEFAULT_DEST);

const exported = join(ROOT, "out");
if (!existsSync(exported)) {
  console.error('ไม่พบโฟลเดอร์ out/ — รัน `npm run build` ก่อน (ต้องมี output: "export" ใน next.config.ts)');
  process.exit(1);
}

// ล้างของเก่าก่อนแพ็กใหม่ ไม่งั้นไฟล์ที่ถูกลบไปแล้วจะค้างอยู่บนเซิร์ฟเวอร์
// กันลบผิดโฟลเดอร์: ยอมลบเฉพาะโฟลเดอร์ว่าง หรือโฟลเดอร์ที่เคยแพ็กไว้
if (existsSync(outDir)) {
  const entries = readdirSync(outDir);
  const looksLikeOurs = entries.includes("index.html");
  if (entries.length > 0 && !looksLikeOurs) {
    console.error(`ปลายทาง ${outDir} มีไฟล์อื่นอยู่และไม่ใช่ผลลัพธ์ของสคริปต์นี้ — ยกเลิกเพื่อกันลบผิดที่`);
    process.exit(1);
  }
  rmSync(outDir, { recursive: true, force: true });
}
mkdirSync(outDir, { recursive: true });

cpSync(exported, outDir, { recursive: true });

// เว็บอยู่ใต้ path ย่อยของโดเมน — ต้องตรงกับ basePath ที่ build มา
// อ่านจาก src/lib/basePath.ts ที่เป็นแหล่งความจริงที่เดียว แทนที่จะเขียนค่าซ้ำไว้ตรงนี้
// ไม่งั้นเปลี่ยน basePath แล้ว RewriteBase ใน .htaccess จะเพี้ยนแบบเงียบ ๆ
const basePathSrc = readFileSync(join(ROOT, "src/lib/basePath.ts"), "utf8");
const BASE = basePathSrc.match(/export const BASE_PATH = "([^"]*)"/)?.[1];
if (BASE === undefined) {
  console.error("อ่าน BASE_PATH จาก src/lib/basePath.ts ไม่ได้ — รูปแบบไฟล์เปลี่ยนไปหรือเปล่า");
  process.exit(1);
}

// CSP ต้องระบุให้ตรงว่าเว็บยิงออกไปที่ไหนได้บ้าง ซึ่งก็คือ backend ที่ NEXT_PUBLIC_API_URL
// สคริปต์นี้เป็นคนละโปรเซสกับ next build จึงต้องอ่าน .env.local เอง
try {
  process.loadEnvFile(join(ROOT, ".env.local"));
} catch {
  // ไม่มีไฟล์ก็ใช้ค่าที่ตั้งมาทาง environment แทน
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? API_FALLBACK;
if (!process.env.NEXT_PUBLIC_API_URL) {
  console.warn(
    `เตือน: ไม่ได้ตั้ง NEXT_PUBLIC_API_URL — CSP จะอนุญาตแค่ ${API_URL} ตามค่าเริ่มต้นของโค้ด`,
  );
}

let API_ORIGIN;
try {
  API_ORIGIN = new URL(API_URL).origin;
} catch {
  console.error(`NEXT_PUBLIC_API_URL ไม่ใช่ URL ที่ถูกต้อง: ${API_URL}`);
  process.exit(1);
}

writeFileSync(
  join(outDir, ".htaccess"),
  `# ${APP_NAME} — static export วางใน DocumentRoot ของ Apache
#
# ทุกหน้าถูก build เป็นไฟล์ index.html ไว้ล่วงหน้าแล้ว (trailingSlash: true)
# กฎด้านล่างมีไว้กันกรณีเปิด URL ที่ไม่ตรงกับไฟล์ไหนเลย ให้ตกมาที่หน้าแรก
# แทนที่จะเป็นหน้า 404 ของ Apache

<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase ${BASE}/

    # มีไฟล์/โฟลเดอร์จริงอยู่แล้ว เสิร์ฟไปตามนั้น
    RewriteCond %{REQUEST_FILENAME} -f [OR]
    RewriteCond %{REQUEST_FILENAME} -d
    RewriteRule ^ - [L]

    # ไม่ตรงกับอะไรเลย -> หน้าแรก (ให้ client router จัดการต่อ)
    RewriteRule . ${BASE}/index.html [L]
</IfModule>

# กันไม่ให้ดาวน์โหลดไฟล์ที่ไม่ควรเปิดเผย เผลอหลุดขึ้นมาก็ยังปิดอยู่
<FilesMatch "^\.">
    Require all denied
</FilesMatch>

# ===== ส่วนหัวด้านความปลอดภัย =====
# ต้องเปิด mod_headers ก่อน:  sudo a2enmod headers && sudo systemctl reload apache2
# ถ้าไม่ได้เปิด บล็อกนี้จะถูกข้ามไปเงียบ ๆ เว็บยังใช้ได้แต่ไม่มีส่วนหัวพวกนี้
<IfModule mod_headers.c>
    # ห้ามเบราว์เซอร์เดาชนิดไฟล์เอง
    Header always set X-Content-Type-Options "nosniff"

    # กัน clickjacking — ห้ามเอาหน้านี้ไปซ้อนใน iframe ของเว็บอื่น
    # (frame-ancestors ใน CSP คุมตัวเดียวกัน บรรทัดนี้ไว้เผื่อเบราว์เซอร์รุ่นเก่า)
    Header always set X-Frame-Options "DENY"

    # ไม่ส่ง referrer ออกไปไหนเลย
    Header always set Referrer-Policy "no-referrer"

    # ปิดสิทธิ์อุปกรณ์ที่เว็บนี้ไม่ได้ใช้
    Header always set Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()"

    # script-src ต้องมี 'unsafe-inline' เพราะ Next ฝังสคริปต์ hydration ไว้ในหน้าโดยตรง
    # และ static export ใช้ nonce ไม่ได้ (ไม่มีเซิร์ฟเวอร์มาสุ่มค่าให้ทุกคำขอ)
    # style-src ต้องมี 'unsafe-inline' ถ้าใช้ recharts/ไลบรารีที่เขียน style ลง element ตรง ๆ
    # font-src ปิดที่ 'self' ได้ถ้าใช้ next/font (ฟอนต์ถูกอบมากับ bundle)
    #   ถ้าโหลดฟอนต์/ไอคอนจาก Google ต้องเติม:
    #   style-src ... https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com
    # connect-src ปิดตายไว้ที่ backend เจ้าเดียว
    Header always set Content-Security-Policy "default-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; object-src 'none'; img-src 'self' data:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self' ${API_ORIGIN}"

    # HSTS มีผลกับทั้งโดเมน ไม่ใช่แค่โฟลเดอร์นี้ — ถ้าโดเมนมีเว็บอื่นที่ยังต้องเข้าทาง http
    # อยู่จะเข้าไม่ได้ทันทีและแก้กลับยาก (เบราว์เซอร์จำไว้นาน)
    # ยืนยันว่าทั้งโดเมนเป็น https หมดแล้วค่อยเปิดบรรทัดนี้
    # Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
</IfModule>
`,
  "utf8",
);

writeFileSync(
  join(outDir, "README.txt"),
  `${APP_NAME} — ชุดไฟล์สำหรับวางบน Apache (static export)
สร้างเมื่อ ${new Date().toLocaleString("th-TH")}

วิธีใช้
  1. ก็อปทั้งโฟลเดอร์ไปวางที่ DocumentRoot ให้ได้ path ${BASE}/
     เช่น /var/www/html${BASE}/
  2. เปิด mod_rewrite (ครั้งเดียว):  sudo a2enmod rewrite && sudo systemctl reload apache2
  3. เปิด mod_headers เพื่อให้ส่วนหัวด้านความปลอดภัยใน .htaccess ทำงาน (ครั้งเดียว):
       sudo a2enmod headers && sudo systemctl reload apache2
  4. ให้ .htaccess ทำงานได้ ต้องมีใน Apache config:
       <Directory /var/www/html>
           AllowOverride All
       </Directory>
  5. เปิด https://<โดเมน>${BASE}/

ไม่ต้องติดตั้ง Node บนเซิร์ฟเวอร์ ไม่ต้องรัน process ใด ๆ

หมายเหตุ
  - URL ของ backend ถูกอบไว้ตอน build แล้ว (NEXT_PUBLIC_API_URL)
    เปลี่ยน backend = ต้อง build ใหม่ ไม่ใช่แก้ไฟล์บนเซิร์ฟเวอร์
  - เว็บถูก build ให้อยู่ใต้ path ${BASE} เปลี่ยน path ต้อง build ใหม่เช่นกัน
  - ไม่มีไฟล์ .env ในชุดนี้ และไม่ต้องมี
  - CSP ใน .htaccess อนุญาตให้ยิงออกได้เฉพาะ ${API_ORIGIN} เปลี่ยน backend
    เมื่อไหร่ต้องแพ็กใหม่ ไม่งั้นเบราว์เซอร์จะบล็อกคำขอทั้งหมด
`,
  "utf8",
);

console.log(`แพ็กเสร็จแล้ว: ${outDir}`);
console.log(`ขั้นต่อไป: ก็อปทั้งโฟลเดอร์ไปวางที่ DocumentRoot ให้ได้ path ${BASE}/`);
