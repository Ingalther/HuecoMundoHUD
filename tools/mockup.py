"""Renders an approximate 1080p preview of the in-game HUD layout over a screenshot (no game needed)."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HUD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the project folder is the HUD
PREV = sys.argv[2] if len(sys.argv) > 2 else None
W, H = 1920, 1080
S = H / 480
UW = W / S


def thumb(name):
    import struct, numpy as np
    p = os.path.join(HUD, 'materials/vgui/replay/thumbnails/hm', name + '.vtf')
    d = open(p, 'rb').read()
    w, h = struct.unpack_from('<HH', d, 16)
    mips = d[56]
    size = sum(max(1, w >> i) * max(1, h >> i) * 4 for i in range(1, mips))
    a = np.frombuffer(d, np.uint8, w * h * 4, 80 + size).reshape(h, w, 4)[..., [2, 1, 0, 3]]
    return Image.fromarray(a.copy(), 'RGBA')


def ux(v):
    v = str(v)
    if v.startswith('c'):
        return UW / 2 + float(v[1:])
    return (UW - float(v[1:])) if v.startswith('r') else float(v)


def uy(v):
    v = str(v)
    return (480 - float(v[1:])) if v.startswith('r') else float(v)


def put(img, name, x, y, w, h, alpha=255, px=0, py=0):
    t = thumb(name).resize((max(1, round(w * S)), max(1, round(h * S))), Image.LANCZOS)
    if alpha != 255:
        a = t.getchannel('A').point(lambda v: v * alpha // 255)
        t.putalpha(a)
    img.alpha_composite(t, (round((px + ux(x)) * S), round((py + uy(y)) * S)))


def font(tall, var='SemiBold Condensed'):
    f = ImageFont.truetype(r'C:\Windows\Fonts\bahnschrift.ttf', round(tall * S / 1.025))
    f.set_variation_by_name(var)
    return f


def text(img, s, x, y, w, h, tall, color, align='west', italic=True, px=0, py=0, shadow=True):
    f = font(tall)
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    bx, by = (px + ux(x)) * S, (py + uy(y)) * S
    tw = d.textlength(s, font=f)
    asc, desc = f.getmetrics()
    ty = by + (h * S - (asc + desc)) / 2
    tx = bx if align == 'west' else bx + w * S - tw
    if shadow:
        d.text((tx + S * 0.5, ty + S * 0.5), s, font=f, fill=(0, 0, 0, 190))
    d.text((tx, ty), s, font=f, fill=color)
    if italic:
        layer = layer.transform(layer.size, Image.AFFINE, (1, 0.2, -0.2 * (ty + asc), 0, 1, 0), Image.BICUBIC)
    img.alpha_composite(layer)


def main(shot):
    img = Image.open(shot).convert('RGBA').resize((W, H), Image.LANCZOS)
    # blur away the screenshot's own HUD so the mock reads cleanly
    from PIL import ImageFilter
    for box in ((0, 0, 560, 200), (0, 640, 720, 1080), (1480, 600, 1920, 1080), (1400, 40, 1920, 140),
                (660, 950, 1260, 1080)):
        reg = img.crop(box).filter(ImageFilter.GaussianBlur(40))
        img.paste(reg, box[:2])
    d = ImageDraw.Draw(img)
    BONE = (226, 226, 220, 255)
    # player cluster (HudPlayerClass / HudPlayerHealth, full screen), laid out by build.py's own helpers
    import build
    pc, wc, K = build.pc, build.wc, build.CARD_K
    put(img, 'shard_red', *pc(0, 0, 130, build.PLAYER_H))
    put(img, 'hp_band', *pc(*build.BAND))
    for name in ('hp_track', 'hp_fill', 'hp_mask'):
        put(img, name, *pc(*build.GAUGE))
    text(img, '125', *pc(*build.DIGITS), 42 * K, BONE)
    put(img, 'tag_streak', *pc(*build.STREAK))
    # weapon cluster (HudWeaponAmmo)
    wx, py = build.weapon_pos()
    px = ux(wx)
    put(img, 'ammo_blade', *wc(0, 0, build.WEAPON_W, build.WEAPON_H), px=px, py=py)
    text(img, '6', *wc(4, 12, 64, 50), 42 * K, BONE, 'east', px=px, py=py)
    text(img, '32', *wc(67, 30, 40, 26), 19 * K, (122, 124, 124, 255), px=px, py=py)
    # team goal notice
    px, py = UW / 2 - build.NOTICE_W / 2, 65
    bg, icon, seal, labels, rule = build.NOTICES['resource/ui/hudteamgoal.res']
    put(img, 'notice_red', 0, 0, build.NOTICE_W, build.NOTICE_H, px=px, py=py)
    put(img, seal, 12, 12, 52, 58, px=px, py=py)
    put(img, 'notice_rule', *rule, px=px, py=py)
    text(img, 'You are now Defending!', *labels[0][1][:2], labels[0][1][2], 20, 17, BONE, italic=False, px=px, py=py)
    # killfeed rows
    kf = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', round(10 * S * 0.78))
    for i, (a, b, local) in enumerate((('Ulquiorra', 'Sentry Gun (gamer)', False), ('Kisuke', 'Scout', True))):
        y = (8 + i * 18) * S
        wtxt = 330
        x0 = W - 20 - wtxt
        d.rectangle((x0, y, W - 20, y + 15 * S), fill=(18, 58, 42, 225) if local else (6, 6, 8, 200))
        d.text((x0 + 10, y + 5), a, font=kf, fill=(128, 160, 200, 255))
        d.text((x0 + 170, y + 5), b, font=kf, fill=(208, 92, 92, 255))
    # damage number
    text(img, '-86', 'c0', 190, 40, 20, 15, (46, 214, 140, 255), italic=False)
    return img


if __name__ == '__main__':
    out = main(sys.argv[1])
    out.convert('RGB').save(PREV or 'mockup.jpg', quality=90)
