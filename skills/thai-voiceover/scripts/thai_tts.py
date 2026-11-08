#!/usr/bin/env python3
"""แปลงสคริปต์พากย์ภาษาไทยเป็นไฟล์ WAV ต่อเฟรม + audio_meta.json (รูปแบบของ HyperFrames)

ใช้:  uv run --python 3.11 --with pythaitts python thai_tts.py SCRIPT.txt --out-dir assets/voice
สคริปต์: เฟรมคั่นด้วยบรรทัดว่าง, 1 บรรทัด = 1 ประโยค, บรรทัดขึ้นต้น # เป็นหมายเหตุ
เอนจิน: pythaitts (CPU) หรือ thonburian (GPU + เสียงอ้างอิง) — auto เลือกให้ตามเครื่อง
"""
import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf


def read_frames(path):
    """คืนรายการเฟรม แต่ละเฟรมคือรายการประโยค"""
    frames, cur = [], []
    for line in Path(path).read_text(encoding="utf-8").splitlines() + [""]:
        line = line.strip()
        if line.startswith("#"):
            continue
        if line:
            cur.append(line)
        elif cur:
            frames.append(cur)
            cur = []
    return frames


def pick_engine(args):
    if args.engine != "auto":
        return args.engine, "ผู้ใช้ระบุเอง"
    if not args.ref:
        return "pythaitts", "ไม่มี --ref (เสียงอ้างอิง)"
    if not importlib.util.find_spec("torch"):
        return "pythaitts", "ไม่พบ torch"
    import torch
    if not torch.cuda.is_available():
        return "pythaitts", "ไม่พบ GPU CUDA"
    if not importlib.util.find_spec("flowtts"):
        return "pythaitts", "ไม่พบ flowtts"
    return "thonburian", "พบ GPU CUDA, flowtts และ --ref"


def make_synth(engine, args):
    """คืนฟังก์ชัน synth(text, wav_path) — สร้างโมเดลครั้งเดียว"""
    if engine == "pythaitts":
        from pythaitts import TTS
        tts = TTS(pretrained=args.model)
        return lambda text, out: tts.tts(text, speaker_idx=args.speaker, filename=out)
    import torch
    from flowtts.inference import AudioConfig, FlowTTSPipeline, ModelConfig
    mc = ModelConfig(
        language="th", model_type="F5",
        checkpoint="hf://biodatlab/ThonburianTTS/megaF5/mega_f5_last.safetensors",
        vocab_file="hf://biodatlab/ThonburianTTS/megaF5/mega_vocab.txt",
        vocoder="vocos", device="cuda" if torch.cuda.is_available() else "cpu")
    pipe = FlowTTSPipeline(mc, AudioConfig(silence_threshold=-45, cfg_strength=2.5, speed=1.0))
    return lambda text, out: pipe(text=text, ref_voice=args.ref, ref_text=args.ref_text, output_file=out)


def split_words(text, start, end, first_id):
    """แบ่งคำด้วย pythainlp แล้วกระจายเวลาตามความยาวตัวอักษร (ค่าประมาณ)"""
    from pythainlp.tokenize import word_tokenize
    words = word_tokenize(text, keep_whitespace=False)
    total = sum(len(w) for w in words)
    out, t = [], start
    for i, w in enumerate(words):
        nxt = end if i == len(words) - 1 else t + (end - start) * len(w) / total
        out.append({"id": f"w{first_id + i}", "text": w,
                    "start": round(t, 3), "end": round(nxt, 3)})
        t = nxt
    return out


def main():
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="สคริปต์พากย์ไทย -> WAV + audio_meta.json")
    ap.add_argument("script")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--meta", default="audio_meta.json")
    ap.add_argument("--engine", choices=["auto", "pythaitts", "thonburian"], default="auto")
    ap.add_argument("--model", default="fastthaig2p")
    ap.add_argument("--speaker", default="thai_som")
    ap.add_argument("--ref")
    ap.add_argument("--ref-text", default="")
    ap.add_argument("--gap", type=float, default=0.25)
    args = ap.parse_args()

    if not Path(args.script).is_file():
        sys.exit(f"ไม่พบไฟล์สคริปต์: {args.script}")
    frames = read_frames(args.script)
    if not frames:
        sys.exit("สคริปต์ว่าง: ไม่มีประโยคให้พากย์")
    engine, why = pick_engine(args)
    if engine == "thonburian" and not args.ref:
        sys.exit("--engine thonburian ต้องระบุ --ref (ไฟล์เสียงอ้างอิง)")
    print(f"เลือกเอนจิน {engine}: {why}", file=sys.stderr)

    synth = make_synth(engine, args)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    voices = []
    with tempfile.TemporaryDirectory() as tmp:
        for n, sentences in enumerate(frames, 1):
            chunks, words, pos, sr = [], [], 0, None
            for i, text in enumerate(sentences):
                tmp_wav = str(Path(tmp) / "s.wav")
                synth(text, tmp_wav)
                data, sr = sf.read(tmp_wav, dtype="float32")
                if data.ndim > 1:
                    data = data.mean(axis=1)
                words += split_words(text, pos / sr, (pos + len(data)) / sr, len(words))
                chunks.append(data)
                pos += len(data)
                if i < len(sentences) - 1:
                    gap = int(args.gap * sr)
                    chunks.append(np.zeros(gap, dtype="float32"))
                    pos += gap
            wav = out_dir / f"{n:02d}.wav"
            sf.write(str(wav), np.concatenate(chunks), sr, subtype="PCM_16")
            voices.append({"frame": n, "path": wav.as_posix(),
                           "duration_s": round(pos / sr, 3), "words": words})

    total = round(sum(v["duration_s"] for v in voices), 3)
    meta = {"tts_provider": engine,
            "voice_id": Path(args.ref).name if engine == "thonburian" else f"{args.model}:{args.speaker}",
            "bgm": None, "sfx": [], "voices": voices, "total_duration_s": total}
    Path(args.meta).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"เอนจิน: {engine} | {len(voices)} เฟรม")
    for v in voices:
        print(f"  เฟรม {v['frame']}: {v['path']} ({v['duration_s']} วินาที)")
    print(f"รวม {total} วินาที -> {args.meta}")


if __name__ == "__main__":
    main()
