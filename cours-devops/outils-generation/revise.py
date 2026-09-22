import re, pathlib, html

# ---------- Générateur de schémas SVG ----------
_mid = [0]
def fig(w, h, body, cap):
    _mid[0] += 1; m = f"ah{_mid[0]}"
    body = body.replace("url(#ah)", f"url(#{m})")
    return (f'<figure class="fig"><svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(cap)}">'
            f'<defs><marker id="{m}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" class="ahead"/></marker></defs>{body}</svg><figcaption>{cap}</figcaption></figure>')

def box(x, y, w, h, lines, cls="box", fs=14, sub=None):
    if isinstance(lines, str): lines = [lines]
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" class="{cls}"/>'
    n = len(lines) + (1 if sub else 0)
    lh = fs + 4
    y0 = y + h/2 - (n-1)*lh/2 + fs*0.35
    for i, t in enumerate(lines):
        out += f'<text x="{x+w/2}" y="{y0+i*lh:.1f}" text-anchor="middle" font-size="{fs}" font-weight="700">{html.escape(t)}</text>'
    if sub:
        out += f'<text x="{x+w/2}" y="{y0+len(lines)*lh:.1f}" text-anchor="middle" class="lbl">{html.escape(sub)}</text>'
    return out

def arrow(x1, y1, x2, y2, label=None, dx=0, dy=-6):
    out = f'<path d="M{x1},{y1} L{x2},{y2}" class="arrow" marker-end="url(#ah)"/>'
    if label:
        out += f'<text x="{(x1+x2)/2+dx}" y="{(y1+y2)/2+dy}" text-anchor="middle" class="lbl">{html.escape(label)}</text>'
    return out

def txt(x, y, t, cls="lbl", anchor="start", fs=None):
    f = f' font-size="{fs}"' if fs else ""
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}"{f}>{html.escape(t)}</text>'

def group_label(x, y, t):
    return f'<text x="{x}" y="{y}" class="glab">{html.escape(t)}</text>'

FIGS = {}

# 1 — DORA : vitesse et stabilité montent ensemble
b = ''
b += f'<rect x="10" y="30" width="220" height="140" rx="10" class="frame"/>' + group_label(20, 22, "Vitesse")
b += box(20, 45, 200, 50, ["Fréquence de déploiement"], "soft", 13)
b += box(20, 105, 200, 50, ["Délai commit → production"], "soft", 13)
b += f'<rect x="250" y="30" width="220" height="140" rx="10" class="frame"/>' + group_label(260, 22, "Stabilité")
b += box(260, 45, 200, 50, ["Taux d'échec des changements"], "green", 13)
b += box(260, 105, 200, 50, ["Temps de rétablissement"], "green", 13)
FIGS[1] = fig(480, 167, b, "Les métriques DORA : deux mesures de vitesse, deux de stabilité, qui progressent ensemble. Les équipes performantes améliorent les quatre en même temps : ce n'est pas un compromis.")

# 3 — le parcours d'une requête HTTPS
b = ''
steps = [("DNS","nom → IP"),("TCP","poignée de main"),("TLS","certificat, clé"),("HTTP","GET /users"),("Réponse","200, JSON")]
for i,(t,s) in enumerate(steps):
    x = 10 + i*94
    b += box(x, 30, 84, 60, [t], "soft" if i<3 else "green", 14, s)
    if i < 4: b += arrow(x+84, 60, x+94, 60)
FIGS[3] = fig(480, 120, b, "Ce qui se passe quand tu tapes une URL HTTPS, et où chercher quand ça casse. Chaque étape peut échouer séparément : « Could not resolve » (DNS), « Connection refused » (TCP), « certificate » (TLS), 4xx/5xx (HTTP). On diagnostique de gauche à droite.")

# 5 — les trois zones de Git
b = box(10, 40, 140, 60, ["Répertoire", "de travail"], "box", 14) + box(170, 40, 140, 60, ["Index", "(staging)"], "soft", 14) + box(330, 40, 140, 60, ["Dépôt", "(.git)"], "green", 14)
b += arrow(150, 60, 170, 60, "git add", 0, -10) + arrow(310, 60, 330, 60, "git commit", 0, -10)
b += f'<path d="M400,100 C400,140 80,140 80,100" class="arrow" marker-end="url(#ah)"/>' + txt(240, 150, "git restore / git switch (revenir en arrière)", "lbl", "middle")
FIGS[5] = fig(480, 152, b, "Les trois zones de Git et les commandes qui font passer d'une zone à l'autre. Une branche = un fichier de 41 octets qui contient le hash d'un commit. HEAD pointe sur la branche courante.")

# 7 — VM contre conteneur
b = group_label(20, 22, "Machine virtuelle") + group_label(260, 22, "Conteneur")
for i,(t,c) in enumerate([("Application","green"),("OS invité + son noyau","amber"),("Hyperviseur","box"),("Matériel","box")]):
    b += box(20, 32+i*46, 200, 40, [t], c, 13)
for i,(t,c) in enumerate([("Application (processus isolé)","green"),("Runtime (containerd)","box"),("Noyau de l'hôte, partagé","amber"),("Matériel","box")]):
    b += box(260, 32+i*46, 200, 40, [t], c, 13)
FIGS[7] = fig(480, 207, b, "Une VM embarque son noyau ; un conteneur est un processus isolé par le noyau de l'hôte. Isolation : namespaces (ce qu'on voit), cgroups (ce qu'on consomme), couches (ce qu'on stocke).")

# 8 — couches d'une image
b = group_label(20, 22, "Image (lecture seule)")
layers = [("FROM eclipse-temurin:21-jre-alpine","soft"),("RUN adduser app","soft"),("COPY app.jar","soft")]
for i,(t,c) in enumerate(layers):
    b += box(20, 32+i*44, 300, 38, [t], c, 12)
b += box(20, 170, 300, 38, ["Couche d'écriture du conteneur (perdue au rm)"], "amber", 12)
b += txt(340, 55, "mise en cache tant que", "lbl") + txt(340, 71, "l'instruction et son", "lbl") + txt(340, 87, "contexte ne changent pas", "lbl")
b += arrow(335, 120, 335, 80) + txt(340, 150, "un changement ici", "lbl") + txt(340, 166, "reconstruit tout", "lbl") + txt(340, 182, "ce qui est en dessous", "lbl")
FIGS[8] = fig(480, 207, b, "Une image est une pile de couches ; l'ordre des instructions décide du cache et de la taille. Ce qui change le moins va en premier. Un fichier supprimé dans une couche suivante reste dans l'image.")

# 11 — anatomie d'un pipeline
b = ''
row1 = [("build","compile"),("test","unit, lint"),("package","image"),("scan","Trivy, SAST")]
for i,(t,s) in enumerate(row1):
    x = 10 + i*118
    b += box(x, 30, 105, 56, [t], "soft", 14, s)
    if i<3: b += arrow(x+105, 58, x+118, 58)
row2 = [("deploy staging","auto"),("tests e2e","smoke, contrat"),("deploy prod","manuel ou auto")]
b += f'<path d="M420,86 L420,105 L62,105 L62,118" class="arrow" marker-end="url(#ah)"/>'
for i,(t,s) in enumerate(row2):
    x = 10 + i*160
    b += box(x, 120, 145, 56, [t], "green" if i<2 else "amber", 14, s)
    if i<2: b += arrow(x+145, 148, x+160, 148)
FIGS[11] = fig(480, 174, b, "Un pipeline type : feedback rapide d'abord, puis l'image unique promue d'environnement en environnement. Une seule image, construite une fois, identifiée par digest, promue de staging à prod.")

# 15 — blue/green et canary
b = group_label(20, 22, "Blue/green : on bascule 100 % du trafic")
b += box(20, 32, 90, 44, ["Proxy"], "box", 13) + box(150, 32, 100, 44, ["Blue v1"], "soft", 13) + box(150, 86, 100, 44, ["Green v2"], "green", 13)
b += arrow(110, 54, 150, 54, "100 %", 0, -8) + f'<path d="M110,58 L150,104" class="arrow dashed" marker-end="url(#ah)"/>' + txt(120, 118, "bascule", "lbl")
b += txt(270, 60, "Rollback : rebasculer", "lbl") + txt(270, 76, "sur blue, en secondes.", "lbl")
b += group_label(20, 156, "Canary : on augmente progressivement")
b += box(20, 166, 90, 44, ["Proxy"], "box", 13) + box(150, 166, 100, 44, ["v1"], "soft", 13) + box(150, 220, 100, 44, ["v2"], "green", 13)
b += arrow(110, 184, 150, 184, "90 %", 0, -8) + arrow(110, 192, 150, 238, "10 %", 30, 6)
b += txt(270, 190, "10 → 50 → 100 % si les", "lbl") + txt(270, 206, "métriques restent bonnes.", "lbl") + txt(270, 222, "Sinon : couper le canari.", "lbl")
FIGS[15] = fig(480, 242, b, "Blue/green pour un rollback instantané ; canary pour valider sur du trafic réel.")

# 16 — code, state, réalité
b = box(170, 20, 140, 50, ["Code (.tf)", "ce que je veux"], "soft", 13) + box(20, 140, 160, 50, ["State", "ce que Terraform croit"], "amber", 13) + box(300, 140, 160, 50, ["Réalité (API cloud)", "ce qui existe"], "green", 13)
b += arrow(200, 70, 110, 140, "plan = diff", -30, -4) + arrow(280, 70, 370, 140, "apply", 30, -4) + arrow(180, 165, 300, 165, "refresh", 0, -8)
FIGS[16] = fig(480, 190, b, "Terraform compare trois choses : le code, le state, la réalité. Le state contient les identifiants réels et des secrets : distant, chiffré, verrouillé, jamais commité.")

# 19 — push contre pull
b = group_label(20, 22, "Push (CI classique)") + group_label(260, 22, "Pull (GitOps)")
b += box(20, 32, 80, 44, ["Git"], "soft", 13) + box(120, 32, 80, 44, ["CI"], "box", 13) + box(20, 110, 180, 60, ["Cluster / cloud"], "green", 13)
b += arrow(100, 54, 120, 54) + arrow(160, 76, 110, 110, "identifiants prod", 40, 10)
b += box(260, 32, 80, 44, ["Git"], "soft", 13) + box(260, 110, 200, 60, ["Cluster"], "green", 13) + box(360, 122, 90, 36, ["agent"], "purple", 12)
b += arrow(405, 122, 320, 76, "lit, réconcilie", 45, 4)
FIGS[19] = fig(480, 174, b, "Push : le pipeline déploie avec des identifiants. Pull : un agent dans le cluster lit Git. En pull, la CI n'a qu'un accès Git ; le cluster ne s'expose pas ; la dérive est corrigée en continu ; rollback = revert.")

# 21 — VPC sur trois zones
b = box(20, 10, 440, 30, ["Internet Gateway"], "box", 13)
for i,z in enumerate("abc"):
    x = 20 + i*150
    b += group_label(x, 60, f"AZ {z}")
    b += box(x, 66, 140, 40, ["public : ALB, NAT"], "soft", 12)
    b += box(x, 114, 140, 40, ["privé : ECS, EKS"], "green", 12)
    b += box(x, 162, 140, 40, ["données : RDS"], "amber", 12)
b += arrow(240, 40, 240, 66)
FIGS[21] = fig(480, 202, b, "Le VPC de production : trois zones, trois niveaux de sous-réseaux. Seul le public a une route vers Internet ; le privé sort par la NAT ou des endpoints ; les données ne sortent jamais.")

# 25 — architecture Kubernetes
b = f'<rect x="10" y="30" width="230" height="190" rx="10" class="frame"/>' + group_label(20, 22, "Control plane")
for i,t in enumerate(["kube-apiserver (tout passe par lui)","etcd (l'état)","scheduler (choisit un nœud)","controller-manager (les boucles)"]):
    b += box(20, 40+i*44, 210, 36, [t], "soft", 11)
b += f'<rect x="260" y="30" width="210" height="190" rx="10" class="frame"/>' + group_label(270, 22, "Nœud (× N)")
for i,t in enumerate(["kubelet (fait tourner les Pods)","containerd (lance les conteneurs)","kube-proxy / CNI (réseau)","Pods"]):
    b += box(270, 40+i*44, 190, 36, [t], "green" if i==3 else "box", 11)
b += arrow(230, 58, 270, 58)
FIGS[25] = fig(480, 220, b, "Les composants de Kubernetes et qui parle à qui. kubectl parle à l'API ; les contrôleurs rapprochent en boucle l'état réel de l'état désiré.")

# 26 — Deployment → ReplicaSet → Pods, Service, Ingress
b = box(20, 20, 130, 44, ["Ingress"], "purple", 13, "hôte, chemin, TLS") + arrow(85, 64, 85, 96)
b += box(20, 96, 130, 44, ["Service"], "soft", 13, "IP stable, DNS")
for i in range(3):
    b += box(20+i*45, 176, 40, 40, ["Pod"], "green", 12)
    b += arrow(85, 140, 40+i*45, 176)
b += box(300, 20, 160, 44, ["Deployment"], "amber", 13, "réplicas, stratégie") + arrow(380, 64, 380, 96)
b += box(300, 96, 160, 44, ["ReplicaSet"], "amber", 13, "maintient N Pods") + arrow(380, 140, 150, 196)
FIGS[26] = fig(480, 220, b, "Comment une requête arrive à un Pod, et qui maintient les Pods en vie. Le Service route vers les Pods prêts (readiness) ; le Deployment crée un ReplicaSet par version.")

# 29 — flux GitOps avec promotion
b = box(10, 30, 100, 50, ["Dépôt code"], "soft", 13) + arrow(110, 55, 130, 55) + box(130, 30, 80, 50, ["CI"], "box", 13) + arrow(210, 55, 230, 55)
b += box(230, 30, 110, 50, ["Registre"], "box", 13, "image@digest") + arrow(285, 80, 285, 110)
b += box(200, 110, 170, 50, ["Dépôt config : staging"], "amber", 12) + arrow(370, 135, 400, 135, "MR", 0, -8) + box(400, 110, 70, 50, ["prod"], "amber", 12)
b += box(200, 190, 170, 44, ["ArgoCD réconcilie"], "purple", 13) + arrow(285, 160, 285, 190) + arrow(435, 160, 340, 190)
FIGS[29] = fig(480, 234, b, "Du commit à la production en GitOps : promotion par merge request. La CI ne touche jamais le cluster : elle écrit un digest dans Git. La prod attend une merge request revue.")

# 34 — les trois signaux corrélés
b = box(20, 30, 130, 60, ["Logs"], "soft", 14, "événements") + box(175, 30, 130, 60, ["Métriques"], "green", 14, "agrégats") + box(330, 30, 130, 60, ["Traces"], "purple", 14, "parcours d'une requête")
b += arrow(150, 60, 175, 60) + arrow(305, 60, 330, 60) + txt(162, 48, "trace_id", "lbl", "middle") + txt(318, 48, "exemplars", "lbl", "middle")
b += arrow(85, 90, 220, 140) + arrow(240, 90, 240, 140) + arrow(395, 90, 260, 140)
b += box(150, 140, 180, 44, ["Grafana / OpenTelemetry"], "box", 13)
FIGS[34] = fig(480, 184, b, "Les trois signaux ne valent que reliés : trace_id dans les logs, exemplars dans les métriques. Depuis une alerte de latence : exemplar → trace → logs de cette trace → Pod et sa mémoire. En quatre clics.")

# 35 — budget d'erreur
b = group_label(20, 22, "SLO 99,9 % sur 30 jours = 43 min de budget")
b += f'<rect x="20" y="34" width="440" height="34" rx="6" class="frame"/>'
b += f'<rect x="20" y="34" width="290" height="34" rx="6" class="redfill"/>'
b += txt(165, 56, "consommé : 29 min", "lblw", "middle") + txt(385, 56, "reste : 14 min", "lbl", "middle")
b += box(20, 92, 210, 56, ["Burn rate 14 ×"], "red", 13, "budget épuisé en 2 jours → page") + box(250, 92, 210, 56, ["Burn rate 1 ×"], "amber", 13, "épuisé pile à 30 jours → ticket")
FIGS[35] = fig(480, 152, b, "Le budget d'erreur se dépense ; le burn rate dit s'il faut réveiller quelqu'un. On alerte sur la vitesse à laquelle le budget brûle (symptôme), pas sur le CPU (cause).")

# 38 — Vault et les secrets dynamiques
b = box(10, 40, 110, 56, ["Pod API"], "green", 13, "token de SA") + arrow(120, 68, 150, 68, "1. auth", 0, -8)
b += box(150, 40, 110, 56, ["Vault"], "purple", 13, "politique, TTL 1 h") + arrow(260, 68, 290, 68, "2. crée", 0, -8)
b += box(290, 40, 170, 56, ["PostgreSQL"], "amber", 13, "rôle temporaire v-kube-…")
b += f'<path d="M345,96 L345,130 L65,130 L65,96" class="arrow dashed" marker-end="url(#ah)"/>' + txt(205, 146, "3. l'API se connecte avec des identifiants qui expirent et sont révocables", "lbl", "middle")
FIGS[38] = fig(480, 150, b, "Un secret dynamique : créé à la demande, lié à une instance, révoqué à l'expiration. Hiérarchie : supprimer le secret (identité) > dynamique > statique centralisé et tourné > chiffré dans Git.")

# 40 — chaîne d'approvisionnement
b = ''
steps = [("Source","MR revue"),("Build","runner éphémère"),("Attester","SBOM, provenance"),("Signer","Sigstore keyless"),("Admission","Kyverno vérifie")]
for i,(t,s) in enumerate(steps):
    x = 10 + i*94
    b += box(x, 30, 84, 60, [t], "soft" if i<4 else "green", 13, s)
    if i<4: b += arrow(x+84, 60, x+94, 60)
FIGS[40] = fig(480, 120, b, "De la source au cluster : chaque étape produit une preuve vérifiée à la suivante. Trois questions à tout artefact : d'où vient-il ? a-t-il été modifié ? que contient-il ? Le déploiement référence le digest vérifié, jamais un tag.")

# 41 — zero trust
b = box(10, 40, 100, 56, ["Humain +", "appareil"], "box", 12) + arrow(110, 68, 130, 68, "MFA", 0, -8)
b += box(130, 40, 90, 56, ["IdP"], "purple", 13, "Keycloak") + arrow(220, 68, 240, 68, "jeton court", 0, -8)
b += box(240, 40, 100, 56, ["Service"], "green", 13, "SPIFFE, mTLS") + arrow(340, 68, 360, 68, "identité", 0, -8)
b += box(360, 40, 110, 56, ["Base / secrets"], "amber", 13, "par identité")
FIGS[41] = fig(480, 120, b, "Zero trust : vérifier à chaque saut, pour les humains comme pour les charges de travail. Chaque saut est authentifié, autorisé, chiffré, journalisé, de courte durée. Pas de confiance implicite au réseau : « à l'intérieur » n'existe plus.")

# 44 — stratégies de reprise
b = f'<path d="M30,150 L450,150" class="axis"/>' + txt(450, 168, "coût ↑", "lbl", "end") + txt(30, 168, "RTO / RPO ↓", "lbl")
for i,(t,s,c) in enumerate([("Sauvegarde","heures, ×1","box"),("Pilot light","minutes, ×2","soft"),("Warm standby","secondes, ×4","green"),("Actif-actif","≈ 0, ×8+","amber")]):
    x = 30 + i*108
    b += box(x, 30+ (3-i)*22, 100, 56, [t], c, 12, s)
FIGS[44] = fig(480, 168, b, "Quatre stratégies de reprise : plus le RTO/RPO baisse, plus le coût monte. Le RTO/RPO se décide avec le métier, en euros. Les données sont le vrai sujet du multi-région.")

# 46 — outbox transactionnel
b = box(10, 40, 90, 56, ["API"], "green", 13) + arrow(100, 68, 120, 68)
b += f'<rect x="120" y="24" width="170" height="88" rx="8" class="frame"/>' + group_label(128, 18, "Une seule transaction")
b += box(130, 34, 150, 32, ["INSERT incident"], "amber", 12) + box(130, 72, 150, 32, ["INSERT outbox"], "amber", 12)
b += arrow(290, 88, 320, 88) + box(320, 60, 70, 56, ["Debezium"], "purple", 12) + arrow(390, 88, 410, 88) + box(410, 60, 60, 56, ["Kafka"], "box", 12)
FIGS[46] = fig(480, 138, b, "L'outbox transactionnel : l'événement et la donnée sont écrits atomiquement. Base OK et Kafka KO ? Rien n'est perdu : l'outbox sera relue. Kafka OK et base rollback ? Impossible. Le consommateur est idempotent : recevoir deux fois n'est pas un problème.")

# 48 — plateforme interne
b = box(20, 20, 440, 40, ["Développeur : « un service Java avec une base et un topic »"], "green", 13) + arrow(240, 60, 240, 74)
b += box(20, 74, 440, 40, ["Portail (Backstage) : templates, catalogue, scorecards, docs"], "purple", 13) + arrow(240, 114, 240, 128)
b += box(20, 128, 440, 40, ["Golden paths : pipeline, GitOps, observabilité, sécurité par défaut"], "soft", 13) + arrow(240, 168, 240, 182)
b += box(20, 182, 440, 40, ["Plateforme : Kubernetes, Crossplane, politiques, secrets, landing zone"], "amber", 13)
FIGS[48] = fig(480, 224, b, "L'Internal Developer Platform : ce que le développeur demande, ce que la plateforme fait. La plateforme est un produit : des utilisateurs, une adoption mesurée, des chemins recommandés, pas une cage.")

# ---------- Résumés « En 30 secondes » ----------
BREF = {
1:["Le DevOps répare un problème d'organisation : Dev et Ops avaient des objectifs contradictoires.","CALMS et les Three Ways en sont la grammaire ; DORA en est la mesure.","Ce n'est pas un poste ni une liste d'outils : en entretien, parle culture, pratiques, mesure."],
2:["Tout est fichier, tout est processus : navigation, permissions, signaux, redirections.","La méthode de diagnostic (uptime, free, df, ss, journalctl) vaut plus que la liste des commandes.","En conteneur, PID 1 doit gérer SIGTERM, sinon Docker tue au bout de 10 s."],
3:["Une requête traverse DNS, TCP, TLS, HTTP : on diagnostique dans cet ordre.","Le CIDR, les ports et les codes HTTP se savent par cœur ; le 502 vient du reverse proxy.","TLS chiffre et authentifie : un certificat auto-signé chiffre mais ne prouve rien."],
4:["Bash pour enchaîner des commandes, avec set -euo pipefail et shellcheck ; Python dès qu'il y a de la logique.","Un script sérieux a des arguments, des codes de retour, des logs et un nettoyage (trap).","Tester ses scripts (Bats, pytest) distingue l'exploitation de la bidouille."],
5:["Git stocke des instantanés ; une branche est un pointeur ; le reflog est le filet de sécurité.","Rebase sur sa branche locale, merge ou squash pour intégrer, revert (jamais reset) sur main.","Conventional Commits et branches protégées automatisent versions et revues."],
6:["ACID, index et EXPLAIN pour le relationnel ; NoSQL seulement quand PostgreSQL plafonne.","Les migrations de schéma sont versionnées et compatibles N-1 (expand/contract).","Les 12 facteurs sont le contrat entre l'application et son exploitant."],
7:["Un conteneur n'est pas une petite VM : namespaces, cgroups, couches, noyau partagé.","Le noyau partagé est l'enjeu de sécurité ; micro-VM (Firecracker) et gVisor pour l'isolation forte.","Sous Windows, Docker tourne dans une VM WSL 2 : chemins, performances et fins de ligne en découlent."],
8:["Le cache de build suit l'ordre des instructions : ce qui change le moins en premier.","Multi-étapes, base minimale, non root, lecture seule, capabilities retirées, versions épinglées.","Déboguer : logs, inspect (ExitCode, OOMKilled), entrypoint sh, netshoot ; 137 = SIGKILL, 143 = SIGTERM."],
9:["Compose décrit une pile complète : services, réseaux, volumes, secrets, healthchecks.","depends_on n'attend pas la disponibilité sans condition: service_healthy ; l'application doit retenter de toute façon.","Override, profils et .env séparent dev et prod ; Compose pilote un seul hôte."],
10:["latest est interdit en production : tags immuables (SHA, version) et déploiement par digest.","Scanner (Trivy), produire un SBOM, signer (Cosign) : contenu, inventaire, origine.","Le SBOM permet de répondre à une nouvelle CVE en secondes, sans rescanner."],
11:["CI : chaque commit est construit et testé. CD : chaque commit est déployable. Déploiement continu : il part seul.","Construire une fois, déployer partout : la même image, identifiée par digest, en staging et en prod.","Un pipeline lent tue la CI : paralléliser, cacher, découper les tests, échouer vite."],
12:["GitLab CI et GitHub Actions font le même travail ; rules/needs d'un côté, on/if/needs de l'autre.","Épingler actions et images de job par SHA ou digest ; permissions minimales ; OIDC pour le cloud.","Jenkins : savoir reprendre un Jenkinsfile et expliquer pourquoi on migre."],
13:["Chaque type de test a sa place dans le pipeline, du plus rapide au plus lent.","Testcontainers remplace H2 et les mocks fragiles par de vraies dépendances.","Quality gate sur le nouveau code ; analyses de sécurité d'abord en observation, puis bloquantes."],
14:["Reproductibilité = lockfiles partout (Maven, npm, pip, Docker par digest, Terraform).","Renovate ouvre les MR de mise à jour ; auto-merge des correctifs, majeures à la main.","semantic-release calcule version et changelog à partir des commits ; Nexus proxifie et gouverne."],
15:["Recreate, rolling, blue/green, canary : interruption, coût, rollback, quand.","Rolling et canary font coexister deux versions : le schéma et les API doivent être compatibles N-1.","Feature flags : déployer n'est pas activer ; rollback par digest en une commande, sans build."],
16:["Terraform compare code, state et réalité ; plan avant apply, toujours.","State distant, chiffré, verrouillé, un par environnement et domaine ; for_each plutôt que count.","import, moved, state mv, force-unlock : les outils de réparation ; apply uniquement depuis la CI."],
17:["Ansible configure par SSH, sans agent, de façon idempotente : relancer ne change rien.","Rôles, handlers, templates, inventaire dynamique par tags ; Molecule et ansible-lint en CI.","Dans un monde conteneurisé, il prépare les hôtes et orchestre les opérations ; il ne déploie plus l'application."],
18:["Packer fabrique des images de machines comme un Dockerfile fabrique des images de conteneurs.","Golden image : construite, scannée, taguée, consommée par Terraform, remplacée plutôt que patchée.","Vagrant a été remplacé par Compose et les Dev Containers pour les applications."],
19:["Immuable : on ne modifie pas une machine, on la remplace ; plus de SSH en prod.","La dérive rend le code menteur : la détecter (plan nocturne), la prévenir (pas d'écriture console), la traiter.","GitOps : déclaratif, versionné, tiré par un agent, réconcilié en continu ; dépôt code séparé du dépôt config."],
20:["Choisir le niveau de service le plus haut qui satisfait les contraintes ; multi-AZ est le minimum.","Responsabilité partagée : la quasi-totalité des fuites vient du côté client (bucket, clé, security group).","Compte root avec MFA puis jamais utilisé ; budgets et alertes avant la première ressource."],
21:["IAM : rôles plutôt que clés, OIDC pour la CI, moindre privilège vérifié par Access Analyzer.","VPC en trois niveaux sur trois AZ ; security groups par référence ; endpoints plutôt que NAT.","Fargate par défaut, EKS pour la plateforme, Lambda pour l'événementiel ; RDS Multi-AZ, S3 verrouillé."],
22:["Les trois clouds font la même chose sous des noms différents ; l'identité et le réseau diffèrent vraiment.","Azure = Entra ID et groupes de ressources ; GCP = VPC global, projets, Cloud Run et GKE.","Cloud de confiance : résidence des données ≠ souveraineté juridique ; SecNumCloud, Bleu, S3NS."],
23:["FinOps : informer (tags, attribution), optimiser (leviers dans l'ordre), opérer (revue mensuelle).","Éteindre, redimensionner, changer d'architecture, puis seulement s'engager (Savings Plans).","NAT, transfert de données, logs sans rétention, IPv4 publiques : les postes surprises."],
24:["Multi-cloud subi, choisi par service, ou portable : le troisième est rarement justifié.","La vraie dépendance est dans les données et les compétences ; formats ouverts et plan de sortie testé.","Hybride : plan d'adressage sans chevauchement, DNS et identités fédérés, liaison dédiée si latence."],
25:["API server, etcd, scheduler, contrôleurs ; kubelet, containerd, CNI sur les nœuds.","Tout est déclaré ; les contrôleurs réconcilient en boucle l'état réel vers l'état désiré.","describe (événements) puis logs --previous : les deux premiers réflexes devant un Pod malade."],
26:["Le Deployment de référence : probes, requests sans limite CPU, arrêt propre, non root, PDB, topologie.","Service pour une adresse stable, Ingress ou Gateway API pour entrer, NetworkPolicy default-deny.","Un Secret n'est pas secret : chiffrement etcd, RBAC, et External Secrets plutôt que Git."],
27:["PV, PVC, StorageClass, CSI ; un volume RWO suit un nœud, d'où la lenteur des bascules.","StatefulSet donne identité et volume stables ; il ne fait pas la réplication : c'est le rôle de l'opérateur.","Base managée par défaut, opérateur (CloudNativePG) si beaucoup de bases, portabilité ou sur site ; restauration testée."],
28:["Helm pour installer et distribuer des paquets ; Kustomize pour les variantes de tes applications.","helm diff, --atomic, versions épinglées, checksum de ConfigMap, hooks de migration.","Toujours rendre et scanner les manifests avant de les appliquer."],
29:["ArgoCD réconcilie Git et cluster ; AppProject restrictif, ApplicationSet par environnement, sync waves.","Secrets : External Secrets vers un gestionnaire, Sealed Secrets ou SOPS sinon ; jamais en clair.","Promotion staging → prod par merge request ; rollback par revert ; Flux fait pareil sans interface."],
30:["Le mesh sort mTLS, autorisation, résilience et métriques de trafic du code de chaque service.","Sidecar hier, ambient et eBPF demain ; Istio, Linkerd, Cilium.","Pas de mesh pour trois services ; oui quand mTLS partout, dizaines de services polyglottes, canary fin."],
31:["HPA sur métriques métier, VPA pour calibrer, KEDA pour scaler à zéro sur une file.","Karpenter provisionne le bon nœud en secondes et consolide ; Spot et ARM pour le coût.","Affinités, taints, priorités, topologie, quotas : gouverner le placement et la capacité entre équipes."],
32:["Logs JSON sur stdout avec trace_id, sans données sensibles, niveaux disciplinés.","Loki indexe peu (labels à faible cardinalité) et coûte peu ; Elastic indexe tout et coûte cher.","Rétention par type, échantillonnage des succès, coût mesuré par service."],
33:["Counter, gauge, histogram ; rate, histogram_quantile ; jamais de moyenne de latence.","La cardinalité tue Prometheus : pas d'identifiant en label.","RED pour les services, USE pour les ressources ; dashboards en code ; Thanos/Mimir pour l'échelle."],
34:["Une trace = des spans reliés par la propagation du contexte (W3C traceparent, en-têtes Kafka).","OpenTelemetry : instrumenter une fois (agent Java sans code), Collector agent + gateway, exporter partout.","Tail sampling : garder toutes les erreurs et les lentes ; corréler par trace_id et exemplars."],
35:["SLI centré utilisateur, SLO négocié avec le produit, budget d'erreur à dépenser.","Alerter sur le burn rate multi-fenêtres (symptôme), tickets pour les causes ; runbook obligatoire.","Alertmanager : regroupement, inhibition, silences, escalade ; revue mensuelle du bruit."],
36:["Astreinte soutenable : rotation à 5 ou 6, moins de 2 pages par semaine, compensation, passation.","Incident : rôles (le commandant ne débogue pas), mitiger avant de comprendre, communication à cadence fixe.","Post-mortem sans blâme dans les 5 jours, actions suivies jusqu'à fermeture ; game days pour s'entraîner."],
37:["Modéliser les menaces (STRIDE) avant de coder ; ASVS comme exigences.","Chaque analyse à sa place, résultats agrégés (DefectDojo), bruit maîtrisé, SLA de correction.","SBOM à chaque build ; prioriser par EPSS, KEV et reachability ; VEX pour documenter le non-exploitable."],
38:["Supprimer le secret (identité) > dynamique > statique centralisé et tourné > chiffré dans Git.","Vault : auth Kubernetes, politiques, moteurs database/PKI/Transit, audit ; livré par agent, opérateur ou SDK.","KMS et chiffrement d'enveloppe pour les données ; HSM pour les clés critiques."],
39:["Les 4 C : cloud, cluster, conteneur, code ; chaque couche protège la suivante.","PSA restricted par namespace (warn → audit → enforce), Kyverno pour le reste, Falco à l'exécution.","kube-bench, kubescape, Trivy Operator : mesurer la posture et la suivre."],
40:["SolarWinds, Codecov, XZ, tj-actions : le build et les dépendances sont des cibles.","Sigstore keyless : signature liée à l'identité du job ; Rekor pour la transparence ; vérification à l'admission.","SLSA L3 : runner éphémère, provenance signée, paramètres non modifiables ; builds reproductibles."],
41:["Zero trust : vérifier à chaque saut, humains (MFA, JIT) et charges (SPIFFE, mTLS).","PKI : racine hors ligne, intermédiaire en ligne (Vault), certificats courts renouvelés par cert-manager.","OAuth 2.1 : code + PKCE, jetons courts, refresh rotation, BFF ; IDOR est la faille numéro un des API."],
42:["Un contrôle = une politique, une implémentation, une preuve ; le DevSecOps automatise les deux dernières.","ISO 27001 pour tous, SOC 2 pour le SaaS, RGPD obligatoire, NIS2 et DORA qui arrivent, SecNumCloud pour l'État.","La conformité papier ne tient pas ; la plateforme rend la politique vraie et la preuve gratuite."],
43:["Timeouts, retries idempotents, circuit breaker, bulkheads, dégradation, load shedding, idempotence, backpressure.","Une seule couche de retries, sinon tempête ; le pool de connexions est le goulot classique.","Chaos engineering : hypothèse, injection contrôlée, mesure, correction ; staging puis prod."],
44:["RTO et RPO se décident avec le métier, en euros ; quatre stratégies de coût croissant.","3-2-1, immutabilité, compte de sauvegarde isolé, restauration testée automatiquement.","Le PRA est du code, testé au moins une fois par an ; l'IdP et le monitoring en font partie."],
45:["Six types de tests de charge ; boucle ouverte (arrival rate) pour voir la vraie dégradation.","Traces d'abord, puis USE sur la ressource suspecte, puis profilage (JFR, Pyroscope).","Mesurer, cibler le goulot dominant, éliminer avant d'accélérer, re-mesurer, garder le test en CI."],
46:["Monolithe modulaire d'abord ; extraire par domaine quand une équipe ou une contrainte le justifie.","Kafka : clé de partition = ordre, acks=all, consommateurs idempotents, outbox transactionnel, schémas compatibles.","Sagas, CQRS, event sourcing : cohérence à terme assumée, à expliquer au produit."],
47:["PgBouncer devant PostgreSQL ; pools applicatifs petits ; lecture répartie avec read-your-writes.","Changements de schéma : lock_timeout, index concurrents, NOT VALID puis VALIDATE, lots, expand/contract.","Partitionner avant de sharder ; autovacuum et wraparound sous surveillance ; restauration testée."],
48:["La plateforme interne réduit la charge cognitive : golden paths, libre-service, conformité par construction.","Backstage pour l'interface, Crossplane et templates pour le libre-service, ArgoCD pour livrer.","C'est un produit : adoption, délai de création d'un service, DORA et satisfaction mesurés."],
49:["Tenancy : namespaces, vCluster, nœuds dédiés, cluster ou compte par tenant selon confiance et réglementation.","Landing zone : comptes par domaine et environnement, hub-and-spoke, IPAM, IdP, garde-fous, vending.","Flotte de clusters en code, bootstrap GitOps identique, cadence de mise à jour trimestrielle."],
50:["Les 7 R avec une répartition réaliste : beaucoup de replatform, peu de refactor, du retire.","Fondations avant vagues ; données en réplication continue avec bascule courte ; décommissionner pour de bon.","Monolithe Java : conteneuriser, tests de caractérisation, strangler fig, données en dernier, OpenRewrite."],
51:["Garde-fous préventifs, détectifs, directifs ; chaque règle a une justification, un propriétaire, une exception.","Standards vivants en dépôt, appliqués en code à chaque couche (OPA, Kyverno, Spectral, compliance pipelines).","Exceptions à durée limitée, revue d'architecture asynchrone, dette budgétée, rapport mensuel à la direction."],
52:["Cinq métriques DORA, définitions opérationnelles, sources automatiques, tendances par service, jamais d'objectif individuel.","SPACE et DevEx complètent ; la valeur métier est la vraie cible.","Audit : entretiens, observation, données, modèle de maturité, feuille de route en trois horizons."],
53:["Les transformations échouent pour des raisons humaines : sens, sponsor, pilote, attraction, ancrage, mesure.","Coacher vers l'autonomie : pairing, dojos, security champions ; reconnaître l'expertise des ops.","Consultant : cadrer, diagnostiquer avant de prescrire, rendre les arbitrages explicites, transférer."],
54:["L'IA accélère l'expert ; agents en lecture seule par défaut, écriture via merge request, tout journalisé.","AIOps utile : anomalies en contexte, assistant d'incident, remédiation déterministe et bornée.","Passerelle LLM, evals en CI, observabilité GenAI, OWASP LLM Top 10 avec l'injection indirecte en fil rouge."],
}
assert len(BREF) == 54

def bref(ch):
    items = ''.join(f'<li>{html.escape(t)}</li>' for t in BREF[ch])
    return f'<div class="bref"><span class="tag">En 30 secondes</span><ol>{items}</ol></div>\n'

CSS = """
/* ============ Résumés et schémas ============ */
.bref{background:var(--paper);border:1px solid var(--accent);border-left:4px solid var(--accent);border-radius:var(--radius);padding:.85rem 1rem;margin:1rem 0}
.bref .tag{font-weight:700;color:var(--accent-ink);display:block;margin-bottom:.35rem}
.bref ol{margin:0;padding-left:1.3rem}
.bref li{margin:.3rem 0}
.fig{margin:1.2rem 0;padding:.6rem .6rem .4rem;background:var(--paper);border:1px solid var(--line);border-radius:var(--radius)}
.fig svg{width:100%;height:auto;display:block;font-family:inherit}
.fig figcaption{font-size:.85rem;color:var(--muted);margin-top:.5rem;text-align:center}
.fig text{fill:var(--ink)}
.fig .lbl{fill:var(--muted);font-size:12px}
.fig .lblw{fill:#fff;font-size:12px;font-weight:700}
.fig .glab{fill:var(--accent-ink);font-size:12px;font-weight:700}
.fig .box{fill:var(--paper);stroke:var(--line-strong);stroke-width:1.5}
.fig .frame{fill:none;stroke:var(--line);stroke-width:1.5;stroke-dasharray:4 3}
.fig .soft{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.5}
.fig .green{fill:var(--tp-soft);stroke:var(--tp);stroke-width:1.5}
.fig .amber{fill:var(--exo-soft);stroke:var(--exo);stroke-width:1.5}
.fig .purple{fill:var(--ent-soft);stroke:var(--ent);stroke-width:1.5}
.fig .red{fill:#FDECEC;stroke:#A11B1B;stroke-width:1.5}
.fig .redfill{fill:#C0392B}
:root[data-theme="dark"] .fig .red{fill:#3A1616;stroke:#F29A9A}
.fig .arrow{fill:none;stroke:var(--ink);stroke-width:1.6}
.fig .arrow.dashed{stroke-dasharray:5 4}
.fig .axis{stroke:var(--line-strong);stroke-width:1.5}
.fig .ahead{fill:var(--ink)}
@media print{.fig{break-inside:avoid}}
</style>"""

# ---------- Corrections d'incohérences ----------
FIXES = {
 "devops-niveau-0-fondations.html": [
  ("<p>Retenir la logique : vitesse (les deux premières) <em>et</em> stabilité (les deux dernières) montent ensemble. Ce n'est pas un compromis.</p>",
   "<p>Retenir la logique : vitesse (les deux premières) <em>et</em> stabilité (les deux dernières) montent ensemble. Ce n'est pas un compromis. Depuis 2024, le rapport en ajoute une cinquième, le taux de retravail (part des déploiements qui corrigent un déploiement précédent) ; le chapitre 52 les mesure toutes les cinq.</p>"),
  ("<li>Les quatre métriques DORA et pourquoi vitesse et stabilité ne s'opposent pas.</li>",
   "<li>Les quatre métriques DORA historiques, la cinquième ajoutée en 2024, et pourquoi vitesse et stabilité ne s'opposent pas.</li>"),
 ],
 "devops-niveau-2-ci-cd.html": [
  ("<details><summary>Corrigé</summary><div class=\"sol\">Sa seule règle est <code>changes:</code>, sans <code>if</code> sur la source du pipeline. Sur une merge request, <code>changes</code> se compare correctement, mais si le pipeline est déclenché par <code>push</code> sur une branche, il fonctionne aussi… Vérifie en réalité <code>workflow:rules</code> ou l'absence de pipeline MR ; la correction robuste est <code>rules: - if: $CI_PIPELINE_SOURCE == \"merge_request_event\"</code> combiné à <code>changes:</code> dans la même règle.</div></details>",
   "<details><summary>Corrigé</summary><div class=\"sol\">Le job n'a qu'une règle <code>changes:</code>, sans <code>if:</code> sur la source du pipeline, et le projet n'a pas de <code>workflow:rules</code> qui crée des pipelines de merge request : GitLab ne lance alors que des pipelines de branche, où <code>changes</code> se compare au commit précédent (souvent vide après un rebase ou un push forcé). Correction : un bloc <code>workflow:rules</code> qui autorise les pipelines de merge request, et sur le job une règle qui combine <code>if: $CI_PIPELINE_SOURCE == \"merge_request_event\"</code> et <code>changes: [scripts/**]</code> ; dans un pipeline de MR, la comparaison se fait avec la branche cible, ce qui est fiable.</div></details>"),
 ],
 "devops-niveau-5-kubernetes.html": [
  ("<li>Écris <code>kind-config.yaml</code> : un control plane et deux workers, avec <code>extraPortMappings</code> 80 et 443 sur le control plane (pour l'ingress plus tard) et un label <code>ingress-ready=true</code>. Crée le cluster : <code>docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v \"$PWD:/w\" -w /w -v \"$HOME/.kube:/root/.kube\" kindest/node:v1.31.0 ...</code> n'est pas la bonne image ; utilise le binaire kind dans un conteneur outillé (par exemple une image que tu construis avec <code>kind</code>, <code>kubectl</code> et <code>helm</code> à partir d'<code>alpine</code>, montée sur le socket Docker). Écris ce Dockerfile <code>tools/Dockerfile</code> et le script <code>k8s.sh</code> qui l'utilise : ce sera ton poste de travail Kubernetes pour tout le niveau.</li>",
   "<li>Construis d'abord ton poste de travail Kubernetes en conteneur : un <code>tools/Dockerfile</code> à partir d'<code>alpine</code> qui installe les binaires <code>kind</code>, <code>kubectl</code> et <code>helm</code> (téléchargés depuis leurs releases officielles, versions épinglées), et un script <code>k8s.sh</code> qui lance ce conteneur avec le socket Docker (<code>-v /var/run/docker.sock:/var/run/docker.sock</code>), ton répertoire courant et <code>$HOME/.kube</code> montés. Écris ensuite <code>kind-config.yaml</code> : un control plane et deux workers, <code>extraPortMappings</code> 80 et 443 sur le control plane (pour l'ingress plus tard) et un label <code>ingress-ready=true</code>. Crée le cluster avec <code>./k8s.sh kind create cluster --name crisisshield --config kind-config.yaml</code>.</li>"),
 ],
}

# ---------- Application ----------
out = pathlib.Path('/mnt/user-data/outputs')
files = [
 ("devops-niveau-0-fondations.html", range(1,7)), ("devops-niveau-1-conteneurs.html", range(7,11)),
 ("devops-niveau-2-ci-cd.html", range(11,16)), ("devops-niveau-3-infrastructure-as-code.html", range(16,20)),
 ("devops-niveau-4-cloud.html", range(20,25)), ("devops-niveau-5-kubernetes.html", range(25,32)),
 ("devops-niveau-6-observabilite.html", range(32,37)), ("devops-niveau-7-securite-devsecops.html", range(37,43)),
 ("devops-niveau-8-sre-architecture.html", range(43,49)), ("devops-niveau-9-expert-leadership.html", range(49,55)),
]
for fn, chs in files:
    p = out/fn; s = p.read_text()
    if 'class="bref"' in s:
        print(fn, 'déjà fait'); continue
    for old, new in FIXES.get(fn, []):
        assert old in s, (fn, old[:60])
        s = s.replace(old, new, 1)
    for ch in chs:
        # repère : la fin du bloc objectifs du chapitre ch (puis éventuellement le mémo)
        start = s.index(f'<span class="chapnum">Chapitre {ch}</span>')
        i = s.index('<div class="objectifs">', start)
        j = s.index('</ul></div>', i) + len('</ul></div>')
        # sauter le mémo s'il suit
        k = j
        if s.startswith('\n<div class="memo">', j):
            k = s.index('</div>', j + 5) + len('</div>')
        insert = '\n' + bref(ch) + (FIGS[ch] + '\n' if ch in FIGS else '')
        s = s[:k] + insert + s[k:]
    s = s.replace('</style>', CSS, 1)
    p.write_text(s)
    print(fn, 'résumés', len(list(chs)), 'schémas', sum(1 for c in chs if c in FIGS))

# page d'accueil
p = out/'devops-parcours-complet.html'; s = p.read_text()
if 'En 30 secondes' not in s:
    s = s.replace('<span>Chaque chapitre : cours, technologie de niche, encadré entretien, exercices corrigés, TP</span>',
                  '<span>Chaque chapitre : résumé en 30 secondes, cours, schémas, technologie de niche, encadré entretien, exercices corrigés, TP</span>', 1)
    s = s.replace('<li><strong>Tags de mémorisation</strong>',
                  '<li><strong>Lecture rapide</strong> : chaque chapitre s\'ouvre sur « En 30 secondes » (l\'idée, la règle, l\'erreur à éviter) et, pour les vingt concepts les plus visuels, un schéma. Pour balayer un niveau en une heure : les résumés, les schémas et les sections « Par cœur ».</li>\n<li><strong>Tags de mémorisation</strong>', 1)
    s = s.replace('</style>', CSS, 1)
    p.write_text(s)
print('index ok')
