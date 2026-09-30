"""Ajoute la réponse attendue sous chaque question de révision, et le schéma « flux complet d'une requête HTTP » au chapitre 3.
Usage : python3 revise.py <page.html> <niveau> [--inline-image]"""
import re, sys, html, base64, pathlib
sys.path.insert(0, '/home/claude')
from revise_answers import R
p = pathlib.Path(sys.argv[1]); lvl = int(sys.argv[2]); inline = '--inline-image' in sys.argv
s = p.read_text()
m = re.search(r'<ol class="quiz">(.*?)</ol>', s, flags=re.S)
items = re.findall(r'<li>(.*?)</li>', m.group(1), flags=re.S)
assert all((lvl, i) in R for i in range(1, len(items)+1)), (lvl, len(items))
new = ''.join(f'<li>{it}<details class="rep"><summary>Réponse attendue</summary><div class="sol">{html.escape(R[(lvl,i)], quote=False)}</div></details></li>\n' for i, it in enumerate(items, 1))
s = s[:m.start(1)] + new.replace('<details class="rep">', '\n<details class="rep">') + s[m.end(1):]
if '.rep' not in s:
    s = s.replace('</style>', '.quiz details.rep{margin:.3rem 0 .6rem}\n.quiz details.rep summary{font-size:.85rem;font-weight:700;color:var(--muted)}\n.quiz details.rep .sol{font-size:.9rem}\n</style>', 1)
if lvl == 0 and 'flux-complet-requete-http' not in s:
    src = 'data:image/webp;base64,' + base64.b64encode(pathlib.Path('/home/claude/flux.webp').read_bytes()).decode() if inline else 'images/flux-complet-requete-http.webp'
    link = '' if inline else f'<a href="{src}" target="_blank" rel="noopener" title="Ouvrir le schéma en grand">'
    fig = f'<figure class="fig" id="flux-complet-requete-http">{link}<img src="{src}" alt="Flux complet d\'une requête HTTPS : utilisateur, DNS, Internet, load balancer, VPC et Kubernetes, base de données" style="width:100%;height:auto;display:block;border-radius:6px" loading="lazy">{"</a>" if link else ""}<figcaption>Flux complet d\'une requête HTTPS, de l\'utilisateur à la base de données : DNS, TCP, TLS, load balancer, Ingress, Service, Pod, puis la réponse par le même chemin. Les douze étapes numérotées sont celles du diagnostic (question 8 de la révision).</figcaption></figure>\n'
    a = s.find('id="c3"'); j = s.find('<figure class="fig">', a)
    s = s[:j] + fig + s[j:]
p.write_text(s); print(p.name, len(items), 'réponses', 'image' if lvl == 0 else '')
