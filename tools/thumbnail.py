"""Store / GitHub thumbnail (1920x1080): the Hueco Mundo scene, a torn manga title panel, the in-game HUD pieces.

    python thumbnail.py [out.png]
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import art
import manga
from art import BONE, EMERALD, INK, ASH

W, H = 1920, 1080


def shade(im, alpha):
    im.alpha_composite(art.solid_with_alpha((0, 0, 0), np.full((im.height, im.width), alpha, np.float32)))


def fit_text(txt, font, max_w, start, color, **kw):
    size = start
    while True:
        im = art.text_img(txt, art.font(font, size), color, **kw)
        if im.width <= max_w or size < 20:
            return im
        size -= 4


def italic(im, k=0.2):
    return im.transform(im.size, Image.AFFINE, (1, k, -im.height * k / 2, 0, 1, 0), Image.BICUBIC)


def title_panel():
    """Torn ink panel, speed lines bursting from the left, BLEACH / HUECO MUNDO in bone serif, HUD in emerald,
    虚圏 down the right edge."""
    w, h = 1180, 470
    pts = [(40, 30), (w - 20, 8), (w - 60, h - 26), (12, h - 6)]
    content = art.rgba((w, h), INK, 238)
    content.alpha_composite(manga.speed_lines((w, h), 90, h // 2, n=110, seed=61, alpha=0.14, inner=0.15))
    tone = manga.tone_fill((w, int(h * 0.26)), 1.0, (40, 110, 80), period=9, vertical=True, lo=1.0, hi=0.3)
    content.alpha_composite(tone, (0, h - tone.height))
    card = manga.panel((w, h), pts, 63, content=content)

    x0, text_w = 100, 850
    small = art.text_img('B L E A C H', art.font(art.SERIF, 40), ASH, tracking=12)
    card.alpha_composite(small, (x0 + 6, 54))
    moon = art.crescent(18, glow=True, phase=0.55, tilt=-150)
    card.alpha_composite(moon, (x0 + 16 + small.width, 54 + small.height // 2 - moon.height // 2))
    big = fit_text('HUECO MUNDO', art.SERIF_B, text_w, 140, BONE, tracking=8)
    card.alpha_composite(big, (x0, 112))
    y = 112 + big.height + 10
    hud = italic(art.text_img('HUD', art.font('bahnschrift.ttf', 132), EMERALD, tracking=10))
    card.alpha_composite(hud, (x0, y))
    card.alpha_composite(manga.rule(w - 80 - 130 - (x0 + hud.width + 30) - 40, 22, thick=7), (x0 + hud.width + 30, y + 40))
    k = art.vertical_text('虚圏', art.font(art.KANJI, 130), EMERALD, gap=12)
    kx = w - k.width - 80
    card.alpha_composite(k, (kx, (h - k.height) // 2 - 10))
    sx = x0 + hud.width + 34
    sub = fit_text('ULQUIORRA  ·  TF2 HUD', 'constan.ttf', kx - sx - 30, 34, ASH, tracking=6)
    card.alpha_composite(sub, (sx, y + 76))
    return card


def hud_pieces(im):
    """The real in-game pieces, big, bottom corners: model triangle + health band, ammo blade."""
    shard = manga.shard((56, 90, 140), 411).resize((330, 317), Image.LANCZOS)
    im.alpha_composite(shard, (70, H - 330))
    band = manga.hp_band(412).resize((330, 133), Image.LANCZOS)
    im.alpha_composite(band, (300, H - 220))
    hp = art.text_img('125', art.font('bahnschrift.ttf', 118), BONE, stroke=0)
    hp = italic(hp)
    im.alpha_composite(hp, (330, H - 222))
    blade = manga.ammo_blade(413).resize((380, 223), Image.LANCZOS)
    im.alpha_composite(blade, (W - 470, H - 300))
    clip = art.text_img('6', art.font('bahnschrift.ttf', 130), BONE)
    clip = italic(clip)
    im.alpha_composite(clip, (W - 380, H - 262))
    res = art.text_img('32', art.font('bahnschrift.ttf', 60), ASH)
    im.alpha_composite(res, (W - 380 + clip.width + 6, H - 262 + clip.height - res.height - 10))
    hit = manga.hitmarker().resize((150, 150), Image.LANCZOS)
    im.alpha_composite(hit, (W // 2 - 75, 770))


def main(out):
    im = art.hueco_mundo_scene(W, H, menu_shade=False).convert('RGBA')
    shade(im, 0.25)
    eye = art.ulq_eye(470)
    im.alpha_composite(eye, (W - 560, 120))
    panel = title_panel()
    panel = panel.rotate(2.5, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(panel, (110, 110))
    hud_pieces(im)
    vig = np.clip(np.hypot(*np.mgrid[-1:1:H * 1j, -1:1:W * 1j]) - 0.95, 0, 1) * 0.8
    im.alpha_composite(art.solid_with_alpha((0, 0, 0), vig.astype(np.float32)))
    im.convert('RGB').save(out, quality=95)
    print('thumbnail ->', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'thumbnail.png'))
