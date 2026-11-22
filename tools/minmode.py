"""MINMODE (cl_hud_minmode 1): the HUD's second layout, the competitive HUDs' minimal one (as in the Reaper HUD), in
place of the old CORNERS one.

The default layout (the manga clusters) lives in the plain keys; this one only in *_minmode keys, written by the
passes below at the end of each file's patch (kv.set clears a key's _minmode twin, so nothing may set those keys
after them). No model, no triangle, no band or blade: the health and the ammo as bare numbers either side of the
crosshair, a quarter of the screen down, each on a torn ink plate that fades out away from the crosshair
(manga.mm_plate). Between them the sticky card, or with a shield its charge bar alone (build.pipes_pos), the kill
streak tag under the health plate, the item meters under the ammo plate, the target IDs under the card.

Units are the HUD's 480-line ones; 'cN' is N from the screen's centre."""
import kv

MM_Y = 318                      # the plates' top (715 px at 1080 lines)
PLATE = (138, 44)               # a plate's box
H_X = -270                      # the health plate's left edge from the centre (it ends 132 left of the crosshair)
A_X = 133                       # the ammo plate's left edge from the centre
NUM_T = 36                      # the numbers' label height
UNDER = MM_Y + PLATE[1] + 2     # the row under the plates (streak tag, item meters)


def c(v):
    return 'c%d' % v


def mm(blk, **keys):
    """Set *_minmode keys, one value each."""
    for k, v in keys.items():
        kv.remove(blk, k + '_minmode')
        blk.append([k + '_minmode', str(v), None])


def hide(blk):
    """Gone in minmode: no size (animations fade some of these, none sizes them)."""
    mm(blk, wide=0, tall=0)


def only_mm(body, name, entries, box):
    """A panel of minmode alone: no size in the default layout, its box in minmode."""
    x, y, w, h = box
    entries = dict(entries, xpos=x, ypos=y, wide=0, tall=0)
    blk = kv.add_block(body, name, entries)
    mm(blk, wide=w, tall=h)
    return blk


def children(body, skip=()):
    return [(k, v) for k, v, *_ in body if isinstance(v, list) and k not in skip]


# ------------------------------------------------------------------ files
def health(body):
    """hudplayerhealth.res: the number right-aligned to the plate's inner end, MAX and the max health at its outer end
    under the 体力 caption (part of the plate art), the status icons over the outer end; the rest goes."""
    import build as B
    keep = {'PlayerStatusHealthValue', 'HM_HealthShadow', 'PlayerStatusMaxHealthValue'}
    icons = set(B.STATUS_ICONS)
    for name, blk in children(body, skip=('HudPlayerHealth',)):
        if name in icons or name.startswith(('PlayerStatus_', 'PlayerStatusMarked')):
            mm(blk, xpos=c(H_X), ypos=MM_Y - 22, wide=20, tall=20)
        elif name not in keep:
            hide(blk)
    nx = H_X + PLATE[0] - 8 - 84
    for name, d in (('PlayerStatusHealthValue', 0), ('HM_HealthShadow', 1)):
        blk = kv.find(body, name)
        if blk is not None:
            mm(blk, xpos=c(nx + d), ypos=MM_Y + 2 + d, wide=84, tall=NUM_T, font='HM_MMNum', textAlignment='east')
    # the max health (its plain keys keep it hidden in the default layout; its text, %MaxHealth%, stays in the plain
    # key: a label's text in a _minmode key is shown raw)
    # (the game shows it only while the health is under the max, so "MAX" is part of its text: both go together)
    blk = kv.find(body, 'PlayerStatusMaxHealthValue')
    if blk is not None:
        kv.setmany(blk, fgcolor='HM_BoneMid', textAlignment='west', labelText='MAX %MaxHealth%')
        mm(blk, xpos=c(H_X + 10), ypos=MM_Y + 24, wide=70, tall=12, font='HM_Small')
    only_mm(body, 'HM_MMPlateH', B.img_panel('HM_MMPlateH', 0, 0, 0, 0, 'mm_plate_h', z=1),
            (c(H_X), MM_Y, PLATE[0], PLATE[1]))


def player_class(body):
    """hudplayerclass.res: no model, no class art, no triangle; the spy's disguise small, left of the health plate."""
    for name, blk in children(body, skip=('HudPlayerClass',)):
        if name in ('PlayerStatusSpyImage', 'PlayerStatusSpyOutlineImage'):
            mm(blk, xpos=c(H_X - 32), ypos=MM_Y + 8, wide=28, tall=28)
        else:
            hide(blk)


def ammo(body):
    """hudammoweapons.res (the panel is the ammo plate's box, layout()): the clip right-aligned near the plate's inner
    end, the reserve small beside it, AMMO under the 弾薬 caption at the outer end; the blade goes."""
    import build as B
    for name in ('HM_AmmoBlade', 'HudWeaponAmmoBG'):
        blk = kv.find(body, name)
        if blk is not None:
            hide(blk)
    blk = kv.find(body, 'HudWeaponLowAmmoImage')
    if blk is not None:
        mm(blk, xpos=0, ypos=0, wide=PLATE[0], tall=PLATE[1])
    for name, x, w, align in (('AmmoInClip', 2, 50, 'east'), ('AmmoNoClip', 10, 90, 'west')):
        for n, d in ((name, 0), (name + 'Shadow', 1)):
            blk = kv.find(body, n)
            if blk is not None:
                mm(blk, xpos=x + d, ypos=2 + d, wide=w, tall=NUM_T, font='HM_MMNum', textAlignment=align)
    for n, d in (('AmmoInReserve', 0), ('AmmoInReserveShadow', 1)):
        blk = kv.find(body, n)
        if blk is not None:
            mm(blk, xpos=56 + d, ypos=14 + d, wide=44, tall=18, font='HM_MMRes')
    only_mm(body, 'HM_MMAmmoLabel', B.label('HM_MMAmmoLabel', 0, 0, 0, 0, 'AMMO', 'HM_Small', 'HM_Bone', 'east'),
            (PLATE[0] - 50, 22, 40, 12))
    only_mm(body, 'HM_MMPlateA', B.img_panel('HM_MMPlateA', 0, 0, 0, 0, 'mm_plate_a', z=0), (0, 0, PLATE[0], PLATE[1]))


STRIP_H = 16                    # one minimal meter row
BAR_X, BAR_W = 64, 70           # a row's bar (or count) right of its label


def killstreak(body):
    """The kill streak under the health plate, as bare text: the count and the game's STREAK word, no tag."""
    blk = kv.find(body, 'HudItemEffectMeter')
    if blk is not None:
        mm(blk, xpos=c(H_X + PLATE[0] - 80), ypos=UNDER, wide=80, tall=STRIP_H)
    blk = kv.find(body, 'ItemEffectMeterBG')
    if blk is not None:
        hide(blk)
    blk = kv.find(body, 'ItemEffectMeterLabel')
    if blk is not None:
        mm(blk, xpos=0, ypos=0, wide=56, tall=STRIP_H, textAlignment='east')
    blk = kv.find(body, 'ItemEffectMeterCount')
    if blk is not None:
        mm(blk, xpos=60, ypos=0, wide=20, tall=STRIP_H, font='HM_Metal')


def meter(body, slot, row):
    """An item meter in minmode: no card, a bare row under the ammo plate (rows going down, the sticky slot's row
    first; the MvM sapper's below the others): the game's word for the meter (DRINK, RAGE, HEADS...) and a thin
    emerald bar beside it, or its count."""
    top = kv.find(body, 'HudItemEffectMeter')
    idx = row if slot == 0 else 3
    mm(top, xpos=c(A_X), ypos=UNDER + idx * STRIP_H, wide=PLATE[0], tall=STRIP_H)
    for name, blk in children(body, skip=('HudItemEffectMeter',)):
        if name == 'ItemEffectMeterLabel':
            mm(blk, xpos=0, ypos=0, wide=BAR_X - 4, tall=STRIP_H, font='HM_Small', textAlignment='east', visible=1)
        elif name in ('ItemEffectMeter', 'HM_BarTint'):
            mm(blk, xpos=BAR_X, ypos=(STRIP_H - 4) // 2, wide=BAR_W, tall=4)
        elif name == 'ItemEffectMeterCount':
            mm(blk, xpos=BAR_X, ypos=0, wide=40, tall=STRIP_H, font='HM_Metal')
        elif name.startswith('KillComboClassIcon'):
            i = int(name[-1])
            mm(blk, xpos=BAR_X + 30 + (i - 1) * 12, ypos=2, wide=11, tall=11)
        else:
            hide(blk)


def pipes(body):
    """huddemomanpipes.res: with a shield, no card: the charge alone, a line bar like the sticky charge bar, level
    with the plates' middle (the Chargin' Targe tag behind it goes; the sticky count's cards cover it otherwise)."""
    blk = kv.find(body, 'background')
    if blk is not None:
        hide(blk)
    blk = kv.find(body, 'ChargeMeter')
    if blk is not None:
        mm(blk, xpos=8, ypos=(PLATE[1] - 6) // 2, wide=53, tall=6)


def layout(body):
    """hudlayout.res: the ammo plate's place."""
    import build as B
    blk = kv.find(body, 'HudWeaponAmmo')
    if blk is not None:
        mm(blk, xpos=c(A_X), ypos=MM_Y, wide=PLATE[0], tall=PLATE[1])
