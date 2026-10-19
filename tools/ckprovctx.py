# ckprovctx.py: review contexts for every provisional name of one Clockwork Knight program (first review,
# no verdict file needed). Writes the function body plus up to 3 caller bodies (funcinfo C lines + literal-pool
# pointers), FUN_/PTR_ replaced by current hand names. Adapted from Pandemonium/tools/provctx.py.
# usage: py -3.13 -I ckprovctx.py <ghidra> <prog> <N> <out prefix>
#   prog = Ghidra program name (GEKAN_A, CK2USA_A, GEKAN_AREA61_LO, GEKAN_AREA62 ...); hand file = hand_<prog
#   minus _A / _LO>.txt; image = bin/<prog>.BIN or bin/areas/<prog>.BIN; base 0x06003000 for *_A else 0x00200000.
import sys, os, re
g, prog, n, pre = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
handname = os.environ.get('HAND', re.sub(r'_A$|_LO$', '', prog))
base = int(os.environ['BASE'], 16) if 'BASE' in os.environ else (0x06003000 if prog.endswith('_A') else 0x00200000)
def bodies():
    d = {}; cur = None; buf = []
    for l in open(os.path.join(g, 'decomp_%s.c' % prog), encoding='utf-8', errors='replace'):
        m = re.match(r'// ==== (\S+) @ ([0-9a-fA-F]+)', l)
        if m:
            if cur: d[cur] = ''.join(buf)
            cur = m.group(2).lower().zfill(8); buf = []
        buf.append(l)
    if cur: d[cur] = ''.join(buf)
    return d
def names(fn):
    d = {}
    if not os.path.exists(fn): return d
    for l in open(fn, encoding='utf-8', errors='replace'):
        f = l.split(None, 4)
        if len(f) > 2: d[f[0][2:].lower().zfill(8)] = (f[2], f[4].strip() if len(f) > 4 else '')
    return d
def callers():
    d = {}; cur = None
    for l in open(os.path.join(g, 'funcinfo_%s.tsv' % prog), encoding='utf-8', errors='replace'):
        f = l.split()
        if not f: continue
        if f[0] == 'F': cur = f[1].lower().zfill(8)
        elif f[0] == 'C' and cur: d.setdefault(f[1].lower().zfill(8), []).append(cur)
    return d
def image():
    for d in ('bin', os.path.join('bin', 'areas')):
        fn = os.path.join(g, d, prog + '.BIN')
        if 'IMG' in os.environ: fn = os.environ['IMG']
        if os.path.exists(fn): return open(fn, 'rb').read()
    return b''
def word(img, a):
    o = a - base
    return int.from_bytes(img[o:o + 4], 'big') if 0 <= o <= len(img) - 4 else None
def poolcallers(img, starts):
    d = {}
    for o in range(0, len(img) - 3, 2):
        v = int.from_bytes(img[o:o + 4], 'big')
        if v < base or v >= base + len(img): continue
        a = base + o; own = None
        lo, hi = 0, len(starts) - 1
        while lo <= hi:
            m = (lo + hi) // 2
            if starts[m] <= a: own = starts[m]; lo = m + 1
            else: hi = m - 1
        if own is not None: d.setdefault('%08x' % v, set()).add('%08x' % own)
    return d
own = names(os.path.join(g, 'hand_%s.txt' % handname))
boot = names(os.path.join(g, 'hand_%s.txt' % os.environ['BOOT'])) if 'BOOT' in os.environ else (names(os.path.join(g, 'hand_%s.txt' % prog.split('_AREA')[0])) if base == 0x00200000 else {})
nm = {**boot, **own}
b, cl, img = bodies(), callers(), image()
starts = sorted(int(k, 16) for k in own)
for k, v in poolcallers(img, starts).items():
    cl.setdefault(k, []).extend(x for x in v if x != k)
def sub(t):
    def ptr(m):
        v = word(img, int(m.group(2), 16))
        if v is None: return m.group(0)
        k = '%08x' % v
        return ('&' + nm[k][0]) if k in nm else ('&DAT_' + k if m.group(1) == 'DAT' else '&FUN_' + k)
    t = re.sub(r'PTR_(FUN|DAT|LAB)_([0-9a-fA-F]{8})', ptr, t)
    return re.sub(r'(?:FUN_|func_0x)([0-9a-fA-F]{8})', lambda m: nm.get(m.group(1).lower(), (m.group(0),))[0], t)
items = []
for a in sorted(own):
    name, cmt = own[a]
    if 'provisional' not in cmt: continue
    txt = '#### %s 0x%s %s | %s\n' % (prog, a, name, cmt)
    ob = sub(b.get(a, '(no body)\n')).splitlines()
    if len(ob) > 300: ob = ob[:300] + ['  ... (body truncated, %d lines)' % len(ob)]
    txt += '\n'.join(ob) + '\n'
    cs = sorted(set(cl.get(a, [])))
    txt += '---- callers: %d (%s)\n' % (len(cs), ' '.join(nm.get(c, (c,))[0] for c in cs[:12]))
    for c in cs[:3]:
        cb = sub(b.get(c, '')).splitlines()
        if len(cb) > 80: cb = cb[:80] + ['  ... (caller truncated)']
        txt += '---- caller %s\n%s\n' % (nm.get(c, (c,))[0], '\n'.join(cb))
    items.append(txt)
print(prog, "items", len(items))
if not items: sys.exit(0)
per = (len(items) + n - 1) // n
for k in range(n):
    open('%s%d.txt' % (pre, k + 1), 'w', encoding='utf-8', newline='\n').write('\n'.join(items[k * per:(k + 1) * per]))
