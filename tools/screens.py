"""Full-screen menus: main menu, matchmaking bar, class select, inventory, scoreboard."""
import os

import kv

# the HUD's version (VERSION at the project root): shown small in the main menu's bottom right corner, and the
# number of the GitHub release
VERSION = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'VERSION'),
               encoding='utf-8').read().strip()

T = 'replay/thumbnails/hm/'
SCENE = '../console/background_huecomundo_widescreen'
OFF = 9999  # parks a panel off screen; code can still toggle it without it showing up


def _root(root):
    return next(e[1] for e in root if isinstance(e[1], list))


def _block(name, entries):
    return [[k, v if isinstance(v, list) else str(v), None] for k, v in entries.items()]


def add(body, name, entries, first=False):
    kv.remove(body, name)
    ent = [name, _block(name, entries), None]
    if first:
        body.insert(1, ent)
    else:
        body.append(ent)


def image(name, x, y, w, h, img, z=0, drawcolor=None, **extra):
    e = {'ControlName': 'ImagePanel', 'fieldName': name, 'xpos': x, 'ypos': y, 'zpos': z, 'wide': w, 'tall': h,
         'visible': 1, 'enabled': 1, 'scaleImage': 1, 'image': img, 'mouseinputenabled': 0}
    if drawcolor:
        e['drawcolor'] = drawcolor
    e.update(extra)
    return e


def box(name, x, y, w, h, z=0, bg=None, border=None):
    e = {'ControlName': 'EditablePanel', 'fieldName': name, 'xpos': x, 'ypos': y, 'zpos': z, 'wide': w, 'tall': h,
         'visible': 1, 'enabled': 1, 'mouseinputenabled': 0}
    if bg:
        e['bgcolor_override'] = bg
        e['PaintBackgroundType'] = 0
    if border:
        e['border'] = border
        e['paintborder'] = 1
    return e


def scene_backdrop(body, z=-30, shade=150):
    """Hueco Mundo scene behind a full-screen menu, dimmed so the UI on top stays readable."""
    add(body, 'HM_Scene', image('HM_Scene', 0, 0, 'f0', 480, SCENE, z=z), first=True)
    add(body, 'HM_SceneShade', image('HM_SceneShade', 0, 0, 'f0', 480, T + 'shade_full', z=z + 1,
                                     drawcolor=f'255 255 255 {shade}'), first=True)


def nav_button(blk, y, label=None):
    kv.setmany(blk, xpos=24, ypos=y, zpos=5, wide=236, tall=24, visible=1, font='HM_Menu', textAlignment='west',
               textinsetx=32, use_proportional_insets=1, paintbackground=0, border_default='HM_Nav',
               border_armed='HM_NavArmed', border_depressed='HM_NavArmed', border_selected='HM_NavArmed',
               defaultFgColor_override='196 198 194 255', armedFgColor_override='255 255 255 255',
               depressedFgColor_override='46 214 140 255', selectedFgColor_override='255 255 255 255',
               image_drawcolor='150 152 150 255', image_armedcolor='46 214 140 255', pinCorner=0)
    if label is not None:
        kv.set(blk, 'labelText', label)
    sub = kv.find(blk, 'SubImage')
    if sub is not None:
        kv.setmany(sub, xpos=10, ypos=6, wide=12, tall=12)


# ------------------------------------------------------------------ main menu
def mainmenu(root):
    body = kv.find(root, 'Resource/UI/MainMenuOverride.res')
    # the 16:9 scene fills the height at every aspect ratio, right-aligned: TF2's if_wider is any ratio >= 1.6, and a
    # width-filling scene left 16:10 screens a black band along the bottom. Narrower screens lose the scene's left
    # edge, ultrawide ones get black left of it; both under the sidebar, where the scene is shaded to ink anyway
    bg = kv.find(body, 'Background')
    bg[:] = [e for e in bg if not (isinstance(e[1], list) and e[0].lower().startswith(
        ('if_halloween', 'if_fullmoon', 'if_christmas', 'if_wider', 'if_taller')))]
    kv.setmany(bg, visible=1, image=SCENE, xpos='rs1', wide='o1.778', tall='f0')

    add(body, 'HM_Sidebar', image('HM_Sidebar', 0, 0, 310, 'f0', T + 'sidebar', z=-60))
    add(body, 'HM_MenuKanji', image('HM_MenuKanji', 'r34', 200, 16, 32, T + 'kanji_huecomundo', z=-50,
                                    drawcolor='226 226 220 90'))
    logo = kv.find(body, 'TFLogoImage')
    kv.setmany(logo, xpos=20, ypos=34, wide=240, tall=60, image=T + 'logo')

    # TF2's holidays: the game loads this file with if_fullmoon (real full-moon nights), if_halloween or if_christmas
    # set, one at a time. Hueco Mundo's eternal crescent turns full (with Ulquiorra's last words beside it), the
    # Halloween night gets bats, green mist and Hollow masks, Smissmas snow and a star on Las Noches (build_art)
    from build_art import MENU_VARIANTS
    for v in MENU_VARIANTS:
        kv.add_block(bg, f'if_{v}', {'image': f'../console/background_huecomundo_{v}_widescreen'})
        kv.add_block(logo, f'if_{v}', {'image': T + 'logo_' + v})
    kv.setmany(kv.find(body, 'TFCharacterImage'), visible=0, wide=0, tall=0)

    # profile / rank block: stock is centre-anchored, re-anchor it to the sidebar (absolute, any aspect ratio)
    # the medal model is drawn over the name labels, and a high-level medal (wings, spikes, stars) reached 12 units
    # into the name / "Casual" / "Level" lines and up over the logo's credit line. Its panel is 85 % size (the model
    # scales with it) and centred at (45, 127): the medal fills x 10..82, y 98..159, left of the text, under the logo
    kv.setmany(kv.find(body, 'RankModelPanel'), xpos=-380, ypos=-298, wide=850, tall=850)
    kv.setmany(kv.find(body, 'CycleRankTypeButton'), xpos=262, ypos=101)
    kv.setmany(kv.find(body, 'RankTooltipPanel'), xpos=29, ypos=101)
    kv.setmany(kv.find(body, 'NoGCMessage'), xpos=24, ypos=96)
    kv.setmany(kv.find(body, 'NoGCImage'), xpos=29, ypos=109)
    kv.setmany(kv.find(body, 'RankBorder'), xpos=24, ypos=96)
    kv.setmany(kv.find(body, 'RankPanel'), xpos=-36, ypos=74)

    # vertical navigation
    y = 172
    for name, lbl in (('CharacterSetupButton', None), ('GeneralStoreButton', None), ('SettingsButton', 'Options'),
                      ('TF2SettingsButton', 'Advanced Options'), ('AchievementsButton', 'Achievements'),
                      ('WorkshopButton', 'Workshop'), ('ReplayButton', 'Replays')):
        blk = kv.find(body, name)
        if blk is not None:
            nav_button(blk, y, lbl)
            y += 26
    hud_settings_button(body, y)
    kv.setmany(kv.find(body, 'StoreHasNewItemsImage'), xpos=236, ypos=198, wide=20, tall=20)
    for name in ('CommentaryButton', 'CoachPlayersButton', 'NewUserForumsButton', 'ReportBugButton',
                 'VRBGPanel', 'VRModeButton', 'EventPromo', 'SettingsButtonSDK', 'TF2SettingsButtonSDK'):
        blk = kv.find(body, name)
        if blk is not None:
            kv.set(blk, 'xpos', OFF)

    # small icon rows at the foot of the sidebar
    # the MOTD panel is the HUD Settings popup now (hud_settings_popup), so its own icon goes
    for i, name in enumerate(('Notifications_ShowButtonPanel', 'QuestLogButton', 'WatchStreamButton')):
        kv.setmany(kv.find(body, name), xpos=24 + i * 34, ypos=436, wide=28, tall=28)
    kv.set(kv.find(body, 'MOTD_ShowButtonPanel'), 'xpos', OFF)
    for i, name in enumerate(('ReportPlayerButton', 'CallVoteButton', 'MutePlayersButton', 'RequestCoachButton')):
        kv.setmany(kv.find(body, name), xpos=24 + i * 30, ypos=400)
    kv.setmany(kv.find(body, 'BackToReplaysButton'), xpos=24, ypos=372)
    kv.setmany(kv.find(body, 'FriendsContainer'), xpos='r284', ypos=262)
    hud_settings_popup(kv.find(body, 'MOTD_Panel'))
    title = kv.find(kv.find(body, 'Notifications_Panel') or [], 'Notifications_TitleLabel')
    if title is not None:  # stock draws it dark for the tan bubble; the panel is ink now
        kv.set(title, 'fgcolor', '226 226 220 255')
    kv.setmany(kv.find(body, 'Notifications_Panel'), xpos=270, ypos=300)
    for n in ('BackgroundFooter', 'FooterLine'):
        kv.setmany(kv.find(body, n), visible=0, wide=0, tall=0)
    add(body, 'HM_Credit', {'ControlName': 'CExLabel', 'fieldName': 'HM_Credit', 'xpos': 'r290', 'ypos': 'r16',
                            'zpos': 1, 'wide': 280, 'tall': 12, 'visible': 1, 'enabled': 1, 'mouseinputenabled': 0,
                            'labelText': f'Hueco Mundo HUD v{VERSION}  -  made by Ingalther Ulquiorra',
                            'textAlignment': 'east',
                            'font': 'HM_Small', 'fgcolor': '150 152 150 110'})


# ------------------------------------------------------------------ HUD Settings popup
# vgui res files cannot open a new window, so the popup reuses the stock MOTD panel: the main menu code shows it on
# "motd_show" and hides it on "motd_hide". Its news widgets are parked and replaced with the layout picker.
# The two layouts are the plain / *_minmode keys of the in-game clusters (build.py LAYOUTS); picking one sets
# cl_hud_minmode and reloads the HUD.
LAYOUT_OPTIONS = [  # (button, preview art, cl_hud_minmode, name, description)
    ('HM_LayoutCentered', 'layout_centered', 0, 'CENTERED', 'Pulled in toward the crosshair (default)'),
    ('HM_LayoutCorners', 'layout_corners', 1, 'CORNERS', 'Health and ammo in the bottom corners'),
]
POPUP_W, POPUP_H = 372, 264
CHARACTER_OPTIONS = (('HM_Char3D', '3D MODEL', 1), ('HM_Char2D', '2D IMAGE', 0))  # cl_hud_playerclass_use_playermodel


def hud_settings_button(body, y):
    """'HUD Settings' entry at the end of the sidebar menu, styled like the stock entries above it."""
    blk = _block('HM_HudSettingsButton', {
        'ControlName': 'CExImageButton', 'fieldName': 'HM_HudSettingsButton', 'autoResize': 0, 'visible': 1,
        'enabled': 1, 'tabPosition': 0, 'labelText': 'HUD Settings', 'dulltext': 0, 'brighttext': 0, 'default': 1,
        'Command': 'motd_show', 'sound_depressed': 'UI/buttonclick.wav', 'sound_released': 'UI/buttonclickrelease.wav'})
    blk.append(['SubImage', _block('SubImage', {'ControlName': 'ImagePanel', 'fieldName': 'SubImage', 'zpos': 1,
                                                'visible': 1, 'enabled': 1, 'image': 'glyph_options',
                                                'scaleImage': 1}), None])
    kv.remove(body, 'HM_HudSettingsButton')
    body.append(['HM_HudSettingsButton', blk, None])
    nav_button(blk, y)


def hud_settings_popup(motd):
    kv.setmany(motd, xpos='c-%d' % (POPUP_W // 2), ypos=110, zpos=60, wide=POPUP_W, tall=POPUP_H, border='',
               paintborder=0, PaintBackgroundType=0, bgcolor_override='0 0 0 0')
    for e in motd:
        if isinstance(e[1], list) and e[0].startswith('MOTD_') and e[0] != 'MOTD_CloseButton':
            kv.setmany(e[1], xpos=OFF, visible=0)
    kv.setmany(kv.find(motd, 'MOTD_CloseButton'), xpos=POPUP_W - 30, ypos=14, zpos=10, wide=14, tall=14)
    add(motd, 'HM_PopupBG', image('HM_PopupBG', 0, 0, POPUP_W, POPUP_H, T + 'popup', z=-1))
    add(motd, 'HM_PopupTitle', {'ControlName': 'CExLabel', 'fieldName': 'HM_PopupTitle', 'xpos': 22, 'ypos': 12,
                                'zpos': 2, 'wide': 250, 'tall': 24, 'visible': 1, 'enabled': 1,
                                'labelText': 'HUD SETTINGS', 'textAlignment': 'west', 'font': 'HM_Title',
                                'fgcolor': '226 226 220 255'})
    add(motd, 'HM_PopupSection', {'ControlName': 'CExLabel', 'fieldName': 'HM_PopupSection', 'xpos': 22,
                                  'ypos': 42, 'zpos': 2, 'wide': POPUP_W - 44, 'tall': 12, 'visible': 1, 'enabled': 1,
                                  'labelText': 'HEALTH AND AMMO LAYOUT', 'textAlignment': 'west', 'font': 'HM_Menu',
                                  'fgcolor': '46 214 140 255'})
    for i, (name, img, mode, title, desc) in enumerate(LAYOUT_OPTIONS):
        x = 22 + i * 168
        blk = _block(name, {'fieldName': name, 'visible': 1, 'enabled': 1, 'tabPosition': 0,
                            'sound_depressed': 'UI/buttonclick.wav', 'sound_released': 'UI/buttonclickrelease.wav',
                            'sound_armed': 'UI/buttonrollover.wav'})
        kv.remove(motd, name)
        motd.append([name, blk, None])
        card_button(motd, blk, img, x, 60, 160, 90, f'engine cl_hud_minmode {mode}; hud_reloadscheme')
        # the main menu runs "engine ..." commands only when they reach it: two levels up from inside MOTD_Panel,
        # like the stock close button
        kv.set(blk, 'actionsignallevel', 2)
        for suffix, y, text, font, color in (('Name', 154, title, 'HM_Menu', '226 226 220 255'),
                                             ('Desc', 168, desc, 'HM_Small', '150 152 150 255')):
            add(motd, name + suffix, {'ControlName': 'CExLabel', 'fieldName': name + suffix, 'xpos': x, 'ypos': y,
                                      'zpos': 2, 'wide': 160, 'tall': 12, 'visible': 1, 'enabled': 1,
                                      'labelText': text, 'textAlignment': 'west', 'font': font, 'fgcolor': color})
    note(motd, 'HM_PopupNote0', 184, 'Applies instantly. Same as cl_hud_minmode 0 / 1 in the console.')
    # PLAYER CHARACTER: the live 3D model or TF2's own 2D class art, through the game's own setting (no reload)
    add(motd, 'HM_PopupSection2', {'ControlName': 'CExLabel', 'fieldName': 'HM_PopupSection2', 'xpos': 22,
                                   'ypos': 202, 'zpos': 2, 'wide': POPUP_W - 44, 'tall': 12, 'visible': 1,
                                   'enabled': 1, 'labelText': 'PLAYER CHARACTER', 'textAlignment': 'west',
                                   'font': 'HM_Menu', 'fgcolor': '46 214 140 255'})
    for i, (name, text, value) in enumerate(CHARACTER_OPTIONS):
        popup_button(motd, name, 22 + i * 100, 218, text, f'engine cl_hud_playerclass_use_playermodel {value}')
    note(motd, 'HM_PopupNote3', 238, 'Same as cl_hud_playerclass_use_playermodel 1 / 0 in the console.')


def popup_button(motd, name, x, y, text, command):
    """Flat emerald button inside the popup; actionsignallevel 2 so its "engine ..." command reaches the main menu."""
    add(motd, name, {
        'ControlName': 'CExButton', 'fieldName': name, 'xpos': x, 'ypos': y, 'zpos': 6, 'wide': 92,
        'tall': 18, 'visible': 1, 'enabled': 1, 'tabPosition': 0, 'labelText': text, 'font': 'HM_Menu',
        'textAlignment': 'center', 'Command': command, 'actionsignallevel': 2,
        'paintbackground': 1, 'defaultBgColor_override': '14 46 34 235', 'armedBgColor_override': '28 110 78 255',
        'depressedBgColor_override': '46 214 140 255', 'defaultFgColor_override': '226 226 220 255',
        'armedFgColor_override': '255 255 255 255', 'depressedFgColor_override': '8 9 10 255',
        'sound_depressed': 'UI/buttonclick.wav', 'sound_released': 'UI/buttonclickrelease.wav'})


def note(motd, name, y, text, x=22):
    add(motd, name, {'ControlName': 'CExLabel', 'fieldName': name, 'xpos': x, 'ypos': y, 'zpos': 2,
                     'wide': POPUP_W - x - 18, 'tall': 12, 'visible': 1, 'enabled': 1, 'labelText': text,
                     'textAlignment': 'west', 'font': 'HM_Small', 'fgcolor': '122 124 124 255'})


def dashboard(root):
    body = _root(root)
    top = kv.find(body, 'TopBar')
    kv.setmany(kv.find(top, 'FindAGameButton'), defaultBgColor_override='14 46 34 235',
               armedBgColor_override='28 110 78 255', defaultFgColor_override='226 226 220 255',
               armedFgColor_override='255 255 255 255')
    for n in ('Gradient',):
        blk = kv.find(top, n)
        if blk is not None:
            kv.set(blk, 'visible', 0)


# ------------------------------------------------------------------ class select
CLASS_ORDER = [('scout', 'numScout'), ('soldier', 'numSoldier'), ('pyro', 'numPyro'), ('demoman', 'numDemoman'),
               ('heavyweapons', 'numHeavy'), ('engineer', 'numEngineer'), ('medic', 'numMedic'),
               ('sniper', 'numSniper'), ('spy', 'numSpy'), ('random', None)]


def manga_backdrop(body, shade=150):
    scene_backdrop(body, z=-30, shade=shade)
    add(body, 'HM_Speed', image('HM_Speed', 'c-427', -20, 854, 520, T + 'speed', z=-25, drawcolor='255 255 255 90'), first=True)
    add(body, 'HM_Tone', image('HM_Tone', 0, 'r140', 'f0', 140, T + 'tone', z=-24, drawcolor='255 255 255 22',
                               tileImage=1, scaleImage=0), first=True)
    add(body, 'HM_Lanza', image('HM_Lanza', 'c-440', 250, 880, 220, T + 'lanza', z=-23, drawcolor='255 255 255 120'),
        first=True)


def card_button(body, blk, img, x, y, w, h, command=None):
    """Card = a static ImagePanel underneath (always drawn) + the button on top whose only visual is the hover
    border. The class menu code rewrites button images, and a button's default border is not applied until its
    first state change, so the resting card cannot live on the button itself."""
    name = kv.get(blk, 'fieldName') or 'card'
    add(body, f'HM_Card_{name}', image(f'HM_Card_{name}', x, y, w, h, T + img, z=5))
    kv.setmany(blk, ControlName='CExImageButton', xpos=x, ypos=y, zpos=6, wide=w, tall=h, labelText='',
               paintbackground=0, paintborder=1, scaleImage=1, border_default='HM_Card_none',
               border_armed=f'HM_Card_{img}_h', border_selected=f'HM_Card_{img}_h', border_depressed=f'HM_Card_{img}_h',
               image_drawcolor='0 0 0 0', image_armedcolor='0 0 0 0', image_selectedcolor='0 0 0 0',
               defaultFgColor_override='0 0 0 0', armedFgColor_override='0 0 0 0',
               depressedFgColor_override='0 0 0 0', selectedFgColor_override='0 0 0 0', pinCorner=0)
    for k in ('image_default', 'image_armed', 'image_selected'):
        kv.remove(blk, k)
    if command:
        kv.set(blk, 'Command', command)
    sub = kv.find(blk, 'SubImage')
    if sub is None:
        sub = _block('SubImage', {})
        blk.append(['SubImage', sub, None])
    kv.setmany(sub, ControlName='ImagePanel', fieldName='SubImage', xpos=0, ypos=0, wide=0, tall=0, visible=0,
               image=T + 'blank')


CARD_BORDERS = ['cls_' + c for c, _ in [('scout', 0), ('soldier', 0), ('pyro', 0), ('demoman', 0), ('heavyweapons', 0),
                                          ('engineer', 0), ('medic', 0), ('sniper', 0), ('spy', 0), ('random', 0)]] +                ['team_blu', 'team_red', 'team_auto', 'team_spec', 'layout_centered', 'layout_corners']


def classselection(root):
    body = _root(root)
    kv.setmany(kv.find(body, 'MenuBG'), visible=0, wide=0, tall=0)
    manga_backdrop(body, shade=150)
    add(body, 'HM_ClassTop', image('HM_ClassTop', 0, 0, 'f0', 110, T + 'header', z=-20))
    kv.setmany(kv.find(body, 'ShadedBar'), image=T + 'footer', ypos='r70', tall=70)

    W, H, GAP = 178, 67, 5
    for i, (btn, num) in enumerate(CLASS_ORDER):
        col, row = divmod(i, 5)
        x = 16 if col == 0 else f'r{W + 16}'
        y = 60 + row * (H + GAP)
        card_button(body, kv.find(body, btn), f'cls_{btn}', x, y, W, H)
        if num:
            kv.setmany(kv.find(body, num), xpos=(16 + W - 30) if col == 0 else f'r{16 + 30}', ypos=y + 4, wide=24,
                       tall=14, zpos=9, textAlignment='east', fgcolor='46 214 140 255', font='HM_AmmoSmall')
    for n in ('Offense', 'Defense', 'Support', 'ClassTipsPanel', 'localPlayerImage', 'localPlayerBG', 'CountLabel'):
        blk = kv.find(body, n)
        if blk is not None:
            kv.set(blk, 'xpos', OFF)
    for e in body:
        if isinstance(e[1], list) and e[0].startswith('MvMUpgradeImage'):
            kv.set(e[1], 'xpos', OFF)
    kv.setmany(kv.find(body, 'TFPlayerModel'), xpos='c-196', ypos=-6, wide=480, tall=480)
    kv.setmany(kv.find(body, 'ClassMenuSelect'), font='HM_Title', xpos='c-200', ypos=14, wide=400, tall=30,
               textAlignment='center', fgcolor='226 226 220 255')
    add(body, 'HM_ClassKanji', image('HM_ClassKanji', 'c-9', 46, 18, 36, T + 'kanji_huecomundo', z=2,
                                     drawcolor='46 214 140 160'))
    kv.setmany(kv.find(body, 'CancelButton'), xpos='c-160', ypos='r40', wide=150, tall=26)
    kv.setmany(kv.find(body, 'EditLoadoutButton'), xpos='c10', ypos='r40', wide=150, tall=26)
    kv.setmany(kv.find(body, 'ResetButton'), xpos='c-55', ypos='r72', wide=110, tall=24)


# ------------------------------------------------------------------ team select
def teammenu(root):
    body = _root(root)
    for n in ('MenuBG', 'bluedoor', 'reddoor', 'autodoor', 'spectate'):
        kv.setmany(kv.find(body, n), visible=0, wide=0, tall=0)
    for n in ('teambutton0', 'teambutton1', 'teambutton2', 'teambutton3', 'TeamMenuAuto', 'TeamMenuSpectate'):
        kv.set(kv.find(body, n), 'xpos', OFF)
    manga_backdrop(body, shade=160)
    add(body, 'HM_TeamTop', image('HM_TeamTop', 0, 0, 'f0', 110, T + 'header', z=-20))
    kv.setmany(kv.find(body, 'ShadedBar'), image=T + 'footer', ypos='r70', tall=70)
    for name, img, cmd, x, y, w, h in (
            ('HM_JoinBlue', 'team_blu', 'jointeam blue', 'c-236', 54, 176, 352),
            ('HM_JoinRed', 'team_red', 'jointeam red', 'c60', 54, 176, 352),
            ('HM_JoinAuto', 'team_auto', 'jointeam auto', 'c-62', 176, 124, 47),
            ('HM_JoinSpec', 'team_spec', 'jointeam spectate', 'c-62', 232, 124, 47)):
        blk = _block(name, {'fieldName': name, 'visible': 1, 'enabled': 1, 'tabPosition': 0,
                            'sound_depressed': 'UI/buttonclick.wav', 'sound_released': 'UI/buttonclickrelease.wav',
                            'sound_armed': 'UI/buttonrollover.wav'})
        kv.remove(body, name)
        body.append([name, blk, None])
        card_button(body, blk, img, x, y, w, h, cmd)
    # team player counts on the lower end of each card (behind the card, only the bottom of the digit showed below
    # its edge as a small half circle); no mouse input, so clicks still reach the card's button
    kv.setmany(kv.find(body, 'BlueCount'), xpos='c-236', ypos=356, zpos=7, wide=176, tall=44, textAlignment='center',
               fgcolor='128 160 200 255', font='HM_ScoreBig', mouseinputenabled=0)
    kv.setmany(kv.find(body, 'RedCount'), xpos='c60', ypos=356, zpos=7, wide=176, tall=44, textAlignment='center',
               fgcolor='208 92 92 255', font='HM_ScoreBig', mouseinputenabled=0)
    kv.setmany(kv.find(body, 'TeamMenuSelect'), font='HM_Title', xpos='c-200', ypos=14, wide=400, tall=30,
               textAlignment='center', fgcolor='226 226 220 255')
    add(body, 'HM_TeamKanji', image('HM_TeamKanji', 'c-9', 120, 18, 36, T + 'kanji_huecomundo', z=2,
                                    drawcolor='226 226 220 120'))



# ------------------------------------------------------------------ map info (intro screen before spawning)
def mapinfo(root):
    """Same backdrop as the class / team menus: the stock tan 3D background (MenuBG) goes, Hueco Mundo shows."""
    body = _root(root)
    for e in body:
        if isinstance(e[1], list) and ('bg' in e[0].lower() and (kv.get(e[1], 'ControlName') or '').lower() in
                                       ('cmodelpanel', 'ctfimagepanel', 'imagepanel')):
            kv.setmany(e[1], visible=0, wide=0, tall=0)
    manga_backdrop(body, shade=170)


# ------------------------------------------------------------------ inventory
def charinfo(root):
    body = _root(root)
    kv.set(kv.find(body, 'character_info'), 'bgcolor_override', '0 0 0 0')
    scene_backdrop(body, z=-30, shade=195)
    kv.setmany(kv.find(body, 'BackgroundHeader'), image=T + 'header', tall=110)
    kv.setmany(kv.find(body, 'BackgroundFooter'), image=T + 'footer', ypos=400, tall=80)
    kv.remove(kv.find(body, 'BackgroundFooter'), 'tileImage')
    kv.setmany(kv.find(body, 'FooterLine'), image=T + 'blank', fillcolor='46 214 140 80', tall=1, ypos=424)
    add(body, 'HM_InvMark', image('HM_InvMark', 'r196', 'r48', 180, 45, T + 'emblem', z=5, drawcolor='255 255 255 200'))


def loadout_sub(root):
    body = _root(root)
    kv.set(kv.find(body, 'CharInfoLoadoutSubPanel'), 'bgcolor_override', '0 0 0 0')
    for i, btn in enumerate(('scout', 'soldier', 'pyro', 'demoman', 'heavyweapons', 'engineer', 'medic', 'sniper', 'spy')):
        kv.setmany(kv.find(body, btn), xpos=f'c{-322 + i * 72}', ypos=96, wide=68, tall=136, scaleImage=1,
                   activeimage=T + f'inv_{btn}_a', inactiveimage=T + f'inv_{btn}')
    for n, x in (('ShowBackpackButton', -290), ('ShowCraftingButton', -160), ('ShowArmoryButton', -30),
                 ('ShowTradeButton', 100), ('ShowPaintkitsButton', 230)):
        kv.set(kv.find(body, n), 'ypos', 262)
    kv.set(kv.find(body, 'SelectLabel'), 'ypos', 238)
    # the game grows the class cards near the mouse (z up to 100) over these lines; our cards are opaque, so the
    # red "changes take effect on respawn" note vanished under them: both lines draw above the cards
    for n in ('SelectLabel', 'LoadoutChangesLabel'):
        kv.set(kv.find(body, n), 'zpos', 150)


def overlay_page(name):
    """Sub-pages drawn over the class grid: must stay opaque, so they carry their own copy of the scene."""
    def patch(root):
        body = _root(root)
        blk = kv.find(body, name)
        for k in ('bgcolor_override', 'infocus_bgcolor_override', 'outoffocus_bgcolor_override'):
            if kv.get(blk, k) is not None:
                kv.set(blk, k, '6 7 8 255')
        add(body, 'HM_Scene', image('HM_Scene', 0, -36, 'f0', 480, SCENE, z=-30), first=True)
        add(body, 'HM_SceneShade', image('HM_SceneShade', 0, -36, 'f0', 480, T + 'shade_full', z=-29,
                                         drawcolor='255 255 255 205'), first=True)
    return patch


# ------------------------------------------------------------------ scoreboard
def scoreboard(root):
    body = _root(root)
    # our header font is wider than TF2 Secondary: give "Ping" room so it is not cut to "Pi..."
    kv.setmany(kv.find(body, 'scores'), ping_width=26, name_width=107)
    # one torn manga page for the body (screentone corners, faint 虚圏 between the teams)
    kv.setmany(kv.find(body, 'MainBG'), border='HM_ScoreMain')
    for n in ('BlueScoreBG', 'RedScoreBG', 'BlueTeamImage', 'RedTeamImage'):
        kv.setmany(kv.find(body, n), wide=0, tall=0, image=T + 'blank')
    add(body, 'HM_BlueHead', image('HM_BlueHead', -8, -2, 292, 73, T + 'score_blue', z=0))
    add(body, 'HM_RedHead', image('HM_RedHead', 356, -2, 292, 73, T + 'score_red', z=0))
    # bone kanji stamps on the outer ends of the team banners (青 BLU, 赤 RED); the names move in beside them
    add(body, 'HM_BlueSeal', image('HM_BlueSeal', 8, 9, 28, 32, T + 'score_seal_blue', z=1))
    add(body, 'HM_RedSeal', image('HM_RedSeal', 604, 9, 28, 32, T + 'score_seal_red', z=1))

    # the game only shows the team names in tournament mode (small, under the count then); the player count takes
    # the name's place, big, beside the 青 / 赤 stamp. zpos above the banner art (same zpos drew them under it)
    kv.setmany(kv.find(body, 'BlueTeamLabel'), visible=1, xpos=42, ypos=38, wide=142, tall=14, zpos=5,
               font='ScoreboardTeamCountNew', textAlignment='west', fgcolor='122 124 124 255')
    kv.setmany(kv.find(body, 'BlueTeamPlayerCount'), xpos=42, ypos=12, wide=142, tall=24, zpos=5, font='HM_Title',
               textAlignment='west', fgcolor='226 226 220 255')
    kv.setmany(kv.find(body, 'BlueTeamScore'), xpos=170, ypos=6, wide=96, tall=56, font='HM_ScoreBig',
               textAlignment='east', fgcolor='128 160 200 255')
    kv.setmany(kv.find(body, 'BlueTeamScoreDropshadow'), xpos=171, ypos=7, wide=96, tall=56, font='HM_ScoreBig',
               textAlignment='east', fgcolor='0 0 0 200')
    kv.setmany(kv.find(body, 'RedTeamLabel'), visible=1, xpos=456, ypos=38, wide=142, tall=14, zpos=5,
               font='ScoreboardTeamCountNew', textAlignment='east', fgcolor='122 124 124 255')
    kv.setmany(kv.find(body, 'RedTeamPlayerCount'), xpos=456, ypos=12, wide=142, tall=24, zpos=5, font='HM_Title',
               textAlignment='east', fgcolor='226 226 220 255')
    kv.setmany(kv.find(body, 'RedTeamScore'), xpos=374, ypos=6, wide=96, tall=56, font='HM_ScoreBig',
               textAlignment='west', fgcolor='208 92 92 255')
    kv.setmany(kv.find(body, 'RedTeamScoreDropshadow'), xpos=375, ypos=7, wide=96, tall=56, font='HM_ScoreBig',
               textAlignment='west', fgcolor='0 0 0 200')

    kv.setmany(kv.find(body, 'TimerBG'), xpos=280, ypos=4, wide=80, tall=48, border='HM_TornTag')
    kv.setmany(kv.find(body, 'ServerTimeLeftInsetBG'), wide=0, tall=0)
    kv.setmany(kv.find(body, 'ServerTimeLeftLabel'), xpos=280, ypos=10, wide=80, tall=10, fgcolor='122 124 124 255')
    kv.setmany(kv.find(body, 'ServerTimeLeftValue'), xpos=280, ypos=22, wide=80, tall=24,
               fgcolor='226 226 220 255')
    line = kv.find(body, 'VerticalLine')  # emerald brush stroke between the teams
    kv.remove(line, 'fillcolor')
    kv.setmany(line, visible=1, image=T + 'rule_v', scaleImage=1, xpos=313, wide=14, ypos=72, tall=276)
    kv.setmany(kv.find(body, 'PlayerNameBG'), border='HM_TornTag')
    # tighter rows: 12 players per team fit without the stock grey scroll bar
    for n in ('BluePlayerList', 'RedPlayerList'):
        kv.set(kv.find(body, n), 'linespacing', 16)
    # the local player block moves up 8 so the 4th stats row clears the page's torn bottom edge; the server / map
    # text ends before the tag's slanted right end; the class model sits lower, clear of the last list row
    for n, y in (('PlayerNameBG', 364), ('PlayerNameLabel', 369), ('ServerLabelNew', 367), ('MapName', 377),
                 ('LocalPlayerStatsPanel', 387), ('LocalPlayerDuelStatsPanel', 387), ('ShadedBar', 364),
                 ('Spectators', 345), ('SpectatorsInQueue', 337)):
        blk = kv.find(body, n)
        if blk is not None:
            kv.set(blk, 'ypos', y)
    for n in ('ServerLabelNew', 'MapName'):
        kv.set(kv.find(body, n), 'wide', 245)
    kv.setmany(kv.find(body, 'classmodelpanel'), xpos=-6, ypos=205, wide=118, tall=240)
    # 2D mode (cl_hud_playerclass_use_playermodel 0) shows the class art instead, where the model stands
    kv.setmany(kv.find(body, 'ClassImage'), xpos=4, ypos=332, wide=108, tall=108)
    # the torn tag's left edge slants in ~17 at the top: the name starts inside it
    kv.set(kv.find(body, 'PlayerNameLabel'), 'xpos', 130)
    add(body, 'HM_ScoreKanji', image('HM_ScoreKanji', 606, 380, 14, 28, T + 'kanji_huecomundo', z=6,
                                     drawcolor='226 226 220 70'))


def winpanel(root):
    """End-of-round win panel. The game re-sets the stock team borders on its panels every round, so they drop to
    zpos -1 at zero size and our art takes their place: a torn manga page with a 勝 stamp, screentone team banners behind the
    scores, emerald brush rules instead of the grey lines."""
    body = _root(root)
    kv.setmany(kv.find(body, 'WinPanelBGBorder'), zpos=-1, wide=0, tall=0)  # the page is see-through: no stock box
    add(body, 'HM_WinPage', image('HM_WinPage', 7, 66, 286, 190, T + 'win_page', z=0))
    add(body, 'HM_WinSeal', image('HM_WinSeal', 22, 73, 22, 25, T + 'win_seal', z=1))
    scores = kv.find(body, 'TeamScoresPanel')
    for n, img, x in (('BlueScoreBG', 'score_blue', 46), ('RedScoreBG', 'score_red', 193)):
        kv.setmany(kv.find(scores, n), zpos=-1, wide=0, tall=0)
        add(scores, 'HM_' + n, image('HM_' + n, x, 11, 143, 48, T + img, z=0))
    for n in ('HorizontalLine', 'HorizontalLine2'):
        blk = kv.find(body, n)
        kv.remove(blk, 'fillcolor')
        kv.setmany(blk, image=T + 'notice_rule', scaleImage=1, ypos=int(kv.get(blk, 'ypos')) - 2, tall=5)
    # a light shade on purpose: solid ink here turned the lower half of the see-through page into a black box (and
    # the bottom-center cards still showed through it, only darker)
    kv.set(kv.find(body, 'ShadedBar'), 'fillcolor', '0 0 0 70')
    for n in ('WinningTeamLabel', 'AdvancingTeamLabel'):
        kv.set(kv.find(body, n), 'font', 'HM_Title')
    for n in ('WinningTeamLabelDropshadow', 'AdvancingTeamLabelDropshadow'):
        kv.set(kv.find(body, n), 'font', 'HM_Title')


# ------------------------------------------------------------------ loading screen
def statsummary(root):
    """Map loading / performance report: Hueco Mundo behind it instead of the class poster art."""
    body = _root(root)
    kv.setmany(kv.find(body, 'MainBackground'), wide=0, tall=0, visible=0)
    manga_backdrop(body, shade=175)
    kv.setmany(kv.find(body, 'TitleBanner'), image=T + 'header', tall=110)
    add(body, 'HM_LoadLogo', image('HM_LoadLogo', 24, 22, 260, 65, T + 'logo', z=2))
    add(body, 'HM_LoadKanji', image('HM_LoadKanji', 'r40', 30, 22, 44, T + 'kanji_huecomundo', z=2,
                                    drawcolor='46 214 140 170'))
    kv.setmany(kv.find(body, 'MapLabel'), font='HM_Title', fgcolor='226 226 220 255')
    kv.setmany(kv.find(body, 'OnYourWayLabel'), fgcolor='46 214 140 255')
    kv.setmany(kv.find(body, 'MapType'), fgcolor='122 124 124 255')
