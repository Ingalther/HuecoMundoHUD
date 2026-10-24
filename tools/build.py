"""Builds the Hueco Mundo HUD.

    python build.py                 -> rebuilds the HUD in the project folder itself
    python build.py --install       -> also installs it into tf/custom

The project folder is the HUD: resource/, scripts/, materials/ and info.vdf sit at its root, so the folder (a
GitHub ZIP like "huecomundo-hud-main" or a clone) works when dropped straight into tf/custom. tools/, docs/ and
update.bat are ignored by the game. If the project folder already is in tf/custom, --install builds in place.

The HUD is derived from the game's own current UI files (extracted from tf2_misc_dir.vpk at build time),
re-skinned through the scheme and patched where the layout changes. Only files that differ from stock are shipped.
"""
import colorsys
import os
import re
import shutil
import sys
import tempfile

import kv
import vpk
import build_art
import screens

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)  # the project folder is the HUD
HUD_NAME = 'huecomundo-hud'
HUD_PARTS = ('resource', 'scripts', 'materials', 'cfg', 'info.vdf')  # what the build owns inside the project folder
IN_CUSTOM = os.path.basename(os.path.dirname(OUT)).lower() == 'custom'
if IN_CUSTOM:  # the game folder is known for sure: <tf>/custom/<this folder>
    vpk.TF = os.path.dirname(os.path.dirname(OUT))
T = 'replay/thumbnails/hm/'
CARD_K = 1.0  # draw scale of the in-game player / weapon clusters (see "in-game clusters")

# ------------------------------------------------------------------ palette
C = {
    'HM_Bone': '226 226 220 255',
    'HM_BoneDim': '226 226 220 150',
    'HM_BoneMid': '184 186 180 255',
    'HM_Ash': '122 124 124 255',
    'HM_AshDim': '122 124 124 120',
    'HM_Ink': '8 9 10 255',
    'HM_InkSoft': '8 9 10 200',
    'HM_Shadow': '0 0 0 190',
    'HM_Emerald': '46 214 140 255',
    'HM_EmeraldDim': '46 214 140 110',
    'HM_EmeraldDeep': '18 60 44 255',
    'HM_Crimson': '222 58 72 255',
    'HM_Amber': '255 196 48 255',
    'HM_TeamRed': '208 92 92 255',
    'HM_TeamBlue': '128 160 200 255',
}

SCHEME_COLORS = {
    'Orange': '70 206 146 255', 'OrangeDim': '70 206 146 120', 'LightOrange': '90 190 150 128',
    'GoalOrange': '90 220 160 255', 'TFOrange': '24 70 50 255', 'Purple': '96 110 104 255',
    'White': '232 232 228 255', 'Yellow': '226 226 220 255', 'TransparentYellow': '226 226 220 140',
    'BrightYellow': '226 226 220 255', 'GreenSolid': '46 214 140 255',
    'Black': '10 10 12 255', 'TransparentBlack': '4 4 5 215', 'TransparentLightBlack': '0 0 0 110',
    'FooterBGBlack': '8 8 10 255',
    'HUDBlueTeam': '96 124 160 127', 'HUDRedTeam': '164 70 72 127', 'HUDSpectator': '110 112 112 127',
    'HUDBlueTeamSolid': '96 124 160 255', 'HUDRedTeamSolid': '164 70 72 255',
    'HUDDeathWarning': '222 58 72 255', 'HudOffWhite': '206 206 200 255', 'HudBlack': '16 16 18 255',
    'HudPanelForeground': '12 12 14 200', 'HudPanelBackground': '12 12 14 200', 'HudPanelBorder': '255 255 255 40',
    'HudProgressBarActive': '226 226 220 255', 'HudProgressBarInActive': '60 62 62 255',
    'HudProgressBarActiveLow': '222 58 72 255', 'HudProgressBarInActiveLow': '222 58 72 99',
    'HudTimerProgressActive': '226 226 220 255', 'HudTimerProgressInActive': '28 28 30 255',
    'HudTimerProgressWarning': '222 58 72 255', 'HudTrainingHint': '46 214 140 255',
    'TanDark': '112 114 114 255', 'TanLight': '226 226 220 255', 'TanDarker': '14 14 16 255',
    'StoreDarkTan': '60 62 62 255', 'StoreGreen': '30 110 76 255', 'SaleGreen': '30 110 76 255',
    'LowHealthRed': '222 58 72 255', 'ProgressOffWhite': '226 226 220 255', 'ProgressBackground': '255 255 255 36',
    'HealthBgGrey': '36 36 38 255', 'ProgressOffWhiteTransparent': '226 226 220 128',
    'LabelDark': '12 12 14 255', 'LabelTransparent': '18 18 20 200', 'BuildMenuActive': '226 226 220 255',
    'MatchmakingDialogTitleColor': '226 226 220 255', 'MatchmakingMenuItemBackground': '12 12 14 255',
    'MatchmakingMenuItemBackgroundActive': '24 70 50 255', 'MatchmakingMenuItemTitleColor': '226 226 220 255',
    'MatchmakingMenuItemDescriptionColor': '160 162 160 255', 'HTMLBackground': '14 14 16 255',
    'ItemAttribLevel': '112 114 114 255', 'ItemAttribNeutral': '226 226 220 255', 'ItemFlags': '112 114 114 255',
    'LightRed': '180 64 70 255', 'LighterRed': '200 80 86 255', 'LighterDarkBrown': '22 22 24 255',
    'DarkBrown': '12 12 14 255',
    'UpgradeDefaultFg': '60 62 62 255', 'UpgradeDefaultBg': '80 82 82 255',
    'UpgradeArmedFg': '24 90 62 255', 'UpgradeArmedBg': '46 170 112 255',
    'UpgradeDepressedFg': '24 100 70 255', 'UpgradeDepressedBg': '56 190 126 255',
    'UpgradeSelectedFg': '24 100 70 255', 'UpgradeSelectedBg': '56 190 126 255',
    'UpgradeDisabledFg': '40 40 42 255', 'UpgradeDisabledBg': '52 52 54 255',
}
KEEP_COLOR = re.compile(r'Quality|Rarity|PartyMember|Halloween|Quest|ItemSet|ItemIsotope|ItemBundle|ItemLimited|'
                        r'Attrib(Positive|Negative)|Disguise|Team(Red|Blue|Spec)|Credits|ForTesting', re.I)


def retint(val):
    """Tan / brown / orange family -> neutral ash or emerald. Everything else untouched."""
    m = re.fullmatch(r'\s*(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})(?:\s+(\d{1,3}))?\s*', val)
    if not m:
        return val
    r, g, b = (int(m.group(i)) for i in (1, 2, 3))
    if max(r, g, b) > 255:
        return val
    a = m.group(4)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    hue = h * 360
    if not (10 <= hue <= 52 and s >= 0.07):
        return val
    if s > 0.55 and v > 0.5:
        k = min(1.0, v / 0.84)
        nr, ng, nb = (round(c * k) for c in (46, 214, 140))
    else:
        l = round(0.299 * r + 0.587 * g + 0.114 * b)
        l = round(l * 0.92)  # a touch colder / darker
        nr, ng, nb = l, min(255, l + 1), min(255, l + 1)
    return f'{nr} {ng} {nb}' + (f' {a}' if a is not None else '')


# ------------------------------------------------------------------ fonts
FONT_REMAP = {
    'tf2 build': 'Bahnschrift SemiBold Condensed',
    'tf2 secondary': 'Bahnschrift SemiCondensed',
    'tf2': 'Bahnschrift SemiCondensed',
    'tf2 professor': 'Constantia',
}


def font_block(name, tall, weight=400, italic=0, outline=0, dropshadow=0, antialias=1):
    return [['1', [['name', name, None], ['tall', str(tall), None], ['weight', str(weight), None],
                   ['additive', '0', None], ['antialias', str(antialias), None], ['italic', str(italic), None],
                   ['outline', str(outline), None], ['dropshadow', str(dropshadow), None]], None]]


HM_FONTS = {
    'HM_Health': font_block('Bahnschrift SemiBold Condensed', 40, 600, italic=1),
    'HM_Ammo': font_block('Bahnschrift SemiBold Condensed', 40, 600, italic=1),
    'HM_AmmoSmall': font_block('Bahnschrift SemiBold Condensed', 18, 600, italic=1),
    # damage numbers: bold italic manga lettering with an ink outline, big hits bigger
    'HM_Damage': font_block('Bahnschrift Bold Condensed', 21, 800, italic=1, outline=1),
    'HM_DamageBig': font_block('Bahnschrift Bold Condensed', 32, 800, italic=1, outline=1),
    # kill feed: manga SFX lettering (bold condensed italic, ink outline so team colours read on ink and paper)
    'HM_Killfeed': font_block('Bahnschrift SemiBold Condensed', 12, 600, italic=1, outline=1),
    'HM_Small': font_block('Bahnschrift SemiCondensed', 8, 400),
    'HM_Menu': font_block('Bahnschrift SemiCondensed', 12, 400),
    'HM_Title': font_block('Constantia', 20, 400),
    'HM_ScoreBig': font_block('Bahnschrift SemiBold Condensed', 40, 600),
    'HM_Streak': font_block('Bahnschrift SemiBold Condensed', 26, 600, italic=1),
    'HM_HealthBig': font_block('Bahnschrift SemiBold Condensed', 40, 600, italic=1),
    'HM_Reserve': font_block('Bahnschrift SemiBold Condensed', 21, 600, italic=1),
    'HM_HealthHuge': font_block('Bahnschrift SemiBold Condensed', round(42 * CARD_K), 600, italic=1),
    'HM_ReserveBig': font_block('Bahnschrift SemiBold Condensed', round(19 * CARD_K), 600, italic=1),
    'HM_StreakSmall': font_block('Bahnschrift SemiBold Condensed', round(16 * CARD_K), 600, italic=1),
    'HM_Sticky': font_block('Bahnschrift SemiBold Condensed', 20, 600, italic=1),
    'HM_Metal': font_block('Bahnschrift SemiBold Condensed', round(13 * CARD_K), 600, italic=1),
    'HM_NoticeTitle': font_block('Bahnschrift SemiBold Condensed', 17, 600),
    'HM_NoticeBody': font_block('Bahnschrift SemiCondensed', 11, 400),
    'HM_SpecHealth': font_block('Bahnschrift SemiBold Condensed', 10, 600, outline=1),
    # spectator key hints / tip / map name: outlined, they float over the map now that the black bars are gone
    'HM_SpecHint': font_block('Bahnschrift SemiCondensed', 10, 500, outline=1),
    'HM_SpecMap': font_block('Bahnschrift SemiBold Condensed', 14, 600, outline=1),
}


def scalable_border(image, corner=8, draw=2, color=None, draw_h=None):
    b = [['bordertype', 'scalable_image', None], ['backgroundtype', '2', None], ['image', 'replay/thumbnails/hm/' + image, None],
         ['src_corner_height', str(corner), None], ['src_corner_width', str(corner), None],
         ['draw_corner_width', str(draw), None], ['draw_corner_height', str(draw if draw_h is None else draw_h), None]]
    if color:
        b.append(['color', color, None])
    return b


HM_BORDERS = {
    'HM_Nav': scalable_border('nav', 4, 2),
    'HM_NavArmed': scalable_border('nav_hover', 4, 2),
    'HM_Frame': scalable_border('panel_thin'),
    'HM_ScoreBG': scalable_border('panel'),
    'HM_ScoreMain': scalable_border('score_main', 0, 0),  # whole-image borders: the art stretched over the panel
    'HM_TornTag': scalable_border('meter_bg', 0, 0),
    'HM_TopBand': scalable_border('top_band', 0, 0),
    'HM_StreakCard': scalable_border('streak_card', 40, 4, draw_h=3),  # only as tall as its text; text starts 5 in
    'HM_RespawnCard': scalable_border('respawn_card', 0, 0),  # the respawn label's own border (patch_spectator)
}
HM_BORDERS['HM_Card_none'] = scalable_border('blank', 0, 0)
for _c in screens.CARD_BORDERS:  # whole-image borders: zero corners stretch the art over the button
    HM_BORDERS[f'HM_Card_{_c}'] = scalable_border(_c, 0, 0)
    HM_BORDERS[f'HM_Card_{_c}_h'] = scalable_border(_c + '_h', 0, 0)


# ------------------------------------------------------------------ borders
def border_image(name, has_color):
    n = name.lower()
    rules = [
        (('mainmenubuttondepressedarmed', 'mainmenubuttonarmed', 'mainmenuminibuttonarmed'), 'btn_hover'),
        (('mainmenubuttondepressed',), 'btn_down'),
        (('mainmenubuttondisabled',), 'btn_off'),
        (('mainmenubuttondefault', 'mainmenuminibuttondefault'), 'btn'),
        (('notificationhighpriority', 'replayhighlightborder'), 'panel_accent'),
        (('mainmenubgborder', 'mainmenuhighlightborder', 'traininresultsbg', 'trainingresultsbg', 'notificationdefault', 'loadoutitempopupborder',
          'graydialogborder', 'replaygraydialogborder', 'replaydefaultborder', 'queststatusborder', 'replayballoonborder'), 'panel'),
        (('redbgopaque', 'redbgmoreopaque', 'replayfatlineborderredbgopaque'), 'panel_red_opaque'),
        (('redbg', 'redwiththinborder'), 'panel_red'),
        (('bluebgopaque', 'bluebgmoreopaque'), 'panel_blue_opaque'),
        (('bluebg', 'bluewiththinborder'), 'panel_blue'),
        (('clearbg',), 'panel_clear'),
        (('tffatlineborderopaque', 'replayfatlineborderopaque'), 'panel_opaque'),
        (('tffatlineborder',), 'panel'),
        (('thinlineborder',), 'panel_thin'),
        (('loadoutitemmouseoverborder',), 'item_hover'),
        (('outlinedgreybox',), 'item_sel'),
        (('outlineddullgreybox', 'econitemborder'), 'item_plain'),
    ]
    for keys, img in rules:
        if any(n.startswith(k) or n == k or k in n for k in keys):
            return img
    if n.startswith('backpackitem'):
        if 'selected' in n:
            return 'item_sel'
        if 'mouseover' in n:
            return 'item_hover'
        if has_color:
            return 'item'
        return 'item_plain'
    return None


def retint_scheme(src_text):
    """SourceScheme: only its colours move from tan to ash / emerald."""
    root = kv.parse(src_text)
    scheme = kv.find(root, 'Scheme')
    for section in ('Colors', 'BaseSettings'):
        for ent in kv.walk(kv.find(scheme, section) or []):
            if not isinstance(ent[1], list):
                ent[1] = retint(ent[1])
    return kv.dump(root) + '\n'


def build_scheme(src_text):
    root = kv.parse(src_text)
    scheme = kv.find(root, 'Scheme')
    colors = kv.find(scheme, 'Colors')
    for ent in colors:
        k = ent[0]
        if isinstance(ent[1], list):
            continue
        if k in SCHEME_COLORS:
            ent[1] = SCHEME_COLORS[k]
        elif not KEEP_COLOR.search(k):
            ent[1] = retint(ent[1])
    for k, v in C.items():
        kv.set(colors, k, v)

    base = kv.find(scheme, 'BaseSettings')
    for ent in kv.walk(base):
        if not isinstance(ent[1], list):
            ent[1] = retint(ent[1])
    kv.setmany(base, **{
        'Button.ArmedBgColor': 'HM_EmeraldDeep', 'Button.SelectedBgColor': 'HM_EmeraldDeep',
        'Button.DepressedBgColor': 'HM_Emerald', 'Button.DepressedTextColor': 'HM_Ink',
        'Econ.Button.ArmedBgColor': 'HM_EmeraldDeep', 'Econ.Button.DepressedBgColor': 'HM_Emerald',
        'Econ.Button.DepressedFgColor': 'HM_Ink', 'Econ.Button.BgColor': '24 25 26 255',
        'Button.BgColor': '24 25 26 255', 'Button.TextColor': 'HM_Bone', 'Button.ArmedTextColor': 'HM_Bone',
        'CheckButton.TextColor': 'HM_Bone', 'CheckButton.SelectedTextColor': 'HM_Bone',
        'CheckButton.Border1': 'HM_Ash', 'CheckButton.Border2': 'HM_Ash', 'CheckButton.Check': 'HM_Emerald',
        'CheckButton.HighlightFgColor': 'HM_Emerald',
        'ListPanel.SelectedBgColor': 'HM_EmeraldDeep', 'ListPanel.SelectedOutOfFocusBgColor': 'HM_EmeraldDeep',
        'ListPanel.SelectedTextColor': 'HM_Bone', 'SectionedListPanel.SelectedBgColor': 'HM_EmeraldDeep',
        'SectionedListPanel.SelectedTextColor': 'HM_Bone', 'SectionedListPanel.OutOfFocusSelectedTextColor': 'HM_Bone',
        'RichText.SelectedBgColor': 'HM_EmeraldDeep', 'Tooltip.TextColor': 'HM_Bone', 'Tooltip.BgColor': 'HM_Ink',
        'Menu.ArmedTextColor': 'HM_Ink', 'Menu.ArmedBgColor': 'HM_Emerald', 'Menu.BgColor': '8 9 10 240',
        'Frame.BgColor': '8 9 10 235', 'Frame.OutOfFocusBgColor': '8 9 10 235',
        'TextEntry.SelectedBgColor': 'HM_EmeraldDeep', 'TextEntry.CursorColor': 'HM_Emerald',
        'Slider.NobColor': 'HM_Emerald', 'Slider.TrackColor': '30 31 32 255',
        'ScrollBarSlider.FgColor': 'HM_Ash', 'ScrollBarButton.FgColor': 'HM_Ash',
        'ItemColor': '46 214 140 200', 'MenuColor': 'HM_Bone', 'VguiScreenCursor': 'HM_Emerald',
        'SelectionNumberFg': 'HM_Bone', 'SelectionTextFg': 'HM_Bone',
    })

    fonts = kv.find(scheme, 'Fonts')
    for fnt in fonts:
        if not isinstance(fnt[1], list):
            continue
        for sub in fnt[1]:
            if isinstance(sub[1], list):
                for e in sub[1]:
                    if e[0].lower() == 'name' and e[1].lower() in FONT_REMAP:
                        e[1] = FONT_REMAP[e[1].lower()]
    for name, blk in HM_FONTS.items():
        kv.remove(fonts, name)
        fonts.append([name, blk, None])

    borders = kv.find(scheme, 'Borders')
    changed = 0
    for b in borders:
        if not isinstance(b[1], list):
            continue
        body = b[1]
        if (kv.get(body, 'bordertype') or '').lower() != 'scalable_image':
            continue
        img = border_image(b[0], kv.get(body, 'color') is not None)
        if not img:
            continue
        kv.set(body, 'image', T + img)
        item = img.startswith('item')
        kv.set(body, 'src_corner_height', '8')
        kv.set(body, 'src_corner_width', '8')
        kv.set(body, 'draw_corner_width', '3' if item else '2')
        kv.set(body, 'draw_corner_height', '3' if item else '2')
        if img == 'item_sel':
            kv.remove(body, 'color')
        changed += 1
    for name in ('MainMenuButtonGlow', 'MainMenuButtonGlow2'):  # orange glow behind highlighted menu buttons
        blk = kv.find(borders, name)
        if blk is not None:
            kv.set(blk, 'color', '46 214 140 255')
    for name, blk in HM_BORDERS.items():
        kv.remove(borders, name)
        borders.append([name, blk, None])
    print(f'  scheme: {changed} borders re-skinned')
    return '\n'.join([kv.dump(root), ''])


# ------------------------------------------------------------------ generic res re-skin
IMAGE_MAP = {
    '../hud/color_panel_brown': T + 'panel', '../hud/color_panel_brown_opaque': T + 'panel_opaque',
    '../hud/tournament_panel_brown': T + 'panel_thin',
    '../hud/color_panel_red': T + 'panel_red', '../hud/color_panel_red_opaque': T + 'panel_red_opaque',
    '../hud/color_panel_red_more_opaque': T + 'panel_red_opaque',
    '../hud/color_panel_blu': T + 'panel_blue', '../hud/color_panel_blu_opaque': T + 'panel_blue_opaque',
    '../hud/color_panel_blu_more_opaque': T + 'panel_blue_opaque',
    '../hud/color_panel_clear': T + 'panel_clear', '../hud/notification_black': T + 'panel_clear',
    '../hud/death_panel_red_bg': T + 'panel_red', '../hud/death_panel_blue_bg': T + 'panel_blue',
    '../hud/score_panel_red_bg': T + 'panel_red', '../hud/score_panel_blue_bg': T + 'panel_blue',
    '../hud/score_panel_red_bg_solid': T + 'panel_red_opaque', '../hud/score_panel_blue_bg_solid': T + 'panel_blue_opaque',
    '../hud/character_red_bg': T + 'blank', '../hud/character_blue_bg': T + 'blank',
    '../hud/character_red_bg_lodef': T + 'blank', '../hud/character_blue_bg_lodef': T + 'blank',
    '../hud/character_red_bg_clipped': T + 'blank', '../hud/character_blue_bg_clipped': T + 'blank',
    '../hud/character_red_bg_lodef_clipped': T + 'blank', '../hud/character_blue_bg_lodef_clipped': T + 'blank',
    '../hud/ammo_red_bg': T + 'blank', '../hud/ammo_blue_bg': T + 'blank',
    '../hud/ammo_red_bg_lodef': T + 'blank', '../hud/ammo_blue_bg_lodef': T + 'blank',
}
for _t in ('red', 'blue'):
    for _v in ('', '_lodef', '_horiz1', '_horiz2', '_horiz1_lodef', '_horiz2_lodef', '_vert', '_vert_lodef'):
        IMAGE_MAP[f'../hud/misc_ammo_area_{_t}{_v}'] = T + 'meter_bg'
        IMAGE_MAP[f'../hud/misc_ammo_area{_v}_{_t}'] = T + 'meter_bg'
IMAGE_KEYS = re.compile(r'^(image|teambg_\d(_lodef)?|image_name|bgimage|image_default|image_armed|image_selected)$', re.I)
COLOR_KEY = re.compile(r'colou?r|_override$', re.I)


def reskin_res(node):
    changed = False
    for ent in kv.walk(node):
        if isinstance(ent[1], list):
            continue
        key, val = ent[0], ent[1]
        if IMAGE_KEYS.match(key) and val.lower() in IMAGE_MAP:
            ent[1] = IMAGE_MAP[val.lower()]
            changed = True
        elif COLOR_KEY.search(key):
            nv = retint(val)
            m = BUTTON_FG.match(key)
            if m and (luma(nv) < 90 or nv.startswith('200 80 60')):
                # stock buttons draw dark text on tan plates; ours are ink, so the text has to go light
                nv = {'default': '200 200 196 255', 'armed': '255 255 255 255'}.get(m.group(1).lower(), '226 226 220 255')
            if nv != val:
                ent[1] = nv
                changed = True
    return changed


BUTTON_FG = re.compile(r'^(default|armed|depressed|selected)FgColor_override$', re.I)


def luma(val):
    m = re.fullmatch(r'\s*(\d+)\s+(\d+)\s+(\d+).*', val)
    if not m:
        return 255
    r, g, b = (int(x) for x in m.groups())
    return 0.299 * r + 0.587 * g + 0.114 * b


# ------------------------------------------------------------------ custom panels
def img_panel(name, x, y, w, h, image, z=1, drawcolor=None, visible=1):
    e = {'ControlName': 'ImagePanel', 'fieldName': name, 'xpos': x, 'ypos': y, 'zpos': z, 'wide': w, 'tall': h,
         'visible': visible, 'enabled': 1, 'scaleImage': 1, 'image': T + image, 'mouseinputenabled': 0}
    if drawcolor:
        e['drawcolor'] = drawcolor
    return e


def label(name, x, y, w, h, text, font, fg, align='west', z=5):
    return {'ControlName': 'CExLabel', 'fieldName': name, 'xpos': x, 'ypos': y, 'zpos': z, 'wide': w, 'tall': h,
            'visible': 1, 'enabled': 1, 'labelText': text, 'textAlignment': align, 'font': font, 'fgcolor': fg}


STATUS_ICONS = ('PlayerStatusBleedImage', 'PlayerStatusHookBleedImage', 'PlayerStatusMilkImage', 'PlayerStatusGasImage',
                'PlayerStatusMarkedForDeathImage', 'PlayerStatusMarkedForDeathSilentImage', 'PlayerStatusSlowed')


def team_img(name, x, y, w, h, image, z=1):
    """Image that swaps to the local player's team art (red = teambg_2, blue = teambg_3)."""
    e = img_panel(name, x, y, w, h, image + '_red', z=z)
    e.update(ControlName='CTFImagePanel', teambg_2=T + image + '_red', teambg_3=T + image + '_blue')
    return e


# ------------------------------------------------------------------ in-game clusters
# Weirdcore-style composition, drawn as torn manga pieces packed close together:
#   player cluster (PLAYER_W x PLAYER_H): the live model standing on a team-toned torn triangle, the health digits
#     on a slanted ink band pressed against the model's chest, the 殺 killstreak tag tucked under the band
#   weapon cluster (WEAPON_W x WEAPON_H): a torn ink blade pointing right, big clip digits, reserve beside them
# Coordinates below are design units relative to each cluster's top-left, drawn at CARD_K.
PLAYER_W, PLAYER_H = 210, 125
SHARD = (0, 0, 130, 130)  # the triangle (manga.shard): runs 5 units below the cluster, where its base's shadow falls
WEAPON_W, WEAPON_H = 130, 76
# Two layouts, picked from the main menu. The default one lives in the plain keys, the other in *_minmode keys and
# the menu buttons flip cl_hud_minmode; stock minmode variants are stripped (strip_minmode) so the cvar moves
# nothing but these clusters.
#   default ("ORTA"): Weirdcore placement, pulled in from the edges, the weapon cluster a little higher
#   minmode ("KOSE"): both clusters in the bottom corners
LAYOUTS = {False: dict(player_x=62, player_bottom=436, weapon_right=109, weapon_bottom=410),
           True: dict(player_x=8, player_bottom=462, weapon_right=8, weapon_bottom=462)}


def k(v):
    return round(v * CARD_K)


def pc(x, y, w, h, alt=False):
    """Player-cluster design box -> screen box, per layout."""
    L = LAYOUTS[alt]
    return L['player_x'] + k(x), L['player_bottom'] - k(PLAYER_H - y), k(w), k(h)


def weapon_pos(alt=False, dx=0, dy=0):
    """Screen position of the point dx, dy (screen units) from the weapon cluster's top-left, per layout."""
    L = LAYOUTS[alt]
    return 'r%d' % (L['weapon_right'] + k(WEAPON_W) - dx), L['weapon_bottom'] - k(WEAPON_H) + dy


def wc(x, y, w, h):
    """Weapon-cluster design box -> box inside HudWeaponAmmo, which is exactly the cluster."""
    return k(x), k(y), k(w), k(h)


def box(x, y, w, h):
    return dict(xpos=x, ypos=y, wide=w, tall=h)


def minmode(node, x, y, w=None, h=None):
    """Append the alternate (corner) layout position as *_minmode keys."""
    for key, v in (('xpos', x), ('ypos', y), ('wide', w), ('tall', h)):
        if v is not None:
            kv.remove(node, key + '_minmode')
            node.append([key + '_minmode', str(v), None])
    return node


def place(node, design, **extra):
    """Put a player-cluster element at its default position, with its corner position as the minmode variant."""
    kv.setmany(node, **extra, **box(*pc(*design)))
    return minmode(node, *pc(*design, alt=True))


def add_placed(body, name, entries, design):
    return minmode(kv.add_block(body, name, entries), *pc(*design, alt=True))


def strip_minmode(node):
    """Drop every stock *_minmode key: cl_hud_minmode is this HUD's layout switch, not the stock minimal HUD."""
    changed = False
    for ent in list(kv.walk(node)):
        if isinstance(ent[1], list):
            before = len(ent[1])
            ent[1][:] = [e for e in ent[1] if not e[0].lower().endswith('_minmode')]
            changed |= len(ent[1]) != before
    before = len(node)
    node[:] = [e for e in node if not e[0].lower().endswith('_minmode')]
    return changed or len(node) != before


BAND = (92, 47, 114, 46)       # health band (hm/hp_band), pressed against the model's chest
GAUGE = (180, 53, 11, 34)      # inside the band's plain-ink right end (manga.hp_band keeps it clear)
DIGITS = (98, 45, 84, 50)


def patch_health(root):
    """Health band: big digits, the vertical bone gauge (the game's health fill seen through the slot of hm/hp_mask),
    status icons just right of the band."""
    body = kv.find(root, 'Resource/UI/HudPlayerHealth.res')
    hp = kv.find(body, 'HudPlayerHealth')
    kv.setmany(hp, xpos=0, ypos=0, wide='f0', tall=480, HealthBonusPosAdj=0, HealthDeathWarning='0.49',
               HealthDeathWarningColor='HM_Crimson')
    place(kv.find(body, 'PlayerStatusHealthImageBG'), GAUGE, zpos=3, image=T + 'hp_track')
    place(kv.find(body, 'PlayerStatusHealthImage'), GAUGE, zpos=4)
    kv.setmany(kv.find(body, 'PlayerStatusMaxHealthValue'), xpos=0, ypos=0, wide=0, tall=0)
    place(kv.find(body, 'PlayerStatusHealthBonusImage'), (84, 38, 132, 64), zpos=0, image=T + 'aura_l', visible=0)
    place(kv.find(body, 'PlayerStatusHealthValue'), DIGITS, zpos=6, font='HM_HealthHuge', fgcolor='HM_Bone',
          textAlignment='west')
    for ent in body:
        if isinstance(ent[1], list) and (ent[0].startswith('PlayerStatus_') or ent[0] in STATUS_ICONS):
            place(ent[1], (210, 58, 20, 20))
    add_placed(body, 'HM_HealthBand', img_panel('HM_HealthBand', *pc(*BAND), 'hp_band', z=1), BAND)
    add_placed(body, 'HM_HealthMask', img_panel('HM_HealthMask', *pc(*GAUGE), 'hp_mask', z=5), GAUGE)
    shadow = (DIGITS[0] + 1, DIGITS[1] + 1) + DIGITS[2:]
    add_placed(body, 'HM_HealthShadow', label('HM_HealthShadow', *pc(*shadow), '%Health%', 'HM_HealthHuge',
                                               'HM_Shadow', z=5), shadow)


def patch_class(root):
    """The live model standing on a torn team-toned triangle; the model's legs end at the triangle's base."""
    body = kv.find(root, 'Resource/UI/HudPlayerClass.res')
    kv.setmany(kv.find(body, 'HudPlayerClass'), xpos=0, ypos=0)
    # the game cuts the model (and the 2D art) off with a straight line at the bottom of its panel: both panels end
    # on the triangle's level base (y 121 of 125), and HM_PlayerShardBase draws the torn base edge over that line
    place(kv.find(body, 'classmodelpanel'), (-6, PLAYER_H - 4 - 260, 130, 260), zpos=3)
    # 2D mode (HUD Settings > PLAYER CHARACTER, i.e. cl_hud_playerclass_use_playermodel 0): TF2's own class art
    # where the model stands, about the model's size, its chest under the band. Narrower than the model panel: the
    # art reaches its frame's edges, and its bottom must stay within the base edge (x 6-127)
    place(kv.find(body, 'PlayerStatusClassImage'), (6, PLAYER_H - 4 - 106, 106, 106), zpos=3)
    for n in ('classmodelpanelBG', 'PlayerStatusClassImageBG'):
        kv.setmany(kv.find(body, n), xpos=0, ypos=0, wide=0, tall=0)
    for n in ('PlayerStatusSpyImage', 'PlayerStatusSpyOutlineImage'):
        place(kv.find(body, n), (4, 92, 28, 28), zpos=8)
    add_placed(body, 'HM_PlayerShard', team_img('HM_PlayerShard', *pc(*SHARD), 'shard', z=1), SHARD)
    add_placed(body, 'HM_PlayerShardBase', img_panel('HM_PlayerShardBase', *pc(*SHARD), 'shard_base', z=4), SHARD)


def patch_ammo(root):
    """Weapon blade: big clip digits in its wide end, reserve beside them."""
    body = kv.find(root, 'Resource/UI/HudAmmoWeapons.res')
    blk = kv.find(body, 'HudWeaponAmmoBG')
    kv.setmany(blk, xpos=0, ypos=0, wide=0, tall=0, image=T + 'blank', teambg_2=T + 'blank', teambg_3=T + 'blank')
    low = kv.find(body, 'HudWeaponLowAmmoImage')
    kv.setmany(low, zpos=1, image=T + 'aura_r', teambg_2=T + 'aura_r', teambg_3=T + 'aura_r',
               drawcolor='255 196 48 255', **box(*wc(0, 8, 110, 60)))
    for x in (blk, low):
        for key in ('teambg_2_lodef', 'teambg_3_lodef'):
            kv.remove(x, key)
    # east-aligned italic digits overhang their box, so keep a right inset or the glyph gets sliced
    common = dict(font='HM_HealthHuge', textAlignment='east', textinsetx=k(6), use_proportional_insets=1)
    kv.setmany(kv.find(body, 'AmmoInClip'), zpos=6, fgcolor='HM_Bone', **common, **box(*wc(4, 12, 64, 50)))
    kv.setmany(kv.find(body, 'AmmoInClipShadow'), zpos=5, fgcolor='HM_Shadow', **common, **box(*wc(5, 13, 64, 50)))
    kv.setmany(kv.find(body, 'AmmoNoClip'), zpos=6, fgcolor='HM_Bone', **common, **box(*wc(4, 12, 90, 50)))
    kv.setmany(kv.find(body, 'AmmoNoClipShadow'), zpos=5, fgcolor='HM_Shadow', **common, **box(*wc(5, 13, 90, 50)))
    small = dict(font='HM_ReserveBig', textAlignment='west', textinsetx=1, use_proportional_insets=1)
    kv.setmany(kv.find(body, 'AmmoInReserve'), zpos=6, fgcolor='HM_Ash', **small, **box(*wc(67, 30, 40, 26)))
    kv.setmany(kv.find(body, 'AmmoInReserveShadow'), zpos=5, fgcolor='HM_Shadow', **small, **box(*wc(68, 31, 40, 26)))
    kv.add_block(body, 'HM_AmmoBlade', img_panel('HM_AmmoBlade', *wc(0, 0, WEAPON_W, WEAPON_H), 'ammo_blade', z=0))


def patch_damage(root):
    body = kv.find(root, 'Resource/UI/HudDamageAccount.res')
    kv.setmany(kv.find(body, 'CDamageAccountPanel'), PositiveColor='226 226 220 255', NegativeColor='46 214 140 255',
               delta_lifetime='1.6', delta_item_font='HM_Damage', delta_item_font_big='HM_DamageBig')


# the metal tag sits on top of the weapon blade; its panel keeps the stock tag row (114) so the floating
# +/- metal numbers (delta_item_*) still rise above it


# Engineer metal: a card in the sticky slot (wrench-on-ingot logo, the count beside it). The panel is taller than
# the card: the game floats the +/- metal deltas upward inside it, above the card.
ACCOUNT_RISE = 36


def account_box(alt=False):
    x, y = meter_card_pos(0, alt)
    return x, y - ACCOUNT_RISE


def patch_account(root):
    body = kv.find(root, 'Resource/UI/HudAccountPanel.res')
    kv.setmany(kv.find(body, 'CHudAccountPanel'), delta_item_x=40, delta_item_start_y=ACCOUNT_RISE - 6,
               delta_item_end_y=2, PositiveColor='46 214 140 255', NegativeColor='200 64 64 255',
               delta_item_font='HM_Metal')
    y = ACCOUNT_RISE + 4
    kv.setmany(kv.find(body, 'AccountBG'), xpos=10, ypos=y, wide=58, tall=26, image=T + 'meter_metal',
               teambg_2=T + 'meter_metal', teambg_3=T + 'meter_metal')
    kv.setmany(kv.find(body, 'MetalIcon'), xpos=0, ypos=0, wide=0, tall=0)
    kv.setmany(kv.find(body, 'AccountValue'), xpos=38, ypos=y, wide=30, tall=26, font='HM_Sticky',
               fgcolor='HM_Bone', textAlignment='west')


STREAK = (110, 97, 72, 24)  # tucked under the health band, like Weirdcore's skull


def patch_killstreak(root):
    """Kill count as a torn 殺 sticker under the health band."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    place(kv.find(body, 'HudItemEffectMeter'), STREAK)
    w, h = k(STREAK[2]), k(STREAK[3])
    kv.setmany(kv.find(body, 'ItemEffectMeterBG'), xpos=0, ypos=0, wide=w, tall=h, image=T + 'tag_streak',
               teambg_2=T + 'tag_streak', teambg_3=T + 'tag_streak')
    kv.setmany(kv.find(body, 'ItemEffectMeterCount'), xpos=k(21), ypos=0, wide=k(22), tall=h,
               font='HM_StreakSmall', textAlignment='west', fgcolor='HM_Bone', textinsetx=0)
    # the label font does not scale with the clusters, so it gets the rest of the tag
    kv.setmany(kv.find(body, 'ItemEffectMeterLabel'), xpos=k(43), ypos=0, wide=w - k(43), tall=h,
               font='HM_Small', textAlignment='west', fgcolor='HM_Emerald')


# item meters (sandvich, cloak, banner, pipes...) keep their stock arrangement, lifted as one block until the lowest
# of them (stock bottom edge ~r2) clears the metal tag / weapon blade of each layout
METER_LIFT = {alt: 482 - weapon_pos(alt)[1] for alt in LAYOUTS}


def lift(node):
    """Move a bottom-right meter up per layout (only 'rN' ypos values, which count from the screen bottom)."""
    y = kv.get(node, 'ypos') or ''
    if re.fullmatch(r'r\d+', y) and (kv.get(node, 'xpos') or '').startswith('r'):
        kv.set(node, 'ypos', 'r%d' % (int(y[1:]) + METER_LIFT[False]))
        minmode(node, kv.get(node, 'xpos'), 'r%d' % (int(y[1:]) + METER_LIFT[True]))


def patch_meter(root):
    """Meters without a card of their own (MvM canteen...) keep their stock layout, lifted above the ammo blade."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    blk = kv.find(body, 'HudItemEffectMeter')
    if blk is not None:
        lift(blk)


def patch_tracker(root):
    """Contract tracker ("Contract Inactive / Press [ F2 ] to view") at the top right.
    - It sat at the height of the kill feed's fifth row (44 + 4 x 19), so a full kill feed covered it: it starts
      below the feed now.
    - The game sizes its box from the header's width plus stats_buffer_width. Our header font is condensed and the
      "Press [ F2 ]" line kept its wide stock font, so that line ran under the folder icon: more buffer."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    kv.set(kv.find(body, 'ItemAttributeTracker'), 'stats_buffer_width', 50)
    kv.set(kv.find(body, 'QuestsStatusContainer'), 'ypos', 146)


def patch_inspect(root):
    """An F tap on a teammate opens the inspect card (their item), and the game hides the ammo, sticky, uber and item
    meter counters while it is open: it locks their render group when the card shows and unlocks it when the card
    hides. A HUD reload with the card open hid the card without the unlock, so the counters stayed gone until the map
    changed. Loading the card as visible keeps that bookkeeping right: the next close (fire, an F tap, death) after a
    reload always unlocks the counters."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    kv.set(kv.find(body, 'itempanel'), 'visible', 1)


def patch_rocketpack(root):
    """Thermal Thruster: stock layout beside the ammo blade. Its file #bases the generic meter, so it would inherit
    the generic card's corner position (the sticky slot) and bar tint: lift it above the blade there, no tint."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    top = kv.find(body, 'HudItemEffectMeter')
    minmode(top, kv.get(top, 'xpos'), 'r%d' % (int(kv.get(top, 'ypos')[1:]) + METER_LIFT[True]))
    kv.add_block(body, 'HM_BarTint', {'visible': 0, 'wide': 0, 'tall': 0})


# Item meters as manga cards in the sticky slot: same torn tag as the sticky counter, a manga logo of the item on its
# (The game shares huditemeffectmeter.res between many items: cloak, Dead Ringer, Jarate, sandvich, banner... The
# per-item files only get an item logo where the in-game test confirmed which item uses them.)
# left (manga.logo_*), an emerald bar (or count) on its right. slot = 0 sits exactly where the sticky
# counter is; meters that can show together with another one (or with the stickies / uber meter) go one card to
# the left (-1) or right (+1).
METER_CARDS = {  # file: (manga logo, slot)
    'huditemeffectmeter.res': ('mask', 0),              # generic: sandvich, banner rage, gas passer... (Hollow mask)
    'huditemeffectmeter_cleaver.res': ('cleaver', -1),  # Flying Guillotine (next to the scout meter)
    'huditemeffectmeter_demoman.res': ('skull', 0),      # shared: Air Strike kills / Eyelander heads (raised, wide)
    'huditemeffectmeter_engineer.res': ('revenge', 1),  # Frontier Justice revenge crits (metal owns slot 0)
    'huditemeffectmeter_heavy.res': ('minigun', 0),     # MvM minigun rage (raised: the lunchbox meter owns slot 0)
    'huditemeffectmeter_organs.res': ('heart', -1),     # Vita-Saw organs (the uber meter owns slot 0)
    'huditemeffectmeter_particlecannon.res': ('plasma', 0),  # Cow Mangler (raised: right above the sticky slot)
    'huditemeffectmeter_pomson.res': ('bolt', 1),       # Pomson 6000 (metal owns slot 0)
    'huditemeffectmeter_pyro.res': ('flame', 0),        # Phlogistinator Mmmph (raised: the Gas Passer in slot 0)
    'huditemeffectmeter_raygun.res': ('beam', 0),       # Righteous Bison (a secondary like the banner: right under
                                                        # the Cow Mangler / Air Strike card, not off to the side)
    'huditemeffectmeter_sapper.res': ('sapper', 1),     # sapper recharge
    'huditemeffectmeter_scout.res': ('drink', 0),       # Bonk / Crit-a-Cola / Mad Milk (raised: Sandman in slot 0)
    'huditemeffectmeter_sniper.res': ('skull', 0),      # Bazaar Bargain heads (raised: Jarate / Razorback in slot 0)
    'huditemeffectmeter_sniperfocus.res': ('scope', 1),  # Hitman's Heatmaker focus
    'huditemeffectmeter_sodapopper.res': ('soda', 1),   # Soda Popper hype
    'huditemeffectmeter_spy.res': ('revolver', 0),      # Diamondback crits (raised: the cloak meter owns slot 0)
    'huditemeffectmeter_spyknife.res': ('icicle', -1),  # Spy-cicle
}
CARD_STEP = 76
# Cards that sit one row above their slot (fixed, like WeirdcoreHUD: the game cannot tell the HUD which other
# meter is showing). Cow Mangler: right above the sticky slot, so a banner's rage card below never covers it.
# The Air Strike and the Eyelander share huditemeffectmeter_demoman.res, so one card serves both: a skull (heads /
# kills), raised over the sticky slot (Demoman's sticky / shield counter and a Soldier's banner rage sit in it), wide
# enough to show the game's own label next to the count, "KILLS" for the Air Strike, "HEADS" for the Eyelander.
# The generic meter file (banner rage, cloak, Jarate, Razorback, Sandman, lunchbox...) owns the sticky slot, so the
# per-item files that a class can show next to it go one row up: Scout's drinks next to the Sandman, Sniper's Bazaar
# Bargain next to Jarate, Spy's Diamondback next to the cloak, Heavy's MvM rage next to the sandvich, Pyro's
# Phlogistinator next to the Gas Passer. No class can show two of the raised cards at once (checked against the
# game's per-class meter list). The row sits right under the target IDs, which move up to clear it (target_id_ys).
METER_RAISED = {'huditemeffectmeter_particlecannon.res', 'huditemeffectmeter_demoman.res',
                'huditemeffectmeter_scout.res', 'huditemeffectmeter_sniper.res', 'huditemeffectmeter_spy.res',
                'huditemeffectmeter_heavy.res', 'huditemeffectmeter_pyro.res'}
# card width (others: 58): count cards wide enough for the game's own word next to the count
# (Air Strike KILLS / Eyelander HEADS, Bazaar Bargain HEADS, Diamondback CRITS)
METER_WIDE = {'huditemeffectmeter_demoman.res': 80, 'huditemeffectmeter_sniper.res': 80,
              'huditemeffectmeter_spy.res': 80}
CARD_ROW = 30  # one card (26) plus a gap


def meter_card_name(filename):
    """huditemeffectmeter_spy.res -> meter_item_spy (texture name, shared with build_art)."""
    return 'meter_' + filename[:-4].replace('huditemeffectmeter', 'item')


def meter_card_pos(slot, alt=False):
    x, y = pipes_pos(alt)
    return 'c%d' % (-PIPES_W // 2 + slot * CARD_STEP), y


TID_H, TID_GAP = 35, 6  # target ID strip height (stock), gap under each strip


def target_id_ys(alt=False):
    """Main and secondary target ID tops (stock 285 / 335). The secondary strip ("Healer: ..." / "Healing: ...")
    covered the raised card row (its art starts 4 under the meter's top), so both strips go up until it clears."""
    healer = min(335, pipes_pos(alt)[1] - CARD_ROW + 4 - TID_GAP - TID_H)
    return min(285, healer - TID_GAP - TID_H), healer


# Item meter bars and the Vaccinator segments are painted white (grey when not full) by the game's code every frame,
# so no .res key recolours them. The cards paint those bars white on an ink track and lay a translucent emerald
# sheet over them: white turns pale jade, the ink track deep emerald. The game blends in linear light (measured in
# game: fill = a*sheet + (1-a)*white in linear), so fill and track always differ by the same linear amount (1-a)
# in every channel; a = 0.6 gives fill ~170 197 181 on a ~6 112 70 track.
BAR_TINT = '3 141 89 153'
BAR_TRACK = '10 10 12 255'


def tint_bar(body, x, y, w, h):
    kv.add_block(body, 'HM_BarTint', {'ControlName': 'EditablePanel', 'fieldName': 'HM_BarTint', 'xpos': x, 'ypos': y,
                                      'zpos': 3, 'wide': w, 'tall': h, 'visible': 1, 'enabled': 1,
                                      'paintbackground': 1, 'bgcolor_override': BAR_TINT, 'mouseinputenabled': 0})


def patch_meter_card(root, rel):
    fname = rel.split('/')[-1]
    _, slot = METER_CARDS[fname]
    name = meter_card_name(fname)
    body = next(e[1] for e in root if isinstance(e[1], list))
    top = kv.find(body, 'HudItemEffectMeter')
    rise = CARD_ROW if fname in METER_RAISED else 0
    cw = METER_WIDE.get(fname, 58)
    grow = cw - 58  # a wider card grows both ways around the slot's centre
    for alt in (False, True):
        x, y = meter_card_pos(slot, alt)
        x = 'c%d' % (int(x[1:]) - grow // 2)
        if alt:
            minmode(top, x, y - rise)
        else:
            kv.setmany(top, **box(x, y - rise, PIPES_W + grow, PIPES_H))
    for key in list(e[0] for e in top if e[0].lower().startswith('x_offset')):
        kv.remove(top, key)
    bg = kv.find(body, 'ItemEffectMeterBG')
    if bg is None:  # a #base file (Pyro) only overrides the generic card underneath: its own logo, the rest inherited
        bg = kv.add_block(body, 'ItemEffectMeterBG', {})
    kv.setmany(bg, xpos=10, ypos=4, zpos=0, wide=cw, tall=26, image=T + name,
               teambg_1=T + name, teambg_2=T + name, teambg_3=T + name)
    kv.remove(bg, 'visible_minmode')
    # the logo says what the meter is, so the game's text labels go; the bar (or count) fills the card's right half.
    # Wide cards keep the first label, small, right of the count (the game writes the item's word into it)
    for n in ('ItemEffectMeterLabel', 'ItemEffectMeterLabel2'):
        blk = kv.find(body, n)
        if blk is None:
            continue
        if fname in METER_WIDE and n == 'ItemEffectMeterLabel':
            kv.setmany(blk, xpos=10 + 52, ypos=12, zpos=2, wide=cw - 54, tall=10, visible=1, font='HM_Small',
                       textAlignment='west', autoResize=0)
        else:
            kv.setmany(blk, xpos=0, ypos=0, wide=0, tall=0)
    kv.remove(body, 'HM_BarTint')
    for n, extra in (('ItemEffectMeter', dict(xpos=38, ypos=13, wide=26, tall=8)),
                     ('ItemEffectMeterCount', dict(xpos=39 if cw == 58 else 10 + 30, ypos=8, wide=28 if cw == 58 else 22,
                                                   tall=18, font='HM_Sticky', fgcolor='HM_Bone'))):
        blk = kv.find(body, n)
        if blk is not None:
            kv.setmany(blk, zpos=2, **extra)
            if 'font' in extra:
                kv.setmany(blk, textAlignment='west', autoResize=0)
            else:
                kv.setmany(blk, bgcolor_override=BAR_TRACK)
                if kv.get(blk, 'visible') != '0':  # count-only meters keep their (hidden) bar: no sheet over the count
                    tint_bar(body, 38, 13, 26, 8)
    for i in range(1, 4):  # heavy kill-combo class icons
        blk = kv.find(body, 'KillComboClassIcon%d' % i)
        if blk is not None:
            kv.setmany(blk, xpos=38 + (i - 1) * 9, ypos=22, zpos=2, wide=8, tall=8)


# stock meter files (shield / bow / uber charge, Dead Ringer, stickies, item meters) keep their layout but lose
# the stock boxes: torn ink tags behind them, emerald bars
METER_FILE = re.compile(r'resource/ui/hud\w*(charge|meter|pipes)\w*\.res$')


# the game paints item meter bars with these; it reads them as raw r g b a, so scheme colour names don't work
METER_COLORS = dict(MeterFG='46 214 140 255', MeterBG='122 124 124 110')


def recolor_meters(root):
    for ent in kv.walk(root):
        if not isinstance(ent[1], list) and ent[0] in METER_COLORS:
            ent[1] = METER_COLORS[ent[0]]


def patch_meter_style(root):
    recolor_meters(root)
    for ent in kv.walk(root):
        blk = ent[1]
        if not isinstance(blk, list):
            continue
        ctl = (kv.get(blk, 'ControlName') or '').lower()
        if ctl in ('continuousprogressbar', 'progressbar'):
            kv.setmany(blk, fgcolor_override='46 214 140 255', bgcolor_override='226 226 220 45')
        elif ctl in ('imagepanel', 'ctfimagepanel'):
            img = (kv.get(blk, 'image') or '').lower()
            if img.startswith('../hud/') and ('_bg' in img or 'misc_ammo' in img):
                kv.set(blk, 'image', T + 'meter_bg')
                for key in ('teambg_1', 'teambg_2', 'teambg_3'):
                    if kv.get(blk, key) is not None:
                        kv.set(blk, key, T + 'meter_bg')


# sticky counter / shield charge card: a small torn ink tag at the bottom center, level with the health / ammo row,
# with a manga stickybomb
# (team band, reiatsu aura) breaking out of its left edge and the count beside it; the bomb dims when none are out
PIPES_W, PIPES_H = 70, 34


def pipes_pos(alt=False):
    """Centered on the screen, level with the middle of the health band / ammo blade row of each layout."""
    band_mid = pc(*BAND, alt=alt)[1] + k(BAND[3]) / 2
    blade_mid = weapon_pos(alt)[1] + k(WEAPON_H) / 2
    return "c-%d" % (PIPES_W // 2), round((band_mid + blade_mid) / 2 + 20 - PIPES_H / 2)


def patch_pipes(root):
    body = next(e[1] for e in root if isinstance(e[1], list))
    # The same panel shows the shield charge instead of the count when a shield is equipped (the game swaps
    # ChargeMeter in and the pipe panels out). The background tag carries a manga Chargin' Targe;
    # in sticky mode the pipe panels lay a plain copy of the tag over it, so the shield only shows with a shield.
    kv.setmany(kv.find(body, 'background'), xpos=10, ypos=4, zpos=0, wide=58, tall=26, image=T + 'tag_shield_red',
               teambg_2=T + 'tag_shield_red', teambg_3=T + 'tag_shield_blue')
    kv.setmany(kv.find(body, 'ChargeLabel'), xpos=0, ypos=0, wide=0, tall=0, visible=0)
    kv.setmany(kv.find(body, 'ChargeMeter'), xpos=38, ypos=13, zpos=1, wide=26, tall=8)
    for panel, color, bomb in (('PipesPresentPanel', 'HM_Bone', None), ('NoPipesPresentPanel', 'HM_Ash', '255 255 255 90')):
        pnl = kv.find(body, panel)
        if pnl is None:
            continue
        kv.setmany(pnl, xpos=0, ypos=0, zpos=2, wide=70, tall=34)
        kv.setmany(kv.find(pnl, 'PipeIcon'), xpos=0, ypos=0, wide=0, tall=0)
        kv.add_block(pnl, 'HM_PipesCover', img_panel('HM_PipesCover', 10, 4, 58, 26, 'meter_bg', z=0))
        icon = team_img('HM_StickyIcon', 0, 0, 34, 34, 'sticky', z=1)
        if bomb:
            icon['drawcolor'] = bomb
        kv.add_block(pnl, 'HM_StickyIcon', icon)
        for n, dx, fg in (('NumPipesLabel', 0, color), ('NumPipesLabelDropshadow', 1, 'HM_Shadow')):
            blk = kv.find(pnl, n)
            if blk is not None:
                kv.setmany(blk, xpos=38 + dx, ypos=4 + dx, wide=30, tall=26, font='HM_Sticky', fgcolor=fg,
                           textAlignment='west')


# ÜberCharge (Vaccinator included) as a card in the sticky slot: medic-cross logo, the charge % above an emerald bar
# (the Vaccinator's four charge segments take the bar's place, its resist icon covers the logo).
# tf2_misc does not always carry hudmediccharge.res, so the stock layout is kept here as a fallback.
STOCK_MEDIC = '''"Resource/UI/HudMedicCharge.res"
{
	"Background"	{ "ControlName" "CTFImagePanel" "fieldName" "Background" "xpos" "0" "ypos" "0" "zpos" "0" "wide" "130" "tall" "65"
		"visible" "1" "enabled" "1" "image" "../hud/medic_charge_blue_bg" "scaleImage" "1" "teambg_2" "../hud/medic_charge_red_bg"
		"teambg_3" "../hud/medic_charge_blue_bg" }
	"ChargeLabel"	{ "ControlName" "CExLabel" "fieldName" "ChargeLabel" "xpos" "30" "ypos" "24" "zpos" "1" "wide" "90" "tall" "15"
		"visible" "1" "enabled" "1" "labelText" "#TF_Ubercharge" "textAlignment" "center" "dulltext" "0" "brighttext" "0"
		"font" "HudFontSmallest" }
	"IndividualChargesLabel"	{ "ControlName" "CExLabel" "fieldName" "IndividualChargesLabel" "xpos" "30" "ypos" "24"
		"zpos" "1" "wide" "90" "tall" "15" "visible" "0" "enabled" "1" "labelText" "#TF_IndividualUbercharges"
		"textAlignment" "center" "dulltext" "0" "brighttext" "0" "font" "HudFontSmallest" }
	"ChargeMeter"	{ "ControlName" "ContinuousProgressBar" "fieldName" "ChargeMeter" "xpos" "30" "ypos" "38" "zpos" "2"
		"wide" "86" "tall" "8" "visible" "1" "enabled" "1" }
	"ChargeMeter1"	{ "ControlName" "ContinuousProgressBar" "fieldName" "ChargeMeter1" "xpos" "30" "ypos" "38" "zpos" "2"
		"wide" "19" "tall" "8" "visible" "0" "enabled" "1" }
	"ChargeMeter2"	{ "ControlName" "ContinuousProgressBar" "fieldName" "ChargeMeter2" "xpos" "52" "ypos" "38" "zpos" "2"
		"wide" "19" "tall" "8" "visible" "0" "enabled" "1" }
	"ChargeMeter3"	{ "ControlName" "ContinuousProgressBar" "fieldName" "ChargeMeter3" "xpos" "74" "ypos" "38" "zpos" "2"
		"wide" "19" "tall" "8" "visible" "0" "enabled" "1" }
	"ChargeMeter4"	{ "ControlName" "ContinuousProgressBar" "fieldName" "ChargeMeter4" "xpos" "96" "ypos" "38" "zpos" "2"
		"wide" "19" "tall" "8" "visible" "0" "enabled" "1" }
	"HealthClusterIcon"	{ "ControlName" "ImagePanel" "fieldName" "HealthClusterIcon" "xpos" "2" "ypos" "17" "zpos" "1"
		"wide" "36" "tall" "36" "visible" "1" "enabled" "1" "image" "../hud/ico_health_cluster" "scaleImage" "1" }
	"ResistIcon"	{ "ControlName" "ImagePanel" "fieldName" "ResistIcon" "xpos" "0" "ypos" "-25" "zpos" "1" "wide" "36"
		"tall" "36" "visible" "0" "enabled" "1" "image" "../HUD/defense_buff_bullet_blue" "scaleImage" "1" }
}
'''


UBER_W, UBER_H = 80, 26
UBER_BAR = (30, 15, 46, 8)   # bar box inside the card, right of the medic cross
UBER_GAP = 2                 # ink gap between the Vaccinator segments
UBER_FILL = '170 198 181 255'   # what the emerald sheet turns a white bar into (measured in game)
UBER_TRACK = '1 112 69 255'


def patch_uber(root):
    """The game pins the Vaccinator's resist icon to the panel's 0,0, so the panel starts at the tag's top left
    (the other cards keep a 10 / 4 margin for the stickybomb) and the icon lands right on the logo."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    bg = kv.find(body, 'Background')
    kv.setmany(bg, xpos=0, ypos=0, zpos=0, wide=UBER_W, tall=UBER_H, image=T + 'meter_uber', teambg_1=T + 'meter_uber',
               teambg_2=T + 'meter_uber', teambg_3=T + 'meter_uber')
    for key in ('teambg_2_lodef', 'teambg_3_lodef'):
        kv.remove(bg, key)
    # the percent only (the game fills %charge% in; the Vaccinator shows its full charges, %charge_count%, there)
    for n, text in (('ChargeLabel', '%charge%'), ('IndividualChargesLabel', '%charge_count%')):
        kv.setmany(kv.find(body, n), labelText=text, xpos=UBER_BAR[0], ypos=0, zpos=2, wide=UBER_BAR[2], tall=14,
                   font='HM_Metal', fgcolor='HM_Bone', textAlignment='west')
    blk = kv.find(body, 'HealthClusterIcon')
    if blk is not None:
        kv.setmany(blk, xpos=0, ypos=0, wide=0, tall=0)
    x, y, w, h = UBER_BAR
    # Vaccinator: four wide segments with ink gaps. The game paints them white (grey while filling), so each gets
    # its own emerald sheet of exactly its size (pale jade on deep emerald, like the item bars)
    seg = (w - 3 * UBER_GAP) // 4
    for i in range(4):
        sx = x + i * (seg + UBER_GAP)
        sw = seg if i < 3 else x + w - sx
        blk = kv.find(body, 'ChargeMeter%d' % (i + 1))
        if blk is not None:
            kv.setmany(blk, xpos=sx, ypos=y, zpos=2, wide=sw, tall=h, bgcolor_override=BAR_TRACK)
        kv.add_block(body, 'HM_SegTint%d' % (i + 1), {
            'ControlName': 'EditablePanel', 'fieldName': 'HM_SegTint%d' % (i + 1), 'xpos': sx, 'ypos': y, 'zpos': 3,
            'wide': sw, 'tall': h, 'visible': 1, 'enabled': 1, 'paintbackground': 1, 'bgcolor_override': BAR_TINT,
            'mouseinputenabled': 0})
    # the regular uber bar: one plain bar in the jade / deep emerald the tinted bars end up as, drawn above the
    # Vaccinator sheets (the game hides it for the Vaccinator, which uncovers them)
    kv.setmany(kv.find(body, 'ChargeMeter'), xpos=x, ypos=y, zpos=5, wide=w, tall=h, fgcolor_override=UBER_FILL,
               bgcolor_override=UBER_TRACK)
    blk = kv.find(body, 'ResistIcon')
    if blk is not None:
        kv.setmany(blk, xpos=0, ypos=0, zpos=4, wide=26, tall=26)


def uber_box(alt=False):
    """Centered on the sticky tag (which is 58 wide at +10 in its slot), wider than it."""
    x, y = meter_card_pos(0, alt)
    return 'c%d' % (int(x[1:]) + 10 + (58 - UBER_W) // 2), y + 4


def patch_streak_notice(root):
    """Killstreak splash ("... is GODLIKE!"): the game sizes and places the background around the text every frame,
    so the torn manga card is a nine-slice border on it instead of the stock flat box."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    bg = kv.find(body, 'Background')
    kv.remove(bg, 'bgcolor_override')
    kv.setmany(bg, PaintBackgroundType=0, paintbackground=0, paintborder=1, border='HM_StreakCard')


# casual / competitive team strip at the top of the screen (hudmatchstatus.res TeamStatus): the frame behind it is
# the torn CTF band, each player portrait gets a torn bone rim, the colours move to the Hueco Mundo palette
PORTRAIT_COLORS = {
    'color_portrait_bg_red': '156 70 70 255', 'color_portrait_bg_blue': '84 114 150 255',  # alive: bright enough to read
    'color_portrait_bg_red_dead': '40 32 32 255', 'color_portrait_bg_blue_dead': '30 34 40 255',
    'color_bar_health_high': '46 214 140 255', 'color_bar_health_med': '214 196 120 255',
    'color_bar_health_low': '200 64 64 255', 'color_portrait_blend_dead_red': '150 150 150 255',
    'color_portrait_blend_dead_blue': '150 150 150 255',
}


def patch_matchstatus(root):
    body = next(e[1] for e in root if isinstance(e[1], list))
    frame = kv.find(body, 'BGFrame')
    if frame is not None:
        kv.set(frame, 'border', 'HM_TopBand')
    status = kv.find(body, 'TeamStatus')
    pp = kv.find(status, 'playerpanels_kv') if status is not None else None
    if pp is None:
        return
    kv.setmany(pp, **PORTRAIT_COLORS)
    for n, bg in (('healthbar', '12 12 14 255'), ('overhealbar', None)):
        blk = kv.find(pp, n)
        if blk is not None and bg:
            kv.set(blk, 'bgcolor_override', bg)
    blk = kv.find(pp, 'overhealbar')
    if blk is not None:
        kv.set(blk, 'fgcolor_override', '170 240 206 200')
    kv.add_block(pp, 'HM_PortraitFrame', {
        'ControlName': 'ImagePanel', 'fieldName': 'HM_PortraitFrame', 'xpos': 0, 'ypos': 0, 'zpos': 4, 'wide': 'f0',
        'tall': 21, 'visible': 1, 'enabled': 1, 'scaleImage': 1, 'image': T + 'portrait_frame',
        'proportionaltoparent': 1, 'mouseinputenabled': 0})


NOTIF_IMAGES = {T + 'panel_red': T + 'notif_red', T + 'panel_blue': T + 'notif_blue', T + 'panel_clear': T + 'notif_ink'}


def patch_notification(root, rel):
    """HUD notifications (resource/ui/notifications/*): the game stretches the background to the text, so the card
    art is a flat torn notice card; the base file sets the lettering."""
    for ent in kv.walk(root):
        if not isinstance(ent[1], list) and ent[0].lower() == 'image' and ent[1] in NOTIF_IMAGES:
            ent[1] = NOTIF_IMAGES[ent[1]]
    if rel.endswith('base_notification.res'):
        body = next(e[1] for e in root if isinstance(e[1], list))
        kv.setmany(kv.find(body, 'Notification_Label'), font='HM_NoticeTitle', fgcolor='HM_Bone')


def patch_freezepanel(root):
    """Death screen "You were killed by ...". The game paints its background flat in the killer's team colour from code
    (hud/color_panel_*), so that panel shrinks to nothing and a torn manga card takes its place. The card follows the
    local player's team inverted (your killer is nearly always on the other team): local RED -> BLU card."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    bases = [e[1] for e in body if e[0] == 'FreezePanelBase' and isinstance(e[1], list)]
    for base in bases:
        bg = kv.find(base, 'FreezePanelBG')
        if bg is not None:
            kv.setmany(bg, wide=0, tall=0)
    base = bases[-1]  # the file defines the panel twice; the last block is the one the game lays out
    card = img_panel('HM_FreezeCard', 2, 154, 268, 44, 'freeze_blue', z=0)
    card.update(ControlName='CTFImagePanel', teambg_2=T + 'freeze_blue', teambg_3=T + 'freeze_red')
    kv.add_block(base, 'HM_FreezeCard', card)
    # plain vgui Labels: fgcolor_override (fgcolor is CExLabel only)
    kv.setmany(kv.find(base, 'FreezeLabel'), xpos=44, ypos=160, font='HM_NoticeBody', fgcolor_override='HM_BoneMid')
    kv.setmany(kv.find(base, 'FreezeLabelKiller'), ypos=172, tall=20, font='HM_NoticeTitle')
    kv.set(kv.find(base, 'AvatarImage'), 'zpos', 2)


def patch_statpanel(root):
    """Death screen record card ("On the bright side... You came close to your record for ..."): the stock framed box
    becomes a torn manga card in your own team's tone, the class portrait on its toned end, the text in the notice
    fonts over an emerald rule. It starts below the spectator target ID, whose bottom the stock box covered."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    kv.setmany(kv.find(body, 'StatPanelBG'), xpos=0, ypos=20, wide=266, tall=92, image=T + 'stat_blue',
               teambg_2=T + 'stat_red', teambg_3=T + 'stat_blue')
    kv.setmany(kv.find(body, 'StatPanelClassImage'), xpos=6, ypos=28, wide=70, tall=70)
    # plain vgui Labels: fgcolor_override (fgcolor is CExLabel only)
    for n, extra in (('titleLable', dict(ypos=26, tall=12, font='HM_NoticeBody', fgcolor_override='HM_Emerald')),
                     ('summaryLabel', dict(ypos=38, tall=40, font='HM_NoticeBody', fgcolor_override='HM_Bone')),
                     ('StatLabelLarge', dict(ypos=80, tall=22, font='HM_NoticeTitle', fgcolor_override='HM_Bone')),
                     ('StatLabelSmall', dict(ypos=83, tall=16, font='HM_NoticeBody', fgcolor_override='HM_BoneMid'))):
        kv.setmany(kv.find(body, n), xpos=82, wide=176, **extra)
    kv.setmany(kv.find(body, 'StatBox'), wide=0, tall=0)  # the game paints it translucent black from code


def patch_tournament(root):
    """Match start countdown (casual / competitive): the digits on a square torn manga card, in the health font."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    bg = kv.find(body, 'CountdownBG')
    if bg is not None:
        kv.setmany(bg, image=T + 'countdown_card', src_corner_width=60, src_corner_height=60, draw_corner_width=9,
                   draw_corner_height=9, wide=50, tall=50)
        comp = kv.find(bg, 'if_competitive')
        if comp is not None:
            kv.setmany(comp, xpos='cs-0.5', ypos=145)
    for n, color in (('CountdownLabel', 'HM_Bone'), ('CountdownLabelShadow', 'HM_Shadow')):
        blk = kv.find(body, n)
        if blk is None:
            continue
        kv.set(blk, 'font', 'HM_HealthHuge')
        comp = kv.find(blk, 'if_competitive')
        if comp is not None:
            kv.setmany(comp, font='HM_HealthHuge', fgcolor=color)
        else:
            kv.set(blk, 'fgcolor', color)


def patch_targetid(root):
    """Target ID (what you look at, who heals you, spectator target): the game stretches the background to the text
    and gives it the target's team (teambg_*), so it becomes the flat torn notice card in that team's tone."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    kv.setmany(kv.find(body, 'TargetIDBG'), image=T + 'tid_ink', teambg_1=T + 'tid_ink', teambg_2=T + 'tid_red',
               teambg_3=T + 'tid_blue')
    for n, img in (('TargetIDBG_Spec_Blue', 'tid_blue'), ('TargetIDBG_Spec_Red', 'tid_red')):
        blk = kv.find(body, n)
        if blk is not None:
            kv.setmany(blk, image=T + img, src_corner_width=40, src_corner_height=40, draw_corner_width=5,
                       draw_corner_height=5)
    kv.set(kv.find(body, 'TargetNameLabel'), 'font', 'HM_NoticeTitle')
    kv.set(kv.find(body, 'TargetDataLabel'), 'font', 'HM_NoticeBody')


# ------------------------------------------------------------------ center-screen notices
# Team goal ("You are now Attacking!"), team switch (autobalanced) and alert (autobalance warning) share one card:
# torn team-toned panel, a bone seal with the notice's kanji where the stock icon was, text beside it split by an
# emerald rule. Labels keep the stock order; any label that can carry a sentence wraps.
NOTICE_W, NOTICE_H = 320, 82
NOTICES = {  # file: background, stock icon, seal, [(label, box, font, colour, wrap)], rule box
    'resource/ui/hudteamgoal.res': (
        'HudTeamGoalBG', 'GoalImage', 'seal_goal',
        [('SwitchLabel', (76, 10, 234, 22), 'HM_NoticeTitle', 'HM_Bone', 0),
         ('GoalLabel', (76, 38, 234, 38), 'HM_NoticeBody', 'HM_BoneMid', 1)], (76, 31, 220, 6)),
    'resource/ui/hudteamswitch.res': (
        'HudTeamSwitchBG', 'SwitchImage', 'seal_switch',
        [('BalanceLabel', (76, 8, 234, 26), 'HM_NoticeBody', 'HM_BoneMid', 1),
         ('SwitchLabel', (76, 42, 234, 36), 'HM_NoticeTitle', 'HM_Bone', 1)], (76, 35, 220, 6)),
    'resource/ui/hudalert.res': (
        'HudAlertBG', 'AlertImage', 'seal_alert',
        [('AlertLabel', (76, 10, 234, 56), 'HM_NoticeTitle', 'HM_Bone', 1)], (76, 70, 220, 6)),
}


def patch_notice(root, rel):
    bg, icon, seal, labels, rule = NOTICES[rel]
    body = next(e[1] for e in root if isinstance(e[1], list))
    blk = kv.find(body, bg)
    kv.setmany(blk, xpos=0, ypos=0, zpos=-1, wide=NOTICE_W, tall=NOTICE_H, image=T + 'notice_blue',
               teambg_2=T + 'notice_red', teambg_3=T + 'notice_blue')
    for key in ('teambg_2_lodef', 'teambg_3_lodef'):
        kv.remove(blk, key)
    kv.setmany(kv.find(body, icon), xpos=0, ypos=0, wide=0, tall=0, visible=0)
    kv.add_block(body, 'HM_NoticeSeal', img_panel('HM_NoticeSeal', 12, 12, 52, 58, seal, z=1))
    kv.add_block(body, 'HM_NoticeRule', img_panel('HM_NoticeRule', *rule, 'notice_rule', z=1))
    for name, bx, font, color, wrap in labels:
        # stock labels are plain vgui Labels, which take fgcolor_override (fgcolor is CExLabel only)
        kv.setmany(kv.find(body, name), zpos=2, font=font, fgcolor_override=color, textAlignment='north-west',
                   wrap=wrap, **box(*bx))


def patch_building(root, rel):
    """Engineer / spy building status items (resource/ui/hud_obj_*.res): stock background hidden, a torn manga
    card sized to the item underneath the stock icons and bars, the building's kanji as a faint watermark.
    Written against whatever the game ships, so it only reads the item size and hides background icons."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    top = next((e[1] for e in body if isinstance(e[1], list)), None)
    if top is None:
        return
    w, h = kv.get(top, 'wide'), kv.get(top, 'tall')
    if not (w and h and w.isdigit() and h.isdigit()):
        return
    w, h = int(w), int(h)
    for ent in kv.walk(body):
        if not isinstance(ent[1], list):
            continue
        fname = (kv.get(ent[1], 'fieldName') or ent[0]).lower()
        icon = (kv.get(ent[1], 'icon') or '').lower()
        if fname == 'background' or icon.startswith('obj_status_background'):
            kv.setmany(ent[1], visible=0, wide=0, tall=0)
    kind = next((k for k in build_art.BUILDING_KANJI if k in rel), None)
    kv.add_block(body, 'HM_BldCard', team_img('HM_BldCard', 0, 0, w, h, 'bld', z=-2))
    s = h - 6
    if kind:
        kv.add_block(body, 'HM_BldKanji', img_panel('HM_BldKanji', w - s - 4, 3, s, s, 'bld_k_' + kind, z=-1,
                                                    drawcolor='226 226 220 34'))
    # alerts (low ammo / health, sapper): the stock tray slid a bright white tab over the card's kanji end. It stays
    # hidden (the game still runs its slide, which is what shows the icons), and the icons sit on the kanji instead:
    # the wrench in bone, the sapper in crimson
    for ent in kv.walk(body):
        if not isinstance(ent[1], list):
            continue
        if (kv.get(ent[1], 'ControlName') or '').lower() == 'cbuildingstatusalerttray':
            kv.set(ent[1], 'visible', 0)
        elif ent[0] in ('WrenchIcon', 'SapperIcon'):
            iw, ih = int(kv.get(ent[1], 'wide') or 27), int(kv.get(ent[1], 'tall') or 27)
            kv.setmany(ent[1], xpos=w - s // 2 - 4 - iw // 2, ypos=3 + s // 2 - ih // 2,
                       iconColor='226 226 220 255' if ent[0] == 'WrenchIcon' else '210 70 64 255')


def patch_spec_health(root):
    """Target-ID / spectator health: its fill is our bone texture now (hud/health_color), so the stock cross
    outline behind it becomes the plain gauge tile."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    bg = kv.find(body, 'PlayerStatusHealthImageBG')
    if bg is not None:
        kv.set(bg, 'image', T + 'hp_track')
    # the grey number vanished on the bone fill: bone lettering with an ink outline reads on fill and track
    val = kv.find(body, 'PlayerStatusHealthValue')
    if val is not None:
        kv.setmany(val, font='HM_SpecHealth', fgcolor='HM_Bone')


def patch_flagpanel(root):
    """CTF: compact torn manga score strip (blue | red tone), flags in torn rings on either side."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    kv.setmany(kv.find(body, 'LeftSideBG'), xpos='c-90', ypos='r48', wide=180, tall=39, image=T + 'ctf_bar')
    for n in ('RightSideBG', 'OutlineBG', 'PlayingToBG'):
        kv.setmany(kv.find(body, n), wide=0, tall=0, visible=0)
    for n, x, fg in (('BlueScore', 'c-80', 'HM_Bone'), ('BlueScoreShadow', 'c-79', 'HM_Shadow'),
                     ('RedScore', 'c20', 'HM_Bone'), ('RedScoreShadow', 'c21', 'HM_Shadow')):
        kv.setmany(kv.find(body, n), xpos=x, ypos='r47' if 'Shadow' not in n else 'r46', wide=60, tall=36,
                   font='HM_Streak', fgcolor=fg, textAlignment='center')
    kv.setmany(kv.find(body, 'PlayingTo'), xpos='c-70', ypos='r12', wide=140, tall=12, font='HM_Small',
               fgcolor='HM_Ash')
    kv.setmany(kv.find(body, 'BlueFlag'), xpos='c-202', ypos='r58')
    kv.setmany(kv.find(body, 'RedFlag'), xpos='c42', ypos='r58')


def patch_flagstatus(root):
    """Shrink the ring / icon inside each flag panel to match the compact strip."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    kv.setmany(kv.find(body, 'Arrow'), xpos=52, ypos=0, wide=56, tall=56)
    brief = kv.find(body, 'Briefcase')
    kv.setmany(brief, xpos=66, ypos=14, wide=28, tall=28)
    for e in brief:
        if isinstance(e[1], list):
            kv.setmany(e[1], xpos=64, ypos=12, wide=32, tall=32)
    kv.setmany(kv.find(body, 'StatusIcon'), xpos=69, ypos=17, wide=22, tall=22)


def patch_chat(root):
    body = next(e[1] for e in root if isinstance(e[1], list))
    kv.setmany(kv.find(body, 'HudChat'), xpos=5, ypos=200, wide=270, tall=112)


def patch_hudlayout(root):
    body = kv.find(root, 'Resource/HudLayout.res')
    ammo = kv.find(body, 'HudWeaponAmmo')
    kv.setmany(ammo, **box(*weapon_pos(), k(WEAPON_W), k(WEAPON_H)))
    minmode(ammo, *weapon_pos(True))
    kv.setmany(kv.find(body, 'CHudAccountPanel'), **box(*account_box(), PIPES_W, PIPES_H + ACCOUNT_RISE))
    minmode(kv.find(body, 'CHudAccountPanel'), *account_box(True))
    kv.setmany(kv.find(body, 'HudChat'), xpos=5, ypos=196, wide=300, tall=112)
    # sticky launcher / bow / flame-rocket charge-up: a thin emerald bar centered right under the sticky card
    for n in ('HudDemomanCharge', 'HudBowCharge', 'HudFlameRocketCharge'):
        blk = kv.find(body, n)
        if blk is not None:
            kv.setmany(blk, zpos=5, xpos='c-30', ypos=pipes_pos()[1] + PIPES_H + 2)
            minmode(blk, 'c-30', pipes_pos(True)[1] + PIPES_H + 2)
    for n in ('HudItemEffectMeter', 'HudDemomanCharge', 'HudBowCharge', 'HudFlameRocketCharge'):
        blk = kv.find(body, n)
        if blk is not None:
            recolor_meters(blk)
    lift(kv.find(body, 'HudItemEffectMeter'))
    # ÜberCharge (incl. Vaccinator): a card in the sticky slot, below the healing target ID
    uber = kv.find(body, 'HudMedicCharge')
    if uber is not None:
        kv.setmany(uber, **box(*uber_box(), UBER_W, UBER_H))
        minmode(uber, *uber_box(True))
    pipes = kv.find(body, 'HudDemomanPipes')
    kv.setmany(pipes, **box(*pipes_pos(), PIPES_W, PIPES_H))
    minmode(pipes, *pipes_pos(True))
    for n, y, y_alt in zip(('CMainTargetID', 'CSecondaryTargetID'), target_id_ys(), target_id_ys(True)):
        blk = kv.find(body, n)
        kv.set(blk, 'ypos', y)
        minmode(blk, None, y_alt)
    kv.setmany(kv.find(body, 'HudVoiceSelfStatus'), ypos=min(weapon_pos(alt)[1] for alt in LAYOUTS) - 38)
    for n, y in (('HudTeamGoal', 65), ('HudTeamSwitch', 75), ('HudAlert', 130)):
        kv.setmany(kv.find(body, n), xpos='c-%d' % (NOTICE_W // 2), ypos=y, wide=NOTICE_W, tall=NOTICE_H + 8)
    # kill feed: the game draws each row as a plain box (no art possible), so it is styled as stacked manga strips:
    # sharp ink strips, your own kills on bone-jade paper, bold outlined lettering, tight gutters. The info text on
    # your rows ("is DOMINATING"...) is emerald: ink text inside the ink outline closed up. The feed starts below
    # the casual team strip (portraits + dead skull tags reach ~40), which covered long rows
    dn = kv.find(body, 'HudDeathNotice')
    kv.setmany(dn, xpos='r640', ypos=44, wide=630, tall=430, MaxDeathNotices=5, IconScale='0.33', LineHeight=17,
               LineSpacing=2, CornerRadius=0, RightJustify=1, TextFont='HM_Killfeed', TeamBlue='HM_TeamBlue',
               TeamRed='HM_TeamRed', IconColor='HM_Bone', LocalPlayerColor='30 140 92 255',
               BaseBackgroundColor='8 8 10 225', LocalBackgroundColor='214 232 222 240')
    # hitmarker: flashed by the DamagedPlayer animation (ANIMS_HITMARKER)
    hm = kv.add_block(body, 'HM_Hitmarker', img_panel('HM_Hitmarker', 'c-12', 'c-12', 24, 24, 'hitmarker', z=10))
    hm.append(['alpha', '0', None])


HUD_VMT = ('"UnlitGeneric"\n{\n\t"$baseTexture"\t"vgui/replay/thumbnails/hm/%s"\n\t"$translucent"\t"1"\n'
           '\t"$vertexcolor"\t"1"\n\t"$vertexalpha"\t"1"\n\t"$no_fullbright"\t"1"\n\t"$ignorez"\t"1"\n}\n')


def redirect_objective_materials():
    """Point the stock control-point / flag materials at our thumbnails (same trick as other HUDs).
    Note: sv_pure servers may keep the stock look for these, everything else is unaffected."""
    src = os.path.join(OUT, 'materials', 'vgui', 'replay', 'thumbnails', 'hm', 'obj')
    for f in sorted(os.listdir(src)):
        if not f.endswith('.vtf'):
            continue
        name = f[:-4]
        folder = 'hud' if name.startswith('objectives_') else os.path.join('sprites', 'obj_icons')
        write(os.path.join(OUT, 'materials', folder, name + '.vmt'), HUD_VMT % ('obj/' + name))
    # the health gauge fill is drawn by the game from hud/health_color (bottom-up), so point it at our bone fill
    # (ignored on sv_pure servers; hp_mask keeps the gauge looking the same with the stock fill)
    write(os.path.join(OUT, 'materials', 'hud', 'health_color.vmt'), HUD_VMT % 'hp_fill')
    # server-sent HUD notifications set these backgrounds in code (not from a .res): our notification cards
    for stock, ours in (('score_panel_red_bg', 'notif_red'), ('score_panel_blue_bg', 'notif_blue'),
                        ('notification_black', 'notif_ink')):
        write(os.path.join(OUT, 'materials', 'hud', stock + '.vmt'), HUD_VMT % ours)


CREDIT = '// Hueco Mundo HUD - made by Ingalther Ulquiorra. Licence: CC BY-NC-SA 4.0 (credit required, no selling).\n'


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if path.endswith(('.res', '.txt')) and not text.startswith('//'):
        text = CREDIT + text
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(text)


ANIMS = r'''// Hueco Mundo HUD - health / ammo feedback (loaded before hudanimations_tf.txt, so these win)

event HudHealthBonusPulse
{
	Animate PlayerStatusHealthValue		FgColor	"HM_Emerald"	Linear 0.0 0.0
	Animate PlayerStatusHealthBonusImage	Alpha	"150"	Linear 0.0 0.35
	Animate PlayerStatusHealthBonusImage	Alpha	"30"	Linear 0.35 0.45
	RunEvent HudHealthBonusPulseLoop	0.8
}
event HudHealthBonusPulseLoop
{
	RunEvent HudHealthBonusPulse 0.0
}
event HudHealthBonusPulseStop
{
	StopEvent HudHealthBonusPulse 0.0
	StopEvent HudHealthBonusPulseLoop 0.0
	Animate PlayerStatusHealthValue		FgColor	"HM_Bone"	Linear 0.0 0.0
	Animate PlayerStatusHealthBonusImage	Alpha	"0"	Linear 0.0 0.0
}

event HudHealthDyingPulse
{
	Animate PlayerStatusHealthValue		FgColor	"HM_Crimson"	Linear 0.0 0.0
	Animate PlayerStatusHealthBonusImage	Alpha	"200"	Linear 0.0 0.1
	Animate PlayerStatusHealthBonusImage	Alpha	"0"		Linear 0.15 0.2
	Animate PlayerStatusHealthValue		FgColor	"HM_Bone"	Linear 0.2 0.15
	RunEvent HudHealthDyingPulseLoop	0.45
}
event HudHealthDyingPulseLoop
{
	RunEvent HudHealthDyingPulse 0.0
}
event HudHealthDyingPulseStop
{
	StopEvent HudHealthDyingPulse 0.0
	StopEvent HudHealthDyingPulseLoop 0.0
	Animate PlayerStatusHealthValue		FgColor	"HM_Bone"	Linear 0.0 0.0
	Animate PlayerStatusHealthBonusImage	Alpha	"0"	Linear 0.0 0.0
}

// casual / competitive matches move the chat back to the stock spot on their own; keep it where the HUD puts it
event CompetitiveGame_LowerChatWindow
{
	Animate HudChat ypos 200 Accel 0 0
}
event CompetitiveGame_RestoreChatWindow
{
	Animate HudChat ypos 200 Accel 0 0
}

event HudLowAmmoPulse
{
	Animate AmmoInClip		FgColor	"HM_Amber"	Linear 0.0 0.0
	Animate AmmoNoClip		FgColor	"HM_Amber"	Linear 0.0 0.0
	Animate HudWeaponLowAmmoImage	Alpha	"170"	Linear 0.0 0.1
	Animate HudWeaponLowAmmoImage	Alpha	"0"		Linear 0.15 0.2
	Animate AmmoInClip		FgColor	"HM_Bone"	Linear 0.2 0.15
	Animate AmmoNoClip		FgColor	"HM_Bone"	Linear 0.2 0.15
	RunEvent HudLowAmmoPulseLoop	0.45
}
event HudLowAmmoPulseLoop
{
	RunEvent HudLowAmmoPulse 0.0
}
event HudLowAmmoPulseStop
{
	StopEvent HudLowAmmoPulse 0.0
	StopEvent HudLowAmmoPulseLoop 0.0
	Animate AmmoInClip		FgColor	"HM_Bone"	Linear 0.0 0.0
	Animate AmmoNoClip		FgColor	"HM_Bone"	Linear 0.0 0.0
	Animate HudWeaponLowAmmoImage	Alpha	"0"	Linear 0.0 0.0
}

// ÜberCharge ready: the jade bar breathes emerald <-> pale jade instead of the stock tan flash
event HudMedicCharged
{
	Animate ChargeMeter		FgColor	"46 214 140 255"	Linear 0.0 0.1
	Animate ChargeMeter		FgColor	"170 198 181 255"	Linear 0.3 0.3
	RunEvent HudMedicChargedLoop	0.6
}
event HudMedicChargedLoop
{
	RunEvent HudMedicCharged 0.0
}
event HudMedicChargedStop
{
	StopEvent HudMedicCharged 0.0
	StopEvent HudMedicChargedLoop 0.0
	Animate ChargeMeter		FgColor	"170 198 181 255"	Linear 0.0 0.0001
}
'''


ANIMS_HITMARKER = r'''
// hitmarker (your damage on an enemy). Restarted through its own event: re-running DamagedPlayer on
// every hit would stack its animations (the well-known hitmarker lag)
event DamagedPlayer
{
	StopEvent HM_HitmarkerFlash 0.0
	RunEvent HM_HitmarkerFlash 0.0
}
event HM_HitmarkerFlash
{
	Animate HM_Hitmarker	Alpha	"255"	Linear 0.0 0.0
	Animate HM_Hitmarker	Alpha	"0"		Linear 0.08 0.22
}
'''

# ------------------------------------------------------------------ respawn card, menus, objectives
SPEC_HINTS = ('ClassOrTeamLabel', 'SwitchCamModeKeyLabel', 'SwitchCamModeLabel', 'CycleTargetFwdKeyLabel',
              'CycleTargetFwdLabel', 'CycleTargetRevKeyLabel', 'CycleTargetRevLabel', 'TipLabel')


def patch_spectator(root):
    """Spectator / death screen (spectator.res, spectatortournament.res).
    - The black letterbox bars are gone. The game shows them again in code on every scheme load and only sizes them
      from the file (the top bar keeps its tall, the bottom one runs from its ypos to the screen bottom), so they
      are shrunk to nothing instead of hidden.
    - The key hints, map name and tip that sat on the bars get outlined lettering so they read over the map.
    - "Respawn in X seconds" sits on a torn manga card that is the label's own border: the game hides the label
      whenever there is no respawn timer (spectator team, freezecam), and the card goes with it."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    for name, vals in (('topbar', dict(tall=0, visible=0)),
                       ('BottomBar', dict(ypos=9999, wide=0, tall=0, visible=0)),
                       ('bottombarblank', dict(ypos='r0', tall=0, visible=0))):
        blk = kv.find(body, name)
        if blk is not None:
            kv.setmany(blk, **vals)
    for name in SPEC_HINTS:
        blk = kv.find(body, name)
        if blk is not None:
            kv.set(blk, 'font', 'HM_SpecHint')
    blk = kv.find(body, 'MapLabel')
    if blk is not None:
        kv.set(blk, 'font', 'HM_SpecMap')
    kv.remove(body, 'HM_RespawnCard')  # older builds drew the card as a separate (always visible) image
    lbl = kv.find(body, 'ReinforcementsLabel')
    if lbl is None:
        return
    # the game creates this one as a plain vgui Label: fgcolor_override, not fgcolor. The card ends above the
    # game's "Press [ , ] to Change Class" line (ypos 68)
    kv.remove(lbl, 'fgcolor')
    kv.setmany(lbl, xpos='c-160', ypos=37, wide=320, tall=29, zpos=2, font='HM_NoticeTitle', fgcolor_override='HM_Bone',
               textAlignment='center', paintbackground=0, paintborder=1, border='HM_RespawnCard')


MENU_DIRS = ('resource/ui/build_menu/', 'resource/ui/destroy_menu/', 'resource/ui/disguise_menu/')
MENU_ICONS = {'hud_menu_bg': 'menu_bg', 'ico_key_blank': 'menu_key'}
MENU_STATES = (('cant_afford', 'red'), ('already_built', 'dim'), ('unavailable', 'dim'), ('inactive', 'dim'))


def patch_menu(root, rel):
    """Engineer build / destroy and spy disguise menus. Their tan backgrounds, slot cards and key chips are
    icons from the game's texture list (CIconPanel), so they are hidden and torn manga art is laid in their place:
    ink sheet, slot cards toned by state (emerald ready, grey built / unavailable, crimson not enough metal),
    emerald key chips."""
    body = next((e[1] for e in root if isinstance(e[1], list)), None)
    if body is None or '/pipboy/' in rel:  # the PDA skin's menus keep their own art
        return
    state = next((st for key, st in MENU_STATES if key in rel.split('/')[-1]), 'on')
    for ent in list(body):
        blk = ent[1]
        if not isinstance(blk, list):
            continue
        icon = (kv.get(blk, 'icon') or '').lower()
        img = MENU_ICONS.get(icon) or ('menu_item_' + state if icon.startswith('hud_menu_item_bg') else None)
        if ent[0] == 'Divider':
            kv.setmany(blk, fillcolor='46 214 140 200', tall=1)
        # blocks the stock file hides are shown by code only in some modes (the disguise menu's group chips, over
        # the 2 / 5 / 8 slots): an always-visible copy would cover those slots' numbers, so they keep the stock art
        if img is None or kv.get(blk, 'visible') == '0':
            continue
        x, y, w, h, z = (kv.get(blk, key) or '0' for key in ('xpos', 'ypos', 'wide', 'tall', 'zpos'))
        kv.setmany(blk, visible=0, wide=0, tall=0)
        kv.add_block(body, 'HM_' + ent[0], img_panel('HM_' + ent[0], x, y, w, h, img, z=z))
    for ent in body:  # the key numbers share the chip's zpos in some menus (disguise), so lift them over it
        if isinstance(ent[1], list) and 'numberlabel' in (kv.get(ent[1], 'fieldName') or ent[0]).lower():
            kv.set(ent[1], 'zpos', 3)


def patch_disguise_status(root):
    """The "disguised as" box on a torn notice card (team tone of the disguise)."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    bg = kv.find(body, 'DisguiseStatusBG')
    if bg is None:
        return
    kv.setmany(bg, image=T + 'disguise_card', teambg_1=T + 'disguise_card', teambg_2=T + 'disguise_card',
               teambg_3=T + 'disguise_card', src_corner_width=40, src_corner_height=40, draw_corner_width=5,
               draw_corner_height=5)
    for key in ('teambg_2_lodef', 'teambg_3_lodef'):
        kv.remove(bg, key)


def patch_escort(root):
    """Payload track on a torn manga strip (single cart; the multi-cart layout keeps the stock look)."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    if kv.find(body, 'LevelBar') is None:
        return
    strip = kv.add_block(body, 'HM_EscortStrip', img_panel('HM_EscortStrip', 50, 106, 300, 40, 'escort_strip', z=-1))
    strip.append(['if_multiple_trains', [['visible', '0', None], ['wide', '0', None]], None])


def patch_cp_progress(root):
    """Capture progress ring gets a torn ink rim instead of the tan teardrop."""
    body = next(e[1] for e in root if isinstance(e[1], list))
    for n in ('Teardrop', 'TeardropSide'):
        blk = kv.find(body, n)
        if blk is not None:
            kv.setmany(blk, visible=0, wide=0, tall=0)
    kv.add_block(body, 'HM_CpRim', img_panel('HM_CpRim', 22, -1, 57, 57, 'cp_rim', z=21))


def main():
    install = '--install' in sys.argv
    work = tempfile.mkdtemp(prefix='hm_stock_')
    vpk.extract('../hl2/hl2_misc', ['resource/ui/basechat.res'], work)
    n = vpk.extract('tf2_misc', ['resource/*.res', 'resource/ui/*.res', 'resource/ui/*/*.res',
                                 'resource/ui/*/*/*.res', 'resource/ui/*/*/*/*.res', 'scripts/hudlayout.res',
                                 'scripts/hudanimations_manifest.txt'], work)
    print(f'extracted {n} stock files')
    for entry in HUD_PARTS:  # only the HUD parts: tools/, docs/, README... stay
        p = os.path.join(OUT, entry)
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)

    custom = {
        'resource/ui/hudplayerhealth.res': patch_health,
        'resource/ui/hudplayerclass.res': patch_class,
        'resource/ui/hudammoweapons.res': patch_ammo,
        'resource/ui/huddamageaccount.res': patch_damage,
        'resource/ui/mainmenuoverride.res': screens.mainmenu,
        'resource/ui/matchmakingdashboard.res': screens.dashboard,
        'resource/ui/classselection.res': screens.classselection,
        'resource/ui/charinfopanel.res': screens.charinfo,
        'resource/ui/charinfoloadoutsubpanel.res': screens.loadout_sub,
        'resource/ui/classloadoutpanel.res': screens.overlay_page('class_loadout_panel'),
        'resource/ui/econ/backpackpanel.res': screens.overlay_page('backpack_panel'),
        'resource/ui/scoreboard.res': screens.scoreboard,
        'scripts/hudlayout.res': patch_hudlayout,
        'resource/ui/hudaccountpanel.res': patch_account,
        'resource/ui/huditemeffectmeter_killstreak.res': patch_killstreak,
        'resource/ui/teammenu.res': screens.teammenu,
        'resource/ui/hudobjectiveflagpanel.res': patch_flagpanel,
        'resource/ui/flagstatus.res': patch_flagstatus,
        'resource/ui/basechat.res': patch_chat,
        'resource/ui/statsummary.res': screens.statsummary,
        'resource/ui/spectatorguihealth.res': patch_spec_health,
        'resource/ui/spectatortournamentguihealth.res': patch_spec_health,
        'resource/ui/huddemomanpipes.res': patch_pipes,
        'resource/ui/hudmediccharge.res': patch_uber,
        'resource/ui/hudkillstreaknotice.res': patch_streak_notice,
        'resource/ui/hudmatchstatus.res': patch_matchstatus,
        'resource/ui/winpanel.res': screens.winpanel,
        'resource/ui/freezepanel_basic.res': patch_freezepanel,
        'resource/ui/statpanel_base.res': patch_statpanel,
        'resource/ui/hudtournament.res': patch_tournament,
        'resource/ui/targetid.res': patch_targetid,
        'resource/ui/mapinfomenu.res': screens.mapinfo,
        'resource/ui/spectator.res': patch_spectator,
        'resource/ui/spectatortournament.res': patch_spectator,
        'resource/ui/spectator_sc.res': patch_spectator,  # Steam Controller variant
        'resource/ui/disguisestatuspanel.res': patch_disguise_status,
        'resource/ui/objectivestatusescort.res': patch_escort,
        'resource/ui/controlpointprogressbar.res': patch_cp_progress,
        'resource/ui/hudrocketpack.res': patch_rocketpack,
        'resource/ui/hudinspectpanel.res': patch_inspect,
        'resource/ui/huditemattributetracker.res': patch_tracker,
    }
    medic = os.path.join(work, 'resource', 'ui', 'hudmediccharge.res')
    if not os.path.exists(medic):
        write(medic, STOCK_MEDIC)
    shipped = 0
    for dirpath, _, files in os.walk(work):
        for fn in files:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, work).replace('\\', '/').lower()
            if not rel.endswith('.res') or rel in ('resource/clientscheme.res', 'resource/sourcescheme.res',
                                                  'resource/chatscheme.res'):
                continue
            text = open(full, encoding='utf-8', errors='replace').read()
            root = kv.parse(text)
            changed = reskin_res(root)
            changed |= strip_minmode(root)
            if METER_FILE.search(rel) and not rel.endswith('killstreak.res'):  # first: the card patches refine it
                patch_meter_style(root)
                changed = True
            if rel in custom:
                custom[rel](root)
                changed = True
            elif rel.startswith('resource/ui/hud_obj_'):
                patch_building(root, rel)
                changed = True
            elif rel.startswith('resource/ui/notifications/'):
                patch_notification(root, rel)
                changed = True
            elif rel in NOTICES:
                patch_notice(root, rel)
                changed = True
            elif rel.split('/')[-1] in METER_CARDS:
                patch_meter_card(root, rel)
                changed = True
            elif rel.startswith('resource/ui/huditemeffectmeter'):
                patch_meter(root)
                changed = True
            elif rel.startswith(MENU_DIRS):
                patch_menu(root, rel)
                changed = True
            if changed:
                write(os.path.join(OUT, rel), kv.dump(root) + '\n')
                shipped += 1
    print(f'  res files shipped: {shipped}')

    write(os.path.join(OUT, 'resource/clientscheme.res'),
          build_scheme(open(os.path.join(work, 'resource/clientscheme.res'), encoding='utf-8', errors='replace').read()))
    ss = os.path.join(work, 'resource/sourcescheme.res')
    if os.path.exists(ss):  # GameUI dialogs (loading window...) take their colours from here
        write(os.path.join(OUT, 'resource/sourcescheme.res'),
              retint_scheme(open(ss, encoding='utf-8', errors='replace').read()))
    write(os.path.join(OUT, 'scripts/hudanimations_hm.txt'), ANIMS + ANIMS_HITMARKER)
    write(os.path.join(OUT, 'scripts/hudanimations_manifest.txt'),
          'hudanimations_manifest\n{\n\t"file"\t\t"scripts/hudanimations.txt"\n'
          '\t"file"\t\t"scripts/hudanimations_hm.txt"\n\t"file"\t\t"scripts/hudanimations_tf.txt"\n}\n')
    bgs = '\n'.join(f'\t{i}\t"background_huecomundo"' for i in range(1, 5))
    write(os.path.join(OUT, 'scripts/chapterbackgrounds.txt'),
          f'"chapters"\n{{\n{bgs}\n}}\n"BackgroundMaps"\n{{\n{bgs}\n}}\n')
    write(os.path.join(OUT, 'info.vdf'), f'"{HUD_NAME}"\n{{\n\t"ui_version"\t"3"\n}}\n')

    print('  generating artwork...')
    pdir = os.path.join(work, 'tex')
    vpk.extract('tf2_textures', ['materials/vgui/class_portraits/*.vtf', 'materials/vgui/class_sel_sm_*.vtf',
                                 'materials/sprites/obj_icons/*.vtf', 'materials/hud/objectives_flagpanel*.vtf'], pdir)
    build_art.build(OUT, portraits=pdir)
    redirect_objective_materials()
    shutil.rmtree(work, ignore_errors=True)
    print('built ->', OUT)

    if install:
        dst = os.path.join(vpk.TF, 'custom', HUD_NAME)
        remove_other_copies(OUT if IN_CUSTOM else dst)
        if IN_CUSTOM:  # already in tf/custom: the build above was the install
            dst = OUT
        else:
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            os.makedirs(dst)
            for entry in HUD_PARTS + ('README.txt', 'LICENSE.txt'):
                src = os.path.join(OUT, entry)
                if os.path.isdir(src):
                    shutil.copytree(src, os.path.join(dst, entry))
                elif os.path.exists(src):
                    shutil.copy(src, os.path.join(dst, entry))
        print('installed ->', dst)
        set_desktop_icon(os.path.join(dst, 'resource', 'game.ico'))


def is_our_install(path):
    vdf = os.path.join(path, 'info.vdf')
    return os.path.isfile(vdf) and HUD_NAME in open(vdf, encoding='utf-8', errors='replace').read()


def remove_other_copies(keep):
    """Two copies of the HUD in tf/custom load together and mix their files (counters drawn from one copy's
    layout with the other's panels go missing or land off screen). Plain installed copies (an older
    custom/huecomundo-hud, an extra ZIP folder) are removed; a project folder (with .git or tools) is only
    reported, since it may hold someone's work."""
    custom = os.path.join(vpk.TF, 'custom')
    if not os.path.isdir(custom):
        return
    for entry in sorted(os.listdir(custom)):
        p = os.path.join(custom, entry)
        if not os.path.isdir(p) or os.path.normcase(os.path.abspath(p)) == os.path.normcase(os.path.abspath(keep)):
            continue
        if not is_our_install(p):
            continue
        if os.path.exists(os.path.join(p, '.git')) or os.path.isdir(os.path.join(p, 'tools')):
            print('WARNING: another Hueco Mundo HUD folder is in tf/custom and loads together with this one:', p)
            print('         delete one of them (keep the one you run update.bat in), then restart TF2.')
        else:
            shutil.rmtree(p)
            print('removed another copy of the HUD (two copies mix their files) ->', p)


def set_desktop_icon(ico):
    """Point the Steam desktop shortcut at the HUD's icon (original line kept as a comment)."""
    url = os.path.join(os.path.expanduser('~'), 'Desktop', 'Team Fortress 2.url')
    if not os.path.exists(url):
        return
    lines = open(url, encoding='utf-8', errors='replace').read().splitlines()
    if not any(l.startswith(';orig ') for l in lines):
        lines += [';orig ' + l for l in lines if l.startswith('IconFile=')]
    lines = ['IconFile=' + ico if l.startswith('IconFile=') else l for l in lines]
    open(url, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('desktop shortcut icon ->', ico)


if __name__ == '__main__':
    main()
