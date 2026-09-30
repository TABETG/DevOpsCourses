"""Planches manga du niveau 2 (chapitres 11 à 15). Usage : python3 manga4.py <page niveau 2>"""
import sys, re, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from manga_engine import Strip, INK
p = pathlib.Path(sys.argv[1]); S = p.read_text()
S = re.sub(r'\n?<figure class="fig manga">.*?</figure>\n?', '\n', S, flags=re.S)   # regénération idempotente
STRIPS = []
def box(s, x, y, w, h, title, lines=(), dashed=False, fs=9):
    s.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fff" stroke="{INK}" stroke-width="2.5"{" stroke-dasharray=\"8 5\"" if dashed else ""}/>')
    s.label(x + w / 2, y + 17, title, 10)
    for k, t in enumerate(lines): s.label(x + w / 2, y + 36 + k * 14, t, fs, False)

# ---- 11 : ça marche sur ma machine
s = Strip("mg11", "ça marche sur ma machine", "Chapitre 11")
x, y, w = s.begin(0); s.tone(x, y, w, 80, 'dots'); s.floor(x, y + 236, w)
s.desk(x + 10, y + 190, 120, laptop=True, screen_lines=["mvn test", "BUILD SUCCESS", "git push"])
s.chara(x + 66, y + 236, 'kai', 'happy', 'up', scale=.9)
s.bubble(x + 122, y + 16, 130, ["Tout est vert", "chez moi,", "je pousse !"], tail=(x + 96, y + 118), fs=10.5)
s.sfx(x + 196, y + 206, "push", 20, -10); s.end(0)
x, y, w = s.begin(1); s.tone(x, y, w, 60, 'dots')
s.terminal(x + 12, y + 44, 236, 104, ["$ mvn -B verify   # CI", "[ERROR] config-dev.yml", "        not found", "BUILD FAILURE"], fs=9)
s.chara(x + 196, y + 236, 'mika', 'shock', 'head', scale=.7, flip=True)
s.bubble(x + 8, y + 158, 150, ["Le fichier n'était", "que sur ton poste…"], tail=(x + 176, y + 190), fs=10)
s.end(1)
x, y, w = s.begin(2); s.floor(x, y + 236, w)
box(s, x + 14, y + 22, 232, 104, "le pipeline fait foi", ["build dans un conteneur", "rien hors de Git", "une image, partout"])
s.chara(x + 62, y + 236, 'sensei', 'smile', 'point', scale=.72); s.chara(x + 204, y + 236, 'kai', 'smile', 'stand', scale=.72, flip=True)
s.caption(x + 6, y + 246, 170, "build once, deploy many"); s.end(2)
STRIPS.append(("c11", s.render("Ce qui n'est pas dans Git ni dans le pipeline n'existe pas : on construit une seule fois, dans un conteneur, et c'est cette image qui part partout.")))

# ---- 12 : les clés du royaume
s = Strip("mg12", "les clés du royaume", "Chapitre 12")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 40, 236, 100, ["[[runners]]", "  volumes = [", "   \"/var/run/docker.sock\"]", "# pratique : docker build"], fs=9)
s.chara(x + 196, y + 236, 'kai', 'smile', 'chin', scale=.72, flip=True)
s.bubble(x + 8, y + 150, 150, ["Comme ça, tous les", "jobs font docker build."], tail=(x + 176, y + 184), fs=10)
s.end(0)
x, y, w = s.begin(1); s.night(x, y, w, s.ph); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 30, 236, 92, ["job: docker run -v /:/h", "     alpine chroot /h", "root@runner:/#  _"], fs=9)
s.rack(x + 22, y + 132, 44, 104, alarm=True)
s.chara(x + 176, y + 236, 'mika', 'shock', 'head', scale=.75)
s.sfx(x + 96, y + 176, "root !", 22, -8); s.end(1)
x, y, w = s.begin(2); s.floor(x, y + 236, w)
box(s, x + 14, y + 22, 232, 104, "construire sans démon", ["Kaniko / BuildKit rootless", "runner éphémère par job", "jetons OIDC, zéro secret"])
s.chara(x + 62, y + 236, 'sensei', 'neutral', 'point', scale=.72); s.chara(x + 204, y + 236, 'mika', 'happy', 'stand', scale=.72, flip=True)
s.end(2)
STRIPS.append(("c12", s.render("Monter le socket Docker dans un runner donne à chaque job le contrôle de l'hôte : on construit sans démon (Kaniko, BuildKit rootless) sur des runners éphémères.")))

# ---- 13 : vert sur H2, rouge en prod
s = Strip("mg13", "vert sur H2, rouge en prod", "Chapitre 13")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 40, 236, 90, ["@DataJpaTest   # base H2", "Tests run: 42, Failures: 0", "couverture : 87 %"], fs=9)
s.chara(x + 66, y + 236, 'kai', 'happy', 'up', scale=.72)
s.bubble(x + 118, y + 146, 134, ["87 % de", "couverture,", "on livre !"], tail=(x + 96, y + 176), fs=10.5)
s.end(0)
x, y, w = s.begin(1); s.night(x, y, w, s.ph); s.floor(x, y + 236, w)
s.rack(x + 22, y + 118, 44, 118, alarm=True)
s.bubble(x + 76, y + 14, 178, ["En prod PostgreSQL :", "operator does not exist:", "jsonb = text"], fs=10, shout=True)
s.chara(x + 178, y + 236, 'mika', 'angry', 'hips', scale=.72)
s.end(1)
x, y, w = s.begin(2); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 34, 236, 92, ["@Container static", " PostgreSQLContainer pg =", "  new …(\"postgres:16\");"], fs=9)
s.chara(x + 62, y + 236, 'sensei', 'smile', 'point', scale=.7); s.label(x + 176, y + 170, "le vrai moteur", 10); s.label(x + 176, y + 186, "en trois secondes", 10)
s.end(2)
STRIPS.append(("c13", s.render("Un test vert sur H2 ne prouve rien pour PostgreSQL : Testcontainers démarre le vrai moteur en quelques secondes, dans le même pipeline.")))

# ---- 14 : la mise à jour du vendredi
s = Strip("mg14", "la mise à jour du vendredi", "Chapitre 14")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 40, 236, 92, ["\"dependencies\": {", "  \"lodash\": \"^4.17.0\" }", "# pas de lockfile commité"], fs=9)
s.chara(x + 196, y + 236, 'kai', 'smile', 'chin', scale=.72, flip=True)
s.bubble(x + 8, y + 146, 150, ["Le ^ prend la", "dernière version,", "c'est bien, non ?"], tail=(x + 176, y + 180), fs=10)
s.end(0)
x, y, w = s.begin(1); s.night(x, y, w, s.ph); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 30, 236, 100, ["vendredi 18 h : npm install", "+ lodash 4.18.0 (auto)", "TypeError: _.merge…", "la prod ne démarre plus"], fs=9)
s.chara(x + 176, y + 236, 'mika', 'panic', 'head', scale=.72)
s.sfx(x + 70, y + 196, "^ !", 26, -8); s.end(1)
x, y, w = s.begin(2); s.floor(x, y + 236, w)
box(s, x + 14, y + 22, 232, 104, "reproductible", ["lockfile commité, npm ci", "Renovate : une MR testée", "versions épinglées"])
s.chara(x + 62, y + 236, 'kai', 'happy', 'stand', scale=.72); s.chara(x + 204, y + 236, 'mika', 'happy', 'stand', scale=.72, flip=True)
s.end(2)
STRIPS.append(("c14", s.render("Une plage de versions sans lockfile installe ce qui sort le jour du build : lockfile commité, installation par npm ci, et Renovate propose chaque mise à jour en MR testée.")))

# ---- 15 : le rollback impossible
s = Strip("mg15", "le rollback impossible", "Chapitre 15")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 40, 236, 92, ["V7__renommer.sql", "ALTER TABLE incident", " RENAME titre TO libelle;"], fs=9)
s.chara(x + 66, y + 236, 'kai', 'happy', 'up', scale=.72)
s.bubble(x + 118, y + 146, 134, ["v2 déployée,", "migration", "passée !"], tail=(x + 96, y + 176), fs=10.5)
s.end(0)
x, y, w = s.begin(1); s.night(x, y, w, s.ph); s.floor(x, y + 236, w)
s.rack(x + 22, y + 118, 44, 118, alarm=True)
s.terminal(x + 78, y + 24, 172, 78, ["rollback → v1 :", "column \"titre\"", "does not exist"], fs=9)
s.chara(x + 178, y + 236, 'mika', 'shock', 'head', scale=.72)
s.sfx(x + 110, y + 132, "bloqué", 18, -8); s.end(1)
x, y, w = s.begin(2); s.floor(x, y + 236, w)
box(s, x + 14, y + 14, 232, 118, "expand / contract", ["1. ajouter libelle", "2. écrire les deux colonnes", "3. lire libelle", "4. supprimer titre, plus tard"], fs=8.5)
s.chara(x + 62, y + 236, 'sensei', 'neutral', 'point', scale=.7); s.chara(x + 204, y + 236, 'kai', 'smile', 'stand', scale=.7, flip=True)
s.end(2)
STRIPS.append(("c15", s.render("Une migration destructive rend le retour arrière impossible : on la découpe en expand puis contract, chaque étape compatible avec la version précédente.")))

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
