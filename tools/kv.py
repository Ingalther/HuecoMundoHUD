"""Tiny Valve KeyValues parser/writer that keeps order and [$PLATFORM] conditionals.

Node = list of [key, value, cond] where value is str or Node.
"""
import re

_TOK = re.compile(r'//[^\n]*|"((?:[^"\\]|\\.)*)"|(\{)|(\})|(\[[^\]]*\])|([^\s{}"\[\]]+)')


def parse(text):
    toks = []
    for m in _TOK.finditer(text):
        if m.group(0).startswith('//'):
            continue
        if m.group(1) is not None:
            toks.append(('s', m.group(1)))
        elif m.group(2):
            toks.append(('{', None))
        elif m.group(3):
            toks.append(('}', None))
        elif m.group(4):
            toks.append(('c', m.group(4)))
        else:
            toks.append(('s', m.group(5)))
    pos = 0

    def block():
        nonlocal pos
        out = []
        while pos < len(toks):
            t, v = toks[pos]
            pos += 1
            if t == '}':
                return out
            if t == 'c':
                if out:
                    out[-1][2] = v
                continue
            key = v
            if pos < len(toks) and toks[pos][0] == 'c':  # "key" [cond] { ... }
                cond = toks[pos][1]
                pos += 1
            else:
                cond = None
            if pos < len(toks) and toks[pos][0] == '{':
                pos += 1
                out.append([key, block(), cond])
            else:
                val = toks[pos][1] if pos < len(toks) else ''
                pos += 1
                ent = [key, val, cond]
                if pos < len(toks) and toks[pos][0] == 'c':
                    ent[2] = toks[pos][1]
                    pos += 1
                out.append(ent)
        return out

    return block()


def dump(node, depth=0):
    lines = []
    ind = '\t' * depth
    for key, val, cond in node:
        c = f' {cond}' if cond else ''
        if isinstance(val, list):
            lines.append(f'{ind}"{key}"{c}')
            lines.append(f'{ind}{{')
            lines.append(dump(val, depth + 1))
            lines.append(f'{ind}}}')
        elif key.startswith('#'):
            lines.append(f'{key} "{val}"')
        else:
            lines.append(f'{ind}"{key}"\t\t"{val}"{c}')
    return '\n'.join(l for l in lines if l != '')


def find(node, key):
    for ent in node:
        if ent[0].lower() == key.lower() and isinstance(ent[1], list):
            return ent[1]
    return None


def path(node, *keys):
    for k in keys:
        node = find(node, k)
        if node is None:
            return None
    return node


def get(node, key, default=None):
    for ent in node:
        if ent[0].lower() == key.lower() and not isinstance(ent[1], list) and ent[2] in (None, '[$WIN32]'):
            return ent[1]
    return default


def set(node, key, value):
    """Replace every variant of key (incl. _minmode/_lodef/_hidef and platform conditionals) with one plain value."""
    kl = key.lower()
    variants = {kl, kl + '_minmode', kl + '_lodef', kl + '_hidef'}
    idx = None
    for i in range(len(node) - 1, -1, -1):
        if node[i][0].lower() in variants and not isinstance(node[i][1], list):
            idx = i
            del node[i]
    ent = [key, str(value), None]
    if idx is None:
        node.append(ent)
    else:
        node.insert(idx, ent)


def setmany(node, **kw):
    for k, v in kw.items():
        set(node, k, v)


def remove(node, key):
    node[:] = [e for e in node if e[0].lower() != key.lower()]


def add_block(node, name, entries, after=None):
    blk = [[k, v if isinstance(v, list) else str(v), None] for k, v in entries.items()]
    remove(node, name)
    node.append([name, blk, None])
    return blk


def walk(node):
    for ent in node:
        yield ent
        if isinstance(ent[1], list):
            yield from walk(ent[1])
