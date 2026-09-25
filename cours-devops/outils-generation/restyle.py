"""Design unifié du site. Usage : python3 restyle.py <dossier cours-devops> [--online]
Injecte dans chaque page : la police, la feuille de style « site-design » (surcharge), la barre de navigation, le pied de page.
--online remplace les liens relatifs par les URLs claude.ai (voir ONLINE)."""
import re, sys, pathlib

ONLINE = {
 'cours-10-ia-agentique.html': 'https://claude.ai/artifact/9Xt8AFCrPaqysv7WPCLxZw',
 'cours-11-keycloak-et-iam.html': 'https://claude.ai/artifact/MD7q8auT7ze4kvvYrPD2qq',
 'cours-08-microservices.html': 'https://claude.ai/artifact/MTCRFWoXqA6fFvmUKgNaHd',
 'cours-16-monitoring.html': 'https://claude.ai/artifact/89Bz6fX26dGg4yVce4xPUb',
 'index.html': 'https://claude.ai/artifact/HgutA9nYckb1fQ3psqfsBj',
 'devops-00-fondations.html': 'https://claude.ai/artifact/SbcBu2KkXvc1rsETDSdfDZ', 'devops-01-virtualisation-et-conteneurs.html': 'https://claude.ai/artifact/LkdWWLG4gRB39uXbRZdFuX',
 'devops-02-integration-et-livraison-continues.html': 'https://claude.ai/artifact/DcFGfKkiYhcMDsZUak7ZnZ', 'devops-03-infrastructure-as-code.html': 'https://claude.ai/artifact/DYjxq8LXdD8Kq2yDcHwknN',
 'devops-04-cloud.html': 'https://claude.ai/artifact/2jgzWyEfQKo1srhkoXw79F', 'devops-05-kubernetes.html': 'https://claude.ai/artifact/9aqMcKBGhyJXNjJv96Sgoy',
 'devops-06-observabilite.html': 'https://claude.ai/artifact/59X5PJ2gqZqdM3zCNG6dgK', 'devops-07-securite-devsecops.html': 'https://claude.ai/artifact/4RwKD847kQZ5ANy53vfAP1',
 'devops-08-sre-et-architecture.html': 'https://claude.ai/artifact/5vSsyu5nU23P6zZEAwXTr2', 'devops-09-expert-et-leadership.html': 'https://claude.ai/artifact/JKKUXnD95WedqDgm9javjH',
 'devops-10-aide-memoire.html': 'https://claude.ai/artifact/R1VURi7M5FUSwshfHjaKPB', 'devops-11-fiches-entretien.html': 'https://claude.ai/artifact/3hJC54hLqcEAzTFtB1G8Qi',
 'cours-01-react.html': 'https://claude.ai/artifact/2Jr4M3v18aTLjxwmdL8377', 'cours-02-angular.html': 'https://claude.ai/artifact/FrwLKYymfrm4HRG9e3bxXB',
 'cours-03-vue.html': 'https://claude.ai/artifact/8c6eyxcphVfq93PeD3Uz7j', 'cours-14-cloud.html': 'https://claude.ai/artifact/9nfso3dXBZ9gFuRq7EbTjW',
 'cours-06-java-pki-signature-electronique.html': 'https://claude.ai/artifact/5G3dH1PuugUZzgy9dX353T', 'cours-15-data-platform-aws-talend.html': 'https://claude.ai/artifact/MginNSvHw2cEiK1iGuirjh',
 'site-00-charte-graphique.html': 'https://claude.ai/artifact/E9pjLtYvMT664fGGVyyVpy',
 'cours-04-struts-hibernate-jsp.html': 'https://claude.ai/artifact/PdV8HSJ2VzyweicX7YQwxD',
 'cours-19-savoir-etre-situations-et-attitudes.html': 'https://claude.ai/artifact/5i7dJdWaLocqqYt5GDio6V',
 'cours-05-kotlin.html': 'https://claude.ai/artifact/BT8jcW4tXpQHEZdrGCSZd8',
 'cours-18-savoir-etre-de-zero-a-expert.html': 'https://claude.ai/artifact/AdVd1XGEaAxvMMjJHMuk1P',
}
LEVEL_GROUPS = [
 ('Phase 1 · Les bases', [('devops-00-fondations.html', '0 · Fondations'), ('devops-01-virtualisation-et-conteneurs.html', '1 · Virtualisation et conteneurs')]),
 ('Phase 2 · Automatiser', [('devops-02-integration-et-livraison-continues.html', '2 · Intégration et livraison continues'), ('devops-03-infrastructure-as-code.html', '3 · Infrastructure as Code')]),
 ('Phase 3 · La plateforme', [('devops-04-cloud.html', '4 · Cloud'), ('devops-05-kubernetes.html', '5 · Kubernetes'), ('devops-06-observabilite.html', '6 · Observabilité')]),
 ('Phase 4 · Sécuriser, fiabiliser, diriger', [('devops-07-securite-devsecops.html', '7 · Sécurité DevSecOps'), ('devops-08-sre-et-architecture.html', '8 · SRE et architecture'), ('devops-09-expert-et-leadership.html', '9 · Expert et leadership')]),
]
COURSE_GROUPS = [
 ('Frontend', [('cours-01-react.html', 'React'), ('cours-02-angular.html', 'Angular'), ('cours-03-vue.html', 'Vue.js')]),
 ('Backend', [('cours-04-struts-hibernate-jsp.html', 'Struts, Hibernate et JSP'), ('cours-05-kotlin.html', 'Kotlin'), ('cours-06-java-pki-signature-electronique.html', 'Java PKI et signature')]),
 ('Architecture', [('cours-08-microservices.html', 'Microservices')]),
 ('Intelligence artificielle', [('cours-10-ia-agentique.html', 'IA agentique')]),
 ('Sécurité', [('cours-11-keycloak-et-iam.html', 'Keycloak et IAM')]),
 ('Cloud, données et exploitation', [('cours-14-cloud.html', 'Cloud'), ('cours-15-data-platform-aws-talend.html', 'Data Platform AWS Talend'), ('cours-16-monitoring.html', 'Monitoring')]),
 ('Savoir-être', [('cours-18-savoir-etre-de-zero-a-expert.html', 'De zéro à expert'), ('cours-19-savoir-etre-situations-et-attitudes.html', 'Situations et attitudes')]),
]
LEVELS = [x for _, g in LEVEL_GROUPS for x in g]
COURSES = [x for _, g in COURSE_GROUPS for x in g]

CSS = r"""
/* ===== Charte graphique unifiée (site-00-charte-graphique.html) ===== */
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


/* --- code : thème IDE (GitHub Dark), commun à tout le site --- */
:root{--code-bg:#0D1117;--code-ink:#E6EDF3;--code-line:#30363D;--code-kw:#FF7B72;--code-str:#A5D6FF;--code-com:#8B949E;--code-num:#79C0FF;--code-fn:#D2A8FF;--code-type:#FFA657;--code-ann:#F2CC60;--code-prompt:#7EE787;--code-key:#7EE787;--code-op:#FF7B72;--code-var:#FFA657}
pre{background:var(--code-bg)!important;color:var(--code-ink)!important;border:1px solid var(--code-line)!important;border-radius:10px;padding:2.4rem 1.1rem 1rem;font-size:.86em;line-height:1.6;tab-size:4;overflow:auto;position:relative;box-shadow:inset 0 1px 0 rgba(255,255,255,.04)}
pre code{background:none!important;color:inherit!important;padding:0!important;font-size:inherit!important;border:0!important}
pre::-webkit-scrollbar{height:10px}pre::-webkit-scrollbar-thumb{background:#484F58;border-radius:6px}pre::-webkit-scrollbar-track{background:#161B22}
pre .copy{background:#21262D!important;color:#C9D1D9!important;border:1px solid #30363D!important;border-radius:6px;font-size:.78rem;padding:.25rem .6rem;position:absolute;top:.6rem;right:.6rem;cursor:pointer;opacity:.85}pre .copy:hover{opacity:1;background:#30363D!important}
pre .explain{background:#21262D!important;color:#C9D1D9!important;border:1px solid #30363D!important;opacity:.92!important}
.tk-kw{color:var(--code-kw)}.tk-str{color:var(--code-str)}.tk-com{color:var(--code-com);font-style:italic}.tk-num{color:var(--code-num)}.tk-fn{color:var(--code-fn)}.tk-type{color:var(--code-type)}.tk-ann{color:var(--code-ann)}.tk-prompt{color:var(--code-prompt);font-weight:700}.tk-key{color:var(--code-key)}.tk-op{color:var(--code-op)}.tk-var{color:var(--code-var)}.tk-tag{color:var(--code-prompt)}
code:not(pre code){background:var(--accent-soft);color:var(--accent-ink);padding:.1em .4em;border-radius:5px;font-size:.9em}
[data-theme="dark"] code:not(pre code){background:#1C2A48;color:#93C5FD}
/* --- sommaire : grille sans dépendre de :has() --- */
.single.with-toc{display:grid;grid-template-columns:270px minmax(0,1fr);gap:2rem;align-items:start}
.single.with-toc>.toc{grid-column:1;grid-row:1 / span 60;position:sticky;top:calc(var(--topbar) + 16px);max-height:calc(100vh - var(--topbar) - 32px);overflow:auto}
.single.with-toc>:not(.toc){grid-column:2}
@media(max-width:900px){.single.with-toc{display:block}.single.with-toc>.toc{position:static;max-height:none;margin-bottom:1.2rem;overflow-x:auto}}

/* --- sommaire : design commun --- */
.toc{padding:1rem .9rem!important}
.toc strong{display:flex!important;align-items:center;gap:.5rem;font-size:.74rem!important;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)!important;margin:0 .2rem .6rem!important}
.toc strong::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--accent)}
.toc ol{list-style:none!important;padding:0!important;margin:0!important;display:grid!important;gap:.15rem;counter-reset:toc}
.toc li{margin:0!important;display:block!important;padding:0!important;counter-increment:none!important}
.toc li::before,.toc li::after,.toc li a::after{content:none!important;display:none!important}
.toc li a{display:grid;grid-template-columns:26px minmax(0,1fr);align-items:start;gap:.55rem;padding:.42rem .55rem;border-radius:8px;color:var(--ink)!important;text-decoration:none;font-size:.9rem;line-height:1.35;counter-increment:toc;transition:background .12s}
.toc li a::before{content:counter(toc);display:inline-grid;place-items:center;width:24px;height:24px;border-radius:7px;background:var(--accent-soft);color:var(--accent-ink);font-size:.72rem;font-weight:800;margin-top:1px}

.toc li a:hover{background:var(--accent-soft)}
.toc li a.active{background:var(--accent);color:#fff!important}.toc li a.active::before{background:rgba(255,255,255,.22);color:#fff}
.toc li a[href="#rev"]::before,.toc li a[href="#revision"]::before,nav.toc ol[start] a[href="#rev"]::before{content:"✓"!important}
.toc li a.toc-junior::before{background:#DCFCE7;color:#166534}.toc li a.toc-confirme::before{background:#DBEAFE;color:#1E40AF}.toc li a.toc-senior::before{background:#FEF3C7;color:#92400E}.toc li a.toc-expert::before{background:#FCE7F3;color:#9D174D}
.toc li a.active.toc-junior::before,.toc li a.active.toc-confirme::before,.toc li a.active.toc-senior::before,.toc li a.active.toc-expert::before{background:rgba(255,255,255,.22);color:#fff}
.toc .legend{margin-top:.8rem!important;padding-top:.7rem;border-top:1px solid var(--line);font-size:.8rem!important}
.toc .prog,.toc .progress{margin-top:.7rem}
@media(max-width:900px){.toc ol{grid-template-columns:1fr 1fr}.toc li a{font-size:.86rem}}
@media(max-width:560px){.toc ol{grid-template-columns:1fr}}
/* --- code : retour à la ligne avec indentation conservée --- */
pre.wrapped code{white-space:pre-wrap;word-break:break-word}
pre .ln{display:block;white-space:pre-wrap;overflow-wrap:anywhere}
pre .ln[data-ind]{text-indent:calc(var(--ind) * -1ch);padding-left:calc(var(--ind) * 1ch)}
pre .wrapbtn{position:absolute;top:.6rem;right:5.2rem;background:#21262D;color:#C9D1D9;border:1px solid #30363D;border-radius:6px;font-size:.78rem;padding:.25rem .55rem;cursor:pointer;opacity:.85}pre .wrapbtn:hover{opacity:1}
pre.wrapped{overflow-x:hidden}
pre .nl{display:none}


/* --- menus groupés --- */
.topbar nav>details>div.groups{grid-template-columns:repeat(2,minmax(220px,1fr));min-width:500px;gap:.1rem .6rem}
.topbar nav>details>div .g{display:grid;align-content:start}
.topbar nav>details>div .grp{font-size:.68rem;font-weight:800;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);padding:.55rem .7rem .2rem}
@media(max-width:900px){.topbar nav>details>div.groups{grid-template-columns:1fr;min-width:0}.topbar nav>details>div .grp{color:#8FA0BA}}
/* --- lecture rapide : ne garder que l'essentiel de chaque chapitre --- */
body.rapid article:not(.expanded) > :is(p,ul,ol,table,pre,.tablewrap,.avap,.se-why,.se-week,.se-recap,.se-check,.roadmap,.grid2,.grid3,details,.note,.memo,.card,figure:not(.fig)),
body.rapid article:not(.expanded) .exo > :not(.tag),body.rapid article:not(.expanded) .tp > :not(.tag){display:none!important}
body.rapid article:not(.expanded) .exo,body.rapid article:not(.expanded) .tp{padding:.5rem .9rem;opacity:.75}
body.rapid article:not(.expanded) h3{cursor:pointer}
body.rapid article:not(.expanded) h3::after{content:"  afficher ▾";font-size:.72rem;font-weight:600;color:var(--muted);letter-spacing:.04em}
body.rapid article .rapid-hint{display:block;font-size:.8rem;color:var(--muted);margin:.4rem 0 0}
.rapid-hint{display:none}
body.rapid article.expanded h3.rapid-toggle::after{content:"  réduire ▴";font-size:.72rem;font-weight:600;color:var(--muted)}
.topbar .rapid-btn{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.18);color:#fff;border-radius:8px;height:36px;padding:0 .7rem;font:inherit;font-size:.82rem;font-weight:700;cursor:pointer;margin-left:.25rem;white-space:nowrap}
.topbar .rapid-btn.on{background:#2563EB;border-color:#2563EB}
@media(max-width:900px){.topbar .rapid-btn{margin:.4rem 0 0}}

.fig.portrait img{max-height:680px;width:auto!important;max-width:100%;margin:0 auto}.gallery .fig.portrait img{max-height:none;width:100%!important}

/* --- tuiles (accueil, charte) --- */
.grp-label{display:flex;align-items:center;gap:.6rem;margin:1.2rem 0 .6rem;font-size:.74rem;font-weight:800;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}.grp-label::after{content:"";flex:1;height:1px;background:var(--line)}
.tiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}@media(max-width:1150px){.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:600px){.tiles{grid-template-columns:1fr}}
.tile{position:relative;display:flex;flex-direction:column;gap:.45rem;background:var(--paper);border:1px solid var(--line);border-top:4px solid var(--tile-c,var(--accent));border-radius:12px;padding:1rem 1.1rem;box-shadow:var(--shadow)}
.tile-head{display:flex;align-items:center;gap:.65rem}.tile .ic{flex:0 0 38px;height:38px;border-radius:10px;display:grid;place-items:center;background:var(--tile-soft,var(--accent-soft));color:var(--tile-c,var(--accent-ink));font-weight:800}
.tile h3{margin:0;border:0!important;padding:0!important;font-size:1.02rem;color:var(--ink)}.tile h3 a{color:inherit;text-decoration:none}.tile h3 a::after{content:"";position:absolute;inset:0}
.tile p{margin:0;font-size:.9rem;color:var(--muted)}.tile-foot{margin-top:auto;display:flex;justify-content:space-between;align-items:center;gap:.6rem;padding-top:.55rem;border-top:1px solid var(--line);font-size:.82rem}
.tile-foot .meta{color:var(--tile-c,var(--accent-ink));font-weight:700;white-space:nowrap}.tile-foot label{position:relative;z-index:2;color:var(--muted);display:flex;gap:.35rem;align-items:center}
.s-dev{--tile-c:#7C3AED;--tile-soft:#EDE9FE}
/* --- galerie de fiches, sous-parties repliables, code long replié --- */
.gallery{margin:1.4rem 0;padding:1rem;border:1px dashed var(--line-strong);border-radius:12px;background:var(--bg)}
.gallery>strong{display:block;font-size:.76rem;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);margin-bottom:.7rem}
.gallery .g-items{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.8rem}
.gallery figure.fig{margin:0;padding:.4rem;background:var(--paper)}
.gallery figure.fig img{aspect-ratio:4/3;object-fit:cover;object-position:top;border-radius:6px}
.gallery figcaption{font-size:.78rem;text-align:left;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.gallery .fig.zoomable::after{top:.7rem;right:.7rem;font-size:.7rem;padding:.2rem .45rem}
@media(max-width:700px){.gallery .g-items{grid-template-columns:1fr 1fr}}
details.sub{border:1px solid var(--line);border-radius:10px;background:var(--paper);margin:.7rem 0;padding:0}
details.sub>summary{padding:.75rem 1rem!important;font-weight:700;font-size:1rem!important;color:var(--ink)!important;cursor:pointer;list-style:none;display:flex!important;align-items:center;gap:.6rem;border:0!important;border-radius:10px!important;background:none!important;width:100%;box-sizing:border-box}
details.sub>summary:hover{background:var(--accent-soft)!important}
details.sub>summary::-webkit-details-marker{display:none}
details.sub>summary::before{content:""!important;width:0;height:0;border-left:7px solid var(--accent)!important;border-top:5px solid transparent!important;border-bottom:5px solid transparent!important;transition:transform .15s;flex:0 0 auto}
details.sub>summary::after{content:"afficher"!important;margin-left:auto;font-size:.72rem;font-weight:600;color:var(--muted);letter-spacing:.04em}
details.sub[open]>summary::after{content:"réduire"!important}
details.sub[open]>summary::before{transform:rotate(90deg)}
details.sub>*:not(summary){margin-left:1rem;margin-right:1rem}
details.sub[open]{padding-bottom:.4rem}
pre.clamped{max-height:calc(30 * 1.6em + 3.4rem);overflow:hidden}
pre.clamped::after{content:"";position:absolute;left:0;right:0;bottom:0;height:5rem;background:linear-gradient(rgba(13,17,23,0),var(--code-bg) 75%);pointer-events:none}
pre .morebtn{position:absolute;left:50%;transform:translateX(-50%);bottom:.7rem;z-index:2;background:#1F6FEB;color:#fff;border:0;border-radius:999px;font-size:.8rem;font-weight:700;padding:.35rem .9rem;cursor:pointer}
pre:not(.clamped) .morebtn{position:static;display:block;margin:.8rem auto 0;transform:none}

pre.ascii,pre.ascii code{white-space:pre!important;overflow-x:auto!important}
[data-theme="dark"] .pipe .col .cnt{color:#C3CCDA}
:is(.single,article) :is(p,li,td,dd,span,.entretien,.niche,.note) a:not([class]){color:#1D4ED8}
[data-theme="dark"] :is(.single,article) :is(p,li,td,dd,span,.entretien,.niche,.note) a:not([class]){color:#93C5FD}
/* --- accessibilité : contrastes clair et sombre --- */
.badge-niche,.tag-niche,.niche .tag{color:#0B6670}
[data-theme="dark"] .badge-niche,[data-theme="dark"] .tag-niche,[data-theme="dark"] .niche .tag,[data-theme="dark"] .legend .badge-niche{color:#5EEAD4}
.legend .badge-niche{color:#0B6670}
.pipe .col{opacity:.62}
.sitefooter .in>div:first-child a{text-decoration:underline;text-underline-offset:2px}
[data-theme="dark"] .tbox button.go,[data-theme="dark"] .pipe .primary,[data-theme="dark"] button.primary{color:#0B1220!important}
[data-theme="dark"] .toc li a.active{background:#2563EB;color:#fff!important}
[data-theme="dark"] .s-start{--tile-c:#5EEAD4}[data-theme="dark"] .s-devops{--tile-c:#93C5FD}[data-theme="dark"] .s-dev{--tile-c:#C4B5FD}
[data-theme="dark"] .s-cloud{--tile-c:#7DD3FC}[data-theme="dark"] .s-sec{--tile-c:#FCA5A5}[data-theme="dark"] .s-soft{--tile-c:#FDBA74}[data-theme="dark"] .s-rev{--tile-c:#CBD5E1}
:focus-visible{outline:3px solid #F59E0B;outline-offset:2px}
/* --- images agrandissables (visionneuse) --- */
.fig.zoomable{position:relative;cursor:zoom-in}
.fig.zoomable img{width:100%;height:auto;display:block;border-radius:6px}
.fig.zoomable::after{content:"⤢ Agrandir";position:absolute;top:.9rem;right:.9rem;background:rgba(15,23,42,.78);color:#fff;font-size:.78rem;font-weight:700;padding:.3rem .6rem;border-radius:6px;pointer-events:none}
.fig a[title="Ouvrir le schéma en grand"]{cursor:zoom-in}
.lightbox{position:fixed;inset:0;z-index:200;background:rgba(5,10,20,.94);display:none;flex-direction:column}
.lightbox.open{display:flex}
.lightbox .bar{display:flex;align-items:center;gap:.5rem;padding:.6rem 1rem;color:#fff;font-size:.9rem;background:rgba(0,0,0,.35)}
.lightbox .bar .cap{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#D7DEEA}
.lightbox .bar button,.lightbox .bar a{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);color:#fff;border-radius:8px;padding:.35rem .7rem;font:inherit;font-size:.85rem;text-decoration:none;cursor:pointer}
.lightbox .view{flex:1;overflow:auto;touch-action:pan-x pan-y pinch-zoom;display:flex;align-items:flex-start;justify-content:center;padding:1rem}
.lightbox .view img{flex:0 0 auto;max-width:none;width:min(96vw,1400px);height:auto;transform-origin:top center;transition:width .15s;cursor:zoom-in}
.lightbox .view img.big{width:2400px;cursor:zoom-out}
@media print{.topbar,.sitefooter,.lightbox{display:none}}
"""

def nav_html(current):
    def a(href, label): return f'<a href="{href}"{" class=\"current\"" if href == current else ""}>{label}</a>'
    grouped = lambda groups: ''.join('<div class="g"><span class="grp">' + name + '</span>' + ''.join(a(h, l) for h, l in items) + '</div>' for name, items in groups)
    lv = grouped(LEVEL_GROUPS); co = grouped(COURSE_GROUPS)
    return f'''<header class="topbar" id="topbar"><div class="in">
<a class="brand" href="index.html"><span class="logo">D</span>DevOps Courses</a>
<button class="burger" type="button" aria-label="Menu" onclick="document.getElementById('topbar').classList.toggle('open')">☰</button>
<nav>{a('index.html', 'Accueil')}<details><summary>Parcours DevOps</summary><div class="groups">{lv}</div></details><details><summary>Cours</summary><div class="groups">{co}</div></details>{a('devops-10-aide-memoire.html', 'Aide-mémoire')}{a('devops-11-fiches-entretien.html', 'Entretien')}
<button class="rapid-btn" type="button" title="N'afficher que le résumé, les objectifs, les titres et les schémas de chaque chapitre" onclick="(function(b){{var on=document.body.classList.toggle('rapid');b.classList.toggle('on',on);try{{localStorage.setItem('devops-rapid',on?'1':'')}}catch(e){{}}}})(this)">Lecture rapide</button>
<button class="theme-btn" type="button" aria-label="Basculer clair / sombre" onclick="(function(){{var r=document.documentElement;var n=r.getAttribute('data-theme')==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{{localStorage.setItem('devops-theme',n)}}catch(e){{}}}})()"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
</nav></div></header>
'''
FOOTER = f'''<footer class="sitefooter"><div class="in">
<div><div class="brand">DevOps Courses</div>Parcours DevOps de zéro à expert et cours complémentaires, avec CrisisShield comme fil conducteur. Tout tourne en Docker. Code source et outils de génération sur <a href="https://github.com/TABETG/DevOpsCourses" rel="noopener" style="display:inline">GitHub</a>.</div>
<div><h4>Parcours</h4>{''.join(f'<a href="{h}">{l}</a>' for h, l in LEVELS[:5])}<a href="index.html">Tous les niveaux →</a></div>
<div><h4>Cours</h4>{''.join(f'<a href="{h}">{l}</a>' for h, l in COURSES)}</div>
<div><h4>Réviser</h4><a href="devops-10-aide-memoire.html">Aide-mémoire</a><a href="devops-11-fiches-entretien.html">Fiches entretien</a><a href="site-00-charte-graphique.html">Charte graphique</a></div>
</div></footer>
'''
JS = r'''<script id="site-lightbox">(function(){
var lb=document.createElement('div');lb.className='lightbox';lb.innerHTML='<div class="bar"><span class="cap"></span><button type="button" data-zoom>Zoom ×2</button><a data-open target="_blank" rel="noopener">Nouvel onglet</a><button type="button" data-close>Fermer ✕</button></div><div class="view"><img alt=""></div>';
document.body.appendChild(lb);var img=lb.querySelector('.view img'),cap=lb.querySelector('.cap'),open=lb.querySelector('[data-open]');
function show(src,text){img.src=src;img.classList.remove('big');cap.textContent=text||'';open.href=src;lb.classList.add('open');document.body.style.overflow='hidden';}
function hide(){lb.classList.remove('open');document.body.style.overflow='';img.src='';}
lb.querySelector('[data-close]').addEventListener('click',hide);lb.addEventListener('click',function(e){if(e.target===lb||e.target.classList.contains('view'))hide();});
lb.querySelector('[data-zoom]').addEventListener('click',function(){img.classList.toggle('big');this.textContent=img.classList.contains('big')?'Zoom ×1':'Zoom ×2';});
img.addEventListener('click',function(){img.classList.toggle('big');});
document.addEventListener('keydown',function(e){if(e.key==='Escape')hide();});
document.querySelectorAll('figure.fig img').forEach(function(i){var f=i.closest('figure');var pc=function(){if(i.naturalHeight>i.naturalWidth*1.15)f.classList.add('portrait')};if(i.complete)pc();else i.addEventListener('load',pc);if(!f.classList.contains('zoomable')&&!i.closest('a'))f.classList.add('zoomable');
 var a=i.closest('a');if(a){a.addEventListener('click',function(e){e.preventDefault();show(i.getAttribute('data-full')||i.currentSrc||i.src,(f.querySelector('figcaption')||{}).textContent);});}
 else i.addEventListener('click',function(){show(i.getAttribute('data-full')||i.currentSrc||i.src,(f.querySelector('figcaption')||{}).textContent);});});
})();</script>
'''
HL = '<script id="site-highlight">' + pathlib.Path(__file__).with_name('site-highlight.js').read_text() + '</script>\n'
TOC = r'''<script id="site-toc">(function(){
/* scroll-spy du sommaire */
document.querySelectorAll('.toc ol[start]').forEach(function(o){o.style.counterReset='toc '+(parseInt(o.getAttribute('start'),10)-1);});
var links=Array.prototype.slice.call(document.querySelectorAll('.toc a[href^="#"]'));if(!links.length)return;
var map={};links.forEach(function(a){var id=a.getAttribute('href').slice(1);var el=document.getElementById(id);if(el)map[id]=a;});
var ids=Object.keys(map);if(!ids.length)return;var cur=null;
function setActive(id){if(cur===id)return;cur=id;links.forEach(function(a){a.classList.remove('active')});map[id].classList.add('active');var t=map[id].closest('.toc');if(t&&t.scrollHeight>t.clientHeight){var r=map[id].getBoundingClientRect(),tr=t.getBoundingClientRect();if(r.top<tr.top||r.bottom>tr.bottom)map[id].scrollIntoView({block:'nearest'});}}
function update(){var top=64+24,best=ids[0];for(var i=0;i<ids.length;i++){var r=document.getElementById(ids[i]).getBoundingClientRect();if(r.top<=top+8)best=ids[i];else break;}setActive(best);}
document.querySelectorAll('.cols,.tablewrap,.gallery .g-items').forEach(function(r){if(r.scrollWidth>r.clientWidth+2&&!r.hasAttribute('tabindex')){r.setAttribute('tabindex','0');r.setAttribute('role','region');r.setAttribute('aria-label','Contenu défilant horizontalement');}});
document.addEventListener('scroll',update,{passive:true});window.addEventListener('resize',update);update();
/* retour à la ligne du code avec indentation conservée */
document.querySelectorAll('pre > code').forEach(function(code){var pre=code.parentElement;if(/[\u2500-\u257F]/.test(code.textContent)){pre.classList.add('ascii');return;}var html=code.innerHTML.replace(/\n$/,'');var lines=html.split('\n');
 code.innerHTML=lines.map(function(l){var m=/^((?:&nbsp;|[ \t])*)/.exec(l.replace(/<[^>]+>/g,''));var ind=(m?m[1].replace(/\t/g,'    '):'').length;return '<span class="ln"'+(ind?' data-ind style="--ind:'+(ind+2)+'"':'')+'>'+l+'</span>';}).join('<span class="nl">\n</span>');
 var wide=false;lines.forEach(function(l){if(l.replace(/<[^>]+>/g,'').length>72)wide=true;});
 if(lines.length>34){pre.classList.add('clamped');var mb=document.createElement('button');mb.type='button';mb.className='morebtn';mb.textContent='Afficher les '+lines.length+' lignes ▾';mb.addEventListener('click',function(){var c=pre.classList.toggle('clamped');mb.textContent=c?'Afficher les '+lines.length+' lignes ▾':'Réduire ▴';if(c)pre.scrollIntoView({block:'nearest'});});pre.appendChild(mb);}
 if(wide){pre.classList.add('wrapped');var b=document.createElement('button');b.type='button';b.className='wrapbtn';b.textContent='⇤ Une ligne';b.title='Basculer le retour à la ligne';b.addEventListener('click',function(){pre.classList.toggle('wrapped');b.textContent=pre.classList.contains('wrapped')?'⇤ Une ligne':'⇌ Replier';});pre.appendChild(b);}
});
})();</script>
'''
RAPID = r'''<script id="site-rapid">(function(){try{if(localStorage.getItem('devops-rapid')==='1'){document.body.classList.add('rapid');var b=document.querySelector('.rapid-btn');if(b)b.classList.add('on');}}catch(e){}
document.querySelectorAll('article').forEach(function(a){var h=a.querySelector('h2');if(h&&!a.querySelector('.rapid-hint')){var s=document.createElement('span');s.className='rapid-hint';s.textContent='Lecture rapide : clique sur un titre de section pour afficher le chapitre entier.';h.insertAdjacentElement('afterend',s);}
 a.querySelectorAll('h3').forEach(function(t){t.classList.add('rapid-toggle');t.addEventListener('click',function(){if(document.body.classList.contains('rapid'))a.classList.toggle('expanded');});});});
})();</script>
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
    s = re.sub(r'<script id="site-lightbox">.*?</script>\n', '', s, flags=re.S)
    s = re.sub(r'<script id="site-highlight">.*?</script>\n', '', s, flags=re.S)
    s = re.sub(r'<script id="site-toc">.*?</script>\n', '', s, flags=re.S)
    s = re.sub(r'<script id="site-rapid">.*?</script>\n', '', s, flags=re.S)
    s = s.replace('<div class="single">\n<nav class="toc">', '<div class="single with-toc">\n<nav class="toc">').replace('<div class="single">\n<div class="toc">', '<div class="single with-toc">\n<div class="toc">')
    s = s.replace('</body>', foot + JS + HL + TOC + RAPID + '</body>', 1)
    path.write_text(s)

if __name__ == '__main__':
    base = pathlib.Path(sys.argv[1]); online = '--online' in sys.argv
    files = [p for p in base.rglob('*.html') if 'outils-generation' not in p.parts]
    for p in files: restyle(p, base, online)
    print(len(files), 'pages restylées', '(en ligne)' if online else '')
