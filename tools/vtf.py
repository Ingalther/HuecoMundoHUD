"""Minimal VTF 7.2 writer (uncompressed BGRA8888 / BGR888, full mip chain)."""
import struct
import numpy as np
from PIL import Image

FLAG_CLAMPS = 0x4
FLAG_CLAMPT = 0x8
FLAG_NOMIP = 0x100
FLAG_NOLOD = 0x200
FLAG_EIGHTBITALPHA = 0x2000

FMT_BGR888 = 3
FMT_BGRA8888 = 12


def bleed_alpha(img):
    """Fill RGB under transparent pixels with nearby colour so bilinear filtering has no dark fringes."""
    from PIL import ImageFilter
    a = np.asarray(img, dtype=np.float32) / 255.0
    rgb, al = a[..., :3], a[..., 3:4]
    pre = rgb * al
    out = rgb.copy()
    acc_pre = np.zeros_like(pre)
    acc_a = np.zeros_like(al)
    for r in (2, 6, 18, 48):
        bp = np.stack([np.asarray(Image.fromarray((pre[..., c] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255 for c in range(3)], -1)
        ba = np.asarray(Image.fromarray((al[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), dtype=np.float32)[..., None] / 255
        m = (acc_a < 1e-4) & (ba > 1e-4)
        acc_pre = np.where(m, bp, acc_pre)
        acc_a = np.where(m, ba, acc_a)
    fill = np.where(acc_a > 1e-4, acc_pre / np.maximum(acc_a, 1e-4), rgb)
    w = np.clip(al * 4, 0, 1)  # keep real colour where visible
    out = rgb * w + fill * (1 - w)
    res = np.concatenate([np.clip(out, 0, 1), al], -1)
    return Image.fromarray((res * 255 + 0.5).astype(np.uint8), 'RGBA')


def write_vtf(path, img, alpha=True, mips=True, clamp=True):
    img = img.convert('RGBA')
    w, h = img.size
    assert w & (w - 1) == 0 and h & (h - 1) == 0, f'{path}: size must be power of two, got {w}x{h}'
    if alpha:
        img = bleed_alpha(img)
    levels = [img]
    if mips:
        while levels[-1].size != (1, 1):
            lw, lh = levels[-1].size
            levels.append(img.resize((max(1, lw // 2), max(1, lh // 2)), Image.LANCZOS if min(lw, lh) > 4 else Image.BOX))
    flags = FLAG_NOLOD
    if clamp:
        flags |= FLAG_CLAMPS | FLAG_CLAMPT
    if not mips:
        flags |= FLAG_NOMIP
    fmt = FMT_BGRA8888 if alpha else FMT_BGR888
    if alpha:
        flags |= FLAG_EIGHTBITALPHA
    hdr = struct.pack('<4sII', b'VTF\0', 7, 2)
    hdr += struct.pack('<IHHIHH', 80, w, h, flags, 1, 0)
    hdr += b'\0' * 4
    hdr += struct.pack('<fff', 0.5, 0.5, 0.5)
    hdr += b'\0' * 4
    hdr += struct.pack('<fIBIBBH', 1.0, fmt, len(levels), 0xFFFFFFFF, 0, 0, 1)
    hdr += b'\0' * (80 - len(hdr))
    body = bytearray()
    for lvl in reversed(levels):  # smallest mip first
        a = np.asarray(lvl, dtype=np.uint8)
        if alpha:
            body += a[..., [2, 1, 0, 3]].tobytes()
        else:
            body += a[..., [2, 1, 0]].tobytes()
    with open(path, 'wb') as f:
        f.write(hdr)
        f.write(body)
