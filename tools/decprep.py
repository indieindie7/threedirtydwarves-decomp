# decprep.py: generic Sonnet naming-slice prep (from ClockworkKnight/tools/ovlprep.py).
# usage: py -3.13 -I decprep.py <ghidra dir> <prog> <N slices> <template file> [boot prog]
# Reads decomp_<prog>.c, replaces FUN_/func_0x/PTR_FUN_ addresses with names from hand_<boot>.txt and hand_<prog>.txt,
# writes naming/<prog>_sub.c, slices the still-unnamed FUN_ functions into naming/<prog>_<k>.c and writes
# naming/<prog>_prompt.txt from the template ({OVL} -> prog).
import sys, os, re
g, prog, n, tpl = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
boot = sys.argv[5] if len(sys.argv) > 5 else None
def hand(fn):
    d = {}
    if not os.path.exists(fn): return d
    for l in open(fn, encoding='utf-8', errors='replace'):
        f = l.split(None, 4)
        if len(f) >= 4: d[f[0][2:].lower().zfill(8)] = f[2]
    return d
own = hand(os.path.join(g, 'hand_%s.txt' % prog))
nm = {**(hand(os.path.join(g, 'hand_%s.txt' % boot)) if boot else {}), **own}
src = open(os.path.join(g, 'decomp_%s.c' % prog), encoding='utf-8', errors='replace').read()
src = re.sub(r'(?:func_0x|FUN_|PTR_FUN_)([0-9a-fA-F]{8})', lambda m: nm.get(m.group(1).lower(), m.group(0)), src)
nd = os.path.join(g, 'naming'); os.makedirs(nd, exist_ok=True)
open(os.path.join(nd, prog + '_sub.c'), 'w', encoding='utf-8', newline='\n').write(src)
funcs, cur = [], None
for l in src.splitlines(True):
    m = re.match(r'// ==== (\S+) @ ([0-9a-fA-F]+)', l)
    if m:
        cur = [m.group(1), m.group(2).lower().zfill(8), []]; funcs.append(cur)
    if cur: cur[2].append(l)
todo = [f for f in funcs if f[0].startswith('FUN_') and f[1] not in own]
tot = sum(len(f[2]) for f in todo); per = tot / max(n, 1)
k, acc, out, files = 1, 0, [], []
def flush():
    global k, acc, out
    if out:
        fn = os.path.join(nd, '%s_%d.c' % (prog, k))
        open(fn, 'w', encoding='utf-8', newline='\n').write(''.join(''.join(f[2]) for f in out))
        files.append((fn, len(out), sum(len(f[2]) for f in out)))
        k += 1; acc = 0; out = []
for f in todo:
    out.append(f); acc += len(f[2])
    if acc >= per and k < n: flush()
flush()
t = open(tpl, encoding='utf-8').read().replace('{OVL}', prog)
open(os.path.join(nd, prog + '_prompt.txt'), 'w', encoding='utf-8', newline='\n').write(t)
print(prog, 'todo', len(todo), 'lines', tot, ' '.join('%s:%d/%d' % (os.path.basename(a), b, c) for a, b, c in files))
