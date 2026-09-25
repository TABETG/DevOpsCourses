"""Insère une figure image à un ancrage. Usage : addfig_at.py <page> <ancrage> <webp> <slug> <légende> [--inline]
ancrage : h3:7.2 (après ce titre) · ch:c9 (après le résumé « En 30 secondes » du chapitre) · top (avant le premier chapitre) · rev (avant les questions de révision)"""
import sys, re, base64, pathlib
p, anchor, img, slug, cap = sys.argv[1:6]; inline = '--inline' in sys.argv
s = pathlib.Path(p).read_text()
if f'id="{slug}"' in s: print('déjà présent', slug); sys.exit()
src = 'data:image/webp;base64,' + base64.b64encode(pathlib.Path(img).read_bytes()).decode() if inline else f'images/{slug}.webp'
fig = f'\n<figure class="fig zoomable" id="{slug}"><img src="{src}" alt="{cap}" loading="lazy" decoding="async"><figcaption>{cap}</figcaption></figure>\n'
kind, _, val = anchor.partition(':')
if kind == 'h3': m = re.search(r'<h3[^>]*>' + re.escape(val) + r' [^<]*(?:<span[^>]*>[^<]*</span>)?</h3>', s); assert m, anchor; pos = m.end()
elif kind == 'ch': a = s.index(f'id="{val}"'); b = s.index('<div class="bref">', a); pos = s.index('</div>', b) + 6
elif kind == 'top': pos = s.index('<article')
elif kind == 'rev': pos = s.index('<ol class="quiz">')
else: raise SystemExit('ancrage inconnu')
pathlib.Path(p).write_text(s[:pos] + fig + s[pos:]); print('ok', anchor, slug)
