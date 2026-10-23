#!/usr/bin/env python3
"""Tidy the form fields in a fillable PDF exported by Scribus (export-pdf.sh --fillable runs it).

Scribus can only export form fields with fonts as outlines (embedding crashes it), and then
its fields name no font and draw a white or black box over the page. This rewrites each
field so it is see-through and types in Helvetica, in brown dark:
  text / drop-down  no fill or border; the viewer draws the typed text (NeedAppearances)
  check box         no fill; a ZapfDingbats tick in brown dark when checked
Usage: python3 scripts/fix-form-pdf.py FILE.pdf ...   (rewrites each file in place)
"""
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, BooleanObject, DecodedStreamObject, DictionaryObject, FloatObject,
                           NameObject, NumberObject, TextStringObject)

INK = "0.290 0.165 0.102 rg"  # Autumn brown dark #4A2A1A
SIZE = 10


def font(base):
    return DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                             NameObject("/Subtype"): NameObject("/Type1"),
                             NameObject("/BaseFont"): NameObject(base),
                             **({NameObject("/Encoding"): NameObject("/WinAnsiEncoding")}
                                if base == "/Helvetica" else {})})


def stream(writer, w, h, content, fonts=None):
    s = DecodedStreamObject()
    s.set_data(content.encode())
    s.update({NameObject("/Type"): NameObject("/XObject"), NameObject("/Subtype"): NameObject("/Form"),
              NameObject("/BBox"): ArrayObject([FloatObject(0), FloatObject(0), FloatObject(w), FloatObject(h)])})
    if fonts:
        s[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): fonts})
    return writer._add_object(s)


def fix(path):
    writer = PdfWriter(clone_from=PdfReader(path))
    form = writer._root_object["/AcroForm"]
    helv, zadb = writer._add_object(font("/Helvetica")), writer._add_object(font("/ZapfDingbats"))
    fonts = DictionaryObject({NameObject("/Helv"): helv, NameObject("/ZaDb"): zadb})
    dr = form.get("/DR")
    dr = dr.get_object() if dr else DictionaryObject()
    dr[NameObject("/Font")] = fonts
    form[NameObject("/DR")] = dr
    form[NameObject("/DA")] = TextStringObject(f"/Helv {SIZE} Tf {INK}")
    n = 0
    for page in writer.pages:
        for ref in page.get("/Annots") or []:
            a = ref.get_object()
            ft = a.get("/FT")
            if a.get("/Subtype") != "/Widget" or ft not in ("/Tx", "/Btn", "/Ch"):
                continue
            x0, y0, x1, y1 = map(float, a["/Rect"])
            w, h = x1 - x0, y1 - y0
            mk = DictionaryObject()
            if ft == "/Btn":
                mk[NameObject("/CA")] = TextStringObject("4")  # ZapfDingbats tick
                a[NameObject("/DA")] = TextStringObject(f"/ZaDb 0 Tf {INK}")
                size = min(w, h) * 0.85
                tick = (f"q BT /ZaDb {size:.2f} Tf {INK} {(w - size * 0.846) / 2:.2f} "
                        f"{(h - size * 0.7) / 2:.2f} Td (4) Tj ET Q")
                a[NameObject("/AP")] = DictionaryObject({NameObject("/N"): DictionaryObject({
                    NameObject("/Yes"): stream(writer, w, h, tick, DictionaryObject({NameObject("/ZaDb"): zadb})),
                    NameObject("/Off"): stream(writer, w, h, "")})})
            else:
                a[NameObject("/DA")] = TextStringObject(f"/Helv {SIZE} Tf {INK}")
                a[NameObject("/AP")] = DictionaryObject({NameObject("/N"): stream(writer, w, h, "/Tx BMC EMC")})
            a[NameObject("/MK")] = mk
            a[NameObject("/BS")] = DictionaryObject({NameObject("/W"): NumberObject(0)})
            n += 1
    form[NameObject("/NeedAppearances")] = BooleanObject(True)
    with open(path, "wb") as f:
        writer.write(f)
    return n


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(f"{p}: {fix(p)} fields tidied")
