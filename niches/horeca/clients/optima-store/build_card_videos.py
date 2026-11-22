"""Optima Store Christmas card + videos.
Usage: python3 -I build_card_videos.py <client_dir> <work_dir> <card|still|V1|V2> [t] [which]
Everything (card faces, envelope, handwriting, motion, music) is generated in code so printed
text stays exact. Kling was used only for the text-free cover artwork.
"""
import sys, os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps

CLIENT, WORK, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
AS = lambda n: os.path.join(CLIENT, "assets", n)
OUT = os.path.join(CLIENT, "outputs")
os.makedirs(OUT, exist_ok=True); os.makedirs(WORK, exist_ok=True)

RED, BLUE, DBLUE = (160, 43, 33), (78, 109, 164), (47, 72, 122)
INK, IVORY, GOLD = (27, 36, 66), (251, 246, 236), (232, 190, 110)
CHORUS = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrechorus-mediumitalic.otf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CW, CH_ = 900, 1200          # card face texture size
W, H, FPS = 1080, 1920, 30

def F(path, size): return ImageFont.truetype(path, size)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def E(t, a, b): return smooth((t - a) / (b - a))
def cover_fit(im, w, h):
    sw, sh = im.size
    s = max(w / sw, h / sh); nw, nh = int(sw * s + .5), int(sh * s + .5)
    im = im.resize((nw, nh), Image.LANCZOS)
    l, t = (nw - w) // 2, (nh - h) // 2
    return im.crop((l, t, l + w, t + h))

# ------------------------------------------------------------------ logo badge
LOGO = Image.open(AS("optima-logo_original.png")).convert("RGB")
def badge(d, ring=True):
    im = Image.new("RGBA", (d * 2, d * 2), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse([0, 0, d * 2 - 1, d * 2 - 1], fill=(255, 255, 255, 255))
    if ring: dr.ellipse([8, 8, d * 2 - 9, d * 2 - 9], outline=GOLD + (255,), width=6)
    lg = LOGO.resize((int(d * 1.5), int(d * 1.5)), Image.LANCZOS)
    im.paste(lg, ((d * 2 - lg.width) // 2, (d * 2 - lg.height) // 2))
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).ellipse([0, 0, d * 2 - 1, d * 2 - 1], fill=255)
    im.putalpha(ImageChops.multiply(im.getchannel("A"), m))
    return im.resize((d, d), Image.LANCZOS)

BOSFOR = Image.open(AS("bosfor-anatolya-logo_original.jpg")).convert("RGB")
def badge_b(d, ring=True):
    im = BOSFOR.resize((d * 2, d * 2), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).ellipse([0, 0, d * 2 - 1, d * 2 - 1], fill=255)
    if ring: ImageDraw.Draw(im).ellipse([8, 8, d * 2 - 9, d * 2 - 9], outline=GOLD + (255,), width=6)
    im.putalpha(m)
    return im.resize((d, d), Image.LANCZOS)

def amp_img(size, fill):
    f = F(CHORUS, size); tmp = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((size * 0.4, size * 0.1), "&", font=f, fill=fill + (255,)); return tmp.crop(tmp.getbbox())

def snowflake(draw, cx, cy, r, fill, w=3):
    for k in range(6):
        a = math.pi / 3 * k
        ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        draw.line([cx, cy, ex, ey], fill=fill, width=w)
        for f in (0.55, 0.8):
            bx, by = cx + r * f * math.cos(a), cy + r * f * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.pi / 5
                draw.line([bx, by, bx + r * 0.22 * math.cos(b), by + r * 0.22 * math.sin(b)], fill=fill, width=max(1, w - 1))

def paper_noise(im, amt=5, seed=1):
    rng = np.random.default_rng(seed)
    a = np.asarray(im.convert("RGB"), dtype=np.int16)
    n = rng.normal(0, amt, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype("uint8"))

# ------------------------------------------------------------------ card faces
def make_cover():
    art = cover_fit(Image.open(AS("card-cover-art_Kling-v4_2k.png")).convert("RGB"), CW, CH_)
    d = ImageDraw.Draw(art)
    f1, f2 = F(CHORUS, 196), F(CHORUS, 214)
    for txt, f, y in (("Crăciun", f1, 380), ("Fericit!", f2, 585)):
        w = d.textlength(txt, font=f)
        d.text(((CW - w) / 2, y), txt, font=f, fill=RED)
    d.line([300, 835, 600, 835], fill=GOLD, width=4)
    for x in (270, 630): d.ellipse([x - 6, 829, x + 6, 841], fill=GOLD)
    bd, gap = 190, 110
    x0 = (CW - (2 * bd + gap)) // 2
    b1, b2 = badge(bd), badge_b(bd)
    art.paste(b1, (x0, 885), b1); art.paste(b2, (x0 + bd + gap, 885), b2)
    am = amp_img(86, GOLD); art.paste(am, (CW // 2 - am.width // 2, 885 + bd // 2 - am.height // 2), am)
    return art

def make_inner_left():
    g = Image.new("RGB", (CW, CH_))
    px = np.zeros((CH_, CW, 3), np.float32)
    top, bot = np.array((70, 100, 154)), np.array((40, 62, 110))
    for c in range(3): px[..., c] = np.linspace(top[c], bot[c], CH_)[:, None]
    g = Image.fromarray(px.astype("uint8"))
    d = ImageDraw.Draw(g, "RGBA")
    rng = np.random.default_rng(7)
    for _ in range(26):
        x, y, r = rng.integers(40, CW - 40), rng.integers(40, CH_ - 40), int(rng.integers(14, 44))
        if abs(x - CW / 2) < 230 and abs(y - 560) < 260: continue
        snowflake(d, x, y, r, (255, 255, 255, int(rng.integers(70, 160))), 2)
    b1, b2 = badge(300), badge_b(300)
    g.paste(b1, ((CW - 300) // 2, 215), b1); g.paste(b2, ((CW - 300) // 2, 700), b2)
    am = amp_img(110, (255, 255, 255)); g.paste(am, (CW // 2 - am.width // 2, 618 - am.height // 2), am)
    d.text(((CW - d.textlength("optimastore.ro", font=F(SANS, 34))) / 2, 1035), "optimastore.ro", font=F(SANS, 34), fill=(255, 255, 255, 220))
    return paper_noise(g, 3)

MSG = [("Dragi clienți și parteneri,", 70, 0, 0.0),
       ("vă mulțumim pentru încrederea", 58, 0, 0.5),
       ("pe care ne-ați acordat-o", 58, 0, -0.4),
       ("în acest an.", 58, 0, 0.3),
       ("Vă dorim un Crăciun liniștit,", 58, 0, -0.3),
       ("plin de lumină și bucurie,", 58, 0, 0.4),
       ("și un An Nou cu sănătate", 58, 0, -0.5),
       ("și realizări!", 58, 0, 0.3),
       ("Cu drag,", 62, 0, -0.3),
       ("Optima Store", 76, 120, 0.5),
       ("& Bosfor Anatolya", 76, 170, -0.3)]

def make_right():
    paper = Image.new("RGB", (CW, CH_), IVORY)
    paper = paper_noise(paper, 4, 3)
    d = ImageDraw.Draw(paper, "RGBA")
    d.rectangle([34, 34, CW - 34, CH_ - 34], outline=BLUE + (150,), width=3)
    d.rectangle([46, 46, CW - 46, CH_ - 46], outline=BLUE + (80,), width=1)
    for (x, y) in ((92, 92), (CW - 92, 92), (92, CH_ - 92), (CW - 92, CH_ - 92)):
        snowflake(d, x, y, 28, BLUE + (170,), 2)
    ink = np.zeros((CH_, CW), np.float32); lines = []
    y = 150
    for txt, size, indent, rot in MSG:
        f = F(CHORUS, size)
        tmp = Image.new("L", (CW, size * 2), 0)
        ImageDraw.Draw(tmp).text((0, 0), txt, font=f, fill=255)
        bb = tmp.getbbox(); tmp = tmp.crop(bb)
        tmp = tmp.rotate(rot, resample=Image.BICUBIC, expand=True)
        x = 100 + indent + (6 if rot > 0 else 0)
        ly = y if txt != "Cu drag," else y + 28
        if txt.startswith("Optima"): ly = y + 12
        a = np.asarray(tmp, np.float32) / 255
        ink[ly:ly + a.shape[0], x:x + a.shape[1]] = np.maximum(ink[ly:ly + a.shape[0], x:x + a.shape[1]], a)
        lines.append((x, ly, x + a.shape[1], ly + a.shape[0]))
        y = ly + a.shape[0] + 20 if size < 70 else ly + a.shape[0] + 26
        if txt == "în acest an.": y += 34
    return paper, ink, lines

# ------------------------------------------------------------------ envelope (drawn at 1x = 680x860)
def make_env():
    ew, eh = 680, 860
    back = Image.new("RGB", (ew, eh), (36, 56, 100))
    d = ImageDraw.Draw(back, "RGBA")
    for yy in range(0, 160):
        d.line([0, yy, ew, yy], fill=(0, 0, 0, int(120 * (1 - yy / 160))))
    front = Image.new("RGBA", (ew, eh), (0, 0, 0, 0))
    fb = paper_noise(Image.new("RGB", (ew, eh), BLUE), 3, 5).convert("RGBA")
    mask = Image.new("L", (ew, eh), 0)
    ImageDraw.Draw(mask).polygon([(0, eh), (0, 78), (ew / 2, 22), (ew, 78), (ew, eh)], fill=255)
    fd = ImageDraw.Draw(fb, "RGBA")
    fd.line([0, eh, ew / 2, 470], fill=(255, 255, 255, 60), width=3)
    fd.line([ew, eh, ew / 2, 470], fill=(255, 255, 255, 60), width=3)
    fd.line([0, 78, ew / 2, 22], fill=(255, 255, 255, 140), width=3)
    fd.line([ew, 78, ew / 2, 22], fill=(255, 255, 255, 140), width=3)
    front.paste(fb, (0, 0), mask)
    # flap
    fh = 430
    tri = Image.new("L", (ew, fh), 0); ImageDraw.Draw(tri).polygon([(0, 0), (ew, 0), (ew / 2, fh)], fill=255)
    outer = paper_noise(Image.new("RGB", (ew, fh), (88, 120, 176)), 3, 6).convert("RGBA")
    od = ImageDraw.Draw(outer, "RGBA")
    od.line([0, 0, ew / 2, fh], fill=(255, 255, 255, 130), width=3); od.line([ew, 0, ew / 2, fh], fill=(255, 255, 255, 130), width=3)
    b = badge(150); outer.paste(b, (ew // 2 - 75, 230), b)
    outer.putalpha(tri)
    inner = Image.new("RGB", (ew, fh), (36, 56, 100)); idr = ImageDraw.Draw(inner, "RGBA")
    rng = np.random.default_rng(11)
    for _ in range(18): snowflake(idr, int(rng.integers(60, ew - 60)), int(rng.integers(20, 200)), int(rng.integers(10, 22)), (255, 255, 255, 90), 2)
    inner = inner.convert("RGBA"); inner.putalpha(tri)
    return back.convert("RGBA"), front, outer, inner

def shadow_tex(w, h, blur=26, alpha=120):
    im = Image.new("L", (w + 120, h + 120), 0)
    ImageDraw.Draw(im).rectangle([60, 60, 60 + w, 60 + h], fill=alpha)
    im = im.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.putalpha(im); return out

# ------------------------------------------------------------------ 3D quad drawing
def coeffs(dst, src):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float))

def draw_quad(canvas, tex, pts2, alpha=1.0):
    xs, ys = [p[0] for p in pts2], [p[1] for p in pts2]
    x0, y0, x1, y1 = int(math.floor(min(xs))) - 1, int(math.floor(min(ys))) - 1, int(math.ceil(max(xs))) + 1, int(math.ceil(max(ys))) + 1
    bw, bh = x1 - x0, y1 - y0
    if bw < 2 or bh < 2 or bw > 4000 or bh > 4000: return
    tw, th = tex.size
    try: c = coeffs([(x - x0, y - y0) for x, y in pts2], [(0, 0), (tw, 0), (tw, th), (0, th)])
    except np.linalg.LinAlgError: return
    out = tex.transform((bw, bh), Image.PERSPECTIVE, tuple(c), Image.BILINEAR)
    a = out.getchannel("A")
    if alpha < 1: a = a.point(lambda v: int(v * alpha))
    canvas.paste(out.convert("RGB"), (x0, y0), a)

class Cam:
    def __init__(s, cx=340, cy=300, zoom=1.0): s.cx, s.cy, s.zoom, s.F = cx, cy, zoom, 2600.0
    def p(s, pt):
        x, y, z = pt; k = s.F / (s.F + z)
        return (W / 2 + (x - s.cx) * s.zoom * k, H / 2 + (y - s.cy) * s.zoom * k)

# ------------------------------------------------------------------ background + snow
def make_bg():
    px = np.zeros((H, W, 3), np.float32)
    top, bot = np.array((10, 20, 44)), np.array((24, 42, 80))
    for c in range(3): px[..., c] = np.linspace(top[c], bot[c], H)[:, None]
    base = Image.fromarray(px.astype("uint8"))
    def bokeh(seed):
        rng = np.random.default_rng(seed); lay = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(lay)
        cols = [(255, 200, 120), (255, 160, 90), (200, 70, 60), (120, 160, 255), (255, 230, 180)]
        for _ in range(34):
            x, y, r = int(rng.integers(0, W)), int(rng.integers(0, H)), int(rng.integers(26, 90))
            c = cols[int(rng.integers(0, len(cols)))]; k = rng.uniform(0.25, 0.7)
            d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(v * k) for v in c))
        return lay.filter(ImageFilter.GaussianBlur(16))
    return base, bokeh(1), bokeh(2)
BG0, BK1, BK2 = make_bg()

def bg_frame(t):
    k = 0.5 + 0.5 * math.sin(t * 1.3)
    bk = Image.blend(BK1, BK2, k)
    return ImageChops.add(BG0, bk.point(lambda v: int(v * 0.8)))

_rng = np.random.default_rng(5)
FLAKES = [(_rng.uniform(0, W), _rng.uniform(0, H), _rng.uniform(40, 220), _rng.uniform(10, 40), _rng.uniform(0, 6.28), int(_rng.choice([2, 3, 4, 6, 9]))) for _ in range(150)]
def sprite(r):
    s = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(s)
    d.ellipse([r, r, r * 3, r * 3], fill=(255, 255, 255, 230))
    return s.filter(ImageFilter.GaussianBlur(max(0.6, r * 0.35)))
SPR = {r: sprite(r) for r in (2, 3, 4, 6, 9)}
def snow(canvas, t, density=1.0):
    for i, (x0, y0, v, amp, ph, r) in enumerate(FLAKES):
        if i / len(FLAKES) > density: continue
        x = (x0 + amp * math.sin(t * 0.9 + ph)) % W
        y = (y0 + v * t * (0.6 + r / 12)) % (H + 60) - 30
        s = SPR[r]; canvas.paste(s, (int(x - s.width / 2), int(y - s.height / 2)), s)

# ------------------------------------------------------------------ handwriting reveal
PAPER, INKA, LINES = make_right()
COVER_TEX, INL_TEX = make_cover().convert("RGBA"), make_inner_left().convert("RGBA")
INL_BACK = ImageOps.mirror(INL_TEX)
ENV_BACK, ENV_FRONT, FLAP_OUT, FLAP_IN = make_env()
SH_CARD, SH_ENV = shadow_tex(600, 800), shadow_tex(680, 860)
SLANT = 0.28
_X, _Y = np.meshgrid(np.arange(CW, dtype=np.float32), np.arange(CH_, dtype=np.float32))
LINFO = []
for (x0, y0, x1, y1) in LINES:
    band = INKA[y0:y1, x0:x1]
    cs = band.sum(0); cum = np.cumsum(cs); tot = cum[-1]
    rows = np.arange(y1 - y0)[:, None]
    LINFO.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, tot=tot, cum=cum / tot, band=band, rows=rows, cs=cs))
TOTAL_INK = sum(l["tot"] for l in LINFO)
GAPW = 0.35 * TOTAL_INK / len(LINFO)  # pause (in ink units) between lines
SPAN = TOTAL_INK + GAPW * len(LINFO)

def reveal(p):
    """p in 0..1 -> (alpha mask array, pen (x,y) in panel px or None)"""
    mask = np.zeros((CH_, CW), np.float32); pen = None
    pos = p * SPAN; start = 0.0
    for L in LINFO:
        end = start + L["tot"]
        y0, y1, x0, x1 = L["y0"], L["y1"], L["x0"], L["x1"]
        if pos >= end:
            mask[y0:y1, x0 - 20:x1 + 20] = 1
        elif pos > start:
            f = (pos - start) / L["tot"]
            xr = x0 + int(np.searchsorted(L["cum"], f))
            ymid = (y0 + y1) / 2
            xx = _X[y0:y1, x0 - 20:x1 + 20]; yy = _Y[y0:y1, x0 - 20:x1 + 20]
            mask[y0:y1, x0 - 20:x1 + 20] = np.clip((xr - (xx - SLANT * (yy - ymid))) / 10 + 0.5, 0, 1)
            cols = L["band"][:, max(0, xr - x0 - 8):max(1, xr - x0 + 8)]
            if cols.sum() > 0: cy = y0 + (cols.sum(1) * np.arange(cols.shape[0])).sum() / cols.sum()
            else: cy = ymid
            pen = (xr, cy)
        start = end + GAPW
        if pos < start - GAPW: break
    return mask, pen

def right_tex(p):
    if p <= 0: return PAPER.convert("RGBA"), None
    m, pen = reveal(p)
    a = np.clip(INKA * m, 0, 1)
    img = PAPER.copy()
    img.paste(Image.new("RGB", (CW, CH_), INK), (0, 0), Image.fromarray((a * 255).astype("uint8")))
    return img.convert("RGBA"), pen

# ------------------------------------------------------------------ scene
def draw_pen(canvas, tip, strength=1.0):
    x, y = tip
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    ux, uy = 0.41, -0.91                      # pen axis (up and to the right)
    def pt(k, off=0.0): return (x + ux * k - uy * off, y + uy * k + ux * off)
    d.polygon([pt(0), pt(52, -9), pt(52, 9)], fill=GOLD + (255,))           # nib
    d.polygon([pt(48, -12), pt(70, -14), pt(70, 14), pt(48, 12)], fill=(20, 24, 44, 255))
    d.polygon([pt(70, -14), pt(330, -17), pt(330, 17), pt(70, 14)], fill=(26, 34, 70, 255))  # barrel
    d.polygon([pt(150, -18), pt(166, -18), pt(166, 18), pt(150, 18)], fill=GOLD + (255,))     # band
    d.line([pt(80, -7), pt(320, -9)], fill=(90, 110, 170, 255), width=4)                      # highlight
    d.polygon([pt(330, -17), pt(344, -12), pt(344, 12), pt(330, 17)], fill=GOLD + (255,))
    sh = ov.filter(ImageFilter.GaussianBlur(8)); sh.putalpha(sh.getchannel("A").point(lambda v: int(v * 0.35)))
    canvas.paste(Image.new("RGB", (W, H), (0, 0, 0)), (14, 20), sh)
    canvas.paste(ov.convert("RGB"), (0, 0), ov.getchannel("A"))

def rot_y(pt, cx, ph):
    x, y, z = pt; dx = x - cx
    return (cx + dx * math.cos(ph), y, z - dx * math.sin(ph))

def render_card(t, P):
    c = bg_frame(t); snow(c, t, 1.0); cam = Cam(P["camx"], P["camy"], P["zoom"])
    ey, th_f = P.get("ey", 0.0), P.get("flap", 0.0)
    cy_, cz, th = P["cardy"], P["cardz"], P["cover"]
    yaw, ycx = P.get("yaw", 0.0), 340
    def pr(pt): return cam.p(rot_y(pt, ycx, yaw) if yaw else pt)
    def quad(tex, pts, alpha=1.0): draw_quad(c, tex, [pr(q) for q in pts], alpha)
    show_env = P.get("env", True) and ey < 1250
    if show_env:
        quad(SH_ENV, [(-60 + 14, ey - 60 + 28, 30), (740 + 14, ey - 60 + 28, 30), (740 + 14, ey + 920 + 28, 30), (-60 + 14, ey + 920 + 28, 30)], 0.9)
        quad(ENV_BACK, [(0, ey, 0), (680, ey, 0), (680, ey + 860, 0), (0, ey + 860, 0)])
        if th_f > 90:
            a = math.radians(th_f)
            quad(FLAP_IN, [(0, ey, 0), (680, ey, 0), (680, ey + 430 * math.cos(a) * -1 * -1, 0)] if False else
                 [(0, ey, 0), (680, ey, 0), (680, ey + 430 * math.cos(a), 430 * math.sin(a)), (0, ey + 430 * math.cos(a), 430 * math.sin(a))])
    # card
    x0, z = 40, cz
    quad(SH_CARD, [(x0 - 60 + 16, cy_ - 60 + 30, z + 40), (x0 + 660 + 16, cy_ - 60 + 30, z + 40), (x0 + 660 + 16, cy_ + 860 + 30, z + 40), (x0 - 60 + 16, cy_ + 860 + 30, z + 40)], 0.8)
    rt, pen = right_tex(P.get("write", 0.0))
    quad(rt, [(x0, cy_, z), (x0 + 600, cy_, z), (x0 + 600, cy_ + 800, z), (x0, cy_ + 800, z)])
    a = math.radians(th)
    tex = COVER_TEX if th <= 90 else INL_BACK
    quad(tex, [(x0, cy_, z), (x0 + 600 * math.cos(a), cy_, z - 600 * math.sin(a)), (x0 + 600 * math.cos(a), cy_ + 800, z - 600 * math.sin(a)), (x0, cy_ + 800, z)])
    if show_env:
        quad(ENV_FRONT, [(0, ey, 0), (680, ey, 0), (680, ey + 860, 0), (0, ey + 860, 0)])
        if th_f <= 90 and th_f > 0:
            a2 = math.radians(th_f)
            quad(FLAP_OUT, [(0, ey, 0), (680, ey, 0), (680, ey + 430 * math.cos(a2), -430 * math.sin(a2) * -1), (0, ey + 430 * math.cos(a2), 430 * math.sin(a2))])
        elif th_f <= 0:
            quad(FLAP_OUT, [(0, ey, 0), (680, ey, 0), (680, ey + 430, 0), (0, ey + 430, 0)])
    if pen is not None and P.get("pen", True) and th >= 179:
        tx, ty = pen
        draw_pen(c, pr((x0 + tx * 2 / 3, cy_ + ty * 2 / 3, z)))
    return c

# ------------------------------------------------------------------ VIDEO 1: envelope -> card -> handwriting
V1_END = 15.2
V1_DUR = 17.8
WRITE_A, WRITE_B = 7.4, 12.9
def params_v1(t):
    P = dict(camx=340, camy=200, zoom=1.15, ey=0.0, flap=0.0, cardy=60, cardz=0, cover=0.0, write=0.0)
    P["flap"] = 180 * E(t, 0.9, 2.2)
    P["cardy"] = lerp(60, -500, E(t, 2.3, 3.9))
    p2 = E(t, 4.0, 5.2)
    P["cardy"] = lerp(P["cardy"], -150, p2)
    P["ey"] = lerp(0, 1500, E(t, 4.0, 5.3))
    P["cardz"] = lerp(0, -300, p2)
    P["camx"], P["camy"], P["zoom"] = lerp(340, 340, p2), lerp(200, 250, p2), lerp(1.15, 1.25, p2)
    # open
    po = E(t, 5.5, 7.0)
    P["cover"] = 180 * po
    P["camx"] = lerp(P["camx"], 40, po); P["zoom"] = lerp(P["zoom"], 0.74, po)
    # zoom to right page for writing
    pw = E(t, 7.0, 7.8)
    P["camx"] = lerp(P["camx"], 340, pw); P["zoom"] = lerp(P["zoom"], 1.33, pw)
    P["write"] = clamp((t - WRITE_A) / (WRITE_B - WRITE_A))
    # pull back
    pb = E(t, 13.2, 14.4)
    P["camx"] = lerp(P["camx"], 40, pb); P["zoom"] = lerp(P["zoom"], 0.74, pb)
    P["pen"] = t < 13.2
    return P

def end_card(t, tl):
    c = bg_frame(t + 3)
    s = E(tl, 0, 0.7); bd, gap = 340, 150
    x0 = (W - (2 * bd + gap)) // 2
    for bb, xx in ((badge(bd), x0), (badge_b(bd), x0 + bd + gap)):
        c.paste(bb, (xx, 520), bb.getchannel("A").point(lambda v: int(v * s)))
    am = amp_img(150, GOLD); am.putalpha(am.getchannel("A").point(lambda v: int(v * s)))
    c.paste(am, (W // 2 - am.width // 2, 520 + bd // 2 - am.height // 2), am)
    d = ImageDraw.Draw(c)
    def ctext(txt, f, y, fill, a):
        im = Image.new("RGBA", (W, f.size * 2), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
        w = dd.textlength(txt, font=f); dd.text(((W - w) / 2, f.size * 0.2), txt, font=f, fill=fill + (int(255 * a),))
        c.paste(im.convert("RGB"), (0, y), im.getchannel("A"))
    ctext("Crăciun fericit!", F(CHORUS, 150), 1010, IVORY, E(tl, 0.5, 1.2))
    ctext("Vă mulțumim pentru încredere.", F(CHORUS, 64), 1230, GOLD, E(tl, 0.9, 1.6))
    ctext("Optima Store & Bosfor Anatolya", F(SANS, 38), 1420, (220, 228, 245), E(tl, 1.3, 1.9))
    ctext("optimastore.ro", F(SANS, 38), 1490, (220, 228, 245), E(tl, 1.5, 2.1))
    snow(c, t, 0.7)
    return c

def frame_v1(t):
    if t < V1_END:
        c = render_card(t, params_v1(t)); snow(c, t + 7, 0.10)
        if t < 0.8: c = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), c, E(t, 0, 0.8))
        if t > V1_END - 0.5: c = Image.blend(c, end_card(t, 0), E(t, V1_END - 0.5, V1_END))
        return c
    c = end_card(t, t - V1_END)
    if t > V1_DUR - 0.4: c = Image.blend(c, Image.new("RGB", (W, H), (0, 0, 0)), (t - (V1_DUR - 0.4)) / 0.4)
    return c

# ------------------------------------------------------------------ VIDEO 2: light-writing -> card flips in -> opens
V2_DUR = 17.0
def glow_text():
    lines = [("Crăciun", 250, 660), ("Fericit!", 270, 960)]
    A = Image.new("L", (W, H), 0); d = ImageDraw.Draw(A); info = []
    for txt, size, y in lines:
        f = F(CHORUS, size); w = d.textlength(txt, font=f); x = int((W - w) / 2)
        tmp = Image.new("L", (W, H), 0); ImageDraw.Draw(tmp).text((x, y), txt, font=f, fill=255)
        A = ImageChops.lighter(A, tmp); bb = tmp.getbbox(); info.append(bb)
    return np.asarray(A, np.float32) / 255, info
GA, GINFO = glow_text()
GGLOW = np.asarray(Image.fromarray((GA * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(22)), np.float32) / 255
GGLOW2 = np.asarray(Image.fromarray((GA * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(7)), np.float32) / 255
GL = []
for (x0, y0, x1, y1) in GINFO:
    band = GA[y0:y1, x0:x1]; cs = band.sum(0); cum = np.cumsum(cs); GL.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, band=band, tot=cs.sum(), cum=cum / cum[-1]))
GTOT = sum(l["tot"] for l in GL) + 0.3 * sum(l["tot"] for l in GL) / 2
_GX, _GY = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
def greveal(p):
    mask = np.zeros((H, W), np.float32); pen = None; pos = p * GTOT; start = 0.0
    for L in GL:
        end = start + L["tot"]; y0, y1, x0, x1 = L["y0"], L["y1"], L["x0"] - 30, L["x1"] + 30
        if pos >= end: mask[y0:y1, x0:x1] = 1
        elif pos > start:
            f = (pos - start) / L["tot"]; xr = L["x0"] + int(np.searchsorted(L["cum"], f)); ym = (y0 + y1) / 2
            mask[y0:y1, x0:x1] = np.clip((xr - (_GX[y0:y1, x0:x1] - SLANT * (_GY[y0:y1, x0:x1] - ym))) / 12 + 0.5, 0, 1)
            cols = L["band"][:, max(0, xr - L["x0"] - 8):max(1, xr - L["x0"] + 8)]
            cy = y0 + ((cols.sum(1) * np.arange(cols.shape[0])).sum() / cols.sum() if cols.sum() > 0 else (y1 - y0) / 2)
            pen = (xr, cy)
        start = end + 0.3 * L["tot"] / 1.0 * 0.5
        if pos < start - 0.15 * L["tot"]: break
    return mask, pen

_sp = np.zeros((161, 161), np.float32)
_yy, _xx = np.mgrid[-80:81, -80:81]
_sp = np.exp(-(_xx ** 2 + _yy ** 2) / (2 * 14.0 ** 2)) + 0.7 * np.exp(-(_xx ** 2 + _yy ** 2) / (2 * 4.0 ** 2))

V2_WRITE_A, V2_WRITE_B = 1.3, 6.0
V2_FLIP, V2_OPEN, V2_RIGHT, V2_RW_A, V2_RW_B, V2_PULL, V2_END = 7.4, 9.3, 10.3, 10.9, 13.4, 14.2, 15.0
def frame_v2(t):
    if t >= V2_END:
        c = end_card(t, t - V2_END)
        if t > V2_DUR - 0.4: c = Image.blend(c, Image.new("RGB", (W, H), (0, 0, 0)), (t - (V2_DUR - 0.4)) / 0.4)
        return c
    # glowing light-writing phase (also fades out as the card flips in)
    base = bg_frame(t)
    fade = 1 - E(t, 6.4, 7.6)
    if fade > 0.01 and t >= 0.5:
        p = clamp((t - V2_WRITE_A) / (V2_WRITE_B - V2_WRITE_A))
        m, pen = greveal(p)
        arr = np.asarray(base, np.float32)
        glow = (GGLOW * 0.9 + GGLOW2 * 0.5) * m * fade
        shimmer = 0.85 + 0.15 * math.sin(t * 6)
        arr += glow[..., None] * np.array(GOLD, np.float32) * 0.9 * shimmer
        core = (GA * m * fade)[..., None]
        arr = arr * (1 - core) + core * np.array((255, 244, 214), np.float32)
        if pen is not None and p < 1:
            px, py = int(pen[0]), int(pen[1])
            x0, y0 = max(0, px - 80), max(0, py - 80); x1, y1 = min(W, px + 81), min(H, py + 81)
            sp = _sp[y0 - (py - 80):y1 - (py - 80), x0 - (px - 80):x1 - (px - 80)]
            arr[y0:y1, x0:x1] += sp[..., None] * np.array((255, 235, 190), np.float32) * 1.4
        base = Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))
    if t < V2_FLIP - 0.9:
        c = base
        if t < 0.5: c = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), base, E(t, 0, 0.5))
        snow(c, t, 1.0)
        return c
    # card phase
    P = dict(camx=340, camy=400, zoom=1.2, ey=0, env=False, flap=0, cardy=0, cardz=0, cover=0.0, write=0.0, pen=False)
    P["yaw"] = 0.0
    pf = E(t, V2_FLIP - 0.9, V2_FLIP + 0.9)
    P["yaw"] = math.radians(lerp(88, 0, pf))
    P["cardz"] = lerp(500, -250, pf)
    P["zoom"] = lerp(1.0, 1.22, pf)
    po = E(t, V2_OPEN, V2_OPEN + 1.4)
    P["cover"] = 180 * po
    P["camx"] = lerp(340, 40, po); P["zoom"] = lerp(P["zoom"], 0.74, po); P["cardz"] = lerp(P["cardz"], -300, po)
    pr = E(t, V2_RIGHT, V2_RIGHT + 0.8)
    P["camx"] = lerp(P["camx"], 340, pr); P["zoom"] = lerp(P["zoom"], 1.33, pr)
    P["write"] = clamp((t - V2_RW_A) / (V2_RW_B - V2_RW_A)); P["pen"] = t < V2_PULL
    pb = E(t, V2_PULL, V2_PULL + 0.8)
    P["camx"] = lerp(P["camx"], 40, pb); P["zoom"] = lerp(P["zoom"], 0.74, pb)
    c = render_card(t, P)
    # blend from glow text scene into card phase
    snow(c, t + 7, 0.10)
    if t < V2_FLIP:
        c = Image.blend(base, c, E(t, V2_FLIP - 0.9, V2_FLIP - 0.2))
    if t > V2_END - 0.5: c = Image.blend(c, end_card(t, 0), E(t, V2_END - 0.5, V2_END))
    return c

# ------------------------------------------------------------------ audio
SR = 44100
def tone(f, dur, amp=0.2, decay=3.0, bright=0.4):
    n = int(dur * SR); t = np.arange(n) / SR
    env = np.exp(-t * decay) * (1 - np.exp(-t * 90))
    return amp * env * (np.sin(2 * np.pi * f * t) + bright * np.sin(4 * np.pi * f * t) * np.exp(-t * 4) + 0.12 * np.sin(6 * np.pi * f * t) * np.exp(-t * 6))
def place(buf, snd, at):
    i = int(at * SR)
    if i >= len(buf) or i < 0: return
    j = min(len(buf), i + len(snd)); buf[i:j] += snd[: j - i]
def noise_band(dur, lo, hi, seed=1):
    n = int(dur * SR); rng = np.random.default_rng(seed)
    sp = np.fft.rfft(rng.standard_normal(n)); fr = np.fft.rfftfreq(n, 1 / SR); sp[(fr < lo) | (fr > hi)] = 0
    x = np.fft.irfft(sp, n); return x / (np.abs(x).max() + 1e-9)
def echo(x, delay=0.34, fb=0.35, n=4):
    out = x.copy()
    for k in range(1, n + 1):
        d = int(delay * SR * k)
        if d < len(x): out[d:] += x[: len(x) - d] * (fb ** k)
    return out
def finish(x, fin=0.6, fout=1.6):
    x = x / (np.abs(x).max() + 1e-9) * 0.85
    x[: int(fin * SR)] *= np.linspace(0, 1, int(fin * SR)); x[-int(fout * SR):] *= np.linspace(1, 0, int(fout * SR)); return x
def write_wav(path, x):
    st = np.stack([x, np.roll(x, 40)], 1); pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

CHORDS = [(130.81, [261.63, 329.63, 392.0]), (110.0, [220.0, 261.63, 329.63]), (87.31, [174.61, 261.63, 349.23]), (98.0, [196.0, 246.94, 293.66])]
def music(dur, bpm=66, amp=1.0):
    buf = np.zeros(int(dur * SR)); beat = 60 / bpm; bar = 4 * beat
    for b in range(int(dur // bar) + 1):
        root, tri = CHORDS[b % 4]; t0 = b * bar
        place(buf, tone(root, bar + 0.8, 0.2 * amp, 0.9, 0.2), t0)
        for k in range(8):
            f = (tri + [tri[1] * 2])[[0, 1, 2, 3, 2, 1, 2, 1][k]] * 2
            place(buf, tone(f, 1.6, 0.11 * amp, 2.8, 0.5), t0 + k * beat / 2)
    return buf
def audio_v1(path):
    buf = music(V1_DUR) * 0.8
    place(buf, noise_band(1.3, 1500, 8000, 2) * np.hanning(int(1.3 * SR)) * 0.10, 0.9)      # flap
    place(buf, noise_band(1.6, 300, 3000, 3) * np.hanning(int(1.6 * SR)) * 0.11, 2.3)        # card slides
    place(buf, noise_band(1.3, 200, 2500, 4) * np.hanning(int(1.3 * SR)) * 0.10, 4.0)
    place(buf, noise_band(1.5, 1200, 7000, 5) * np.hanning(int(1.5 * SR)) * 0.10, 5.5)        # opens
    n = int((WRITE_B - WRITE_A) * SR); rng = np.random.default_rng(9)
    pen = noise_band(WRITE_B - WRITE_A, 2500, 7500, 6) * (0.5 + 0.5 * np.abs(np.sin(np.arange(n) / SR * 13 + np.cumsum(rng.normal(0, 0.003, n))))) * 0.045
    place(buf, pen, WRITE_A)
    for k, f in enumerate([880.0, 1318.5, 1760.0]): place(buf, tone(f, 2.4, 0.15, 1.6, 0.1), V1_END + 0.3 + 0.12 * k)
    write_wav(path, finish(echo(buf), 0.6, 1.8))
def audio_v2(path):
    buf = music(V2_DUR, 60, 0.9) * 0.8
    for k in range(14): place(buf, tone(1318.5 * (1 + 0.5 * (k % 3)), 1.2, 0.05, 3, 0.1), V2_WRITE_A + k * 0.33)
    place(buf, noise_band(0.9, 600, 4000, 7) * np.hanning(int(0.9 * SR)) * 0.2, V2_FLIP - 0.8)
    place(buf, noise_band(1.5, 1200, 7000, 8) * np.hanning(int(1.5 * SR)) * 0.1, V2_OPEN)
    n = int((V2_RW_B - V2_RW_A) * SR); rng = np.random.default_rng(10)
    pen = noise_band(V2_RW_B - V2_RW_A, 2500, 7500, 11) * (0.5 + 0.5 * np.abs(np.sin(np.arange(n) / SR * 13 + np.cumsum(rng.normal(0, 0.003, n))))) * 0.04
    place(buf, pen, V2_RW_A)
    for k, f in enumerate([880.0, 1318.5, 1760.0]): place(buf, tone(f, 2.4, 0.15, 1.6, 0.1), V2_END + 0.3 + 0.12 * k)
    write_wav(path, finish(echo(buf), 0.6, 1.8))

# ------------------------------------------------------------------ render helpers
def render(fn, dur, out):
    n = int(round(dur * FPS))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for k in range(n): p.stdin.write(fn(k / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait()
def mux(v, a, out): subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)

if __name__ == "__main__":
    if MODE == "card":
        full = Image.new("RGB", (CW * 3 + 80, CH_ + 80), (230, 226, 218))
        rt = PAPER.copy(); a = Image.fromarray((INKA * 255).astype("uint8")); rt.paste(Image.new("RGB", (CW, CH_), INK), (0, 0), a)
        full.paste(COVER_TEX.convert("RGB"), (20, 40)); full.paste(INL_TEX.convert("RGB"), (CW + 40, 40)); full.paste(rt, (2 * CW + 60, 40))
        full.save(os.path.join(OUT, "2026-11-22_optima-christmas-card_preview.png"))
        COVER_TEX.convert("RGB").save(os.path.join(OUT, "2026-11-22_optima-christmas-card_front.png"))
        spread = Image.new("RGB", (CW * 2, CH_)); spread.paste(INL_TEX.convert("RGB"), (0, 0)); spread.paste(rt, (CW, 0))
        spread.save(os.path.join(OUT, "2026-11-22_optima-christmas-card_inside.png"))
        print("card faces saved")
    elif MODE == "still":
        t = float(sys.argv[4]); which = sys.argv[5]
        (frame_v1 if which == "V1" else frame_v2)(t).save(os.path.join(WORK, f"still_{which}_{t}.png"))
    elif MODE == "V1":
        render(frame_v1, V1_DUR, os.path.join(WORK, "V1_video.mp4")); audio_v1(os.path.join(WORK, "V1.wav"))
        mux(os.path.join(WORK, "V1_video.mp4"), os.path.join(WORK, "V1.wav"), os.path.join(OUT, "2026-11-22_optima-christmas-card_video1_envelope_9x16.mp4"))
    elif MODE == "V2":
        render(frame_v2, V2_DUR, os.path.join(WORK, "V2_video.mp4")); audio_v2(os.path.join(WORK, "V2.wav"))
        mux(os.path.join(WORK, "V2_video.mp4"), os.path.join(WORK, "V2.wav"), os.path.join(OUT, "2026-11-22_optima-christmas-card_video2_surprise_9x16.mp4"))
