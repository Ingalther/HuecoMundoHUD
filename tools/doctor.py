"""Checks a Hueco Mundo HUD install for what makes it look wrong in game, fixes what it safely can, and writes
hm_report.txt next to update.bat (the file to send along when reporting a problem). update.bat runs it after the
build; it can also be run by hand:

    python tools/doctor.py

What it looks at:
  - TF2 running: the game reads the HUD's files at start, so an update shows only after a restart;
  - the HUD's own files: every material points at a texture that is there;
  - everything else in tf/custom (folders and .vpk files). TF2 reads those in alphabetical order and takes each file
    from the first one that has it, so another HUD mixes its panels in with this one's, and a mod sorting before
    this folder replaces whatever of the HUD's files it also has (e.g. the CTF flag compass). Those are moved,
    after asking, into tf/custom_disabled: nothing is deleted, moving them back undoes it;
  - loose HUD files straight in tf/resource/ui or tf/scripts (an old style of install): only reported.
"""
import datetime
import os
import re
import shutil
import struct
import subprocess
import sys

import vpk

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
HUD_NAME = 'huecomundo-hud'  # build.py installs here when the project folder is not in tf/custom itself
IN_CUSTOM = os.path.basename(os.path.dirname(PROJECT)).lower() == 'custom'
TF = os.path.dirname(os.path.dirname(PROJECT)) if IN_CUSTOM else vpk.TF
HUD = PROJECT if IN_CUSTOM else os.path.join(TF, 'custom', HUD_NAME)
CUSTOM = os.path.join(TF, 'custom')
DISABLED = os.path.join(TF, 'custom_disabled')
REPORT = os.path.join(PROJECT, 'hm_report.txt')
PARTS = ('resource', 'scripts', 'materials')  # where a HUD's files live; other folders cannot clash with it
# files only a HUD ships: a folder or VPK that has one of these is a HUD (or a HUD mod) and mixes with this one
HUD_MARKERS = {'scripts/hudlayout.res', 'resource/clientscheme.res', 'resource/ui/mainmenuoverride.res',
               'resource/ui/hudplayerhealth.res', 'scripts/hudanimations_manifest.txt'}
TF2_EXES = ('tf_win64.exe', 'tf.exe', 'hl2.exe')

lines = []  # the report


def say(text=''):
    print(text)
    lines.append(text)


def note(text):
    lines.append(text)


def rel_files(root):
    """The HUD-part files under a folder, as lower-case paths with forward slashes."""
    out = set()
    for part in PARTS:
        base = os.path.join(root, part)
        for dirpath, dirnames, filenames in os.walk(base):
            for fn in filenames:
                out.add(os.path.relpath(os.path.join(dirpath, fn), root).replace('\\', '/').lower())
    return out


def vpk_files(path):
    """The file names in a VPK. Only its directory tree is read: a mod's VPK can be hundreds of MB."""
    with open(path, 'rb') as f:
        head = f.read(28)
        if len(head) < 12:
            return set()
        sig, ver, tree = struct.unpack_from('<III', head, 0)
        if sig != 0x55AA1234:
            return set()
        f.seek(12 if ver == 1 else 28)
        data = f.read(tree)
    files, p = set(), 0

    def word():
        nonlocal p
        e = data.index(b'\0', p)
        s = data[p:e].decode('latin1')
        p = e + 1
        return s
    while True:
        ext = word()
        if not ext:
            break
        while True:
            folder = word()
            if not folder:
                break
            while True:
                name = word()
                if not name:
                    break
                preload = struct.unpack_from('<IHHIIH', data, p)[1]
                p += 18 + preload
                full = (folder + '/' if folder.strip() else '') + name + ('.' + ext if ext.strip() else '')
                files.add(full.lower())
    return files


def is_hud_folder(path, files):
    if files & HUD_MARKERS:
        return True
    vdf = os.path.join(path, 'info.vdf')
    return os.path.isfile(vdf) and 'ui_version' in open(vdf, encoding='utf-8', errors='replace').read().lower()


def is_this_hud(path):
    vdf = os.path.join(path, 'info.vdf')
    return os.path.isfile(vdf) and HUD_NAME in open(vdf, encoding='utf-8', errors='replace').read()


def entries():
    """What TF2 loads from tf/custom: folders and .vpk files (a split VPK by its _dir file), in its order."""
    out = []
    for name in sorted(os.listdir(CUSTOM), key=str.lower):
        path = os.path.join(CUSTOM, name)
        if os.path.isdir(path):
            out.append((name, path, 'folder'))
        elif name.lower().endswith('.vpk') and not re.search(r'_\d{3}\.vpk$', name, re.I):
            out.append((name, path, 'vpk'))
    return out


def companions(path):
    """A VPK's other files: its numbered archives (when split) and the sound cache the game writes next to it."""
    folder, name = os.path.split(path)
    stem = re.sub(r'(_dir)?\.vpk$', '', name, flags=re.I)
    out = []
    for other in os.listdir(folder):
        o = other.lower()
        if other != name and (re.fullmatch(re.escape(stem.lower()) + r'_\d{3}\.vpk', o)
                              or o.startswith(name.lower() + '.')):
            out.append(os.path.join(folder, other))
    return out


def move_out(path):
    """Moves a folder or VPK (with its companions) into tf/custom_disabled, under a free name."""
    os.makedirs(DISABLED, exist_ok=True)
    moved = []
    for src in [path] + companions(path):
        name = os.path.basename(src)
        dst, n = os.path.join(DISABLED, name), 2
        while os.path.exists(dst):
            stem, ext = os.path.splitext(name) if os.path.isfile(src) else (name, '')
            dst = os.path.join(DISABLED, f'{stem} ({n}){ext}')
            n += 1
        shutil.move(src, dst)
        moved.append(dst)
    return moved


def tf2_running():
    if os.name != 'nt':
        return []
    try:
        out = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True, text=True, errors='replace',
                             timeout=20).stdout.lower()
    except (OSError, subprocess.SubprocessError):
        return []
    return [exe for exe in TF2_EXES if f'"{exe}"' in out]


def check_own_files():
    """Every material of the HUD that points at one of its textures must find it; the key files must be there."""
    missing = [f for f in ('info.vdf', 'scripts/hudlayout.res', 'resource/clientscheme.res',
                           'resource/ui/mainmenuoverride.res') if not os.path.isfile(os.path.join(HUD, f))]
    for dirpath, _, filenames in os.walk(os.path.join(HUD, 'materials')):
        for fn in filenames:
            if not fn.lower().endswith('.vmt'):
                continue
            text = open(os.path.join(dirpath, fn), encoding='utf-8', errors='replace').read()
            m = re.search(r'"\$basetexture"\s+"(vgui/replay/thumbnails/hm/[^"]+)"', text, re.I)
            if m and not os.path.isfile(os.path.join(HUD, 'materials', m.group(1) + '.vtf')):
                missing.append('materials/' + m.group(1) + '.vtf')
    return missing


def main():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    version = open(os.path.join(PROJECT, 'VERSION'), encoding='utf-8').read().strip() \
        if os.path.isfile(os.path.join(PROJECT, 'VERSION')) else '?'
    try:
        commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=PROJECT, capture_output=True,
                                text=True, timeout=20).stdout.strip() or '-'
    except (OSError, subprocess.SubprocessError):
        commit = '-'
    note(f'Hueco Mundo HUD check, {now}')
    note(f'HUD version {version} (git {commit}), Python {sys.version.split()[0]}')
    note(f'HUD folder: {HUD}')
    note(f'TF2 folder: {TF}')
    note('')
    problems = 0

    running = tf2_running()
    if running:
        problems += 1
        say('  !! TF2 is running (' + ', '.join(running) + '). It reads the HUD when it starts: close it fully and')
        say('     start it again, or it keeps showing parts of the old version.')
    else:
        say('  OK TF2 is closed.')

    if not os.path.isdir(HUD):
        say(f'  !! The HUD is not in {HUD}. Run update.bat again; if this stays, send hm_report.txt.')
        return finish(problems + 1)
    missing = check_own_files()
    if missing:
        problems += 1
        say(f'  !! {len(missing)} of the HUD\'s files are missing, e.g. {missing[0]}.')
        say('     Run update.bat again; if this stays, send hm_report.txt.')
        for f in missing:
            note('     missing: ' + f)
    else:
        say('  OK The HUD\'s files are all there.')

    ours = rel_files(HUD)
    our_key = os.path.basename(HUD).lower()
    found = []  # (name, path, why)
    note('')
    note('tf\\custom, in the order TF2 reads it:')
    for name, path, kind in entries():
        if os.path.normcase(os.path.abspath(path)) == os.path.normcase(os.path.abspath(HUD)):
            note(f'  {name}  <- this HUD')
            continue
        try:
            files = rel_files(path) if kind == 'folder' else vpk_files(path)
        except (OSError, ValueError, struct.error) as e:
            note(f'  {name}  ({kind}, could not be read: {e})')
            continue
        clash = sorted(files & ours)
        first = name.lower() < our_key
        if kind == 'folder' and is_this_hud(path):
            why = 'another copy of this HUD: the two copies mix their files'
        elif (kind == 'folder' and is_hud_folder(path, files)) or files & HUD_MARKERS:
            why = 'another HUD: its panels mix with this one\'s'
        elif clash and first:
            why = f'replaces {len(clash)} of this HUD\'s files, e.g. {clash[0]}'
        else:
            why = None
        if why:
            found.append((name, path, why))
        note(f'  {name}  ({kind}, {len(files)} HUD-part files, {len(clash)} shared with this HUD'
             + (', read before it' if first else '') + (f') -> {why}' if why else ', fine)'))
    note('')

    if not found:
        say('  OK Nothing else in tf\\custom changes the HUD.')
    else:
        problems += 1
        say('  !! These in tf\\custom change how the HUD looks:')
        for name, _, why in found:
            say(f'       {name}: {why}')
        say('     They can be moved into tf\\custom_disabled now (nothing is deleted; moving one back turns it on')
        say('     again).')
        try:
            answer = input('     Move them? [Y/N] ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            answer = ''
        note(f'     Move them? -> {answer or "(no answer)"}')
        if answer.startswith('y'):
            failed = 0
            for name, path, _ in found:
                try:
                    for dst in move_out(path):
                        say(f'     moved -> {dst}')
                except OSError as e:
                    failed += 1
                    say(f'     could not move {name}: {e}')
                    say('     (a program has its files open, often TF2: close it and run update.bat again)')
            if not failed:
                problems -= 1
                say('  OK Fixed: they no longer load with the HUD.')
        else:
            say('     Left as they are.')

    loose = []
    ui = os.path.join(TF, 'resource', 'ui')
    if os.path.isdir(ui):
        loose += ['resource\\ui\\' + f for f in os.listdir(ui) if f.lower().endswith('.res')]
    for f in ('scripts\\hudlayout.res', 'scripts\\hudanimations_manifest.txt'):
        if os.path.isfile(os.path.join(TF, *f.split('\\'))):
            loose.append(f)
    if loose:
        say(f'  ?? {len(loose)} HUD files sit loose in the tf folder (an old way of installing a HUD), e.g.')
        say(f'     tf\\{loose[0]}. They fill in panels this HUD leaves as they are; if something looks off,')
        say('     move them out of the tf folder.')
        for f in loose:
            note('     loose: tf\\' + f)
    return finish(problems)


def finish(problems):
    say('')
    say('  All good.' if not problems else f'  {problems} problem(s) left, see above.')
    try:
        with open(REPORT, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        print(f'  The full report is in {REPORT}')
        print('  If the HUD still looks wrong in game, send that file along with a screenshot.')
    except OSError as e:
        print(f'  Could not write the report ({e}).')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:  # the check must never stop an update that went through
        print(f'  The install check stopped early ({type(e).__name__}: {e}). The HUD itself is installed.')
        sys.exit(0)
