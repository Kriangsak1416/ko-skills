// แก้ชื่อไฟล์ RSC segment ที่ next build บน Windows เขียนผิดรูป
//
// ไฟล์ __next.*.txt คือ payload ที่เบราว์เซอร์ดึงมา prefetch ตอนชี้เมนู Next ตั้งใจให้เป็น
// ไฟล์แบนชื่อเดียว โดยแทน "/" ในชื่อ segment ด้วย "." (convertSegmentPathToStaticExportFilename)
// แต่ collectSegmentPaths คืน path ที่คั่นด้วย "\" บน Windows ซึ่งตัวแทนที่ไม่ได้แตะ
// path.join จึงตีความเป็นตัวคั่นโฟลเดอร์แล้วสร้างไดเรกทอรีซ้อนออกมาแทน
//
//   ที่ build ได้     out/refer/new/__next.!KGFwcCk/refer/new/__PAGE__.txt
//   ที่เบราว์เซอร์ขอ  out/refer/new/__next.!KGFwcCk.refer.new.__PAGE__.txt   -> 404
//
// สคริปต์นี้ยุบโฟลเดอร์ที่ซ้อนกลับเป็นชื่อไฟล์แบนตามที่เบราว์เซอร์ขอ
// build บน Linux ไม่มีปัญหานี้ตั้งแต่แรก สคริปต์จะไม่เจออะไรให้ทำแล้วจบเงียบ ๆ
import { readdirSync, renameSync, rmSync, statSync } from "node:fs";
import { basename, join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const OUT = join(ROOT, "out");

// คืน path ของไฟล์ทุกไฟล์ใต้ dir (เทียบกับ dir) — โครงในนี้ตื้นมาก ไม่ต้องกลัว recursion ลึก
function filesUnder(dir, prefix = []) {
  const found = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      found.push(...filesUnder(join(dir, entry.name), [...prefix, entry.name]));
    } else {
      found.push([...prefix, entry.name]);
    }
  }
  return found;
}

// เดินหาโฟลเดอร์ชื่อขึ้นต้นด้วย "__next." ทุกชั้นใน out/
function brokenDirs(dir) {
  const found = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const full = join(dir, entry.name);
    if (entry.name.startsWith("__next.")) found.push(full);
    else found.push(...brokenDirs(full));
  }
  return found;
}

// ไม่มี out/ = build เป็นเซิร์ฟเวอร์ Node ไม่ใช่ static export จึงไม่มีไฟล์ให้แก้
if (!statSync(OUT, { throwIfNoEntry: false })?.isDirectory()) {
  console.log("ไม่ได้ build เป็น static export — ข้ามขั้นตอนแก้ชื่อไฟล์ RSC segment");
  process.exit(0);
}

let moved = 0;
for (const dir of brokenDirs(OUT)) {
  const base = basename(dir);
  for (const parts of filesUnder(dir)) {
    renameSync(join(dir, ...parts), join(dirname(dir), [base, ...parts].join(".")));
    moved++;
  }
  rmSync(dir, { recursive: true });
}

console.log(
  moved === 0
    ? "ไฟล์ RSC segment อยู่ในรูปที่ถูกต้องแล้ว ไม่ต้องแก้"
    : `แก้ชื่อไฟล์ RSC segment แล้ว ${moved} ไฟล์`,
);
