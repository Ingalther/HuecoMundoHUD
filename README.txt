HUECO MUNDO HUD  —  a Bleach / Ulquiorra Cifer themed TF2 HUD
Made by Ingalther Ulquiorra  -  version 1.0 (the number is also shown small in the main menu's
bottom right corner; compare it with the latest release on GitHub)
==============================================================

Black sky, a crescent moon, bone-white dunes and emerald tear marks.
Quiet, somber palette: black - bone white - emerald green.

INSTALLATION
------------
1) Download the ZIP from GitHub (Code > Download ZIP) and extract it. You get one folder,
   "HuecoMundoHUD-main" (the name does not matter).
2) Put that whole folder into TF2's custom folder, as it is:
   ...\steamapps\common\Team Fortress 2\tf\custom\HuecoMundoHUD-main\
   Inside it you should see resource, scripts, materials, info.vdf (plus tools, docs and update.bat,
   which the game ignores). Do not put it one folder deeper.
3) Make sure NO OTHER HUD is left in custom (e.g. another HUD you used before), and no older Hueco Mundo copy
   (e.g. a separate "huecomundo-hud" folder). Two HUDs at once mix their files and break the interface.
4) Restart the game ("hud_reloadscheme" is not enough if you installed it while TF2 was running).

WHAT CHANGES
------------
- Main menu: Hueco Mundo backdrop (Las Noches, quartz trees, crescent moon), ULQUIORRA logo,
  ink-black buttons with an emerald edge on hover.
- Every menu (loadout, backpack, store, options, scoreboard, class / team select, death screen,
  notifications): TF2's tan / orange tones replaced with a black - grey - emerald palette;
  fonts are Bahnschrift / Constantia.
- In game: torn manga pieces packed close together, Weirdcore-style.
    * Bottom left: the 3D model stands on a torn triangle in team screentone; the health digits sit
      on a slanted ink band pressed against the model's chest, with a vertical health gauge that
      fills from the bottom.
    * Killstreak: a 殺 tag right under the health band.
    * Right: clip + reserve on a torn ink blade pointing right. Engineer metal is a card
      at the bottom center (a pile of steel ingots), where the sticky counter sits, with the +/- metal
      floating up above it; charge-up bars (sticky launcher, Huntsman) sit centered under the sticky card.
    * Engineer buildings: torn manga cards (sentry 砲, dispenser 補, teleporters 入 / 出).
    * Center-screen notices ("You are now Attacking!", autobalance warning, team switch): torn
      manga cards with a kanji seal (任務 / 警告 / 移籍).
    * Item meters (cloak / Dead Ringer, Heatmaker focus, Jarate, Pomson, Cow Mangler, Soda Popper,
      banner rage, Eyelander heads...) are manga cards at the bottom center, in the same spot as the
      sticky counter: each with its own inked logo (pocket watch, scope, jar, lightning bolt, plasma
      orb, soda can, a Hollow mask for the shared generic meter...) and an emerald bar
      (the game paints these bars white, so an emerald sheet lies over them: pale jade on deep emerald). Meters that can show at the same
      time sit side by side, or one row up: the Cow Mangler, the Air Strike / Eyelander and Bazaar Bargain cards (a
      skull, the count and the game's own word next to it, KILLS or HEADS), the Diamondback (CRITS), Bonk / Mad Milk
      and the MvM rage bar sit right above the sticky slot, so the card in it (banner rage, cloak, Jarate, Sandman,
      sandvich, the sticky counter...) never covers them. ÜberCharge is a card there too: a bold medic cross, the charge % over an emerald
      bar that breathes when it is ready (Vaccinator: four segments and the full-charge count, its resist
      icon over the cross).
    * Demoman: a small torn tag at the bottom center, level with the health band and the ammo blade:
      a manga stickybomb and the sticky count, or a Chargin' Targe with an emerald charge bar when a
      shield is equipped.
    * HUD notifications ("Your INTELLIGENCE has been dropped!", flag taken / returned...): flat torn manga
      cards, team tone behind the icon, an emerald brush stroke under the text.
    * Overheal -> health digits turn emerald with a faint glow behind them.
    * Low health -> the digits flash red.
    * Low ammo -> the ammo digits flash amber.
- Damage numbers: bold italic outlined manga lettering, big hits bigger. Their colour follows TF2's own hud_combattext_red /
  _green / _blue settings; set them to 46 214 140 for the Cero green that matches the HUD.
- Scoreboard: one torn manga page (screentone corners, a faint 虚圏 between the teams), screentone team
  banners with bone 青 / 赤 stamps, an emerald brush stroke between the teams, torn tags for the timer and your name.
- Casual / competitive team strip at the top: a torn blue | red band, each player portrait in a torn bone rim,
  emerald / bone / crimson health bars.
- Death screen ("You were killed by"): a torn manga card in the killer's team tone with a faint 死.
- Target ID (what you look at, who is healing you): a see-through torn manga card in the target's team tone.
- Match start countdown: the digits on a square torn manga card with speed lines.
- End-of-round win panel: a torn manga page with speed lines and a 勝 stamp, screentone team banners behind
  the scores, emerald brush rules.
- Kill feed: stacked sharp manga strips with bold outlined italic lettering: ink strips, your own kills on
  bone-jade paper with emerald info text (the game draws the rows as plain boxes, so they take colours, not art).
- Hitmarker: an emerald X flashes on the crosshair every time you hurt an enemy.
- Respawn timer ("Respawn in X seconds"): on a torn manga card (hidden when there is no timer).
- Spectator / death screen: no black bars at the top and bottom; the key hints, map name and tip
  have outlined lettering so they read over the map.
- Engineer build / destroy menus and the spy disguise menu: torn manga sheets; the slots are emerald (ready),
  grey (built / unavailable) or crimson (not enough metal), the number keys on emerald chips. The
  "disguised as" box is a torn manga card.
- Payload: the cart track on a torn manga strip. Capture progress: a torn ink rim around the ring.
- Killstreak splash ("... is GODLIKE!"): a torn ink manga sticker with an emerald slash, sized to the text.
  For a bigger splash, set cl_hud_killstreak_display_fontsize 1 or 2 in the console.

HUD SETTINGS (MAIN MENU)
------------------------
"HUD Settings" at the bottom of the main menu's left column opens a popup with a preview of each
health / ammo layout:
    CENTERED -> default; pulled in from the screen edges, ammo a little higher (Weirdcore placement)
    CORNERS  -> both in the bottom corners
It applies instantly. It uses TF2's cl_hud_minmode cvar (CENTERED = 0, CORNERS = 1), so it can also
be set from the console. In this HUD minmode does not give TF2's "minimal HUD"; it only switches
between these two layouts.
RELOAD HUD at its bottom reloads the HUD (same as hud_reloadscheme in the console): use it if a counter
(ammo, stickies...) ever goes missing in a match (ESC brings the main menu up in game).
The popup replaces the main menu's news (MOTD) panel, which is why the MOTD icon is gone.

VAC / SAFETY
------------
The HUD is made of interface files only: .res (layout), .txt (animations), .vtf/.vmt (images).
No .dll, no .exe, no script injection, no config exploits. It loads through TF2's own supported
"custom" folder; VAC does not look at HUDs, and thousands of players have used HUDs like budhud,
rayshud and toonhud for years.

Images live under "materials/vgui/replay/thumbnails/": that path is on TF2's sv_pure whitelist,
so they show on Valve's casual servers too. The main menu backdrop is only used in the menu and
on loading screens.

FONTS
-----
Nothing to install: Bahnschrift, Segoe UI and Constantia ship with Windows 10/11.

UNINSTALL
---------
Delete the HUD folder from tf\custom (e.g. HuecoMundoHUD-main) and restart the game.

EDITING IT YOURSELF
-------------------
To update: with TF2 closed, double-click update.bat in the HUD folder (needs Git and Python 3 with Pillow
and numpy). It pulls the latest version from GitHub and rebuilds the HUD. If the folder sits in tf\custom
it is rebuilt right there; from anywhere else it is installed as tf\custom\huecomundo-hud. A ZIP
download has no git data: the first update.bat run links the folder to GitHub by itself.

tools\build.py regenerates the whole HUD (needs Python 3 + Pillow + numpy):
    python tools\build.py            -> rebuilds the HUD parts of the project folder
    python tools\build.py --install  -> also installs it into tf\custom (in place when already there)
Colours are in the "C" and "SCHEME_COLORS" tables at the top of build.py, layout in the patch_*
functions (in-game positions in LAYOUTS, overall size in CARD_K), artwork in tools\art.py,
tools\manga.py and tools\build_art.py. When TF2 updates, just run build.py again: it reads the
game's current interface files from its VPKs and re-applies the theme on top of them.
