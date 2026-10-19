# decmerge.py: merge Sonnet slice outputs naming/q<prog>_*.txt into hand_<prog>.txt (which holds the transferred
# names). Keeps the first line per address, makes names unique (_<last 5 hex digits> suffix), reports counts
# of addresses still unnamed against funcinfo_<prog>.tsv.
# usage: py -3.13 -I decmerge.py <ghidra> <prog>   (merges naming/q<prog>_*.txt into hand_<prog>.txt)
import sys, os, re, glob
g, prog = sys.argv[1], sys.argv[2]
hp = os.path.join(g, 'hand_%s.txt' % prog)
lines = {}
def add(fn):
    for l in open(fn, encoding='utf-8', errors='replace'):
        l = l.rstrip('\r\n')
        m = re.match(r'(0x[0-9a-fA-F]{8}) func ([A-Za-z_][A-Za-z0-9_]*) hand(.*)$', l)
        if not m: continue
        a = int(m.group(1), 16)
        if a not in lines: lines[a] = [m.group(2), m.group(3).strip()]
if os.path.exists(hp): add(hp)
for fn in sorted(glob.glob(os.path.join(g, 'naming', 'q%s_*.txt' % prog))): add(fn)
seen = set()
for a in sorted(lines):
    n = lines[a][0]
    if n in seen: lines[a][0] = '%s_%05x' % (n, a & 0xfffff)
    seen.add(lines[a][0])
out = ['0x%08x func %s hand %s' % (a, v[0], v[1]) for a, v in sorted(lines.items())]
open(hp, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
funcs = [int(f[1], 16) for f in (l.split() for l in open(os.path.join(g, 'funcinfo_%s.tsv' % prog), encoding='utf-8', errors='replace')) if f and f[0] == 'F']
miss = [a for a in funcs if a not in lines]
prov = sum(1 for v in lines.values() if 'provisional' in v[1])
print(prog, 'hand', len(out), 'provisional', prov, 'functions', len(funcs), 'unnamed', len(miss), ' '.join('%08x' % a for a in miss[:10]))
