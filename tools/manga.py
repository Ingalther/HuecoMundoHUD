"""Manga-panel look: ink/screentone filter for portraits, torn-paper panels, speed lines."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import art
from art import BONE, EMERALD, INK, rgba

CLASSES = [  # (button name, portrait name, sel name, number, label, katakana)
    ('scout', 'scout', 'scout', 1, 'SCOUT', 'スカウト'),
    ('soldier', 'soldier', 'soldier', 2, 'SOLDIER', 'ソルジャー'),
    ('pyro', 'pyro', 'pyro', 3, 'PYRO', 'パイロ'),
    ('demoman', 'demoman', 'demo', 4, 'DEMOMAN', 'デモマン'),
    ('heavyweapons', 'heavy', 'heavy', 5, 'HEAVY', 'ヘビー'),
    ('engineer', 'engineer', 'engineer', 6, 'ENGINEER', 'エンジニア'),
    ('medic', 'medic', 'medic', 7, 'MEDIC', 'メディック'),
    ('sniper', 'sniper', 'sniper', 8, 'SNIPER', 'スナイパー'),
    ('spy', 'spy', 'spy', 9, 'SPY', 'スパイ'),
]


def arr(im):
    return np.asarray(im, np.float32) / 255


def screentone(gray, period=6, angle=45, dot_color=INK, paper=BONE, gamma=1.0):
    """Clustered-dot halftone: gray (0..1, 1 = white) -> RGB image of dots on paper."""
    h, w = gray.shape
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(angle)
    u = (xs * math.cos(a) + ys * math.sin(a)) / period
    v = (-xs * math.sin(a) + ys * math.cos(a)) / period
    cell = np.hypot(u - np.round(u), v - np.round(v)) / 0.7071  # 0 centre .. 1 corner
    darkness = np.clip(1 - gray, 0, 1) ** gamma
    ink = np.clip((np.sqrt(darkness) - cell) * 6 + 0.5, 0, 1)
    out = np.array(paper, np.float32)[None, None] * (1 - ink[..., None]) + np.array(dot_color, np.float32)[None, None] * ink[..., None]
    return out


def mangaize(im, size=None, period=5, contrast=1.35, lines=True, paper=BONE, ink=(10, 10, 12), lift=0.6):
    """Colour render -> black ink + screentone + paper, keeping alpha."""
    im = im.convert('RGBA')
    if size:
        im = im.resize(size, Image.LANCZOS)
    a = arr(im)
    alpha = a[..., 3]
    g = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    g = np.clip(g, 0, 1) ** lift
    g = np.clip((g - 0.5) * contrast + 0.55, 0, 1)
    solid_black = g < 0.16
    paper_white = g > 0.86
    tone = screentone(np.clip((g - 0.16) / 0.7, 0, 1), period=period, dot_color=ink, paper=paper)
    rgb = np.where(solid_black[..., None], np.array(ink, np.float32)[None, None], tone)
    rgb = np.where(paper_white[..., None], np.array(paper, np.float32)[None, None], rgb)
    if lines:
        L = Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
        e = arr(L.filter(ImageFilter.FIND_EDGES))
        e = np.clip((e - 0.06) * 5, 0, 1)
        rgb = rgb * (1 - e[..., None]) + np.array(ink, np.float32)[None, None] * e[..., None]
    out = np.concatenate([rgb, alpha[..., None] * 255], -1)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), 'RGBA')


def poly_mask(size, pts, ss=3):
    W, H = size
    m = Image.new('L', (W * ss, H * ss), 0)
    ImageDraw.Draw(m).polygon([(x * ss, y * ss) for x, y in pts], fill=255)
    return m.resize(size, Image.LANCZOS)


def torn(mask, seed, grow=6, shrink=3, rough=0.35):
    """From a clean mask build (outer, inner) masks with ragged torn-paper edges."""
    w, h = mask.size
    n = art.noise2d(w, h, seed, scale=10, octaves=3)
    n2 = art.noise2d(w, h, seed + 7, scale=4, octaves=2)
    outer = arr(mask.filter(ImageFilter.GaussianBlur(grow)))
    outer = np.clip((outer + n * rough + n2 * 0.12 - 0.18) * 14, 0, 1)
    outer *= arr(mask.filter(ImageFilter.GaussianBlur(grow * 1.5))) > 0.08  # no stray flecks away from the edge
    inner = arr(mask.filter(ImageFilter.GaussianBlur(shrink)))
    inner = np.clip((inner + n * 0.12 - 0.72) * 14, 0, 1)
    return outer, inner * outer


def panel(size, pts, seed, content=None, fill=(8, 9, 10), edge=BONE, edge_alpha=1.0, shadow=True):
    """Manga panel: ink (or content) inside a torn paper edge, with a hard offset shadow."""
    w, h = size
    m = poly_mask(size, pts)
    outer, inner = torn(m, seed)
    base = np.zeros((h, w, 4), np.float32)
    if shadow:
        sh = np.zeros_like(outer)  # hard offset shadow; a plain shift, np.roll would wrap it onto the top/left edge
        sh[7:, 9:] = outer[:-7, :-9] * 0.85
        base[..., :3] = 0
        base[..., 3] = sh
    edge_rgb = np.array(edge, np.float32) / 255
    base[..., :3] = base[..., :3] * (1 - outer[..., None]) + edge_rgb * outer[..., None]
    base[..., 3] = np.maximum(base[..., 3], outer * edge_alpha)
    fill_rgb = np.broadcast_to(np.array(fill, np.float32) / 255, (h, w, 3)).copy()
    if content is not None:
        c = arr(content.convert('RGBA'))
        fill_rgb = fill_rgb * (1 - c[..., 3:4]) + c[..., :3] * c[..., 3:4]
    base[..., :3] = base[..., :3] * (1 - inner[..., None]) + fill_rgb * inner[..., None]
    base[..., 3] = np.maximum(base[..., 3], inner)
    return Image.fromarray((base * 255).clip(0, 255).astype(np.uint8), 'RGBA')


def speed_lines(size, cx, cy, n=140, seed=3, color=BONE, inner=0.18, alpha=0.5):
    w, h = size
    r = np.random.default_rng(seed)
    ss = 2
    im = Image.new('L', (w * ss, h * ss), 0)
    d = ImageDraw.Draw(im)
    R = math.hypot(w, h) * ss
    for _ in range(n):
        a = r.uniform(0, 2 * math.pi)
        wd = r.uniform(0.004, 0.02)
        r0 = R * r.uniform(inner, inner + 0.25) / 2
        p0 = (cx * ss + math.cos(a) * r0, cy * ss + math.sin(a) * r0)
        p1 = (cx * ss + math.cos(a - wd) * R, cy * ss + math.sin(a - wd) * R)
        p2 = (cx * ss + math.cos(a + wd) * R, cy * ss + math.sin(a + wd) * R)
        d.polygon([p0, p1, p2], fill=int(255 * r.uniform(0.4, 1)))
    m = arr(im.resize(size, Image.LANCZOS)) * alpha
    return art.solid_with_alpha(color, m)


def lanza(w, h, seed=9):
    """Lanza del Relampago: a long emerald spear streak with glow, diagonal."""
    ss = 3
    m = Image.new('L', (w * ss, h * ss), 0)
    d = ImageDraw.Draw(m)
    x0, y0, x1, y1 = 0.02 * w * ss, 0.85 * h * ss, 0.98 * w * ss, 0.15 * h * ss
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang), math.cos(ang)
    t = h * ss * 0.035
    d.polygon([(x0, y0), (x1 - nx * 0, y1), (x0 + nx * t, y0 + ny * t)], fill=255)
    core = arr(m.resize((w, h), Image.LANCZOS))
    glow = arr(Image.fromarray((core * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(h * 0.05)))
    out = art.solid_with_alpha(EMERALD, np.clip(glow * 1.6, 0, 1) * 0.8)
    out.alpha_composite(art.solid_with_alpha((220, 255, 236), core))
    return out


def load_portrait(root, name):
    from vtfread import read_vtf
    return read_vtf(os.path.join(root, name))


def class_card(portrait, num, label, kana, seed, hover=False, size=(512, 192)):
    w, h = size
    pts = [(38, 16), (502, 6), (474, 176), (10, 186)]
    content = rgba(size, (8, 9, 10), 255)
    p = portrait.convert('RGBA').resize((300, 300), Image.LANCZOS)
    if not hover:
        p = mangaize(p, period=4)
    content.alpha_composite(p, (w - 300 + 10, -62))
    # ink fade from the left so the name stays readable
    fade = np.clip(1.55 - np.linspace(0, 1, w) * 1.7, 0, 1)[None, :].repeat(h, 0)  # ink under the whole name
    content.alpha_composite(art.solid_with_alpha((8, 9, 10), fade * (0.97 if not hover else 0.9)))
    card = panel(size, pts, seed, content=content, edge=EMERALD if hover else BONE)
    numi = art.text_img(str(num), art.font(art.SERIF_B, 150), EMERALD if not hover else (120, 255, 190))
    card.alpha_composite(numi, (40, (h - numi.height) // 2 - 4))
    # long names (ENGINEER, RANDOM) shrink to fit inside the torn right edge instead of running off it
    x0 = 40 + numi.width + 22
    for size_pt in range(50, 20, -2):
        name = art.text_img(label, art.font(art.SERIF, size_pt), BONE, tracking=6 * size_pt // 50)
        if x0 + name.width <= int(w * 0.76):  # well clear of the torn edge and the hover glow
            break
    # soft ink shadow so letters that reach the portrait still read
    shadow = art.solid_with_alpha(INK, arr(name.getchannel('A').filter(ImageFilter.MaxFilter(5))
                                           .filter(ImageFilter.GaussianBlur(3))) * 0.95)
    card.alpha_composite(shadow, (x0, 46 + (50 - size_pt) // 2))
    card.alpha_composite(name, (x0, 46 + (50 - size_pt) // 2))
    k = art.text_img(kana, art.font(art.KANA, 26), (150, 152, 150), tracking=4)
    card.alpha_composite(k, (40 + numi.width + 26, 46 + name.height + 16))
    if hover:
        glow = card.getchannel('A').filter(ImageFilter.GaussianBlur(6))
        g = art.solid_with_alpha(EMERALD, arr(glow) * 0.5)
        g.alpha_composite(card)
        card = g
    return card


def tall_card(figure, num, kana, seed, active=False, size=(256, 512)):
    """Inventory class tile: full-body figure inside a slanted torn panel, numeral + vertical katakana."""
    w, h = size
    pts = [(22, 14), (244, 8), (234, 500), (12, 504)]
    content = rgba(size, (8, 9, 10), 255)
    tone = screentone(np.full((h, w), 0.82, np.float32), period=6, dot_color=(24, 26, 28), paper=(8, 9, 10))
    content.alpha_composite(Image.fromarray(np.concatenate([tone, np.full((h, w, 1), 255.)], -1).astype(np.uint8), 'RGBA'))
    f = figure.convert('RGBA').resize((w, h), Image.LANCZOS)
    if not active:
        f = mangaize(f, period=4, lift=0.55)
    content.alpha_composite(f, (0, 14))
    card = panel(size, pts, seed, content=content, edge=EMERALD if active else BONE)
    numi = art.text_img(str(num), art.font(art.SERIF_B, 84), EMERALD if not active else (130, 255, 196))
    card.alpha_composite(numi, (30, 22))
    k = art.vertical_text(kana, art.font(art.KANA, 26), BONE, gap=2)
    card.alpha_composite(k, (w - k.width - 26, 30))
    return card


def team_card(portraits, label, kanji, tint, seed, hover=False, size=(512, 1024)):
    w, h = size
    pts = [(40, 20), (500, 8), (474, 1004), (12, 1016)]
    content = rgba(size, (8, 9, 10), 255)
    g = np.clip(np.linspace(0.95, 0.35, h), 0, 1)[:, None].repeat(w, 1)
    tone = screentone(g, period=8, dot_color=tuple(int(c * 0.55) for c in tint), paper=(8, 9, 10))
    content.alpha_composite(Image.fromarray(np.concatenate([tone, np.full((h, w, 1), 255.)], -1).astype(np.uint8), 'RGBA'))
    for i, p in enumerate(portraits):
        p = p.convert('RGBA').resize((420, 420), Image.LANCZOS)
        if not hover:
            p = mangaize(p, period=5, lift=0.55)
        content.alpha_composite(p, (60 + (i % 2) * 40 - 20, 260 + i * 230))
    fade = np.clip(np.linspace(1.1, -0.2, h), 0, 1)[:, None].repeat(w, 1) ** 1.5
    content.alpha_composite(art.solid_with_alpha((8, 9, 10), fade))
    card = panel(size, pts, seed, content=content, edge=EMERALD if hover else BONE)
    t = art.text_img(label, art.font(art.SERIF_B, 170), tint if not hover else BONE, tracking=10)
    card.alpha_composite(t, ((w - t.width) // 2, 60))
    k = art.text_img(kanji, art.font(art.KANJI, 110), BONE)
    card.alpha_composite(k, ((w - k.width) // 2, 70 + t.height + 20))
    if hover:
        glow = card.getchannel('A').filter(ImageFilter.GaussianBlur(10))
        gl = art.solid_with_alpha(EMERALD, arr(glow) * 0.55)
        gl.alpha_composite(card)
        card = gl
    return card


def small_card(label, kanji, seed, hover=False, size=(512, 192)):
    w, h = size
    pts = [(30, 18), (500, 8), (480, 176), (10, 184)]
    card = panel(size, pts, seed, edge=EMERALD if hover else BONE)
    t = art.text_img(label, art.font(art.SERIF, 64), BONE, tracking=8)
    k = art.text_img(kanji, art.font(art.KANJI, 56), EMERALD)
    x = (w - t.width - k.width - 24) // 2
    card.alpha_composite(t, (x, (h - t.height) // 2))
    card.alpha_composite(k, (x + t.width + 24, (h - k.height) // 2))
    return card


def model_frame(tint, seed, size=(512, 512)):
    """In-game player model backdrop: tilted torn panel, team-tinted tone rising from the bottom."""
    w, h = size
    pts = [(40, 150), (490, 110), (470, 480), (14, 500)]
    content = rgba(size, (8, 9, 10), 235)
    g = np.clip(np.linspace(1.2, 0.2, h), 0, 1)[:, None].repeat(w, 1)
    tone = screentone(g, period=9, dot_color=tint, paper=(8, 9, 10))
    content.alpha_composite(Image.fromarray(np.concatenate([tone, np.full((h, w, 1), 235.)], -1).astype(np.uint8), 'RGBA'))
    return panel(size, pts, seed, content=content)


def banner(tint, seed, mirror=False, size=(1024, 256)):
    """Scoreboard team header strip."""
    w, h = size
    pts = [(30, 30), (1000, 12), (984, 230), (12, 244)]
    content = rgba(size, (8, 9, 10), 240)
    g = np.clip(np.linspace(0.3, 1.1, w), 0, 1)[None, :].repeat(h, 0)
    tone = screentone(g, period=9, dot_color=tint, paper=(8, 9, 10))
    content.alpha_composite(Image.fromarray(np.concatenate([tone, np.full((h, w, 1), 240.)], -1).astype(np.uint8), 'RGBA'))
    im = panel(size, pts, seed, content=content)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if mirror else im


def score_main(seed=406, size=(1024, 656)):
    """Scoreboard body: one big torn manga page (ink, bone edge), screentone rising from two corners, a faint
    虚圏 (Hueco Mundo) brushed into the middle between the two teams."""
    w, h = size
    pts = [(16, 22), (w - 12, 10), (w - 22, h - 14), (10, h - 24)]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    g = np.clip(1 - np.hypot(xx / w, yy / h) * 2.2, 0, 1) + np.clip(1 - np.hypot(1 - xx / w, 1 - yy / h) * 2.2, 0, 1)
    tone = screentone(np.clip(1 - g * 0.5, 0, 1), period=9, dot_color=(34, 60, 50), paper=(8, 9, 10))
    content = Image.fromarray(np.concatenate([tone, np.full((h, w, 1), 245.)], -1).astype(np.uint8), 'RGBA')
    k = art.vertical_text('虚圏', art.font(art.KANJI, int(h * 0.3)), (226, 226, 220), gap=10)
    k.putalpha(Image.fromarray((arr(k.getchannel('A')) * 0.06 * 255).astype(np.uint8)))
    content.alpha_composite(k, ((w - k.width) // 2, (h - k.height) // 2))
    return panel(size, pts, seed, content=content)


def see_through(img, alpha):
    """See-through ink: only the bright bone torn edge stays solid, the dark inside lets the map through."""
    a = arr(img)
    rim = np.clip((a[..., :3].mean(-1) - 0.45) * 4, 0, 1)
    a[..., 3] *= alpha + (1 - alpha) * rim
    return Image.fromarray((a * 255).clip(0, 255).astype(np.uint8), 'RGBA')


def win_page(seed=411, size=(1024, 672), alpha=0.6):
    """End-of-round win panel: a torn manga page, speed lines bursting down from the title, screentone rising from
    the bottom corners, a faint 勝 (victory) brushed on the right."""
    w, h = size
    pts = [(14, 18), (w - 10, 8), (w - 18, h - 12), (8, h - 20)]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    g = np.clip(1 - np.hypot(xx / w, 1 - yy / h) * 2.4, 0, 1) + np.clip(1 - np.hypot(1 - xx / w, 1 - yy / h) * 2.4, 0, 1)
    tone = screentone(np.clip(1 - g * 0.5, 0, 1), period=9, dot_color=(34, 60, 50), paper=(8, 9, 10))
    content = Image.fromarray(np.concatenate([tone, np.full((h, w, 1), 245.)], -1).astype(np.uint8), 'RGBA')
    lines = arr(speed_lines(size, w // 2, int(h * 0.06), n=120, seed=seed, alpha=0.14, inner=0.12))
    lines[..., 3] *= np.clip(1.3 - np.linspace(0, 1, h) * 1.2, 0, 1)[:, None]
    content.alpha_composite(Image.fromarray((lines * 255).astype(np.uint8), 'RGBA'))
    k = art.text_img('勝', art.font(art.KANJI, int(h * 0.62)), (226, 226, 220))
    k.putalpha(Image.fromarray((arr(k.getchannel('A')) * 0.05 * 255).astype(np.uint8)))
    content.alpha_composite(k, (w - k.width - 20, (h - k.height) // 2 + 30))
    return see_through(panel(size, pts, seed, content=content), alpha)


def rule_v(h=512, w=24):
    """Vertical emerald brush stroke (the scoreboard's team divider)."""
    return rule(h, w, thick=5).rotate(90, expand=True)


def top_band(seed=407, size=(1024, 80)):
    """Casual / competitive team strip at the top of the screen: the CTF score strip's torn band, stretched wider."""
    return ctf_bar(seed, size)


def portrait_frame(seed=408, size=(128, 100)):
    """Torn bone rim laid over each player portrait of the top team strip (the centre stays clear)."""
    w, h = size
    m = poly_mask(size, [(6, 5), (w - 5, 7), (w - 7, h - 5), (5, h - 7)])
    outer, inner = torn(m, seed, grow=4, shrink=6)
    rim = np.clip(outer - inner, 0, 1)
    return art.solid_with_alpha(BONE, rim)


def tone_tile(size=64, level=0.8, period=8):
    t = screentone(np.full((size, size), level, np.float32), period=period, angle=0, dot_color=(255, 255, 255), paper=(0, 0, 0))
    a = t[..., 0] / 255
    return art.solid_with_alpha((226, 226, 220), a)


def ulq_eyes(size=(1024, 384), seed=21):
    """Manga close-up of Ulquiorra's eyes: heavy lids, emerald irises, the tear marks, bangs over the brow."""
    W, H = size
    ss = 2
    w, h = W * ss, H * ss
    skin = np.full((h, w), 0.93, np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # shadow under the bangs and toward the temples
    skin -= np.clip(0.42 - yy / h, 0, 1) * 0.9
    skin -= (np.abs(xx / w - 0.5) * 2) ** 3 * 0.35
    base = screentone(np.clip(skin, 0, 1), period=6 * ss, dot_color=(30, 32, 34), paper=(236, 234, 228))
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    d = ImageDraw.Draw(img)
    INKC = (10, 10, 12, 255)
    for cx, flip in ((0.3, -1), (0.7, 1)):
        ex, ey = cx * w, 0.56 * h
        ew, eh = 0.155 * w, 0.2 * h
        inner = (ex - flip * ew, ey + eh * 0.05)
        outer = (ex + flip * ew, ey + eh * 0.12)
        top = [(inner[0] + (outer[0] - inner[0]) * t, ey - eh * 0.40 * math.sin(math.pi * t) ** 0.7 + (outer[1] - ey) * t)
               for t in np.linspace(0, 1, 50)]
        bot = [(inner[0] + (outer[0] - inner[0]) * t, ey + eh * 0.34 * math.sin(math.pi * t) ** 1.1 + (outer[1] - ey) * t * 0.6)
               for t in np.linspace(1, 0, 50)]
        eye_mask = Image.new('L', (w, h), 0)
        ImageDraw.Draw(eye_mask).polygon(top + bot, fill=255)
        white = Image.new('RGBA', (w, h), (240, 240, 236, 255))
        # iris: emerald, dark rim, radial strokes, small pupil and a hard highlight
        ir = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        idr = ImageDraw.Draw(ir)
        icx, icy, R = ex + flip * ew * 0.06, ey + eh * 0.04, eh * 0.52
        for i in range(40, 0, -1):
            t = i / 40
            c = (int(12 + 40 * (1 - t)), int(90 + 150 * (1 - t) ** 0.7), int(60 + 100 * (1 - t) ** 0.7), 255)
            idr.ellipse((icx - R * t, icy - R * t, icx + R * t, icy + R * t), fill=c)
        idr.ellipse((icx - R, icy - R, icx + R, icy + R), outline=(6, 30, 20, 255), width=int(R * 0.1))
        r = np.random.default_rng(seed)
        for a in np.linspace(0, 2 * math.pi, 46, endpoint=False):
            r0, r1 = R * r.uniform(0.3, 0.45), R * r.uniform(0.75, 0.95)
            idr.line((icx + math.cos(a) * r0, icy + math.sin(a) * r0, icx + math.cos(a) * r1, icy + math.sin(a) * r1),
                     fill=(8, 60, 40, 150), width=ss)
        idr.ellipse((icx - R * 0.22, icy - R * 0.3, icx + R * 0.22, icy + R * 0.3), fill=(4, 10, 8, 255))
        idr.ellipse((icx - R * 0.5, icy - R * 0.3, icx - R * 0.3, icy - R * 0.1), fill=(250, 255, 252, 255))
        white.alpha_composite(ir)
        img.paste(white, (0, 0), eye_mask)
        # shade under the upper lid
        sh = Image.new('L', (w, h), 0)
        ImageDraw.Draw(sh).line(top, fill=200, width=int(eh * 0.35))
        sh = Image.fromarray((arr(sh.filter(ImageFilter.GaussianBlur(eh * 0.08))) * arr(eye_mask) * 150).astype(np.uint8))
        img.paste(Image.new('RGBA', (w, h), (6, 20, 14, 255)), (0, 0), sh)
        # heavy upper lid line, thicker toward the outer corner, with a few lash strokes
        for i in range(len(top) - 1):
            t = i / len(top)
            wd = int(ss * (4 + 13 * t ** 1.2))
            d.line((top[i], top[i + 1]), fill=INKC, width=wd)
        for k in range(4):
            px, py = top[-1 - k * 3]
            d.line((px, py, px + flip * ew * (0.12 + 0.03 * k), py + eh * (0.18 + 0.04 * k)), fill=INKC, width=3 * ss)
        d.line(bot[5:-3], fill=(40, 40, 44, 255), width=2 * ss)
        # tear mark: straight emerald line falling from the lower lid to the panel edge
        tx = ex + flip * ew * 0.05
        ty = ey + eh * 0.36
        tw = 0.013 * h
        d.polygon([(tx - tw, ty), (tx + tw, ty), (tx + tw * 0.8, h), (tx - tw * 0.8, h)], fill=(20, 150, 100, 255))
        d.line((tx - tw, ty, tx - tw * 0.8, h), fill=INKC, width=2 * ss)
        d.line((tx + tw, ty, tx + tw * 0.8, h), fill=INKC, width=2 * ss)
    # bangs: black tapered strands from the top edge
    r = np.random.default_rng(seed + 1)
    xs = np.linspace(-0.05, 1.05, 30)
    for i, x0 in enumerate(xs):
        x0 = (x0 + r.uniform(-0.02, 0.02)) * w
        L = h * (0.14 + 0.2 * r.random() + (0.2 if 12 <= i <= 17 else 0))
        bw = w * r.uniform(0.018, 0.034)
        tip = (x0 + r.uniform(-0.04, 0.04) * w, L)
        d.polygon([(x0 - bw, -5), (x0 + bw, -5), tip], fill=INKC)
        d.line([(x0 - bw * 0.2, 0), tip], fill=(60, 62, 66, 255), width=ss)
    d.line((0.5 * w, 0.55 * h, 0.51 * w, 0.72 * h), fill=(60, 60, 64, 255), width=2 * ss)
    img = img.resize((W, H), Image.LANCZOS)
    pts = [(30, 40), (W - 10, 8), (W - 40, H - 30), (8, H - 8)]
    return panel(size, pts, seed, content=img)


def tone_fill(size, level, tint, period=9, alpha=235, vertical=True, lo=0.3, hi=1.1):
    w, h = size
    n = h if vertical else w
    g = np.clip(np.linspace(hi, lo, n), 0, 1)
    g = g[:, None].repeat(w, 1) if vertical else g[None, :].repeat(h, 0)
    t = screentone(g * level, period=period, dot_color=tint, paper=(8, 9, 10))
    return Image.fromarray(np.concatenate([t, np.full((h, w, 1), float(alpha))], -1).astype(np.uint8), 'RGBA')


def _label(card, txt_kanji, txt_latin, xy, size=1.0):
    """Small 'kanji · LATIN' caption, the same pairing the class cards use."""
    k = art.text_img(txt_kanji, art.font(art.KANJI, int(34 * size)), EMERALD)
    l = art.text_img(txt_latin, art.font(art.SERIF, int(26 * size)), (150, 152, 150), tracking=int(6 * size))
    x, y = xy
    card.alpha_composite(k, (x, y))
    card.alpha_composite(l, (x + k.width + int(14 * size), y + k.height - l.height))


def _watermark(card, ch, box, alpha=0.13):
    """Huge faint kanji bleeding off a card, like the class-card numerals."""
    x, y, w, h = box
    g = art.text_img(ch, art.font(art.KANJI, int(h * 1.25)), BONE)
    g.thumbnail((w, h), Image.LANCZOS)
    a = arr(g)[..., 3] * alpha
    card.alpha_composite(art.solid_with_alpha(BONE, a), (x + (w - g.width) // 2, y + (h - g.height) // 2))


def shard(tint, seed, size=(512, 492)):
    """Player cluster base (HUD 130x125): torn triangle in team screentone, the model stands on it (Weirdcore's
    triangle, inked)."""
    w, h = size
    pts = [(0.52 * w, 0.03 * h), (0.97 * w, 0.86 * h), (0.03 * w, 0.97 * h)]
    content = tone_fill(size, 1.0, tint, period=8, vertical=True, lo=0.12, hi=1.0)
    content.alpha_composite(speed_lines(size, int(w * 0.5), int(h * 0.35), n=60, seed=seed, alpha=0.10, inner=0.3))
    return panel(size, pts, seed, content=content)


def hp_band(seed, size=(512, 206)):
    """Slanted ink band for the health digits (HUD 114x46). The right end (x 0.77-0.87) stays plain ink for the
    health gauge and its mask."""
    w, h = size
    pts = [(40, 10), (w - 8, 6), (w - 42, h - 8), (8, h - 6)]
    content = rgba(size, (8, 9, 10), 240)
    lines = arr(speed_lines(size, 0, h // 2, n=50, seed=seed, alpha=0.10, inner=0.1))
    lines[..., 3] *= np.clip(1.2 - np.linspace(0, 1, w) * 1.9, 0, 1)[None, :]
    content.alpha_composite(Image.fromarray((lines * 255).astype(np.uint8), 'RGBA'))
    card = panel(size, pts, seed, content=content)
    card.alpha_composite(rule(int(w * 0.66), 16, thick=4), (int(w * 0.07), h - 40))
    return card


def ammo_blade(seed, size=(512, 300)):
    """Weapon cluster (HUD 130x76): torn ink blade pointing right, ash screentone thinning toward the tip."""
    w, h = size
    pts = [(10, 10), (w - 12, 130), (w - 22, 190), (60, h - 10)]
    content = tone_fill(size, 0.95, (46, 50, 52), period=7, vertical=False, lo=1.0, hi=0.3)
    content.alpha_composite(speed_lines(size, w - 20, 160, n=60, seed=seed, alpha=0.08, inner=0.3))
    return panel(size, pts, seed, content=content)


def tag(seed, kanji=None, tint=None, size=(512, 160)):
    """Small torn sticker for metal / killstreak: ink, optional team tone, kanji on the left."""
    w, h = size
    pts = [(18, 16), (w - 10, 6), (w - 24, h - 10), (6, h - 16)]
    content = tone_fill(size, 1.0, tint, period=7, vertical=False, lo=0.2, hi=1.0) if tint else None
    card = panel(size, pts, seed, content=content)
    if kanji:
        k = art.text_img(kanji, art.font(art.KANJI, int(h * 0.62)), EMERALD)
        card.alpha_composite(k, (int(h * 0.22), (h - k.height) // 2))
    return card


def streak_card(seed=433, size=(512, 128)):
    """Killstreak splash ("... is GODLIKE!"): the torn ink sticker as a nine-slice card (the game sizes it to the
    text, so everything but the rim sits in the corner cells): an emerald brush slash on its left end."""
    w, h = size
    card = tag(seed, size=size)
    m = Image.new('L', size, 0)
    d = ImageDraw.Draw(m)
    # one bold slash inside the left corner cell (drawn ~9 px wide at 1080p, where two thin ones merged into one),
    # clear of the text that starts right after it
    d.polygon([(19, 12), (32, 12), (17, h - 12), (4, h - 12)], fill=255)
    glow = arr(m.filter(ImageFilter.GaussianBlur(2.5)))
    card.alpha_composite(art.solid_with_alpha(EMERALD, np.clip(glow * 1.6, 0, 1) * 0.8))
    card.alpha_composite(art.solid_with_alpha((170, 240, 206), arr(m)))
    return card


def hp_track(size=(64, 256)):
    """Empty gauge: dark tile with a faint bone rim (also the target-ID health backdrop)."""
    w, h = size
    im = rgba(size, (26, 27, 28), 255)
    ImageDraw.Draw(im).rectangle((0, 0, w - 1, h - 1), outline=BONE + (90,), width=2)
    return im


def hp_fill(size=(64, 256)):
    """Health gauge fill (hud/health_color override). Near white so the game's death-warning tint reads as red;
    a fine screentone keeps it inked instead of flat."""
    w, h = size
    t = screentone(np.full((h, w), 0.93, np.float32), period=6, angle=45, dot_color=(150, 152, 148), paper=(246, 246, 240))
    return Image.fromarray(np.concatenate([t, np.full((h, w, 1), 255.)], -1).clip(0, 255).astype(np.uint8), 'RGBA')


def hp_mask(size=(64, 256), slot=(0.39, 0.61)):
    """Card-ink cover drawn over the health fill, with one vertical slot cut down the middle.
    The game draws the fill from hud/health_color; sv_pure servers ignore our override of that material and draw
    the stock plus-shaped fill instead. Only the middle column shows through the slot, and the plus sign's vertical
    arm fills that column top to bottom, so the gauge looks the same on every server."""
    w, h = size
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :3] = INK
    a[..., 3] = 255
    x0, x1 = int(w * slot[0]), int(w * slot[1])
    a[:, x0:x1, 3] = 0
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    d.rectangle((x0 - 3, 0, x1 + 2, h - 1), outline=BONE + (210,), width=2)
    for i in range(1, 10):
        y = int(h * i / 10)
        d.line((x0 - 12, y, x0 - 6, y), fill=BONE + (120,), width=2)
    return im


def sticky_icon(tint, size=256, seed=31):
    """Stickybomb as a manga illustration: lit sphere (screentone + crosshatch in the shadow, reflected rim light),
    a riveted team band wrapped round it in perspective, conical spikes on the silhouette, a heavy
    brush outline, and an emerald reiatsu aura with burst lines behind it."""
    ss = 3
    S = size * ss
    c, R = S * 0.5, S * 0.27
    r = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    X, Y = (xx - c) / R, (yy - c) / R
    D2 = X * X + Y * Y
    inside = D2 <= 1.0
    Z = np.sqrt(np.clip(1 - D2, 0, 1))
    # light from the upper left, slightly in front
    L = np.array([-0.55, -0.6, 0.58]); L = L / np.linalg.norm(L)
    lam = np.clip(X * L[0] + Y * L[1] + Z * L[2], 0, 1)

    # --- silhouette spikes (cones) and their mask
    spikes = Image.new('L', (S, S), 0)
    sd = ImageDraw.Draw(spikes)
    spike_list = []
    for i in range(12):
        a = math.radians(i * 30 + 15 + r.uniform(-4, 4))
        ux, uy = math.cos(a), math.sin(a)
        wv = R * 0.2
        base1 = (c + ux * R * 0.9 - uy * wv, c + uy * R * 0.9 + ux * wv)
        base2 = (c + ux * R * 0.9 + uy * wv, c + uy * R * 0.9 - ux * wv)
        tip = (c + ux * R * 1.38, c + uy * R * 1.38)
        spike_list.append((a, base1, base2, tip))
        sd.polygon([base1, tip, base2], fill=255)
    body = Image.new('L', (S, S), 0)
    ImageDraw.Draw(body).ellipse((c - R, c - R, c + R, c + R), fill=255)
    sil = np.maximum(arr(spikes), arr(body))

    out = np.zeros((S, S, 4), np.float32)

    # --- burst lines + reiatsu aura behind everything
    fade = np.clip(1 - np.hypot(xx - c, yy - c) / (S * 0.46), 0, 1) ** 0.7  # round, gone before the edges
    burst = arr(speed_lines((S, S), int(c), int(c), n=60, seed=seed, color=BONE, inner=0.55, alpha=0.55))
    out[..., :3] = burst[..., :3]
    out[..., 3] = burst[..., 3] * 0.6 * fade
    grow = arr(Image.fromarray((sil * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(int(S * 0.06) | 1)))
    flame = art.noise2d(S, S, seed + 3, scale=20, octaves=3)
    aura = arr(Image.fromarray((np.clip(grow + flame * 0.35, 0, 1) * 255).astype(np.uint8))
               .filter(ImageFilter.GaussianBlur(S * 0.03)))
    aura = np.clip(aura * 1.4, 0, 1) * (1 - sil) * np.clip(fade * 2.2, 0, 1)  # flames only near the bomb
    em = np.array(EMERALD, np.float32) / 255
    out[..., :3] = out[..., :3] * (1 - aura[..., None]) + em * aura[..., None]
    out[..., 3] = np.maximum(out[..., 3], aura * 0.9)

    # --- sphere shading: screentone, crosshatch in the core shadow, rim light
    tone = screentone(np.clip(0.18 + lam * 0.95, 0, 1), period=6 * ss, dot_color=(22, 24, 26), paper=BONE) / 255
    shadow = np.clip(0.28 - lam, 0, 1) / 0.28
    u = (xx + yy) / (5 * ss)
    v = (xx - yy) / (5 * ss)
    hatch = np.maximum(np.abs(u - np.round(u)) < 0.16, (np.abs(v - np.round(v)) < 0.16) * (shadow > 0.55))
    ink = np.array(INK, np.float32) / 255
    col = np.where((hatch & (shadow > 0.15))[..., None], ink, tone)
    rim = np.clip((np.sqrt(D2) - 0.8) / 0.2, 0, 1) * np.clip(X * 0.7 + Y * 0.7, 0, 1)
    col = col * (1 - rim[..., None] * 0.85) + np.array(BONE, np.float32) / 255 * rim[..., None] * 0.85

    # --- team band wrapped round the sphere (tilted equator)
    t = math.radians(28)
    Yr = Y * math.cos(t) - Z * math.sin(t)
    band = (np.abs(Yr) < 0.2) & inside
    edge = (np.abs(np.abs(Yr) - 0.2) < 0.035) & inside
    tc = np.array(tint, np.float32) / 255
    bshade = (0.45 + 0.75 * lam)[..., None]
    col = np.where(band[..., None], np.clip(tc * bshade, 0, 1), col)
    # rivets along the band
    for k in range(-3, 4):
        lon = k * 0.42
        px, pz = math.sin(lon), math.cos(lon)
        if pz <= 0.15:
            continue
        py = math.sin(t) * pz  # on the tilted equator
        cx_, cy_ = c + px * R, c + py * R
        rr = R * 0.05 * (0.6 + 0.4 * pz)
        m = ((xx - cx_) ** 2 + (yy - cy_) ** 2) < rr * rr
        col[m] = np.array(BONE, np.float32) / 255
    col = np.where(edge[..., None], ink, col)

    sphere_a = inside.astype(np.float32)
    out[..., :3] = out[..., :3] * (1 - sphere_a[..., None]) + col * sphere_a[..., None]
    out[..., 3] = np.maximum(out[..., 3], sphere_a)

    # --- spikes: lit flank bone, shadow flank ink
    img = Image.fromarray((out.clip(0, 1) * 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(img)
    for a, b1, b2, tip in spike_list:
        mid = ((b1[0] + b2[0]) / 2, (b1[1] + b2[1]) / 2)
        lit_side = math.cos(a) * L[0] + math.sin(a) * L[1] > -0.1
        d.polygon([b1, tip, mid], fill=(BONE if lit_side else INK) + (255,))
        d.polygon([mid, tip, b2], fill=INK + (255,))
    # --- heavy brush outline, thicker on the shadow side
    silm = Image.fromarray((sil * 255).astype(np.uint8))
    o1 = arr(silm.filter(ImageFilter.MaxFilter(int(S * 0.022) | 1)))
    shifted = np.zeros_like(o1)
    sh = int(S * 0.012)
    shifted[sh:, sh:] = o1[:-sh, :-sh]
    outline = np.clip(np.maximum(o1, shifted) - sil, 0, 1)
    oa = arr(img)
    oa[..., :3] = oa[..., :3] * (1 - outline[..., None]) + ink * outline[..., None]
    oa[..., 3] = np.maximum(oa[..., 3], outline)
    img = Image.fromarray((oa * 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(img)
    # inner contour between sphere and spikes
    d.ellipse((c - R, c - R, c + R, c + R), outline=INK + (255,), width=int(ss * 5))
    # specular + emerald glint
    g = R * 0.16
    gx, gy = c - R * 0.42, c - R * 0.5
    d.ellipse((gx - g, gy - g * 0.6, gx + g, gy + g * 0.6), fill=(255, 255, 250, 255))
    d.ellipse((gx + g * 0.9, gy + g * 0.5, gx + g * 1.5, gy + g * 1.0), fill=EMERALD + (255,))
    return img.resize((size, size), Image.LANCZOS)


def targe_icon(tint, size=256, seed=37):
    """Chargin' Targe as a manga drawing: round shield of vertical planks (screentone, ink seams, grain strokes),
    four iron straps crossing from the boss to the rim, a team-tone ring, a studded iron rim and a spiked bone boss."""
    ss = 3
    S = size * ss
    c = S / 2
    R = S * 0.45
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    X, Y = (xx - c) / R, (yy - c) / R
    D = np.sqrt(X * X + Y * Y)
    inside = D <= 1
    lam = np.clip(0.6 - X * 0.35 - Y * 0.4, 0, 1)
    ink = np.array(INK, np.float32) / 255
    bone = np.array(BONE, np.float32) / 255
    # planks: every plank a slightly different tone, seams in ink, a few grain strokes
    plank = np.floor((X + 1) * 3.5)
    shade = np.clip(0.2 + lam * 0.75 + (plank % 2) * 0.08, 0, 1)
    col = screentone(shade, period=6 * ss, dot_color=(24, 26, 28), paper=BONE) / 255
    seam = np.abs(((X + 1) * 3.5) - np.round((X + 1) * 3.5)) < 0.045
    grain = art.noise2d(S, S, seed, scale=5, octaves=2)
    streak = np.abs(np.sin(Y * 18 + grain * 4 + plank * 1.7)) < 0.06
    col[seam | (streak & (lam < 0.55))] = ink
    # iron straps: diagonal cross from the boss to the rim
    for ang in (45, 135):
        t = math.radians(ang)
        dist = np.abs(-math.sin(t) * X + math.cos(t) * Y)
        strap = (dist < 0.1) & (D < 0.82)
        col[strap] = np.where((lam[strap] > 0.5)[:, None], bone * 0.92, ink * 1.0 + 0.12)
        col[(np.abs(dist - 0.1) < 0.02) & (D < 0.82)] = ink
    ring = (D > 0.82) & (D < 0.9)
    col[ring] = np.clip(np.array(tint, np.float32) / 255 * (0.55 + 0.6 * lam[ring][:, None]), 0, 1)
    rim = D >= 0.9
    col[rim] = np.where((lam[rim] > 0.5)[:, None], bone, ink)
    for rr in (0.82, 0.9):
        col[np.abs(D - rr) < 0.018] = ink
    out = np.zeros((S, S, 4), np.float32)
    out[..., :3] = col
    out[..., 3] = inside
    img = Image.fromarray((out * 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(img)
    for i in range(12):  # rim studs
        a = math.radians(i * 30 + 15)
        px, py = c + math.cos(a) * R * 0.95, c + math.sin(a) * R * 0.95
        r = R * 0.04
        d.ellipse((px - r, py - r, px + r, py + r), fill=BONE + (255,), outline=INK + (255,), width=ss * 2)
    for ang in (45, 135, 225, 315):  # rivets where the straps meet the rim
        a = math.radians(ang)
        px, py = c + math.cos(a) * R * 0.74, c + math.sin(a) * R * 0.74
        r = R * 0.05
        d.ellipse((px - r, py - r, px + r, py + r), fill=BONE + (255,), outline=INK + (255,), width=ss * 2)
    b = R * 0.24  # domed boss with a short spike
    d.ellipse((c - b, c - b, c + b, c + b), fill=BONE + (255,), outline=INK + (255,), width=ss * 5)
    d.pieslice((c - b, c - b, c + b, c + b), 20, 200, fill=(150, 152, 150, 255))
    d.ellipse((c - b * 0.7, c - b * 0.7, c + b * 0.7, c + b * 0.7), fill=BONE + (255,))
    d.polygon([(c - b * 0.28, c), (c, c - b * 1.35), (c + b * 0.28, c)], fill=INK + (255,))
    d.ellipse((c - b * 0.6, c - b * 0.6, c - b * 0.2, c - b * 0.25), fill=(255, 255, 250, 255))
    d.ellipse((c - R, c - R, c + R, c + R), outline=INK + (255,), width=ss * 8)
    return img.resize((size, size), Image.LANCZOS)


# ------------------------------------------------------------------ item meter logos
# Small manga illustrations for the item meter cards, built from layered parts: each part is a shape (drawn in a
# 0..1 unit square) with a style: 'tone' (bone screentone lit from the upper left), 'color' (flat colour with the
# same lighting), 'ink', 'bone'. Every part gets a thin ink edge, the whole silhouette a heavy brush outline.
def _part_mask(S, draw):
    m = Image.new('L', (S, S), 0)
    draw(ImageDraw.Draw(m), lambda x, y: (x * S, y * S), S)
    return arr(m)


def _shade(mask, style, color, S, ss):
    ys, xs = np.nonzero(mask > 0.5)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    if len(xs):
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        g = 1 - np.clip(((xx - x0) / (x1 - x0) + (yy - y0) / (y1 - y0)) / 2, 0, 1)
    else:
        g = np.ones((S, S), np.float32)
    if style == 'tone':
        rgb = screentone(np.clip(0.1 + g * 0.8, 0, 1), period=6 * ss, dot_color=(20, 22, 24), paper=BONE) / 255
    elif style == 'color':
        rgb = np.clip(np.array(color, np.float32)[None, None] / 255 * (0.4 + 0.6 * g[..., None]), 0, 1)
    elif style == 'ink':
        rgb = np.broadcast_to(np.array(INK, np.float32) / 255, (S, S, 3))
    elif style == 'flat':  # crisp flat fill, no lighting (logos that must read sharp)
        rgb = np.broadcast_to(np.array(color or BONE, np.float32) / 255, (S, S, 3))
    else:  # bone
        rgb = np.clip(np.array(BONE, np.float32)[None, None] / 255 * (0.85 + 0.15 * g[..., None]), 0, 1)
    return rgb


def item_logo(parts, highlights=(), size=256, outline=0.03):
    """parts: [(draw(d, P, S), style, colour)], drawn in order. highlights: [(x, y, rx, ry)] white glints."""
    ss = 3
    S = size * ss
    out = np.zeros((S, S, 4), np.float32)
    sil = np.zeros((S, S), np.float32)
    ink = np.array(INK, np.float32) / 255
    for draw, style, color in parts:
        m = _part_mask(S, draw)
        rgb = _shade(m, style, color, S, ss)
        out[..., :3] = out[..., :3] * (1 - m[..., None]) + rgb * m[..., None]
        out[..., 3] = np.maximum(out[..., 3], m)
        edge = np.clip(arr(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(ss * 2 + 1))) - m, 0, 1)
        out[..., :3] = out[..., :3] * (1 - edge[..., None]) + ink * edge[..., None]
        out[..., 3] = np.maximum(out[..., 3], edge)
        sil = np.maximum(sil, m)
    silm = Image.fromarray((sil * 255).astype(np.uint8))
    o1 = arr(silm.filter(ImageFilter.MaxFilter(int(S * outline) | 1)))
    sh = int(S * 0.012)
    shifted = np.zeros_like(o1)
    shifted[sh:, sh:] = o1[:-sh, :-sh]
    ring = np.clip(np.maximum(o1, shifted) - sil, 0, 1)
    out[..., :3] = out[..., :3] * (1 - ring[..., None]) + ink * ring[..., None]
    out[..., 3] = np.maximum(out[..., 3], ring)
    img = Image.fromarray((out.clip(0, 1) * 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(img)
    for x, y, rx, ry in highlights:
        d.ellipse(((x - rx) * S, (y - ry) * S, (x + rx) * S, (y + ry) * S), fill=(255, 255, 250, 255))
    return img.resize((size, size), Image.LANCZOS)


def _poly(pts):
    return lambda d, P, S: d.polygon([P(x, y) for x, y in pts], fill=255)


def _ell(x0, y0, x1, y1):
    return lambda d, P, S: d.ellipse((*P(x0, y0), *P(x1, y1)), fill=255)


def _rect(x0, y0, x1, y1, r=0.0):
    return lambda d, P, S: d.rounded_rectangle((*P(x0, y0), *P(x1, y1)), radius=r * S, fill=255)


def _line(pts, w):
    return lambda d, P, S: d.line([P(x, y) for x, y in pts], fill=255, width=int(w * S), joint='curve')


def _rot(pts, ang, cx=0.5, cy=0.5):
    a = math.radians(ang)
    return [(cx + (x - cx) * math.cos(a) - (y - cy) * math.sin(a), cy + (x - cx) * math.sin(a) + (y - cy) * math.cos(a))
            for x, y in pts]


# Hueco Mundo palette only: ink, bone / grey screentone, Ulquiorra's emerald in a few depths
EM_DEEP, EM_MID, EM_PALE, ASHC, ASH_DARK = (20, 96, 66), (34, 160, 106), (150, 206, 182), (138, 140, 136), (70, 72, 74)
CRIMSON, GOLD, ICE, EM_BRIGHT = EM_DEEP, ASHC, EM_PALE, EM_MID


def logo_banner():      # banner rage: war flag on a pole
    return item_logo([
        (_rect(0.22, 0.1, 0.29, 0.92, 0.02), 'tone', None),
        (_poly([(0.29, 0.14), (0.88, 0.2), (0.72, 0.36), (0.9, 0.54), (0.29, 0.48)]), 'color', CRIMSON),
        (_line([(0.34, 0.26), (0.7, 0.3)], 0.025), 'bone', None),
        (_ell(0.18, 0.04, 0.33, 0.16), 'color', GOLD)], highlights=[(0.23, 0.08, 0.02, 0.015)])


def logo_mask():        # generic meter (sandvich, banner, gas passer...): the Bleach Hollow emblem
    # geometry measured on the emblem (x 0..1, y 0..1 of its 1.21:1 frame), fitted into the square
    def M(x, y):
        return 0.05 + x * 0.9, 0.11 + y * 0.9 / 1.21

    def eye(cx, cy, ang):
        a = math.radians(ang)
        return [M(cx + 0.17 * math.cos(t) * math.cos(a) - 0.1 * math.sin(t) * math.sin(a),
                  cy + (0.17 * math.cos(t) * math.sin(a) + 0.1 * math.sin(t) * math.cos(a)) * 1.21)
                for t in np.linspace(0, 2 * math.pi, 48)]

    def emblem(d, P, S):
        pt = lambda x, y: P(*M(x, y))
        d.polygon([pt(0.2, 0), pt(0.81, 0), pt(0.995, 0.39), pt(0.8, 0.63), pt(0.57, 0.63), pt(0.5, 0.765),
                   pt(0.43, 0.63), pt(0.19, 0.63), pt(0.005, 0.39)], fill=255)
        for bar in ([(0.243, 0.669), (0.31, 0.669), (0.31, 0.905), (0.243, 0.82)],
                    [(0.364, 0.669), (0.415, 0.669), (0.49, 0.8), (0.49, 1.0), (0.364, 0.915)],
                    [(0.636, 0.669), (0.585, 0.669), (0.51, 0.8), (0.51, 1.0), (0.636, 0.915)],
                    [(0.757, 0.669), (0.69, 0.669), (0.69, 0.905), (0.757, 0.82)]):
            d.polygon([pt(x, y) for x, y in bar], fill=255)
        for e in (eye(0.268, 0.36, 38), eye(0.732, 0.36, -38)):  # eye holes
            d.polygon([P(x, y) for x, y in e], fill=0)
        for x0, y0, x1, y1 in ((0.25, 0.36, 0.04, 0.62), (0.75, 0.36, 0.96, 0.62)):  # slots out to the edge
            d.line([pt(x0, y0), pt(x1, y1)], fill=0, width=int(0.05 * 0.9 * S))

    def glow(cx, ang):
        pts = eye(cx, 0.36, ang)
        c = (sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts))
        pts = [(c[0] + (x - c[0]) * 0.45, c[1] + (y - c[1]) * 0.45) for x, y in pts]
        return lambda d, P, S: d.polygon([P(x, y) for x, y in pts], fill=255)

    return item_logo([(emblem, 'flat', BONE), (glow(0.268, 38), 'flat', EMERALD), (glow(0.732, -38), 'flat', EMERALD)],
                     outline=0.018)


def logo_cleaver():     # Flying Guillotine: meat cleaver, wooden handle
    t = -20
    return item_logo([
        (_poly(_rot([(0.02, 0.5), (0.34, 0.46), (0.36, 0.58), (0.04, 0.62)], t)), 'color', ASH_DARK),
        (_poly(_rot([(0.3, 0.2), (0.9, 0.16), (0.94, 0.72), (0.34, 0.74)], t)), 'tone', None),
        (_line(_rot([(0.36, 0.71), (0.92, 0.69)], t), 0.035), 'bone', None),
        (_ell(*_rot([(0.76, 0.24)], t)[0], *[v + 0.1 for v in _rot([(0.76, 0.24)], t)[0]]), 'ink', None),
        ], highlights=[(0.5, 0.32, 0.08, 0.015)])


def logo_eyelander():   # Eyelander: claymore with the eye in the pommel
    return item_logo([
        (_poly([(0.3, 0.64), (0.8, 0.14), (0.86, 0.14), (0.86, 0.2), (0.36, 0.7)]), 'tone', None),
        (_poly(_rot([(0.18, 0.62), (0.52, 0.62), (0.52, 0.7), (0.18, 0.7)], 45, 0.35, 0.66)), 'ink', None),
        (_poly(_rot([(0.3, 0.76), (0.4, 0.76), (0.4, 0.9), (0.3, 0.9)], 45, 0.3, 0.76)), 'color', ASH_DARK),
        (_ell(0.08, 0.76, 0.26, 0.94), 'bone', None),
        (_ell(0.13, 0.81, 0.21, 0.89), 'color', EM_MID)], highlights=[(0.6, 0.36, 0.05, 0.012)])


LOGO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logos')


def logo(name, size=256, fallback=None):
    """An item logo: the hand-picked artwork tools/logos/<name>.png (square, transparent) when there is one,
    else the procedural drawing (fallback, or logo_<name>(), or the Hollow mask)."""
    p = os.path.join(LOGO_DIR, name + '.png')
    if os.path.exists(p):
        return Image.open(p).convert('RGBA').resize((size, size), Image.LANCZOS)
    if fallback is not None:
        return fallback()
    return globals().get('logo_' + name, logo_mask)()


def logo_skull():       # Air Strike kills / Eyelander heads (one shared meter file): a bone skull, emerald eyes
    em = (46, 214, 140)
    return item_logo([
        (_ell(0.16, 0.08, 0.84, 0.66), 'bone', None),
        (_rect(0.3, 0.5, 0.7, 0.88, r=0.07), 'bone', None),
        (_ell(0.25, 0.31, 0.47, 0.53), 'ink', None),
        (_ell(0.53, 0.31, 0.75, 0.53), 'ink', None),
        (_ell(0.32, 0.38, 0.4, 0.46), 'flat', em),
        (_ell(0.6, 0.38, 0.68, 0.46), 'flat', em),
        (_poly([(0.5, 0.53), (0.44, 0.65), (0.56, 0.65)]), 'ink', None),
        (_rect(0.405, 0.72, 0.425, 0.88), 'ink', None),
        (_rect(0.49, 0.72, 0.51, 0.88), 'ink', None),
        (_rect(0.575, 0.72, 0.595, 0.88), 'ink', None),
        (_poly([(0.62, 0.1), (0.58, 0.2), (0.64, 0.24), (0.6, 0.3), (0.62, 0.3), (0.67, 0.24), (0.61, 0.2),
                (0.64, 0.1)]), 'ink', None)], highlights=[(0.34, 0.18, 0.045, 0.02)])


def logo_revenge():     # Frontier Justice: two shotgun shells
    def shell(dx, dy):
        return [(_rect(0.36 + dx, 0.14 + dy, 0.6 + dx, 0.66 + dy, 0.04), 'color', CRIMSON),
                (_rect(0.34 + dx, 0.64 + dy, 0.62 + dx, 0.84 + dy, 0.02), 'color', GOLD),
                (_ell(0.44 + dx, 0.7 + dy, 0.52 + dx, 0.78 + dy), 'ink', None)]
    return item_logo(shell(0.16, -0.06) + shell(-0.1, 0.06), highlights=[(0.34, 0.3, 0.015, 0.1), (0.6, 0.18, 0.015, 0.1)])


def logo_sandvich():    # lunchbox: sandvich
    return item_logo([
        (_rect(0.12, 0.62, 0.88, 0.8, 0.06), 'color', ASHC),
        (_poly([(0.1, 0.56)] + [(0.1 + i * 0.08, 0.5 + (i % 2) * 0.1) for i in range(11)] + [(0.9, 0.62), (0.1, 0.62)]), 'color', EM_MID),
        (_rect(0.14, 0.46, 0.86, 0.54, 0.02), 'color', CRIMSON),
        (_poly([(0.12, 0.44), (0.88, 0.44), (0.8, 0.52), (0.2, 0.52)]), 'color', GOLD),
        (_ell(0.1, 0.16, 0.9, 0.5), 'color', ASHC),
        (_line([(0.5, 0.06), (0.5, 0.3)], 0.02), 'bone', None),
        (_ell(0.46, 0.03, 0.54, 0.1), 'color', EM_MID)], highlights=[(0.34, 0.26, 0.08, 0.03)])


def logo_heart():       # Vita-Saw organs: heart with a medic cross
    heart = [(0.5, 0.88)] + [(0.5 + 0.4 * math.sin(t) ** 3 * 1.0, 0.46 - (0.32 * math.cos(t) - 0.12 * math.cos(2 * t)
             - 0.05 * math.cos(3 * t) - 0.02 * math.cos(4 * t))) for t in np.linspace(-math.pi, math.pi, 60)]
    return item_logo([
        (_poly(heart), 'color', CRIMSON),
        (_rect(0.44, 0.34, 0.56, 0.7, 0.01), 'bone', None),      # medic cross
        (_rect(0.32, 0.46, 0.68, 0.58, 0.01), 'bone', None)],
        highlights=[(0.34, 0.34, 0.06, 0.035)])


def logo_plasma():      # Cow Mangler: plasma orb with orbits
    return item_logo([
        (_ell(0.2, 0.2, 0.8, 0.8), 'color', EM_BRIGHT),
        (_ell(0.34, 0.34, 0.66, 0.66), 'bone', None),
        (lambda d, P, S: d.ellipse((*P(0.06, 0.36), *P(0.94, 0.64)), outline=255, width=int(0.035 * S)), 'ink', None),
        (lambda d, P, S: d.ellipse((*P(0.36, 0.06), *P(0.64, 0.94)), outline=255, width=int(0.035 * S)), 'ink', None)],
        highlights=[(0.42, 0.4, 0.05, 0.035)])


def logo_bolt():        # Pomson: lightning bolt
    return item_logo([
        (_poly([(0.56, 0.04), (0.2, 0.56), (0.46, 0.56), (0.36, 0.96), (0.82, 0.4), (0.54, 0.4), (0.66, 0.04)]),
         'color', EM_PALE)], highlights=[(0.52, 0.22, 0.03, 0.08)])


def logo_beam():        # Righteous Bison: energy rings
    return item_logo([
        (_ell(0.1, 0.1, 0.9, 0.9), 'color', EM_DEEP),
        (_ell(0.24, 0.24, 0.76, 0.76), 'ink', None),
        (_ell(0.32, 0.32, 0.68, 0.68), 'color', EM_PALE),
        (_ell(0.43, 0.43, 0.57, 0.57), 'bone', None)], highlights=[(0.3, 0.26, 0.05, 0.03)])


def logo_sapper():      # sapper: box, dial, prongs, spark
    return item_logo([
        (_line([(0.34, 0.3), (0.3, 0.08)], 0.05), 'ink', None),
        (_line([(0.66, 0.3), (0.7, 0.08)], 0.05), 'ink', None),
        (_rect(0.16, 0.28, 0.84, 0.82, 0.06), 'tone', None),
        (_ell(0.32, 0.38, 0.68, 0.74), 'bone', None),
        (_line([(0.5, 0.56), (0.62, 0.44)], 0.03), 'ink', None),
        (_poly([(0.46, 0.0), (0.38, 0.14), (0.5, 0.14), (0.44, 0.26), (0.6, 0.1), (0.5, 0.1), (0.56, 0.0)]),
         'color', EM_BRIGHT)], highlights=[(0.26, 0.34, 0.04, 0.02)])


def logo_ball():        # Sandman ball: baseball
    return item_logo([
        (_ell(0.14, 0.14, 0.86, 0.86), 'tone', None),
        (lambda d, P, S: d.arc((*P(-0.2, 0.2), *P(0.42, 0.8)), -60, 60, fill=255, width=int(0.03 * S)), 'color', CRIMSON),
        (lambda d, P, S: d.arc((*P(0.58, 0.2), *P(1.2, 0.8)), 120, 240, fill=255, width=int(0.03 * S)), 'color', CRIMSON)],
        highlights=[(0.36, 0.3, 0.07, 0.04)])


def logo_jar():         # Jarate
    return item_logo([
        (_rect(0.24, 0.24, 0.76, 0.9, 0.1), 'tone', None),
        (_rect(0.26, 0.46, 0.74, 0.88, 0.08), 'color', EM_MID),
        (_rect(0.3, 0.1, 0.7, 0.24, 0.03), 'ink', None),
        (_rect(0.34, 0.56, 0.66, 0.72, 0.02), 'bone', None)], highlights=[(0.34, 0.36, 0.025, 0.08)])


def logo_scope():       # Hitman's Heatmaker focus: scope reticle
    return item_logo([
        (_ell(0.08, 0.08, 0.92, 0.92), 'ink', None),
        (_ell(0.16, 0.16, 0.84, 0.84), 'tone', None),
        (_line([(0.5, 0.14), (0.5, 0.86)], 0.025), 'ink', None),
        (_line([(0.14, 0.5), (0.86, 0.5)], 0.025), 'ink', None),
        (_ell(0.44, 0.44, 0.56, 0.56), 'color', CRIMSON)], highlights=[(0.3, 0.28, 0.05, 0.03)])


def logo_soda():        # Soda Popper hype: soda can with bubbles
    return item_logo([
        (_rect(0.26, 0.26, 0.74, 0.92, 0.06), 'color', EM_DEEP),
        (_rect(0.26, 0.48, 0.74, 0.64, 0.0), 'bone', None),
        (_ell(0.26, 0.2, 0.74, 0.32), 'tone', None),
        (_ell(0.14, 0.02, 0.26, 0.14), 'bone', None),
        (_ell(0.62, 0.04, 0.72, 0.14), 'bone', None),
        (_ell(0.42, 0.06, 0.5, 0.14), 'bone', None)], highlights=[(0.34, 0.4, 0.02, 0.06)])


def logo_watch():       # cloak: spy's pocket watch
    return item_logo([
        (lambda d, P, S: d.arc((*P(0.0, 0.3), *P(0.5, 1.1)), 200, 320, fill=255, width=int(0.03 * S)), 'color', GOLD),
        (_rect(0.44, 0.04, 0.56, 0.16, 0.02), 'color', GOLD),
        (_ell(0.14, 0.14, 0.86, 0.86), 'color', GOLD),
        (_ell(0.22, 0.22, 0.78, 0.78), 'bone', None),
        (_line([(0.5, 0.5), (0.5, 0.3)], 0.03), 'ink', None),
        (_line([(0.5, 0.5), (0.64, 0.58)], 0.03), 'ink', None)], highlights=[(0.3, 0.3, 0.04, 0.025)])


def logo_uber():        # ÜberCharge: bold bone medic cross edged in deep emerald, flat and crisp like the Hollow emblem
    # (no ring, shrunk and nudged up: the Vaccinator's shield-shaped resist icon lands on this logo and, tapering
    # towards its point, has to cover it whole)
    def r(x0, y0, x1, y1, rad):
        f = lambda x, y: (0.5 + (x - 0.5) * 0.82, 0.44 + (y - 0.5) * 0.82)
        return _rect(*f(x0, y0), *f(x1, y1), rad)
    return item_logo([
        (r(0.33, 0.1, 0.67, 0.9, 0.03), 'flat', EM_DEEP),
        (r(0.1, 0.33, 0.9, 0.67, 0.03), 'flat', EM_DEEP),
        (r(0.39, 0.16, 0.61, 0.84, 0.02), 'flat', BONE),
        (r(0.16, 0.39, 0.84, 0.61, 0.02), 'flat', BONE)], outline=0.018)


def logo_metal():       # Engineer metal: a pile of three steel ingots (the TF2 metal pile), emerald glint on the top one
    def ingot(x0, y1, w=0.43, h=0.27, inset=0.06, dx=0.07, dy=0.08):
        y0 = y1 - h
        front = [(x0, y1), (x0 + w, y1), (x0 + w - inset, y0), (x0 + inset, y0)]
        top = [(x0 + inset, y0), (x0 + w - inset, y0), (x0 + w - inset + dx, y0 - dy), (x0 + inset + dx, y0 - dy)]
        side = [(x0 + w - inset, y0), (x0 + w, y1), (x0 + w + dx, y1 - dy), (x0 + w - inset + dx, y0 - dy)]
        return [(_poly(side), 'color', ASH_DARK), (_poly(front), 'tone', None), (_poly(top), 'flat', (214, 216, 210))]

    STEEL_TOP = (0.26, 0.67)
    ty = STEEL_TOP[1] - 0.27 - 0.04  # middle of the top ingot's top face
    glint = [(STEEL_TOP[0] + 0.1, ty + 0.012), (STEEL_TOP[0] + 0.36, ty + 0.012),
             (STEEL_TOP[0] + 0.38, ty - 0.012), (STEEL_TOP[0] + 0.12, ty - 0.012)]
    parts = ingot(0.02, 0.95) + ingot(0.48, 0.95) + ingot(*STEEL_TOP) + [(_poly(glint), 'flat', EMERALD)]
    return item_logo(parts, highlights=[(0.14, 0.72, 0.05, 0.012), (0.6, 0.72, 0.05, 0.012)], outline=0.022)


def logo_icicle():      # Spy-cicle
    return item_logo([
        (_poly(_rot([(0.44, 0.02), (0.58, 0.02), (0.56, 0.62), (0.5, 0.66), (0.46, 0.62)], 30)), 'color', ICE),
        (_poly(_rot([(0.36, 0.62), (0.66, 0.62), (0.66, 0.68), (0.36, 0.68)], 30)), 'ink', None),
        (_poly(_rot([(0.46, 0.68), (0.56, 0.68), (0.56, 0.96), (0.46, 0.96)], 30)), 'color', ASH_DARK)],
        highlights=[(0.46, 0.26, 0.015, 0.1)])


def _curve(pts, tips=(), n=10):
    """Closed Catmull-Rom curve through pts; the points listed in tips stay sharp (flame tongues)."""
    out = []
    for i in range(len(pts)):
        p0, p1, p2, p3 = (pts[(i + k) % len(pts)] for k in (-1, 0, 1, 2))
        if p1 in tips:
            p0 = p1
        if p2 in tips:
            p3 = p2
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(tuple(0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t
                                    + (-a + 3 * b - 3 * c + d) * t ** 3) for a, b, c, d in zip(p0, p1, p2, p3)))
    return out


def logo_flame():       # Phlogistinator Mmmph: a three-tongued flame, ember red outside, gold core
    def flame(pts, tips, s=1.0, cx=0.5, cy=0.95):
        pts = [(cx + (x - cx) * s, cy + (y - cy) * s) for x, y in pts]
        tips = [(cx + (x - cx) * s, cy + (y - cy) * s) for x, y in tips]
        return _poly(_curve(pts, tips))

    main, left, right = (0.54, 0.03), (0.2, 0.3), (0.84, 0.2)
    outer = [main, (0.64, 0.24), (0.68, 0.36), right, (0.86, 0.5), (0.82, 0.72), (0.66, 0.92), (0.5, 0.96),
             (0.34, 0.92), (0.18, 0.74), (0.15, 0.52), left, (0.32, 0.44), (0.4, 0.26)]
    inner = [(0.5, 0.36), (0.6, 0.56), (0.64, 0.74), (0.56, 0.88), (0.44, 0.88), (0.36, 0.74), (0.4, 0.56)]
    return item_logo([
        (flame(outer, (main, left, right)), 'flat', (226, 66, 34)),
        (flame(outer, (main, left, right), s=0.66), 'flat', (250, 146, 40)),
        (flame(inner, ((0.5, 0.36),), s=0.9), 'flat', (255, 228, 146))],
        highlights=[(0.36, 0.56, 0.025, 0.06)], outline=0.026)


def tag_with_icon(icon, seed=419, size=(512, 160), crisp=False, box=(58, 26)):
    """meter_bg (manga.tag seed 419) with an icon inked into its left end. Same seed and size as meter_bg, so a
    plain meter_bg drawn on top covers it exactly (the sticky mode hides the shield that way)."""
    im = tag(seed, size=size)
    h = size[1]
    # the tag texture is squashed into its HUD box (58x26 for most); pre-stretch the icon so it lands round
    stretch = (size[0] / size[1]) / (box[0] / box[1])
    ih = int(h * 0.86)
    ic = icon.resize((int(ih * stretch), ih), Image.LANCZOS)
    # emerald reiatsu rim (like the stickybomb's aura) so dark ink outlines still read on the ink tag
    halo = ic.getchannel('A').point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(7))
    halo = halo.filter(ImageFilter.GaussianBlur(0.6 if crisp else 2.2))
    pos = (int(h * 0.12), (h - ic.height) // 2)
    im.alpha_composite(art.solid_with_alpha((36, 168, 112), np.clip(arr(halo) * 1.3, 0, 1) * 0.85), pos)
    im.alpha_composite(ic, pos)
    return im


def building_card(tint, seed, size=(512, 192)):
    """Engineer building status backdrop: torn ink card, team tone rising on the left (behind the building icon)."""
    w, h = size
    pts = [(14, 12), (w - 8, 6), (w - 18, h - 8), (6, h - 12)]
    content = rgba(size, (8, 9, 10), 235)
    zone = tone_fill((int(w * 0.4), h), 1.0, tint, period=7, vertical=True, lo=0.2, hi=1.0)
    fade = np.clip(1.3 - np.linspace(0, 1, zone.width) * 1.4, 0, 1)[None, :].repeat(h, 0)
    za = arr(zone)
    za[..., 3] *= fade
    content.alpha_composite(Image.fromarray((za * 255).astype(np.uint8), 'RGBA'))
    card = panel(size, pts, seed, content=content)
    d = ImageDraw.Draw(card)
    d.line((int(w * 0.02), h - 22, int(w * 0.5), h - 30), fill=EMERALD + (220,), width=4)
    return card


def building_kanji(ch, size=(256, 256)):
    g = art.text_img(ch, art.font(art.KANJI, 230), BONE)
    g.thumbnail(size, Image.LANCZOS)
    return art.fit(g, size)


def rule(w, h, thick=5, color=EMERALD):
    """Tapered emerald stroke (thick at the left, needle-thin at the right) with a soft glow."""
    ss = 3
    m = Image.new('L', (w * ss, h * ss), 0)
    cy = h * ss / 2
    ImageDraw.Draw(m).polygon([(0, cy - thick * ss / 2), (w * ss, cy - 0.3 * ss), (w * ss, cy + 0.3 * ss),
                               (0, cy + thick * ss / 2)], fill=255)
    core = arr(m.resize((w, h), Image.LANCZOS))
    glow = arr(Image.fromarray((core * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(h * 0.25)))
    out = art.solid_with_alpha(color, np.clip(glow * 1.8, 0, 1) * 0.7)
    out.alpha_composite(art.solid_with_alpha((200, 255, 228), core))
    return out


def notice_card(tint, seed, size=(1024, 256)):
    """Center-screen notice (team goal / team switch / alert), HUD 320x82: torn ink card, team tone behind the seal
    on the left, speed lines bursting from it. The emerald rule between the text lines is its own image (rule)."""
    w, h = size
    pts = [(18, 14), (w - 12, 6), (w - 26, h - 14), (8, h - 8)]
    content = rgba(size, (8, 9, 10), 240)
    zone = arr(tone_fill((int(w * 0.36), h), 1.0, tint, period=8, vertical=True, lo=0.15, hi=1.0))
    zone[..., 3] *= np.clip(1.3 - np.linspace(0, 1, zone.shape[1]) * 1.35, 0, 1)[None, :]
    content.alpha_composite(Image.fromarray((zone * 255).astype(np.uint8), 'RGBA'))
    lines = arr(speed_lines(size, int(w * 0.12), h // 2, n=90, seed=seed, alpha=0.12, inner=0.2))
    lines[..., 3] *= np.clip(1.2 - np.linspace(0, 1, w) * 1.1, 0, 1)[None, :]
    content.alpha_composite(Image.fromarray((lines * 255).astype(np.uint8), 'RGBA'))
    card = panel(size, pts, seed, content=content)
    return card


def notif_card(tint, seed, size=(1024, 176)):
    """HUD notification ("Your INTELLIGENCE has been dropped!"...): the notice card, flatter (the game stretches it
    to the text), team tone behind the icon, an emerald brush stroke under the text."""
    w, h = size
    card = notice_card(tint, seed, size)
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).polygon([(int(w * 0.14), h - 34), (w - 60, h - 40), (w - 64, h - 35), (int(w * 0.14), h - 29)],
                              fill=255)
    glow = arr(m.filter(ImageFilter.GaussianBlur(3)))
    card.alpha_composite(art.solid_with_alpha(EMERALD, np.clip(glow * 1.5, 0, 1) * 0.7))
    card.alpha_composite(art.solid_with_alpha((170, 240, 206), arr(m) * 0.9))
    return card


def freeze_card(tint, seed, size=(1024, 176)):
    """Death screen "You were killed by ...": the flat notice card (killer's team tone behind the health cross),
    a faint 死 brushed on its right end."""
    w, h = size
    card = notice_card(tint, seed, size)
    k = art.text_img('死', art.font(art.KANJI, int(h * 0.9)), (226, 226, 220))
    k.putalpha(Image.fromarray((arr(k.getchannel('A')) * 0.1 * 255).astype(np.uint8)))
    card.alpha_composite(k, (w - k.width - 40, (h - k.height) // 2))
    return card


def stat_card(tint, seed, size=(1024, 354)):
    """Death screen record card ("On the bright side... You came close to your record ..."), HUD 266x92: the notice
    card (your team's tone behind the class portrait), an emerald brush rule over the stat line, a faint 記録 (record)
    down its right end."""
    w, h = size
    card = notice_card(tint, seed, size)
    k = art.vertical_text('記録', art.font(art.KANJI, int(h * 0.36)), (226, 226, 220), gap=4)
    k.putalpha(Image.fromarray((arr(k.getchannel('A')) * 0.1 * 255).astype(np.uint8)))
    card.alpha_composite(k, (w - k.width - 40, (h - k.height) // 2))
    y = int(h * 0.635)
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).polygon([(int(w * 0.3), y + 2), (w - 66, y - 4), (w - 70, y + 1), (int(w * 0.3), y + 7)], fill=255)
    glow = arr(m.filter(ImageFilter.GaussianBlur(3)))
    card.alpha_composite(art.solid_with_alpha(EMERALD, np.clip(glow * 1.5, 0, 1) * 0.7))
    card.alpha_composite(art.solid_with_alpha((170, 240, 206), arr(m) * 0.9))
    return card


def countdown_card(seed=423, size=(256, 256)):
    """Match start countdown: a square torn manga panel, speed lines bursting from the digits, emerald screentone
    rising from the corners (a nine-slice image: the rim sits in the corner cells)."""
    w, h = size
    pts = [(12, 16), (w - 10, 8), (w - 16, h - 12), (8, h - 18)]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    g = np.clip(np.hypot(xx / w - 0.5, yy / h - 0.5) * 2.6 - 0.95, 0, 1)
    tone = screentone(np.clip(1 - g * 0.7, 0, 1), period=7, dot_color=(34, 90, 64), paper=(8, 9, 10))
    content = Image.fromarray(np.concatenate([tone, np.full((h, w, 1), 245.)], -1).astype(np.uint8), 'RGBA')
    content.alpha_composite(speed_lines(size, w // 2, h // 2, n=70, seed=seed, alpha=0.3, inner=0.35))
    return panel(size, pts, seed, content=content)


def seal(txt, seed, size=(224, 256)):
    """Bone-paper stamp with the kanji stacked in ink: sits where the stock notice icon was."""
    w, h = size
    pts = [(12, 10), (w - 10, 16), (w - 16, h - 10), (8, h - 16)]
    card = panel(size, pts, seed, fill=(222, 222, 214), edge=BONE, shadow=False)
    if len(txt) == 1:  # single-kanji seals (item meter cards) fill the stamp
        g = art.text_img(txt, art.font(art.KANJI, int(h * 0.7)), INK, stroke=2)
        g.thumbnail((int(w * 0.72), int(h * 0.66)), Image.LANCZOS)
    else:
        g = art.vertical_text(txt, art.font(art.KANJI, int(h * 0.36)), INK, gap=6)
        g.thumbnail((int(w * 0.74), int(h * 0.8)), Image.LANCZOS)
    card.alpha_composite(g, ((w - g.width) // 2, (h - g.height) // 2))
    d = ImageDraw.Draw(card)
    d.line((int(w * 0.2), h - 30, int(w * 0.8), h - 34), fill=EMERALD + (255,), width=5)
    return card


def popup_bg(seed, size=(1024, 650)):
    """HUD Settings popup (HUD 372x236): torn ink sheet, screentone header band, emerald rule under the title."""
    w, h = size
    pts = [(14, 10), (w - 10, 16), (w - 16, h - 10), (8, h - 14)]
    content = rgba(size, (8, 9, 10), 248)
    band = arr(tone_fill((w, int(h * 0.2)), 1.0, (40, 44, 46), period=8, vertical=True, lo=1.0, hi=0.2))
    content.alpha_composite(Image.fromarray((band * 255).astype(np.uint8), 'RGBA'))
    lines = arr(speed_lines(size, w, 0, n=80, seed=seed, alpha=0.07, inner=0.2))
    content.alpha_composite(Image.fromarray((lines * 255).astype(np.uint8), 'RGBA'))
    card = panel(size, pts, seed, content=content)
    card.alpha_composite(rule(int(w * 0.5), 18, thick=5), (int(w * 0.06), int(h * 0.165)))
    return card


def layout_preview(scene, pieces, hover=False, size=(512, 288)):
    """Mini 16:9 screen showing where the health / ammo pieces sit in one layout.
    pieces: [(image, (x, y, w, h) in 853x480 screen units)]."""
    w, h = size
    s = w / 853.33
    im = scene.convert('RGBA').resize(size, Image.LANCZOS)
    im.alpha_composite(art.solid_with_alpha((0, 0, 0), np.full((h, w), 0.35, np.float32)))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        d.line((cx + dx * 4, cy + dy * 4, cx + dx * 10, cy + dy * 10), fill=BONE + (230,), width=2)
    for img, (x, y, bw, bh) in pieces:
        t = img.convert('RGBA').resize((max(1, round(bw * s)), max(1, round(bh * s))), Image.LANCZOS)
        im.alpha_composite(t, (round(x * s), round(y * s)))
    edge = EMERALD if hover else (70, 72, 72)
    d.rectangle((0, 0, w - 1, h - 1), outline=edge + (255,), width=6 if hover else 3)
    return im


def ctf_bar(seed, size=(512, 112)):
    w, h = size
    pts = [(40, 8), (w - 40, 8), (w - 8, h - 10), (8, h - 10)]
    left = tone_fill((w // 2, h), 1.0, (60, 100, 160), vertical=False, lo=1.0, hi=0.35)
    right = tone_fill((w - w // 2, h), 1.0, (170, 56, 60), vertical=False, lo=0.35, hi=1.0)
    c = rgba(size, (8, 9, 10), 240)
    c.alpha_composite(left, (0, 0))
    c.alpha_composite(right, (w // 2, 0))
    im = panel(size, pts, seed, content=c)
    d = ImageDraw.Draw(im)
    d.line((w // 2, 14, w // 2 - 6, h - 16), fill=EMERALD + (255,), width=3)
    return im


def ring(tint, seed, pointer=False, size=256):
    """Torn manga circle for the CTF flag compass (pointer = the little arrow the game rotates)."""
    m = Image.new('L', (size * 3, size * 3), 0)
    d = ImageDraw.Draw(m)
    c, R = size * 1.5, size * 1.5 * 0.78
    d.ellipse((c - R, c - R, c + R, c + R), fill=255)
    if pointer:
        d.polygon([(c - R * 0.28, c - R * 0.9), (c, c - R * 1.22), (c + R * 0.28, c - R * 0.9)], fill=255)
    m = m.resize((size, size), Image.LANCZOS)
    outer, inner = torn(m, seed, grow=4, shrink=5)
    content = tone_fill((size, size), 1.0, tint, period=7)
    base = np.zeros((size, size, 4), np.float32)
    base[..., :3] = np.array(BONE, np.float32) / 255
    base[..., 3] = outer
    c_arr = arr(content)
    base[..., :3] = base[..., :3] * (1 - inner[..., None]) + c_arr[..., :3] * inner[..., None]
    return Image.fromarray((base * 255).clip(0, 255).astype(np.uint8), 'RGBA')


def glyph(stock, size=256):
    """Recolour a dark stock glyph (flag home/dropped/moving) to bone with an ink outline."""
    a = arr(stock.convert('RGBA').resize((size, size), Image.LANCZOS))[..., 3]
    outline = arr(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)))
    im = art.solid_with_alpha((8, 9, 10), outline)
    im.alpha_composite(art.solid_with_alpha(BONE, a))
    return im


def cp_icon(stock, team, seed, size=128):
    """Control point icon: torn ink square, team screentone, the stock icon's bone-coloured symbol kept."""
    tint = {'blu': (60, 100, 160), 'red': (170, 56, 60)}.get(team, (90, 92, 94))
    pts = [(10, 12), (118, 8), (120, 118), (8, 120)]
    im = panel((size, size), pts, seed, content=tone_fill((size, size), 1.0, tint, period=6), shadow=False)
    s = arr(stock.convert('RGBA').resize((size, size), Image.LANCZOS))
    lum = 0.299 * s[..., 0] + 0.587 * s[..., 1] + 0.114 * s[..., 2]
    yy, xx = np.mgrid[0:size, 0:size]
    interior = (xx > 14) & (xx < size - 14) & (yy > 14) & (yy < size - 14)
    sym = np.clip((lum - 0.62) * 8, 0, 1) * s[..., 3] * interior
    im.alpha_composite(art.solid_with_alpha(BONE, sym))
    return im


# ------------------------------------------------------------------ hitmarker, respawn card, menus, objectives
def hitmarker(size=128):
    """Hitmarker: four tapered slashes around the crosshair gap, bone core, emerald glow, ink outline."""
    ss = 4
    S = size * ss
    core = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(core)
    c = S / 2
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        r0, r1, wd = S * 0.16, S * 0.42, S * 0.055
        # a slash along the diagonal, thick at the outer end, needle at the inner end
        ax, ay = c + sx * r0 * 0.7071, c + sy * r0 * 0.7071
        bx, by = c + sx * r1 * 0.7071, c + sy * r1 * 0.7071
        nx, ny = -sy * 0.7071, sx * 0.7071
        d.polygon([(ax, ay), (bx + nx * wd, by + ny * wd), (bx - nx * wd, by - ny * wd)], fill=255)
    core = core.resize((size, size), Image.LANCZOS)
    a = arr(core)
    outline = arr(core.filter(ImageFilter.MaxFilter(7)))
    glow = arr(core.filter(ImageFilter.GaussianBlur(size * 0.05)))
    im = art.solid_with_alpha(EMERALD, np.clip(glow * 2.2, 0, 1) * 0.9)
    im.alpha_composite(art.solid_with_alpha(INK, outline))
    im.alpha_composite(art.solid_with_alpha(EMERALD, arr(core.filter(ImageFilter.MaxFilter(3)))))
    im.alpha_composite(art.solid_with_alpha((226, 250, 238), a))
    return im


def respawn_card(seed=443, size=(1024, 128)):
    """Respawn timer ("Respawn in 5 seconds"): a flat torn ink card, grey screentone on both ends, a thin emerald
    stroke under the text."""
    w, h = size
    pts = [(24, 12), (w - 14, 6), (w - 30, h - 12), (10, h - 8)]
    content = rgba(size, (8, 9, 10), 238)
    for mirror in (False, True):
        zone = arr(tone_fill((int(w * 0.22), h), 1.0, (84, 86, 88), period=7, vertical=True, lo=0.15, hi=1.0))
        fade = np.clip(1.2 - np.linspace(0, 1, zone.shape[1]) * 1.3, 0, 1)
        zone[..., 3] *= (fade[::-1] if mirror else fade)[None, :]
        content.alpha_composite(Image.fromarray((zone * 255).astype(np.uint8), 'RGBA'),
                                (w - zone.shape[1] if mirror else 0, 0))
    card = panel(size, pts, seed, content=content)
    card.alpha_composite(rule(int(w * 0.5), 16, thick=4), (int(w * 0.25), h - 30))
    return card


def menu_bg(seed, size=(1024, 384), header=0.27):
    """Engineer build / destroy and spy disguise menus: torn ink sheet, screentone header band under the title,
    speed lines, emerald rule where the stock divider was."""
    w, h = size
    pts = [(16, 12), (w - 10, 18), (w - 18, h - 10), (8, h - 14)]
    content = rgba(size, (8, 9, 10), 242)
    band = arr(tone_fill((w, int(h * header)), 1.0, (46, 50, 52), period=8, vertical=True, lo=1.0, hi=0.15))
    content.alpha_composite(Image.fromarray((band * 255).astype(np.uint8), 'RGBA'))
    lines = arr(speed_lines(size, int(w * 0.08), int(h * 0.1), n=70, seed=seed, alpha=0.08, inner=0.2))
    content.alpha_composite(Image.fromarray((lines * 255).astype(np.uint8), 'RGBA'))
    return panel(size, pts, seed, content=content)


MENU_ITEM_TONES = {'on': ((46, 150, 104), BONE, 1.0), 'dim': ((60, 62, 64), (120, 122, 122), 0.75),
                   'red': ((110, 30, 38), (200, 150, 150), 1.0)}  # dark: the game writes red text on it


def menu_item(state, seed, size=(256, 272)):
    """One building / class slot of those menus: small torn ink card, state tone rising from the bottom
    (emerald = ready, grey = built / unavailable, crimson = not enough metal)."""
    tint, edge, alpha = MENU_ITEM_TONES[state]
    w, h = size
    pts = [(12, 10), (w - 8, 14), (w - 14, h - 8), (6, h - 12)]
    content = rgba(size, (8, 9, 10), 238)
    # (tone_fill: 0 = dense dots, 1 = plain ink) the crimson slot keeps its top plain ink, where the game writes
    # its red cost and "Not Enough Metal", and only rises from the bottom
    hi, lo = (1.0, 0.35) if state == 'red' else (0.0, 1.0)
    content.alpha_composite(tone_fill((w, h), 1.0, tint, period=7, vertical=True, lo=lo, hi=hi))
    card = panel(size, pts, seed, content=content, edge=edge, shadow=False)
    if alpha < 1:
        card = see_through(card, alpha)
    return card


def menu_key(seed=447, size=(128, 128)):
    """Number key tag under each slot: a small torn emerald-on-bone chip (the number is drawn in ink on top)."""
    w, h = size
    pts = [(14, 16), (w - 12, 10), (w - 16, h - 14), (10, h - 10)]
    return panel(size, pts, seed, fill=(46, 214, 140), edge=BONE, shadow=False)


def escort_strip(seed=449, size=(1024, 128)):
    """Payload: a torn ink strip under the cart track, grey screentone at both ends."""
    w, h = size
    pts = [(30, 14), (w - 16, 8), (w - 34, h - 12), (12, h - 8)]
    content = rgba(size, (8, 9, 10), 225)
    zone = arr(tone_fill((w, h), 1.0, (70, 72, 74), period=8, vertical=True, lo=0.0, hi=0.9))
    content.alpha_composite(Image.fromarray((zone * 255).astype(np.uint8), 'RGBA'))
    return panel(size, pts, seed, content=content)


def cp_rim(seed=451, size=256):
    """Capture progress: a torn ink ring around the game's circular progress bar (the centre stays open)."""
    m = Image.new('L', (size * 3, size * 3), 0)
    d = ImageDraw.Draw(m)
    c = size * 1.5
    R, r = c * 0.9, c * 0.66
    d.ellipse((c - R, c - R, c + R, c + R), fill=255)
    d.ellipse((c - r, c - r, c + r, c + r), fill=0)
    m = m.resize((size, size), Image.LANCZOS)
    outer, inner = torn(m, seed, grow=3, shrink=3)
    base = np.zeros((size, size, 4), np.float32)
    base[..., :3] = np.array(BONE, np.float32) / 255
    base[..., 3] = outer
    base[..., :3] = base[..., :3] * (1 - inner[..., None]) + np.array(INK, np.float32) / 255 * inner[..., None]
    return Image.fromarray((base * 255).clip(0, 255).astype(np.uint8), 'RGBA')
