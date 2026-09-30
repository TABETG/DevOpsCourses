"""Insère une figure image au début d'un chapitre. Usage : addfig.py <page> <id chapitre> <webp> <slug> <légende> [--inline]"""
import sys, base64, pathlib
p, cid, img, slug, cap = map(pathlib.Path.__call__ if False else str, sys.argv[1:6]); inline = '--inline' in sys.argv
s = pathlib.Path(p).read_text()
if slug in s: print('déjà présent'); sys.exit()
src = 'data:image/webp;base64,' + base64.b64encode(pathlib.Path(img).read_bytes()).decode() if inline else f'images/{slug}.webp'
link = '' if inline else f'<a href="{src}" target="_blank" rel="noopener" title="Ouvrir le schéma en grand">'
fig = f'<figure class="fig" id="{slug}">{link}<img src="{src}" alt="{cap}" style="width:100%;height:auto;display:block;border-radius:6px" loading="lazy">{"</a>" if link else ""}<figcaption>{cap}</figcaption></figure>\n'
a = s.find(f'id="{cid}"'); j = s.find('<figure class="fig">', a); assert a > 0 and j > 0
pathlib.Path(p).write_text(s[:j] + fig + s[j:]); print('ok', p)
