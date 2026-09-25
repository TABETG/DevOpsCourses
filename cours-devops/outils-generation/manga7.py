"""Planches manga du niveau 5 (chapitres 25 à 31), gabarit en trois cases : la situation, la conséquence, la bonne pratique.
Usage : python3 manga7.py <page niveau 5>"""
import sys, re, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from manga_engine import Strip, INK
p = pathlib.Path(sys.argv[1]); S = p.read_text()
S = re.sub(r'\n?<figure class="fig manga">.*?</figure>\n?', '\n', S, flags=re.S)

def box(s, x, y, w, h, title, lines=(), fs=8.5):
    s.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
    s.label(x + w / 2, y + 17, title, 10)
    for k, t in enumerate(lines): s.label(x + w / 2, y + 36 + k * 14, t, fs, False)

def strip3(sid, titre, chap, p0, p1, fin_titre, fin_lignes, legende):
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

STRIPS = [
 ("c25", strip3("mg25", "supprimer le Pod ne guérit rien", "Chapitre 25",
   dict(term=["api-7d9f  CrashLoopBackOff", "$ kubectl delete pod api-7d9f", "pod deleted"], bulle=["Je le supprime,", "il redémarre", "tout propre."]),
   dict(term=["api-5c1a  CrashLoopBackOff", "api-9e2b  CrashLoopBackOff", "# même image, même config"], who='kai', sfx="encore"),
   "observer avant d'agir", ["kubectl describe : événements", "kubectl logs --previous", "puis Service → Endpoints → Pod", "corriger la cause, pas le Pod"],
   "Supprimer un Pod en échec le recrée à l'identique : on lit d'abord describe et logs --previous, on corrige la cause, et seulement ensuite on redéploie.")),
 ("c26", strip3("mg26", "la liveness qui tue tout", "Chapitre 26",
   dict(term=["livenessProbe:", "  httpGet: /health", "  # /health appelle la base"], bulle=["Si la base ne", "répond pas, on", "redémarre : logique."]),
   dict(term=["base lente 30 s", "8/8 Pods : Liveness failed", "restart, restart, restart…", "service : 0 Pod prêt"], sfx="×8"),
   "liveness ≠ readiness", ["liveness : le processus vit", "readiness : dépendances prêtes", "startup : laisser démarrer la JVM", "jamais la base dans la liveness"],
   "Une liveness qui dépend de la base redémarre tous les Pods au premier ralentissement : la liveness vérifie le processus, la readiness vérifie les dépendances.")),
 ("c27", strip3("mg27", "la base dans un Deployment", "Chapitre 27",
   dict(term=["kind: Deployment", "  image: postgres:16", "  volumes: emptyDir: {}"], bulle=["Un Pod postgres,", "comme les autres,", "ça ira."]),
   dict(term=["nœud 2 drainé", "postgres replanifié", "sur le nœud 3", "base vide"], sfx="vide !"),
   "une base a une identité", ["StatefulSet + volume par réplica", "ou opérateur CloudNativePG", "sauvegardes et bascule gérées", "ou service managé (RDS)"],
   "Un Deployment traite les Pods comme interchangeables : une base a besoin d'une identité et d'un volume stables, donc d'un StatefulSet piloté par un opérateur, ou d'un service managé.")),
 ("c28", strip3("mg28", "l'upgrade à l'aveugle", "Chapitre 28",
   dict(term=["$ helm upgrade api ./chart", "  -f values-prod.yaml", "# nouvelle version du chart"], bulle=["Nouvelle version", "du chart, on", "met à jour."]),
   dict(term=["replicaCount: 3 → 1 (défaut)", "resources: supprimées", "Release \"api\" upgraded"], sfx="1 Pod"),
   "voir avant d'appliquer", ["helm diff upgrade avant tout", "values.schema.json validé", "helm upgrade --atomic", "rollback testé : helm rollback"],
   "Une nouvelle version de chart change des valeurs par défaut sans prévenir : helm diff avant d'appliquer, un schéma de values, et --atomic pour revenir seul en arrière.")),
 ("c29", strip3("mg29", "base64 n'est pas du chiffrement", "Chapitre 29",
   dict(term=["kind: Secret", "data:", "  password: Y3Jpc2lzMjAyNg=="], bulle=["C'est encodé,", "donc ça peut aller", "dans le dépôt."]),
   dict(term=["$ echo Y3Jpc2lzMjAyNg== |", "  base64 -d", "crisis2026"], rack=False, nuit=False, who='mika', expr='angry', pose='hips', sfx="lisible"),
   "rien de secret dans Git", ["External Secrets → Vault", "ou SealedSecrets / SOPS", "le dépôt ne contient", "que des références"],
   "Un Secret Kubernetes est seulement encodé : dans un dépôt GitOps, on ne met que des références (External Secrets vers Vault) ou des valeurs chiffrées (SealedSecrets, SOPS).")),
 ("c30", strip3("mg30", "un mesh pour cinq services", "Chapitre 30",
   dict(term=["istioctl install", "  --set profile=demo", "# pour 5 microservices"], bulle=["Tout le monde a", "un mesh, il nous", "en faut un."]),
   dict(term=["+40 ms de latence p99", "+60 Mo par Pod (sidecar)", "3 jours sur un mTLS cassé"], who='kai', sfx="+40 ms"),
   "un mesh se mérite", ["dizaines de services", "mTLS obligatoire partout", "canary pondéré, autorisation L7", "sinon : NetworkPolicy + TLS"],
   "Un service mesh apporte mTLS, routage et métriques, au prix d'un composant de plus à exploiter : il se justifie à l'échelle, pas pour cinq services.")),
 ("c31", strip3("mg31", "l'autoscaler qui ne voit rien", "Chapitre 31",
   dict(term=["kind: HorizontalPodAutoscaler", "  targetCPU: 70 %", "# Deployment sans requests"], bulle=["L'HPA ajoutera", "des Pods si ça", "chauffe."]),
   dict(term=["$ kubectl get hpa", "TARGETS  <unknown>/70%", "REPLICAS 2   # pic de charge"], sfx="?"),
   "requests d'abord", ["requests CPU et mémoire posées", "HPA sur une métrique réelle", "pas de limite CPU (throttling)", "tester la montée avec k6"],
   "Sans requests, l'autoscaler ne peut pas calculer un pourcentage d'utilisation et ne fait rien : requests obligatoires, puis un test de charge pour vérifier la montée.")),
]

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
