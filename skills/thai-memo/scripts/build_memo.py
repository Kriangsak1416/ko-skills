#!/usr/bin/env python3
"""สร้างบันทึกข้อความ (.docx) ตามแบบงานสารบรรณจาก spec JSON

ใช้:  python build_memo.py <spec.json> [out.docx]
รูปแบบ spec ดูใน SKILL.md และ examples/ — ใช้ stdlib อย่างเดียว ไม่ต้องลง package
"""
import json
import re
import struct
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
GARUDA = HERE.parent / "assets" / "garuda.png"

BODY_FONT = "TH SarabunIT๙"  # ฟอนต์นี้แสดงเลข 0-9 เป็นเลขไทย
CODE_FONT = "TH SarabunPSK"  # เลขอารบิก — ใช้กับรหัส / URL / ค่าที่ต้องพิมพ์ตาม
TEXT_W = 9071  # ความกว้างบรรทัด (twips) = A4 − ขอบซ้าย 3 ซม. − ขอบขวา 2 ซม.
INDENT = 1418  # ย่อหน้า 2.5 ซม.
EMU_PER_CM = 360000
THAI_DIGITS = str.maketrans("0123456789", "๐๑๒๓๔๕๖๗๘๙")

NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"')
HDR_PAGE, HDR_EMPTY = "rIdHdrPage", "rIdHdrEmpty"

MEDIA = []  # (rId, bytes) ของรูปที่ฝังในเอกสาร
BASE = Path(".")  # โฟลเดอร์ของ spec — path รูปแบบ relative อ้างจากตรงนี้


def run(text="", bold=False, size=32, font=BODY_FONT, dotted=False, tab=False):
    rpr = f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:eastAsia="{font}" w:cs="{font}"/>'
    if bold:
        rpr += "<w:b/><w:bCs/>"
    rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    if dotted:
        rpr += '<w:u w:val="dotted"/>'
    body = "<w:tab/>" if tab else f'<w:t xml:space="preserve">{escape(text)}</w:t>'
    return f"<w:r><w:rPr>{rpr}</w:rPr>{body}</w:r>"


def inline(text, size=32, bold=False):
    """**ตัวหนา** และ `รหัส` (ฟอนต์เลขอารบิก) ภายในข้อความ"""
    out = []
    for part in re.split(r"(\*\*.+?\*\*|`[^`]+`)", text):
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            out.append(run(part[2:-2], bold=True, size=size))
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            out.append(run(part[1:-1], bold=bold, size=size, font=CODE_FONT))
        elif part:
            out.append(run(part, bold=bold, size=size))
    return "".join(out)


def para(runs="", jc=None, first=None, left=None, hanging=None, right=None,
         before=0, after=0, tabs=(), keep_next=False, shade=None, sect=""):
    ppr = "<w:keepNext/>" if keep_next else ""
    if shade:
        ppr += f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>'
    if tabs:
        ppr += "<w:tabs>" + "".join(f'<w:tab w:val="{k}" w:pos="{p}"/>' for k, p in tabs) + "</w:tabs>"
    ppr += f'<w:spacing w:before="{before}" w:after="{after}"/>'
    ind = "".join(f' w:{k}="{v}"' for k, v in
                  (("left", left), ("right", right), ("firstLine", first), ("hanging", hanging))
                  if v is not None)
    if ind:
        ppr += f"<w:ind{ind}/>"
    if jc:
        ppr += f'<w:jc w:val="{jc}"/>'
    return f"<w:p><w:pPr>{ppr}{sect}</w:pPr>{runs}</w:p>"


def image_run(path, width_cm):
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit(f"รองรับเฉพาะรูป PNG: {path}")
    w, h = struct.unpack(">II", data[16:24])
    MEDIA.append((f"rIdImg{len(MEDIA) + 1}", data))
    rid, n = MEDIA[-1][0], len(MEDIA)
    cx = int(width_cm * EMU_PER_CM)
    cy = int(cx * h / w)
    return (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{n}" name="Picture {n}"/>'
            '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic><pic:nvPicPr><pic:cNvPr id="{n}" name="image{n}.png"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            "</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>")


def header_block(spec):
    def label(t):
        return run(t, bold=True, size=40)

    def value(t):
        return run(" " + t, dotted=True)

    fill = run(dotted=True, tab=True)  # เส้นประลากถึง tab ถัดไป
    return [
        para(image_run(GARUDA, 1.37) + run(tab=True) + run("บันทึกข้อความ", bold=True, size=58),
             tabs=[("center", TEXT_W // 2)]),
        para(label("ส่วนราชการ") + value(spec["agency"]) + fill, tabs=[("left", TEXT_W)]),
        para(label("ที่") + value(spec.get("ref_no", "")) + fill
             + label("วันที่") + value(spec.get("date", "")) + fill,
             tabs=[("left", TEXT_W // 2), ("left", TEXT_W)]),
        para(label("เรื่อง") + value(spec["subject"]) + fill, tabs=[("left", TEXT_W)]),
        para(run("เรียน   " + spec["to"]), before=120),
    ]


MARKERS = {
    "bullet": lambda i: "•",
    "number": lambda i: f"{i}.".translate(THAI_DIGITS),
    "paren": lambda i: f"({i})".translate(THAI_DIGITS),
    "dash": lambda i: "-",
}


def list_block(b, level=0):
    out = []
    left = INDENT + 454 * (level + 1)
    for i, item in enumerate(b["items"], b.get("start", 1)):  # start: นับต่อหลังตารางคั่นกลาง
        if isinstance(item, str):
            item = {"text": item}
        marker = MARKERS[b.get("style", "bullet")](i)
        out.append(para(run(marker) + run(tab=True) + inline(item["text"]),
                        left=left, hanging=454, tabs=[("left", left)], jc="both"))
        if item.get("items"):
            out += list_block({"style": item.get("style", "dash"), "items": item["items"]}, level + 1)
    return out


def table(b):
    rows = b["rows"]
    ind = INDENT + 454 if b.get("indent") else 0  # indent: เยื้องให้ตรงข้อความของข้อ ๑. ๒.
    total = TEXT_W - ind
    weights = b.get("widths") or [1] * len(rows[0])
    widths = [round(total * w / sum(weights)) for w in weights]
    align = b.get("align") or [None] * len(widths)
    border = "".join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                     for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    xml = (f'<w:tbl><w:tblPr><w:tblW w:w="{total}" w:type="dxa"/><w:tblInd w:w="{ind}" w:type="dxa"/>'
           f'<w:tblBorders>{border}</w:tblBorders>'
           '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="40" w:type="dxa"/>'
           '<w:left w:w="100" w:type="dxa"/><w:bottom w:w="40" w:type="dxa"/>'
           '<w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>'
           + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>")
    for r, row in enumerate(rows):
        head = r == 0 and b.get("header", True)
        xml += "<w:tr>" + ("<w:trPr><w:tblHeader/></w:trPr>" if head else "")
        for c, cell in enumerate(row):
            shd = '<w:shd w:val="clear" w:color="auto" w:fill="E7E6E6"/>' if head else ""
            xml += (f'<w:tc><w:tcPr><w:tcW w:w="{widths[c]}" w:type="dxa"/>{shd}</w:tcPr>'
                    f"{para(inline(str(cell), bold=head), jc=align[c])}</w:tc>")
        xml += "</w:tr>"
    return xml + "</w:tbl>"


def blocks(items):
    out = []
    for b in items:
        if isinstance(b, str):
            b = {"type": "para", "text": b}
        kind = b.get("type", "para")
        if kind == "para":
            out.append(para(inline(b["text"]), jc="both", before=60,
                            first=INDENT if b.get("indent", True) else None))
        elif kind == "heading":
            out.append(para(inline(b["text"], bold=True), keep_next=True, before=240, after=60))
        elif kind == "list":
            out += list_block(b)
        elif kind == "table":
            out.append(table(b))
        elif kind == "code":
            lines = b["text"].split("\n")
            for i, line in enumerate(lines):
                out.append(para(run(line.replace(" ", " "), size=24, font=CODE_FONT),
                                left=284, right=284, shade="F2F2F2", keep_next=i < len(lines) - 1))
        elif kind == "image":
            out.append(para(image_run(BASE / b["path"], b.get("width_cm", 3)), before=120))
            if b.get("caption"):
                out.append(para(inline(b["caption"], size=28)))
        else:
            sys.exit(f"ไม่รู้จัก block type: {kind}")
    return out


def lines_of(v):
    return [v] if isinstance(v, str) else list(v)


def signer(s):
    lines = [s["name"]] + lines_of(s.get("position", []))
    out = [para(keep_next=True) for _ in range(3)]  # ที่ว่างสำหรับลายเซ็น — keepNext กันบล็อกแตกข้ามหน้า
    for i, line in enumerate(lines):
        out.append(para(run(line), jc="center", left=INDENT, keep_next=i < len(lines) - 1))
    return out


def approval(a):
    out = [para(run(a["title"], bold=True), before=360, keep_next=True)]
    for opt in a.get("options", ["อนุมัติ", "อื่น ๆ " + "." * 110]):
        out.append(para(run(f"(     )  {opt}"), left=567, before=60, keep_next=True))
    sign = ["ลงชื่อ " + "." * 51, a["name"]] + lines_of(a.get("position", [])) + ["วันที่ " + "." * 51]
    for i, line in enumerate(sign):
        out.append(para(run(line), jc="center", left=TEXT_W // 2, before=480 if i == 0 else 40,
                        keep_next=i < len(sign) - 1))
    return out


def sect(first, default, title_pg):
    return (f'<w:sectPr><w:headerReference w:type="default" r:id="{default}"/>'
            f'<w:headerReference w:type="first" r:id="{first}"/>'
            '<w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="850" w:right="1134" w:bottom="1134" w:left="1701" '
            'w:header="709" w:footer="0" w:gutter="0"/>'
            + ("<w:titlePg/>" if title_pg else "") + "</w:sectPr>")


def page_header():
    field = ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
             '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
             '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
             + run("2") + '<w:r><w:fldChar w:fldCharType="end"/></w:r>')
    return f"<w:hdr {NS}>{para(run('- ') + field + run(' -'), jc='center')}</w:hdr>"


def package(body_xml, title):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    head = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    ct = "application/vnd.openxmlformats-officedocument.wordprocessingml"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    doc_rels = [("rIdStyles", "styles", "styles.xml"), ("rIdSettings", "settings", "settings.xml"),
                (HDR_PAGE, "header", "header1.xml"), (HDR_EMPTY, "header", "header2.xml")]
    doc_rels += [(rid, "image", f"media/{rid}.png") for rid, _ in MEDIA]
    return {
        "[Content_Types].xml": head + (
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Default Extension="png" ContentType="image/png"/>'
            f'<Override PartName="/word/document.xml" ContentType="{ct}.document.main+xml"/>'
            f'<Override PartName="/word/styles.xml" ContentType="{ct}.styles+xml"/>'
            f'<Override PartName="/word/settings.xml" ContentType="{ct}.settings+xml"/>'
            f'<Override PartName="/word/header1.xml" ContentType="{ct}.header+xml"/>'
            f'<Override PartName="/word/header2.xml" ContentType="{ct}.header+xml"/>'
            '<Override PartName="/docProps/core.xml" '
            'ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>'),
        "_rels/.rels": head + (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rId1" Type="{rel}/officeDocument" Target="word/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/'
            'metadata/core-properties" Target="docProps/core.xml"/></Relationships>'),
        "word/_rels/document.xml.rels": head + (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(f'<Relationship Id="{i}" Type="{rel}/{t}" Target="{p}"/>' for i, t, p in doc_rels)
            + "</Relationships>"),
        "word/document.xml": head + f"<w:document {NS}><w:body>{body_xml}</w:body></w:document>",
        "word/styles.xml": head + (
            '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:docDefaults><w:rPrDefault><w:rPr>"
            f'<w:rFonts w:ascii="{BODY_FONT}" w:hAnsi="{BODY_FONT}" w:eastAsia="{BODY_FONT}" w:cs="{BODY_FONT}"/>'
            '<w:sz w:val="32"/><w:szCs w:val="32"/><w:lang w:val="th-TH" w:eastAsia="th-TH" w:bidi="th-TH"/>'
            "</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr>"
            '<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:pPrDefault>'
            '</w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
            '<w:name w:val="Normal"/><w:qFormat/></w:style></w:styles>'),
        "word/settings.xml": head + (
            '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:defaultTabStop w:val="720"/><w:compat><w:compatSetting w:name="compatibilityMode" '
            'w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat></w:settings>'),
        "word/header1.xml": head + page_header(),
        "word/header2.xml": head + f"<w:hdr {NS}><w:p/></w:hdr>",
        "docProps/core.xml": head + (
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/'
            'core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" '
            'xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f"<dc:title>{escape(title)}</dc:title><dc:language>th-TH</dc:language>"
            f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
            f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>'),
        **{f"word/media/{rid}.png": data for rid, data in MEDIA},
    }


def main():
    global BASE
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    spec_path = Path(sys.argv[1])
    BASE = spec_path.resolve().parent
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = Path(sys.argv[2] if len(sys.argv) > 2 else spec["output"])

    letter = header_block(spec) + blocks(spec.get("body", []))
    if spec.get("signer"):
        letter += signer(spec["signer"])
    letter += blocks(spec.get("after_signature", []))  # เช่น QR / ช่องทางติดต่อ ใต้ลายเซ็น
    if spec.get("approval"):
        letter += approval(spec["approval"])
    sections = [(letter, sect(HDR_EMPTY, HDR_PAGE, True))]  # เลขหน้า "- ๒ -" เริ่มหน้า 2
    for att in spec.get("attachments", []):
        title = [para(inline(t, bold=True)) for t in lines_of(att.get("title", []))]
        sections.append((title + blocks(att.get("body", [])), sect(HDR_EMPTY, HDR_EMPTY, False)))

    body = ""
    for i, (paras, s) in enumerate(sections):
        body += "".join(paras)
        body += para(sect=s) if i < len(sections) - 1 else s

    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in package(body, spec["subject"]).items():
            z.writestr(name, data)
    print(out)


if __name__ == "__main__":
    main()
