import re, pathlib, html as H

out = pathlib.Path('/mnt/user-data/outputs')
FIGS = []  # (level file, section number, svg html)

class Fig:
    def __init__(self, ident, w, h, label):
        self.id = ident; self.w = w; self.h = h; self.label = label; self.b = ''
        self.m = f'ah_{ident}'
    def box(self, x, y, w, h, lines, cls='box', fs=12, bold=True, sub=None, rx=7):
        if isinstance(lines, str): lines = [lines]
        self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>'
        n = len(lines) + (1 if sub else 0); lh = fs + 4
        y0 = y + h/2 - (n-1)*lh/2 + fs*0.35
        for i, t in enumerate(lines):
            self.b += f'<text x="{x+w/2}" y="{y0+i*lh:.1f}" text-anchor="middle" font-size="{fs}"{" font-weight=\"700\"" if bold else ""}>{H.escape(t)}</text>'
        if sub: self.b += f'<text x="{x+w/2}" y="{y0+len(lines)*lh:.1f}" text-anchor="middle" class="lbl">{H.escape(sub)}</text>'
        return self
    def text(self, x, y, t, cls='lbl', anchor='middle', fs=None, bold=False):
        extra = (f' font-size="{fs}"' if fs else '') + (' font-weight="700"' if bold else '')
        self.b += f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}"{extra}>{H.escape(t)}</text>'
        return self
    def arrow(self, x1, y1, x2, y2, label=None, dashed=False, dx=0, dy=-6, head=True):
        self.b += f'<path d="M{x1},{y1} L{x2},{y2}" class="arrow{" dashed" if dashed else ""}"{f" marker-end=\"url(#{self.m})\"" if head else ""}/>'
        if label: self.b += f'<text x="{(x1+x2)/2+dx}" y="{(y1+y2)/2+dy}" text-anchor="middle" class="lbl">{H.escape(label)}</text>'
        return self
    def path(self, d, label=None, lx=0, ly=0, dashed=False, head=True):
        self.b += f'<path d="{d}" class="arrow{" dashed" if dashed else ""}"{f" marker-end=\"url(#{self.m})\"" if head else ""}/>'
        if label: self.b += f'<text x="{lx}" y="{ly}" text-anchor="middle" class="lbl">{H.escape(label)}</text>'
        return self
    def frame(self, x, y, w, h, label=None, cls='frame'):
        self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" class="{cls}"/>'
        if label: self.b += f'<text x="{x+8}" y="{y+15}" class="glab">{H.escape(label)}</text>'
        return self
    def raw(self, s): self.b += s; return self
    def render(self, caption):
        return (f'<figure class="fig"><svg viewBox="0 0 {self.w} {self.h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{H.escape(self.label)}">'
                f'<defs><marker id="{self.m}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="ahead"/></marker></defs>'
                f'{self.b}</svg><figcaption>{caption}</figcaption></figure>')

def add(level, section, fig, caption):
    FIGS.append((level, section, fig.render(caption)))

L0="devops-niveau-0-fondations.html"; L1="devops-niveau-1-conteneurs.html"; L2="devops-niveau-2-ci-cd.html"; L3="devops-niveau-3-infrastructure-as-code.html"
L4="devops-niveau-4-cloud.html"; L5="devops-niveau-5-kubernetes.html"; L6="devops-niveau-6-observabilite.html"; L7="devops-niveau-7-securite-devsecops.html"
L8="devops-niveau-8-sre-architecture.html"; L9="devops-niveau-9-expert-leadership.html"

# ---------------- 2 : méthode de diagnostic ----------------
f = Fig("diag", 480, 150, "La méthode de diagnostic d'une machine Linux")
steps = [("uptime","charge ?"),("top","CPU ou attente ?"),("free","swap ?"),("df","disque, inodes ?"),("ss","le port écoute ?"),("journalctl","que dit le service ?")]
for i,(c,q) in enumerate(steps):
    x = 4 + i*79
    f.box(x, 20, 70, 44, c, 'soft', 12, sub=None); f.text(x+35, 82, q, fs=11)
    if i < 5: f.arrow(x+70, 42, x+79, 42)
f.box(4, 100, 226, 36, "Symptôme utilisateur : « c'est lent », « ça ne répond pas »", 'amber', 11, bold=False)
f.box(250, 100, 226, 36, "Cause trouvée → correction → post-mortem", 'green', 11, bold=False)
f.arrow(230, 118, 250, 118)
add(L0, "2.6", f, "Six commandes, dans cet ordre, et une question par commande. On ne « regarde partout » pas : on descend du symptôme (charge) vers la cause (le service), et on s'arrête dès qu'une réponse explique le symptôme.")

# ---------------- 4 : flux et redirections ----------------
f = Fig("redir", 480, 190, "Entrées, sorties et redirections d'un processus")
f.box(170, 60, 140, 70, ["commande"], 'soft', 13, sub="un processus")
f.box(10, 70, 110, 44, ["clavier ou", "< fichier"], 'box', 11, bold=False); f.arrow(120, 92, 170, 92, "0 : stdin", dy=-8)
f.box(360, 40, 110, 40, ["écran ou", "> fichier"], 'green', 11, bold=False); f.arrow(310, 78, 360, 60, "1 : stdout", dx=-4, dy=-10)
f.box(360, 110, 110, 40, ["écran ou", "2> erreurs.log"], 'red', 11, bold=False); f.arrow(310, 110, 360, 130, "2 : stderr", dx=-4, dy=14)
f.text(240, 160, "2>&1 : stderr rejoint stdout   |   cmd1 | cmd2 : le stdout de l'un devient le stdin de l'autre", fs=11)
f.text(240, 178, "> fichier 2>&1 : tout dans le fichier   ;   $? : code de retour (0 = succès)", fs=11)
add(L0, "4.1", f, "Trois flux numérotés : 0 entre, 1 et 2 sortent. Toute redirection ne fait que rebrancher ces flux ; un pipe branche la sortie d'un processus sur l'entrée du suivant. Séparer stdout et stderr, c'est ce qui rend un script utilisable en pipeline.")

# ---------------- 6 : index ----------------
f = Fig("index", 480, 175, "Requête sans index et avec index")
f.frame(4, 8, 230, 158, "Sans index : Seq Scan")
for i in range(8):
    f.raw(f'<rect x="{16+i*26}" y="60" width="22" height="70" rx="3" class="amber"/>')
f.text(119, 46, "lit toutes les lignes (1 000 000)", fs=11); f.text(119, 150, "temps ∝ taille de la table", fs=11)
f.frame(246, 8, 230, 158, "Avec index : Index Scan")
f.box(330, 40, 60, 26, "racine", 'soft', 11); f.box(280, 84, 60, 26, "< M", 'soft', 11); f.box(380, 84, 60, 26, "≥ M", 'soft', 11)
f.arrow(350, 66, 315, 84); f.arrow(370, 66, 405, 84)
f.raw('<rect x="396" y="124" width="22" height="30" rx="3" class="green"/>'); f.arrow(410, 110, 408, 124)
f.text(361, 150, "3 ou 4 lectures", fs=11, anchor='middle'); f.text(361, 163, "temps ∝ log(taille)", fs=11)
add(L0, "6.3", f, "EXPLAIN ANALYZE dit lequel des deux se produit. Un Seq Scan sur une table qui grossit est une bombe à retardement : rapide en développement, lent en production. L'index se paie à l'écriture ; on indexe ce qu'on filtre et ce qu'on joint.")

# ---------------- 9 : pile Compose ----------------
f = Fig("compose", 480, 200, "Une pile Compose avec deux réseaux et des volumes")
f.frame(4, 30, 210, 100, "réseau frontend")
f.frame(140, 30, 336, 160, "réseau backend")
f.box(20, 60, 100, 44, "proxy", 'soft', 12, sub="nginx / Caddy"); f.box(160, 60, 90, 44, "web", 'box', 12, sub="React")
f.box(280, 60, 90, 44, "api", 'box', 12, sub="Spring Boot"); f.box(390, 60, 76, 44, "db", 'green', 12, sub="PostgreSQL")
f.box(280, 130, 90, 40, "redis", 'box', 12, sub="cache"); f.box(390, 130, 76, 40, "volume", 'amber', 11, sub="pgdata")
f.arrow(120, 82, 160, 82); f.arrow(250, 82, 280, 82); f.arrow(370, 82, 390, 82); f.arrow(325, 104, 325, 130); f.arrow(428, 104, 428, 130, head=False)
f.text(70, 22, "Internet", 'glab'); f.arrow(70, 26, 70, 60, ":443 seul port publié", dx=60, dy=0)
add(L1, "9.3", f, "Un seul point d'entrée publie un port ; le front ne voit pas la base (réseaux séparés) ; ce qui doit survivre est dans un volume nommé. depends_on avec condition service_healthy ordonne le démarrage, et l'application retente quand même.")

# ---------------- 10 : registre, tags et digests ----------------
f = Fig("registry", 480, 170, "Build, push, pull : tags et digest")
f.box(10, 30, 100, 50, "docker build", 'box', 12, sub="CI"); f.box(190, 30, 110, 50, "registre", 'soft', 12, sub="Harbor, ECR…"); f.box(370, 30, 100, 50, "cluster", 'green', 12, sub="pull")
f.arrow(110, 55, 190, 55, "push api:1.7.0", dy=-8); f.arrow(300, 55, 370, 55, "pull par digest", dy=-8)
f.box(10, 110, 220, 46, ["tag  api:1.7.0  →  mutable", "peut être réécrit : jamais en prod"], 'amber', 11, bold=False)
f.box(250, 110, 220, 46, ["digest  sha256:3f9c…  →  immuable", "identifie exactement ce qui tourne"], 'green', 11, bold=False)
f.arrow(245, 80, 130, 110, dashed=True, head=False); f.arrow(245, 80, 360, 110, dashed=True, head=False)
add(L1, "10.1", f, "Le tag est un nom, le digest est une empreinte du contenu. On construit une fois, on pousse un tag pour les humains et un digest pour les machines ; le déploiement référence le digest, vérifié à l'admission (chapitre 40).")

# ---------------- 12 : modèle des runners ----------------
f = Fig("runner", 480, 190, "Serveur CI, runners et exécuteurs")
f.box(10, 60, 120, 60, ["GitLab / GitHub"], 'soft', 12, sub="pipelines, jobs, artefacts")
f.box(200, 20, 120, 46, "runner A", 'box', 12, sub="docker executor"); f.box(200, 80, 120, 46, "runner B", 'box', 12, sub="kubernetes executor"); f.box(200, 140, 120, 40, "runner C", 'box', 12, sub="shell (à éviter)")
f.arrow(130, 80, 200, 43, "demande un job (poll)", dx=-10, dy=-14); f.arrow(130, 95, 200, 103); f.arrow(130, 105, 200, 160)
f.box(370, 20, 100, 46, "conteneur", 'green', 11, sub="image du job"); f.box(370, 80, 100, 46, "Pod éphémère", 'green', 11, sub="par job")
f.arrow(320, 43, 370, 43); f.arrow(320, 103, 370, 103)
f.text(420, 150, "artefacts, cache,", fs=11); f.text(420, 164, "logs → serveur", fs=11); f.arrow(370, 150, 330, 150, head=False, dashed=True)
add(L2, "12.1", f, "Le serveur ne fait rien tourner : les runners viennent chercher des jobs et les exécutent dans un conteneur ou un Pod jetable. Un runner shell partagé exécute du code inconnu sur une machine durable : c'est la première faille des CI d'entreprise.")

# ---------------- 13 : pyramide des tests et quality gate ----------------
f = Fig("pyramid", 480, 190, "La pyramide des tests et la barrière qualité")
f.raw('<polygon points="200,20 280,20 330,80 150,80" class="amber"/><polygon points="150,86 330,86 380,146 100,146" class="soft"/><polygon points="100,152 380,152 420,182 60,182" class="green"/>')
f.text(240, 55, "bout en bout : peu, lents, fragiles", fs=11, bold=True); f.text(240, 121, "intégration : Testcontainers, contrats", fs=11, bold=True); f.text(240, 172, "unitaires : nombreux, rapides, isolés", fs=11, bold=True)
f.text(50, 40, "minutes", fs=11); f.text(50, 110, "secondes", fs=11); f.text(50, 170, "millisecondes", fs=11)
f.box(390, 20, 84, 110, ["quality", "gate"], 'red', 12, sub="bloque la MR")
f.text(432, 145, "couverture du neuf", fs=10); f.text(432, 158, "0 bug critique", fs=10); f.text(432, 171, "mutation ≥ 60 %", fs=10)
add(L2, "13.1", f, "Beaucoup de tests rapides en bas, peu de tests lents en haut. La barrière qualité juge le code nouveau, pas l'historique, et bloque la merge request : c'est ce qui rend la pyramide obligatoire plutôt que souhaitable.")

# ---------------- 14 : dépendances ----------------
f = Fig("deps", 480, 170, "Le circuit des dépendances")
f.box(10, 30, 100, 50, "développeur", 'box', 12, sub="pom.xml, package.json"); f.box(150, 30, 110, 50, "lockfile", 'soft', 12, sub="versions exactes"); f.box(300, 30, 100, 50, "proxy", 'amber', 12, sub="Nexus, Artifactory"); f.box(420, 30, 50, 50, ["dépôts", "publics"], 'box', 11)
f.arrow(110, 55, 150, 55); f.arrow(260, 55, 300, 55, "npm ci / mvn", dy=-8); f.arrow(400, 55, 420, 55)
f.box(150, 110, 110, 46, "Renovate", 'green', 12, sub="MR automatique"); f.arrow(205, 110, 205, 80, "met à jour", dx=40, dy=0)
f.box(300, 110, 170, 46, ["SCA, liste d'autorisation,", "cache, quarantaine"], 'red', 11, bold=False); f.arrow(350, 110, 350, 80, head=False, dashed=True)
add(L2, "14.1", f, "Le lockfile rend le build reproductible, le proxy le rend disponible et contrôlé, Renovate le maintient à jour par petites merge requests, et l'analyse bloque ce qui est vulnérable ou inconnu. Sans ces quatre pièces, chaque build dépend d'Internet et de la bonne foi du monde entier.")

# ---------------- 17 : modèle Ansible ----------------
f = Fig("ansible", 480, 185, "Ansible : nœud de contrôle, inventaire, hôtes")
f.frame(4, 8, 200, 168, "nœud de contrôle (conteneur)")
f.box(16, 40, 176, 34, "playbook.yml", 'soft', 12); f.box(16, 82, 84, 34, "rôles", 'box', 11); f.box(108, 82, 84, 34, "inventaire", 'box', 11); f.box(16, 124, 176, 36, "ansible-playbook", 'green', 12, sub="SSH, pas d'agent")
for i, h in enumerate(["web1","web2","db1"]):
    y = 30 + i*50
    f.box(370, y, 100, 38, h, 'box', 12, sub="python3"); f.arrow(204, 142, 370, y+19, "modules → état désiré" if i==0 else None, dx=0, dy=-12)
f.text(290, 165, "idempotent : relancer ne change rien", fs=11)
add(L3, "17.1", f, "Pas d'agent sur les hôtes : le nœud de contrôle pousse des modules par SSH, chaque module vérifie l'état et ne modifie que ce qui diffère. Le playbook décrit l'état voulu ; l'inventaire dit sur quoi ; les rôles rendent tout cela réutilisable.")

# ---------------- 18 : image dorée ----------------
f = Fig("golden", 480, 160, "Le pipeline d'images de machines")
f.box(10, 40, 90, 50, "image de base", 'box', 11, sub="Ubuntu 24.04"); f.box(130, 40, 90, 50, "Packer", 'soft', 12, sub="+ rôle Ansible"); f.box(250, 40, 90, 50, "tests", 'amber', 12, sub="Goss, Trivy"); f.box(370, 40, 100, 50, "image dorée", 'green', 12, sub="AMI, template")
f.arrow(100, 65, 130, 65); f.arrow(220, 65, 250, 65); f.arrow(340, 65, 370, 65)
f.box(370, 110, 100, 36, "Terraform", 'box', 11, sub="instances"); f.arrow(420, 90, 420, 110)
f.text(170, 128, "immuable : on remplace, on ne modifie pas ; rotation mensuelle (CVE)", fs=11)
add(L3, "18.1", f, "L'image est construite, durcie et testée une fois ; les instances sont des copies jetables. Corriger un serveur en place est interdit : on reconstruit l'image et on remplace les machines, ce qui rend le parc reproductible et les correctifs vérifiables.")

# ---------------- 20 : responsabilité partagée ----------------
f = Fig("shared", 480, 210, "Le modèle de responsabilité partagée")
cols = [("IaaS (EC2)", 60), ("PaaS (RDS, EKS)", 200), ("SaaS / serverless", 340)]
layers = ["données, accès (IAM)", "application, code", "runtime, middleware", "OS, patchs", "réseau virtuel, pare-feu", "hyperviseur, serveurs", "datacenter, physique"]
custom = {0:5, 1:3, 2:2}
for ci,(name,x) in enumerate(cols):
    f.text(x+60, 22, name, 'glab')
    for li, lay in enumerate(layers):
        y = 30 + li*24; cls = 'amber' if li < custom[ci] else 'soft'
        f.raw(f'<rect x="{x}" y="{y}" width="120" height="22" rx="4" class="{cls}"/>')
        f.text(x+60, y+15, lay, fs=10, cls='')
f.raw('<rect x="6" y="40" width="14" height="14" class="amber"/><rect x="6" y="64" width="14" height="14" class="soft"/>')
f.text(24, 51, "toi", fs=10, anchor='start'); f.text(24, 75, "le", fs=10, anchor='start'); f.text(24, 87, "cloud", fs=10, anchor='start')
add(L4, "20.2", f, "Plus le service est managé, moins tu portes de couches ; les données et les accès restent toujours à toi. La majorité des incidents cloud ne viennent pas du fournisseur mais d'une configuration client : un bucket public, un rôle trop large, un port ouvert.")

# ---------------- 22 : portable contre spécifique ----------------
f = Fig("portable", 480, 150, "Ce qui est portable entre clouds, ce qui ne l'est pas")
f.box(10, 20, 460, 40, "applications en conteneurs, Kubernetes, Terraform, OpenTelemetry, PostgreSQL", 'green', 11, sub="portable : même code sur AWS, Azure, GCP")
f.box(10, 76, 220, 46, ["services managés spécifiques", "Lambda, DynamoDB, Cosmos DB, BigQuery"], 'amber', 11, bold=False)
f.box(250, 76, 220, 46, ["identité, réseau, facturation", "IAM, Entra ID, VPC/VNet, comptes"], 'soft', 11, bold=False)
f.text(240, 140, "multi-cloud réel = coûteux ; choisir un cloud principal, garder les briques portables", fs=11)
add(L4, "22.1", f, "La couche du haut se déplace ; celle du bas se réapprend à chaque fournisseur. Le vrai multi-cloud est rare et cher ; ce qui compte est de savoir où l'on s'attache, et de ne le faire que là où le gain est réel.")

# ---------------- 23 : FinOps ----------------
f = Fig("finops", 480, 175, "Le cycle FinOps et l'échelle des leviers")
f.box(10, 20, 110, 44, "Informer", 'soft', 12, sub="tags, coût par équipe"); f.box(10, 74, 110, 44, "Optimiser", 'green', 12, sub="leviers ci-contre"); f.box(10, 128, 110, 40, "Opérer", 'box', 12, sub="revue mensuelle")
f.arrow(65, 64, 65, 74); f.arrow(65, 118, 65, 128); f.path("M120,148 C160,148 160,42 120,42", head=True)
lev = [("éteindre ce qui ne sert pas", "20 à 40 %", 'green'),("redimensionner (VPA, Graviton)", "10 à 30 %", 'green'),("architecture (endpoints, cache, Spot)", "10 à 20 %", 'soft'),("engagements (Savings Plans)", "20 à 40 %, en dernier", 'amber')]
for i,(t,g,c) in enumerate(lev):
    y = 20 + i*38
    f.box(180, y, 200, 30, t, c, 11, bold=False); f.text(400, y+19, g, fs=11, anchor='start')
f.text(280, 168, "coût par unité (par utilisateur, par requête) : la seule métrique qui distingue croissance et gaspillage", fs=10)
add(L4, "23.1", f, "Rendre le coût visible par équipe, l'optimiser dans l'ordre des leviers (le plus simple d'abord), et en faire une routine mensuelle. Les engagements viennent en dernier : on ne s'engage pas sur du gaspillage.")

# ---------------- 24 : hybride ----------------
f = Fig("hybrid", 480, 170, "Une architecture hybride")
f.frame(4, 8, 210, 154, "sur site")
f.box(20, 40, 80, 40, "vSphere /", 'box', 11, sub="Proxmox, Nutanix"); f.box(114, 40, 86, 40, "Active Directory", 'soft', 11)
f.box(20, 100, 180, 44, "Kubernetes on-prem", 'green', 12, sub="GitOps, même dépôt")
f.frame(266, 8, 210, 154, "cloud")
f.box(282, 40, 80, 40, "Direct Connect", 'box', 11, sub="/ VPN"); f.box(376, 40, 86, 40, "Identity Center", 'soft', 11, sub="fédéré à AD")
f.box(282, 100, 180, 44, "EKS + services managés", 'green', 12, sub="GitOps, même dépôt")
f.arrow(200, 60, 282, 60, "lien privé", dy=-8); f.arrow(200, 60, 376, 60, head=False, dashed=True)
f.arrow(200, 122, 282, 122, "ArgoCD, un dépôt", dy=-8)
add(L4, "24.1", f, "Deux plateformes, une seule façon de travailler : identité fédérée, réseau privé, GitOps depuis le même dépôt, observabilité centralisée. L'hybride qui marche est celui où les équipes ne voient pas la différence.")

# ---------------- 27 : stockage ----------------
f = Fig("storage", 480, 165, "Comment un Pod obtient un disque persistant")
f.box(10, 30, 90, 46, "Pod", 'box', 12, sub="volumeMounts"); f.box(130, 30, 90, 46, "PVC", 'soft', 12, sub="demande : 20 Gi"); f.box(250, 30, 90, 46, "PV", 'green', 12, sub="le disque, lié"); f.box(370, 30, 100, 46, "disque cloud", 'box', 11, sub="EBS, Ceph RBD")
f.arrow(100, 53, 130, 53); f.arrow(220, 53, 250, 53, "liaison", dy=-8); f.arrow(340, 53, 370, 53)
f.box(130, 105, 210, 40, "StorageClass + pilote CSI", 'amber', 12, sub="provisionne à la demande")
f.arrow(235, 105, 235, 76, head=True); f.arrow(300, 105, 420, 76, head=True)
f.text(60, 125, "modes d'accès :", fs=11); f.text(60, 139, "RWO, RWX, ROX", fs=11)
f.text(410, 125, "WaitForFirstConsumer :", fs=10); f.text(410, 139, "bon AZ, bon nœud", fs=10)
add(L5, "27.1", f, "Le Pod demande (PVC), la StorageClass fait créer (PV) par le pilote du stockage. RWO = un nœud à la fois ; un PVC Pending vient presque toujours d'une StorageClass absente ou d'une zone différente de celle du Pod.")

# ---------------- 28 : Helm et Kustomize ----------------
f = Fig("helmkust", 480, 190, "Helm et Kustomize : deux façons de produire des manifests")
f.frame(4, 8, 230, 174, "Helm")
f.box(16, 36, 96, 40, "chart", 'soft', 11, sub="templates"); f.box(124, 36, 96, 40, "values.yaml", 'box', 11, sub="par environnement")
f.box(16, 100, 204, 34, "release (révision 1, 2, 3…)", 'green', 11); f.arrow(64, 76, 100, 100); f.arrow(172, 76, 140, 100)
f.text(118, 156, "rollback = révision précédente", fs=11); f.text(118, 170, "pour les paquets tiers", fs=11)
f.frame(246, 8, 230, 174, "Kustomize")
f.box(300, 36, 120, 40, "base/", 'soft', 11, sub="manifests communs")
f.box(258, 100, 96, 34, "overlays/dev", 'box', 11); f.box(366, 100, 96, 34, "overlays/prod", 'box', 11)
f.arrow(340, 76, 306, 100); f.arrow(380, 76, 414, 100)
f.text(360, 156, "patches, images, réplicas", fs=11); f.text(360, 170, "pour ses propres applications", fs=11)
add(L5, "28.1", f, "Helm rend un modèle avec des valeurs et garde l'historique des releases ; Kustomize empile des correctifs sur une base. Les deux sortent des manifests que Kubernetes applique ; ArgoCD sait lire les deux.")

# ---------------- 30 : service mesh ----------------
f = Fig("mesh", 480, 180, "Service mesh : plan de contrôle et plan de données")
f.box(160, 14, 160, 40, "plan de contrôle", 'purple', 12, sub="istiod : config, certificats, politiques")
for i,(n,x) in enumerate([("api",30),("notification",190),("incidents",350)]):
    f.frame(x, 84, 110, 80, None)
    f.box(x+8, 92, 94, 30, n, 'box', 11); f.box(x+8, 128, 94, 30, "proxy (sidecar)", 'soft', 10, sub=None)
    f.arrow(240, 54, x+55, 84, dashed=True)
f.arrow(140, 143, 190, 143, "mTLS", dy=-6); f.arrow(300, 143, 350, 143, "mTLS", dy=-6)
f.text(240, 176, "ambient : le proxy quitte le Pod (ztunnel par nœud) ; l'application ne change pas", fs=10)
add(L5, "30.1", f, "Le plan de contrôle distribue configuration, identités et certificats ; les proxies du plan de données chiffrent, authentifient, routent et mesurent chaque appel sans que l'application ne change. On l'adopte pour le mTLS et l'observabilité, on le paie en complexité.")

# ---------------- 31 : autoscaling ----------------
f = Fig("autoscale", 480, 175, "La boucle d'autoscaling, des métriques aux nœuds")
f.box(10, 30, 100, 46, "metrics-server", 'box', 11, sub="CPU, mémoire"); f.box(140, 30, 90, 46, "HPA", 'soft', 12, sub="cible : 70 % CPU"); f.box(260, 30, 100, 46, "Deployment", 'green', 11, sub="replicas 3 → 6"); f.box(390, 30, 80, 46, "Pods", 'box', 12, sub="Pending ?")
f.arrow(110, 53, 140, 53); f.arrow(230, 53, 260, 53); f.arrow(360, 53, 390, 53)
f.box(260, 110, 210, 46, "Cluster Autoscaler / Karpenter", 'amber', 11, sub="ajoute un nœud si Pending")
f.arrow(430, 76, 430, 110); f.arrow(260, 133, 60, 133, "les nouveaux Pods remontent des métriques", dy=-8); f.arrow(60, 133, 60, 76)
f.text(140, 160, "KEDA : à zéro et sur des files ; VPA : ajuste les requests", fs=11)
add(L5, "31.1", f, "Deux boucles emboîtées : l'HPA ajoute des Pods à partir des métriques ; quand ils ne trouvent plus de place, l'autoscaler de cluster ajoute des nœuds. Sans requests correctes, aucune des deux ne fonctionne.")

# ---------------- 32 : pipeline de logs ----------------
f = Fig("logs", 480, 150, "Le chemin d'une ligne de log")
f.box(10, 30, 100, 50, "application", 'box', 11, sub="JSON sur stdout"); f.box(140, 30, 100, 50, "agent", 'soft', 11, sub="Alloy, par nœud"); f.box(270, 30, 100, 50, "Loki", 'green', 12, sub="labels, rétention"); f.box(400, 30, 70, 50, "Grafana", 'box', 11, sub="LogQL")
f.arrow(110, 55, 140, 55); f.arrow(240, 55, 270, 55, "+ labels k8s", dy=-8); f.arrow(370, 55, 400, 55)
f.text(240, 110, '{"ts":"…","level":"ERROR","trace_id":"4f2c…","msg":"paiement refusé","user":"***"}', fs=10)
f.text(240, 132, "le trace_id relie le log à sa trace ; les données personnelles sont masquées à la source", fs=10)
add(L6, "32.1", f, "L'application écrit une ligne structurée sur sa sortie standard et ne sait rien de la suite ; l'agent enrichit et expédie ; Loki indexe quelques labels et stocke le reste. Peu de labels, un trace_id partout, jamais de donnée personnelle.")

# ---------------- 33 : Prometheus ----------------
f = Fig("prom", 480, 185, "Le modèle Prometheus : tirer, stocker, évaluer, alerter")
for i,(n) in enumerate(["api /metrics","db exporter","node exporter"]):
    f.box(10, 20+i*50, 100, 38, n, 'box', 11)
f.box(170, 40, 120, 70, "Prometheus", 'soft', 12, sub="scrape 15 s, TSDB, règles")
for i in range(3): f.arrow(170, 75, 110, 39+i*50, head=True)
f.text(140, 22, "pull", 'glab')
f.box(330, 20, 140, 40, "Alertmanager", 'red', 12, sub="regroupe, route, silence"); f.arrow(290, 60, 330, 45, "burn rate", dy=-8)
f.box(330, 80, 140, 40, "Grafana", 'green', 12, sub="PromQL, dashboards"); f.arrow(330, 100, 290, 90, head=True)
f.box(330, 140, 140, 34, "astreinte / ticket", 'box', 11); f.arrow(400, 60, 400, 140)
f.text(230, 165, "longue durée et HA : Thanos, Mimir, VictoriaMetrics", fs=10)
add(L6, "33.1", f, "Prometheus va chercher les métriques (pull), les stocke en séries temporelles, évalue des règles et confie les alertes à Alertmanager qui les regroupe et les route. Grafana ne fait que lire. Les labels à forte cardinalité sont l'ennemi.")

# ---------------- 36 : cycle d'un incident ----------------
f = Fig("incident", 480, 190, "Le cycle d'un incident et ses trois délais")
f.raw('<line x1="20" y1="70" x2="460" y2="70" class="axis"/>')
pts = [("panne",30),("détection",120),("prise en charge",210),("mitigation",320),("résolution",440)]
for n,x in pts:
    f.raw(f'<circle cx="{x}" cy="70" r="6" class="redfill"/>'); f.text(x, 96, n, fs=11)
f.arrow(30, 40, 120, 40, "MTTD", dy=-6); f.arrow(120, 40, 210, 40, "MTTA", dy=-6); f.arrow(210, 40, 440, 40, "MTTR (mitigation puis résolution)", dy=-6)
f.box(10, 115, 108, 40, "commandant", 'purple', 11, sub="décide, ne débogue pas"); f.box(128, 115, 108, 40, "opérations", 'soft', 11, sub="diagnostique, agit"); f.box(246, 115, 108, 40, "communication", 'green', 11, sub="statut à cadence fixe"); f.box(364, 115, 106, 40, "scribe", 'box', 11, sub="chronologie")
f.box(10, 165, 460, 22, "post-mortem sans blâme sous 5 jours → actions suivies → l'incident ne revient pas", 'amber', 11, bold=False, rx=5)
add(L6, "36.1", f, "On mesure séparément détecter, prendre en charge et réparer, parce que chacun s'améliore avec un levier différent : alertes de symptômes, astreinte outillée, rollback et runbooks. Les rôles évitent que tout le monde débogue et que personne ne communique.")

# ---------------- 37 : contrôles DevSecOps ----------------
f = Fig("devsecops", 480, 200, "Où chaque contrôle de sécurité s'exécute")
stages = [("IDE, pre-commit","secrets, lint"),("CI","SAST, SCA, IaC"),("build","scan image, SBOM, signature"),("registre","admission : signé ? digest ?"),("staging","DAST, tests de sécurité"),("production","Falco, posture, patchs")]
for i,(s_,c) in enumerate(stages):
    x = 6 + i*79
    f.box(x, 30, 72, 46, s_, 'soft', 11); f.text(x+36, 92, c.split(',')[0]+',', fs=10); f.text(x+36, 105, ','.join(c.split(',')[1:]).strip(), fs=10)
    if i < 5: f.arrow(x+72, 53, x+79, 53)
f.box(6, 130, 230, 50, ["bloquant : critique exploitable,", "secret, image non signée"], 'red', 11, bold=False)
f.box(246, 130, 228, 50, ["en observation puis ticket avec SLA :", "le reste, priorisé par EPSS et KEV"], 'amber', 11, bold=False)
f.text(240, 195, "un outil qui produit 200 alertes inexploitables est désactivé en une semaine : le bruit est l'ennemi", fs=10)
add(L7, "37.2", f, "Chaque contrôle a une place où il coûte le moins et arrête le plus : les secrets avant le commit, les dépendances à la CI, l'image au build, la signature à l'admission, le comportement à l'exécution. Bloquer peu, expliquer tout, mesurer le bruit.")

# ---------------- 39 : les 4C ----------------
f = Fig("fourc", 480, 200, "Les quatre couches de sécurité de Kubernetes")
f.raw('<rect x="10" y="10" width="460" height="180" rx="12" class="amber"/><rect x="60" y="40" width="360" height="140" rx="12" class="soft"/><rect x="110" y="70" width="260" height="100" rx="12" class="green"/><rect x="160" y="100" width="160" height="60" rx="12" class="box"/>')
f.text(240, 30, "Cloud : comptes, IAM, réseau, chiffrement, logs", fs=11, bold=True, cls='')
f.text(240, 60, "Cluster : API, RBAC, PSA, admission, NetworkPolicy, etcd", fs=11, bold=True, cls='')
f.text(240, 90, "Conteneur : image durcie, non root, lecture seule, scan, signature", fs=11, bold=True, cls='')
f.text(240, 125, "Code : entrées, secrets, dépendances", fs=11, bold=True, cls=''); f.text(240, 142, "OWASP Top 10, tests de sécurité", fs=10)
add(L7, "39.1", f, "Chaque couche protège la suivante ; une faille dans une couche externe rend les internes inutiles. On sécurise de l'extérieur vers l'intérieur, et on ne compte jamais sur une seule couche.")

# ---------------- 42 : chaîne de preuve ----------------
f = Fig("compliance", 480, 150, "De l'exigence à la preuve automatique")
f.box(10, 30, 90, 50, "exigence", 'box', 11, sub="ISO 27001 A.8.x"); f.box(120, 30, 90, 50, "politique", 'soft', 11, sub="une page"); f.box(230, 30, 90, 50, "implémentation", 'green', 11, sub="pipeline, config"); f.box(340, 30, 130, 50, "preuve automatique", 'amber', 11, sub="rapport, journal, signé")
f.arrow(100, 55, 120, 55); f.arrow(210, 55, 230, 55); f.arrow(320, 55, 340, 55)
f.box(120, 105, 210, 34, "auditeur : échantillons en minutes", 'purple', 11); f.arrow(405, 80, 300, 105)
f.text(60, 125, "collectée chaque mois", fs=10); f.text(60, 138, "par script, versionnée", fs=10)
add(L7, "42.1", f, "Une exigence devient une politique courte, une implémentation dans les outils, et une preuve produite par les systèmes eux-mêmes. La conformité cesse d'être une campagne annuelle de captures d'écran : elle est un sous-produit du pipeline.")

# ---------------- 43 : contrat SRE ----------------
f = Fig("srecontract", 480, 190, "Qui est responsable de quoi : équipe produit, SRE, plateforme")
f.box(10, 20, 146, 120, ["équipe produit", "", "code et fiabilité", "de son service,", "astreinte, SLO,", "post-mortems"], 'box', 11, bold=False)
f.box(167, 20, 146, 120, ["SRE", "", "standards, SLO", "de la plateforme,", "revue de lancement,", "incidents majeurs, toil"], 'purple', 11, bold=False)
f.box(324, 20, 146, 120, ["plateforme", "", "capacités en", "libre-service :", "SLO as code, canary,", "sauvegardes, incidents"], 'green', 11, bold=False)
f.text(83, 36, "équipe produit", fs=12, bold=True, cls=''); f.text(240, 36, "SRE", fs=12, bold=True, cls=''); f.text(397, 36, "plateforme", fs=12, bold=True, cls='')
f.arrow(156, 80, 167, 80, head=True); f.arrow(313, 80, 324, 80, head=True)
f.box(10, 152, 460, 30, "contrat : prise en charge si revue de lancement passée et budget d'erreur respecté ; retour si toil ou incidents insoutenables", 'amber', 10, bold=False, rx=5)
add(L8, "43.1", f, "La responsabilité d'un service reste à l'équipe qui l'écrit ; la SRE fixe les standards et tient la plateforme ; la plateforme rend la fiabilité disponible sans ticket. Le contrat écrit évite l'exploitation subie.")

# ---------------- 45 : où part le temps ----------------
f = Fig("latency", 480, 190, "Où part le temps d'une requête (p95, exemple)")
segs = [("DNS + TLS",25,'box'),("équilibreur",10,'box'),("API : code",40,'soft'),("base : requête",60,'amber'),("appel externe",120,'red'),("sérialisation",15,'box')]
x = 20; tot = sum(v for _,v,_ in segs); scale = 440/tot
for n,v,c in segs:
    w = v*scale
    f.raw(f'<rect x="{x:.1f}" y="40" width="{w:.1f}" height="34" class="{c}"/>')
    f.text(x+w/2, 62, f"{v} ms", fs=10, cls='')
    f.text(x+w/2, 92 if segs.index((n,v,c))%2==0 else 106, n, fs=10)
    x += w
f.text(240, 24, f"total ≈ {tot} ms : la moitié dans un appel externe sans cache ni timeout", fs=11, bold=True, cls='')
f.box(20, 125, 440, 26, "mesurer d'abord (traces), corriger le plus gros segment, remesurer", 'green', 11, bold=False, rx=5)
f.text(240, 172, "leviers par segment : cache, index, connexions persistantes, appels parallèles, timeouts, CDN", fs=10)
add(L8, "45.1", f, "Une trace montre la répartition ; l'optimisation commence par le segment le plus large, pas par celui qu'on connaît le mieux. La moyenne cache tout : on regarde le p95 et le p99.")

# ---------------- 47 : expand / contract ----------------
f = Fig("expand", 480, 175, "Migration de schéma sans interruption : expand, migrate, contract")
ph = [("1. expand","ajoute la colonne, nullable ; le code v1 l'ignore",'soft'),("2. migrate","le code v2 écrit les deux, un lot remplit l'ancien stock",'green'),("3. switch","le code v3 lit la nouvelle colonne ; rollback encore possible",'green'),("4. contract","supprime l'ancienne colonne, plus tard",'amber')]
for i,(t,d,c) in enumerate(ph):
    y = 14 + i*38
    f.box(10, y, 110, 30, t, c, 11); f.text(130, y+19, d, fs=11, anchor='start')
f.text(240, 168, "chaque étape est un déploiement compatible avec le précédent ; lock_timeout, index concurrents, lots", fs=10)
add(L8, "47.2", f, "Jamais de changement de schéma en une seule fois : on ajoute, on migre, on bascule, on retire, chaque étape étant compatible avec le code précédent. Le rollback du code suffit alors à tout moment.")

# ---------------- 49 : landing zone ----------------
f = Fig("lz", 480, 200, "Une landing zone AWS : organisation, unités, comptes")
f.box(180, 12, 120, 34, "Organisation", 'purple', 12, sub="SCP, facturation")
ous = [("Sécurité",30),("Infrastructure",140),("Charges de travail",250),("Bac à sable",380)]
for n,x in ous:
    f.box(x, 70, 90 if n!="Charges de travail" else 110, 32, n, 'soft', 11); f.arrow(240, 46, x+45, 70, head=True)
accs = [("log archive",30,'box'),("audit",80,'box'),("réseau",140,'box'),("outillage CI",190,'box'),("dev",250,'green'),("staging",300,'green'),("prod",350,'amber'),("perso",380,'box')]
for n,x,c in accs:
    f.box(x, 125, 46 if n not in ("log archive","outillage CI") else 48, 34, n, c, 9)
for x in (30,80,140,190,250,300,350,380):
    f.arrow(x+23, 102, x+23, 125, head=False)
f.text(240, 185, "Identity Center + SSO pour les humains, rôles pour les charges, CloudTrail centralisé, budgets par compte", fs=10)
add(L9, "49.1", f, "Un compte est une frontière de sécurité et de facturation : un par environnement et par domaine, groupés en unités où s'appliquent les garde-fous (SCP). Sécurité et journaux vivent dans des comptes que personne d'autre n'écrit.")

# ---------------- 50 : arbre des 7 R ----------------
f = Fig("sevenr", 480, 200, "Les 7 R : l'arbre de décision par application")
f.box(160, 10, 160, 32, "l'application sert-elle encore ?", 'soft', 11)
f.box(20, 60, 100, 30, "non → Retire", 'amber', 11); f.arrow(200, 42, 70, 60)
f.box(200, 60, 160, 32, "un SaaS équivalent existe ?", 'soft', 11); f.arrow(280, 42, 280, 60)
f.box(380, 60, 90, 30, "oui → Repurchase", 'amber', 11); f.arrow(360, 76, 380, 76)
f.box(200, 110, 160, 32, "vaut-elle un investissement ?", 'soft', 11); f.arrow(280, 92, 280, 110)
f.box(20, 110, 130, 30, "non → Rehost / Relocate", 'green', 10); f.arrow(200, 126, 150, 126)
f.box(380, 110, 90, 30, "oui → Refactor", 'red', 11); f.arrow(360, 126, 380, 126)
f.box(200, 160, 160, 32, "entre les deux → Replatform", 'green', 11); f.arrow(280, 142, 280, 160)
f.text(70, 175, "Retain : pas maintenant,", fs=10); f.text(70, 188, "décision datée", fs=10)
add(L9, "50.1", f, "Quatre questions par application, dans cet ordre, et une réponse par lot. Le résultat réaliste d'un portefeuille : beaucoup de replatform et de rehost, peu de refactor, et un tiers de retire que personne n'avait vu.")

# ---------------- 51 : gouvernance ----------------
f = Fig("gov", 480, 140, "De la décision technique à la règle appliquée")
f.box(10, 30, 90, 50, "RFC", 'box', 11, sub="proposition"); f.box(120, 30, 90, 50, "revue", 'soft', 11, sub="commentaires, délai"); f.box(230, 30, 90, 50, "ADR", 'green', 11, sub="décision datée"); f.box(340, 30, 130, 50, "politique as code", 'amber', 11, sub="OPA, Kyverno, CI")
f.arrow(100, 55, 120, 55); f.arrow(210, 55, 230, 55); f.arrow(320, 55, 340, 55)
f.text(240, 115, "les exceptions sont écrites, datées, revues ; la règle sans outil est un vœu", fs=11)
add(L9, "51.1", f, "Une décision se propose, se discute, se consigne, puis s'applique par un outil plutôt que par une revue humaine. Ce qui n'est pas dans le code de politique n'est pas une règle, c'est une préférence.")

# ---------------- 52 : chaîne de mesure DORA ----------------
f = Fig("dora", 480, 150, "D'où viennent les métriques DORA")
f.box(10, 20, 100, 40, "Git", 'box', 11, sub="commits, MR"); f.box(10, 70, 100, 40, "CI/CD", 'box', 11, sub="déploiements"); f.box(10, 120, 100, 26, "incidents", 'box', 11)
f.box(170, 45, 130, 60, "collecteur", 'soft', 12, sub="DevLake, script, API"); f.arrow(110, 40, 170, 65); f.arrow(110, 90, 170, 80); f.arrow(110, 133, 170, 95)
f.box(340, 20, 130, 46, "quatre métriques", 'green', 11, sub="par équipe, par mois"); f.box(340, 90, 130, 46, "décision", 'amber', 11, sub="revue mensuelle")
f.arrow(300, 65, 340, 43); f.arrow(405, 66, 405, 90)
add(L9, "52.1", f, "Les métriques sortent des systèmes, jamais de saisies : un commit horodaté, un déploiement horodaté, un incident horodaté suffisent. Elles servent à décider quelque chose chaque mois ; sans décision, ce sont des graphiques.")

# ---------------- 53 : Team Topologies ----------------
f = Fig("topo", 480, 190, "Team Topologies : quatre types d'équipes")
for i,n in enumerate(["équipe flux : incidents","équipe flux : notifications","équipe flux : cartographie"]):
    f.box(10+i*128, 20, 118, 44, n.split(':')[0].strip(), 'box', 11, sub=n.split(':')[1].strip())
f.box(400, 20, 70, 44, "sous-système", 'purple', 10, sub="complexe")
f.box(10, 110, 380, 44, "équipe plateforme : ce que les équipes flux consomment en libre-service", 'green', 11)
for i in range(3): f.arrow(69+i*128, 64, 69+i*128, 110, dashed=True)
f.box(400, 110, 70, 44, "habilitante", 'amber', 10, sub="temporaire")
f.arrow(400, 132, 390, 132, head=True); f.arrow(435, 110, 435, 64, dashed=True)
f.text(240, 178, "modes d'interaction : collaboration (courte), X-as-a-service (durable), facilitation (temporaire)", fs=10)
add(L9, "53.2", f, "Les équipes alignées sur un flux livrent de la valeur ; la plateforme réduit leur charge cognitive ; l'équipe habilitante fait monter en compétence puis s'efface. La SRE est une plateforme ou une équipe habilitante, jamais un goulot.")

# ---------------- 54 : application LLM ----------------
f = Fig("llmapp", 480, 210, "Architecture d'une application LLM en production")
f.box(10, 20, 90, 40, "utilisateur", 'box', 11); f.box(130, 20, 220, 40, "application (Spring AI, LangChain4j)", 'soft', 11, sub="garde-fous d'entrée, prompt, validation de sortie")
f.arrow(100, 40, 130, 40)
f.box(380, 20, 90, 40, "sources", 'green', 11, sub="citées"); f.arrow(350, 40, 380, 40)
f.box(130, 80, 100, 44, "récupération", 'green', 11, sub="pgvector + BM25"); f.box(250, 80, 100, 44, "droits d'accès", 'red', 11, sub="filtre avant classement"); f.arrow(240, 60, 180, 80); f.arrow(230, 102, 250, 102)
f.box(130, 145, 220, 40, "passerelle LLM", 'purple', 11, sub="auth, quotas, journal, coût, cache, routage"); f.arrow(240, 124, 240, 145)
f.box(380, 145, 90, 40, "modèle", 'box', 11, sub="API ou vLLM"); f.arrow(350, 165, 380, 165)
f.box(10, 145, 100, 40, "evals en CI", 'amber', 10, sub="30 cas, seuil"); f.arrow(110, 165, 130, 165, dashed=True)
f.text(240, 202, "traces OpenTelemetry par requête : récupération, prompt, appel, validation, tokens, coût", fs=10)
add(L9, "54.8", f, "Le modèle est une brique parmi huit : la récupération filtrée par les droits, la validation de sortie, la passerelle et l'évaluation continue font la différence entre une démonstration et un produit.")

# ============ insertion ============
by_file = {}
for lvl, sec, svg in FIGS: by_file.setdefault(lvl, []).append((sec, svg))
for fn, items in by_file.items():
    p = out/fn; s = p.read_text(); n = 0
    for sec, svg in items:
        m = re.search(r'<h3>' + re.escape(sec) + r' [^<]*(?:<span class="badge[^<]*</span>)?</h3>', s)
        assert m, (fn, sec)
        # ne pas doubler
        if 'aria-label="' + H.escape(re.search(r'aria-label="([^"]+)"', svg).group(1)) + '"' in s: continue
        s = s[:m.end()] + '\n' + svg + s[m.end():]; n += 1
    p.write_text(s); print(fn, n, 'schémas ajoutés')
print('total', len(FIGS))
