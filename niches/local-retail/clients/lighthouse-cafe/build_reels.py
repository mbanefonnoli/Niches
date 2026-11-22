import sys, math, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

CLIENT = sys.argv[1]          # client folder
WORK = sys.argv[2]            # scratch folder for intermediates
OUT = os.path.join(CLIENT, "outputs")
FPS, W, H = 30, 1080, 1920
BG = (0x2A, 0x17, 0x10)
BLUSH = (0xF4, 0xD6, 0xD0)
WHITE = (255, 255, 255)

A = lambda n: os.path.join(CLIENT, "assets", n)
SRC = {
    "isus": A("2026-11-22_girl-isus-viata-front_AI.png"),
    "christ": A("2026-11-22_boy-christ-is-enough-back_AI.png"),
    "nu": A("2026-11-22_boy-nu-te-teme-front_AI_v2.png"),
    "faith": A("2026-11-22_girl-faith-over-fear-back_AI.png"),
    "god": A("2026-11-22_girl-but-god-hoodie_AI-test.png"),
}
ORDER = ["isus", "christ", "nu", "faith", "god"]
LABEL = {"isus": "ISUS mi-a salvat viața", "christ": "Christ is enough",
         "nu": "Nu te teme", "faith": "Faith over fear", "god": "but God."}
# focus point (fraction of source) used for print close-ups
FOCUS = {"isus": (0.5, 0.64), "christ": (0.5, 0.68), "nu": (0.5, 0.75),
         "faith": (0.48, 0.70), "god": (0.5, 0.62)}
IMG = {k: Image.open(v).convert("RGB") for k, v in SRC.items()}
LOGO = Image.open(os.path.join(CLIENT, "brand", "lighthouse-logo_transparent.png")).convert("RGBA")

FD = "/usr/share/fonts/truetype/dejavu/"
def font(name, size): return ImageFont.truetype(FD + name, size)
SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def back_out(x, s=1.4):
    x = clamp(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2

def cover(img, w, h, zoom=1.0, focus=(0.5, 0.5)):
    w, h = max(1, int(round(w))), max(1, int(round(h)))
    sw, sh = img.size
    if sw / sh > w / h: ch = sh; cw = ch * w / h
    else: cw = sw; ch = cw * h / w
    cw /= zoom; ch /= zoom
    cx = clamp(focus[0] * sw, cw / 2, sw - cw / 2)
    cy = clamp(focus[1] * sh, ch / 2, sh - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return img.resize((w, h), Image.BICUBIC, box=box)

def new(): return Image.new("RGB", (W, H), BG)

def text_img(txt, f, fill):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), txt, font=f)
    im = Image.new("RGBA", (r - l + 8, b - t + 16), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - l, 8 - t), txt, font=f, fill=fill + (255,))
    return im

_cache = {}
def put_text(canvas, txt, f_key, y, fill=BLUSH, alpha=1.0, dy=0, shadow=False, x=None):
    key = (txt, f_key, fill)
    if key not in _cache:
        kind, size = f_key
        f = {"serif": SERIF_B, "sans": SANS, "sansb": SANS_B}[kind](size)
        _cache[key] = text_img(txt, f, fill)
    im = _cache[key]
    if alpha <= 0: return
    layer = im.copy()
    layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    px = int((W - im.width) / 2) if x is None else x
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sh.putalpha(im.getchannel("A").point(lambda v: int(v * alpha * 0.6)))
        canvas.paste(Image.new("RGB", im.size, (0, 0, 0)), (px + 3, int(y + dy) + 3), sh)
    canvas.paste(layer.convert("RGB"), (px, int(y + dy)), layer)

def put_logo(canvas, size, cx, cy, alpha=1.0):
    lg = LOGO.resize((size, int(size * LOGO.height / LOGO.width)), Image.LANCZOS)
    if alpha < 1: lg.putalpha(lg.getchannel("A").point(lambda v: int(v * alpha)))
    canvas.paste(lg, (int(cx - lg.width / 2), int(cy - lg.height / 2)), lg)

def disclosure(c, alpha=0.8):
    put_text(c, "Persoane generate cu AI", ("sans", 26), 1862, fill=WHITE, alpha=alpha, shadow=True)

def blend(a, b, t): return Image.blend(a, b, clamp(t))

# ---------------- grid geometry ----------------
TW, TH, GAP = 340, 453, 14
GX0 = (W - (3 * TW + 2 * GAP)) // 2
GY0 = (H - (2 * TH + GAP)) // 2 + 20
def slot(i):
    c, r = i % 3, i // 3
    return GX0 + c * (TW + GAP), GY0 + r * (TH + GAP), TW, TH

def tile_logo(canvas, alpha):
    x, y, w, h = slot(5)
    ImageDraw.Draw(canvas).rectangle([x, y, x + w, y + h], fill=(0x1B, 0x0F, 0x0A))
    put_logo(canvas, 250, x + w / 2, y + h / 2 - 20, alpha)

# =================== VIDEO A  (21.5 s) ===================
A_INTRO, A_SC, A_COL, A_END = 2.0, 2.3, 4.0, 4.0
A_DUR = A_INTRO + 5 * A_SC + A_COL + A_END
def dots(c, idx):
    d = ImageDraw.Draw(c)
    for i in range(5):
        x = W // 2 + (i - 2) * 44
        d.ellipse([x - 10, 86, x + 10, 106], fill=BLUSH if i == idx else None, outline=BLUSH, width=3)

def scene_img(i, local, fade_in=0.0):
    k = ORDER[i]
    z = 1.0 + 0.07 * clamp(local / A_SC)
    im = cover(IMG[k], W, H, z)
    return im

def frame_A(t):
    if t < A_INTRO:
        c = new(); a = smooth(t / 0.6)
        put_logo(c, 460, W / 2, 820, a)
        put_text(c, "Colecția", ("serif", 92), 1150, alpha=smooth((t - 0.4) / 0.6))
        put_text(c, "de iarnă", ("serif", 92), 1260, alpha=smooth((t - 0.6) / 0.6))
        return c
    ts = t - A_INTRO
    if ts < 5 * A_SC:
        i = min(4, int(ts // A_SC)); local = ts - i * A_SC
        im = scene_img(i, local)
        if local > A_SC - 0.25 and i < 4:
            im = blend(im, scene_img(i + 1, 0), (local - (A_SC - 0.25)) / 0.25)
        if i == 0 and local < 0.3:
            im = blend(new(), im, local / 0.3)
        dots(im, i)
        disclosure(im)
        return im
    tc = ts - 5 * A_SC
    if tc < A_COL:
        c = new()
        starts = {4: 0.0, 3: 0.25, 2: 0.5, 1: 0.75, 0: 1.0}
        for i in range(5):  # draw bottom -> top
            k = ORDER[i]; p = smooth((tc - starts[i]) / 0.9)
            gx, gy, gw, gh = slot(i)
            x, y, w, h = lerp(0, gx, p), lerp(0, gy, p), lerp(W, gw, p), lerp(H, gh, p)
            z = lerp(1.07, 1.0, p)
            c.paste(cover(IMG[k], w, h, z), (int(round(x)), int(round(y))))
        la = smooth((tc - 1.9) / 0.5)
        if la > 0: tile_logo(c, la)
        put_text(c, "Colecția de iarnă", ("serif", 70), 250, alpha=la)
        put_text(c, "Hanorace cu mesaj", ("sans", 40), 350, alpha=la)
        put_text(c, "Fiecare hanorac poartă un mesaj", ("sans", 36), 1560, alpha=la)
        disclosure(c)
        return c
    te = tc - A_COL
    c = new()
    s = smooth(te / 0.6)
    put_logo(c, int(lerp(400, 480, s)), W / 2, 760, s)
    put_text(c, "Găsești hanoracele în cafenea,", ("serif", 56), 1090, alpha=smooth((te - 0.5) / 0.5))
    put_text(c, "în Constanța.", ("serif", 56), 1170, alpha=smooth((te - 0.6) / 0.5))
    put_text(c, "Treci pe la noi", ("sansb", 52), 1330, alpha=smooth((te - 1.1) / 0.5))
    put_text(c, "Persoane generate cu AI", ("sans", 26), 1862, fill=WHITE, alpha=0.7)
    if te > A_END - 0.4:
        c = blend(c, new(), (te - (A_END - 0.4)) / 0.4)
    return c

# =================== VIDEO C  (16 s, creative cut) ===================
C_HOOK, C_SC, C_SHUF, C_GRID, C_END = 1.6, 1.6, 2.0, 2.0, 2.4
C_DUR = C_HOOK + 5 * C_SC + C_SHUF + C_GRID + C_END

def flash(c, local, dur=0.12):
    if local < dur: return blend(c, Image.new("RGB", (W, H), WHITE), 0.75 * (1 - local / dur))
    return c

def frame_C(t):
    if t < C_HOOK:
        c = Image.new("RGB", (W, H), (0x14, 0x0B, 0x07))
        put_logo(c, 200, W / 2, 330, smooth(t / 0.4))
        put_text(c, "Unele mesaje", ("serif", 108), 880, alpha=smooth((t - 0.1) / 0.35), dy=40 * (1 - smooth((t - 0.1) / 0.35)))
        put_text(c, "se poartă.", ("serif", 108), 1020, fill=BLUSH, alpha=smooth((t - 0.8) / 0.35), dy=40 * (1 - smooth((t - 0.8) / 0.35)))
        return c
    ts = t - C_HOOK
    if ts < 5 * C_SC:
        i = min(4, int(ts // C_SC)); local = ts - i * C_SC; k = ORDER[i]
        z = 1.0 + 0.22 * smooth(local / C_SC)
        c = cover(IMG[k], W, H, z, FOCUS[k])
        # dark gradient strip for caption
        strip = Image.new("RGB", (W, 360), (0, 0, 0))
        mask = Image.linear_gradient("L").resize((W, 360))
        c.paste(strip, (0, H - 360), mask)
        put_text(c, "%02d" % (i + 1), ("serif", 110), 90, alpha=1.0, x=70, shadow=True)
        put_text(c, LABEL[k], ("sansb", 50), 1690, alpha=smooth(local / 0.3), shadow=True, x=70)
        disclosure(c)
        return flash(c, local)
    tt = ts - 5 * C_SC
    if tt < C_SHUF:
        i = int(tt // 0.4) % 5; local = tt - int(tt // 0.4) * 0.4; k = ORDER[i]
        c = cover(IMG[k], W, H, 1.0 + 0.1 * (local / 0.4), FOCUS[k])
        disclosure(c)
        return flash(c, local, 0.08)
    tg = tt - C_SHUF
    if tg < C_GRID:
        c = new()
        for i in range(5):
            p = back_out((tg - i * 0.12) / 0.35)
            if p <= 0: continue
            gx, gy, gw, gh = slot(i)
            s = clamp(p, 0, 1.15)
            w, h = gw * s, gh * s
            c.paste(cover(IMG[ORDER[i]], w, h), (int(gx + (gw - w) / 2), int(gy + (gh - h) / 2)))
        la = smooth((tg - 0.7) / 0.3)
        if la > 0: tile_logo(c, la)
        put_text(c, "Alege-ți mesajul.", ("serif", 78), 250, alpha=smooth((tg - 0.5) / 0.4))
        disclosure(c)
        return c
    te = tg - C_GRID
    c = new(); s = smooth(te / 0.5)
    put_logo(c, 440, W / 2, 780, s)
    put_text(c, "Treci pe la noi", ("serif", 84), 1130, alpha=smooth((te - 0.4) / 0.4))
    put_text(c, "Lighthouse Cafe · Constanța", ("sans", 42), 1270, alpha=smooth((te - 0.7) / 0.4))
    put_text(c, "Persoane generate cu AI", ("sans", 26), 1862, fill=WHITE, alpha=0.7)
    if te > C_END - 0.3: c = blend(c, new(), (te - (C_END - 0.3)) / 0.3)
    return c

# =================== audio ===================
SR = 44100
def tone(f, dur, amp=0.2, decay=3.0, bright=0.4):
    n = int(dur * SR); t = np.arange(n) / SR
    env = np.exp(-t * decay) * (1 - np.exp(-t * 90))
    w = np.sin(2 * np.pi * f * t) + bright * np.sin(4 * np.pi * f * t) * np.exp(-t * 4) + 0.12 * np.sin(6 * np.pi * f * t) * np.exp(-t * 6)
    return amp * env * w
def place(buf, snd, at):
    i = int(at * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(snd)); buf[i:j] += snd[: j - i]
def echo(x, delay=0.32, fb=0.35, n=4):
    out = x.copy()
    for k in range(1, n + 1):
        d = int(delay * SR * k)
        if d < len(x): out[d:] += x[: len(x) - d] * (fb ** k)
    return out
def noise_band(dur, lo, hi, seed=1):
    n = int(dur * SR); rng = np.random.default_rng(seed)
    sp = np.fft.rfft(rng.standard_normal(n)); fr = np.fft.rfftfreq(n, 1 / SR)
    sp[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(sp, n)
def finish(x, fin=0.5, fout=1.5):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.85
    n = len(x); x[: int(fin * SR)] *= np.linspace(0, 1, int(fin * SR)); x[-int(fout * SR):] *= np.linspace(1, 0, int(fout * SR))
    return x
def write_wav(path, x):
    import wave
    st = np.stack([x, np.roll(x, 40)], 1)   # tiny stereo offset
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

CH = [(110.0, [220.0, 261.63, 329.63]), (87.31, [174.61, 261.63, 349.23]),
      (130.81, [261.63, 329.63, 392.0]), (98.0, [196.0, 246.94, 293.66])]
def audio_A(path):
    dur = A_DUR; buf = np.zeros(int(dur * SR))
    beat = 60 / 72.0; step = beat / 2
    bar = 4 * beat; nb = int(dur // bar) + 1
    for b in range(nb):
        root, tri = CH[b % 4]; t0 = b * bar
        place(buf, tone(root, bar + 0.8, 0.22, 0.9, 0.2), t0)
        for k in range(8):
            f = (tri + [tri[1] * 2])[[0, 1, 2, 3, 2, 1, 2, 1][k]]
            place(buf, tone(f * 2 if k % 2 else f * 2, 1.4, 0.13, 3.2, 0.5), t0 + k * step)
        pad = sum(np.sin(2 * np.pi * f * np.arange(int((bar + 0.6) * SR)) / SR) for f in tri) * 0.025
        pad *= np.minimum(1, np.arange(len(pad)) / (0.5 * SR)) * np.linspace(1, 0.3, len(pad))
        place(buf, pad, t0)
    # whoosh as tiles come together, chime on the end card
    wh = noise_band(1.2, 500, 3500) * np.hanning(int(1.2 * SR)) * 0.5
    place(buf, wh, A_INTRO + 5 * A_SC + 0.0)
    for k, f in enumerate([880.0, 1318.5, 1760.0]):
        place(buf, tone(f, 2.4, 0.16, 1.6, 0.1), A_INTRO + 5 * A_SC + A_COL + 0.35 + 0.12 * k)
    write_wav(path, finish(echo(buf), 0.6, 1.8))

def audio_C(path):
    dur = C_DUR; buf = np.zeros(int(dur * SR)); beat = 0.4
    nb = int(dur / beat) + 1
    for i in range(nb):
        t0 = i * beat
        if i % 2 == 0:  # kick every 0.8 s
            n = int(0.35 * SR); t = np.arange(n) / SR
            ph = 2 * np.pi * np.cumsum(45 + 90 * np.exp(-t * 28)) / SR
            place(buf, 0.7 * np.sin(ph) * np.exp(-t * 9), t0)
        h = noise_band(0.08, 6000, 16000, i + 3) * np.exp(-np.arange(int(0.08 * SR)) / SR * 55) * 0.08
        place(buf, h, t0 + beat / 2 if False else t0 + 0.2)
        root, tri = CH[(i // 8) % 4]
        if i % 4 == 0: place(buf, tone(root, 1.5, 0.26, 2.2, 0.3), t0)
        f = tri[[0, 1, 2, 1][i % 4]] * 2
        place(buf, tone(f, 0.5, 0.12, 6.0, 0.6), t0)
    if C_HOOK > 0: place(buf, noise_band(0.5, 400, 2500) * np.hanning(int(0.5 * SR)) * 0.4, C_HOOK - 0.5)
    place(buf, noise_band(0.8, 500, 3500) * np.hanning(int(0.8 * SR)) * 0.45, C_HOOK + 5 * C_SC + C_SHUF - 0.1)
    for k, f in enumerate([880.0, 1318.5]):
        place(buf, tone(f, 2.0, 0.16, 1.8, 0.1), C_HOOK + 5 * C_SC + C_SHUF + C_GRID + 0.2 + 0.1 * k)
    write_wav(path, finish(echo(buf, 0.2, 0.25, 3), 0.1, 1.2))

# =================== render ===================
def render(fn, dur, out_path):
    n = int(round(dur * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", "-movflags", "+faststart", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(n):
        p.stdin.write(fn(k / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait()

def mux(video, audio, out):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", audio, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)

if __name__ == "__main__":
    which = sys.argv[3]
    os.makedirs(OUT, exist_ok=True)
    if which == "A":
        render(frame_A, A_DUR, os.path.join(WORK, "A_video.mp4"))
        audio_A(os.path.join(WORK, "A.wav"))
        mux(os.path.join(WORK, "A_video.mp4"), os.path.join(WORK, "A.wav"), os.path.join(OUT, "2026-11-22_hoodie-collection_reel_A_sound_9x16.mp4"))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(WORK, "A_video.mp4"), "-an", "-c:v", "copy",
                        os.path.join(OUT, "2026-11-22_hoodie-collection_reel_B_silent_9x16.mp4")], check=True)
    elif which == "C":
        render(frame_C, C_DUR, os.path.join(WORK, "C_video.mp4"))
        audio_C(os.path.join(WORK, "C.wav"))
        mux(os.path.join(WORK, "C_video.mp4"), os.path.join(WORK, "C.wav"), os.path.join(OUT, "2026-11-22_hoodie-collection_reel_C_creative_9x16.mp4"))
    elif which == "still":
        # quick preview stills
        t = float(sys.argv[4]); fn = frame_A if sys.argv[5] == "A" else frame_C
        fn(t).save(os.path.join(WORK, f"still_{sys.argv[5]}_{t}.png"))
