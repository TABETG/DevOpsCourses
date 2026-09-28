"""Cours Alibaba Cloud de zéro à expert (10 chapitres). Usage : python3 alibaba_pages.py <dossier>"""
import sys, runpy, pathlib
g = runpy.run_path(pathlib.Path(__file__).with_name('front_gen.py'), run_name='front'); ch, page = g['ch'], g['page']
def T(rows, head): return '<div class="tablewrap"><table><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table></div>'
DK = "Tout en conteneur : Terraform (<code>hashicorp/terraform</code>) avec le fournisseur <code>aliyun/alicloud</code>, et la CLI <code>aliyun</code> dans une petite image construite à partir de son binaire officiel. Les identifiants viennent de variables d'environnement, jamais du dépôt."
DOC = "Les noms de services, d'offres et d'arguments évoluent : on vérifie la documentation d'Alibaba Cloud et du fournisseur Terraform pour la version utilisée."

AL = [
ch("Découvrir Alibaba Cloud : régions, sites, comptes, correspondances", 'j',
 ["Alibaba Cloud est le premier fournisseur en Chine et très présent en Asie ; ses services couvrent calcul, réseau, stockage, bases, données, IA et sécurité, avec des équivalents de ceux d'AWS.", "Deux mondes à distinguer : le site international (alibabacloud.com) et le site Chine continentale (aliyun.com), avec des comptes, des régions et des obligations différents (déclaration ICP pour un site web hébergé en Chine).", "On apprend vite en partant des correspondances avec AWS, puis en étudiant les différences qui piègent : réseau, quotas, nommage, facturation."],
 ["Choisir région et site selon les utilisateurs et les obligations", "Traduire ses repères AWS en services Alibaba Cloud", "Ouvrir et sécuriser un compte, piloter la facturation"],
 [("Correspondances avec AWS", T([
    ("Compte, organisation", "AWS Organizations", "Resource Directory"),
    ("Identités", "IAM, STS", "RAM (Resource Access Management), STS"),
    ("Réseau", "VPC, sous-réseau, Transit Gateway", "VPC, vSwitch, CEN (Transit Router)"),
    ("Équilibreur de charge", "ALB, NLB, CLB", "Server Load Balancer : ALB, NLB, CLB"),
    ("Machines virtuelles", "EC2, Auto Scaling", "ECS (Elastic Compute Service), Auto Scaling"),
    ("Conteneurs, fonctions", "EKS, Fargate, Lambda", "ACK, ECI, Function Compute"),
    ("Objets, disques", "S3, EBS", "OSS, disques ESSD"),
    ("Bases relationnelles", "RDS, Aurora", "ApsaraDB RDS, PolarDB"),
    ("Cache, NoSQL", "ElastiCache, DynamoDB", "Tair (compatible Redis), Tablestore"),
    ("Données", "Redshift, EMR, Glue", "AnalyticDB, E-MapReduce, DataWorks, MaxCompute"),
    ("Surveillance, journaux, audit", "CloudWatch, CloudTrail", "CloudMonitor, Simple Log Service (SLS), ActionTrail"),
    ("Infrastructure comme code", "CloudFormation", "ROS (Resource Orchestration Service), Terraform"),
    ("Clés, sécurité", "KMS, GuardDuty, WAF, Shield", "KMS, Security Center, WAF, Anti-DDoS")], ("Besoin", "AWS", "Alibaba Cloud")), None),
  ("Site international ou Chine continentale", "Pour des utilisateurs en Chine, les régions de Chine continentale offrent la meilleure latence mais imposent un compte adapté, une déclaration ICP pour tout site web hébergé, et le respect des règles chinoises sur les données. Pour l'Europe ou l'Asie hors Chine, le site international et ses régions (Francfort, Londres, Singapour…) suffisent.", None),
  ("Démarrer proprement", DK, """# compte principal : MFA, aucune AccessKey ; travail quotidien par utilisateurs RAM ou rôles (chapitre 2)
# budget et alertes : Centre de facturation → alertes de dépenses (seuils) ; étiquettes projet, environnement, équipe
# CLI en conteneur (image construite à partir du binaire officiel « aliyun »)
docker run --rm -e ALIBABA_CLOUD_ACCESS_KEY_ID -e ALIBABA_CLOUD_ACCESS_KEY_SECRET -e ALIBABA_CLOUD_REGION_ID=eu-central-1 \\
  outils/aliyun-cli ecs DescribeRegions
# modes de facturation : paiement à l'usage, abonnement (moins cher sur la durée), plans d'économie, instances préemptibles""")],
 [("Une filiale veut ouvrir un site web pour des clients en Chine continentale en utilisant son compte international et une région de Singapour. Qu'en penses-tu ?", "La latence depuis la Chine sera médiocre et variable ; pour un hébergement en Chine continentale, il faut un compte adapté, une région chinoise et une déclaration ICP avant la mise en ligne, avec un avis juridique sur les données. Singapour peut servir pour l'Asie hors Chine."),
  ("Question d'entretien : comment apprends-tu un nouveau cloud quand tu connais AWS ?", "Par les correspondances de services, puis en cherchant les différences qui piègent (identités, réseau, quotas, facturation, obligations locales), et en déployant tout de suite un petit projet en code pour vérifier ses hypothèses.")],
 ("Premier pas sur Alibaba Cloud", ["Ouvrir un compte international, activer la MFA, créer un utilisateur RAM d'administration et des alertes de dépenses.", "Construire l'image de la CLI aliyun et lister régions et zones.", "Remplir le tableau de correspondances pour les dix services de CrisisShield."],
  "Attendu : aucune AccessKey sur le compte principal ; la CLI tourne en conteneur avec des identifiants d'un utilisateur RAM ; le tableau signale au moins trois différences importantes avec AWS.")),

ch("Identités et accès : RAM, STS, Resource Directory, ActionTrail", 'c',
 ["RAM gère utilisateurs, groupes, rôles et politiques ; les politiques JSON ressemblent à celles d'IAM, avec des ressources nommées acs:… et une version « 1 ».", "Les applications et les services utilisent des rôles RAM et des identifiants temporaires obtenus par STS ; les AccessKey permanentes restent l'exception, surtout sur le compte principal.", "Resource Directory organise plusieurs comptes membres ; ActionTrail enregistre les actions, à conserver dans OSS ou SLS."],
 ["Écrire des politiques RAM au moindre privilège", "Utiliser rôles et STS pour les applications", "Organiser plusieurs comptes et tracer les actions"],
 [("Une politique RAM", "Même logique qu'IAM : actions et ressources précises, conditions (adresse source, MFA). On attache les politiques à des groupes ou des rôles, pas aux personnes une par une.", """{ "Version": "1",
  "Statement": [
    { "Effect": "Allow",
      "Action": ["oss:GetObject", "oss:PutObject"],
      "Resource": ["acs:oss:*:*:crise-pieces-jointes/incidents/*"] },
    { "Effect": "Deny",
      "Action": ["oss:DeleteBucket"],
      "Resource": ["acs:oss:*:*:crise-pieces-jointes"] } ] }"""),
  ("Rôles et identifiants temporaires", "Une instance ECS reçoit un rôle RAM : l'application obtient des identifiants temporaires par les métadonnées de l'instance, sans clé stockée. Dans ACK, les Pods utilisent l'identité liée au compte de service (RRSA) ; une CI externe endosse un rôle par STS.", """# rôle RAM attaché à l'instance ; le SDK récupère seul des identifiants temporaires
# endosser un rôle depuis la CI (identifiants de la CI limités à sts:AssumeRole)
docker run --rm -e ALIBABA_CLOUD_ACCESS_KEY_ID -e ALIBABA_CLOUD_ACCESS_KEY_SECRET outils/aliyun-cli \\
  sts AssumeRole --RoleArn acs:ram::1234567890123456:role/deploiement-crise --RoleSessionName ci-$CI_PIPELINE_ID --DurationSeconds 3600"""),
  ("Plusieurs comptes et traces", "Resource Directory regroupe les comptes (production, recette, sécurité) en dossiers, avec des politiques de contrôle qui plafonnent les droits. ActionTrail enregistre chaque action et les livre dans un compartiment OSS ou un projet SLS du compte de sécurité.", None)],
 [("Un script de déploiement utilise l'AccessKey du compte principal, stockée dans le dépôt. Priorités ?", "Désactiver et supprimer cette AccessKey, vérifier dans ActionTrail son usage passé, créer un rôle de déploiement au moindre privilège endossé par STS, et ajouter une détection de secrets en CI."),
  ("Question d'entretien : RAM et IAM, quelles différences retenir ?", "Les principes sont les mêmes (utilisateurs, rôles, politiques JSON, identifiants temporaires) ; la syntaxe diffère (Version « 1 », ressources acs:…), les noms des actions aussi, et l'organisation multi-comptes passe par Resource Directory.")],
 ("Identités de CrisisShield", ["Groupes RAM (administration, lecture), rôle de l'application sur ECS, rôle de déploiement pour la CI.", "Politique OSS limitée au préfixe des pièces jointes, refus explicite de suppression du compartiment.", "ActionTrail livré dans un compte de sécurité ; retrouver l'auteur d'une action de test."],
  "Attendu : aucune AccessKey permanente hors d'un utilisateur de CI limité à AssumeRole ; l'application ne peut rien supprimer ; ActionTrail montre qui a fait l'action de test.")),

ch("Réseau : VPC, vSwitch, groupes de sécurité, SLB, CEN", 'c',
 ["Un VPC par environnement et par région ; ses sous-réseaux s'appellent vSwitch et vivent chacun dans une zone.", "Les groupes de sécurité filtrent le trafic des instances ; la passerelle NAT et les adresses IP élastiques (EIP) gèrent les sorties et les entrées publiques.", "Server Load Balancer (ALB, NLB, CLB) expose les services ; CEN et son Transit Router relient VPC et régions, Express Connect relie un site."],
 ["Construire un VPC multi-zones en code", "Filtrer et exposer correctement", "Relier des réseaux avec CEN et Express Connect"],
 [("Un VPC en Terraform", DK, """terraform {
  required_providers { alicloud = { source = "aliyun/alicloud" } }
}
provider "alicloud" { region = "eu-central-1" }          # identifiants par variables d'environnement
resource "alicloud_vpc" "crise" {
  vpc_name   = "crise-prod"
  cidr_block = "10.30.0.0/16"
}
resource "alicloud_vswitch" "app_a" {
  vpc_id       = alicloud_vpc.crise.id
  cidr_block   = "10.30.10.0/24"
  zone_id      = "eu-central-1a"
  vswitch_name = "app-a"
}
resource "alicloud_vswitch" "app_b" {
  vpc_id       = alicloud_vpc.crise.id
  cidr_block   = "10.30.11.0/24"
  zone_id      = "eu-central-1b"
  vswitch_name = "app-b"
}"""),
  ("Filtrer et exposer", "Les instances applicatives n'ont pas d'adresse publique : elles sortent par la passerelle NAT, et seul l'équilibreur de charge est exposé. Les ports d'administration ne sont jamais ouverts au monde ; l'accès passe par un bastion géré ou une connexion d'administration contrôlée.", """resource "alicloud_security_group" "app" {
  security_group_name = "app"
  vpc_id              = alicloud_vpc.crise.id
}
resource "alicloud_security_group_rule" "http_depuis_vpc" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "8080/8080"
  cidr_ip           = "10.30.0.0/16"        # seulement depuis le VPC (équilibreur)
  security_group_id = alicloud_security_group.app.id
}
# jamais : port_range = "22/22" avec cidr_ip = "0.0.0.0/0\""""),
  ("Relier des réseaux", "", T([
    ("CEN et Transit Router", "relier des VPC et des régions", "concentrateur, routage central"),
    ("Express Connect", "lien dédié avec un site", "débit et latence maîtrisés"),
    ("VPN Gateway", "relier un site par Internet", "chiffré, rapide à mettre en place"),
    ("PrivateLink", "exposer un service à d'autres VPC", "sans relier les réseaux")], ("Option", "Pour", "À retenir")))],
 [("Les instances de recette sont accessibles en SSH depuis Internet « pour dépanner ». Que proposes-tu ?", "Fermer le port 22 au monde, retirer les adresses publiques, administrer par un bastion géré ou une session contrôlée avec journalisation, et vérifier les tentatives de connexion passées."),
  ("Question d'entretien : un vSwitch, c'est quoi ?", "Le sous-réseau d'un VPC Alibaba Cloud, rattaché à une zone de disponibilité : on en crée au moins un par zone et par usage (application, données) pour répartir les ressources.")],
 ("Réseau de CrisisShield sur Alibaba Cloud", ["VPC et vSwitch sur deux zones, en Terraform exécuté en conteneur.", "Groupes de sécurité chaînés, passerelle NAT, équilibreur ALB seul exposé.", "Schéma de liaison avec AWS (VPN ou CEN) pour un scénario multi-cloud."],
  "Attendu : terraform plan relu en MR, apply par la CI ; seule l'adresse de l'équilibreur est publique ; aucun port d'administration ouvert à 0.0.0.0/0.")),

ch("Calcul : ECS, Auto Scaling, ECI, Function Compute", 'c',
 ["ECS (Elastic Compute Service) fournit des machines virtuelles, créées à partir d'images et de modèles de lancement, regroupées par Auto Scaling.", "Les instances préemptibles coûtent beaucoup moins cher mais peuvent être reprises : on les réserve à ce qui supporte l'interruption.", "ECI lance des conteneurs sans serveur à gérer ; Function Compute exécute des fonctions déclenchées par événements."],
 ["Déployer des instances ECS en groupe Auto Scaling", "Choisir le bon mode de facturation du calcul", "Utiliser ECI et Function Compute à bon escient"],
 [("Instances et Auto Scaling", "Une image personnalisée (construite par Packer) et un modèle de lancement décrivent l'instance ; le groupe Auto Scaling maintient le nombre d'instances saines sur plusieurs zones et les attache à l'équilibreur de charge.", """resource "alicloud_instance" "api" {
  instance_name        = "api-crise"
  instance_type        = "ecs.g7.large"
  image_id             = var.image_doree_id               # image construite par Packer
  vswitch_id           = alicloud_vswitch.app_a.id
  security_groups      = [alicloud_security_group.app.id]
  role_name            = "api-crise"                      # rôle RAM : identifiants temporaires
  internet_max_bandwidth_out = 0                          # pas d'adresse publique
}
# en production : groupe Auto Scaling (alicloud_ess_scaling_group) sur deux vSwitch, rattaché à l'ALB"""),
  ("Modes de facturation", "", T([
    ("Paiement à l'usage", "facturé à la seconde ou à l'heure", "variable, essais"),
    ("Abonnement", "engagement mensuel ou annuel", "charge stable"),
    ("Plans d'économie", "engagement de dépense horaire", "flotte stable et variée"),
    ("Instances préemptibles", "prix réduit, reprise possible", "traitements, CI, calcul interruptible")], ("Mode", "Principe", "Pour"))),
  ("ECI et Function Compute", "ECI exécute un conteneur à la demande, sans cluster ni serveur : pratique pour des tâches ponctuelles ou en complément d'ACK. Function Compute exécute du code déclenché par un événement (dépôt dans OSS, message, minuterie), facturé à l'exécution.", None)],
 [("La base PostgreSQL de recette tourne sur une instance préemptible « pour économiser » ; elle disparaît en pleine démonstration. Quelle règle a été enfreinte ?", "Les instances préemptibles ne servent que pour ce qui supporte l'interruption (traitements, CI, calcul sans état). Une base passe sur un service géré (ApsaraDB RDS ou PolarDB) ou une instance classique avec sauvegardes."),
  ("Question d'entretien : comment réduis-tu le coût du calcul sur Alibaba Cloud ?", "Dimensionner d'après les mesures, abonnement ou plans d'économie pour le stable, instances préemptibles pour l'interruptible, arrêt des environnements hors production la nuit, et étiquettes pour attribuer chaque coût.")],
 ("Calcul de CrisisShield", ["Image personnalisée, instance ECS sans adresse publique avec rôle RAM, puis groupe Auto Scaling derrière l'ALB.", "Tâche de nuit en Function Compute déclenchée par une minuterie.", "Estimation de coût comparée : paiement à l'usage, abonnement, préemptible pour la CI."],
  "Attendu : l'arrêt d'une instance est compensé automatiquement ; la tâche de nuit ne coûte que ses exécutions ; le tableau de coûts justifie le mode choisi pour chaque charge.")),

ch("Conteneurs : ACK, registre, intégration", 's',
 ["ACK (Container Service for Kubernetes) fournit des clusters Kubernetes gérés, en version gérée classique ou sans serveur (les Pods tournent sur ECI).", "Le registre de conteneurs ACR stocke et analyse les images ; les services Kubernetes s'exposent par l'équilibreur de charge et le contrôleur d'entrée gérés.", "La sécurité se règle dès la création : accès à l'API du cluster restreint, identités RAM liées à Kubernetes, politiques réseau, images scannées."],
 ["Créer un cluster ACK en code et y déployer", "Utiliser ACR, l'équilibreur et le stockage d'ACK", "Sécuriser un cluster ACK"],
 [("Un cluster ACK en code", "Terraform crée le cluster géré, ses groupes de nœuds et l'accès ; ensuite, tout se déploie avec les outils Kubernetes habituels (Helm, Argo CD), comme dans les niveaux 5 et 7 du parcours.", """resource "alicloud_cs_managed_kubernetes" "crise" {
  name                 = "crise-prod"
  cluster_spec         = "ack.pro.small"
  worker_vswitch_ids   = [alicloud_vswitch.app_a.id, alicloud_vswitch.app_b.id]
  new_nat_gateway      = false
  service_cidr         = "172.21.0.0/20"
  slb_internet_enabled = false                           # API du cluster non exposée sur Internet
}
resource "alicloud_cs_kubernetes_node_pool" "applis" {
  cluster_id     = alicloud_cs_managed_kubernetes.crise.id
  node_pool_name = "applis"
  vswitch_ids    = [alicloud_vswitch.app_a.id, alicloud_vswitch.app_b.id]
  instance_types = ["ecs.g7.xlarge"]
  desired_size   = 3
}
# """ + "arguments à vérifier selon la version du fournisseur alicloud" + """"""),
  ("Registre, exposition, stockage", "ACR stocke les images, les analyse et peut les signer ; un Service de type LoadBalancer crée un équilibreur géré ; les volumes persistants s'appuient sur les disques ESSD ou NAS par des classes de stockage fournies.", """apiVersion: v1
kind: Service
metadata:
  name: api
  annotations:
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-address-type: intranet   # équilibreur interne
spec:
  type: LoadBalancer
  selector: { app: api }
  ports: [ { port: 443, targetPort: 8443 } ]"""),
  ("Sécuriser ACK", "API du cluster en accès privé ou restreint, droits Kubernetes attribués aux utilisateurs RAM par rôles, identités des Pods par RRSA plutôt que les droits des nœuds, politiques réseau, images d'ACR scannées, et journaux d'audit du cluster envoyés vers SLS.", None)],
 [("L'API d'un cluster ACK est ouverte sur Internet, et tous les développeurs sont administrateurs du cluster. Priorités ?", "Restreindre l'accès à l'API (réseau privé ou liste d'adresses), attribuer des rôles Kubernetes par espace de noms aux utilisateurs RAM, révoquer les certificats d'administration distribués, et activer l'audit vers SLS."),
  ("Question d'entretien : ACK géré ou ACK sans serveur ?", "Géré : on garde des nœuds ECS pour des charges régulières et des réglages fins ; sans serveur : les Pods tournent sur ECI, sans nœuds à gérer, pour des charges variables ou ponctuelles. Les deux gardent l'API Kubernetes standard.")],
 ("CrisisShield sur ACK", ["Cluster ACK géré en Terraform, API non exposée, groupe de nœuds sur deux zones.", "Images dans ACR avec analyse ; déploiement par Helm ; service exposé par un ALB.", "Rôles Kubernetes pour deux utilisateurs RAM, audit vers SLS, politique réseau par défaut."],
  "Attendu : l'API du cluster n'est pas joignable depuis Internet ; un développeur ne voit que son espace de noms ; une image avec une vulnérabilité critique est signalée par ACR avant déploiement.")),

ch("Stockage et bases : OSS, disques, ApsaraDB RDS, PolarDB, Tair", 'c',
 ["OSS stocke des objets : classes de stockage, cycle de vie, versioning, chiffrement, blocage de l'accès public, URL signées pour le partage.", "Les bases gérées : ApsaraDB RDS (MySQL, PostgreSQL, SQL Server), PolarDB (base cloud native à stockage partagé), Tair compatible Redis, Tablestore pour le NoSQL.", "Sauvegardes et reprise : sauvegardes automatiques, restauration à un instant donné, copies dans une autre région, service de sauvegarde hybride (HBR)."],
 ["Configurer un compartiment OSS sûr", "Choisir et déployer une base gérée", "Sauvegarder et restaurer"],
 [("Un compartiment OSS bien réglé", "Liste d'accès privée, blocage de l'accès public, chiffrement côté serveur par KMS, versioning, règles de cycle de vie, journalisation des accès ; le partage ponctuel passe par des URL signées à durée limitée.", """resource "alicloud_oss_bucket" "pj" {
  bucket = "crise-pieces-jointes"
  versioning { status = "Enabled" }
  server_side_encryption_rule {
    sse_algorithm     = "KMS"
    kms_master_key_id = alicloud_kms_key.pj.id
  }
  lifecycle_rule {
    id      = "archiver"
    enabled = true
    transitions {
      days          = 90
      storage_class = "IA"
    }
  }
}
resource "alicloud_oss_bucket_public_access_block" "pj" {
  bucket              = alicloud_oss_bucket.pj.bucket
  block_public_access = true
}
# """ + DOC),
  ("Choisir une base", "", T([
    ("ApsaraDB RDS PostgreSQL ou MySQL", "base relationnelle gérée classique", "sauvegardes, haute disponibilité, réplicas"),
    ("PolarDB", "stockage partagé, montée en lecture rapide", "équivalent d'Aurora"),
    ("Tair (compatible Redis)", "cache, sessions, compteurs", "équivalent d'ElastiCache"),
    ("Tablestore", "NoSQL à grande échelle", "équivalent de DynamoDB, à modéliser selon les requêtes"),
    ("AnalyticDB", "analytique", "voir le chapitre 7")], ("Service", "Pour", "À retenir"))),
  ("Sauvegardes et reprise", "Les bases gérées sauvegardent automatiquement avec restauration à un instant donné ; on active la copie des sauvegardes dans une autre région pour la reprise, et on teste la restauration chaque mois, comme partout ailleurs.", None)],
 [("Un compartiment OSS contenant des pièces jointes d'incidents est en lecture publique « pour que l'application mobile les affiche ». Que proposes-tu ?", "Repasser le compartiment en privé avec blocage de l'accès public, et faire générer par l'API des URL signées à courte durée pour chaque pièce jointe demandée par un utilisateur autorisé."),
  ("Question d'entretien : PolarDB ou ApsaraDB RDS ?", "RDS pour une base relationnelle gérée classique ; PolarDB quand on veut un stockage partagé entre nœuds, une montée en lecture rapide et une bascule courte, comme Aurora sur AWS ; on mesure coût et besoins avant de choisir.")],
 ("Données de CrisisShield sur Alibaba Cloud", ["Compartiment OSS privé, chiffré par KMS, versionné, avec cycle de vie ; URL signées depuis l'API.", "ApsaraDB RDS PostgreSQL en haute disponibilité, dans le vSwitch des données.", "Restaurer la base à un instant donné et un objet écrasé depuis sa version précédente."],
  "Attendu : aucun objet lisible sans signature ; la base n'accepte que le vSwitch applicatif ; les deux restaurations réussissent et sont chronométrées.")),

ch("Données et IA : MaxCompute, DataWorks, Flink, Model Studio", 's',
 ["MaxCompute est l'entrepôt de données massif d'Alibaba Cloud ; DataWorks orchestre et gouverne les flux de données autour de lui ; Realtime Compute for Apache Flink traite les flux en continu.", "AnalyticDB sert l'analytique interactive ; E-MapReduce fournit Spark et Hadoop gérés ; OSS joue le rôle de lac de données.", "Model Studio donne accès aux modèles Qwen et à d'autres par API, et PAI couvre l'apprentissage automatique ; les mêmes règles que dans le cours IA agentique s'appliquent."],
 ["Situer les services de données d'Alibaba Cloud", "Construire un flux simple de l'objet à l'entrepôt", "Appeler un modèle de Model Studio en respectant les règles de données"],
 [("Les services de données", "", T([
    ("OSS", "lac de données : fichiers bruts et nettoyés", "S3"),
    ("MaxCompute", "entrepôt massif, SQL sur très gros volumes", "Redshift ou BigQuery"),
    ("DataWorks", "développement, planification, gouvernance des flux", "Glue, Airflow, catalogue"),
    ("Realtime Compute for Apache Flink", "traitement en continu", "Kinesis Data Analytics"),
    ("AnalyticDB", "analytique interactive", "Redshift"),
    ("E-MapReduce", "Spark, Hadoop gérés", "EMR")], ("Service", "Rôle", "Équivalent AWS"))),
  ("Un flux simple", "Les fichiers arrivent dans OSS ; une tâche DataWorks les charge dans une table MaxCompute partitionnée par date, puis une requête d'agrégation alimente le tableau de bord. On limite toujours les partitions lues : le coût suit le volume scanné.", """-- MaxCompute : table partitionnée par jour
CREATE TABLE IF NOT EXISTS incidents (id STRING, zone STRING, gravite STRING, cree_le DATETIME) PARTITIONED BY (jour STRING);
-- requête qui ne lit qu'une partition (coût maîtrisé)
SELECT zone, gravite, COUNT(*) AS nb FROM incidents WHERE jour = '20260925' GROUP BY zone, gravite;
-- à éviter : la même requête sans filtre sur jour, qui lit tout l'historique"""),
  ("Model Studio", "Les modèles s'appellent par une API, en partie compatible avec le format OpenAI ; on y applique tout le cours IA agentique : prompts testés, sorties validées, données personnelles masquées, région et contrat vérifiés.", """# appel au format compatible OpenAI (point d'accès international ; """ + "vérifier l'adresse et le modèle dans la documentation" + """)
docker run --rm -e DASHSCOPE_API_KEY curlimages/curl:8.10.1 -s https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions \\
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" -H "Content-Type: application/json" \\
  -d '{"model":"qwen-plus","messages":[{"role":"system","content":"Classe l'"'"'incident en P1, P2 ou P3."},{"role":"user","content":"Fuite de gaz près d'"'"'une école."}]}'""")],
 [("Une requête MaxCompute quotidienne coûte dix fois plus que prévu. Première vérification ?", "Le filtre sur la partition : sans lui, la requête lit tout l'historique et le coût suit le volume scanné. On ajoute le filtre, on fixe des quotas et des alertes de coût, et on vérifie le plan d'exécution."),
  ("Question d'entretien : que changes-tu en passant d'OpenAI ou Claude à un modèle Qwen de Model Studio ?", "Pas les principes : mêmes prompts versionnés, même jeu d'évaluation pour comparer, même validation des sorties ; je vérifie la qualité sur mes cas, la région de traitement et le contrat pour les données.")],
 ("Chaîne de données sur Alibaba Cloud", ["Fichiers d'incidents dans OSS, chargement en table MaxCompute partitionnée par DataWorks (ou script en conteneur).", "Agrégation quotidienne filtrée sur la partition ; alerte de coût.", "Classification des incidents par un modèle de Model Studio, évaluée sur vingt cas."],
  "Attendu : la requête quotidienne ne lit qu'une partition ; le coût du flux est suivi ; l'exactitude du modèle est mesurée et comparée à un autre modèle sur les mêmes cas.")),

ch("Infrastructure comme code et exploitation : Terraform, ROS, CloudMonitor, SLS", 's',
 ["Terraform (fournisseur aliyun/alicloud) ou ROS, l'outil natif, décrivent l'infrastructure ; l'état Terraform se stocke dans un compartiment OSS avec verrouillage.", "CloudMonitor surveille métriques et envoie les alertes ; Simple Log Service (SLS) collecte, indexe et interroge les journaux, et alerte sur des requêtes.", "Cloud Config vérifie la conformité des ressources ; ActionTrail trace les actions ; les runbooks guident l'astreinte."],
 ["Gérer l'état Terraform et la CI sur Alibaba Cloud", "Surveiller avec CloudMonitor et SLS", "Contrôler la conformité et exploiter au quotidien"],
 [("État Terraform et CI", "L'état est stocké dans OSS, verrouillé par une table Tablestore ; la CI endosse un rôle de déploiement par STS et applique le plan relu en MR.", """terraform {
  backend "oss" {
    bucket              = "crise-etat-terraform"
    prefix              = "prod"
    region              = "eu-central-1"
    tablestore_endpoint = "https://crise-verrous.eu-central-1.ots.aliyuncs.com"
    tablestore_table    = "verrous_terraform"
  }
}
# CI : docker run --rm -v "$PWD:/w" -w /w -e ALIBABA_CLOUD_ACCESS_KEY_ID -e ALIBABA_CLOUD_ACCESS_KEY_SECRET -e ALIBABA_CLOUD_SECURITY_TOKEN hashicorp/terraform:1.9 plan"""),
  ("CloudMonitor et SLS", "CloudMonitor fournit les métriques des services et les alertes, routées vers l'astreinte ; SLS reçoit les journaux des applications (agent Logtail ou OpenTelemetry), les indexe et permet recherche, analyse SQL et alertes.", """# requête SLS : erreurs par service sur 5 minutes
level: ERROR and service: incidents | SELECT date_trunc('minute', __time__) AS minute, count(*) AS erreurs GROUP BY minute ORDER BY minute
# alerte SLS : erreurs > 50 en 5 minutes → canal d'astreinte ; alerte CloudMonitor : processeur de l'équilibreur, erreurs 5xx"""),
  ("Conformité et quotidien", "Cloud Config évalue en continu des règles (compartiment OSS public, disque non chiffré, groupe de sécurité ouvert) ; ActionTrail sert l'enquête ; chaque alerte renvoie à un runbook. On surveille aussi les quotas du compte, qui diffèrent de ceux d'AWS.", None)],
 [("Deux personnes lancent terraform apply en même temps et l'état est corrompu. Qu'a-t-il manqué ?", "Un état distant verrouillé (OSS avec verrou Tablestore) et une règle : seule la CI applique, après relecture du plan en MR."),
  ("Question d'entretien : ROS ou Terraform sur Alibaba Cloud ?", "ROS est natif et couvre vite les nouveaux services ; Terraform est multi-fournisseur et déjà connu des équipes, idéal en multi-cloud. En multi-cloud, Terraform garde un seul outil et un seul flux de revue.")],
 ("Exploitation outillée", ["État Terraform dans OSS avec verrou ; CI avec rôle STS et plan relu.", "Journaux de CrisisShield dans SLS, deux alertes (erreurs, latence) et une alerte CloudMonitor.", "Trois règles Cloud Config et un runbook par alerte."],
  "Attendu : un apply concurrent est bloqué par le verrou ; les alertes arrivent à l'astreinte avec leur runbook ; Cloud Config signale un compartiment public créé pour le test.")),

ch("Sécurité et conformité, dont les spécificités de la Chine", 's',
 ["Les briques de sécurité : KMS pour les clés, Security Center pour la détection et la conformité, WAF, Anti-DDoS, Cloud Firewall, certificats gérés.", "Pour la Chine continentale : déclaration ICP obligatoire pour un site web hébergé, loi sur la cybersécurité, loi sur la protection des informations personnelles (PIPL), règles sur les transferts de données hors de Chine.", "En multi-cloud, on garde une même politique de sécurité (identités, chiffrement, journaux, correctifs) appliquée avec les outils de chaque fournisseur."],
 ["Activer les briques de sécurité essentielles", "Connaître les obligations propres à la Chine continentale", "Tenir une politique de sécurité commune en multi-cloud"],
 [("Les briques essentielles", "", T([
    ("KMS", "clés de chiffrement gérées, rotation", "OSS, disques, bases chiffrés"),
    ("Security Center", "détection des menaces, vulnérabilités, conformité", "tableau de bord de sécurité du compte"),
    ("WAF", "filtrage des attaques web", "devant l'équilibreur de charge"),
    ("Anti-DDoS", "protection contre les attaques volumétriques", "services exposés"),
    ("Cloud Firewall", "filtrage centralisé entre Internet, VPC et régions", "contrôle des flux"),
    ("Certificats", "certificats TLS gérés, renouvellement", "domaines publics")], ("Brique", "Rôle", "Usage"))),
  ("Spécificités de la Chine continentale", "Un site web hébergé en Chine continentale doit être déclaré (ICP) avant d'être accessible ; les données personnelles relèvent de la PIPL, et leur transfert hors de Chine suit des procédures (évaluation, contrat type ou certification selon les cas). On s'appuie sur un conseil juridique local ; l'architecture garde les données là où la loi l'exige.", None),
  ("Une politique commune en multi-cloud", "Les règles restent les mêmes que sur AWS : identités fédérées et rôles, pas de clé permanente, chiffrement partout, journaux centralisés et conservés, correctifs réguliers, sauvegardes testées. Seuls les outils changent ; un tableau de correspondance des contrôles évite les trous.", """Contrôle commun                AWS                         Alibaba Cloud
identités fédérées, rôles      IAM Identity Center, IAM    RAM, SSO, STS
aucune clé permanente          Access Analyzer, SCP        audit RAM, politiques de contrôle
chiffrement au repos           KMS                          KMS
journal des actions            CloudTrail                   ActionTrail
détection                      GuardDuty, Security Hub      Security Center
filtrage web                   WAF                          WAF
conformité continue            Config                       Cloud Config""")],
 [("Une application européenne veut stocker à Francfort les données personnelles de ses utilisateurs chinois collectées en Chine. Que conseilles-tu ?", "De ne pas décider seul : la PIPL encadre ce transfert (procédure selon les volumes et la nature des données) ; je demande un avis juridique, je propose une architecture qui garde les données en Chine si nécessaire, et je documente le flux dans le registre des traitements."),
  ("Question d'entretien : comment gardes-tu le même niveau de sécurité sur deux clouds ?", "Avec une politique unique exprimée en contrôles, déclinée par fournisseur dans un tableau de correspondance, vérifiée automatiquement (Config, Cloud Config, analyse du code d'infrastructure), et des journaux centralisés au même endroit.")],
 ("Sécurité de CrisisShield sur Alibaba Cloud", ["Activer KMS, Security Center, WAF devant l'équilibreur et Cloud Config.", "Tableau de correspondance des contrôles AWS et Alibaba Cloud pour CrisisShield.", "Fiche d'une page : obligations en cas d'ouverture à des utilisateurs en Chine continentale."],
  "Attendu : Security Center ne signale aucune alerte critique après correction ; le tableau couvre au moins dix contrôles ; la fiche distingue ce qui relève de l'architecture et ce qui relève du juridique.")),

ch("Projet multi-cloud, migration, certification et entretien", 'e',
 ["Déployer CrisisShield sur Alibaba Cloud en code, à côté d'AWS : même architecture, services équivalents, différences documentées.", "Migrer d'AWS vers Alibaba Cloud (ou l'inverse) : inventaire, correspondances, écarts de fonctions et de quotas, données, bascule par étapes.", "Les certifications Alibaba Cloud vont d'associé à expert ; en entretien, on montre qu'on raisonne en exigences et en compromis, pas en logos."],
 ["Déployer une même architecture sur deux clouds", "Planifier une migration entre clouds", "Préparer une certification et un entretien"],
 [("Les pièges d'une migration AWS vers Alibaba Cloud", "", T([
    ("Réseau", "adresses, zones, équilibreurs aux options différentes", "cartographier et tester"),
    ("Identités", "syntaxe des politiques et noms d'actions", "réécrire, ne pas copier"),
    ("Quotas", "limites par défaut différentes", "demander les hausses à l'avance"),
    ("Services", "équivalents aux fonctions partielles", "tester le besoin réel, pas le nom"),
    ("Données", "volumes, transfert, localisation", "copie incrémentale, bascule planifiée"),
    ("Chine continentale", "ICP, PIPL, connectivité", "anticiper de plusieurs semaines")], ("Domaine", "Piège", "Parade"))),
  ("Trente questions d'entretien", "", """1 Site international ou Chine ? Selon utilisateurs et obligations. 2 ICP ? Déclaration obligatoire d'un site hébergé en Chine continentale. 3 RAM ? Identités et politiques, comme IAM. 4 Compte principal ? MFA, aucune AccessKey. 5 STS ? Identifiants temporaires. 6 Resource Directory ? Organisation multi-comptes. 7 ActionTrail ? Journal des actions. 8 vSwitch ? Sous-réseau lié à une zone. 9 Groupe de sécurité ? Filtrage des instances. 10 SLB ? ALB, NLB, CLB. 11 CEN ? Relier VPC et régions. 12 Express Connect ? Lien dédié. 13 ECS ? Machines virtuelles. 14 Préemptible ? Moins cher, reprise possible. 15 ECI ? Conteneurs sans serveur. 16 Function Compute ? Fonctions sur événements. 17 ACK ? Kubernetes géré. 18 ACR ? Registre et analyse d'images. 19 OSS ? Objets, comme S3. 20 URL signée ? Partage temporaire. 21 PolarDB ? Base à stockage partagé. 22 Tair ? Cache compatible Redis. 23 Tablestore ? NoSQL. 24 MaxCompute ? Entrepôt massif. 25 DataWorks ? Flux de données gouvernés. 26 Model Studio ? Modèles Qwen par API. 27 ROS ou Terraform ? Natif, ou multi-cloud. 28 SLS ? Journaux, recherche, alertes. 29 Security Center ? Détection et conformité. 30 Migrer entre clouds ? Inventaire, correspondances, quotas, bascule par étapes.""")],
 [("On te demande de « faire tourner CrisisShield sur Alibaba Cloud comme sur AWS » en deux semaines. Que réponds-tu ?", "Qu'il faut d'abord les exigences (utilisateurs en Chine ou non, données, disponibilité) ; je propose un pilote : réseau, calcul et base en Terraform, avec la liste des écarts constatés et une estimation réaliste pour le reste, plutôt qu'une promesse de copie à l'identique."),
  ("Question d'entretien : pourquoi une entreprise européenne choisirait-elle Alibaba Cloud ?", "Pour servir des utilisateurs en Chine ou en Asie avec une bonne latence et un fournisseur local, parfois pour des services ou des prix précis ; le choix se fait sur les exigences, les obligations réglementaires et le coût, avec un plan de réversibilité.")],
 ("Projet final Alibaba Cloud", ["Déployer CrisisShield (réseau, calcul ou ACK, base, stockage, journaux) sur Alibaba Cloud en Terraform, depuis la CI.", "Document de correspondance et d'écarts avec la version AWS, coûts comparés.", "Plan de migration par étapes avec bascule et retour arrière ; trente questions répondues à voix haute."],
  "Attendu : l'environnement se crée et se détruit depuis le dépôt ; le document liste les écarts réels constatés ; le plan de migration est chiffré et réversible.")),
]

d = sys.argv[1]
page('cours-53-alibaba-cloud.html', 'Alibaba Cloud — de zéro à expert', "Dix chapitres pour maîtriser Alibaba Cloud en partant de tes repères AWS : régions et sites (international, Chine continentale), identités RAM, STS et Resource Directory, réseau (VPC, vSwitch, SLB, CEN), calcul (ECS, Auto Scaling, ECI, Function Compute), Kubernetes avec ACK, stockage et bases (OSS, ApsaraDB RDS, PolarDB, Tair), données et IA (MaxCompute, DataWorks, Model Studio), Terraform, CloudMonitor et SLS, sécurité et obligations propres à la Chine, projet multi-cloud, migration et préparation à la certification. Fil conducteur : CrisisShield en Terraform, outils en conteneur ; chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 35 h de travail · prérequis : bases d'AWS ou d'un autre cloud, Docker, Terraform.", AL, [('cours-52-aws.html', 'AWS'), ('cours-51-cloud.html', 'Cloud AWS, Azure, GCP'), ('cours-31-ia-agentique.html', 'IA agentique')])
