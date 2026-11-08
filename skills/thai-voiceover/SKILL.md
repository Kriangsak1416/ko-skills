---
name: thai-voiceover
description: Turn a Thai narration script into voiceover WAV files (one per frame) plus per-word timings and a HyperFrames-compatible audio_meta.json. Auto-picks ThonburianTTS (voice cloning) when a CUDA GPU and a reference voice are available, otherwise PyThaiTTS on CPU. Use when the user asks for "เสียงพากย์ไทย", "พากย์เสียง", "อ่านออกเสียง", "text to speech ภาษาไทย", "ทำ voiceover", or needs Thai narration for a HyperFrames video.
---

# เสียงพากย์ไทย (WAV + audio_meta.json)

แปลงสคริปต์พากย์ภาษาไทยเป็นไฟล์เสียง `.wav` ต่อ 1 เฟรม พร้อมเวลาของแต่ละคำ และเขียน
`audio_meta.json` ในรูปแบบที่ pipeline faceless-explainer ของ HyperFrames อ่านได้
ใช้เมื่อต้องการเสียงพากย์ไทยสำหรับวิดีโอ หรืออ่านข้อความไทยออกเสียงเป็นไฟล์ WAV
`scripts/thai_tts.py` เลือกเอนจินให้เอง: มี GPU CUDA และเสียงอ้างอิง -> ThonburianTTS (โคลนเสียงได้)
ไม่เช่นนั้น -> PyThaiTTS (รันบน CPU)

## สิ่งที่ต้องมี

- `uv` และ `ffmpeg` (ใช้ตรวจไฟล์เสียงด้วย `ffprobe`)
- เส้นทาง CPU ไม่ต้องติดตั้งอะไรเพิ่ม `uv run --with pythaitts` ลงให้ทันที
  รันครั้งแรกจะดาวน์โหลดโมเดล (ราว ๆ หลายสิบ MB จาก GitHub/HF) ต้องต่ออินเทอร์เน็ต

## 1. เขียนสคริปต์

ดูตัวอย่างที่ `examples/script.txt`

- เฟรมคั่นด้วยบรรทัดว่าง (เฟรม 1..N ตามลำดับ)
- 1 บรรทัด = 1 ประโยค ยิ่งสั้นยิ่งอ่านเป็นธรรมชาติ และเวลาของคำแม่นขึ้น
- บรรทัดขึ้นต้นด้วย `#` เป็นหมายเหตุ ไม่ถูกอ่าน
- ตัวเลขอาราบิก PyThaiTTS แปลงเป็นคำอ่านไทยให้อัตโนมัติ (`5` -> "ห้า")

## 2. รันคำสั่ง

CPU (ค่าเริ่มต้น เสียง `thai_som`):

```
uv run --python 3.11 --with pythaitts python <skill-dir>/scripts/thai_tts.py script.txt --out-dir assets/voice --meta audio_meta.json
```

เสียงผู้ชาย:

```
... thai_tts.py script.txt --out-dir assets/voice --model makham --speaker newvoice_male
```

(`makham` มี `newvoice_female` / `newvoice_male`)

GPU + ThonburianTTS โคลนเสียง — **ยังไม่ได้ทดสอบ เพราะเครื่องที่เขียน skill ไม่มี GPU**:

```
uv run --python 3.11 --with pythaitts --with "git+https://github.com/biodatlab/thonburian-tts.git" --with torch --index https://download.pytorch.org/whl/cu124 python <skill-dir>/scripts/thai_tts.py script.txt --out-dir assets/voice --ref ref.wav --ref-text "ข้อความที่พูดในไฟล์ ref.wav ตรงตามจริง"
```

- เสียงอ้างอิง 5–15 วินาที พูดชัด ไม่มีเสียงรบกวน และ `--ref-text` ต้องเป็นคำพูดในคลิปนั้นตรงตัว
- `--engine auto` (ค่าเริ่มต้น) จะแจ้งทาง stderr ว่าเลือกเอนจินอะไรเพราะอะไร
  บังคับด้วย `--engine pythaitts` หรือ `--engine thonburian` (อย่างหลังต้องมี `--ref`)
- `--gap` คือความเงียบระหว่างประโยคในเฟรมเดียวกัน (ค่าเริ่มต้น 0.25 วินาที)

ตรวจผล: `ffprobe -v error -show_entries format=duration:stream=sample_rate,channels -of default=nw=1 assets/voice/01.wav`

## 3. ใช้กับ HyperFrames

1. เขียน WAV ลง `assets/voice/` ของโปรเจกต์ และ meta ที่ `./audio_meta.json`
2. เลขเฟรมต้องตรงกับหัวข้อ `(Frame N)` ใน `SCRIPT.md`
3. ข้ามขั้น TTS ของ HyperFrames (`--provider` รับแค่ heygen/elevenlabs/kokoro ซึ่งพูดไทยไม่ได้)
   แล้วรันต่อที่ขั้นซิงก์เวลา:
   ```
   node <hyperframes-skills>/faceless-explainer/scripts/audio.mjs sync-durations --audio-meta ./audio_meta.json --storyboard ./STORYBOARD.md
   ```
   (`<hyperframes-skills>` คือโฟลเดอร์ `skills/` ของปลั๊กอิน hyperframes เช่น
   `~/.claude/plugins/cache/claude-plugins-official/hyperframes/<version>/skills`)
   จากนั้นทำขั้น captions ตามปกติ
4. แคปชั่นไทยต้องฝังฟอนต์ที่มีอักษรไทยผ่าน `@font-face` (เช่น Noto Sans Thai, Sarabun)
5. ถ้าต้องการเวลาของคำที่แม่นจริง ให้ถอดเสียงจากไฟล์ที่ได้:
   `npx hyperframes transcribe assets/voice/01.wav --model small --language th`
   (ห้ามใช้โมเดล `.en`)

## ข้อจำกัด

- เวลาของแต่ละคำเป็นค่าประมาณ กระจายตามความยาวตัวอักษรภายในประโยค
  ส่วนขอบเขตของประโยคแม่นยำ เพราะรู้จากความยาวเสียงจริง
- น้ำหนักโมเดล ThonburianTTS เป็น CC BY-NC-SA 4.0 ห้ามใช้เชิงพาณิชย์
- โค้ดของ PyThaiTTS เป็น Apache-2.0 แต่สัญญาอนุญาตของน้ำหนักโมเดลแต่ละตัวต้องตรวจเองก่อนใช้เชิงพาณิชย์
- ThonburianTTS รันบน CPU ได้ แต่ช้ามาก
- บน Windows `huggingface_hub` จะเตือนเรื่อง symlink ตอนโหลดโมเดล `makham` ครั้งแรก ไม่มีผลกับเสียงที่ได้
