---
name: framer-motion
description: Check whether framer-motion (now published as `motion`, imported from `motion/react`) fits an existing project, then add animation to a React / Next.js App Router site the team's way — "use client" boundaries, LazyMotion to keep the bundle small, reduced-motion support, CSP on the Apache static export, and no replaying animations on dashboard polling. Use when the user asks "ใช้ framer-motion ได้ไหม", "เช็ค package framer-motion", "ใส่ animation", "ทำให้เว็บมี motion", "เพิ่ม transition ให้ panel/การ์ด", or names framer-motion / motion / AnimatePresence in a React or Next project.
---

# framer-motion (`motion`) ในโปรเจกต์ของทีม

framer-motion เป็น library ของ **React เท่านั้น** ตอนนี้ออกในชื่อใหม่ว่า `motion` ด้วย
(ทีมเดียวกัน API เดียวกัน และเวอร์ชันตรงกัน คือ 14.14.0 ณ 2026-11-21)

โปรเจกต์ที่เช็คแล้ว: **ICU Dashboard** (`IT-Phrae-hospital/phrae-icu-dashboard`)
ใช้ React 19.2.8 + Next 16 App Router + `output: "export"` บน Apache ใช้ได้ทุกข้อ
แต่ยังไม่ได้ติดตั้งจริง (ตรวจเมื่อ 2026-11-21)

## 1. เช็คก่อนว่าใช้ได้ไหม

ทำครบทุกข้อก่อนแนะนำให้ติดตั้ง แล้วรายงานเป็นตาราง (ข้อที่ดู / สิ่งที่พบ / ผล)

1. **peer dependency ของเวอร์ชันปัจจุบัน:** `npm view motion version peerDependencies`
   ต้องได้ `react` + `react-dom` (ตอนนี้คือ `^18 || ^19`)
2. **`package.json` ของโปรเจกต์:** มี `react` / `react-dom` อยู่ในช่วงนั้นไหม
   - ไม่มี React (Vue, Quasar, Laravel Blade, PHP ล้วน) → **ใช้ไม่ได้** บอกผู้ใช้แล้วหยุด
     ห้ามแนะนำให้ลง React เพิ่มเพื่อใช้ library นี้
3. **มี animation library อยู่แล้วไหม** (`framer-motion`, `motion`, `react-spring`, `gsap`,
   `react-transition-group`) ถ้ามีให้ใช้ตัวเดิมต่อ ห้ามลงซ้อน
   ถ้ามี `framer-motion` อยู่แล้วก็ใช้ต่อ ไม่ต้องย้ายไป `motion`
4. **Next App Router:** component ที่ใช้ `motion.*`, `AnimatePresence` หรือ hook ต้องเป็น
   client component (`"use client"`) ดูว่าหน้าที่จะใส่เป็น client อยู่แล้วหรือยัง
5. **CSP ตอน deploy** (`.htaccess` หรือ `scripts/pack-deploy.mjs` ของ `next-static-pack`):
   ตอน static export ค่า `initial` จะถูกเขียนลง HTML เป็น attribute `style="..."`
   ถ้า CSP ไม่มี `style-src 'unsafe-inline'` attribute นั้นจะโดนบล็อก ทำให้ element กระตุก
   ตอนโหลด (เพราะไม่ได้ initial state) โปรเจกต์ที่มี recharts เปิดค่านี้ไว้อยู่แล้ว
   ส่วนค่าที่ motion ตั้งผ่าน `element.style` ตอนเล่น animation นั้น CSP ไม่บล็อก

## 2. ติดตั้ง

```
npm i motion
```

import จาก `motion/react` เสมอ (ห้ามปน `framer-motion` กับ `motion` ในโปรเจกต์เดียวกัน)

ครอบทั้งแอปด้วย provider ตัวเดียว เพื่อให้ bundle เล็ก (`LazyMotion` + `m.*` แทน `motion.*`)
และเคารพการตั้งค่า "ลดการเคลื่อนไหว" ของเครื่องผู้ใช้:

```tsx
// src/components/MotionProvider.tsx
"use client";
import { LazyMotion, MotionConfig, domAnimation } from "motion/react";

export default function MotionProvider({ children }: { children: React.ReactNode }) {
  return (
    <LazyMotion features={domAnimation} strict>
      <MotionConfig reducedMotion="user">{children}</MotionConfig>
    </LazyMotion>
  );
}
```

ใส่ใน `src/app/layout.tsx` (server component ครอบ client component ได้) แล้วในทุกไฟล์ใช้
`import * as m from "motion/react-m"` เขียน `<m.div>` (`strict` จะ error ถ้าเผลอใช้ `motion.div`)
ถ้าต้องใช้ drag หรือ layout animation ให้เปลี่ยน `domAnimation` เป็น `domMax`

## 3. กฎสำหรับ dashboard

จอ dashboard มักเปิดค้างและดึงข้อมูลใหม่เป็นรอบ ๆ

- **เล่น animation ตอน mount ครั้งแรก กับตอนผู้ใช้กดเท่านั้น** ห้ามเล่นซ้ำทุกรอบ polling
  ห้ามเปลี่ยน `key` ของรายการตามรอบ fetch (React จะ mount ใหม่ทำให้ animation เล่นซ้ำ)
  ให้ใช้ id ที่คงที่ เช่นรหัส ward หรือ HN
- **ตัวเลขที่เปลี่ยน:** animate เฉพาะตอนค่าเปลี่ยนจริง ไม่ใช่ทุกครั้งที่ render
- **กราฟ recharts มี animation ของตัวเองแล้ว** ไม่ต้องครอบด้วย motion
- เวลาไม่เกินประมาณ 0.3 วินาทีสำหรับ UI และ stagger รวมทั้งหมดไม่ควรเกิน 0.5 วินาที
- ห้าม animate ข้อมูลที่ต้องอ่านทันที (สถานะวิกฤต สีระดับความรุนแรง) ให้ช้าลงเพราะ animation

## 4. pattern ที่ใช้บ่อย

**panel / dialog เลื่อนเข้า-ออก:** `AnimatePresence` ต้องอยู่นอกเงื่อนไข ไม่อย่างนั้นจะไม่มี exit animation

```tsx
<AnimatePresence>
  {open && (
    <m.aside
      key="drilldown"
      initial={{ x: "100%" }}
      animate={{ x: 0 }}
      exit={{ x: "100%" }}
      transition={{ duration: 0.25, ease: "easeOut" }}
    >
      …
    </m.aside>
  )}
</AnimatePresence>
```

**การ์ดค่อย ๆ โผล่ทีละใบตอนโหลดครั้งแรก:**

```tsx
{wards.map((w, i) => (
  <m.div
    key={w.code}
    initial={{ opacity: 0, y: 8 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.2, delay: Math.min(i * 0.03, 0.3) }}
  >
    …
  </m.div>
))}
```

**ตัวเลขนับขึ้นตอนค่าเปลี่ยน:**

```tsx
const mv = useMotionValue(value);
const text = useTransform(mv, (v) => Math.round(v).toLocaleString("th-TH"));
useEffect(() => {
  const c = animate(mv, value, { duration: 0.5 });
  return () => c.stop();
}, [mv, value]);
return <m.span>{text}</m.span>;
```

**สลับมุมมอง** (รายวัน/สัปดาห์/เดือน): `AnimatePresence mode="wait"` ครอบเนื้อหา
ที่ใช้ `key={view}` ให้ fade ออกก่อนแล้วค่อย fade เข้า

## 5. ก่อนบอกว่าเสร็จ

- รัน `npm run build` (หรือ `npm run pack` ถ้าใช้ `next-static-pack`) ให้ผ่าน
- เปิดหน้าจาก `out/` ผ่าน Apache หรือ server ที่ส่ง CSP เดียวกัน แล้วดู console ว่าไม่มี
  CSP violation และไม่มี element กระพริบตอนโหลด
- เปิด "ลดการเคลื่อนไหว" ใน OS แล้วดูว่าการเคลื่อนที่ถูกปิด
- ปล่อยหน้าไว้ข้ามรอบ polling อย่างน้อยหนึ่งรอบ แล้วดูว่า animation ไม่เล่นซ้ำ
- API อาจเปลี่ยนตามเวอร์ชันหลัก ถ้า `npm view motion version` ไม่ใช่ 14.x ให้เทียบตัวอย่าง
  ด้านบนกับเอกสารที่ motion.dev ก่อนใช้
