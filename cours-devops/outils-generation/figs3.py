import re, pathlib, html as H

out = pathlib.Path('/mnt/user-data/outputs')
FIGS = []

def tw(t, fs, bold=False): return len(t) * fs * (0.66 if bold else 0.6)

def wrap(t, fs, maxw, bold=False):
    """coupe un texte en lignes qui tiennent dans maxw"""
    words = t.split(' '); lines = []; cur = ''
    for w in words:
        cand = (cur + ' ' + w).strip()
        if tw(cand, fs, bold) <= maxw or not cur: cur = cand
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

class Fig:
    def __init__(self, ident, w, h, label):
        self.id = ident; self.w = w; self.h = h; self.label = label; self.b = ''; self.m = f'ah_{ident}'
    def box(self, x, y, w, h, lines, cls='box', fs=12, bold=True, sub=None, rx=7):
        if isinstance(lines, str): lines = [lines]
        maxw = w - 10
        # ajuster : réduire la police jusqu'à 9, puis couper en lignes
        out = []
        for t in lines:
            f2 = fs
            while tw(t, f2, bold) > maxw and f2 > 9: f2 -= 1
            if tw(t, f2, bold) > maxw: out += [(l, f2) for l in wrap(t, f2, maxw, bold)]
            else: out.append((t, f2))
        subl = []
        if sub:
            f3 = 11
            while tw(sub, f3) > maxw and f3 > 8: f3 -= 1
            subl = [(l, f3) for l in (wrap(sub, f3, maxw) if tw(sub, f3) > maxw else [sub])]
        self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>'
        allines = [(t, f, True) for t, f in out] + [(t, f, False) for t, f in subl]
        tot = sum(f + 3 for _, f, _ in allines) - 3
        yy = y + h/2 - tot/2
        for t, f, main in allines:
            yy += f
            if main: self.b += f'<text x="{x+w/2}" y="{yy:.1f}" text-anchor="middle" font-size="{f}"{" font-weight=\"700\"" if bold else ""}>{H.escape(t)}</text>'
            else: self.b += f'<text x="{x+w/2}" y="{yy:.1f}" text-anchor="middle" class="lbl" font-size="{f}">{H.escape(t)}</text>'
            yy += 3
        return self
    def text(self, x, y, t, cls='lbl', anchor='middle', fs=11, bold=False, maxw=None):
        lines = wrap(t, fs, maxw, bold) if maxw and tw(t, fs, bold) > maxw else [t]
        for i, l in enumerate(lines):
            self.b += f'<text x="{x}" y="{y + i*(fs+3)}" text-anchor="{anchor}" class="{cls}" font-size="{fs}"{" font-weight=\"700\"" if bold else ""}>{H.escape(l)}</text>'
        return self
    def arrow(self, x1, y1, x2, y2, label=None, dashed=False, dx=0, dy=-6, head=True):
        self.b += f'<path d="M{x1},{y1} L{x2},{y2}" class="arrow{" dashed" if dashed else ""}"{f" marker-end=\"url(#{self.m})\"" if head else ""}/>'
        if label: self.b += f'<text x="{(x1+x2)/2+dx}" y="{(y1+y2)/2+dy}" text-anchor="middle" class="lbl" font-size="11">{H.escape(label)}</text>'
        return self
    def path(self, d, dashed=False, head=True):
        self.b += f'<path d="{d}" class="arrow{" dashed" if dashed else ""}"{f" marker-end=\"url(#{self.m})\"" if head else ""}/>'; return self
    def frame(self, x, y, w, h, label=None, cls='frame'):
        self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" class="{cls}"/>'
        if label: self.b += f'<text x="{x+8}" y="{y+15}" class="glab">{H.escape(label)}</text>'
        return self
    def raw(self, s): self.b += s; return self
    def render(self, caption):
        return (f'<figure class="fig"><svg viewBox="0 0 {self.w} {self.h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{H.escape(self.label)}">'
                f'<defs><marker id="{self.m}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="ahead"/></marker></defs>'
                f'{self.b}</svg><figcaption>{caption}</figcaption></figure>')

def add(level, section, fig, caption): FIGS.append((level, section, fig.render(caption)))

L0="devops-niveau-0-fondations.html"; L1="devops-niveau-1-conteneurs.html"; L2="devops-niveau-2-ci-cd.html"; L3="devops-niveau-3-infrastructure-as-code.html"
L4="devops-niveau-4-cloud.html"; L5="devops-niveau-5-kubernetes.html"; L6="devops-niveau-6-observabilite.html"; L7="devops-niveau-7-securite-devsecops.html"
L8="devops-niveau-8-sre-architecture.html"; L9="devops-niveau-9-expert-leadership.html"

# 2 — diagnostic
f = Fig("diag", 480, 175, "La méthode de diagnostic d'une machine Linux")
steps = [("uptime","charge ?"),("top","CPU ou attente ?"),("free","swap ?"),("df","disque, inodes ?"),("ss","le port écoute ?"),("journalctl","que dit le service ?")]
for i,(c,q) in enumerate(steps):
    x = 4 + i*79
    f.box(x, 16, 70, 40, c, 'soft', 12); f.text(x+35, 74, q, fs=10, maxw=74)
    if i < 5: f.arrow(x+70, 36, x+79, 36)
f.box(4, 112, 226, 50, ["symptôme utilisateur", "« c'est lent », « ça ne répond pas »"], 'amber', 11, bold=False)
f.box(250, 112, 226, 50, ["cause trouvée", "correction, puis post-mortem"], 'green', 11, bold=False)
f.arrow(230, 137, 250, 137)
add(L0, "2.6", f, "Six commandes, dans cet ordre, et une question par commande. On ne « regarde partout » pas : on descend du symptôme (charge) vers la cause (le service), et on s'arrête dès qu'une réponse explique le symptôme.")

# 4 — redirections
f = Fig("redir", 480, 215, "Entrées, sorties et redirections d'un processus")
f.box(180, 60, 120, 70, ["commande"], 'soft', 13, sub="un processus")
f.box(20, 72, 100, 46, ["clavier ou", "< fichier"], 'box', 11, bold=False); f.arrow(120, 95, 180, 95); f.text(150, 84, "0 : stdin", fs=10)
f.box(360, 30, 100, 44, ["écran ou", "> fichier"], 'green', 11, bold=False); f.arrow(300, 80, 360, 56); f.text(316, 60, "1 : stdout", fs=10)
f.box(360, 116, 100, 44, ["écran ou", "2> erreurs.log"], 'red', 11, bold=False); f.arrow(300, 110, 360, 134); f.text(316, 140, "2 : stderr", fs=10)
f.text(240, 178, "2>&1 : stderr rejoint stdout", fs=10); f.text(240, 194, "cmd1 | cmd2 : le stdout de l'un devient le stdin de l'autre", fs=10)
f.text(240, 210, "$? : code de retour (0 = succès)", fs=10)
add(L0, "4.1", f, "Trois flux numérotés : 0 entre, 1 et 2 sortent. Toute redirection ne fait que rebrancher ces flux ; un pipe branche la sortie d'un processus sur l'entrée du suivant. Séparer stdout et stderr, c'est ce qui rend un script utilisable en pipeline.")

# 6 — index
f = Fig("index", 480, 180, "Requête sans index et avec index")
f.frame(4, 8, 230, 164, "Sans index : Seq Scan")
for i in range(8): f.raw(f'<rect x="{16+i*26}" y="58" width="22" height="66" rx="3" class="amber"/>')
f.text(119, 44, "lit toutes les lignes (1 000 000)", fs=11); f.text(119, 150, "temps proportionnel à la table", fs=11)
f.frame(246, 8, 230, 164, "Avec index : Index Scan")
f.box(330, 36, 60, 24, "racine", 'soft', 11); f.box(280, 78, 60, 24, "< M", 'soft', 11); f.box(380, 78, 60, 24, "≥ M", 'soft', 11)
f.arrow(350, 60, 316, 78); f.arrow(370, 60, 404, 78)
f.raw('<rect x="399" y="112" width="22" height="26" rx="3" class="green"/>'); f.arrow(410, 102, 410, 112)
f.text(361, 155, "3 ou 4 lectures, temps en log(taille)", fs=11)
add(L0, "6.3", f, "EXPLAIN ANALYZE dit lequel des deux se produit. Un Seq Scan sur une table qui grossit est une bombe à retardement : rapide en développement, lent en production. L'index se paie à l'écriture ; on indexe ce qu'on filtre et ce qu'on joint.")

# 9 — Compose
f = Fig("compose", 480, 215, "Une pile Compose avec deux réseaux et des volumes")
f.text(70, 16, "Internet", 'glab'); f.arrow(70, 22, 70, 62); f.text(150, 40, ":443, seul port publié", fs=10)
f.frame(4, 48, 214, 96, None); f.text(12, 140, "réseau frontend", 'glab', anchor='start')
f.frame(140, 48, 336, 160, None); f.text(470, 204, "réseau backend", 'glab', anchor='end')
f.box(20, 62, 100, 44, "proxy", 'soft', 12, sub="nginx / Caddy"); f.box(160, 62, 90, 44, "web", 'box', 12, sub="React")
f.box(280, 62, 90, 44, "api", 'box', 12, sub="Spring Boot"); f.box(390, 62, 76, 44, "db", 'green', 12, sub="PostgreSQL")
f.box(280, 132, 90, 40, "redis", 'box', 12, sub="cache"); f.box(390, 132, 76, 40, "volume", 'amber', 11, sub="pgdata")
f.arrow(120, 84, 160, 84); f.arrow(250, 84, 280, 84); f.arrow(370, 84, 390, 84); f.arrow(325, 106, 325, 132); f.arrow(428, 106, 428, 132, head=False)
add(L1, "9.3", f, "Un seul point d'entrée publie un port ; le front ne voit pas la base (réseaux séparés) ; ce qui doit survivre est dans un volume nommé. depends_on avec condition service_healthy ordonne le démarrage, et l'application retente quand même.")

# 10 — registre
f = Fig("registry", 480, 175, "Build, push, pull : tags et digest")
f.box(10, 30, 96, 50, "docker build", 'box', 12, sub="CI"); f.box(192, 30, 96, 50, "registre", 'soft', 12, sub="Harbor, ECR"); f.box(374, 30, 96, 50, "cluster", 'green', 12, sub="pull")
f.arrow(106, 55, 192, 55); f.text(149, 46, "push", fs=10); f.arrow(288, 55, 374, 55); f.text(331, 46, "pull par digest", fs=10)
f.box(10, 112, 220, 50, ["tag api:1.7.0 : mutable", "peut être réécrit : jamais en prod"], 'amber', 11, bold=False)
f.box(250, 112, 220, 50, ["digest sha256:3f9c… : immuable", "identifie exactement ce qui tourne"], 'green', 11, bold=False)
f.arrow(240, 80, 130, 112, dashed=True, head=False); f.arrow(240, 80, 360, 112, dashed=True, head=False)
add(L1, "10.1", f, "Le tag est un nom, le digest est une empreinte du contenu. On construit une fois, on pousse un tag pour les humains et un digest pour les machines ; le déploiement référence le digest, vérifié à l'admission (chapitre 40).")

# 12 — runners
f = Fig("runner", 480, 195, "Serveur CI, runners et exécuteurs")
f.box(10, 66, 120, 60, "GitLab / GitHub", 'soft', 12, sub="jobs, artefacts")
f.box(210, 20, 120, 46, "runner A", 'box', 12, sub="docker executor"); f.box(210, 80, 120, 46, "runner B", 'box', 12, sub="kubernetes executor"); f.box(210, 140, 120, 40, "runner C", 'box', 12, sub="shell, à éviter")
f.arrow(130, 86, 210, 43); f.arrow(130, 96, 210, 103); f.arrow(130, 106, 210, 160); f.text(150, 144, "demande un job", fs=10)
f.box(370, 20, 100, 46, "conteneur", 'green', 11, sub="image du job"); f.box(370, 80, 100, 46, "Pod éphémère", 'green', 11, sub="par job")
f.arrow(330, 43, 370, 43); f.arrow(330, 103, 370, 103)
f.text(420, 152, "artefacts, cache, logs", fs=10); f.text(420, 166, "remontent au serveur", fs=10)
add(L2, "12.1", f, "Le serveur ne fait rien tourner : les runners viennent chercher des jobs et les exécutent dans un conteneur ou un Pod jetable. Un runner shell partagé exécute du code inconnu sur une machine durable : c'est la première faille des CI d'entreprise.")

# 13 — pyramide
f = Fig("pyramid", 480, 195, "La pyramide des tests et la barrière qualité")
f.raw('<polygon points="200,20 260,20 300,78 160,78" class="amber"/><polygon points="150,84 310,84 350,142 110,142" class="soft"/><polygon points="100,148 360,148 400,186 60,186" class="green"/>')
f.text(230, 54, "bout en bout", fs=11, bold=True, cls=''); f.text(230, 118, "intégration : Testcontainers", fs=11, bold=True, cls=''); f.text(230, 172, "unitaires : nombreux, rapides", fs=11, bold=True, cls='')
f.text(40, 40, "peu, lents", fs=10); f.text(40, 54, "minutes", fs=10); f.text(40, 110, "quelques", fs=10); f.text(40, 124, "secondes", fs=10); f.text(40, 165, "beaucoup", fs=10); f.text(40, 179, "millisecondes", fs=10)
f.box(396, 20, 80, 70, ["quality", "gate"], 'red', 12, sub="bloque la MR")
f.text(432, 112, "couverture du", fs=9); f.text(432, 124, "nouveau code", fs=9); f.text(432, 140, "0 bug critique", fs=9); f.text(432, 156, "mutation ≥ 60 %", fs=9)
add(L2, "13.1", f, "Beaucoup de tests rapides en bas, peu de tests lents en haut. La barrière qualité juge le code nouveau, pas l'historique, et bloque la merge request : c'est ce qui rend la pyramide obligatoire plutôt que souhaitable.")

# 14 — dépendances
f = Fig("deps", 480, 180, "Le circuit des dépendances")
f.box(10, 30, 96, 50, "développeur", 'box', 12, sub="pom.xml, package.json"); f.box(140, 30, 100, 50, "lockfile", 'soft', 12, sub="versions exactes"); f.box(290, 30, 96, 50, "proxy", 'amber', 12, sub="Nexus, Artifactory"); f.box(420, 30, 50, 50, ["dépôts", "publics"], 'box', 10)
f.arrow(106, 55, 140, 55); f.arrow(240, 55, 290, 55); f.text(265, 46, "npm ci", fs=10); f.arrow(386, 55, 420, 55)
f.box(140, 116, 100, 46, "Renovate", 'green', 12, sub="MR automatique"); f.arrow(190, 116, 190, 80); f.text(215, 100, "met à jour", fs=10, anchor='start')
f.box(290, 116, 180, 46, ["SCA, liste d'autorisation,", "cache, quarantaine"], 'red', 11, bold=False); f.arrow(338, 116, 338, 80, head=False, dashed=True)
add(L2, "14.1", f, "Le lockfile rend le build reproductible, le proxy le rend disponible et contrôlé, Renovate le maintient à jour par petites merge requests, et l'analyse bloque ce qui est vulnérable ou inconnu. Sans ces quatre pièces, chaque build dépend d'Internet et de la bonne foi du monde entier.")

# 17 — Ansible
f = Fig("ansible", 480, 195, "Ansible : nœud de contrôle, inventaire, hôtes")
f.frame(4, 8, 200, 168, "nœud de contrôle (conteneur)")
f.box(16, 40, 176, 34, "playbook.yml", 'soft', 12); f.box(16, 82, 84, 34, "rôles", 'box', 11); f.box(108, 82, 84, 34, "inventaire", 'box', 11); f.box(16, 124, 176, 36, "ansible-playbook", 'green', 12, sub="SSH, pas d'agent")
for i, h in enumerate(["web1","web2","db1"]):
    y = 26 + i*50
    f.box(370, y, 100, 38, h, 'box', 12, sub="python3"); f.arrow(204, 142, 370, y+19)
f.text(290, 40, "modules → état désiré", fs=10); f.text(300, 188, "idempotent : relancer ne change rien", fs=10)
add(L3, "17.1", f, "Pas d'agent sur les hôtes : le nœud de contrôle pousse des modules par SSH, chaque module vérifie l'état et ne modifie que ce qui diffère. Le playbook décrit l'état voulu ; l'inventaire dit sur quoi ; les rôles rendent tout cela réutilisable.")

# 18 — image dorée
f = Fig("golden", 480, 175, "Le pipeline d'images de machines")
f.box(10, 40, 90, 50, "image de base", 'box', 11, sub="Ubuntu 24.04"); f.box(130, 40, 90, 50, "Packer", 'soft', 12, sub="+ rôle Ansible"); f.box(250, 40, 90, 50, "tests", 'amber', 12, sub="Goss, Trivy"); f.box(370, 40, 100, 50, "image dorée", 'green', 12, sub="AMI, template")
f.arrow(100, 65, 130, 65); f.arrow(220, 65, 250, 65); f.arrow(340, 65, 370, 65)
f.box(370, 116, 100, 36, "Terraform", 'box', 11, sub="instances"); f.arrow(420, 90, 420, 116)
f.text(180, 128, "immuable : on remplace, on ne modifie pas", fs=11); f.text(180, 146, "rotation mensuelle pour les CVE", fs=11)
add(L3, "18.1", f, "L'image est construite, durcie et testée une fois ; les instances sont des copies jetables. Corriger un serveur en place est interdit : on reconstruit l'image et on remplace les machines, ce qui rend le parc reproductible et les correctifs vérifiables.")

# 20 — responsabilité partagée
f = Fig("shared", 480, 215, "Le modèle de responsabilité partagée")
cols = [("IaaS (EC2)", 60), ("PaaS (RDS, EKS)", 200), ("SaaS, serverless", 340)]
layers = ["données, accès (IAM)", "application, code", "runtime, middleware", "OS, patchs", "réseau virtuel, pare-feu", "hyperviseur, serveurs", "datacenter, physique"]
custom = {0:5, 1:3, 2:2}
for ci,(name,x) in enumerate(cols):
    f.text(x+62, 22, name, 'glab')
    for li, lay in enumerate(layers):
        y = 30 + li*24; cls = 'amber' if li < custom[ci] else 'soft'
        f.raw(f'<rect x="{x}" y="{y}" width="124" height="22" rx="4" class="{cls}"/>'); f.text(x+62, y+15, lay, fs=10, cls='')
f.raw('<rect x="8" y="40" width="14" height="14" class="amber"/><rect x="8" y="70" width="14" height="14" class="soft"/>')
f.text(26, 51, "toi", fs=10, anchor='start'); f.text(26, 81, "le cloud", fs=10, anchor='start')
add(L4, "20.2", f, "Plus le service est managé, moins tu portes de couches ; les données et les accès restent toujours à toi. La majorité des incidents cloud ne viennent pas du fournisseur mais d'une configuration client : un bucket public, un rôle trop large, un port ouvert.")

# 22 — portable
f = Fig("portable", 480, 160, "Ce qui est portable entre clouds, ce qui ne l'est pas")
f.box(10, 16, 460, 48, ["conteneurs, Kubernetes, Terraform, OpenTelemetry, PostgreSQL"], 'green', 11, sub="portable : même code sur AWS, Azure, GCP")
f.box(10, 80, 220, 48, ["services managés spécifiques", "Lambda, DynamoDB, Cosmos DB, BigQuery"], 'amber', 11, bold=False)
f.box(250, 80, 220, 48, ["identité, réseau, facturation", "IAM, Entra ID, VPC, VNet, comptes"], 'soft', 11, bold=False)
f.text(240, 150, "le multi-cloud réel coûte cher : un cloud principal, des briques portables", fs=11)
add(L4, "22.1", f, "La couche du haut se déplace ; celle du bas se réapprend à chaque fournisseur. Le vrai multi-cloud est rare et cher ; ce qui compte est de savoir où l'on s'attache, et de ne le faire que là où le gain est réel.")

# 23 — FinOps
f = Fig("finops", 480, 200, "Le cycle FinOps et l'échelle des leviers")
f.box(10, 20, 116, 44, "Informer", 'soft', 12, sub="coût par équipe"); f.box(10, 74, 116, 44, "Optimiser", 'green', 12, sub="leviers ci-contre"); f.box(10, 128, 116, 40, "Opérer", 'box', 12, sub="revue mensuelle")
f.arrow(68, 64, 68, 74); f.arrow(68, 118, 68, 128); f.path("M126,148 C170,148 170,42 126,42")
lev = [("éteindre ce qui ne sert pas", "20 à 40 %", 'green'),("redimensionner, Graviton", "10 à 30 %", 'green'),("architecture : endpoints, cache, Spot", "10 à 20 %", 'soft'),("engagements, en dernier", "20 à 40 %", 'amber')]
for i,(t,g,c) in enumerate(lev):
    y = 20 + i*36
    f.box(190, y, 210, 28, t, c, 10, bold=False); f.text(410, y+18, g, fs=10, anchor='start')
f.text(250, 184, "coût par unité (par utilisateur, par requête) :", fs=10); f.text(250, 197, "la métrique qui distingue croissance et gaspillage", fs=10)
add(L4, "23.1", f, "Rendre le coût visible par équipe, l'optimiser dans l'ordre des leviers (le plus simple d'abord), et en faire une routine mensuelle. Les engagements viennent en dernier : on ne s'engage pas sur du gaspillage.")

# 24 — hybride
f = Fig("hybrid", 480, 175, "Une architecture hybride")
f.frame(4, 8, 200, 160, "sur site"); f.frame(276, 8, 200, 160, "cloud")
f.box(16, 38, 84, 44, "vSphere", 'box', 11, sub="Proxmox, Nutanix"); f.box(108, 38, 86, 44, "Active Directory", 'soft', 10)
f.box(16, 104, 178, 48, "Kubernetes on-prem", 'green', 12, sub="GitOps, même dépôt")
f.box(288, 38, 84, 44, "Direct Connect", 'box', 10, sub="ou VPN"); f.box(380, 38, 86, 44, "Identity Center", 'soft', 10, sub="fédéré à AD")
f.box(288, 104, 178, 48, "EKS + managés", 'green', 12, sub="GitOps, même dépôt")
f.arrow(194, 60, 288, 60); f.text(240, 52, "lien privé", fs=10); f.arrow(194, 128, 288, 128); f.text(241, 116, "un dépôt GitOps", fs=10)
add(L4, "24.1", f, "Deux plateformes, une seule façon de travailler : identité fédérée, réseau privé, GitOps depuis le même dépôt, observabilité centralisée. L'hybride qui marche est celui où les équipes ne voient pas la différence.")

# 27 — stockage
f = Fig("storage", 480, 170, "Comment un Pod obtient un disque persistant")
f.box(10, 30, 90, 46, "Pod", 'box', 12, sub="volumeMounts"); f.box(130, 30, 90, 46, "PVC", 'soft', 12, sub="demande 20 Gi"); f.box(250, 30, 90, 46, "PV", 'green', 12, sub="le disque, lié"); f.box(370, 30, 100, 46, "disque cloud", 'box', 11, sub="EBS, Ceph RBD")
f.arrow(100, 53, 130, 53); f.arrow(220, 53, 250, 53); f.arrow(340, 53, 370, 53)
f.box(130, 108, 210, 42, "StorageClass + pilote CSI", 'amber', 12, sub="provisionne à la demande")
f.arrow(235, 108, 235, 76); f.arrow(300, 108, 420, 76)
f.text(55, 122, "modes d'accès :", fs=10); f.text(55, 136, "RWO, RWX, ROX", fs=10)
f.text(410, 122, "WaitForFirstConsumer :", fs=9); f.text(410, 135, "même zone que le Pod", fs=9)
add(L5, "27.1", f, "Le Pod demande (PVC), la StorageClass fait créer (PV) par le pilote du stockage. RWO = un nœud à la fois ; un PVC Pending vient presque toujours d'une StorageClass absente ou d'une zone différente de celle du Pod.")

# 28 — Helm et Kustomize
f = Fig("helmkust", 480, 190, "Helm et Kustomize : deux façons de produire des manifests")
f.frame(4, 8, 230, 174, "Helm"); f.box(16, 36, 96, 40, "chart", 'soft', 11, sub="templates"); f.box(124, 36, 96, 40, "values.yaml", 'box', 11, sub="par environnement")
f.box(16, 100, 204, 34, "release (révision 1, 2, 3…)", 'green', 11); f.arrow(64, 76, 100, 100); f.arrow(172, 76, 140, 100)
f.text(118, 156, "rollback = révision précédente", fs=11); f.text(118, 170, "pour les paquets tiers", fs=11)
f.frame(246, 8, 230, 174, "Kustomize"); f.box(300, 36, 120, 40, "base/", 'soft', 11, sub="manifests communs")
f.box(258, 100, 96, 34, "overlays/dev", 'box', 11); f.box(366, 100, 96, 34, "overlays/prod", 'box', 11)
f.arrow(340, 76, 306, 100); f.arrow(380, 76, 414, 100)
f.text(360, 156, "patches, images, réplicas", fs=11); f.text(360, 170, "pour ses propres applications", fs=11)
add(L5, "28.1", f, "Helm rend un modèle avec des valeurs et garde l'historique des releases ; Kustomize empile des correctifs sur une base. Les deux sortent des manifests que Kubernetes applique ; ArgoCD sait lire les deux.")

# 30 — mesh
f = Fig("mesh", 480, 200, "Service mesh : plan de contrôle et plan de données")
f.box(150, 12, 180, 44, "plan de contrôle : istiod", 'purple', 12, sub="configuration, certificats, politiques")
for i,(n,x) in enumerate([("api",30),("notification",190),("incidents",350)]):
    f.frame(x, 86, 110, 80, None); f.box(x+8, 94, 94, 30, n, 'box', 11); f.box(x+8, 130, 94, 30, "proxy sidecar", 'soft', 10)
    f.arrow(240, 56, x+55, 86, dashed=True)
f.arrow(140, 145, 190, 145); f.text(165, 137, "mTLS", fs=10); f.arrow(300, 145, 350, 145); f.text(325, 137, "mTLS", fs=10)
f.text(240, 188, "ambient : proxy hors du Pod (ztunnel par nœud), application inchangée", fs=10)
add(L5, "30.1", f, "Le plan de contrôle distribue configuration, identités et certificats ; les proxies du plan de données chiffrent, authentifient, routent et mesurent chaque appel sans que l'application ne change. On l'adopte pour le mTLS et l'observabilité, on le paie en complexité.")

# 31 — autoscaling
f = Fig("autoscale", 480, 190, "La boucle d'autoscaling, des métriques aux nœuds")
f.box(10, 30, 100, 46, "metrics-server", 'box', 11, sub="CPU, mémoire"); f.box(140, 30, 96, 46, "HPA", 'soft', 12, sub="cible 70 % CPU"); f.box(266, 30, 100, 46, "Deployment", 'green', 11, sub="replicas 3 → 6"); f.box(396, 30, 74, 46, "Pods", 'box', 12, sub="Pending ?")
f.arrow(110, 53, 140, 53); f.arrow(236, 53, 266, 53); f.arrow(366, 53, 396, 53)
f.box(266, 108, 204, 46, "Cluster Autoscaler, Karpenter", 'amber', 11, sub="ajoute un nœud si Pending")
f.arrow(433, 76, 433, 108); f.arrow(266, 131, 60, 131); f.arrow(60, 131, 60, 76); f.text(135, 148, "les nouveaux Pods remontent des métriques", fs=10, maxw=250)
f.text(240, 178, "KEDA : à zéro et sur des files ; VPA : ajuste les requests", fs=10)
add(L5, "31.1", f, "Deux boucles emboîtées : l'HPA ajoute des Pods à partir des métriques ; quand ils ne trouvent plus de place, l'autoscaler de cluster ajoute des nœuds. Sans requests correctes, aucune des deux ne fonctionne.")

# 32 — logs
f = Fig("logs", 480, 160, "Le chemin d'une ligne de log")
f.box(10, 30, 100, 50, "application", 'box', 11, sub="JSON sur stdout"); f.box(140, 30, 100, 50, "agent", 'soft', 11, sub="Alloy, par nœud"); f.box(270, 30, 100, 50, "Loki", 'green', 12, sub="labels, rétention"); f.box(400, 30, 70, 50, "Grafana", 'box', 11, sub="LogQL")
f.arrow(110, 55, 140, 55); f.arrow(240, 55, 270, 55); f.arrow(370, 55, 400, 55); f.text(255, 24, "+ labels Kubernetes", fs=10)
f.text(240, 108, '{"ts":"…","level":"ERROR","trace_id":"4f2c…","msg":"paiement refusé"}', fs=10)
f.text(240, 128, "le trace_id relie le log à sa trace ;", fs=10); f.text(240, 142, "les données personnelles sont masquées à la source", fs=10)
add(L6, "32.1", f, "L'application écrit une ligne structurée sur sa sortie standard et ne sait rien de la suite ; l'agent enrichit et expédie ; Loki indexe quelques labels et stocke le reste. Peu de labels, un trace_id partout, jamais de donnée personnelle.")

# 33 — Prometheus
f = Fig("prom", 480, 200, "Le modèle Prometheus : tirer, stocker, évaluer, alerter")
for i,n in enumerate(["api /metrics","db exporter","node exporter"]): f.box(10, 20+i*50, 100, 38, n, 'box', 11)
f.box(170, 42, 120, 66, "Prometheus", 'soft', 12, sub="scrape, TSDB, règles")
for i in range(3): f.arrow(170, 75, 110, 39+i*50)
f.text(140, 24, "pull", 'glab')
f.box(330, 14, 140, 44, "Alertmanager", 'red', 12, sub="regroupe et route"); f.arrow(290, 60, 330, 40); f.text(322, 68, "burn rate", fs=9)
f.box(330, 78, 140, 44, "Grafana", 'green', 12, sub="PromQL, dashboards"); f.arrow(330, 100, 290, 92)
f.box(330, 144, 140, 34, "astreinte ou ticket", 'box', 11); f.arrow(400, 58, 400, 78, head=False); f.arrow(400, 122, 400, 144)
f.text(150, 190, "longue durée et HA : Thanos, Mimir, VictoriaMetrics", fs=10)
add(L6, "33.1", f, "Prometheus va chercher les métriques (pull), les stocke en séries temporelles, évalue des règles et confie les alertes à Alertmanager qui les regroupe et les route. Grafana ne fait que lire. Les labels à forte cardinalité sont l'ennemi.")

# 36 — incident
f = Fig("incident", 480, 200, "Le cycle d'un incident et ses trois délais")
f.raw('<line x1="20" y1="70" x2="460" y2="70" class="axis"/>')
for n,x in [("panne",30),("détection",120),("prise en charge",210),("mitigation",320),("résolution",440)]:
    f.raw(f'<circle cx="{x}" cy="70" r="6" class="redfill"/>'); f.text(x, 94, n, fs=11)
f.arrow(30, 40, 120, 40); f.text(75, 32, "MTTD", fs=10); f.arrow(120, 40, 210, 40); f.text(165, 32, "MTTA", fs=10); f.arrow(210, 40, 440, 40); f.text(325, 32, "MTTR : mitigation puis résolution", fs=10)
f.box(10, 112, 108, 46, "commandant", 'purple', 11, sub="décide, ne débogue pas"); f.box(128, 112, 108, 46, "opérations", 'soft', 11, sub="diagnostique, agit"); f.box(246, 112, 108, 46, "communication", 'green', 11, sub="statut à cadence fixe"); f.box(364, 112, 106, 46, "scribe", 'box', 11, sub="chronologie")
f.box(10, 168, 460, 26, "post-mortem sans blâme sous 5 jours, actions suivies : l'incident ne revient pas", 'amber', 10, bold=False, rx=5)
add(L6, "36.1", f, "On mesure séparément détecter, prendre en charge et réparer, parce que chacun s'améliore avec un levier différent : alertes de symptômes, astreinte outillée, rollback et runbooks. Les rôles évitent que tout le monde débogue et que personne ne communique.")

# 37 — contrôles DevSecOps
f = Fig("devsecops", 480, 205, "Où chaque contrôle de sécurité s'exécute")
stages = [("pre-commit",["secrets","lint"]),("CI",["SAST, SCA","IaC"]),("build",["scan, SBOM","signature"]),("registre",["admission :","signé, digest"]),("staging",["DAST","tests sécu"]),("production",["Falco","posture"])]
for i,(s_,c) in enumerate(stages):
    x = 6 + i*79
    f.box(x, 26, 72, 40, s_, 'soft', 11); f.text(x+36, 86, c[0], fs=10); f.text(x+36, 100, c[1], fs=10)
    if i < 5: f.arrow(x+72, 46, x+79, 46)
f.box(6, 124, 230, 50, ["bloquant : critique exploitable,", "secret, image non signée"], 'red', 11, bold=False)
f.box(246, 124, 228, 50, ["en observation, puis ticket avec SLA :", "le reste, priorisé par EPSS et KEV"], 'amber', 11, bold=False)
f.text(240, 195, "200 alertes inexploitables : outil désactivé en une semaine", fs=10)
add(L7, "37.2", f, "Chaque contrôle a une place où il coûte le moins et arrête le plus : les secrets avant le commit, les dépendances à la CI, l'image au build, la signature à l'admission, le comportement à l'exécution. Bloquer peu, expliquer tout, mesurer le bruit.")

# 39 — 4C
f = Fig("fourc", 480, 200, "Les quatre couches de sécurité de Kubernetes")
f.raw('<rect x="10" y="10" width="460" height="180" rx="12" class="amber"/><rect x="60" y="44" width="360" height="140" rx="12" class="soft"/><rect x="110" y="78" width="260" height="100" rx="12" class="green"/><rect x="160" y="112" width="160" height="60" rx="12" class="box"/>')
f.text(240, 32, "Cloud : comptes, IAM, réseau, chiffrement, journaux", fs=11, bold=True, cls='')
f.text(240, 66, "Cluster : API, RBAC, PSA, admission, NetworkPolicy, etcd", fs=11, bold=True, cls='')
f.text(240, 100, "Conteneur : image durcie, non root, scan, signature", fs=11, bold=True, cls='')
f.text(240, 138, "Code : entrées, secrets, dépendances", fs=11, bold=True, cls=''); f.text(240, 156, "OWASP Top 10, tests de sécurité", fs=10)
add(L7, "39.1", f, "Chaque couche protège la suivante ; une faille dans une couche externe rend les internes inutiles. On sécurise de l'extérieur vers l'intérieur, et on ne compte jamais sur une seule couche.")

# 42 — preuve
f = Fig("compliance", 480, 160, "De l'exigence à la preuve automatique")
f.box(10, 30, 96, 50, "exigence", 'box', 11, sub="ISO 27001 A.8.x"); f.box(126, 30, 96, 50, "politique", 'soft', 11, sub="une page"); f.box(242, 30, 96, 50, "implémentation", 'green', 11, sub="pipeline, config"); f.box(358, 30, 112, 50, "preuve", 'amber', 11, sub="rapport signé, journal")
f.arrow(106, 55, 126, 55); f.arrow(222, 55, 242, 55); f.arrow(338, 55, 358, 55)
f.box(242, 110, 228, 36, "auditeur : échantillons en minutes", 'purple', 11); f.arrow(414, 80, 414, 110)
f.text(120, 120, "collectée chaque mois par script,", fs=10); f.text(120, 134, "versionnée, sans capture d'écran", fs=10)
add(L7, "42.1", f, "Une exigence devient une politique courte, une implémentation dans les outils, et une preuve produite par les systèmes eux-mêmes. La conformité cesse d'être une campagne annuelle de captures d'écran : elle est un sous-produit du pipeline.")

# 43 — contrat SRE
f = Fig("srecontract", 480, 205, "Qui est responsable de quoi : équipe produit, SRE, plateforme")
f.box(10, 16, 146, 120, ["équipe produit", "", "code et fiabilité", "de son service,", "astreinte, SLO,", "post-mortems"], 'box', 11, bold=False)
f.box(167, 16, 146, 120, ["SRE", "", "standards, SLO", "de la plateforme,", "revue de lancement,", "incidents majeurs, toil"], 'purple', 11, bold=False)
f.box(324, 16, 146, 120, ["plateforme", "", "capacités en", "libre-service :", "SLO as code, canary,", "sauvegardes, incidents"], 'green', 11, bold=False)
f.arrow(156, 76, 167, 76); f.arrow(313, 76, 324, 76)
f.box(10, 150, 460, 46, ["contrat : prise en charge si la revue de lancement est passée et le budget d'erreur respecté ;", "retour à l'équipe si le toil ou les incidents deviennent insoutenables"], 'amber', 10, bold=False, rx=5)
add(L8, "43.1", f, "La responsabilité d'un service reste à l'équipe qui l'écrit ; la SRE fixe les standards et tient la plateforme ; la plateforme rend la fiabilité disponible sans ticket. Le contrat écrit évite l'exploitation subie.")

# 45 — latence
f = Fig("latency", 480, 195, "Où part le temps d'une requête (p95, exemple)")
segs = [("DNS + TLS",25,'box'),("équilibreur",10,'box'),("API : code",40,'soft'),("base : requête",60,'amber'),("appel externe",120,'red'),("sérialisation",15,'box')]
x = 20; tot = sum(v for _,v,_ in segs); scale = 440/tot
for i,(n,v,c) in enumerate(segs):
    w = v*scale
    f.raw(f'<rect x="{x:.1f}" y="40" width="{w:.1f}" height="34" class="{c}"/>')
    if w > 30: f.text(x+w/2, 62, f"{v} ms", fs=10, cls='')
    f.text(min(x+w/2, 436), 92 if i%2==0 else 108, n, fs=10)
    x += w
f.text(240, 24, f"total ≈ {tot} ms : la moitié dans un appel externe", fs=11, bold=True, cls='')
f.box(20, 124, 440, 26, "mesurer d'abord (traces), corriger le plus gros segment, remesurer", 'green', 11, bold=False, rx=5)
f.text(240, 170, "leviers par segment : cache, index, connexions persistantes,", fs=10); f.text(240, 184, "appels parallèles, timeouts, CDN", fs=10)
add(L8, "45.1", f, "Une trace montre la répartition ; l'optimisation commence par le segment le plus large, pas par celui qu'on connaît le mieux. La moyenne cache tout : on regarde le p95 et le p99.")

# 47 — expand / contract
f = Fig("expand", 480, 180, "Migration de schéma sans interruption : expand, migrate, contract")
ph = [("1. expand","ajoute la colonne, nullable ; le code v1 l'ignore",'soft'),("2. migrate","le code v2 écrit les deux ; un lot remplit l'ancien stock",'green'),("3. switch","le code v3 lit la nouvelle colonne ; rollback encore possible",'green'),("4. contract","supprime l'ancienne colonne, bien plus tard",'amber')]
for i,(t,d,c) in enumerate(ph):
    y = 14 + i*38
    f.box(10, y, 104, 30, t, c, 11); f.text(124, y+19, d, fs=10, anchor='start')
f.text(240, 172, "chaque étape reste compatible avec la précédente", fs=10)
add(L8, "47.2", f, "Jamais de changement de schéma en une seule fois : on ajoute, on migre, on bascule, on retire, chaque étape étant compatible avec le code précédent. Le rollback du code suffit alors à tout moment.")

# 49 — landing zone
f = Fig("lz", 480, 205, "Une landing zone AWS : organisation, unités, comptes")
f.box(180, 10, 120, 34, "Organisation", 'purple', 12, sub="SCP, facturation")
ous = [("Sécurité",20,100),("Infrastructure",130,100),("Charges de travail",240,120),("Bac à sable",370,90)]
for n,x,w in ous:
    f.box(x, 68, w, 30, n, 'soft', 11); f.arrow(240, 44, x+w/2, 68)
accs = [("logs",20,'box'),("audit",76,'box'),("réseau",130,'box'),("outillage",186,'box'),("dev",240,'green'),("staging",296,'green'),("prod",352,'amber'),("perso",408,'box')]
for n,x,c in accs:
    f.box(x, 122, 52, 32, n, c, 10); f.arrow(x+26, 98, x+26, 122, head=False)
f.text(240, 178, "Identity Center pour les humains, rôles pour les charges,", fs=10); f.text(240, 192, "CloudTrail centralisé, budgets par compte", fs=10)
add(L9, "49.1", f, "Un compte est une frontière de sécurité et de facturation : un par environnement et par domaine, groupés en unités où s'appliquent les garde-fous (SCP). Sécurité et journaux vivent dans des comptes que personne d'autre n'écrit.")

# 50 — 7 R
f = Fig("sevenr", 480, 215, "Les 7 R : l'arbre de décision par application")
f.box(140, 10, 200, 32, "l'application sert-elle ?", 'soft', 11)
f.box(10, 62, 120, 30, "non → Retire", 'amber', 11); f.arrow(170, 42, 70, 62)
f.box(140, 62, 200, 32, "un SaaS équivalent existe ?", 'soft', 10); f.arrow(240, 42, 240, 62)
f.box(350, 62, 120, 30, "oui → Repurchase", 'amber', 11); f.arrow(340, 78, 350, 78)
f.box(140, 114, 200, 32, "vaut-elle un investissement ?", 'soft', 10); f.arrow(240, 94, 240, 114)
f.box(10, 114, 120, 32, ["non → Rehost,", "Relocate"], 'green', 10); f.arrow(140, 130, 130, 130)
f.box(350, 114, 120, 30, "oui → Refactor", 'red', 11); f.arrow(340, 130, 350, 130)
f.box(140, 166, 200, 32, "entre les deux → Replatform", 'green', 10); f.arrow(240, 146, 240, 166)
f.text(12, 178, "Retain : pas maintenant,", fs=10, anchor='start'); f.text(12, 192, "décision datée", fs=10, anchor='start')
add(L9, "50.1", f, "Quatre questions par application, dans cet ordre, et une réponse par lot. Le résultat réaliste d'un portefeuille : beaucoup de replatform et de rehost, peu de refactor, et un tiers de retire que personne n'avait vu.")

# 51 — gouvernance
f = Fig("gov", 480, 140, "De la décision technique à la règle appliquée")
f.box(10, 30, 96, 50, "RFC", 'box', 11, sub="proposition"); f.box(126, 30, 96, 50, "revue", 'soft', 11, sub="commentaires, délai"); f.box(242, 30, 96, 50, "ADR", 'green', 11, sub="décision datée"); f.box(358, 30, 112, 50, "politique as code", 'amber', 11, sub="OPA, Kyverno, CI")
f.arrow(106, 55, 126, 55); f.arrow(222, 55, 242, 55); f.arrow(338, 55, 358, 55)
f.text(240, 112, "les exceptions sont écrites, datées, revues ;", fs=11); f.text(240, 128, "une règle sans outil est un vœu", fs=11)
add(L9, "51.1", f, "Une décision se propose, se discute, se consigne, puis s'applique par un outil plutôt que par une revue humaine. Ce qui n'est pas dans le code de politique n'est pas une règle, c'est une préférence.")

# 52 — DORA
f = Fig("dora", 480, 155, "D'où viennent les métriques DORA")
f.box(10, 16, 100, 40, "Git", 'box', 11, sub="commits, MR"); f.box(10, 66, 100, 40, "CI/CD", 'box', 11, sub="déploiements"); f.box(10, 116, 100, 30, "incidents", 'box', 11)
f.box(170, 45, 130, 60, "collecteur", 'soft', 12, sub="DevLake, script, API"); f.arrow(110, 36, 170, 65); f.arrow(110, 86, 170, 80); f.arrow(110, 131, 170, 95)
f.box(340, 16, 130, 46, "quatre métriques", 'green', 11, sub="par équipe, par mois"); f.box(340, 90, 130, 46, "décision", 'amber', 11, sub="revue mensuelle")
f.arrow(300, 65, 340, 43); f.arrow(405, 62, 405, 90)
add(L9, "52.1", f, "Les métriques sortent des systèmes, jamais de saisies : un commit horodaté, un déploiement horodaté, un incident horodaté suffisent. Elles servent à décider quelque chose chaque mois ; sans décision, ce sont des graphiques.")

# 53 — Team Topologies
f = Fig("topo", 480, 205, "Team Topologies : quatre types d'équipes")
for i,n in enumerate([("équipe flux","incidents"),("équipe flux","notifications"),("équipe flux","cartographie")]):
    f.box(10+i*124, 20, 114, 44, n[0], 'box', 11, sub=n[1])
f.box(388, 20, 82, 44, "sous-système", 'purple', 10, sub="complexe")
f.box(10, 112, 362, 48, ["équipe plateforme", "ce que les équipes flux consomment en libre-service"], 'green', 11, bold=False)
for i in range(3): f.arrow(67+i*124, 64, 67+i*124, 112, dashed=True)
f.box(388, 112, 82, 48, "habilitante", 'amber', 10, sub="temporaire"); f.arrow(388, 136, 372, 136); f.arrow(429, 112, 429, 64, dashed=True)
f.text(240, 182, "interactions : collaboration (courte),", fs=10); f.text(240, 196, "X-as-a-service (durable), facilitation (temporaire)", fs=10)
add(L9, "53.2", f, "Les équipes alignées sur un flux livrent de la valeur ; la plateforme réduit leur charge cognitive ; l'équipe habilitante fait monter en compétence puis s'efface. La SRE est une plateforme ou une équipe habilitante, jamais un goulot.")

# 54 — application LLM
f = Fig("llmapp", 480, 232, "Architecture d'une application LLM en production")
f.box(10, 20, 90, 44, "utilisateur", 'box', 11); f.box(130, 20, 220, 44, "application", 'soft', 12, sub="garde-fous, prompt, sortie validée"); f.arrow(100, 42, 130, 42)
f.box(380, 20, 90, 44, "réponse", 'green', 11, sub="avec sources"); f.arrow(350, 42, 380, 42)
f.box(130, 86, 100, 46, "récupération", 'green', 11, sub="pgvector, BM25"); f.box(250, 86, 100, 46, "droits d'accès", 'red', 11, sub="filtre avant classement"); f.arrow(240, 64, 180, 86); f.arrow(230, 109, 250, 109)
f.box(130, 154, 220, 44, "passerelle LLM", 'purple', 11, sub="auth, quotas, journal, coût, cache"); f.arrow(240, 132, 240, 154)
f.box(380, 154, 90, 44, "modèle", 'box', 11, sub="API ou vLLM"); f.arrow(350, 176, 380, 176)
f.box(10, 154, 100, 44, "evals en CI", 'amber', 11, sub="30 cas, seuil"); f.arrow(110, 176, 130, 176, dashed=True)
f.text(240, 214, "traces OpenTelemetry par requête :", fs=10); f.text(240, 228, "récupération, prompt, appel, validation, tokens, coût", fs=10)
add(L9, "54.8", f, "Le modèle est une brique parmi huit : la récupération filtrée par les droits, la validation de sortie, la passerelle et l'évaluation continue font la différence entre une démonstration et un produit.")

# ============ insertion ============
by_file = {}
for lvl, sec, svg in FIGS: by_file.setdefault(lvl, []).append((sec, svg))
for fn, items in by_file.items():
    p = out/fn; s = p.read_text(); n = 0
    for sec, svg in items:
        lab = re.search(r'aria-label="([^"]+)"', svg).group(1)
        s = re.sub(r'<figure class="fig"><svg[^>]*aria-label="' + re.escape(lab) + r'".*?</figure>\n?', '', s, count=1, flags=re.S)   # remplace une version précédente
        m = re.search(r'<h3>' + re.escape(sec) + r' [^<]*(?:<span class="badge[^<]*</span>)?</h3>', s); assert m, (fn, sec)
        s = s[:m.end()] + '\n' + svg + s[m.end():]; n += 1
    p.write_text(s); print(fn, n)
print('total', len(FIGS))
