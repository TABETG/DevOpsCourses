import re, pathlib
d = pathlib.Path('/home/claude/build/cours-devops')
levels = [
 ("SbcBu2KkXvc1rsETDSdfDZ","devops-00-fondations.html","Niveau 0 — Fondations"),
 ("LkdWWLG4gRB39uXbRZdFuX","devops-01-virtualisation-et-conteneurs.html","Niveau 1 — Virtualisation et conteneurs"),
 ("DcFGfKkiYhcMDsZUak7ZnZ","devops-02-integration-et-livraison-continues.html","Niveau 2 — Intégration et livraison continues"),
 ("DYjxq8LXdD8Kq2yDcHwknN","devops-03-infrastructure-as-code.html","Niveau 3 — Infrastructure as Code"),
 ("2jgzWyEfQKo1srhkoXw79F","devops-04-cloud.html","Niveau 4 — Cloud"),
 ("9aqMcKBGhyJXNjJv96Sgoy","devops-05-kubernetes.html","Niveau 5 — Kubernetes"),
 ("59X5PJ2gqZqdM3zCNG6dgK","devops-06-observabilite.html","Niveau 6 — Observabilité"),
 ("4RwKD847kQZ5ANy53vfAP1","devops-07-securite-devsecops.html","Niveau 7 — Sécurité DevSecOps"),
 ("5vSsyu5nU23P6zZEAwXTr2","devops-08-sre-et-architecture.html","Niveau 8 — SRE et architecture"),
 ("JKKUXnD95WedqDgm9javjH","devops-09-expert-et-leadership.html","Niveau 9 — Expert et leadership"),
]
extra_css = """
.pagenav{display:flex;flex-wrap:wrap;gap:.6rem;margin-bottom:1rem;font-size:.9rem}
.pagenav a{color:#fff;text-decoration:none;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);padding:.3rem .75rem;border-radius:6px}
.pagenav a:hover{background:rgba(255,255,255,.2);color:#fff}
.footnav{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin-top:2rem;padding-top:1.2rem;border-top:1px solid var(--line)}
.footnav a{text-decoration:none;font-weight:700;background:var(--paper);border:1px solid var(--line);padding:.6rem 1rem;border-radius:var(--radius)}
.footnav a:hover{background:var(--accent-soft)}
@media print{.pagenav,.footnav{display:none}}
</style>"""
# index.html : liens locaux
idx = (d/'index.html').read_text()
for aid, fn, _ in levels:
    idx = idx.replace(f'https://claude.ai/artifact/{aid}', fn)
idx = idx.replace('https://claude.ai/artifact/3hJC54hLqcEAzTFtB1G8Qi', 'devops-11-fiches-entretien.html').replace('https://claude.ai/artifact/R1VURi7M5FUSwshfHjaKPB', 'devops-10-aide-memoire.html').replace('https://claude.ai/artifact/2Jr4M3v18aTLjxwmdL8377', 'cours-01-react.html').replace('https://claude.ai/artifact/FrwLKYymfrm4HRG9e3bxXB', 'cours-02-angular.html').replace('https://claude.ai/artifact/8c6eyxcphVfq93PeD3Uz7j', 'cours-03-vue.html').replace('https://claude.ai/artifact/9nfso3dXBZ9gFuRq7EbTjW', 'cours-14-cloud.html').replace('https://claude.ai/artifact/5G3dH1PuugUZzgy9dX353T', 'cours-06-java-pki-signature-electronique.html').replace('https://claude.ai/artifact/MginNSvHw2cEiK1iGuirjh', 'cours-15-data-platform-aws-talend.html').replace('https://claude.ai/artifact/E9pjLtYvMT664fGGVyyVpy', 'site-00-charte-graphique.html').replace('https://claude.ai/artifact/PdV8HSJ2VzyweicX7YQwxD', 'cours-04-struts-hibernate-jsp.html').replace('https://claude.ai/artifact/5i7dJdWaLocqqYt5GDio6V', 'cours-19-savoir-etre-situations-et-attitudes.html').replace('https://claude.ai/artifact/BT8jcW4tXpQHEZdrGCSZd8', 'cours-05-kotlin.html').replace('https://claude.ai/artifact/MTCRFWoXqA6fFvmUKgNaHd', 'cours-08-microservices.html').replace('https://claude.ai/artifact/9Xt8AFCrPaqysv7WPCLxZw', 'cours-10-ia-agentique.html').replace('https://claude.ai/artifact/MD7q8auT7ze4kvvYrPD2qq', 'cours-11-keycloak-et-iam.html').replace('https://claude.ai/artifact/89Bz6fX26dGg4yVce4xPUb', 'cours-16-monitoring.html').replace('https://claude.ai/artifact/AdVd1XGEaAxvMMjJHMuk1P', 'cours-18-savoir-etre-de-zero-a-expert.html').replace('https://claude.ai/artifact/9xRGVRTmjgFU9fkCg9XyBp', 'cours-03-vue.html').replace('https://claude.ai/artifact/R4VuBjse7pvSSB34Cu827M', 'cours-14-cloud.html')
idx = idx.replace('</style>', extra_css, 1)
(d/'index.html').write_text(idx)
# pages de niveau : lien accueil dans le hero, précédent/suivant en bas
for i,(aid, fn, title) in enumerate(levels):
    s = (d/fn).read_text()
    s = s.replace('</style>', extra_css, 1)
    s = s.replace('<div class="level">', '<div class="pagenav"><a href="index.html">← Accueil du parcours</a></div>\n    <div class="level">', 1)
    prev = f'<a href="{levels[i-1][1]}">← {levels[i-1][2]}</a>' if i>0 else '<a href="index.html">← Accueil du parcours</a>'
    nxt = f'<a href="{levels[i+1][1]}">{levels[i+1][2]} →</a>' if i<len(levels)-1 else '<a href="index.html">Retour à l\'accueil →</a>'
    s = s.replace('</main>', f'<div class="footnav">{prev}{nxt}</div>\n</main>', 1)
    (d/fn).write_text(s)
    print(fn, 'ok')
