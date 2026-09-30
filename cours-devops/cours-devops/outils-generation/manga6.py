"""Planches manga du niveau 4 (chapitres 20 à 24). Usage : python3 manga6.py <page niveau 4>"""
import sys, re, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from manga_engine import Strip, INK
p = pathlib.Path(sys.argv[1]); S = p.read_text()
S = re.sub(r'\n?<figure class="fig manga">.*?</figure>\n?', '\n', S, flags=re.S)
STRIPS = []
def box(s, x, y, w, h, title, lines=(), fs=9):
    s.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
    s.label(x + w / 2, y + 17, title, 10)
    for k, t in enumerate(lines): s.label(x + w / 2, y + 36 + k * 14, t, fs, False)
def fin(s, title, lines, a='sensei', b='kai'):
    x, y, w = s.begin(2); s.floor(x, y + 236, w)
    box(s, x + 14, y + 18, 232, 118, title, lines, fs=8.5)
    s.chara(x + 62, y + 236, a, 'smile' if a == 'sensei' else 'happy', 'point' if a == 'sensei' else 'stand', scale=.7)
    s.chara(x + 204, y + 236, b, 'happy', 'stand', scale=.7, flip=True); s.end(2)

# ---- 20 : tout dans une seule zone
s = Strip("mg20", "tout dans eu-west-3a", "Chapitre 20")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.rack(x + 20, y + 110, 40, 126); s.rack(x + 66, y + 110, 40, 126); s.rack(x + 112, y + 110, 40, 126)
s.label(x + 86, y + 100, "zone A : api, base, cache", 9)
s.chara(x + 206, y + 236, 'kai', 'smile', 'up', scale=.72)
s.bubble(x + 120, y + 14, 132, ["Tout au même", "endroit, c'est", "plus simple."], fs=10)
s.end(0)
x, y, w = s.begin(1); s.night(x, y, w, s.ph); s.floor(x, y + 236, w)
s.rack(x + 20, y + 110, 40, 126, alarm=True); s.rack(x + 66, y + 110, 40, 126, alarm=True); s.rack(x + 112, y + 110, 40, 126, alarm=True)
s.chara(x + 206, y + 236, 'mika', 'panic', 'head', scale=.72)
s.bubble(x + 10, y + 14, 180, ["Panne de la zone A :", "tout le service tombe."], fs=9.5, shout=True)
s.end(1)
fin(s, "concevoir pour la panne", ["trois zones, trois sous-réseaux", "base multi-AZ", "un NAT par zone", "tester la perte d'une zone"])
STRIPS.append(("c20", s.render("Une zone de disponibilité tombe un jour : on répartit sur trois zones, base en multi-AZ, et on teste la perte d'une zone au lieu de l'espérer.")))

# ---- 21 : la clé dans le dépôt
s = Strip("mg21", "la clé dans le dépôt", "Chapitre 21")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 36, 236, 92, ["# config.properties", "aws.key=AKIA3F…", "aws.secret=wJalr…", "$ git push   # dépôt public"], fs=9)
s.chara(x + 196, y + 236, 'kai', 'smile', 'chin', scale=.72, flip=True)
s.bubble(x + 8, y + 146, 150, ["Juste le temps", "de tester."], tail=(x + 176, y + 180), fs=10)
s.end(0)
x, y, w = s.begin(1); s.night(x, y, w, s.ph); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 30, 236, 96, ["+ 4 min : 40 instances", "  p4d.24xlarge (minage)", "facture estimée :", "  38 000 $ / jour"], fs=9)
s.chara(x + 178, y + 236, 'kai', 'panic', 'head', scale=.72)
s.sfx(x + 70, y + 196, "38 k$", 22, -8); s.end(1)
fin(s, "zéro clé statique", ["rôles pour les charges", "OIDC pour la CI", "SSO pour les humains", "gitleaks avant chaque push"], b='mika')
STRIPS.append(("c21", s.render("Une clé d'accès poussée sur un dépôt public est exploitée en quelques minutes : aucune clé statique, des rôles pour les charges, OIDC pour la CI, SSO pour les humains.")))

# ---- 22 : ce n'est pas AWS avec un autre logo
s = Strip("mg22", "pas AWS avec un autre logo", "Chapitre 22")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 36, 236, 92, ["gcloud compute firewall-rules", "  create allow-ssh", "  --source-ranges 0.0.0.0/0", "# « comme un SG AWS »"], fs=8.5)
s.chara(x + 196, y + 236, 'kai', 'smile', 'chin', scale=.72, flip=True)
s.bubble(x + 8, y + 146, 150, ["Une règle pour", "ma région, pareil", "qu'un SG."], tail=(x + 176, y + 180), fs=10)
s.end(0)
x, y, w = s.begin(1); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.bubble(x + 10, y + 16, 240, ["VPC GCP global : ta règle", "ouvre SSH partout."], fs=9.5, shout=True)
s.chara(x + 70, y + 236, 'mika', 'angry', 'hips', scale=.72); s.chara(x + 196, y + 236, 'kai', 'shock', 'head', scale=.72, flip=True)
s.end(1)
fin(s, "apprendre les différences", ["identité : Entra ID, projets GCP", "réseau : portée et règles", "facturation et quotas", "même Terraform, autres modèles"])
STRIPS.append(("c22", s.render("Les services se ressemblent, les modèles diffèrent : sur GCP le VPC est global, sur Azure l'identité passe par Entra ID ; on apprend ce qui change avant de copier ses réflexes AWS.")))

# ---- 23 : la facture du lundi
s = Strip("mg23", "la facture du lundi", "Chapitre 23")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 36, 236, 84, ["vendredi 17 h :", "  instance GPU de test", "  « je l'éteins lundi »"], fs=9)
s.chara(x + 66, y + 236, 'kai', 'happy', 'up', scale=.72)
s.bubble(x + 118, y + 138, 134, ["Bon", "week-end !"], tail=(x + 96, y + 168), fs=11)
s.end(0)
x, y, w = s.begin(1); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 30, 236, 96, ["lundi : facture du mois", "  GPU 62 h      2 900 €", "  NAT + transfert 1 400 €", "  logs sans rétention 600 €"], fs=9)
s.chara(x + 178, y + 236, 'mika', 'shock', 'head', scale=.72)
s.sfx(x + 70, y + 196, "4 900 €", 20, -8); s.end(1)
fin(s, "voir, puis optimiser", ["tags obligatoires, par équipe", "budgets avec alertes", "arrêt automatique le soir", "coût par requête suivi"], b='mika')
STRIPS.append(("c23", s.render("Le cloud facture ce qu'on oublie : tags obligatoires, budgets avec alertes, arrêt automatique des environnements hors production, et un coût par unité suivi chaque mois.")))

# ---- 24 : deux clouds, deux fois plus de pannes
s = Strip("mg24", "deux clouds, deux fois plus", "Chapitre 24")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.chara(x + 70, y + 236, 'sensei', 'neutral', 'stand', scale=.72)
s.bubble(x + 106, y + 14, 148, ["La direction veut", "AWS et Azure en", "actif-actif."], fs=10)
s.chara(x + 196, y + 236, 'kai', 'smile', 'up', scale=.72, flip=True); s.end(0)
x, y, w = s.begin(1); s.night(x, y, w, s.ph); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 30, 236, 96, ["6 mois plus tard :", "  deux IAM, deux réseaux", "  deux équipes d'astreinte", "  la base ne se réplique pas"], fs=9)
s.chara(x + 178, y + 236, 'kai', 'panic', 'head', scale=.72)
s.sfx(x + 70, y + 196, "×2", 26, -8); s.end(1)
fin(s, "portable, pas doublé", ["conteneurs, PostgreSQL, Terraform", "OpenTelemetry, Keycloak", "plan de réversibilité écrit", "multi-cloud seulement si exigé"])
STRIPS.append(("c24", s.render("Le multi-cloud actif-actif double l'identité, le réseau et l'astreinte : on vise des briques portables et un plan de réversibilité écrit, et on ne double que sur exigence réelle.")))

CSS = """
/* ============ Planches manga ============ */
.fig.manga svg{min-width:640px;border-radius:6px}
.fig.manga svg text{font-family:"Atkinson Hyperlegible",system-ui,sans-serif}
.fig.manga figcaption::before{content:"Manga — ";font-weight:700;color:var(--ink)}
:root[data-theme="dark"] .fig.manga svg{opacity:.94}
</style>"""
if 'Planches manga' not in S: S = S.replace('</style>', CSS, 1)
for cid, svg in STRIPS:
    a = S.index(f'id="{cid}"'); b = S.index('<div class="bref">', a); e = S.index('</div>', b) + 6
    S = S[:e] + '\n' + svg + S[e:]
p.write_text(S); print('planches :', S.count('class="fig manga"'))
