import re, pathlib, json, html as H
from collections import Counter

out = pathlib.Path('/mnt/user-data/outputs')
src = pathlib.Path('/home/claude/pipes.py').read_text()
CSS = src.split('CSS = """')[1].split('"""')[0]
JS = src.split('JS = r"""')[1].split('"""')[0]

def pipe(ident, question, cmd_parts, stages, done, caption, sep=' | '):
    data = {"cmd": cmd_parts, "sep": sep, "stages": stages, "done": done}
    return (f'<figure class="pipe" id="{ident}">'
            f'<div class="ctl"><button type="button" class="primary" data-play>Exécuter pas à pas</button><button type="button" data-next>Étape suivante</button><button type="button" data-reset>Réinitialiser</button><span class="st"></span></div>'
            f'<p class="q">{H.escape(question)}</p><div class="cmd"></div><div class="cols"></div><p class="expl"></p>'
            f'<script type="application/json">{json.dumps(data, ensure_ascii=False)}</script>'
            f'<figcaption>{caption}</figcaption></figure>')
def st(title, lines, why, hl=None):
    d = {"title": title, "lines": lines, "why": why}
    if hl: d["hl"] = hl
    return d

L = {1:"devops-01-virtualisation-et-conteneurs.html",2:"devops-02-integration-et-livraison-continues.html",3:"devops-03-infrastructure-as-code.html",4:"devops-04-cloud.html",5:"devops-05-kubernetes.html",6:"devops-06-observabilite.html",7:"devops-07-securite-devsecops.html",8:"devops-08-sre-et-architecture.html",9:"devops-09-expert-et-leadership.html"}
P = {k: [] for k in L}
A = ' → '

# ================================================================ Niveau 1
P[1].append(("8.2", pipe("pipe-layers", "Comment une image se construit, couche par couche ?",
 ["FROM eclipse-temurin:21-jre", "RUN apt-get install -y curl", "COPY target/app.jar /app/", "USER 1001", "ENTRYPOINT [\"java\",\"-jar\",\"/app/app.jar\"]"],
 [st("FROM", ["couche 0  eclipse-temurin:21-jre   85 Mo", "  (CACHED : déjà sur le poste)"], "L'image de base apporte ses couches, en lecture seule ; elles sont partagées entre toutes les images qui en dérivent."),
  st("RUN apt-get", ["couche 0  base                     85 Mo", "couche 1  + curl, apt lists        12 Mo", "  (CACHED tant que la ligne RUN ne change pas)"], "Chaque RUN crée une couche avec ce qu'il a ajouté ; un rm dans un RUN suivant ne réduit rien, la couche précédente reste."),
  st("COPY app.jar", ["couche 0  base                     85 Mo", "couche 1  + curl                   12 Mo", "couche 2  + app.jar                 38 Mo", "  (RECONSTRUITE : le jar a changé)"], "La couche qui change le plus souvent vient en dernier : tout ce qui précède reste en cache."),
  st("USER", ["couche 0..2                       135 Mo", "métadonnée : User=1001", "  (pas de couche : 0 octet)"], "USER, EXPOSE, ENV, ENTRYPOINT n'ajoutent pas de fichiers : ce sont des métadonnées de l'image."),
  st("ENTRYPOINT", ["image api:1.7.0                 135 Mo", "digest sha256:3f9c…", "3 couches + config"], "L'image finale est la pile des couches plus une configuration ; le digest est l'empreinte de l'ensemble.", ["digest sha256:3f9c…"])],
 "135 Mo, 3 couches, tout sauf le jar vient du cache",
 "L'ordre des instructions décide du cache : ce qui change rarement d'abord, ce qui change à chaque commit à la fin. docker history montre ces couches.", sep=A)))
P[1].append(("8.6", pipe("pipe-exit", "Pourquoi mon conteneur s'est-il arrêté ?",
 ["docker ps -a --filter status=exited --format '{{.Names}} {{.Status}}'", "docker inspect api --format '{{.State.ExitCode}} {{.State.OOMKilled}}'", "docker logs --tail 5 api"],
 [st("docker ps -a", ["api     Exited (137) 2 minutes ago", "worker  Exited (0) 3 hours ago", "db      Up 2 days (healthy)"], "docker ps sans -a cache les conteneurs arrêtés ; le code entre parenthèses est le premier indice : 137 = 128 + 9, tué par SIGKILL."),
  st("docker inspect", ["ExitCode   137", "OOMKilled  true", "StartedAt  10:41:02", "FinishedAt 10:52:18"], "inspect confirme : OOMKilled = le noyau a tué le processus qui dépassait sa limite mémoire. Ce n'est pas un bug du code, c'est une limite."),
  st("docker logs --tail", ["10:52:10 INFO  cache warm-up 1.2 Go", "10:52:14 WARN  GC pressure", "10:52:17 INFO  loading zone index", "(fin des logs : tué sans message)"], "Les derniers logs montrent ce que faisait l'application juste avant : un chargement en mémoire. Solution : -Xmx cohérent avec --memory, ou plus de mémoire, ou moins de cache.", ["(fin des logs : tué sans message)"])],
 "OOMKilled : limite mémoire dépassée pendant le chargement du cache",
 "ps -a, inspect, logs : trois commandes, dans cet ordre, avant toute hypothèse. 137 = OOM ou kill -9 ; 143 = arrêt propre ; 1 = erreur applicative, les logs le diront.", sep=A)))
P[1].append(("9.4", pipe("pipe-compose", "Dans quel ordre la pile démarre-t-elle avec docker compose up ?",
 ["docker compose up -d", "db : healthcheck", "api : depends_on db healthy", "proxy : depends_on api healthy"],
 [st("compose up", ["réseau backend    créé", "réseau frontend   créé", "volume pgdata     créé", "db     démarrage…", "api    en attente (db)", "proxy  en attente (api)"], "Compose crée réseaux et volumes, puis démarre les services en respectant depends_on : api n'a pas démarré."),
  st("db healthy", ["db     healthy (pg_isready OK, 3e essai)", "api    démarrage…", "proxy  en attente (api)"], "condition: service_healthy fait attendre que le healthcheck passe, pas seulement que le processus existe. Sans condition, api démarrerait avant que PostgreSQL n'accepte des connexions."),
  st("api healthy", ["db     healthy", "api    healthy (/actuator/health 200)", "proxy  démarrage…"], "api expose un healthcheck qui vérifie la base : Compose ne lance proxy que quand l'API répond réellement."),
  st("proxy up", ["db     healthy", "api    healthy", "proxy  running, :443 publié", "→ https://localhost"], "La pile est prête dans le bon ordre. Et si db redémarre plus tard, c'est à l'application de retenter : depends_on n'agit qu'au démarrage.", ["proxy  running, :443 publié"])],
 "trois services, un seul port publié, démarrés dans l'ordre des dépendances",
 "depends_on + healthcheck ordonne le démarrage ; les reconnexions applicatives (retries) gèrent le reste de la vie de la pile.", sep=A)))
P[1].append(("10.3", pipe("pipe-scan", "Quelles vulnérabilités bloquent la publication de l'image ?",
 ["syft api:1.7.0 -o cyclonedx-json > sbom.json", "grype sbom:sbom.json -o json", "jq -r '.matches[] | .vulnerability.severity+\" \"+.artifact.name+\" \"+.vulnerability.id'", "grep -E '^(High|Critical)'", "sort | uniq -c | sort -rn"],
 [st("syft (SBOM)", ["libssl3        3.0.13", "curl           8.5.0", "jackson-databind 2.15.2", "log4j-api      2.20.0", "spring-web     6.1.4", "… 212 composants"], "Le SBOM liste tout ce que contient l'image : paquets de l'OS et dépendances Java. Généré une fois, réutilisable pour chaque nouvelle CVE."),
  st("grype", ["Critical curl CVE-2026-1234", "High libssl3 CVE-2026-2211", "High jackson-databind CVE-2026-3301", "Medium curl CVE-2025-9987", "Low libssl3 CVE-2025-4410", "… 31 correspondances"], "grype croise le SBOM avec les bases de vulnérabilités : chaque composant vulnérable donne une ligne avec sa gravité."),
  st("jq", ["Critical curl CVE-2026-1234", "High libssl3 CVE-2026-2211", "High jackson-databind CVE-2026-3301", "Medium curl CVE-2025-9987", "Low libssl3 CVE-2025-4410"], "jq aplatit le JSON en lignes « gravité composant CVE » : on revient aux outils texte."),
  st("grep High|Critical", ["Critical curl CVE-2026-1234", "High libssl3 CVE-2026-2211", "High jackson-databind CVE-2026-3301"], "Seules les gravités élevées bloquent ; le reste part en ticket avec un délai de correction."),
  st("sort | uniq -c", ["      1 Critical curl", "      1 High jackson-databind", "      1 High libssl3"], "Trois composants à corriger : mettre à jour l'image de base (curl, libssl3) et la dépendance Java (jackson). Puis rebuild, et le pipeline repasse au vert.", ["      1 Critical curl"])],
 "3 composants bloquants : 2 dans l'image de base, 1 dépendance Java",
 "SBOM d'abord, scan ensuite : quand une CVE sort, on interroge le SBOM en secondes au lieu de rescanner toutes les images.")))

# ================================================================ Niveau 2
P[2].append(("12.1", pipe("pipe-push", "Que se passe-t-il entre git push et le déploiement en staging ?",
 ["git push origin feature/x", "pipeline créé", "build", "test", "package", "deploy staging"],
 [st("git push", ["feature/x  a1b2c3 → origin", "merge request !42 ouverte", "règles : merge_request_event", "→ pipeline #1842 créé"], "Le push déclenche un pipeline selon les règles du fichier de CI : ici parce qu'une merge request est ouverte."),
  st("jobs planifiés", ["build     (image maven)     en attente", "test      (needs: build)    en attente", "sast      (parallèle)       en attente", "package   (needs: test)     en attente", "deploy    (manual, staging) en attente"], "Les jobs sont créés avec leurs dépendances (needs) : test et sast peuvent tourner en parallèle après build."),
  st("build", ["runner docker-01 prend le job", "./mvnw -q package -DskipTests", "artefact target/app.jar  38 Mo", "durée 1 min 12"], "Un runner exécute le job dans un conteneur jetable et remonte l'artefact au serveur."),
  st("test + sast", ["test : 214 tests, 0 échec, 84 % couverture", "rapport JUnit attaché à la MR", "sast : 0 finding bloquant", "durée 2 min 40 (en parallèle)"], "Les rapports s'affichent dans la merge request ; un échec ici arrête tout le reste."),
  st("package", ["docker build -t api:a1b2c3", "trivy image → 0 High/Critical", "push registry → sha256:3f9c…", "durée 1 min 05"], "Une image par commit, taguée par son SHA, scannée, poussée : c'est ce digest qui sera déployé partout."),
  st("deploy staging", ["kubectl set image deploy/api api=…@sha256:3f9c…", "rollout OK en 40 s", "smoke test /health 200", "URL staging dans la MR"], "Le déploiement référence le digest, pas un tag ; un test de fumée confirme ; la MR contient le lien pour tester.", ["rollout OK en 40 s"])],
 "5 min 40 du push au staging, sans intervention humaine",
 "Construire une fois, tester en parallèle, déployer par digest : chaque étape produit une preuve (artefact, rapport, digest) que la suivante consomme.", sep=A)))
P[2].append(("13.4", pipe("pipe-gate", "La merge request peut-elle être fusionnée ?",
 ["tests unitaires", "couverture du nouveau code", "analyse statique", "quality gate"],
 [st("tests", ["214 tests, 0 échec, 3 ignorés", "durée 48 s", "mutation score 67 % (PIT)"], "Des tests verts sont nécessaires, pas suffisants : le score de mutation dit s'ils vérifient vraiment quelque chose."),
  st("couverture", ["nouveau code : 84 % (seuil 80 %)", "IncidentService  92 %", "ZoneMapper       61 %  ← sous le seuil", "global : 71 % (non bloquant)"], "La barrière juge le code nouveau, pas l'historique : on ne demande pas de rattraper dix ans de dette pour fusionner une fonctionnalité."),
  st("SAST + SCA", ["Semgrep : 1 finding, sévérité moyenne", "  sql-injection ? non : requête paramétrée (faux positif marqué)", "Trivy fs : 0 High/Critical", "secrets : 0"], "Les findings sont triés : le faux positif est documenté dans le dépôt, pas ignoré en silence."),
  st("gate", ["couverture nouveau code ≥ 80 %   OK", "0 bug bloquant                   OK", "0 vulnérabilité High/Critical    OK", "dette nouvelle ≤ 30 min          OK", "→ PASSED : fusion autorisée"], "Quatre règles, toutes objectives, appliquées automatiquement : la revue humaine se concentre sur le design.", ["→ PASSED : fusion autorisée"])],
 "gate PASSED, fusion autorisée, ZoneMapper à couvrir dans la prochaine MR",
 "La barrière qualité rend la pyramide obligatoire : sans elle, la couverture baisse à chaque sprint et personne ne s'en aperçoit.", sep=A)))
P[2].append(("14.2", pipe("pipe-cve", "Une CVE sort ce matin : quels services sont touchés ?",
 ["curl -s dependency-track/api/v1/component?name=jackson-databind", "jq -r '.[] | .project.name+\" \"+.version'", "sort -u", "awk '$2 < \"2.17.1\"'"],
 [st("interroger les SBOM", ["crisisshield-api      2.15.2", "notification-service  2.17.1", "legacy-reporting      2.12.7", "crisisshield-api      2.15.2", "geo-service           2.17.1"], "Tous les SBOM sont centralisés (Dependency-Track) : une requête suffit pour savoir qui contient le composant, sans rescanner."),
  st("jq", ["crisisshield-api 2.15.2", "notification-service 2.17.1", "legacy-reporting 2.12.7", "crisisshield-api 2.15.2", "geo-service 2.17.1"], "Une ligne par projet et version."),
  st("sort -u", ["crisisshield-api 2.15.2", "geo-service 2.17.1", "legacy-reporting 2.12.7", "notification-service 2.17.1"], "Dédoublonné : quatre projets, deux versions distinctes."),
  st("awk version < 2.17.1", ["crisisshield-api 2.15.2", "legacy-reporting 2.12.7"], "Seules les versions antérieures au correctif sont vulnérables : deux services à mettre à jour, Renovate ouvre les deux merge requests.", ["crisisshield-api 2.15.2", "legacy-reporting 2.12.7"])],
 "2 services vulnérables sur 4, MR Renovate ouvertes en 10 minutes",
 "Sans SBOM centralisé, cette question prend une journée de grep dans les dépôts ; avec, dix minutes, et la preuve pour l'auditeur.")))

# ================================================================ Niveau 3
P[3].append(("16.2", pipe("pipe-plan", "Que va faire terraform apply ?",
 ["terraform plan", "lire le code", "lire le state", "rafraîchir depuis le cloud", "calculer le diff", "ordonner"],
 [st("code HCL", ["aws_vpc.main", "aws_subnet.private[0..2]", "aws_security_group.api", "aws_db_instance.main  (classe db.t4g.small)", "aws_instance.web      (ami-2026)"], "Le code décrit l'état voulu : cinq ressources, avec leurs attributs."),
  st("state", ["aws_vpc.main             vpc-0a1b", "aws_subnet.private[0..2] subnet-…", "aws_security_group.api   sg-9f3e", "aws_db_instance.main     db.t4g.micro", "(aws_instance.web : absent)"], "Le state est ce que Terraform croit exister : quatre ressources connues, l'instance web n'y est pas encore."),
  st("refresh", ["vpc-0a1b        OK", "subnets         OK", "sg-9f3e         tags modifiés à la console !", "db              db.t4g.micro (comme le state)"], "Terraform interroge le cloud : il découvre qu'un tag a été changé à la main sur le security group (dérive)."),
  st("diff", ["+ aws_instance.web        (à créer)", "~ aws_db_instance.main    micro → small (modif. en place)", "~ aws_security_group.api  tags (revient au code)", "  aws_vpc.main            inchangé", "Plan: 1 to add, 2 to change, 0 to destroy"], "Le plan est la différence entre voulu et réel : + crée, ~ modifie, -/+ recrée, - détruit. Lire la ligne « forces replacement » avant tout apply."),
  st("ordre", ["1. aws_security_group.api  (tags)", "2. aws_db_instance.main    (resize, ~4 min)", "3. aws_instance.web        (dépend du SG)"], "Les dépendances (références entre ressources) donnent l'ordre ; apply exécute en parallèle ce qui est indépendant.", ["Plan: 1 to add, 2 to change, 0 to destroy"])],
 "1 création, 2 modifications, 0 destruction : apply sans risque",
 "Code, state, réalité : trois sources, un plan. Une dérive vue au plan est corrigée par le code, jamais à la console.", sep=A)))
P[3].append(("17.2", pipe("pipe-ansible", "Que fait ansible-playbook sur trois hôtes ?",
 ["ansible-playbook -i inventory/prod.ini site.yml", "inventaire", "facts", "tâche : paquet nginx", "tâche : template", "handler", "recap"],
 [st("inventaire", ["[web]", "web1  ansible_host=10.0.1.11", "web2  ansible_host=10.0.1.12", "[db]", "db1   ansible_host=10.0.2.5", "→ play « web » : 2 hôtes"], "Le play cible le groupe web : deux hôtes, par SSH, en parallèle (forks)."),
  st("gather facts", ["web1 : Ubuntu 24.04, 2 CPU, python3.12", "web2 : Ubuntu 24.04, 2 CPU, python3.12"], "Ansible collecte des faits sur chaque hôte : OS, réseau, mémoire ; utilisables dans les tâches (ansible_os_family)."),
  st("apt: nginx", ["web1 : ok      (déjà installé)", "web2 : changed (installé 1.26)"], "Le module vérifie l'état avant d'agir : web1 avait déjà nginx, rien n'a changé. C'est l'idempotence."),
  st("template", ["web1 : changed (nginx.conf : upstream modifié)", "web2 : changed (nginx.conf créé)", "→ notify : reload nginx"], "Le template est rendu avec les variables ; s'il diffère du fichier en place, il est remplacé et le handler est notifié."),
  st("handler", ["web1 : reload nginx  changed", "web2 : reload nginx  changed"], "Le handler ne tourne qu'une fois par hôte, à la fin, seulement si une tâche l'a notifié : pas de rechargement inutile."),
  st("PLAY RECAP", ["web1 : ok=4 changed=2 failed=0", "web2 : ok=4 changed=3 failed=0", "db1  : (hors du play)"], "Le récapitulatif dit ce qui a changé ; relancer le playbook donnerait changed=0 partout.", ["web1 : ok=4 changed=2 failed=0"])],
 "2 hôtes configurés, 0 échec, relance à changed=0",
 "Inventaire, facts, tâches idempotentes, handlers : c'est le cycle de tout playbook ; --check --diff le simule sans rien toucher.", sep=A)))

# ================================================================ Niveau 4
P[4].append(("21.3", pipe("pipe-aws", "Où passe une requête vers CrisisShield sur AWS ?",
 ["https://app.crisisshield.example", "Route 53", "ALB (public)", "target group", "ECS task (privé)", "RDS (privé)"],
 [st("Route 53", ["app.crisisshield.example", "  → alias ALB", "  → 52.47.10.3, 52.47.10.9 (2 AZ)", "TTL 60 s, health check"], "Le DNS renvoie les adresses de l'équilibreur, dans deux zones : la première résilience est ici."),
  st("ALB", ["listener 443, certificat ACM", "  règle : /api/* → tg-api", "  règle : /*     → tg-web", "WAF : règles gérées OK", "logs d'accès → S3"], "L'ALB termine le TLS, applique le WAF et route par chemin vers le bon groupe cible ; il est le seul composant sur Internet."),
  st("target group", ["tg-api : 3 cibles", "  10.0.11.4  healthy", "  10.0.12.7  healthy", "  10.0.13.2  draining (déploiement)", "health check /actuator/health"], "Le groupe cible ne reçoit que des cibles saines ; une cible en cours de remplacement est vidée avant d'être retirée."),
  st("ECS task", ["subnet privé 10.0.11.0/24", "SG api : entrée 8080 depuis SG-alb uniquement", "rôle IAM : lecture Secrets Manager", "logs → CloudWatch"], "La tâche n'a pas d'adresse publique ; son security group n'accepte que l'ALB ; son identité est un rôle, pas une clé."),
  st("RDS", ["subnet base 10.0.21.0/24, multi-AZ", "SG db : entrée 5432 depuis SG-api uniquement", "mot de passe via Secrets Manager (rotation 30 j)", "→ réponse 200 en 42 ms"], "La base n'est joignable que depuis les tâches ; trois couches de sécurité (subnet, SG, secret) avant la première ligne de SQL.", ["→ réponse 200 en 42 ms"])],
 "DNS → ALB → tâches privées → base privée, chaque saut filtré par identité",
 "L'architecture trois niveaux se lit comme une chaîne : chaque composant ne parle qu'au suivant, par référence de security group, jamais par IP.", sep=A)))
P[4].append(("23.2", pipe("pipe-cost", "D'où vient la facture de ce mois ?",
 ["aws ce get-cost-and-usage --group-by Type=DIMENSION,Key=SERVICE", "jq -r '.ResultsByTime[0].Groups[] | .Metrics.UnblendedCost.Amount+\" \"+.Keys[0]'", "sort -rn", "head -5"],
 [st("Cost Explorer", ["{ \"Groups\": [", "  {\"Keys\":[\"Amazon EC2\"], \"Metrics\":{\"UnblendedCost\":{\"Amount\":\"2140.2\"}}},", "  {\"Keys\":[\"Amazon RDS\"], …\"812.5\"},", "  {\"Keys\":[\"NAT Gateway\"], …\"640.0\"},", "  … 14 services"], "L'API renvoie le coût par service ; la même donnée que la console, mais scriptable chaque mois."),
  st("jq", ["2140.2 Amazon EC2", "812.5 Amazon RDS", "640.0 NAT Gateway", "310.4 Amazon S3", "95.1 CloudWatch", "…"], "Une ligne par service : montant puis nom."),
  st("sort -rn", ["2140.2 Amazon EC2", "812.5 Amazon RDS", "640.0 NAT Gateway", "310.4 Amazon S3", "95.1 CloudWatch", "…"], "Du plus cher au moins cher."),
  st("head -5", ["2140.2 Amazon EC2   ← 12 instances dev allumées la nuit", "812.5 Amazon RDS    ← surdimensionnée ?", "640.0 NAT Gateway   ← S3 sans endpoint", "310.4 Amazon S3", "95.1 CloudWatch"], "Trois lignes concentrent 90 % : éteindre le dev la nuit (levier 1), redimensionner la base (levier 2), endpoint S3 pour supprimer le NAT (levier 3).", ["640.0 NAT Gateway   ← S3 sans endpoint"])],
 "3 leviers identifiés, ≈ 1 500 $ par mois économisables",
 "Le NAT Gateway est le poste caché classique : chaque Go vers S3 le traverse tant qu'il n'y a pas d'endpoint. Le coût se lit dans l'ordre des leviers.")))

# ================================================================ Niveau 5
P[5].append(("25.2", pipe("pipe-apply", "Que se passe-t-il après kubectl apply -f deploy.yaml ?",
 ["kubectl apply", "API server : authn, RBAC, admission", "etcd", "Deployment controller", "ReplicaSet controller", "scheduler", "kubelet"],
 [st("kubectl", ["POST /apis/apps/v1/…/deployments", "Deployment api, replicas: 3", "image api@sha256:3f9c…"], "kubectl envoie l'objet à l'API ; il ne crée aucun Pod lui-même."),
  st("API server", ["authentification : OIDC gael@…  OK", "RBAC : edit sur ns crisisshield  OK", "admission : Kyverno vérifie la signature  OK", "admission : PSA restricted  OK", "→ objet validé"], "Chaque requête passe l'authentification, l'autorisation et les politiques d'admission : c'est là que la sécurité s'applique."),
  st("etcd", ["deployments/crisisshield/api   v1", "(rien d'autre n'existe encore)"], "L'objet est écrit ; l'API répond « created ». Aucun conteneur ne tourne : tout le reste est asynchrone."),
  st("Deployment ctrl", ["voit Deployment api sans ReplicaSet", "crée ReplicaSet api-7d9f  replicas: 3"], "Le contrôleur compare voulu et réel et crée ce qui manque : un ReplicaSet pour cette version du template."),
  st("ReplicaSet ctrl", ["voit 0 Pod sur 3", "crée Pod api-7d9f-x1k2  (Pending)", "crée Pod api-7d9f-m4n8  (Pending)", "crée Pod api-7d9f-q9r3  (Pending)"], "Trois Pods sont créés, sans nœud : ils sont Pending."),
  st("scheduler", ["api-7d9f-x1k2 → worker-1 (ressources, affinité, taints)", "api-7d9f-m4n8 → worker-2", "api-7d9f-q9r3 → worker-3 (topologySpread)"], "Le scheduler choisit un nœud par Pod selon requests, contraintes et répartition."),
  st("kubelet", ["worker-1 : pull image (digest) → conteneur démarré", "startup OK → liveness → readiness OK", "Pod Running, Ready 1/1", "→ EndpointSlice mise à jour : le Service route"], "Le kubelet de chaque nœud lance le conteneur et sonde sa santé ; seuls les Pods Ready reçoivent du trafic.", ["Pod Running, Ready 1/1"])],
 "7 acteurs, une boucle de réconciliation, 3 Pods Ready en 25 s",
 "Rien n'est impératif : chaque contrôleur rapproche l'état réel de l'état voulu. C'est pourquoi un Pod supprimé revient, et pourquoi kubectl répond avant que quoi que ce soit ne tourne.", sep=A)))
P[5].append(("25.5", pipe("pipe-crash", "Pourquoi le Pod est-il en CrashLoopBackOff ?",
 ["kubectl get pods -n crisisshield", "grep CrashLoop", "awk '{print $1}'", "xargs -I{} kubectl logs {} --previous -n crisisshield", "grep -iE 'error|exception' | head -3"],
 [st("get pods", ["api-7d9f-x1k2   0/1  CrashLoopBackOff  6  4m", "api-7d9f-m4n8   1/1  Running           0  4m", "db-0            1/1  Running           0  2d", "worker-5c8-p2   0/1  CrashLoopBackOff  6  4m"], "Deux Pods redémarrent en boucle ; les autres vont bien. Le nombre de redémarrages monte : le conteneur sort juste après avoir démarré."),
  st("grep CrashLoop", ["api-7d9f-x1k2   0/1  CrashLoopBackOff  6  4m", "worker-5c8-p2   0/1  CrashLoopBackOff  6  4m"], "On isole les Pods malades."),
  st("awk", ["api-7d9f-x1k2", "worker-5c8-p2"], "Seulement les noms, pour la commande suivante."),
  st("logs --previous", ["[x1k2] Caused by: java.net.ConnectException: db:5432", "[x1k2]   at HikariPool.getConnection", "[p2]   psycopg2.OperationalError: could not connect to db:5432", "…"], "--previous lit le conteneur qui vient de mourir, pas celui qui redémarre : sans lui, les logs sont vides."),
  st("grep error", ["ConnectException: db:5432", "OperationalError: could not connect to db:5432", "→ cause commune : la base est injoignable"], "Deux services, la même erreur : ce n'est pas l'application, c'est le chemin vers db. Suite : kubectl get endpointslices db, describe svc db, NetworkPolicy.", ["→ cause commune : la base est injoignable"])],
 "cause commune : db:5432 injoignable ; enquête sur le Service db, pas sur l'API",
 "get, grep, logs --previous : le diagnostic tient en une ligne. Une erreur partagée par plusieurs Pods pointe vers une dépendance, pas vers le code.")))
P[5].append(("26.2", pipe("pipe-route", "Comment une requête atteint-elle le bon Pod ?",
 ["https://api.crisisshield.example/incidents", "Ingress", "Service api", "EndpointSlice", "Pod (readiness)", "conteneur :8080"],
 [st("Ingress", ["host api.crisisshield.example", "  path /  → service api:80", "tls : secret api-tls (cert-manager)", "ingressClassName nginx"], "Le contrôleur d'ingress termine le TLS et route par nom d'hôte et chemin vers un Service."),
  st("Service", ["api  ClusterIP 10.96.12.5", "  port 80 → targetPort 8080", "  selector app=api"], "Le Service est une adresse stable ; il ne connaît pas les Pods, seulement un sélecteur de labels."),
  st("EndpointSlice", ["api-abc12", "  10.244.1.7:8080  ready", "  10.244.2.9:8080  ready", "  10.244.3.4:8080  NOT ready (démarrage)"], "Le contrôleur d'endpoints liste les Pods qui matchent le sélecteur ET sont Ready : le troisième n'y est pas."),
  st("Pod", ["api-7d9f-m4n8  10.244.2.9  Ready", "readiness /actuator/health/readiness 200", "kube-proxy (ou eBPF) : 10.96.12.5 → 10.244.2.9"], "kube-proxy traduit l'adresse du Service en adresse d'un Pod prêt, au hasard entre les prêts."),
  st("conteneur", ["GET /incidents HTTP/1.1", "200 OK, 31 ms", "log JSON avec trace_id"], "La requête arrive au conteneur sur 8080 ; la réponse remonte par le même chemin.", ["200 OK, 31 ms"])],
 "Ingress → Service → EndpointSlice → Pod prêt → :8080",
 "Quand « le Service ne répond pas », on suit cette chaîne : Ingress (hôte, classe), Service (sélecteur, targetPort), EndpointSlice (vide ?), readiness.", sep=A)))
P[5].append(("28.2", pipe("pipe-helm", "Que fait helm upgrade --install ?",
 ["helm upgrade --install api ./chart -f values-prod.yaml", "values", "template", "diff", "apply", "release"],
 [st("values", ["image.tag: 1.7.0", "replicaCount: 3", "resources.requests.memory: 512Mi", "ingress.host: api.crisisshield.example", "(défauts du chart + values-prod.yaml)"], "Les valeurs de production surchargent les défauts du chart ; helm show values montre tout ce qu'on peut régler."),
  st("template", ["Deployment api  (3 réplicas, image 1.7.0)", "Service api", "Ingress api", "ConfigMap api-config  (checksum a91f)", "ServiceAccount api"], "Les templates Go sont rendus avec les valeurs : des manifests Kubernetes ordinaires, qu'on peut lire avec helm template."),
  st("diff", ["~ Deployment api : image 1.6.2 → 1.7.0", "~ Deployment api : annotation checksum/config", "  Service, Ingress, SA : inchangés"], "helm diff (plugin) montre ce qui va changer avant d'appliquer : ici l'image et le checksum, qui force le rolling."),
  st("apply", ["Deployment mis à jour", "rolling update : 1 nouveau Pod à la fois", "readiness OK ×3", "--atomic : rollback automatique si échec"], "Helm applique les manifests ; Kubernetes fait le rolling update ; --atomic revient à la révision précédente si les Pods ne deviennent pas prêts."),
  st("release", ["api  révision 12  deployed", "révision 11  superseded (1.6.2)", "helm rollback api 11  ← une commande"], "Helm garde l'historique : chaque révision est restaurable.", ["api  révision 12  deployed"])],
 "révision 12 déployée, rollback en une commande",
 "Valeurs → templates → manifests → release : Helm est un moteur de rendu avec un historique. Le diff avant l'upgrade est la bonne pratique numéro un.", sep=A)))

# ================================================================ Niveau 6
P[6].append(("33.3", pipe("pipe-promql", "Comment se calcule le taux d'erreur du service api ?",
 ["http_server_requests_seconds_count", "rate(…[5m])", "sum by (service) (… {status=~\"5..\"})", "/ sum by (service) (…)", "* 100"],
 [st("séries brutes", ["{service=\"api\",status=\"200\"}  184 210", "{service=\"api\",status=\"500\"}    1 032", "{service=\"api\",status=\"404\"}    2 118", "{service=\"web\",status=\"200\"}   90 552", "{service=\"web\",status=\"500\"}      110"], "Un compteur par combinaison de labels, qui ne fait que monter depuis le démarrage : inutilisable tel quel."),
  st("rate 5m", ["api 200  61.4 /s", "api 500   0.34 /s", "api 404   0.71 /s", "web 200  30.2 /s", "web 500   0.04 /s"], "rate transforme les compteurs en débit par seconde sur une fenêtre de 5 minutes ; il gère les redémarrages (compteur remis à zéro)."),
  st("sum 5xx by service", ["api  0.34 /s", "web  0.04 /s"], "On ne garde que les statuts 5xx et on additionne par service : les autres labels disparaissent."),
  st("/ total", ["api  0.34 / 62.45 = 0.0054", "web  0.04 / 30.24 = 0.0013"], "Divisé par le débit total du même service : les deux membres doivent avoir les mêmes labels, d'où le sum by (service) des deux côtés."),
  st("* 100", ["api  0.54 %", "web  0.13 %", "SLO api : 99.9 % dispo → erreur max 0.1 %", "→ api consomme son budget 5 fois plus vite que prévu"], "Un pourcentage lisible. Comparé au SLO, l'API brûle son budget d'erreur : c'est cette valeur que l'alerte de burn rate surveille.", ["api  0.54 %"])],
 "api : 0,54 % d'erreurs, 5 fois le budget du SLO",
 "Compteur → rate → filtre → agrégation → ratio : toute requête PromQL utile suit ce chemin. Jamais de moyenne de latence, toujours histogram_quantile pour les percentiles.", sep=A)))
P[6].append(("32.3", pipe("pipe-logql", "Retrouver les erreurs d'un utilisateur dans Loki",
 ["{namespace=\"crisisshield\", app=\"api\"}", "| json", "| level=\"ERROR\"", "| user_id=\"u-4821\"", "| line_format \"{{.ts}} {{.msg}} trace={{.trace_id}}\""],
 [st("sélecteur de labels", ["2 flux : api-7d9f-x1k2, api-7d9f-m4n8", "184 000 lignes sur 1 h", "(index : namespace, app, pod)"], "Le sélecteur choisit les flux par labels indexés : c'est la seule partie rapide, tout le reste lit les lignes."),
  st("| json", ["ts=… level=INFO msg=\"incident created\" user_id=u-1201", "ts=… level=ERROR msg=\"payment refused\" user_id=u-4821 trace_id=4f2c", "ts=… level=WARN msg=\"slow query\"", "…"], "Chaque ligne JSON est parsée : ses champs deviennent des labels temporaires, sans avoir été indexés."),
  st("level=ERROR", ["ts=… level=ERROR msg=\"payment refused\" user_id=u-4821 trace_id=4f2c", "ts=… level=ERROR msg=\"db timeout\" user_id=u-0093 trace_id=88a1", "ts=… level=ERROR msg=\"payment refused\" user_id=u-4821 trace_id=51de", "… 212 lignes"], "Filtre sur un champ extrait : rapide même sur des millions de lignes, parce que Loki lit séquentiellement des blocs compressés."),
  st("user_id", ["ts=10:41:02 msg=\"payment refused\" trace_id=4f2c", "ts=10:52:17 msg=\"payment refused\" trace_id=51de"], "Deux erreurs pour cet utilisateur, chacune avec son trace_id."),
  st("line_format", ["10:41:02 payment refused trace=4f2c", "10:52:17 payment refused trace=51de", "→ cliquer trace=4f2c ouvre Tempo"], "La sortie est reformatée ; le trace_id relie le log à la trace complète de la requête.", ["→ cliquer trace=4f2c ouvre Tempo"])],
 "2 erreurs, 2 traces à ouvrir dans Tempo",
 "Labels pour choisir les flux, filtres pour tout le reste : indexer user_id serait une erreur de cardinalité ; le parser JSON à la volée fait le travail.", sep=A)))
P[6].append(("35.4", pipe("pipe-burn", "Faut-il réveiller l'astreinte ?",
 ["SLO : 99.9 % sur 30 jours", "budget d'erreur", "erreurs mesurées (1 h et 5 min)", "burn rate", "décision"],
 [st("SLO", ["disponibilité 99.9 % sur 30 jours", "→ erreurs tolérées : 0.1 % des requêtes", "→ 43 min d'indisponibilité totale par mois"], "Le SLO fixe combien d'échecs sont acceptables : c'est le budget d'erreur."),
  st("budget", ["requêtes / mois ≈ 160 M", "budget = 160 000 erreurs", "consommé depuis le 1er : 58 000 (36 %)", "reste : 102 000"], "Le budget se dépense ; l'objectif est de finir le mois sans l'épuiser, pas de le garder intact."),
  st("mesure", ["taux d'erreur 1 h  : 1.4 %", "taux d'erreur 5 min : 1.6 %", "(taux acceptable : 0.1 %)"], "On mesure sur deux fenêtres : longue pour éviter le bruit, courte pour savoir si c'est encore en cours."),
  st("burn rate", ["1 h   : 1.4 / 0.1 = 14×", "5 min : 1.6 / 0.1 = 16×", "à 14×, le budget du mois part en 2 jours"], "Le burn rate dit à quelle vitesse le budget brûle par rapport au rythme normal (1× = juste épuisé en fin de mois)."),
  st("décision", ["règle page : burn 1 h > 14.4 ET 5 min > 14.4", "→ 14 > 14.4 ? non… 16 > 14.4 oui", "→ condition 1 h non atteinte : ticket, pas page", "→ si ça continue 10 min : page"], "Deux fenêtres, deux seuils : on page seulement quand le problème est à la fois grave et en cours. Ici, à la limite : ticket immédiat, page dans dix minutes si rien ne change.", ["→ condition 1 h non atteinte : ticket, pas page"])],
 "burn rate 14× : ticket maintenant, page si ça persiste",
 "L'alerte sur le burn rate remplace les seuils arbitraires : elle ne réveille que pour ce qui menace réellement le SLO, et elle se tait pour un pic de deux minutes.", sep=A)))

# ================================================================ Niveau 7
P[7].append(("37.4", pipe("pipe-triage", "Une CVE critique vient de sortir : que fait l'équipe, dans l'ordre ?",
 ["CVE publiée", "SBOM : qui est touché ?", "exploitable ?", "mitiger", "corriger", "vérifier", "documenter"],
 [st("CVE", ["CVE-2026-1234  curl  CVSS 9.8", "exécution de code via redirection", "correctif : curl 8.6.1"], "L'alerte arrive (Dependency-Track, veille) avec la gravité et la version corrigée."),
  st("SBOM", ["images contenant curl < 8.6.1 :", "  api:1.7.0        (base temurin 21)", "  worker:2.3.1     (base temurin 21)", "  legacy:0.9       (base debian 11)", "3 images, 2 bases"], "En secondes : quelles images, quelles bases ; sans SBOM, c'est une journée."),
  st("exploitable ?", ["EPSS : 0.71 (fort)  KEV : oui", "api : curl appelé par le code ? non", "worker : oui (webhooks sortants)  ← exposé", "legacy : réseau sortant bloqué"], "Priorité par probabilité d'exploitation et par exposition réelle : un seul service est réellement à risque."),
  st("mitiger", ["worker : NetworkPolicy egress limitée aux domaines connus", "WAF : règle sur les redirections", "→ risque réduit en 20 min, sans déploiement de code"], "On réduit l'exposition tout de suite, avant même le correctif."),
  st("corriger", ["Renovate : MR base image temurin 21-jre-2026-09-22", "rebuild api, worker, legacy", "scan : 0 Critical", "déploiement canary → prod"], "Le correctif est une mise à jour d'image de base : trois rebuilds, le pipeline habituel."),
  st("vérifier", ["trivy image api → curl 8.6.1  OK", "SBOM régénérés", "Dependency-Track : 0 projet affecté"], "La preuve vient des outils, pas d'un mail « c'est fait »."),
  st("documenter", ["VEX : api, legacy = not_affected (non exploitable)", "worker = fixed", "post-mortem si exploitation détectée ; sinon fiche de 10 lignes"], "Le VEX explique aux auditeurs et aux clients pourquoi deux images n'étaient pas affectées : on ne corrige pas tout en urgence, on justifie.", ["worker = fixed"])],
 "3 h de l'alerte au correctif en production, 1 service réellement exposé",
 "SBOM, exploitabilité, mitigation, correctif, preuve, VEX : c'est le déroulé attendu en entretien pour « Log4Shell sort demain, que faites-vous ? ».", sep=A)))
P[7].append(("38.3", pipe("pipe-vault", "Comment le Pod obtient-il un mot de passe de base sans que personne ne le connaisse ?",
 ["Pod démarre", "jeton de ServiceAccount", "vault login (auth kubernetes)", "vault read database/creds/api", "PostgreSQL", "expiration"],
 [st("Pod", ["Pod api-7d9f-x1k2", "ServiceAccount api", "jeton projeté, audience vault, 1 h", "aucun secret dans le manifest"], "Le Pod n'a qu'une identité Kubernetes : un jeton signé par le cluster, monté automatiquement."),
  st("auth kubernetes", ["POST /auth/kubernetes/login  role=api", "Vault vérifie le jeton auprès de l'API Kubernetes", "→ SA api dans ns crisisshield : OK", "→ token Vault, politique api-db, TTL 1 h"], "Vault fait confiance au cluster, pas à un secret partagé : le rôle lie un ServiceAccount précis à une politique."),
  st("database/creds", ["Vault se connecte à PostgreSQL avec son compte root", "CREATE ROLE \"v-k8s-api-x8f2…\" PASSWORD '…' VALID UNTIL '+1h'", "GRANT app_rw", "→ username v-k8s-api-x8f2, password (unique)"], "Vault crée un compte à la volée, avec une durée de vie : chaque Pod a le sien."),
  st("application", ["HikariCP : jdbc:postgresql://db/crisis", "user v-k8s-api-x8f2", "connexions établies", "renouvellement du bail à 45 min"], "L'application utilise l'identifiant reçu ; l'agent ou la bibliothèque renouvelle le bail avant expiration."),
  st("expiration", ["Pod supprimé → bail révoqué", "DROP ROLE v-k8s-api-x8f2", "audit Vault : qui, quand, quel rôle", "mot de passe root : tourné par Vault, connu de personne"], "Plus de Pod, plus de compte : un identifiant volé dans un dump de mémoire expire en moins d'une heure.", ["mot de passe root : tourné par Vault, connu de personne"])],
 "un compte par Pod, valable 1 h, jamais écrit nulle part",
 "Identité (jeton) → confiance (rôle) → secret dynamique (bail) → révocation : la hiérarchie des secrets en action, et la réponse à « comment gérez-vous les secrets ? ».", sep=A)))
P[7].append(("40.4", pipe("pipe-supply", "De la source à l'image vérifiée : la chaîne d'approvisionnement",
 ["commit signé", "build sur runner éphémère", "SBOM + provenance", "cosign sign", "registre", "admission Kyverno", "déploiement par digest"],
 [st("commit", ["a1b2c3  feat(api): export CSV", "signature SSH : gael@… vérifiée", "branche main, MR approuvée par 1 relecteur"], "L'origine est prouvée : commit signé, revue obligatoire, branche protégée."),
  st("build", ["runner Kubernetes éphémère, sans socket Docker", "Kaniko : image api:a1b2c3", "dépendances via proxy Nexus (lockfile)", "digest sha256:3f9c…"], "Le build est reproductible et isolé : aucun outil du poste, aucune dépendance directe d'Internet."),
  st("SBOM + provenance", ["syft → sbom.cdx.json (214 composants)", "attestation SLSA provenance : builder, source, commit", "→ attachées au digest"], "On sait ce que contient l'image et qui l'a construite à partir de quoi."),
  st("cosign sign", ["cosign sign --yes api@sha256:3f9c…", "identité OIDC : job de CI, branche main", "signature dans Rekor (journal public)", "cosign attest --type cyclonedx"], "Signature keyless : la clé est l'identité du job ; le journal de transparence rend la signature vérifiable par tous."),
  st("registre", ["harbor/crisisshield/api", "  sha256:3f9c…  signé  SBOM  provenance", "  tag 1.7.0 → 3f9c…", "scan Harbor : 0 Critical"], "Le registre garde l'image et ses attestations ; le tag n'est qu'un alias vers le digest."),
  st("admission", ["Kyverno verifyImages :", "  registre autorisé      OK", "  signature (issuer, subject main) OK", "  attestation SBOM       OK", "  mutateDigest : tag → digest"], "Le cluster refuse toute image non signée par le bon job ; il remplace le tag par le digest vérifié."),
  st("déploiement", ["Deployment api : image api@sha256:3f9c…", "ArgoCD : synchronisé depuis Git", "→ ce qui tourne est exactement ce qui a été construit, signé, scanné"], "La chaîne se ferme : de la source au Pod, chaque maillon a produit une preuve que le suivant a vérifiée.", ["→ ce qui tourne est exactement ce qui a été construit, signé, scanné"])],
 "7 maillons, 7 preuves : provenance, contenu, signature, vérification",
 "Trois questions à chaque étape : d'où ça vient, qu'est-ce que ça contient, qui l'a signé. SLSA et Sigstore ne sont que l'outillage de ces trois questions.", sep=A)))
P[7].append(("41.5", pipe("pipe-oauth", "Que se passe-t-il quand l'opérateur clique « Se connecter » ?",
 ["clic Se connecter", "redirection vers Keycloak", "authentification + MFA", "code d'autorisation", "échange code + PKCE", "jetons", "appel API"],
 [st("BFF", ["génère code_verifier (aléatoire)", "code_challenge = SHA256(verifier)", "state = 7f2a…, nonce = 9c1e…", "→ 302 vers /realms/crisis/protocol/openid-connect/auth"], "Le client prépare la preuve PKCE et des valeurs anti-rejeu ; aucun secret n'est envoyé au navigateur."),
  st("Keycloak", ["client_id=crisisshield-web", "redirect_uri=https://app…/callback  (liste blanche)", "scope=openid profile", "code_challenge_method=S256"], "Keycloak vérifie que le client et l'URL de retour sont connus ; sinon, il refuse avant tout login."),
  st("login", ["mot de passe  OK", "passkey (WebAuthn)  OK", "consentement : non requis (client interne)", "session SSO créée"], "L'utilisateur s'authentifie chez l'IdP, jamais dans l'application ; le second facteur résiste au phishing."),
  st("code", ["302 → https://app…/callback?code=Xy9…&state=7f2a…", "le BFF vérifie state = 7f2a… OK", "code : usage unique, 60 s"], "Le code ne vaut rien seul : il faut le code_verifier pour l'échanger."),
  st("échange", ["POST /token", "  grant_type=authorization_code", "  code=Xy9…  code_verifier=…", "Keycloak : SHA256(verifier) = challenge ? OK"], "PKCE prouve que celui qui échange est celui qui a lancé la demande : un code intercepté est inutilisable."),
  st("jetons", ["access_token  (JWT, 5 min, aud=crisisshield-api)", "id_token      (JWT, nonce=9c1e… vérifié)", "refresh_token (30 min, rotation)", "→ BFF stocke tout, cookie de session HttpOnly au navigateur"], "Trois jetons, trois usages ; le JavaScript ne voit aucun d'eux."),
  st("API", ["GET /api/incidents  Authorization: Bearer …", "API : alg RS256 OK, JWKS OK, iss OK, aud OK, exp OK", "rôle operator OK, organisation = celle du jeton", "→ 200"], "L'API valide le jeton en sept points sans appeler Keycloak, puis applique le contrôle d'accès par objet.", ["→ 200"])],
 "Authorization Code + PKCE, BFF, jetons courts, validation en sept points",
 "Chaque étape a une raison de sécurité : state contre le CSRF, nonce contre le rejeu, PKCE contre l'interception, BFF contre le XSS, audience contre la réutilisation.", sep=A)))

# ================================================================ Niveau 8
P[8].append(("43.2", pipe("pipe-errbudget", "Le produit veut livrer vendredi : que dit la politique de budget d'erreur ?",
 ["SLO du mois", "budget", "incidents du mois", "reste", "politique", "décision"],
 [st("SLO", ["api : 99.9 % de requêtes réussies", "checkout : 99.95 %", "période : 30 jours glissants"], "Chaque service a son objectif, négocié avec le produit."),
  st("budget", ["api : 0.1 % de 160 M = 160 000 erreurs", "checkout : 0.05 % de 12 M = 6 000 erreurs"], "Le budget est la quantité d'échec tolérée avant que le SLO ne soit rompu."),
  st("incidents", ["12/09 déploiement raté api : 95 000 erreurs", "18/09 panne base : api 60 000, checkout 5 200", "20/09 pic de charge : api 12 000"], "Les incidents du mois consomment le budget ; chacun est mesuré, pas estimé."),
  st("reste", ["api : 160 000 − 167 000 = −7 000  (épuisé, −4 %)", "checkout : 6 000 − 5 200 = 800  (13 % restant)"], "L'API a dépassé son budget ; checkout est presque à sec."),
  st("politique", ["budget épuisé → gel des changements non liés à la fiabilité", "budget < 20 % → déploiements canary obligatoires, pas de vendredi", "signée par produit et ingénierie le 3 mars"], "La politique a été écrite à froid, avant l'incident : c'est ce qui la rend applicable."),
  st("décision", ["api : livraison vendredi refusée", "  sauf correctif de fiabilité", "checkout : autorisé lundi, en canary 5 % → 50 % → 100 %", "→ compte rendu au sponsor, pas de négociation à chaud"], "Le Tech Lead SRE n'arbitre pas à l'émotion : il applique une règle que le produit a signée, et propose la voie de sortie.", ["api : livraison vendredi refusée"])],
 "api gelé jusqu'à retour du budget ; checkout en canary lundi",
 "Le budget d'erreur transforme « on livre ou pas ? » en calcul : c'est l'outil qui rend le SRE crédible face au produit.", sep=A)))
P[8].append(("47.2", pipe("pipe-expand", "Renommer une colonne sans interrompre le service",
 ["état initial", "1. expand", "2. double écriture", "3. migration des données", "4. bascule lecture", "5. contract"],
 [st("initial", ["table incidents : zone_name varchar", "code v1 : lit et écrit zone_name", "3 réplicas de l'API en production"], "Objectif : passer de zone_name à zone_code sans que les utilisateurs ne voient rien."),
  st("expand", ["ALTER TABLE incidents ADD COLUMN zone_code varchar NULL;", "(instantané : pas de réécriture de table)", "code v1 : inchangé, ignore la colonne"], "On ajoute sans rien retirer : le schéma est compatible avec le code en place."),
  st("double écriture", ["déploiement v2 (rolling, 1 Pod à la fois)", "v2 écrit zone_name ET zone_code", "v2 lit encore zone_name", "v1 et v2 coexistent pendant le rolling : OK"], "Pendant le rolling, les deux versions écrivent quelque chose de valide."),
  st("migration", ["UPDATE incidents SET zone_code = map(zone_name)", "  WHERE zone_code IS NULL  — par lots de 5 000", "lock_timeout = 3 s, entre 22 h et 6 h", "2.1 M lignes en 40 min, sans blocage"], "L'ancien stock est rempli par lots : jamais un UPDATE massif qui verrouille la table."),
  st("bascule lecture", ["déploiement v3 : lit zone_code, écrit les deux", "vérification : 0 ligne avec zone_code NULL", "rollback possible : v2 lit encore zone_name"], "La lecture bascule quand toutes les lignes sont prêtes ; le rollback du code reste possible."),
  st("contract", ["une semaine plus tard, aucun incident :", "déploiement v4 : n'écrit plus zone_name", "ALTER TABLE incidents DROP COLUMN zone_name;", "→ terminé, zéro interruption"], "On retire l'ancien seulement quand plus personne ne le lit ni ne l'écrit, avec du recul.", ["→ terminé, zéro interruption"])],
 "5 étapes, 4 déploiements, 0 seconde d'interruption",
 "Expand, migrate, contract : chaque déploiement est compatible avec le précédent et le suivant, ce qui rend le rollback toujours possible.", sep=A)))
P[8].append(("45.2", pipe("pipe-trace", "Une requête en 780 ms : où part le temps ?",
 ["GET /incidents/42", "trace", "spans triés", "le plus long", "hypothèse", "correction"],
 [st("trace", ["trace 4f2c… durée 780 ms", "12 spans, 3 services", "api → geo-service → PostgreSQL"], "La trace distribuée montre la requête de bout en bout, service par service."),
  st("spans", ["api        HTTP GET /incidents/42         780 ms", "api        SELECT incident               18 ms", "api        → geo-service /zones/nord     640 ms", "geo        SELECT zones WHERE code=…      610 ms", "api        sérialisation JSON            12 ms"], "Chaque span est une étape avec sa durée ; les spans enfants expliquent le parent."),
  st("tri", ["geo  SELECT zones           610 ms  (78 %)", "api  → geo-service          640 ms  (dont 610 attente)", "api  SELECT incident         18 ms", "api  JSON                    12 ms"], "Trié par durée : un seul span explique presque tout."),
  st("le plus long", ["geo-service : SELECT * FROM zones WHERE code = $1", "EXPLAIN : Seq Scan on zones (rows=2 100 000)", "aucun index sur zones.code"], "On regarde la requête : un Seq Scan sur deux millions de lignes."),
  st("hypothèse", ["un index sur zones(code) ramènerait à ~2 ms", "vérification en staging avec les données de prod (copie)", "p95 mesuré avant : 780 ms"], "On ne suppose pas, on teste sur une copie réaliste."),
  st("correction", ["CREATE INDEX CONCURRENTLY ON zones (code);", "p95 après : 96 ms", "cache 60 s côté api : p95 41 ms", "→ trace 4f2c… relancée : 44 ms"], "Le plus gros segment d'abord ; ensuite seulement le second levier (cache). On remesure à chaque étape.", ["→ trace 4f2c… relancée : 44 ms"])],
 "780 ms → 44 ms : un index, puis un cache, mesurés",
 "Trace, tri par durée, plus gros segment, hypothèse, test, mesure : la méthode évite d'optimiser ce qu'on connaît le mieux au lieu de ce qui coûte.", sep=A)))

# ================================================================ Niveau 9
P[9].append(("52.2", pipe("pipe-dora", "Comment se calcule le délai de livraison (lead time) ?",
 ["commits (Git)", "déploiements (CI)", "jointure", "durées", "médiane"],
 [st("commits", ["a1b2c3  2026-09-15 09:12  feat: export", "d4e5f6  2026-09-15 14:40  fix: zone", "789abc  2026-09-16 10:05  feat: alertes", "m0e1r2  2026-09-17 16:30  chore: deps"], "Chaque commit sur main a une date : c'est le début du chronomètre."),
  st("déploiements", ["deploy #1842  2026-09-15 16:02  contient a1b2c3, d4e5f6", "deploy #1851  2026-09-16 11:20  contient 789abc", "deploy #1860  2026-09-18 09:45  contient m0e1r2"], "Chaque déploiement en production est horodaté et sait quels commits il embarque (tags d'image, changelog)."),
  st("jointure", ["a1b2c3 → #1842", "d4e5f6 → #1842", "789abc → #1851", "m0e1r2 → #1860"], "On associe chaque commit au premier déploiement qui le contient."),
  st("durées", ["a1b2c3 : 6 h 50", "d4e5f6 : 1 h 22", "789abc : 1 h 15", "m0e1r2 : 17 h 15  (déployé le lendemain)"], "Le délai de chaque commit, du commit à la production."),
  st("médiane", ["triées : 1 h 15, 1 h 22, 6 h 50, 17 h 15", "médiane = (1 h 22 + 6 h 50) / 2 ≈ 4 h 06", "catégorie DORA : High (< 1 jour)", "→ objectif : Elite (< 1 h) en déployant à chaque merge"], "La médiane résiste aux valeurs extrêmes ; un commit attendu toute une nuit ne fausse pas la tendance.", ["médiane = (1 h 22 + 6 h 50) / 2 ≈ 4 h 06"])],
 "lead time médian 4 h 06, catégorie High",
 "Deux horodatages et une jointure : toute métrique DORA se calcule à partir de ce que Git et la CI savent déjà. Aucune saisie manuelle.", sep=A)))
P[9].append(("54.8", pipe("pipe-rag", "Que se passe-t-il quand un opérateur pose une question à l'assistant ?",
 ["question", "garde-fous d'entrée", "recherche filtrée par droits", "prompt", "modèle via la passerelle", "validation de sortie", "réponse + trace"],
 [st("question", ["« Quelle procédure pour une coupure d'eau en zone nord ? »", "utilisateur u-4821, organisation Nord, rôle operator"], "La question arrive avec l'identité de l'utilisateur, pas seulement du texte."),
  st("garde-fous", ["longueur OK, langue fr", "injection ? aucun motif détecté", "données personnelles : aucune", "→ accepté"], "On filtre avant de dépenser des tokens : taille, injection, données sensibles."),
  st("recherche", ["filtre : org = Nord OU public", "vecteurs (pgvector) top 20 + BM25 top 20", "reranking → 4 passages", "  runbook-eau-nord.md §3   0.91", "  fiche-incident-2025-11   0.84"], "Le filtre de droits s'applique AVANT le classement : un passage de l'organisation Sud n'entre jamais dans le contexte."),
  st("prompt", ["système : rôle, format JSON attendu, « cite tes sources »", "contexte : 4 passages (1 900 tokens)", "question", "total 2 400 tokens"], "Le prompt est assemblé à partir de gabarits versionnés ; le contexte est borné."),
  st("passerelle", ["auth OK, quota u-4821 : 41/200 aujourd'hui", "journal : prompt, modèle, tokens", "cache sémantique : miss", "modèle standard (pas premium) : 0,004 $"], "Un seul point de contrôle pour l'authentification, les quotas, le journal et le coût."),
  st("validation", ["JSON conforme au schéma  OK", "sources citées présentes dans le contexte  OK", "filtre de sortie : aucune donnée personnelle", "→ accepté"], "La sortie est vérifiée comme une entrée utilisateur : jamais affichée ni exécutée sans validation."),
  st("réponse", ["« Fermer la vanne V-12, prévenir … » + 2 sources cliquables", "trace OTel : 1,8 s, 2 400 tokens, 0,004 $", "eval hors ligne : cas ajouté au jeu de test"], "L'opérateur voit la réponse et ses sources ; l'équipe voit la trace et le coût ; la question enrichit les tests.", ["« Fermer la vanne V-12, prévenir … » + 2 sources cliquables"])],
 "réponse sourcée en 1,8 s, droits respectés, coût connu",
 "Le modèle est une étape sur sept : les droits à la récupération, la validation de sortie et la passerelle sont ce qui rend l'assistant utilisable en production.", sep=A)))

# ================================================================ insertion
for lvl, items in P.items():
    fn = out/L[lvl]; s = fn.read_text()
    if 'class="pipe"' in s: print(fn.name, 'déjà fait'); continue
    s = s.replace('</style>', CSS + '</style>', 1) if '</style>' not in CSS else s.replace('</style>', CSS, 1)
    n = 0
    for sec, block in items:
        m = re.search(r'<h3>' + re.escape(sec) + r' [^<]*(?:<span class="badge[^<]*</span>)?</h3>', s)
        if not m:
            ch = sec.split('.')[0]; m = re.search(r'<h3>' + re.escape(ch) + r'\.1 [^<]*(?:<span class="badge[^<]*</span>)?</h3>', s); print('  repli sur', ch + '.1 pour', sec)
        assert m, (fn.name, sec)
        j = m.end()
        while True:
            m2 = re.match(r'\n(<figure class="fig(?: manga)?">.*?</figure>)', s[j:], flags=re.S)
            if not m2: break
            j += m2.end()
        s = s[:j] + '\n' + block + s[j:]; n += 1
    s = s.replace('</body>', JS + '</body>', 1)
    fn.write_text(s); print(fn.name, n, 'pipelines')
