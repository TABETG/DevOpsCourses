"""Design unifié du site. Usage : python3 restyle.py <dossier cours-devops> [--online]
Injecte dans chaque page : la police, la feuille de style « site-design » (surcharge), la barre de navigation, le pied de page.
--online remplace les liens relatifs par les URLs claude.ai (voir ONLINE)."""
import re, sys, pathlib

ONLINE = {
 'index.html': 'https://claude.ai/artifact/HgutA9nYckb1fQ3psqfsBj',
 'devops-niveau-0-fondations.html': 'https://claude.ai/artifact/SbcBu2KkXvc1rsETDSdfDZ', 'devops-niveau-1-conteneurs.html': 'https://claude.ai/artifact/LkdWWLG4gRB39uXbRZdFuX',
 'devops-niveau-2-ci-cd.html': 'https://claude.ai/artifact/DcFGfKkiYhcMDsZUak7ZnZ', 'devops-niveau-3-infrastructure-as-code.html': 'https://claude.ai/artifact/DYjxq8LXdD8Kq2yDcHwknN',
 'devops-niveau-4-cloud.html': 'https://claude.ai/artifact/2jgzWyEfQKo1srhkoXw79F', 'devops-niveau-5-kubernetes.html': 'https://claude.ai/artifact/9aqMcKBGhyJXNjJv96Sgoy',
 'devops-niveau-6-observabilite.html': 'https://claude.ai/artifact/59X5PJ2gqZqdM3zCNG6dgK', 'devops-niveau-7-securite-devsecops.html': 'https://claude.ai/artifact/4RwKD847kQZ5ANy53vfAP1',
 'devops-niveau-8-sre-architecture.html': 'https://claude.ai/artifact/5vSsyu5nU23P6zZEAwXTr2', 'devops-niveau-9-expert-leadership.html': 'https://claude.ai/artifact/JKKUXnD95WedqDgm9javjH',
 'devops-aide-memoire.html': 'https://claude.ai/artifact/R1VURi7M5FUSwshfHjaKPB', 'devops-fiches-entretien.html': 'https://claude.ai/artifact/3hJC54hLqcEAzTFtB1G8Qi',
 'cours-react.html': 'https://claude.ai/artifact/2Jr4M3v18aTLjxwmdL8377', 'cours-angular.html': 'https://claude.ai/artifact/FrwLKYymfrm4HRG9e3bxXB',
 'cours-vue.html': 'https://claude.ai/artifact/8c6eyxcphVfq93PeD3Uz7j', 'cours-cloud.html': 'https://claude.ai/artifact/9nfso3dXBZ9gFuRq7EbTjW',
 'cours-java-pki-signature-electronique.html': 'https://claude.ai/artifact/5G3dH1PuugUZzgy9dX353T', 'cours-data-platform-aws-talend.html': 'https://claude.ai/artifact/MginNSvHw2cEiK1iGuirjh',
 'maquette.html': 'https://claude.ai/artifact/E9pjLtYvMT664fGGVyyVpy',
 'cours-struts-hibernate-jsp.html': 'https://claude.ai/artifact/PdV8HSJ2VzyweicX7YQwxD',
}
LEVELS = [('devops-niveau-0-fondations.html', '0 · Fondations'), ('devops-niveau-1-conteneurs.html', '1 · Conteneurs'), ('devops-niveau-2-ci-cd.html', '2 · CI/CD'), ('devops-niveau-3-infrastructure-as-code.html', '3 · Infrastructure as Code'), ('devops-niveau-4-cloud.html', '4 · Cloud'), ('devops-niveau-5-kubernetes.html', '5 · Kubernetes'), ('devops-niveau-6-observabilite.html', '6 · Observabilité'), ('devops-niveau-7-securite-devsecops.html', '7 · Sécurité DevSecOps'), ('devops-niveau-8-sre-architecture.html', '8 · SRE et architecture'), ('devops-niveau-9-expert-leadership.html', '9 · Expert et leadership')]
COURSES = [('cours-react.html', 'React'), ('cours-angular.html', 'Angular'), ('cours-vue.html', 'Vue.js'), ('cours-cloud.html', 'Cloud'), ('cours-java-pki-signature-electronique.html', 'Java PKI et signature'), ('cours-data-platform-aws-talend.html', 'Data Platform AWS Talend'), ('cours-struts-hibernate-jsp.html', 'Struts, Hibernate et JSP')]

CSS = r"""
/* ===== Charte graphique unifiée (maquette.html) ===== */
:root{--bg:#F4F6FA;--paper:#FFFFFF;--ink:#0F172A;--muted:#5B6474;--line:#E2E8F0;--line-strong:#CBD5E1;--accent:#2563EB;--accent-ink:#1E40AF;--accent-soft:#EAF1FE;--hero:#0B1220;--hero-2:#132A57;--radius:12px;--shadow:0 1px 2px rgba(15,23,42,.05),0 6px 18px rgba(15,23,42,.06);--topbar:64px;--code-bg:#0F172A;--code-ink:#E2E8F0;--code-line:#1E293B}
[data-theme="dark"]{--bg:#0B1220;--paper:#111A2E;--ink:#E5EAF3;--muted:#9AA6BA;--line:#22304A;--line-strong:#33456A;--accent:#60A5FA;--accent-ink:#93C5FD;--accent-soft:#16264A;--hero:#070D1A;--hero-2:#0F2148;--shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.35);--code-bg:#060B16;--code-line:#1F2C46}
html{scroll-padding-top:calc(var(--topbar) + 16px)}
body{font-family:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif;font-size:16.5px;line-height:1.65;background:var(--bg);color:var(--ink)}
pre,code,kbd{font-family:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace}
h1,h2,h3,h4{letter-spacing:-.01em}
/* --- barre de navigation --- */
.topbar{position:sticky;top:0;z-index:80;height:var(--topbar);background:var(--hero);color:#fff;border-bottom:1px solid rgba(255,255,255,.08);box-shadow:0 2px 12px rgba(0,0,0,.25)}
.topbar .in{max-width:1180px;margin:0 auto;padding:0 1.25rem;height:100%;display:flex;align-items:center;gap:1rem}
.topbar .brand{display:flex;align-items:center;gap:.6rem;color:#fff;text-decoration:none;font-weight:800;font-size:1.05rem;letter-spacing:-.01em;white-space:nowrap}
.topbar .brand .logo{width:30px;height:30px;border-radius:8px;background:linear-gradient(135deg,#3B82F6,#22D3EE);display:grid;place-items:center;font-size:.95rem;color:#0B1220;font-weight:900}
.topbar nav{margin-left:auto;display:flex;align-items:center;gap:.25rem}
.topbar nav>a,.topbar nav>details>summary{color:#D7DEEA;text-decoration:none;font-size:.92rem;font-weight:600;padding:.45rem .7rem;border-radius:8px;cursor:pointer;list-style:none;white-space:nowrap}
.topbar nav>details>summary::-webkit-details-marker{display:none}
.topbar nav>details>summary::after{content:" ▾";font-size:.75em;opacity:.7}
.topbar nav>a:hover,.topbar nav>details>summary:hover,.topbar nav>a.current{background:rgba(255,255,255,.1);color:#fff}
.topbar nav>details{position:relative;margin:0;background:none;border:0;padding:0;box-shadow:none}
.topbar nav>details>summary::before,.topbar nav>details>summary::marker{content:none;display:none}
.topbar nav>details>summary{background:none;border:0;padding:.45rem .7rem}
.topbar nav>details>div{position:absolute;right:0;top:calc(100% + 6px);min-width:260px;background:var(--paper);color:var(--ink);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);padding:.4rem;display:grid}
.topbar nav>details>div a{color:var(--ink);text-decoration:none;font-size:.9rem;padding:.45rem .7rem;border-radius:8px}
.topbar nav>details>div a:hover{background:var(--accent-soft);color:var(--accent-ink)}
.topbar .theme-btn{display:inline-grid;place-items:center;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.18);color:#fff;border-radius:8px;width:36px;height:36px;font-size:1rem;cursor:pointer;margin-left:.25rem}
.topbar .burger{display:none;background:none;border:1px solid rgba(255,255,255,.2);color:#fff;border-radius:8px;width:38px;height:36px;font-size:1.1rem;cursor:pointer;margin-left:auto}
@media(max-width:900px){.topbar nav{display:none;position:absolute;left:0;right:0;top:var(--topbar);background:var(--hero);flex-direction:column;align-items:stretch;padding:.6rem 1rem 1rem;gap:.15rem;border-bottom:1px solid rgba(255,255,255,.1)}
 .topbar.open nav{display:flex}.topbar .burger{display:block}.topbar nav>details>div{position:static;margin:.2rem 0 .4rem .5rem;background:rgba(255,255,255,.06);border-color:rgba(255,255,255,.12)}.topbar nav>details>div a{color:#D7DEEA}.topbar .theme-btn{display:inline-grid;place-items:center;margin:.4rem 0 0}}
/* --- bandeau de page --- */
.hero{background:linear-gradient(120deg,var(--hero) 0%,var(--hero-2) 100%);background-image:linear-gradient(120deg,var(--hero) 0%,var(--hero-2) 100%);padding:2.4rem 1.25rem 2rem;color:#fff}
.hero .in{max-width:1180px;margin:0 auto}
.hero .pagenav{display:none}
.hero .level{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.18);font-size:.8rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:.25rem .7rem;border-radius:999px;margin-bottom:1rem}
.hero h1{font-size:clamp(1.7rem,3.2vw,2.5rem);line-height:1.15;margin:.2rem 0 .8rem;max-width:30ch}
.hero .lead,.hero p{max-width:70ch;color:#D7DEEA;font-size:1.05rem;line-height:1.6;margin:0 0 1rem}
.hero .meta{display:flex;flex-wrap:wrap;gap:.5rem;margin:.6rem 0 0}
.hero .meta span,.hero .btn,.hero .pill{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.16);border-radius:8px;padding:.3rem .7rem;font-size:.85rem;color:#E6ECF7}
.hero .theme,#theme{display:none}
.hero .global,.hero .bar{max-width:70ch}
/* --- conteneurs --- */
.wrap{max-width:1180px;margin:0 auto;padding:1.6rem 1.25rem 4rem;display:grid;grid-template-columns:270px minmax(0,1fr);gap:2rem;align-items:start}
.single{max-width:1180px;margin:0 auto;padding:1.6rem 1.25rem 4rem}
.single:has(> .toc){display:grid;grid-template-columns:270px minmax(0,1fr);gap:2rem;align-items:start}
.single:has(> .toc)>.toc{grid-column:1;grid-row:1 / span 60;position:sticky;top:calc(var(--topbar) + 16px);max-height:calc(100vh - var(--topbar) - 32px);overflow:auto}
.single:has(> .toc)>:not(.toc){grid-column:2}
.wrap>nav.toc,.single>.toc{position:sticky;top:calc(var(--topbar) + 16px);max-height:calc(100vh - var(--topbar) - 32px);overflow:auto;background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);padding:1rem 1.1rem;box-shadow:var(--shadow);font-size:.92rem}
.toc strong{display:block;font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:.5rem}
.toc ol{columns:1!important;padding-left:1.2rem;margin:.2rem 0}
.toc li{margin:.15rem 0}
.toc a{color:var(--ink);text-decoration:none}.toc a:hover{color:var(--accent)}
@media(max-width:900px){.wrap,.single:has(> .toc){display:block}.wrap>nav.toc,.single>.toc{position:static;max-height:none;margin-bottom:1.2rem;overflow-x:auto}body{overflow-x:hidden}}
article,.card,.memo,.global,.note{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}
article{padding:1.6rem 1.9rem 1.8rem;margin-bottom:1.6rem}
.chaphead .chapnum,.chaphead .badge{font-size:.74rem}
.chapnum{background:var(--accent-soft);color:var(--accent-ink);font-weight:700;padding:.2rem .6rem;border-radius:999px}
article h2,.single h2{border-top:0;margin-top:.4rem;padding-top:0;font-size:1.65rem}
h2{border-top:0;padding-top:0}
h3{border-left:3px solid var(--accent);padding-left:.7rem;font-size:1.15rem;color:var(--accent-ink)}
a{color:var(--accent)}
.bref,.objectifs,.exo,.tp,.fig,.memo,.note{border-radius:10px}
.bref{background:var(--accent-soft);border:1px solid transparent;border-left:4px solid var(--accent)}
.bref .tag,.exo .tag,.tp .tag{display:inline-block;font-size:.72rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;margin-bottom:.4rem}
pre{border-radius:10px;font-size:.84em}
.copy{border-radius:6px}
table{font-size:.92em}th{background:var(--accent-soft);color:var(--accent-ink)}
details>summary{cursor:pointer;font-weight:700;color:var(--accent-ink)}
.footnav a{border-radius:10px}
/* --- pied de page --- */
.sitefooter{background:var(--hero);color:#B7C1D3;padding:2rem 1.25rem 2.4rem;margin-top:2rem;font-size:.9rem}
.sitefooter .in{max-width:1180px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:1.5rem}
.sitefooter h4{color:#fff;margin:0 0 .5rem;font-size:.85rem;letter-spacing:.06em;text-transform:uppercase}
.sitefooter a{color:#D7DEEA;text-decoration:none;display:block;padding:.15rem 0}.sitefooter a:hover{color:#fff}
.sitefooter .brand{color:#fff;font-weight:800;font-size:1.05rem;margin-bottom:.4rem}
@media(max-width:800px){.sitefooter .in{grid-template-columns:1fr 1fr}}
#sprint{background:var(--hero)}
@media print{.topbar,.sitefooter{display:none}}
"""

def nav_html(current):
    def a(href, label): return f'<a href="{href}"{" class=\"current\"" if href == current else ""}>{label}</a>'
    lv = ''.join(a(h, l) for h, l in LEVELS); co = ''.join(a(h, l) for h, l in COURSES)
    return f'''<header class="topbar" id="topbar"><div class="in">
<a class="brand" href="index.html"><span class="logo">D</span>DevOps Courses</a>
<button class="burger" type="button" aria-label="Menu" onclick="document.getElementById('topbar').classList.toggle('open')">☰</button>
<nav>{a('index.html', 'Accueil')}<details><summary>Parcours DevOps</summary><div>{lv}</div></details><details><summary>Cours</summary><div>{co}</div></details>{a('devops-aide-memoire.html', 'Aide-mémoire')}{a('devops-fiches-entretien.html', 'Entretien')}
<button class="theme-btn" type="button" aria-label="Basculer clair / sombre" onclick="(function(){{var r=document.documentElement;var n=r.getAttribute('data-theme')==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{{localStorage.setItem('devops-theme',n)}}catch(e){{}}}})()"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
</nav></div></header>
'''
FOOTER = f'''<footer class="sitefooter"><div class="in">
<div><div class="brand">DevOps Courses</div>Parcours DevOps de zéro à expert et cours complémentaires, avec CrisisShield comme fil conducteur. Tout tourne en Docker. Code source et outils de génération sur <a href="https://github.com/TABETG/DevOpsCourses" rel="noopener" style="display:inline">GitHub</a>.</div>
<div><h4>Parcours</h4>{''.join(f'<a href="{h}">{l}</a>' for h, l in LEVELS[:5])}<a href="index.html">Tous les niveaux →</a></div>
<div><h4>Cours</h4>{''.join(f'<a href="{h}">{l}</a>' for h, l in COURSES)}</div>
<div><h4>Réviser</h4><a href="devops-aide-memoire.html">Aide-mémoire</a><a href="devops-fiches-entretien.html">Fiches entretien</a><a href="maquette.html">Charte graphique</a></div>
</div></footer>
'''
FONT = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">\n'

def restyle(path, base, online):
    s = path.read_text()
    s = re.sub(r'<style id="site-design">.*?</style>\n', '', s, flags=re.S)
    s = re.sub(r'<header class="topbar".*?</header>\n', '', s, flags=re.S)
    s = re.sub(r'<footer class="sitefooter">.*?</footer>\n', '', s, flags=re.S)
    if 'family=Inter' not in s: s = s.replace('</head>', FONT + '</head>', 1)
    s = s.replace('</head>', f'<style id="site-design">{CSS}</style>\n</head>', 1)
    rel = path.relative_to(base); prefix = '../' * (len(rel.parts) - 1)
    top = nav_html(rel.name if prefix == '' else '#'); foot = FOOTER
    if prefix: top = top.replace('href="', f'href="{prefix}').replace(f'href="{prefix}#', 'href="#'); foot = foot.replace('href="', f'href="{prefix}').replace(f'href="{prefix}https', 'href="https')
    if online:
        for k, v in ONLINE.items(): top = top.replace(f'href="{k}"', f'href="{v}"'); foot = foot.replace(f'href="{k}"', f'href="{v}"')
    s = re.sub(r'<body([^>]*)>\n?', lambda m: f'<body{m.group(1)}>\n' + top, s, count=1)
    s = s.replace('</body>', foot + '</body>', 1)
    path.write_text(s)

if __name__ == '__main__':
    base = pathlib.Path(sys.argv[1]); online = '--online' in sys.argv
    files = [p for p in base.rglob('*.html') if 'outils-generation' not in p.parts]
    for p in files: restyle(p, base, online)
    print(len(files), 'pages restylées', '(en ligne)' if online else '')
