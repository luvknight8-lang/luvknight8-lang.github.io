#!/usr/bin/env python3
"""PaperPetalStudio free page generator.
Usage: make_free_pages.py OUTDIR START END
Makes mandala pages START..END (1-based, deterministic per number) as A4 PDFs
plus small JPG thumbnails, and (once) the 2027 habit tracker.
"""
import math, os, random, subprocess, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

W, H = A4
BRAND = "PaperPetalStudio"


def petal(c, r0, r1, w):
    L = r1 - r0
    p = c.beginPath()
    p.moveTo(r0, 0)
    p.curveTo(r0 + L * .3, w, r0 + L * .8, w * .9, r1, 0)
    p.curveTo(r0 + L * .8, -w * .9, r0 + L * .3, -w, r0, 0)
    c.drawPath(p, stroke=1, fill=0)


def spin(c, n, fn, offset=0.0):
    for i in range(n):
        c.saveState()
        c.rotate(360.0 / n * i + offset)
        fn()
        c.restoreState()


def layer(c, kind, n, r0, r1):
    mid = (r0 + r1) / 2
    th = r1 - r0
    arc = 2 * math.pi * mid / n
    if kind == "petals":
        w = min(arc * .55, th * .7)
        spin(c, n, lambda: (petal(c, r0, r1, w), petal(c, r0 + th * .3, r1 - th * .15, w * .45)))
    elif kind == "petals_off":
        w = min(arc * .55, th * .7)
        spin(c, n, lambda: petal(c, r0, r1, w), 180.0 / n)
        spin(c, n, lambda: c.circle(r0 + th * .35, 0, th * .06, stroke=1, fill=1), 0)
    elif kind == "circles":
        rr = min(arc * .42, th * .42)
        spin(c, n, lambda: (c.circle(mid, 0, rr, stroke=1, fill=0), c.circle(mid, 0, rr * .35, stroke=1, fill=1)))
    elif kind == "scallop":
        rr = mid * math.sin(math.pi / n)
        spin(c, n, lambda: c.circle(mid, 0, rr, stroke=1, fill=0))
    elif kind == "triangles":
        def tri():
            p = c.beginPath()
            p.moveTo(r0, -arc * .38); p.lineTo(r1, 0); p.lineTo(r0, arc * .38); p.close()
            c.drawPath(p, stroke=1, fill=0)
            p = c.beginPath()
            p.moveTo(r0 + th * .3, -arc * .15); p.lineTo(r0 + th * .7, 0); p.lineTo(r0 + th * .3, arc * .15); p.close()
            c.drawPath(p, stroke=1, fill=0)
        spin(c, n, tri)
    elif kind == "diamonds":
        def dia():
            p = c.beginPath()
            p.moveTo(r0, 0); p.lineTo(mid, th * .5); p.lineTo(r1, 0); p.lineTo(mid, -th * .5); p.close()
            c.drawPath(p, stroke=1, fill=0)
            c.circle(mid, 0, th * .08, stroke=1, fill=1)
        spin(c, n, dia)
    elif kind == "dots":
        spin(c, n * 2, lambda: c.circle(mid, 0, max(th * .12, 0.8 * mm), stroke=0, fill=1))
    elif kind == "rays":
        def ray():
            c.line(r0, 0, r1, 0)
        spin(c, n * 2, ray)
        spin(c, n * 2, lambda: c.circle(r1, 0, th * .07, stroke=1, fill=1))
    elif kind == "teardrops":
        def td():
            p = c.beginPath()
            p.moveTo(r0, 0)
            p.curveTo(r0 + th * .2, th * .45, mid + th * .1, th * .4, r1, 0)
            p.curveTo(mid + th * .1, -th * .4, r0 + th * .2, -th * .45, r0, 0)
            c.drawPath(p, stroke=1, fill=0)
            c.circle(mid, 0, th * .1, stroke=1, fill=0)
        spin(c, n, td)


KINDS = ["petals", "petals_off", "circles", "petals", "triangles", "diamonds", "dots", "rays", "teardrops"]


def mandala_page(path, num):
    rnd = random.Random(1000 + num * 7919)
    n = rnd.choice([8, 10, 12, 12, 16])
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle(f"Free Mandala Coloring Page No. {num} - {BRAND}")
    c.setAuthor(BRAND)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(1.5)
    c.setLineJoin(1); c.setLineCap(1)
    c.saveState()
    c.translate(W / 2, H / 2 + 6 * mm)
    rmax = 92 * mm
    # center flower
    c.setLineWidth(1.5)
    c.circle(0, 0, 5 * mm, stroke=1, fill=1)
    r = 7 * mm
    last = None
    while r < rmax - 8 * mm:
        th = rnd.uniform(8, 14) * mm
        r1 = min(r + th, rmax)
        kind = rnd.choice([k for k in KINDS if k != last])
        last = kind
        nn = n * rnd.choice([1, 1, 2]) if r > 30 * mm else n
        layer(c, kind, nn, r, r1)
        c.circle(0, 0, r1 + 0.8 * mm, stroke=1, fill=0)
        r = r1 + 1.6 * mm
    # outer border
    c.setLineWidth(2.4)
    c.circle(0, 0, rmax + 2 * mm, stroke=1, fill=0)
    c.setLineWidth(1.2)
    c.circle(0, 0, rmax + 4.5 * mm, stroke=1, fill=0)
    c.restoreState()
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(.45, .45, .45)
    c.drawCentredString(W / 2, 11 * mm, f"{BRAND}  -  Free Mandala No. {num}  -  For personal use only, please do not resell")
    c.showPage()
    c.save()


def habit_tracker(path):
    c = canvas.Canvas(path, pagesize=(H, W))  # landscape A4
    PW, PH = H, W
    c.setTitle(f"Free 2027 Monthly Habit Tracker - {BRAND}")
    c.setAuthor(BRAND)
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(.2, .2, .25)
    c.drawString(15 * mm, PH - 18 * mm, "Monthly Habit Tracker 2027")
    c.setFont("Helvetica", 10)
    c.drawString(15 * mm, PH - 25 * mm, "Month: ______________________      Goal for this month: ____________________________________________")
    left, top = 15 * mm, PH - 32 * mm
    namew = 48 * mm
    cw = (PW - left - 15 * mm - namew) / 31
    rh = 11.5 * mm
    rows = 12
    c.setStrokeColorRGB(.55, .55, .6)
    c.setLineWidth(.6)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(left + 2 * mm, top - 6 * mm, "HABIT")
    for d in range(31):
        x = left + namew + d * cw
        c.drawCentredString(x + cw / 2, top - 6 * mm, str(d + 1))
    for r_ in range(rows + 1):
        y = top - 9 * mm - r_ * rh
        c.line(left, y, left + namew + 31 * cw, y)
    for d in range(32):
        x = left + namew + d * cw
        c.line(x, top - 9 * mm, x, top - 9 * mm - rows * rh)
    c.line(left, top - 9 * mm, left, top - 9 * mm - rows * rh)
    c.line(left, top - 9 * mm, left + namew + 31 * cw, top - 9 * mm)
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(.45, .45, .45)
    c.drawCentredString(PW / 2, 8 * mm, f"{BRAND}  -  Free printable  -  For personal use only, please do not resell")
    c.showPage()
    c.save()


def thumb(pdf, jpg):
    base = jpg[:-4]
    subprocess.run(["pdftoppm", "-r", "70", "-png", "-singlefile", pdf, base], check=True)
    subprocess.run(["convert", base + ".png", "-quality", "82", jpg], check=True)
    os.remove(base + ".png")


if __name__ == "__main__":
    out, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    os.makedirs(out + "/files", exist_ok=True)
    os.makedirs(out + "/thumbs", exist_ok=True)
    for i in range(a, b + 1):
        p = f"{out}/files/free-mandala-{i:02d}.pdf"
        mandala_page(p, i)
        thumb(p, f"{out}/thumbs/free-mandala-{i:02d}.jpg")
    if a == 1:
        p = f"{out}/files/habit-tracker-2027.pdf"
        habit_tracker(p)
        thumb(p, f"{out}/thumbs/habit-tracker-2027.jpg")
    print("done")
