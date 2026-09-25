"""Ajoute un sommaire collant (étapes numérotées) aux pages de correction qui ont au moins 4 étapes. Idempotent.
Usage : python3 corr_toc.py <dossier corrections>"""
import re, sys, pathlib, html
n = 0
for p in sorted(pathlib.Path(sys.argv[1]).glob('tp*.html')):
    s = p.read_text()
    if '<nav class="toc" data-auto="corrections">' in s: s = re.sub(r'<nav class="toc" data-auto="corrections">.*?</nav>\n', '', s, flags=re.S)
    k = 0
    def ident(m):
        global k
        k += 1
        return f'<article id="etape-{k}"' + m.group(1) + '>'
    k = 0; s = re.sub(r'<article(?! id=)([^>]*)>', ident, s)
    titres = re.findall(r'<article id="(etape-\d+)"[^>]*>.*?<h2[^>]*>(.*?)</h2>', s, flags=re.S)
    if len(titres) < 4: p.write_text(s); continue
    items = ''.join(f'<li><a href="#{i}">{re.sub(r"<[^>]+>", "", t).strip()}</a></li>' for i, t in titres)
    nav = f'<nav class="toc" data-auto="corrections"><strong>Étapes de la correction</strong><ol>{items}</ol></nav>\n'
    s = re.sub(r'<div class="single(?: with-toc)?">\n?', '<div class="single with-toc">\n' + nav, s, count=1)
    p.write_text(s); n += 1
print('sommaires ajoutés :', n)
