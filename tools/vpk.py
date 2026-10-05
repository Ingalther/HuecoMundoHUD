import struct, os, sys, fnmatch
TF = r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2\tf"
def read_vpk(dirpath):
    f = open(dirpath, 'rb'); data = f.read()
    sig, ver, tree = struct.unpack_from('<III', data, 0)
    hdr = 12 if ver == 1 else 28
    p = hdr; entries = {}
    def rs():
        nonlocal p
        e = data.index(b'\0', p); s = data[p:e].decode('latin1'); p = e+1; return s
    while True:
        ext = rs()
        if not ext: break
        while True:
            path = rs()
            if not path: break
            while True:
                name = rs()
                if not name: break
                crc, pre, arch, off, ln, term = struct.unpack_from('<IHHIIH', data, p); p += 18
                preload = data[p:p+pre]; p += pre
                full = (path + '/' if path != ' ' else '') + name + '.' + ext
                entries[full.lower()] = (pre, preload, arch, off, ln)
    return entries, data, hdr + tree
def extract(vpkname, patterns, out):
    d = os.path.join(TF, vpkname + '_dir.vpk')
    entries, data, dataoff = read_vpk(d)
    n = 0
    for k, (pre, preload, arch, off, ln) in entries.items():
        if not any(fnmatch.fnmatch(k, pat) for pat in patterns): continue
        if arch == 0x7fff: body = data[dataoff+off: dataoff+off+ln]
        elif ln:
            with open(os.path.join(TF, '%s_%03d.vpk' % (vpkname, arch)), 'rb') as a:
                a.seek(off); body = a.read(ln)
        else: body = b''
        o = os.path.join(out, k); os.makedirs(os.path.dirname(o), exist_ok=True)
        open(o, 'wb').write(preload + body); n += 1
    return n
if __name__ == '__main__':
    print(extract('tf2_misc', ['resource/*.res', 'resource/ui/*.res', 'scripts/hudlayout.res', 'scripts/hudanimations*.txt', 'resource/ui/*/*.res', 'scripts/chapterbackgrounds.txt', 'resource/*.txt'], 'default'))
