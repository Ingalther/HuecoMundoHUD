"""Generates every texture of the HUD into <out>/materials."""
import os

import numpy as np
from PIL import Image, ImageFilter

import art
from art import ASH, BONE, EMERALD, rgba
from vtf import write_vtf

THUMB = 'materials/vgui/replay/thumbnails/hm'


def vmt(path, basetexture):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('"UnlitGeneric"\n{\n'
                f'\t"$basetexture"\t"{basetexture}"\n'
                '\t"$translucent"\t"1"\n\t"$vertexcolor"\t"1"\n\t"$vertexalpha"\t"1"\n'
                '\t"$no_fullbright"\t"1"\n\t"$ignorez"\t"1"\n}\n')


class Out:
    def __init__(self, root, preview=None):
        self.root = root
        self.preview = preview
        os.makedirs(os.path.join(root, THUMB), exist_ok=True)
        os.makedirs(os.path.join(root, 'materials/console'), exist_ok=True)

    def thumb(self, name, img, mips=True):
        p = os.path.join(self.root, THUMB, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        w, h = img.size
        pw, ph = 1 << (w - 1).bit_length(), 1 << (h - 1).bit_length()
        if (pw, ph) != (w, h):
            # textures must be power-of-two; the panel draws it at the art's own aspect, so a stretch round-trips
            img = img.resize((pw, ph), Image.LANCZOS)
        write_vtf(p + '.vtf', img, alpha=True, mips=mips)
        vmt(p + '.vmt', f'vgui/replay/thumbnails/hm/{name}')
        if self.preview:
            img.save(os.path.join(self.preview, name + '.png'))

    def console(self, name, img):
        p = os.path.join(self.root, 'materials/console', name)
        write_vtf(p + '.vtf', img.convert('RGBA'), alpha=False, mips=False)
        with open(p + '.vmt', 'w', encoding='utf-8') as f:
            f.write('"UnlitGeneric"\n{\n\t"$basetexture"\t"console/%s"\n\t"$vertexcolor"\t"1"\n'
                    '\t"$vertexalpha"\t"1"\n\t"$no_fullbright"\t"1"\n\t"$ignorez"\t"1"\n}\n' % name)
        if self.preview:
            img.save(os.path.join(self.preview, name + '.jpg'), quality=88)


def aura(w, h, seed, mirror=False):
    base = art.brush_stroke(int(w * 0.90), int(h * 0.62), seed, color=(255, 255, 255), alpha=1.0, taper=0.12)
    im = rgba((w, h))
    im.alpha_composite(base, (int(w * 0.05), int(h * 0.19)))
    a = np.asarray(im, np.float32)
    al = Image.fromarray(a[..., 3].astype(np.uint8)).filter(ImageFilter.GaussianBlur(h * 0.09))
    out = art.solid_with_alpha((255, 255, 255), np.asarray(al, np.float32) / 255 * 0.85)
    if mirror:
        out = out.transpose(Image.FLIP_LEFT_RIGHT)
    return out


def emblem():
    """In-game top-left mark: eye + BLEACH / ULQUIORRA."""
    W, H = 1024, 256
    im = rgba((W, H))
    eye = art.ulq_eye(232)
    im.alpha_composite(eye, (8, 12))
    title = art.text_img('ULQUIORRA', art.font(art.SERIF, 92), BONE, tracking=14)
    im.alpha_composite(title, (270, 40))
    # hairline with a fading tail
    line = np.zeros((3, 680), np.float32)
    line[:] = np.clip(np.linspace(1.3, 0, 680), 0, 1) ** 0.8
    im.alpha_composite(art.solid_with_alpha(ASH, line * 0.9), (262, 150))
    kana = art.text_img('ウルキオラ・シファー', art.font(art.KANA, 38), BONE, tracking=6)
    im.alpha_composite(kana, (272, 172))
    num = art.text_img('第4十刃', art.font(art.KANJI, 34), EMERALD, tracking=4)
    im.alpha_composite(num, (272 + kana.width + 28, 176))
    return im


def menu_logo():
    """Main menu title: small BLEACH + moon, large ULQUIORRA, subtitle."""
    W, H = 1024, 256
    im = rgba((W, H))
    small = art.text_img('B L E A C H', art.font(art.SERIF, 34), ASH, tracking=10)
    im.alpha_composite(small, (14, 14))
    moon = art.crescent(16, glow=True, phase=0.55, tilt=-150)
    im.alpha_composite(moon, (14 + small.width + 6, 14 + small.height // 2 - moon.height // 2))
    big = art.text_img('ULQUIORRA', art.font(art.SERIF, 128), BONE, tracking=12)
    im.alpha_composite(big, (8, 62))
    y = 62 + big.height + 26
    sub = art.text_img('CUATRO ESPADA  ·  HUECO MUNDO', art.font('constan.ttf', 28), ASH, tracking=5)
    sub_k = art.text_img('虚圏', art.font(art.KANJI, 30), EMERALD, tracking=4)
    im.alpha_composite(sub, (14, y))
    im.alpha_composite(sub_k, (14 + sub.width + 22, y + sub.height - sub_k.height))
    by = art.text_img('HUD BY INGALTHER ULQUIORRA', art.font('constan.ttf', 16), (110, 112, 110), tracking=4)
    im.alpha_composite(by, (16, min(H - by.height - 2, y + sub.height + 12)))
    return im


def kanji(txt, size, vertical=False):
    f = art.font(art.KANJI, 200)
    g = art.vertical_text(txt, f, BONE, gap=18) if vertical else art.text_img(txt, f, BONE, stroke=2)
    g.thumbnail(size, Image.LANCZOS)
    return art.fit(g, size)


MENU_VARIANTS = ('fullmoon', 'halloween', 'christmas')  # TF2's holiday conditions on the main menu (screens.mainmenu)


def menu_scene(variant=None):
    """The main menu's 16:9 scene as its 2048x1024 texture; variant: one of MENU_VARIANTS."""
    scene = art.hueco_mundo_scene(1920, 1080, variant=variant)
    if variant == 'fullmoon':
        # Ulquiorra's last words beside the moon, pre-rendered (its fonts are not Windows fonts). It is part of the
        # scene, not a panel: the game hides the scene in a match, a panel would float over the game's ESC menu
        import manga
        quote = Image.open(os.path.join(manga.LOGO_DIR, 'moon_quote.png')).convert('RGBA')
        scene = scene.convert('RGBA')
        scene.alpha_composite(quote.resize((270, 360), Image.LANCZOS), (1537, 68))
        scene = scene.convert('RGB')
    return scene.resize((2048, 1024), Image.LANCZOS)


def scene_images(out):
    out.console('background_huecomundo_widescreen', menu_scene())
    sq = art.hueco_mundo_scene(1440, 1080)
    out.console('background_huecomundo', sq.resize((1024, 1024), Image.LANCZOS))
    for v in MENU_VARIANTS:
        out.console(f'background_huecomundo_{v}_widescreen', menu_scene(v))


def _runs(mask_cols, gap):
    """Column runs of a boolean column mask, split where the gap between set columns exceeds gap."""
    cols = np.nonzero(mask_cols)[0]
    runs, start, prev = [], cols[0], cols[0]
    for c in cols[1:]:
        if c - prev > gap:
            runs.append((start, prev))
            start = c
        prev = c
    return runs + [(start, prev)]


def logo_variant(logo, variant):
    """The menu title on TF2's holidays, drawn over the finished title (works on any build of it): the small crescent
    beside BLEACH becomes the full moon (in a green halo with a bat crossing it on Halloween), or the A of ULQUIORRA
    gets a Santa hat (Smissmas)."""
    im = logo.copy()
    a = np.asarray(im)[..., 3] > 200
    if variant in ('fullmoon', 'halloween'):
        top = a[:52]  # the BLEACH line; ULQUIORRA starts lower
        x0, x1 = _runs(top.any(0), 6)[-1]  # the crescent: the last shape right of B L E A C H
        ys, xs = np.nonzero(top[:, x0:x1 + 1])
        xs = xs + x0
        r = 16  # menu_logo draws art.crescent(16)
        # the disc it was cut from: the centres whose radius-r disc covers the whole crescent, averaged
        fits = []
        for cy in np.arange(ys.min() - r, ys.max() + r, 0.5):
            for cx in np.arange(xs.min() - r, xs.max() + r, 0.5):
                fits.append((np.count_nonzero((xs - cx) ** 2 + (ys - cy) ** 2 > (r + 0.7) ** 2), cx, cy))
        least = min(f[0] for f in fits)
        cx = np.mean([f[1] for f in fits if f[0] == least])
        cy = np.mean([f[2] for f in fits if f[0] == least])
        moon = art.crescent(r, phase=None, glow_color=(140, 232, 186) if variant == 'halloween' else (200, 214, 208))
        layer = rgba(im.size)
        layer.alpha_composite(moon, (int(round(cx - moon.width / 2)), int(round(cy - moon.height / 2))))
        # the full disc's glow reaches past the title's top edge: fade it out above the disc instead of cutting it
        top = max(1, int(cy - r))
        la = np.array(layer)
        la[:top, :, 3] = (la[:top, :, 3] * (np.arange(top) / top)[:, None]).astype(np.uint8)
        im.alpha_composite(Image.fromarray(la, 'RGBA'))
        if variant == 'halloween':
            b = art.bat(int(r * 2.3))
            im.alpha_composite(b, (int(round(cx - b.width * 0.42)), int(round(cy - b.height * 0.05))))
    elif variant == 'christmas':
        # on the apex of the last letter, the A: the only letter with free sky above it
        rows = a[55:200]
        x0, x1 = _runs(rows.any(0), 3)[-1]
        apex = np.nonzero(rows[:, x0:x1 + 1].any(1))[0].min()
        ax = x0 + np.mean(np.nonzero(rows[apex:apex + 3, x0:x1 + 1].any(0))[0])
        hat = art.santa_hat(int((x1 - x0) * 0.72)).rotate(-10, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(hat, (int(ax - hat.width * 0.45), int(55 + apex + 12 - hat.height)))
    return im


def panels(out):
    P = art.scalable_panel
    INKF = (10, 11, 12, 238)
    LINE = (58, 60, 60, 255)
    EM = EMERALD + (255,)
    out.thumb('panel', P(INKF, LINE), mips=False)
    out.thumb('panel_opaque', P((10, 11, 12, 255), LINE), mips=False)
    out.thumb('panel_clear', P((0, 0, 0, 150), (40, 42, 42, 200)), mips=False)
    out.thumb('panel_thin', P((0, 0, 0, 120), (70, 72, 72, 255)), mips=False)
    out.thumb('panel_red', P((34, 12, 14, 235), (120, 44, 48, 255)), mips=False)
    out.thumb('panel_red_opaque', P((34, 12, 14, 255), (120, 44, 48, 255)), mips=False)
    out.thumb('panel_blue', P((12, 18, 28, 235), (52, 76, 110, 255)), mips=False)
    out.thumb('panel_blue_opaque', P((12, 18, 28, 255), (52, 76, 110, 255)), mips=False)
    out.thumb('panel_accent', P(INKF, LINE, accent=EM, accent_side='left', accent_px=4), mips=False)
    import manga
    out.thumb('meter_bg', manga.tag(419))  # every stock meter box becomes a torn ink tag
    # main menu buttons: flat ink, hover gets the emerald edge
    out.thumb('btn', P((8, 9, 10, 205), (36, 38, 38, 255)), mips=False)
    out.thumb('btn_hover', P((18, 40, 31, 235), (36, 38, 38, 255), accent=EM, accent_side='left', accent_px=5), mips=False)
    out.thumb('btn_down', P((14, 70, 48, 245), EM, accent=EM, accent_side='left', accent_px=5), mips=False)
    out.thumb('btn_off', P((8, 9, 10, 120), (28, 29, 29, 255)), mips=False)
    # items (tinted by quality colour through the border "color")
    out.thumb('item', P((12, 13, 14, 235), (170, 170, 170, 255)), mips=False)
    out.thumb('item_hover', P((22, 24, 24, 240), (255, 255, 255, 255), border_px=3), mips=False)
    out.thumb('item_plain', P((12, 13, 14, 235), (60, 62, 62, 255)), mips=False)
    out.thumb('item_sel', P((16, 40, 30, 240), EM, border_px=3), mips=False)
    out.thumb('blank', rgba((8, 8)), mips=False)


def gradient(w, h, stops, axis='x', color=(6, 7, 8)):
    """Alpha gradient along one axis; stops = [(pos 0..1, alpha 0..1), ...]."""
    n = w if axis == 'x' else h
    t = np.linspace(0, 1, n)
    a = np.interp(t, [p for p, _ in stops], [v for _, v in stops])
    arr = np.tile(a[None, :], (h, 1)) if axis == 'x' else np.tile(a[:, None], (1, w))
    return art.solid_with_alpha(color, arr)


def sidebar():
    im = gradient(256, 512, [(0, 0.94), (0.72, 0.9), (0.9, 0.55), (1, 0.0)])
    # faint grain so the ink is not flat
    g = art.noise2d(256, 512, 44, scale=32, octaves=3)
    a = np.asarray(im, np.float32)
    a[..., :3] += g[..., None] * 10
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
    return im


def nav(hover):
    w, h = 64, 32
    if not hover:
        im = rgba((w, h))
        d = np.zeros((h, w), np.float32)
        d[h - 1, :] = np.clip(np.linspace(1.2, 0, w), 0, 1) * 0.35
        return art.solid_with_alpha((200, 200, 196), d)
    im = gradient(w, h, [(0, 0.55), (1, 0.0)], color=(18, 70, 50))
    bar = np.zeros((h, w), np.float32)
    bar[:, 0:3] = 1
    im.alpha_composite(art.solid_with_alpha(EMERALD, bar))
    return im


def app_icon(path):
    """Single 256x256 PNG entry: the engine only takes the first image of resource/game.ico."""
    eye = art.ulq_eye(256)
    eye.save(path, format='ICO', sizes=[(256, 256)])


def objective_icons(out, pdir):
    """Control point + CTF flag art. The stock materials are redirected here by vmt overrides (see build.py)."""
    import glob
    import manga
    from vtfread import read_vtf
    src = os.path.join(pdir, 'materials', 'sprites', 'obj_icons')
    for i, f in enumerate(sorted(glob.glob(os.path.join(src, 'icon_obj_*.vtf')))):
        name = os.path.basename(f)[:-4]
        if not any(t in name for t in ('_blu', '_red', '_neutral')) or 'cap_' in name or 'mannhattan' in name:
            continue
        team = 'blu' if '_blu' in name else 'red' if '_red' in name else 'neutral'
        out.thumb('obj/' + name, manga.cp_icon(read_vtf(f), team, 500 + i))
    hud = os.path.join(pdir, 'materials', 'hud')
    for name, tint in (('blue', (60, 100, 160)), ('red', (170, 56, 60)), ('grey', (90, 92, 94)), ('grey_with_red', (120, 70, 72))):
        out.thumb(f'obj/objectives_flagpanel_compass_{name}', manga.ring(tint, 600 + len(name), pointer=True))
        if name in ('blue', 'red'):
            out.thumb(f'obj/objectives_flagpanel_compass_{name}_noarrow', manga.ring(tint, 620 + len(name)))
    for g in ('home', 'home_alt', 'dropped', 'moving', 'moving_alt'):
        out.thumb(f'obj/objectives_flagpanel_ico_flag_{g}',
                  manga.glyph(read_vtf(os.path.join(hud, f'objectives_flagpanel_ico_flag_{g}.vtf'))))


BUILDING_KANJI = {'sentry': '砲', 'dispenser': '補', 'tele_entrance': '入', 'tele_exit': '出', 'sapper': '破'}


def hud_cards(out):
    """In-game HUD: shard, health band, ammo blade, tags, gauge, notices, building cards (no portraits needed)."""
    import manga
    red, blue = (150, 50, 54), (56, 90, 140)
    out.thumb('shard_red', manga.shard(red, 411))
    out.thumb('shard_blue', manga.shard(blue, 411))
    out.thumb('hp_band', manga.hp_band(412))
    out.thumb('ammo_blade', manga.ammo_blade(413))
    out.thumb('tag_streak', manga.tag(414, '殺'))
    # artwork in tools/logos/*.png replaces the procedural drawings (manga.logo)
    out.thumb('sticky_red', manga.logo('sticky_red', fallback=lambda: manga.sticky_icon(red)))
    out.thumb('sticky_blue', manga.logo('sticky_blue', fallback=lambda: manga.sticky_icon(blue)))
    out.thumb('tag_shield_red', manga.tag_with_icon(manga.logo('shield_red', fallback=lambda: manga.targe_icon(red))))
    out.thumb('tag_shield_blue', manga.tag_with_icon(manga.logo('shield_blue',
                                                                fallback=lambda: manga.targe_icon(blue))))
    out.thumb('streak_card', manga.streak_card(), mips=False)  # killstreak splash (nine-slice border)
    out.thumb('meter_metal', manga.tag_with_icon(manga.logo('metal'), crisp=True))  # Engineer metal card
    # ÜberCharge card: wider than the other tags (80x26, build.UBER_W), so its own size keeps the tag and the cross
    out.thumb('meter_uber', manga.tag_with_icon(manga.logo('uber'), size=(704, 160), crisp=True, box=(80, 26)))
    import build  # item meter cards: the item's manga logo on the sticky tag (build.METER_CARDS)
    for fname, (logo, _) in sorted(build.METER_CARDS.items()):
        cw = build.METER_WIDE.get(fname, 58)  # wide cards get their own aspect, so the tag and logo stay true
        out.thumb(build.meter_card_name(fname), manga.tag_with_icon(manga.logo(logo), size=(round(512 * cw / 58), 160),
                                                                   crisp=True, box=(cw, 26)))
    out.thumb('hp_track', manga.hp_track(), mips=False)
    out.thumb('hp_fill', manga.hp_fill(), mips=False)
    out.thumb('hp_mask', manga.hp_mask())
    out.thumb('notice_red', manga.notice_card(red, 416))
    out.thumb('notice_blue', manga.notice_card(blue, 416))
    out.thumb('notif_red', manga.notif_card(red, 421))  # HUD notifications (flag dropped / taken / returned...)
    out.thumb('notif_blue', manga.notif_card(blue, 421))
    out.thumb('notif_ink', manga.notif_card((120, 122, 120), 421))
    # target ID ("Sentry Gun built by ...", "Healer: ..."): the flat notice card, see-through, target's team tone
    # behind the health
    out.thumb('tid_red', manga.see_through(manga.notice_card(red, 424, size=(1024, 176)), 0.35))
    out.thumb('tid_blue', manga.see_through(manga.notice_card(blue, 424, size=(1024, 176)), 0.35))
    out.thumb('tid_ink', manga.see_through(manga.notice_card((120, 122, 120), 424, size=(1024, 176)), 0.35))
    out.thumb('countdown_card', manga.countdown_card())  # match start countdown
    out.thumb('freeze_red', manga.freeze_card(red, 422))  # death screen "You were killed by" (killer's team)
    out.thumb('freeze_blue', manga.freeze_card(blue, 422))
    out.thumb('stat_red', manga.stat_card(red, 425))  # death screen record card (your own team)
    out.thumb('stat_blue', manga.stat_card(blue, 425))
    out.thumb('notice_rule', manga.rule(512, 32, thick=8))
    for name, txt in (('goal', '任務'), ('switch', '移籍'), ('alert', '警告')):
        out.thumb('seal_' + name, manga.seal(txt, 417))
    out.thumb('bld_red', manga.building_card(red, 415))
    out.thumb('bld_blue', manga.building_card(blue, 415))
    for k, ch in BUILDING_KANJI.items():
        out.thumb('bld_k_' + k, manga.building_kanji(ch))


def hud_settings_art(out):
    """Main-menu HUD Settings popup and its layout previews, drawn from the real in-game pieces at their real
    positions (build.LAYOUTS)."""
    import build
    import manga
    import screens
    out.thumb('popup', manga.popup_bg(430, size=(1024, round(1024 * screens.POPUP_H / screens.POPUP_W))))
    scene = art.hueco_mundo_scene(854, 480, menu_shade=False)
    shard, band = manga.shard((56, 90, 140), 411), manga.hp_band(412)
    blade, streak = manga.ammo_blade(413), manga.tag(414, '殺')
    digits = art.text_img('150', art.font(art.SANS, 120), BONE)
    ammo = art.text_img('6', art.font(art.SANS, 120), BONE)
    for name, alt in (('layout_centered', False), ('layout_corners', True)):
        wx, wy = build.weapon_pos(alt)
        wx = 853.33 - float(wx[1:])
        d = build.pc(*build.DIGITS, alt=alt)
        pieces = [(shard, build.pc(0, 0, 130, build.PLAYER_H, alt=alt)),
                  (band, build.pc(*build.BAND, alt=alt)),
                  (digits, (d[0] + 4, d[1] + 12, 26 * digits.width / digits.height, 26)),
                  (streak, build.pc(*build.STREAK, alt=alt)),
                  (blade, (wx, wy, build.WEAPON_W, build.WEAPON_H)),
                  (ammo, (wx + 40, wy + 22, 26 * ammo.width / ammo.height, 26))]
        out.thumb(name, manga.layout_preview(scene, pieces))
        out.thumb(name + '_h', manga.layout_preview(scene, pieces, hover=True))


def extras_art(out):
    """Hitmarker, respawn card, engineer / spy menu cards, payload strip, capture ring rim."""
    import manga
    out.thumb('hitmarker', manga.hitmarker())
    out.thumb('respawn_card', manga.respawn_card())
    out.thumb('menu_bg', manga.menu_bg(453))
    for i, state in enumerate(manga.MENU_ITEM_TONES):
        out.thumb('menu_item_' + state, manga.menu_item(state, 455 + i))
    out.thumb('menu_key', manga.menu_key())
    out.thumb('disguise_card', manga.notice_card((84, 86, 88), 459, size=(1024, 176)))
    out.thumb('escort_strip', manga.escort_strip())
    out.thumb('cp_rim', manga.cp_rim())


def manga_assets(out, pdir):
    """Class / team / scoreboard / menu art, built from the game's own class portraits run through the manga filter."""
    import manga
    from vtfread import read_vtf

    def tex(rel):
        return read_vtf(os.path.join(pdir, 'materials', rel + '.vtf'))

    for i, (btn, por, sel, num, label, kana) in enumerate(manga.CLASSES):
        out.thumb(f'cls_{btn}', manga.class_card(tex(f'vgui/class_portraits/{por}_grey'), num, label, kana, 100 + i))
        out.thumb(f'cls_{btn}_h', manga.class_card(tex(f'vgui/class_portraits/{por}'), num, label, kana, 100 + i, hover=True))
        fig = tex(f'vgui/class_sel_sm_{sel}_red')
        out.thumb(f'inv_{btn}', manga.tall_card(fig, num, kana, 200 + i))
        out.thumb(f'inv_{btn}_a', manga.tall_card(fig, num, kana, 200 + i, active=True))
    allc = tex('vgui/class_portraits/all_class')
    out.thumb('cls_random', manga.class_card(allc, '?', 'RANDOM', 'ランダム', 120))
    out.thumb('cls_random_h', manga.class_card(allc, '?', 'RANDOM', 'ランダム', 120, hover=True))

    blu = [tex('vgui/class_portraits/soldier_blue'), tex('vgui/class_portraits/medic_blue')]
    red = [tex('vgui/class_portraits/heavy'), tex('vgui/class_portraits/pyro')]
    out.thumb('team_blu', manga.team_card(blu, 'BLU', '青', (96, 140, 200), 301))
    out.thumb('team_blu_h', manga.team_card(blu, 'BLU', '青', (96, 140, 200), 301, hover=True))
    out.thumb('team_red', manga.team_card(red, 'RED', '赤', (210, 80, 80), 302))
    out.thumb('team_red_h', manga.team_card(red, 'RED', '赤', (210, 80, 80), 302, hover=True))
    out.thumb('team_auto', manga.small_card('RANDOM', '運', 303))
    out.thumb('team_auto_h', manga.small_card('RANDOM', '運', 303, hover=True))
    out.thumb('team_spec', manga.small_card('SPECTATE', '観', 304))
    out.thumb('team_spec_h', manga.small_card('SPECTATE', '観', 304, hover=True))

    out.thumb('ctf_bar', manga.ctf_bar(405))
    objective_icons(out, pdir)
    out.thumb('score_blue', manga.banner((70, 110, 170), 403))
    out.thumb('score_red', manga.banner((180, 60, 64), 404, mirror=True))
    out.thumb('score_main', manga.score_main())
    out.thumb('win_page', manga.win_page())
    out.thumb('win_seal', manga.seal('勝', 412))
    out.thumb('score_seal_blue', manga.seal('青', 409))
    out.thumb('score_seal_red', manga.seal('赤', 410))
    out.thumb('rule_v', manga.rule_v(), mips=False)
    out.thumb('top_band', manga.top_band())
    out.thumb('portrait_frame', manga.portrait_frame(), mips=False)
    out.thumb('eyes', manga.ulq_eyes())
    out.thumb('lanza', manga.lanza(1024, 256))
    out.thumb('speed', manga.speed_lines((1024, 512), 512, 256, alpha=0.35))
    out.thumb('tone', manga.tone_tile(), mips=False)


def build(root, preview=None, portraits=None):
    out = Out(root, preview)
    panels(out)
    hud_cards(out)
    hud_settings_art(out)
    extras_art(out)
    out.thumb('emblem', emblem())
    logo = menu_logo()
    out.thumb('logo', logo)
    for v in MENU_VARIANTS:
        out.thumb('logo_' + v, logo_variant(logo, v))
    out.thumb('aura_l', aura(512, 128, 21))
    out.thumb('aura_r', aura(512, 128, 22, mirror=True))
    out.thumb('wing_l', art.bat_wing(512, 256, seed=5))
    out.thumb('wing_r', art.bat_wing(512, 256, seed=6, flip=True))
    out.thumb('kanji_murcielago', kanji('黒翼大魔', (64, 256), vertical=True))
    out.thumb('eye', art.ulq_eye(256))
    out.thumb('sidebar', sidebar())
    out.thumb('nav', nav(False), mips=False)
    out.thumb('nav_hover', nav(True), mips=False)
    out.thumb('header', gradient(32, 128, [(0, 0.96), (0.55, 0.8), (1, 0)], axis='y'))
    out.thumb('footer', gradient(32, 128, [(0, 0), (0.35, 0.8), (1, 0.96)], axis='y'))
    out.thumb('shade_left', gradient(256, 32, [(0, 0.85), (0.5, 0.55), (1, 0)]))
    out.thumb('shade_full', gradient(32, 32, [(0, 0.55), (1, 0.55)]), mips=False)
    out.thumb('kanji_huecomundo', kanji('虚圏', (64, 128), vertical=True))
    os.makedirs(os.path.join(root, 'resource'), exist_ok=True)
    app_icon(os.path.join(root, 'resource', 'game.ico'))
    if portraits:
        manga_assets(out, portraits)
    scene_images(out)
