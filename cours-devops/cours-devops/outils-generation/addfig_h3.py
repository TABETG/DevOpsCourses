"""Insère une figure image juste après un <h3> donné. Usage : addfig_h3.py <page> <numéro h3 ex 7.2> <webp> <slug> <légende> [--inline]"""
import sys, re, base64, pathlib
p, sec, img, slug, cap = sys.argv[1:6]; inline = '--inline' in sys.argv
s = pathlib.Path(p).read_text()
if slug in s: print('déjà présent'); sys.exit()
src = 'data:image/webp;base64,' + base64.b64encode(pathlib.Path(img).read_bytes()).decode() if inline else f'images/{slug}.webp'
link = '' if inline else f'<a href="{src}" target="_blank" rel="noopener" title="Ouvrir le schéma en grand">'
fig = f'\n<figure class="fig" id="{slug}">{link}<img src="{src}" alt="{cap}" style="width:100%;height:auto;display:block;border-radius:6px" loading="lazy" decoding="async">{"</a>" if link else ""}<figcaption>{cap}</figcaption></figure>\n'
m = re.search(r'<h3[^>]*>' + re.escape(sec) + r' [^<]*(?:<span[^>]*>[^<]*</span>)?</h3>', s); assert m, sec
pathlib.Path(p).write_text(s[:m.end()] + fig + s[m.end():]); print('ok', sec)
