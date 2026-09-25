import re, pathlib

COEUR = set("""1.2 1.5 2.2 2.4 2.6 3.2 3.3 3.4 3.5 3.6 4.1 5.2 5.3 6.1 7.2 8.2 8.3 8.6 8.7 9.1 10.2 11.1 12.1 13.1 15.1 15.4
16.2 16.5 17.3 19.3 20.1 20.3 21.1 21.2 21.3 23.3 25.2 25.3 25.4 26.1 26.2 26.3 27.1 27.2 28.4 29.1 31.1 32.2 33.1 33.2 34.1
35.1 35.2 36.2 36.3 37.2 38.2 39.1 39.3 40.3 41.1 41.4 42.1 43.2 44.1 44.3 45.2 46.3 47.4 48.2 49.1 50.1 51.1 52.1 53.2 54.4""".split())

CONTEXTE = set("""1.1 1.3 2.5 3.1 4.3 4.5 5.1 6.2 6.3 7.1 7.3 9.4 10.1 11.3 12.3 13.3 14.4 15.2 16.1 17.1 17.2 17.6 18.1 18.2 18.3
19.4 20.4 20.5 22.1 22.2 22.3 23.1 23.4 24.1 24.2 24.3 25.1 26.6 29.4 30.1 30.2 30.3 30.4 31.4 32.1 32.4 33.4 33.5 34.4 34.5
36.1 36.4 37.6 38.6 39.6 40.5 42.4 43.1 44.4 45.4 46.6 48.1 48.5 49.4 51.5 52.2 52.4 53.1 53.5 54.1 54.2""".split())

CSS = """
/* ============ Tags de mémorisation ============ */
.tag-coeur{color:#A11B1B;background:#FDECEC;border-color:#E8A1A1}
.tag-important{color:#9A5B00;background:#FFF6E3;border-color:#E9B860}
.tag-contexte{color:#55606F;background:#EEF1F5;border-color:#C5CDD8}
.tag-coeur::before{content:"\\2605";background:none;width:auto;height:auto;border-radius:0;font-size:.85em;margin-right:.35em;vertical-align:baseline}
.tag-important::before{content:"!";background:none;width:auto;height:auto;border-radius:0;font-weight:900;margin-right:.35em;vertical-align:baseline}
.tag-contexte::before{content:"i";background:none;width:auto;height:auto;border-radius:0;font-weight:900;font-style:italic;margin-right:.35em;vertical-align:baseline}
:root[data-theme="dark"] .tag-coeur{color:#F29A9A;background:#3A1616;border-color:#7A2E2E}
:root[data-theme="dark"] .tag-important{color:#F1B75A;background:#2C2410;border-color:#7E5D1C}
:root[data-theme="dark"] .tag-contexte{color:#9AA7B8;background:#1F2833;border-color:#3A4654}
h3 .badge{font-size:.72rem;vertical-align:middle;margin-left:.5rem;font-weight:700;letter-spacing:0}
.memo{display:flex;flex-wrap:wrap;gap:.5rem .9rem;align-items:center;margin:1rem 0 .2rem;padding:.7rem .9rem;border:1px dashed var(--line-strong);border-radius:var(--radius);font-size:.88rem;color:var(--muted);background:var(--bg)}
.memo .badge{margin-left:0}
.memo b{color:var(--ink)}
@media (max-width:480px){h3 .badge{display:inline-block;margin:.3rem 0 0 0}}
</style>"""

MEMO = ('<div class="memo"><b>Que retenir :</b> <span class="badge tag-coeur">Par cœur</span> à restituer sans support (définitions, commandes, chiffres) '
        '<span class="badge tag-important">Important</span> à savoir expliquer avec ses mots '
        '<span class="badge tag-contexte">Bon à savoir</span> lu une fois, on sait où le retrouver</div>')

def tag(num):
    if num in COEUR: return '<span class="badge tag-coeur">Par cœur</span>'
    if num in CONTEXTE: return '<span class="badge tag-contexte">Bon à savoir</span>'
    return '<span class="badge tag-important">Important</span>'

out = pathlib.Path('/mnt/user-data/outputs')
seen = set()
for f in sorted(out.glob('devops-0*.html')):
    s = f.read_text()
    if 'tag-coeur' in s:
        print(f.name, 'déjà fait'); continue
    def rep(m):
        num = m.group(1); seen.add(num)
        return f'<h3>{num} {m.group(2)}{tag(num)}</h3>'
    s, n = re.subn(r'<h3>(\d+\.\d+) ([^<]*?)</h3>', rep, s)
    # le mémo sous les objectifs du premier chapitre de la page, et une ligne dans la légende du sommaire
    s = s.replace('</div>\n\n<h3>', '</div>\n' + MEMO + '\n\n<h3>', 1)
    s = s.replace(' <span class="badge badge-niche">Techno de niche</span> = encadré différenciant dans chaque chapitre</div>',
                  ' <span class="badge badge-niche">Techno de niche</span> = encadré différenciant dans chaque chapitre<br>Mémorisation : <span class="badge tag-coeur">Par cœur</span> <span class="badge tag-important">Important</span> <span class="badge tag-contexte">Bon à savoir</span></div>', 1)
    s = s.replace('</style>', CSS, 1)
    f.write_text(s)
    print(f.name, n, 'sous-titres tagués')

missing = (COEUR | CONTEXTE) - seen
print('références inconnues :', sorted(missing))

# page d'accueil : légende et explication
p = out/'devops-parcours-complet.html'; s = p.read_text()
if 'tag-coeur' not in s:
    s = s.replace('<span class="badge badge-niche">Techno de niche</span> = un encadré différenciant par chapitre</div>',
                  '<span class="badge badge-niche">Techno de niche</span> = un encadré différenciant par chapitre</div>\n' + MEMO, 1)
    s = s.replace('<li><strong>Technologie de niche</strong>',
                  '<li><strong>Tags de mémorisation</strong> : chaque sous-titre indique ce qu\'il faut en faire. « Par cœur » (environ 30 %) se révise à voix haute jusqu\'à le restituer sans support ; « Important » se comprend et s\'explique ; « Bon à savoir » se lit une fois. Pour réviser vite avant un entretien, ne relis que les sections « Par cœur » et les encadrés « En entretien ».</li>\n<li><strong>Technologie de niche</strong>', 1)
    s = s.replace('</style>', CSS, 1)
    p.write_text(s)
print('index ok')
