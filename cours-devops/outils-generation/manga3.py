"""Planches manga du niveau 1 (une par chapitre 7 à 10). Usage : python3 manga3.py <page niveau 1>"""
import sys, re, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from manga_engine import Strip, INK
p = pathlib.Path(sys.argv[1]); S = p.read_text()
S = re.sub(r'<figure class="fig manga">.*?</figure>\n?', '', S, flags=re.S)   # regénération idempotente
STRIPS = []
def box(s, x, y, w, h, title, lines=(), dashed=False, fs=9):
    s.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fff" stroke="{INK}" stroke-width="2.5"{" stroke-dasharray=\"8 5\"" if dashed else ""}/>')
    s.label(x+w/2, y+16, title, 10)
    for k, t in enumerate(lines): s.label(x+w/2, y+34+k*13, t, fs, False)

# ---- 7 : VM contre conteneur
s = Strip("mg7", "une petite VM, vraiment ?", "Chapitre 7")
x, y, w = s.begin(0); s.tone(x, y, w, 80, 'dots'); s.floor(x, y+236, w)
s.desk(x+10, y+190, 120, laptop=True, screen_lines=["docker run", "ubuntu bash", "root@a1b2:/#"])
s.chara(x+66, y+236, 'kai', 'happy', 'up', scale=.9)
s.bubble(x+120, y+14, 132, ["Un shell root, un", "Ubuntu entier en", "0,3 seconde : c'est", "une mini VM !"], tail=(x+96, y+120), fs=10)
s.sfx(x+200, y+200, "0,3 s", 20, -12); s.end(0)
x, y, w = s.begin(1); s.floor(x, y+236, w)
box(s, x+12, y+70, 108, 122, "VM", ["noyau invité", "systemd, sshd", "disque virtuel", "démarre en 30 s"])
box(s, x+140, y+70, 108, 122, "conteneur", ["processus", "namespaces", "cgroups", "couches"], dashed=True)
s.raw(f'<path d="M{x+12},{y+206} L{x+248},{y+206}" stroke="{INK}" stroke-width="3"/>'); s.label(x+130, y+224, "un seul noyau Linux, partagé", 9.5)
s.bubble(x+6, y+4, 248, ["Même noyau. Ton « Ubuntu », c'est des", "fichiers et un processus isolé, pas", "une machine.  — Sensei"], fs=9.5)
s.end(1)
x, y, w = s.begin(2); s.night(x, y, w, s.ph); s.floor(x, y+236, w)
s.rack(x+20, y+96, 50, 140, alarm=True); s.chara(x+150, y+236, 'mika', 'angry', 'hips', scale=.9)
s.bubble(x+80, y+8, 172, ["Le conteneur A a", "fait tomber le noyau…", "et B, C, D avec lui."], fs=10.5, shout=True)
s.caption(x+6, y+246, 150, "isolation ≠ virtualisation")
s.end(2)
STRIPS.append(("c7", s.render("Un conteneur démarre en 0,3 s parce qu'il n'est qu'un processus isolé sur le noyau de l'hôte ; c'est aussi pourquoi une faille noyau touche tous les voisins.")))

# ---- 8 : les couches et le secret
s = Strip("mg8", "le secret dans la couche", "Chapitre 8")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y+236, w)
s.terminal(x+12, y+50, 236, 120, ["FROM ubuntu", "COPY .aws/credentials /root/.aws/", "RUN aws s3 sync … ", "RUN rm -rf /root/.aws", "# supprimé, donc sûr ?"], fs=8.5)
s.chara(x+206, y+236, 'kai', 'smile', 'chin', scale=.7, flip=True)
s.bubble(x+6, y+176, 150, ["Je l'efface à la fin,", "personne ne le verra."], tail=(x+190, y+206), fs=10)
s.end(0)
x, y, w = s.begin(1)
for k, (t, dark) in enumerate([("4  RUN rm -rf /root/.aws   (whiteout)", False), ("3  RUN aws s3 sync", False), ("2  COPY credentials  ← les octets sont ICI", True), ("1  FROM ubuntu", False)]):
    yy = y+50+k*44
    s.raw(f'<rect x="{x+16}" y="{yy}" width="{w-32}" height="36" rx="5" fill="{"url(#mg8_dark)" if dark else "#fff"}" stroke="{INK}" stroke-width="2.5"/>')
    s.raw(f'<text x="{x+26}" y="{yy+23}" font-size="9.5" font-weight="700" style="fill:{"#fff" if dark else INK}">{t}</text>')
s.label(x+w/2, y+40, "image = pile de couches immuables", 10)
s.sfx(x+w-60, y+240, "docker save", 11, 0); s.end(1)
x, y, w = s.begin(2); s.floor(x, y+236, w)
s.chara(x+60, y+236, 'sensei', 'neutral', 'point', scale=.85); s.chara(x+206, y+236, 'kai', 'shock', 'head', scale=.85, flip=True)
s.bubble(x+6, y+6, 248, ["Une couche ne s'efface pas, elle se", "recouvre. Multi-étapes ou", "--mount=type=secret : jamais COPY."], fs=10)
s.focus(x+206, y+150, 40, 90, 20, 1); s.end(2)
STRIPS.append(("c8", s.render("Supprimer un fichier dans une couche suivante ajoute un « whiteout » ; les octets restent dans la couche précédente et sortent avec docker save. Le secret ne doit jamais entrer dans une couche.")))

# ---- 9 : depends_on
s = Strip("mg9", "depends_on ne suffit pas", "Chapitre 9")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots')
s.terminal(x+12, y+44, 236, 118, ["services:", "  api:", "    depends_on: [db]", "  db:", "    image: postgres:16", "$ docker compose up", "api | Connection refused"], fs=8.5)
s.chara(x+50, y+236, 'kai', 'panic', 'head', scale=.45); s.sfx(x+180, y+215, "refused", 16, -8); s.end(0)
x, y, w = s.begin(1); s.floor(x, y+236, w)
s.robot(x+70, y+200, 'java', 'neutral', "api : prêt en 2 s"); s.robot(x+190, y+200, 'sh', 'sleep', "postgres : prêt en 6 s")
s.raw(f'<path d="M{x+100},{y+120} L{x+160},{y+120}" stroke="{INK}" stroke-width="3" marker-end="url(#mg9_arr)"/><defs><marker id="mg9_arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="{INK}"/></marker></defs>')
s.bubble(x+6, y+6, 248, ["depends_on = « démarré », pas", "« prêt ». La base initialise", "encore son dossier de données."], fs=10)
s.end(1)
x, y, w = s.begin(2); s.tone(x, y, w, 60, 'dots')
s.terminal(x+12, y+44, 236, 112, ["  db:", "    healthcheck:", "      test: [\"CMD\", \"pg_isready\"]", "      interval: 2s", "  api:", "    depends_on:", "      db: { condition: service_healthy }"], fs=8)
s.chara(x+34, y+236, 'mika', 'happy', 'stand', scale=.45); s.chara(x+226, y+236, 'kai', 'happy', 'up', scale=.45, flip=True)
s.label(x+130, y+200, "et l'API sait", 9); s.label(x+130, y+214, "se reconnecter seule", 9)
s.end(2)
STRIPS.append(("c9", s.render("depends_on attend le démarrage du conteneur, pas la disponibilité du service : il faut un healthcheck et condition: service_healthy, et une application qui réessaie.")))

# ---- 10 : le tag latest
s = Strip("mg10", "latest, deux fois", "Chapitre 10")
x, y, w = s.begin(0); s.floor(x, y+236, w)
s.rack(x+20, y+96, 46, 140); s.rack(x+76, y+96, 46, 140)
s.label(x+43, y+86, "prod-1", 9); s.label(x+99, y+86, "prod-2", 9)
s.label(x+43, y+250, "latest, lundi", 8); s.label(x+99, y+250, "latest, jeudi", 8)
s.chara(x+196, y+236, 'mika', 'shock', 'head', scale=.85)
s.bubble(x+120, y+6, 134, ["Même tag, deux", "images différentes !", "Laquelle a le bug ?"], fs=10, shout=True)
s.end(0)
x, y, w = s.begin(1); s.tone(x, y, w, 60, 'dots')
s.terminal(x+12, y+44, 236, 120, ["$ docker inspect api:latest", "  RepoDigests: sha256:9c4d…", "$ docker inspect api:latest   # prod-2", "  RepoDigests: sha256:71ab…"], fs=8.5)
s.chara(x+60, y+236, 'sensei', 'neutral', 'point', scale=.6); s.bubble(x+96, y+172, 156, ["Un tag est un alias mobile.", "Le digest, lui, ne ment pas."], fs=9.5)
s.end(1)
x, y, w = s.begin(2); s.floor(x, y+236, w)
box(s, x+14, y+40, 232, 96, "déployer par digest", ["harbor…/api@sha256:9c4d…", "signé (cosign), SBOM attaché,", "scanné, vérifié à l'admission"], fs=8.5)
s.chara(x+60, y+236, 'kai', 'happy', 'stand', scale=.7); s.chara(x+200, y+236, 'mika', 'happy', 'stand', scale=.7, flip=True)
s.sfx(x+130, y+165, "immuable", 18, 0); s.end(2)
STRIPS.append(("c10", s.render("latest est mutable : deux serveurs peuvent exécuter deux images différentes sous le même nom. On déploie par digest, on signe le digest, on scanne l'image.")))

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
