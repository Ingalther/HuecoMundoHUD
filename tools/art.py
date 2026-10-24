"""Procedural artwork for the Hueco Mundo HUD.

Everything is generated from code + locally installed Windows fonts, so the HUD ships no third-party art.
Run build.py (not this file directly) to regenerate materials.
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

FONTS = r'C:\Windows\Fonts'

# ---------------------------------------------------------------- palette
BONE = (232, 232, 226)
ASH = (150, 152, 150)
INK = (8, 9, 10)
EMERALD = (46, 214, 140)
EMERALD_DEEP = (20, 120, 78)


def font(name, size, index=0):
    for cand in name.split('|'):
        p = os.path.join(FONTS, cand)
        if os.path.exists(p):
            return ImageFont.truetype(p, size, index=index)
    raise FileNotFoundError(name)


SERIF = 'GARA.TTF|constan.ttf|georgia.ttf'
SERIF_B = 'GARABD.TTF|constanb.ttf|georgiab.ttf'
KANJI = 'simsun.ttc|YuGothM.ttc|msgothic.ttc'
KANA = 'YuGothL.ttc|YuGothR.ttc|msgothic.ttc'
SANS = 'bahnschrift.ttf|segoeui.ttf'


def rng(seed):
    return np.random.default_rng(seed)


def noise1d(n, seed, octaves=5, base=24):
    r = rng(seed)
    out = np.zeros(n)
    amp = 1.0
    step = base
    for _ in range(octaves):
        k = max(2, n // step + 2)
        pts = r.uniform(-1, 1, k)
        xs = np.linspace(0, k - 1, n)
        out += amp * np.interp(xs, np.arange(k), pts)
        amp *= 0.5
        step = max(1, step // 2)
    return out / 1.9


def smooth1d(n, seed, octaves=4, base=200, sigma=None):
    v = noise1d(n, seed, octaves, base)
    sigma = sigma or max(2, base // 6)
    k = np.exp(-0.5 * (np.arange(-3 * sigma, 3 * sigma + 1) / sigma) ** 2)
    k /= k.sum()
    return np.convolve(np.pad(v, 3 * sigma, mode='edge'), k, mode='valid')


def noise2d(w, h, seed, scale=64, octaves=4):
    r = rng(seed)
    out = np.zeros((h, w), np.float32)
    amp = 1.0
    s = scale
    for _ in range(octaves):
        gw, gh = max(2, w // s + 2), max(2, h // s + 2)
        g = Image.fromarray((r.uniform(0, 255, (gh, gw))).astype(np.uint8))
        g = np.asarray(g.resize((w, h), Image.BICUBIC), np.float32) / 255 - 0.5
        out += amp * g
        amp *= 0.5
        s = max(1, s // 2)
    return out


def rgba(size, color=(0, 0, 0), a=0):
    return Image.new('RGBA', size, color + (a,))


def solid_with_alpha(color, alpha_arr):
    h, w = alpha_arr.shape
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., :3] = color
    arr[..., 3] = np.clip(alpha_arr * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def over(dst, src, xy=(0, 0)):
    dst.alpha_composite(src, xy)
    return dst


def text_img(txt, fnt, color=BONE, tracking=0, stroke=0, pad=8):
    """Render text with letter spacing on a transparent canvas, trimmed."""
    d = ImageDraw.Draw(Image.new('L', (1, 1)))
    widths = [d.textlength(c, font=fnt) for c in txt]
    asc, desc = fnt.getmetrics()
    w = int(sum(widths) + tracking * (len(txt) - 1) + pad * 2 + stroke * 2)
    h = asc + desc + pad * 2
    im = rgba((max(1, w), h))
    dr = ImageDraw.Draw(im)
    x = pad
    for c, cw in zip(txt, widths):
        dr.text((x, pad), c, font=fnt, fill=color + (255,), stroke_width=stroke, stroke_fill=color + (255,))
        x += cw + tracking
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def vertical_text(txt, fnt, color=BONE, gap=4):
    chars = [text_img(c, fnt, color, pad=2) for c in txt]
    w = max(c.width for c in chars)
    h = sum(c.height for c in chars) + gap * (len(chars) - 1)
    im = rgba((w, h))
    y = 0
    for c in chars:
        im.alpha_composite(c, ((w - c.width) // 2, y))
        y += c.height + gap
    return im


def roughen(im, seed, amount=1.6, erode=0.12):
    """Make crisp glyphs look inked: displace edges with noise and break them slightly."""
    a = np.asarray(im, np.float32)
    h, w = a.shape[:2]
    n1 = noise2d(w, h, seed, scale=6, octaves=2)
    n2 = noise2d(w, h, seed + 1, scale=6, octaves=2)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    sx = np.clip(xs + n1 * amount * 4, 0, w - 1).astype(int)
    sy = np.clip(ys + n2 * amount * 4, 0, h - 1).astype(int)
    out = a[sy, sx].copy()
    grit = noise2d(w, h, seed + 2, scale=3, octaves=2)
    out[..., 3] *= np.clip(1.0 - erode + grit * 2.2, 0, 1)
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def fit(im, size, anchor='center'):
    """Paste im into a transparent canvas of given size (power of two)."""
    c = rgba(size)
    x = (size[0] - im.width) // 2 if anchor in ('center', 'top', 'bottom') else (0 if 'left' in anchor else size[0] - im.width)
    y = (size[1] - im.height) // 2 if anchor in ('center', 'left', 'right') else (0 if 'top' in anchor else size[1] - im.height)
    c.alpha_composite(im, (max(0, x), max(0, y)))
    return c


# ---------------------------------------------------------------- motifs
def crescent(r, color=BONE, glow=True, phase=0.62, tilt=-28, glow_color=(200, 214, 208)):
    """The moon: a crescent, or the full disc with phase=None (the holiday menus)."""
    s = int(r * 2 + r * 5)
    ss = 4
    big = Image.new('L', (s * ss, s * ss), 0)
    d = ImageDraw.Draw(big)
    c = s * ss / 2
    R = r * ss
    d.ellipse((c - R, c - R, c + R, c + R), fill=255)
    if phase is not None:
        ang = math.radians(tilt)
        off = R * phase
        ox, oy = off * math.cos(ang), off * math.sin(ang)
        d.ellipse((c - R * 0.96 + ox, c - R * 0.96 + oy, c + R * 0.96 + ox, c + R * 0.96 + oy), fill=0)
    m = big.resize((s, s), Image.LANCZOS)
    # faint surface texture
    tex = noise2d(s, s, 7, scale=max(4, r // 3), octaves=3)
    shade = np.clip(0.9 + tex * 0.35, 0.6, 1.0)
    arr = np.zeros((s, s, 4), np.float32)
    arr[..., :3] = np.array(color, np.float32) * shade[..., None]
    arr[..., 3] = np.asarray(m, np.float32)
    moon = Image.fromarray(arr.clip(0, 255).astype(np.uint8), 'RGBA')
    if not glow:
        return moon
    g = m.filter(ImageFilter.GaussianBlur(r * 0.35))
    g2 = m.filter(ImageFilter.GaussianBlur(r * 1.1))
    ga = np.asarray(g, np.float32) / 255 * 0.55 + np.asarray(g2, np.float32) / 255 * 0.35
    out = solid_with_alpha(glow_color, ga)
    out.alpha_composite(moon)
    return out


def bat(w, color=INK):
    """Murcielago: a small bat silhouette, wings spread, scalloped trailing edge (the Halloween menus)."""
    ss = 4
    W, H = w * ss, max(2, int(w * 0.5)) * ss
    half = [(0.00, -0.30), (0.06, -0.62), (0.10, -0.30), (0.25, -0.38), (0.55, -0.62), (1.00, -0.55),
            (0.82, -0.05), (0.70, 0.12), (0.58, -0.02), (0.45, 0.22), (0.30, 0.05), (0.16, 0.30), (0.06, 0.55),
            (0.00, 0.60)]
    pts = [(W / 2 + x * W / 2, H / 2 + y * H / 2) for x, y in half]
    pts += [(W / 2 - x * W / 2, H / 2 + y * H / 2) for x, y in reversed(half)]
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).polygon(pts, fill=255)
    return solid_with_alpha(color, np.asarray(im.resize((W // ss, H // ss), Image.LANCZOS), np.float32) / 255)


def hollow_mask(h, color=BONE):
    """A small bone Hollow mask: rounded brow, pointed jaw, slanted eye holes, a row of teeth (Halloween menus)."""
    ss = 4
    W, H = int(h * 0.78) * ss, h * ss
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    d.polygon([(W * 0.5, 0), (W * 0.85, H * 0.08), (W * 0.98, H * 0.35), (W * 0.86, H * 0.62), (W * 0.66, H * 0.84),
               (W * 0.5, H), (W * 0.34, H * 0.84), (W * 0.14, H * 0.62), (W * 0.02, H * 0.35), (W * 0.15, H * 0.08)],
              fill=255)
    d.polygon([(W * 0.20, H * 0.38), (W * 0.42, H * 0.44), (W * 0.40, H * 0.53), (W * 0.22, H * 0.48)], fill=0)
    d.polygon([(W * 0.80, H * 0.38), (W * 0.58, H * 0.44), (W * 0.60, H * 0.53), (W * 0.78, H * 0.48)], fill=0)
    lw = max(1, int(W * 0.014))
    d.line((W * 0.30, H * 0.70, W * 0.70, H * 0.70), fill=0, width=lw)
    for i in range(7):
        x = W * (0.32 + i * 0.06)
        d.line((x, H * 0.66, x, H * 0.80), fill=0, width=lw)
    m = np.asarray(im.resize((W // ss, H // ss), Image.LANCZOS), np.float32) / 255
    # lit from the moon (upper right): the left cheek falls into shadow
    xs = np.linspace(0, 1, m.shape[1])[None, :]
    shade = np.clip(0.62 + xs * 0.45, 0, 1)[..., None]
    rgb = np.array(color, np.float32)[None, None] * shade * np.ones_like(m)[..., None]
    return Image.fromarray(np.concatenate([rgb, m[..., None] * 255], -1).clip(0, 255).astype(np.uint8), 'RGBA')


def santa_hat(w):
    """A small manga Santa hat (the Smissmas menu title): red cone drooping to the right, bone brim and pom-pom."""
    ss = 4
    W, H = w * ss, int(w * 0.92) * ss
    cone = [(W * 0.10, H * 0.78), (W * 0.22, H * 0.40), (W * 0.40, H * 0.14), (W * 0.62, H * 0.08),
            (W * 0.84, H * 0.22), (W * 0.93, H * 0.42), (W * 0.84, H * 0.40), (W * 0.74, H * 0.30),
            (W * 0.66, H * 0.40), (W * 0.90, H * 0.78)]
    layers = []
    for pts, col, kind in ((cone, (184, 38, 44), 'poly'), (None, (240, 240, 234), 'brim'), (None, (240, 240, 234), 'pom')):
        m = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(m)
        if kind == 'poly':
            d.polygon(pts, fill=255)
        elif kind == 'brim':
            d.rounded_rectangle((W * 0.02, H * 0.70, W * 0.98, H * 0.98), radius=H * 0.12, fill=255)
        else:
            d.ellipse((W * 0.83, H * 0.36, W * 1.0, H * 0.53), fill=255)
        layers.append((np.asarray(m.resize((W // ss, H // ss), Image.LANCZOS), np.float32) / 255, col))
    w2, h2 = W // ss, H // ss
    out = np.zeros((h2, w2, 4), np.float32)
    sil = np.zeros((h2, w2), np.float32)
    lit = np.clip(1.05 - np.linspace(0, 1, w2)[None, :] * 0.35, 0, 1)  # lit from the upper left
    for m, col in layers:
        rgb = np.array(col, np.float32)[None, None] * lit[..., None]
        out[..., :3] = out[..., :3] * (1 - m[..., None]) + rgb * m[..., None]
        out[..., 3] = np.maximum(out[..., 3], m)
        sil = np.maximum(sil, m)
    # thin ink outline around the whole hat, like the rest of the manga art
    edge = np.asarray(Image.fromarray((sil * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
    ring = np.clip(edge - sil, 0, 1)
    out[..., :3] = out[..., :3] * (1 - ring[..., None]) + np.array(INK, np.float32) * ring[..., None]
    out[..., 3] = np.maximum(out[..., 3], ring) * 255
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), 'RGBA')


def star_glint(r, color=(255, 222, 150)):
    """A four-point star with a soft glow (the Smissmas menu: on top of Las Noches)."""
    s = r * 6
    ss = 4
    im = Image.new('L', (s * ss, s * ss), 0)
    c, R, t = s * ss / 2, r * ss * 2.4, r * ss * 0.32
    ImageDraw.Draw(im).polygon([(c, c - R), (c + t, c - t), (c + R, c), (c + t, c + t), (c, c + R), (c - t, c + t),
                                (c - R, c), (c - t, c - t)], fill=255)
    m = im.resize((s, s), Image.LANCZOS)
    glow = np.asarray(m.filter(ImageFilter.GaussianBlur(r * 1.2)), np.float32) / 255 * 0.8
    out = solid_with_alpha(color, np.clip(glow, 0, 1))
    out.alpha_composite(solid_with_alpha((255, 248, 230), np.asarray(m, np.float32) / 255))
    return out


def tear_streak(h, w, color=EMERALD, seed=0):
    """Ulquiorra's tear mark: thin at the eye, widening slightly, fading into a drip."""
    ss = 4
    W, H = w * ss, h * ss
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    wob = noise1d(H, seed, octaves=3, base=H // 6)
    pts_l, pts_r = [], []
    for y in range(0, H, ss):
        t = y / H
        width = W * (0.18 + 0.30 * math.sin(math.pi * min(1, t * 1.15)) ** 0.8) * (1 - 0.55 * max(0, t - 0.8) / 0.2)
        cx = W / 2 + wob[y] * W * 0.06
        pts_l.append((cx - width / 2, y))
        pts_r.append((cx + width / 2, y))
    d.polygon(pts_l + pts_r[::-1], fill=255)
    m = np.asarray(im.resize((w, h), Image.LANCZOS), np.float32) / 255
    fade = np.clip(np.linspace(1.2, 0.0, h), 0, 1)[:, None] ** 0.7
    core = solid_with_alpha(color, m * fade)
    glow = solid_with_alpha(color, np.asarray(Image.fromarray((m * fade * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(1, w / 5))), np.float32) / 255 * 0.6)
    glow.alpha_composite(core)
    return glow


def brush_stroke(w, h, seed, color=INK, alpha=0.9, dry_end='right', taper=0.18, slant=0.0):
    """Horizontal ink brush stroke with ragged edges and dry-brush bristle gaps."""
    r = rng(seed)
    xs = np.arange(w)
    top = h * 0.14 + noise1d(w, seed, 5, 40) * h * 0.10
    bot = h * 0.86 + noise1d(w, seed + 9, 5, 40) * h * 0.10
    ys = np.arange(h)[:, None]
    t = xs / (w - 1)
    # taper both ends (thin & broken at the dry end)
    if dry_end == 'right':
        env = np.clip(t / taper, 0, 1) ** 0.5 * np.clip((1 - t) / (taper * 1.8), 0, 1) ** 0.35
    else:
        env = np.clip((1 - t) / taper, 0, 1) ** 0.5 * np.clip(t / (taper * 1.8), 0, 1) ** 0.35
    mid = (top + bot) / 2 + slant * (t - 0.5) * h
    half = (bot - top) / 2 * (0.25 + 0.75 * env)
    body = np.clip((half[None, :] - np.abs(ys - mid[None, :])) / 1.2, 0, 1)
    # bristle streaks: horizontal lines of varying density
    bristle = np.array([noise1d(w, seed + 100 + i, 3, 60) for i in range(8)])
    rows = (np.interp(np.linspace(0, 7, h), np.arange(8), np.arange(8))).astype(int)
    lanes = r.uniform(0, 1, h)
    lane_noise = bristle[rows] * 0.6 + lanes[:, None] * 0.8
    dryness = (1 - env) ** 1.5 if True else 0
    gap = np.clip((lane_noise - (1.35 - dryness[None, :] * 1.1)) * 3, 0, 1)
    grain = noise2d(w, h, seed + 3, scale=48, octaves=3)
    a = body * (1 - gap) * np.clip(0.97 + grain * 0.12, 0, 1) * alpha
    return solid_with_alpha(color, a)


def dry_slash(w, h, seed, color=BONE, thickness=0.22, alpha=0.95, angle_up=True):
    """A fast dry-brush slash line (used as white highlight under plates)."""
    im = brush_stroke(w, h, seed, color=color, alpha=alpha, dry_end='right', taper=0.08)
    a = np.asarray(im, np.float32)
    # squash vertically into a thin band
    th = max(2, int(h * thickness))
    band = Image.fromarray(a.astype(np.uint8), 'RGBA').resize((w, th), Image.LANCZOS)
    out = rgba((w, h))
    out.alpha_composite(band, (0, (h - th) // 2))
    return out


def bat_wing(w, h, seed=5, flip=False, fill=(14, 15, 17), edge=BONE):
    """Murcielago wing silhouette with scalloped membrane."""
    ss = 3
    W, H = w * ss, h * ss
    shoulder = (0.04 * W, 0.97 * H)
    wrist = (0.50 * W, 0.12 * H)
    tips = [(0.99 * W, 0.20 * H), (0.93 * W, 0.52 * H), (0.74 * W, 0.80 * H), (0.47 * W, 0.97 * H), (0.22 * W, 1.0 * H)]

    def bez(p0, p1, p2, n=40):
        return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                 (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]

    arm = bez(shoulder, (0.18 * W, 0.18 * H), wrist)
    lead = bez(wrist, (0.78 * W, 0.02 * H), tips[0])
    poly = arm + lead
    prev = tips[0]
    for tp in tips[1:] + [shoulder]:
        mx, my = (prev[0] + tp[0]) / 2, (prev[1] + tp[1]) / 2
        # pull membrane edge toward the wrist to make the scallop
        cx = mx + (wrist[0] - mx) * 0.28
        cy = my + (wrist[1] - my) * 0.28
        poly += bez(prev, (cx, cy), tp)[1:]
        prev = tp
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    d.polygon(poly, fill=255)
    # finger bones (slightly lighter lines)
    bones = Image.new('L', (W, H), 0)
    bd = ImageDraw.Draw(bones)
    for tp in tips:
        bd.line(bez(wrist, ((wrist[0] + tp[0]) / 2 + 0.03 * W, (wrist[1] + tp[1]) / 2 - 0.03 * H), tp), fill=255, width=int(2.2 * ss))
    bd.line(arm + lead, fill=255, width=int(3.2 * ss))
    m = m.resize((w, h), Image.LANCZOS)
    bones = bones.resize((w, h), Image.LANCZOS)
    ma = np.asarray(m, np.float32) / 255
    ba = np.asarray(bones, np.float32) / 255 * ma
    # edge light along the leading edge only (top region)
    edge_m = np.asarray(m.filter(ImageFilter.FIND_EDGES), np.float32) / 255
    yy = np.linspace(1, 0, h)[:, None]
    edge_m = np.clip(edge_m * 1.6, 0, 1) * np.clip(yy * 1.6 - 0.1, 0, 1)
    grain = noise2d(w, h, seed, scale=20, octaves=3)
    fade = np.clip(1.15 - np.linspace(0, 1, w)[None, :] * 0.2 - (1 - yy) * 0.15 + grain * 0.2, 0, 1)
    arr = np.zeros((h, w, 4), np.float32)
    col = np.array(fill, np.float32)
    arr[..., :3] = col + ba[..., None] * 26
    arr[..., 3] = ma * 0.92 * fade * 255
    base = Image.fromarray(arr.clip(0, 255).astype(np.uint8), 'RGBA')
    base.alpha_composite(solid_with_alpha(edge, edge_m * 0.55))
    if flip:
        base = base.transpose(Image.FLIP_LEFT_RIGHT)
    return base


def ulq_eye(size, seed=11):
    """Emblem: ink disc, a single cold eye with an emerald iris and the twin tear marks."""
    S = size
    im = rgba((S, S))
    # ink disc with ragged edge
    ss = 3
    disc = Image.new('L', (S * ss, S * ss), 0)
    d = ImageDraw.Draw(disc)
    n = 360
    rad = noise1d(n, seed, 4, 20)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = S * ss * (0.46 + rad[i] * 0.02)
        pts.append((S * ss / 2 + rr * math.cos(a), S * ss / 2 + rr * math.sin(a)))
    d.polygon(pts, fill=255)
    disc = disc.resize((S, S), Image.LANCZOS)
    da = np.asarray(disc, np.float32) / 255
    grain = noise2d(S, S, seed, scale=S // 10, octaves=3)
    im.alpha_composite(solid_with_alpha((10, 11, 12), da * np.clip(0.93 + grain * 0.2, 0, 1)))
    # thin bone ring
    ring = disc.filter(ImageFilter.FIND_EDGES)
    im.alpha_composite(solid_with_alpha(ASH, np.clip(np.asarray(ring, np.float32) / 255 * 1.4, 0, 1) * 0.55))
    # eye
    E = Image.new('L', (S * ss, S * ss), 0)
    ed = ImageDraw.Draw(E)
    cx, cy = S * ss * 0.5, S * ss * 0.42
    ew, eh = S * ss * 0.30, S * ss * 0.085
    up = [(cx - ew + 2 * ew * t, cy - eh * math.sin(math.pi * t) ** 0.9 - eh * 0.25 * math.sin(math.pi * t) * (t - 0.5)) for t in np.linspace(0, 1, 60)]
    lo = [(cx - ew + 2 * ew * t, cy + eh * 0.75 * math.sin(math.pi * t) ** 1.1) for t in np.linspace(1, 0, 60)]
    ed.polygon(up + lo, fill=255)
    E = E.resize((S, S), Image.LANCZOS)
    im.alpha_composite(solid_with_alpha(BONE, np.asarray(E, np.float32) / 255 * 0.95))
    # iris (emerald) clipped to eye, slit-ish pupil
    ir = Image.new('L', (S * ss, S * ss), 0)
    idr = ImageDraw.Draw(ir)
    R = eh * 1.05
    idr.ellipse((cx - R, cy - R * 1.05, cx + R, cy + R * 0.95), fill=255)
    ir = ImageChops.multiply(ir.resize((S, S), Image.LANCZOS), E)
    ira = np.asarray(ir, np.float32) / 255
    yy, xx = np.mgrid[0:S, 0:S]
    dist = np.hypot(xx - cx / ss, yy - cy / ss) / (R / ss)
    iris_col = np.zeros((S, S, 4), np.float32)
    iris_col[..., :3] = np.array(EMERALD_DEEP) + (np.array(EMERALD) - np.array(EMERALD_DEEP)) * np.clip(1.2 - dist, 0, 1)[..., None]
    iris_col[..., 3] = ira * 255
    im.alpha_composite(Image.fromarray(iris_col.clip(0, 255).astype(np.uint8), 'RGBA'))
    pup = Image.new('L', (S * ss, S * ss), 0)
    ImageDraw.Draw(pup).ellipse((cx - R * 0.22, cy - R * 0.8, cx + R * 0.22, cy + R * 0.8), fill=255)
    pup = ImageChops.multiply(pup.resize((S, S), Image.LANCZOS), E)
    im.alpha_composite(solid_with_alpha((5, 12, 9), np.asarray(pup, np.float32) / 255))
    # upper lid line (heavy ink)
    lid = Image.new('L', (S * ss, S * ss), 0)
    ImageDraw.Draw(lid).line(up, fill=255, width=int(S * ss * 0.018))
    im.alpha_composite(solid_with_alpha((4, 4, 5), np.asarray(lid.resize((S, S), Image.LANCZOS), np.float32) / 255))
    # tear marks: two streaks from under the eye down through the disc edge
    th = int(S * 0.50)
    t = tear_streak(th, max(6, int(S * 0.06)), seed=seed)
    im.alpha_composite(t, (int(S * 0.5 - t.width / 2), int(cy / ss + eh / ss * 0.95)))
    return im


# ---------------------------------------------------------------- background scene
def hueco_mundo_scene(W=1920, H=1080, seed=3, menu_shade=True, variant=None):
    """Hueco Mundo by night. variant (the main menu on TF2's holidays, same landscape): None, the eternal crescent;
    'fullmoon', the moon full; 'halloween', a full moon in a green halo, bats across it, green mist, Hollow masks
    sunk in the sand; 'christmas', snowfall and a star on Las Noches."""
    r = rng(seed)
    rv = rng(seed + 101)  # the variants' own random stream: the shared landscape stays identical
    yy = np.linspace(0, 1, H)[:, None]
    horizon = 0.60
    sky = np.zeros((H, W, 3), np.float32)
    top = np.array((4, 5, 7), np.float32)
    low = np.array((22, 24, 28), np.float32)
    k = np.clip(yy / horizon, 0, 1) ** 2.2
    sky[:] = top + (low - top) * k[..., None]
    img = Image.fromarray(sky.clip(0, 255).astype(np.uint8), 'RGB').convert('RGBA')

    # stars: sparse and dim
    st = np.zeros((H, W), np.float32)
    n = 260
    sx, sy = r.integers(0, W, n), (r.uniform(0, 1, n) ** 1.6 * H * horizon * 0.9).astype(int)
    st[sy, sx] = r.uniform(0.15, 0.7, n)
    st = np.asarray(Image.fromarray((st * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255 * 2.2
    img.alpha_composite(solid_with_alpha((200, 210, 215), np.clip(st, 0, 1)))

    # moon
    mx, my = int(W * 0.74), int(H * 0.21)
    if variant in ('fullmoon', 'halloween'):
        moon = crescent(int(H * 0.085), phase=None,
                        glow_color=(140, 232, 186) if variant == 'halloween' else (200, 214, 208))
    else:
        moon = crescent(int(H * 0.085), phase=0.58, tilt=-150)
    img.alpha_composite(moon, (mx - moon.width // 2, my - moon.height // 2))
    if variant == 'halloween':  # Murcielago: bats across the moon
        for dx, dy, s in ((-0.035, -0.010, 0.030), (0.020, 0.040, 0.022), (0.045, -0.055, 0.017), (-0.075, 0.060, 0.016),
                          (0.090, 0.015, 0.013), (-0.010, -0.095, 0.012), (0.130, -0.070, 0.010)):
            b = bat(int(W * s))
            img.alpha_composite(b, (int(mx + W * dx) - b.width // 2, int(my + H * dy) - b.height // 2))

    # Las Noches on the horizon: flat dome + thin towers, hazed into the sky
    ln = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(ln)
    hx, hy = W * 0.36, H * horizon + 6
    dw, dh = W * 0.20, H * 0.055
    d.pieslice((hx - dw, hy - dh, hx + dw, hy + dh), 180, 360, fill=255)
    for off, th, tw in ((-0.9, 0.105, 5), (-0.55, 0.14, 6), (0.12, 0.19, 7), (0.45, 0.125, 5), (0.82, 0.09, 4), (1.15, 0.06, 4)):
        x = hx + off * dw
        d.rectangle((x - tw, hy - H * th, x + tw, hy), fill=255)
        d.polygon([(x - tw, hy - H * th), (x + tw, hy - H * th), (x, hy - H * th - tw * 3)], fill=255)
    lna = np.asarray(ln.filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    img.alpha_composite(solid_with_alpha((30, 32, 36), lna * 0.95))
    if variant == 'christmas':  # a star on the tallest tower
        star = star_glint(max(3, int(H * 0.006)))
        img.alpha_composite(star, (int(hx + 0.12 * dw) - star.width // 2, int(hy - H * 0.19 - 7 * 3) - star.height // 2))

    # dunes: smooth layered heightfields, lit from the moon side (upper right)
    layers = [
        (horizon + 0.004, 0.010, (46, 48, 52), (92, 94, 98), 11),
        (horizon + 0.045, 0.028, (40, 42, 47), (132, 134, 138), 12),
        (horizon + 0.14, 0.050, (30, 31, 35), (168, 170, 173), 13),
        (horizon + 0.30, 0.070, (18, 19, 22), (190, 191, 193), 14),
    ]
    xs = np.arange(W)
    Y = np.arange(H)[:, None].astype(np.float32)
    for base, amp, dark, lit, sd in layers:
        prof = base * H + smooth1d(W, sd, 4, W // 5, W // 60) * amp * H * 3.0
        slope = np.gradient(prof)
        light = np.clip(0.5 + slope * 0.9 * (H / 1080), 0, 1)
        light = np.convolve(np.pad(light, 20, mode='edge'), np.ones(41) / 41, mode='valid')
        mask = np.clip((Y - prof[None, :]) / 1.2, 0, 1)
        depth = np.clip((Y - prof[None, :]) / (H * 0.22), 0, 1)
        shade = np.clip(light[None, :] * (1 - depth) ** 1.4, 0, 1)
        col = np.array(dark, np.float32) + (np.array(lit, np.float32) - np.array(dark, np.float32)) * shade[..., None]
        ripple = np.sin((Y - prof[None, :]) * 0.9 + smooth1d(W, sd + 50, 3, 120, 10)[None, :] * 12) * 0.5 + 0.5
        col = col * (0.97 + ripple[..., None] * 0.03)
        crest = np.clip(1 - np.abs(Y - prof[None, :] - 1.5) / 2.5, 0, 1) * light[None, :] ** 2
        col = col + crest[..., None] * 34
        arr = np.concatenate([col.clip(0, 255), (mask * 255)[..., None]], -1)
        if variant == 'halloween' and sd == 13:
            # Hollow masks behind this dune line, so its sand hides their lower half
            for tx, th, rot in ((0.47, 0.050, -14), (0.70, 0.040, 10), (0.84, 0.056, -7)):
                x0 = int(W * tx)
                hm = hollow_mask(int(H * th)).rotate(rot, expand=True, resample=Image.BICUBIC)
                img.alpha_composite(hm, (x0 - hm.width // 2, int(prof[x0]) - int(hm.height * 0.55)))
        img.alpha_composite(Image.fromarray(arr.astype(np.uint8), 'RGBA'))

        if sd == 12:
            # quartz trees standing on the second dune line
            for tx, th in ((0.60, 0.11), (0.635, 0.07), (0.90, 0.09)):
                x0 = int(W * tx)
                tree = quartz_tree(int(H * th), seed=int(tx * 1000))
                img.alpha_composite(tree, (x0 - tree.width // 2, int(prof[x0]) + 4 - tree.height))

    # low mist over the horizon (green and thicker on Halloween)
    halloween = variant == 'halloween'
    mist = np.exp(-((yy - horizon - 0.03) / (0.07 if halloween else 0.05)) ** 2) * (0.30 if halloween else 0.22)
    mist = mist * np.clip(0.8 + noise2d(W, H, 21, scale=240, octaves=3)[..., None][..., 0] * 1.4, 0, 1.2)
    img.alpha_composite(solid_with_alpha((96, 214, 156) if halloween else (170, 176, 180), np.clip(mist, 0, 1)))

    if variant == 'christmas':  # snowfall: soft flakes, bigger and brighter toward the viewer
        n = W * H // 1400
        fx, fy = rv.uniform(0, W, n), rv.uniform(0, H, n)
        near = rv.uniform(0, 1, n) ** 2.2
        snow = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(snow)
        for x, y, k in zip(fx, fy, near):
            rad = (0.6 + k * 2.4) * H / 1080
            d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=int(110 + 145 * k))
        sa = np.asarray(snow.filter(ImageFilter.GaussianBlur(0.7 * H / 1080)), np.float32) / 255
        img.alpha_composite(solid_with_alpha((238, 242, 246), np.clip(sa * 1.25, 0, 1)))

    # left shade for the menu column + vignette + grain
    xx = np.linspace(0, 1, W)[None, :]
    a = np.zeros((H, W), np.float32)
    if menu_shade:
        a += np.clip(1 - xx / 0.46, 0, 1) ** 1.5 * 0.82
    vig = np.hypot((xx - 0.55) / 0.75, (yy - 0.5) / 0.62)
    a = 1 - (1 - a) * (1 - np.clip(vig - 0.55, 0, 1) * 0.9)
    img.alpha_composite(solid_with_alpha(INK, np.clip(a, 0, 1)))
    g = noise2d(W, H, 99, scale=1, octaves=1)
    arr = np.asarray(img, np.float32)
    arr[..., :3] += g[..., None] * 14
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), 'RGBA').convert('RGB')


def quartz_tree(h, seed=0):
    """Hueco Mundo's white crystal trees: angular, leafless branching."""
    r = random.Random(seed)
    W, H = 160, 170
    ss = 3
    im = Image.new('L', (W * ss, H * ss), 0)
    d = ImageDraw.Draw(im)
    scale = h / 120 * ss

    def branch(x, y, ang, ln, wd, depth):
        x2 = x + math.cos(ang) * ln * scale
        y2 = y - math.sin(ang) * ln * scale
        d.line((x, y, x2, y2), fill=255, width=max(1, int(wd * scale)))
        if depth == 0:
            return
        for s in (-1, 1):
            if r.random() < 0.85:
                branch(x2, y2, ang + s * r.uniform(0.35, 0.7), ln * r.uniform(0.55, 0.75), wd * 0.62, depth - 1)

    branch(W * ss / 2, H * ss, math.pi / 2 + r.uniform(-0.08, 0.08), 48, 5, 4)
    m = np.asarray(im.resize((W, H), Image.LANCZOS), np.float32) / 255
    return solid_with_alpha((168, 172, 176), m * 0.8)


# ---------------------------------------------------------------- UI plates
def scalable_panel(fill, border, border_px=2, size=32, accent=None, accent_side='left', accent_px=3, alpha=1.0):
    im = Image.new('RGBA', (size, size), fill)
    d = ImageDraw.Draw(im)
    if border is not None and border_px:
        for i in range(border_px):
            d.rectangle((i, i, size - 1 - i, size - 1 - i), outline=border)
    if accent is not None:
        if accent_side == 'left':
            d.rectangle((0, 0, accent_px - 1, size - 1), fill=accent)
        elif accent_side == 'bottom':
            d.rectangle((0, size - accent_px, size - 1, size - 1), fill=accent)
    if alpha < 1:
        a = np.asarray(im, np.float32)
        a[..., 3] *= alpha
        im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    return im
