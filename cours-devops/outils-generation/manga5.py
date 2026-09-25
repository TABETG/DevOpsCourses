"""Planches manga du niveau 3 (chapitres 16 à 19). Usage : python3 manga5.py <page niveau 3>"""
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

# ---- 16 : deux apply, un state
s = Strip("mg16", "deux apply, un state", "Chapitre 16")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.desk(x + 8, y + 190, 110, laptop=True, screen_lines=["terraform", "apply", "state local"])
s.chara(x + 60, y + 236, 'kai', 'smile', 'up', scale=.75)
s.desk(x + 138, y + 190, 110, laptop=True, screen_lines=["terraform", "apply", "state local"])
s.chara(x + 196, y + 236, 'mika', 'smile', 'stand', scale=.75, flip=True)
s.sfx(x + 130, y + 60, "à 17 h 02", 16, -6); s.end(0)
x, y, w = s.begin(1); s.night(x, y, w, s.ph); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 30, 236, 100, ["Plan: 0 to add,", "  14 to destroy.", "# le state de Kai", "# ignore les ressources de Mika"], fs=9)
s.rack(x + 22, y + 142, 44, 94, alarm=True)
s.chara(x + 178, y + 236, 'kai', 'panic', 'head', scale=.72)
s.sfx(x + 104, y + 188, "14 !", 24, -8); s.end(1)
x, y, w = s.begin(2); s.floor(x, y + 236, w)
box(s, x + 14, y + 18, 232, 118, "un state, verrouillé", ["backend S3 + verrou DynamoDB", "plan relu dans la MR", "apply par la CI seulement", "state par environnement"], fs=8.5)
s.chara(x + 62, y + 236, 'sensei', 'neutral', 'point', scale=.7); s.chara(x + 204, y + 236, 'mika', 'happy', 'stand', scale=.7, flip=True)
s.end(2)
STRIPS.append(("c16", s.render("Un state local sur deux postes, c'est deux vérités : le state vit dans un backend distant verrouillé, le plan se relit en MR, et seule la CI applique.")))

# ---- 17 : changed=12, encore
s = Strip("mg17", "changed=12, encore", "Chapitre 17")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 36, 236, 104, ["- name: installer nginx", "  shell: apt-get install -y nginx", "- name: config", "  shell: echo '…' >> nginx.conf"], fs=8.5)
s.chara(x + 196, y + 236, 'kai', 'smile', 'chin', scale=.72, flip=True)
s.bubble(x + 8, y + 150, 150, ["Du shell, c'est", "plus rapide", "à écrire."], tail=(x + 176, y + 184), fs=10)
s.end(0)
x, y, w = s.begin(1); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 30, 236, 96, ["2e exécution :", "PLAY RECAP", "web1 : ok=12 changed=12", "nginx.conf : ligne dupliquée ×2"], fs=9)
s.chara(x + 178, y + 236, 'mika', 'angry', 'hips', scale=.72)
s.bubble(x + 10, y + 140, 128, ["Rien n'a changé", "et tout a", "« changé » ?"], fs=10, shout=True)
s.end(1)
x, y, w = s.begin(2); s.floor(x, y + 236, w)
box(s, x + 14, y + 18, 232, 118, "idempotent", ["apt: name=nginx state=present", "template: nginx.conf.j2", "2e passage : changed=0", "Molecule le vérifie en CI"], fs=8.5)
s.chara(x + 62, y + 236, 'sensei', 'smile', 'point', scale=.7); s.chara(x + 204, y + 236, 'kai', 'happy', 'up', scale=.7, flip=True)
s.end(2)
STRIPS.append(("c17", s.render("Un playbook en shell n'est pas idempotent : les modules décrivent l'état voulu, le second passage doit afficher changed=0, et Molecule le prouve à chaque MR.")))

# ---- 18 : le serveur flocon de neige
s = Strip("mg18", "le serveur flocon de neige", "Chapitre 18")
x, y, w = s.begin(0); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.rack(x + 26, y + 96, 56, 140)
s.label(x + 54, y + 88, "srv-prod-07", 9)
s.chara(x + 176, y + 236, 'kai', 'smile', 'stand', scale=.8)
s.bubble(x + 96, y + 14, 158, ["Trois ans de correctifs", "à la main, il n'a", "jamais planté."], fs=10)
s.end(0)
x, y, w = s.begin(1); s.night(x, y, w, s.ph); s.floor(x, y + 236, w)
s.rack(x + 26, y + 110, 56, 126, alarm=True)
s.bubble(x + 96, y + 18, 158, ["Disque mort.", "Qui sait le", "reconstruire ?"], fs=10.5, shout=True)
s.chara(x + 186, y + 236, 'mika', 'panic', 'head', scale=.72)
s.sfx(x + 120, y + 190, "…", 30, 0); s.end(1)
x, y, w = s.begin(2); s.floor(x, y + 236, w)
box(s, x + 14, y + 18, 232, 118, "remplacer, pas réparer", ["image dorée Packer, datée", "tests Goss, scan", "Terraform recrée", "aucun SSH en production"], fs=8.5)
s.chara(x + 62, y + 236, 'sensei', 'neutral', 'point', scale=.7); s.chara(x + 204, y + 236, 'mika', 'happy', 'stand', scale=.7, flip=True)
s.end(2)
STRIPS.append(("c18", s.render("Un serveur modifié à la main pendant des années ne se reconstruit plus : on construit une image dorée avec Packer, on la teste, et on remplace les machines au lieu de les réparer.")))

# ---- 19 : le correctif de 2 h du matin
s = Strip("mg19", "le correctif de 2 h du matin", "Chapitre 19")
x, y, w = s.begin(0); s.night(x, y, w, s.ph); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 30, 236, 84, ["$ kubectl edit deploy api", "  replicas: 2  →  8", "deployment edited"], fs=9)
s.chara(x + 66, y + 236, 'kai', 'smile', 'up', scale=.72)
s.bubble(x + 118, y + 130, 134, ["Réglé, je", "ferai la MR", "demain."], tail=(x + 96, y + 160), fs=10.5)
s.end(0)
x, y, w = s.begin(1); s.tone(x, y, w, 60, 'dots'); s.floor(x, y + 236, w)
s.terminal(x + 12, y + 30, 236, 84, ["argocd : OutOfSync", "selfHeal → replicas: 2", "02 h 07 : latence ×10"], fs=9)
s.chara(x + 178, y + 236, 'kai', 'shock', 'head', scale=.72)
s.bubble(x + 10, y + 128, 140, ["Git a gagné,", "ton correctif", "a disparu."], fs=10, shout=True)
s.end(1)
x, y, w = s.begin(2); s.floor(x, y + 236, w)
box(s, x + 14, y + 18, 232, 118, "Git est la seule entrée", ["le correctif est une MR", "même à 2 h : revue express", "ArgoCD applique", "dérive alertée, pas tolérée"], fs=8.5)
s.chara(x + 62, y + 236, 'sensei', 'smile', 'point', scale=.7); s.chara(x + 204, y + 236, 'kai', 'smile', 'stand', scale=.7, flip=True)
s.end(2)
STRIPS.append(("c19", s.render("En GitOps, une modification faite à la main est effacée à la prochaine synchronisation : même en urgence, le correctif passe par une MR, et la dérive déclenche une alerte.")))

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
