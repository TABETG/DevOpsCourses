import re, pathlib

LEVELS = {
 1:"junior",2:"junior",3:"junior",4:"junior",5:"junior",6:"confirme",
 7:"junior",8:"confirme",9:"confirme",10:"confirme",
 11:"confirme",12:"confirme",13:"confirme",14:"confirme",15:"senior",
 16:"confirme",17:"confirme",18:"senior",19:"senior",
 20:"confirme",21:"senior",22:"senior",23:"senior",24:"expert",
 25:"confirme",26:"confirme",27:"senior",28:"senior",29:"senior",30:"expert",31:"senior",
 32:"confirme",33:"senior",34:"senior",35:"senior",36:"senior",
 37:"senior",38:"senior",39:"expert",40:"expert",41:"expert",42:"expert",
 43:"senior",44:"expert",45:"senior",46:"expert",47:"expert",48:"expert",
 49:"expert",50:"expert",51:"expert",52:"expert",53:"expert",54:"expert",
}
LABEL = {"junior":"Junior","confirme":"Confirmé","senior":"Senior","expert":"Expert"}
ORDER = ["junior","confirme","senior","expert"]

CSS = """
/* ============ Badges de niveau ============ */
.badge{display:inline-block;font-size:.74rem;font-weight:700;letter-spacing:.01em;padding:.15rem .6rem;border-radius:999px;border:1px solid;margin-left:.45rem;vertical-align:middle;white-space:nowrap}
.badge::before{content:"";display:inline-block;width:.5em;height:.5em;border-radius:50%;background:currentColor;margin-right:.4em;vertical-align:middle}
.lvl-junior{color:#1B7A4E;background:#E4F5EB;border-color:#7CC79C}
.lvl-confirme{color:#0F3F94;background:#E6EEFB;border-color:#8FB1EC}
.lvl-senior{color:#9A5B00;background:#FFF6E3;border-color:#E9B860}
.lvl-expert{color:#8A1C3A;background:#FBE7EC;border-color:#E39CB0}
.badge-niche{color:#0E7C86;background:#E1F4F6;border-color:#8CCFD6;margin-left:0;margin-right:.5rem}
:root[data-theme="dark"] .lvl-junior{color:#6CD19B;background:#12291D;border-color:#2A6B48}
:root[data-theme="dark"] .lvl-confirme{color:#A9C7FA;background:#1A2A45;border-color:#2F4F8A}
:root[data-theme="dark"] .lvl-senior{color:#F1B75A;background:#2C2410;border-color:#7E5D1C}
:root[data-theme="dark"] .lvl-expert{color:#F2A2B8;background:#33151F;border-color:#7A2E44}
:root[data-theme="dark"] .badge-niche{color:#66D3DD;background:#0F2A2E;border-color:#1F5D64}
.chaphead{display:flex;flex-wrap:wrap;align-items:center;gap:.4rem;margin-bottom:.7rem}
.chaphead .chapnum{margin-bottom:0}
.legend{display:flex;flex-wrap:wrap;gap:.5rem .9rem;align-items:center;margin:.8rem 0 0;font-size:.9rem;color:var(--muted)}
.legend .badge{margin-left:0}
@media print{.badge{border-color:#000;color:#000;background:none}}
</style>"""

def badge(level):
    return f'<span class="badge lvl-{level}">{LABEL[level]}</span>'

files = [
 ("devops-niveau-0-fondations.html", range(1,7)),
 ("devops-niveau-1-conteneurs.html", range(7,11)),
 ("devops-niveau-2-ci-cd.html", range(11,16)),
 ("devops-niveau-3-infrastructure-as-code.html", range(16,20)),
 ("devops-niveau-4-cloud.html", range(20,25)),
 ("devops-niveau-5-kubernetes.html", range(25,32)),
 ("devops-niveau-6-observabilite.html", range(32,37)),
 ("devops-niveau-7-securite-devsecops.html", range(37,43)),
 ("devops-niveau-8-sre-architecture.html", range(43,49)),
 ("devops-niveau-9-expert-leadership.html", range(49,55)),
]
out = pathlib.Path('/mnt/user-data/outputs')
ranges = {}
for fn, chs in files:
    p = out/fn; s = p.read_text()
    if 'class="badge' in s:
        print(fn, 'déjà fait'); continue
    for ch in chs:
        old = f'<span class="chapnum">Chapitre {ch}</span>\n'
        assert old in s, (fn, ch)
        s = s.replace(old, f'<div class="chaphead"><span class="chapnum">Chapitre {ch}</span>{badge(LEVELS[ch])}</div>\n', 1)
    # marqueur sur les blocs de niche
    s = s.replace('<span class="tag">Pour sortir du lot — ', '<span class="tag"><span class="badge badge-niche">Techno de niche</span>Pour sortir du lot — ')
    # légende sous le sommaire
    lv = [LEVELS[c] for c in chs]
    lo, hi = min(lv, key=ORDER.index), max(lv, key=ORDER.index)
    ranges[fn] = (lo, hi)
    legend = ('<div class="legend">Niveau des chapitres : ' + ''.join(badge(l) for l in ORDER if l in set(lv)) +
              ' <span class="badge badge-niche">Techno de niche</span> = encadré différenciant dans chaque chapitre</div>\n  <div class="prog">')
    s = s.replace('  <div class="prog">', legend, 1)
    # dans le sommaire, un point coloré par chapitre
    def toc_fix(m):
        ch = int(m.group(1))
        return f'<li><a href="#c{ch}" class="toc-{LEVELS[ch]}">'
    s = re.sub(r'<li><a href="#c(\d+)">', toc_fix, s)
    s = s.replace("</style>", CSS + """""".replace("</style>",""), 1) if False else s.replace("</style>", CSS.replace("</style>", "") + """nav.toc a[class^="toc-"]::after{content:"";width:.5em;height:.5em;border-radius:50%;margin-left:auto;align-self:center}
nav.toc a.toc-junior::after{background:#1B7A4E}nav.toc a.toc-confirme::after{background:#1D5FD1}nav.toc a.toc-senior::after{background:#9A5B00}nav.toc a.toc-expert::after{background:#8A1C3A}
@media (max-width:900px){nav.toc a[class^="toc-"]::after{margin-left:.4rem}}
</style>""", 1)
    p.write_text(s)
    print(fn, s.count('class="badge lvl-'), s.count('badge-niche'))

# page d'accueil : badge d'étendue par niveau et légende
p = out/'devops-parcours-complet.html'; s = p.read_text()
if 'class="badge' not in s:
    for fn, (lo, hi) in ranges.items():
        rng = badge(lo) if lo == hi else badge(lo) + ' <span style="color:var(--muted)">→</span>' + badge(hi)
        s = re.sub(r'(<a class="btn" href="https://claude\.ai/artifact/[^"]+">Ouvrir</a>)',
                   lambda m, fn=fn: m.group(1), s)  # rien à faire ici, les liens restent
    # insérer les badges dans chaque carte : après le <h3>
    cards = {
     "Fondations":"devops-niveau-0-fondations.html","Virtualisation et conteneurs":"devops-niveau-1-conteneurs.html",
     "Intégration et livraison continues":"devops-niveau-2-ci-cd.html","Infrastructure as Code":"devops-niveau-3-infrastructure-as-code.html",
     "Cloud":"devops-niveau-4-cloud.html","Kubernetes":"devops-niveau-5-kubernetes.html","Observabilité":"devops-niveau-6-observabilite.html",
     "Sécurité DevSecOps":"devops-niveau-7-securite-devsecops.html","SRE et architecture":"devops-niveau-8-sre-architecture.html",
     "Expert et leadership":"devops-niveau-9-expert-leadership.html"}
    for title, fn in cards.items():
        lo, hi = ranges[fn]
        rng = badge(lo) if lo == hi else badge(lo) + '<span style="color:var(--muted);margin-left:.3rem">→</span>' + badge(hi)
        s = s.replace(f'<h3>{title}</h3>', f'<h3>{title}{rng}</h3>', 1)
    legend = ('<div class="legend">Échelle des chapitres : ' + ''.join(badge(l) for l in ORDER) +
              ' <span class="badge badge-niche">Techno de niche</span> = un encadré différenciant par chapitre</div>')
    s = s.replace('<h2 style="border-top:none;padding-top:0;margin-top:2.5rem">Les dix niveaux</h2>',
                  '<h2 style="border-top:none;padding-top:0;margin-top:2.5rem">Les dix niveaux</h2>\n' + legend, 1)
    s = s.replace("</style>", CSS, 1)
    p.write_text(s)
print('index ok')
