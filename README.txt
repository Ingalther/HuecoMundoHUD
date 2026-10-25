HUECO MUNDO HUD  -  a Bleach / Ulquiorra Cifer themed TF2 HUD
Made by Ingalther Ulquiorra  -  version 1.0
==============================================================

Black sky, a crescent moon, bone-white dunes and emerald tear marks: torn manga pieces in
black, bone white and emerald.

INSTALLATION
------------
1) On GitHub: Code > Download ZIP, then extract it.
2) Put the extracted folder (HuecoMundoHUD-main) into
   ...\steamapps\common\Team Fortress 2\tf\custom\
   resource, scripts, materials and info.vdf must sit directly inside it.
3) Remove any other HUD from custom and restart TF2.

WHAT'S IN IT
------------
- Main menu: Hueco Mundo by night with Las Noches and the ULQUIORRA logo. It changes by itself on
  full-moon nights, for Scream Fortress and for Smissmas.
- All menus (loadout, backpack, scoreboard, class / team select...) in black, grey and emerald.
- In game: your 3D model (or TF2's 2D class art) on a torn triangle with the health beside it,
  ammo on an ink blade, and ÜberCharge, metal, stickies and item meters as manga cards.
- Manga-style kill feed, damage numbers, target ID, death screen, win panel, notifications,
  Engineer / Spy menus and a hitmarker.

HUD SETTINGS
------------
"HUD Settings" in the main menu:
- Layout: CENTERED (default) or CORNERS       (console: cl_hud_minmode 0 / 1)
- Player: 3D MODEL or 2D IMAGE                (console: cl_hud_playerclass_use_playermodel 1 / 0)

GOOD TO KNOW
------------
- Interface files only (layouts, animations, images): nothing VAC looks at. The images use the
  path sv_pure allows, so the HUD works on Valve's casual servers too.
- No fonts to install: Bahnschrift, Segoe UI and Constantia come with Windows 10/11.
- Ammo or item cards gone in a match? Inspecting a teammate (F) hides them until that card
  closes; fire or tap F again.
- Damage number colours follow hud_combattext_red / _green / _blue; 46 214 140 matches the HUD.

UPDATING AND EDITING
--------------------
With TF2 closed, update.bat pulls the latest version and rebuilds the HUD (needs Git and Python 3
with Pillow and numpy). tools\build.py rebuilds it from TF2's current files; colours, layout and
artwork are all in tools\.

UNINSTALL
---------
Delete the HUD folder from tf\custom and restart TF2.

Licence: CC BY-NC-SA 4.0 (see LICENSE.txt).
