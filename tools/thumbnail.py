"""Store / GitHub thumbnail (1920x1080): a clean title card, no HUD pieces.

    python thumbnail.py [style] [out.png]      style: moon (default), eye, paper
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

import art
import manga
from art import BONE, EMERALD, INK

W, H = 1920, 1080


def fill(color, alpha=1.0):
    return art.solid_with_alpha(color, np.full((H, W), alpha, np.float32))


def centered(im, layer, y, x=None):
    im.alpha_composite(layer, ((W - layer.width) // 2 if x is None else x, y))


def wordmark(color=BONE, accent=EMERALD, size=150):
    """HUECO MUNDO in wide-tracked serif, a thin rule, HUD small and spaced below it."""
    title = art.text_img('HUECO  MUNDO', art.font(art.SERIF, size), color, tracking=int(size * 0.18))
    hud = art.text_img('H U D', art.font(art.SERIF_B, int(size * 0.42)), accent, tracking=int(size * 0.2))
    w = max(title.width, hud.width)
    out = art.rgba((w, title.height + hud.height + 70))
    out.alpha_composite(title, ((w - title.width) // 2, 0))
    line = np.zeros((2, int(w * 0.5)), np.float32)
    line[:] = np.sin(np.linspace(0, np.pi, line.shape[1])) ** 0.6
    out.alpha_composite(art.solid_with_alpha(accent, line * 0.8), ((w - line.shape[1]) // 2, title.height + 26))
    out.alpha_composite(hud, ((w - hud.width) // 2, title.height + 56))
    return out


def moon():
    """Night over Hueco Mundo: the scene (its crescent moon, the dunes) sunk in black, the wordmark in the sky."""
    im = art.hueco_mundo_scene(W, H, menu_shade=False).convert('RGBA')
    im = im.filter(ImageFilter.GaussianBlur(2))
    im.alpha_composite(fill((0, 0, 0), 0.55))
    yy = np.linspace(0, 1, H)[:, None].repeat(W, 1).astype(np.float32)
    im.alpha_composite(art.solid_with_alpha((0, 0, 0), np.clip(1.2 - yy * 1.6, 0, 1) * 0.6))
    centered(im, wordmark(), 300)
    return im


def eye():
    """Ink black, Ulquiorra's eye on the left with its emerald tear, the wordmark on the right."""
    im = fill(INK)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    glow = np.exp(-(((xx - 480) / 520) ** 2 + ((yy - 540) / 420) ** 2)) * 0.18
    im.alpha_composite(art.solid_with_alpha((20, 90, 62), glow.astype(np.float32)))
    e = art.ulq_eye(620)
    im.alpha_composite(e, (170, (H - e.height) // 2))
    wm = wordmark(size=92)
    im.alpha_composite(wm, (860 + (980 - wm.width) // 2, (H - wm.height) // 2))
    return im


def paper():
    """Bone manga paper with a soft screentone, a huge faint 虚圏 behind, the wordmark in ink."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(1 - np.hypot(xx / W - 0.5, (yy / H - 0.5) * 0.7) * 1.1, 0, 1)
    tone = manga.screentone(np.clip(0.55 + g * 0.45, 0, 1), period=10, dot_color=(190, 188, 180),
                            paper=(226, 224, 216))
    im = Image.fromarray(np.concatenate([tone, np.full((H, W, 1), 255.)], -1).astype(np.uint8), 'RGBA')
    k = art.text_img('虚圏', art.font(art.KANJI, 700), INK)
    k.putalpha(Image.fromarray((manga.arr(k.getchannel('A')) * 0.08 * 255).astype(np.uint8)))
    centered(im, k, (H - k.height) // 2)
    centered(im, wordmark(color=INK, accent=(20, 150, 98)), 460)
    return im


STYLES = {'moon': moon, 'eye': eye, 'paper': paper}


def main(style='moon', out=None):
    out = out or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'thumbnail.png')
    STYLES[style]().convert('RGB').save(out, quality=95)
    print('thumbnail ->', out)


if __name__ == '__main__':
    main(*sys.argv[1:3])
