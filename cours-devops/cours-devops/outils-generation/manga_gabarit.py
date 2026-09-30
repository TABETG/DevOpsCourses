"""Gabarit de planche manga en trois cases (situation, conséquence, bonne pratique) et insertion dans une page.
Utilisé par manga7.py et les suivants."""
import re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from manga_engine import Strip, INK

def box(s, x, y, w, h, title, lines=(), fs=8.5):
    s.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
    s.label(x + w / 2, y + 17, title, 10)
    for k, t in enumerate(lines): s.label(x + w / 2, y + 36 + k * 14, t, fs, False)

def _check(sid, p0, p1, fin_lignes):
    for k, l in [('terminal', x) for x in p0['term'] + p1['term']] + [('bulle', x) for x in p0['bulle']] + [('encadré', x) for x in fin_lignes]:
        lim = {'terminal': 36, 'bulle': 19, 'encadré': 38}[k]
        if len(l) > lim: print(f'  ATTENTION {sid} : ligne de {k} trop longue ({len(l)} > {lim}) : {l}')

def strip3(sid, titre, chap, p0, p1, fin_titre, fin_lignes, legende):
    _check(sid, p0, p1, fin_lignes)
    s = Strip(sid, titre, chap)
    # case 1 : la situation
    x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
    s.terminal(x + 12, y + 36, 236, 22 + 16 * len(p0['term']), p0['term'], fs=8.8)
    s.chara(x + 196, y + 236, p0.get('who', 'kai'), p0.get('expr', 'smile'), p0.get('pose', 'chin'), scale=.72, flip=True)
    s.bubble(x + 8, y + 146, 150, p0['bulle'], tail=(x + 176, y + 180), fs=10); s.end(0)
    # case 2 : la conséquence
    x, y, w = s.begin(1)
    (s.night if p1.get('nuit', True) else (lambda x, y, w, h: s.tone(x, y, w, 60, 'dots')))(x, y, w, s.ph); s.floor(x, y + 236, w)
    s.terminal(x + 12, y + 28, 236, 22 + 16 * len(p1['term']), p1['term'], fs=8.8)
    if p1.get('rack', True): s.rack(x + 22, y + 134, 44, 102, alarm=True)
    s.chara(x + 178, y + 236, p1.get('who', 'mika'), p1.get('expr', 'panic'), p1.get('pose', 'head'), scale=.72)
    if p1.get('sfx'): s.sfx(x + 96, y + 190, p1['sfx'], 20, -8)
    s.end(1)
    # case 3 : la bonne pratique
    x, y, w = s.begin(2); s.floor(x, y + 236, w)
    box(s, x + 14, y + 18, 232, 22 + 14 * len(fin_lignes) + 12, fin_titre, fin_lignes)
    s.chara(x + 62, y + 236, 'sensei', 'smile', 'point', scale=.7); s.chara(x + 204, y + 236, 'kai', 'happy', 'stand', scale=.7, flip=True); s.end(2)
    return s.render(legende)

CSS = """
/* ============ Planches manga ============ */
.fig.manga svg{min-width:640px;border-radius:6px}
.fig.manga svg text{font-family:"Atkinson Hyperlegible",system-ui,sans-serif}
.fig.manga figcaption::before{content:"Manga — ";font-weight:700;color:var(--ink)}
:root[data-theme="dark"] .fig.manga svg{opacity:.94}
</style>"""

def apply(path, strips):
    """Insère les planches (liste de (id de chapitre, svg)) après le résumé « En 30 secondes » ; régénération idempotente."""
    p = pathlib.Path(path); S = p.read_text()
    S = re.sub(r'\n?<figure class="fig manga">.*?</figure>\n?', '\n', S, flags=re.S)
    if 'Planches manga' not in S: S = S.replace('</style>', CSS, 1)
    for cid, svg in strips:
        a = S.index(f'id="{cid}"'); b = S.index('<div class="bref">', a); e = S.index('</div>', b) + 6
        S = S[:e] + '\n' + svg + S[e:]
    p.write_text(S); print('planches :', S.count('class="fig manga"'))
