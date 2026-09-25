"""Rendre une page plus digeste, sans perdre de contenu.
- gallery(s, chap, ids, titre) : regroupe des figures (par id) en une galerie de vignettes agrandissables, avant les exercices du chapitre
- move_after_h3(s, fig_id, num) : déplace une figure juste après le titre de section « num »
- collapse_h4(s, num, open_first) : transforme les sous-parties h4 d'une section longue en panneaux repliables
- split_long(s, limite) : coupe les paragraphes trop longs à la phrase la plus proche du milieu
Usage en ligne de commande : python3 digest.py <page> <recette>   (recettes dans RECETTES)"""
import re, sys, pathlib

END_MARKERS = ('<h3', '<div class="entretien', '<div class="niche', '<div class="exo', '<div class="tp', '</article>')

def _fig(s, fid):
    m = re.search(r'\n?<figure class="fig[^"]*" id="' + re.escape(fid) + r'">.*?</figure>\n?', s, flags=re.S)
    return m

def _h3_end(s, num):
    m = re.search(r'<h3[^>]*>' + re.escape(num) + r' ', s); assert m, num
    return s.index('</h3>', m.start()) + 5

def _section_end(s, start):
    return min(x for x in (s.find(k, start) for k in END_MARKERS) if x > 0)

def gallery(s, chap, ids, titre="Fiches visuelles du chapitre — clique pour agrandir"):
    figs = []
    for fid in ids:
        m = _fig(s, fid)
        if not m: continue
        figs.append(m.group(0).strip().replace('class="fig"', 'class="fig zoomable"', 1)); s = s[:m.start()] + '\n' + s[m.end():]
    if not figs or f'id="gal-{chap}"' in s: return s
    a = s.index(f'<article id="{chap}"'); pos = s.find('<div class="exo"', a)
    block = f'\n<div class="gallery" id="gal-{chap}"><strong>{titre}</strong><div class="g-items">' + ''.join(figs) + '</div></div>\n'
    return s[:pos] + block + s[pos:]

def move_after_h3(s, fid, num):
    m = _fig(s, fid)
    if not m: return s
    fig = m.group(0).strip(); s = s[:m.start()] + '\n' + s[m.end():]
    pos = _h3_end(s, num)
    # après le contrôle de minuterie éventuel qui suit le titre
    ctl = re.match(r'\s*<div class="sprintctl.*?</div>', s[pos:], flags=re.S)
    if ctl: pos += ctl.end()
    return s[:pos] + '\n' + fig + '\n' + s[pos:]

def collapse_h4(s, num, open_first=True):
    start = _h3_end(s, num); end = _section_end(s, start); seg = s[start:end]
    if '<details class="sub"' in seg: return s
    parts = re.split(r'(?=<h4)', seg)
    if len(parts) < 3: return s
    out = parts[0]
    for k, p in enumerate(parts[1:]):
        m = re.match(r'<h4[^>]*>(.*?)</h4>(.*)', p, flags=re.S)
        body = m.group(2)
        if body.count('<div') != body.count('</div>') or body.count('<details') != body.count('</details>'): return s
        out += f'<details class="sub"{" open" if (k == 0 and open_first) else ""}><summary>{m.group(1)}</summary>{body}</details>\n'
    return s[:start] + out + s[end:]

def split_long(s, limite=90):
    a = s.find('<main')
    if a < 0: a = s.find('<div class="single')
    if a < 0: a = s.find('<body')
    b = s.find('<footer class="sitefooter">'); b = b if b > a else len(s)
    def rep(m):
        inner = m.group(1)
        if any(t in inner for t in ('<table', '<td', '<div', '<ul', '<ol', '<pre', '<details', '<figure', '<p ')): return m.group(0)
        if len(re.sub(r'<[^>]+>', ' ', inner).split()) <= limite: return m.group(0)
        cands = [x.start() for x in re.finditer(r'\. (?=[A-ZÀÂÉÈÊÎÔÛÇ«])', inner)
                 if inner.rfind('<', 0, x.start()) <= inner.rfind('>', 0, x.start()) and inner.count('<code', 0, x.start()) == inner.count('</code>', 0, x.start())]
        if not cands: return m.group(0)
        pos = min(cands, key=lambda p: abs(p - len(inner) / 2))
        return '<p>' + inner[:pos + 1] + '</p>\n<p>' + inner[pos + 2:] + '</p>'
    return s[:a] + re.sub(r'<p>(.*?)</p>', rep, s[a:b], flags=re.S) + s[b:]

RECETTES = {
 'cours': lambda s: split_long(s),
 'niveau-08': lambda s: split_long(collapse_h4(collapse_h4(s, '43.2'), '43.3')),
 'niveau-09': lambda s: split_long(collapse_h4(collapse_h4(collapse_h4(s, '53.6'), '54.5'), '54.7')),
 'niveau-07': lambda s: split_long(collapse_h4(s, '41.9')),
 'niveau-06': lambda s: split_long(s),
 'niveau-05': lambda s: split_long(collapse_h4(s, '25.7')),
 'niveau-04': lambda s: split_long(s),
 'niveau-03': lambda s: split_long(s),
 'niveau-02': lambda s: split_long(s),
 'niveau-01': lambda s: split_long(collapse_h4(collapse_h4(gallery(move_after_h3(s, 'chapitre-7-vm-conteneurs-isolation', '7.2'), 'c7',
      ['conteneur-pas-une-petite-vm', 'virtualisation-conteneurs-idees-cles', 'isolation-hyperviseurs-entreprise']), '7.4'), '7.5')),
}

if __name__ == '__main__':
    p = pathlib.Path(sys.argv[1]); s = p.read_text(); t = RECETTES[sys.argv[2]](s)
    p.write_text(t); print(p.name, 'modifiée' if t != s else 'inchangée')

def audit(s):
    """Rapport de lisibilité d'une page : mots par chapitre et par section, figures, code, paragraphes longs, sous-parties."""
    main = s[s.find('<main'):s.find('<footer class="sitefooter">')]
    W = lambda x: len(re.sub(r'<svg.*?</svg>|<[^>]+>', ' ', x, flags=re.S).split())
    out = [f'mots total {W(main)}']
    for m in re.finditer(r'<article id="(c\d+)"', main):
        a = main[m.start():]; n = a.find('<article ', 10); a = a[:n if n > 0 else a.find('</article>') + 10]
        pres = [p.count('\n') for p in re.findall(r'<pre.*?</pre>', a, flags=re.S)]
        figs = re.findall(r'<figure class="([^"]*)"', a)
        out.append(f"\n== {m.group(1)} {re.search(r'<h2>([^<]*)', a).group(1)[:60]} | mots {W(a)} | figures {len(figs)} ({', '.join(sorted(set(f.split()[-1] for f in figs)))}) | code {len(pres)} blocs, max {max(pres) if pres else 0} lignes | tableaux {a.count('<table')}")
        for p in re.findall(r'<p>(.*?)</p>', a, flags=re.S):
            w = len(re.sub(r'<[^>]+>', ' ', p).split())
            if w > 90: out.append(f'   paragraphe long {w} mots : {re.sub("<[^>]+>", "", p)[:60]}')
        for h in re.finditer(r'<h3[^>]*>(\d+\.\d+ [^<]*)', a):
            st = h.end(); en = _section_end(a, st); seg = a[st:en]
            flags = ' '.join(x for x, c in (('fig', '<figure'), ('code', '<pre'), ('table', '<table')) if c in seg)
            h4 = seg.count('<h4')
            out.append(f"   {h.group(1)[:58].ljust(58)} {str(W(seg)).rjust(5)} mots  {flags}{'  h4×' + str(h4) if h4 else ''}")
    return '\n'.join(out)
