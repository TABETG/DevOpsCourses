import re, pathlib

N = {}
def n(ch, tech, quoi, pourquoi, essai):
    N[ch] = (tech, quoi, pourquoi, essai)

n(1, "Nix et les flakes",
  "Environnements de développement et de build reproductibles au bit près : un fichier <code>flake.nix</code> décrit exactement les outils et leurs versions, identiques pour toute l'équipe et la CI. C'est aussi la base de NixOS et d'images de conteneurs sans distribution.",
  "Rares sont ceux qui le maîtrisent ; il répond à « ça marche sur ma machine » par construction, et c'est un excellent sujet de discussion sur la reproductibilité.",
  "<code>docker run -it --rm nixos/nix nix-shell -p terraform kubectl --run \"terraform version\"</code>")

n(2, "eBPF avec bpftrace",
  "Observer le noyau en direct, sans redémarrage ni instrumentation : fichiers ouverts par un processus, latence des I/O, connexions, appels système d'un conteneur précis. C'est la technologie derrière Cilium, Falco et Beyla.",
  "Le diagnostic « impossible » devient une ligne ; en entretien, savoir répondre « je regarderais avec bpftrace » sur une question de performance système marque immédiatement.",
  "<code>docker run --rm -it --privileged --pid=host quay.io/iovisor/bpftrace bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf(\"%s %s\\n\", comm, str(args->filename)); }'</code> (fonctionne sur la VM WSL de Docker Desktop)")

n(3, "Caddy",
  "Serveur web et reverse proxy avec HTTPS automatique (ACME pour le public, autorité de certification locale pour le labo), HTTP/3 (QUIC) natif, et une configuration de cinq lignes là où Nginx en demande cinquante.",
  "Connaître HTTP/3 et une PKI locale automatique te place en avance ; Caddy est aussi ce qui tourne derrière beaucoup d'outils internes modernes.",
  "Un <code>Caddyfile</code> contenant <code>localhost { reverse_proxy app1:5678 }</code> puis <code>docker run -p 443:443 -v \"$PWD/Caddyfile:/etc/caddy/Caddyfile\" --network tp3_default caddy:2</code> : refais le TP 3 en trois lignes.")

n(4, "Bats-core",
  "Un cadre de tests unitaires pour Bash : des fichiers <code>.bats</code> avec assertions, exécutables en CI, pour tester tes scripts d'exploitation comme du code.",
  "Presque personne ne teste ses scripts ; montrer une suite Bats sur <code>backup.sh</code> est un marqueur de sérieux rare.",
  "<code>docker run --rm -v \"$PWD:/code\" bats/bats test/</code> avec un test <code>@test \"refuse une source absente\" { run ./backup.sh -s /nope -d /tmp; [ \"$status\" -eq 2 ]; }</code>")

n(5, "Jujutsu (jj)",
  "Un système de contrôle de version compatible Git (même dépôt, même serveur) qui repense l'expérience : le répertoire de travail est toujours un commit, les conflits sont enregistrés sans bloquer, toute réécriture d'historique est annulable avec <code>jj undo</code>.",
  "C'est l'outil qui monte dans les équipes plateforme et chez Google ; en parler avec précision montre une veille au-delà de Git.",
  "Binaire depuis les releases GitHub de <code>jj-vcs/jj</code> dans un conteneur <code>debian:stable</code>, puis <code>jj git init --colocate</code> dans ton dépôt <code>devops-lab</code> et <code>jj log</code>.")

n(6, "Atlas (Ariga)",
  "Le schéma de base de données déclaré en HCL ou SQL ; l'outil calcule les migrations par différence, les lint (changement destructif, verrou long) et les planifie. Fonctionne avec ou à la place de Flyway/Liquibase.",
  "« Schema as code » avec analyse des risques de migration, c'est un cran au-dessus du versionnage de scripts.",
  "<code>docker run --rm --network host arigaio/atlas schema inspect -u \"postgres://postgres:lab@localhost:5432/shop?sslmode=disable\"</code> puis <code>migrate lint</code> sur tes migrations du TP 6.")

n(7, "Firecracker",
  "La micro-VM d'AWS qui fait tourner Lambda et Fargate : démarrage en 125 ms, noyau minimal, isolation matérielle pour des charges non fiables. Kata Containers l'utilise comme runtime OCI, ce qui permet de lancer un « conteneur » qui est en réalité une VM.",
  "Savoir expliquer la différence entre gVisor (noyau en espace utilisateur), Kata/Firecracker (micro-VM) et un conteneur classique est une question d'expert sur l'isolation multi-locataire.",
  "Nécessite KVM : sur une instance EC2 metal ou une VM avec virtualisation imbriquée (à combiner avec le TP 21), suivre le quickstart Firecracker et lancer une micro-VM en moins de dix commandes.")

n(8, "Wolfi et apko (Chainguard)",
  "Une « distribution sans distribution » : des images minimales construites déclarativement par apko à partir de paquets Wolfi (melange pour en compiler), avec SBOM natif, mises à jour quotidiennes, et souvent zéro CVE. Les images <code>cgr.dev/chainguard/jre</code> en sont issues.",
  "C'est l'état de l'art des images durcies ; comparer Trivy sur <code>jre-alpine</code> et sur une image Chainguard est un argument massue en entretien DevSecOps.",
  "Un <code>apko.yaml</code> avec <code>contents.packages: [wolfi-base, openjdk-21-jre]</code>, puis <code>docker run --rm -v \"$PWD:/w\" -w /w cgr.dev/chainguard/apko build apko.yaml api:wolfi api.tar</code> et <code>docker load &lt; api.tar</code>.")

n(9, "Podman et Quadlet",
  "Podman exécute des conteneurs sans démon et sans root par défaut ; Quadlet décrit des conteneurs et des pods dans des fichiers <code>.container</code>/<code>.pod</code> que systemd transforme en services. C'est la façon Red Hat de servir des conteneurs sur des VM, sans Kubernetes ni Compose.",
  "Très présent dans le secteur public et bancaire français (RHEL) ; rootless par défaut, c'est un argument sécurité immédiat.",
  "<code>docker run --rm -it --privileged quay.io/podman/stable podman run --rm alpine echo ok</code>, puis écrire le fichier <code>crisisshield-api.container</code> équivalent à ton service Compose.")

n(10, "ORAS et Zot",
  "ORAS pousse n'importe quel artefact (SBOM, chart, plan Terraform, modèle ML, fichier de politique) dans un registre OCI, avec tags, digests et signatures Cosign ; Zot est un registre OCI natif (CNCF) léger avec scan et synchronisation.",
  "Un seul système de distribution pour tous les artefacts, signé et versionné : c'est ce que les plateformes matures font désormais.",
  "<code>docker run --rm --network host ghcr.io/oras-project/oras:v1.2.0 push localhost:5000/crisisshield/sbom:1.0.0 sbom.json:application/json</code> puis <code>oras pull</code> depuis un autre conteneur.")

n(11, "Dagger",
  "Des pipelines écrits en code (Go, Python, TypeScript, Java via l'API) et exécutés dans des conteneurs BuildKit : strictement identiques en local et en CI, avec cache intelligent et composition de modules. Le YAML de GitLab ou GitHub ne fait plus qu'appeler <code>dagger call</code>.",
  "Il met fin au « ça marche dans la CI mais pas sur mon poste » et à la duplication GitLab/GitHub/Jenkins ; encore peu maîtrisé en France.",
  "Installer le CLI dans un conteneur avec accès au socket Docker, <code>dagger init --sdk=python</code>, puis <code>dagger call build --source=.</code> pour reconstruire l'image CrisisShield.")

n(12, "Tekton",
  "CI/CD natif Kubernetes : Tasks, Pipelines et PipelineRuns sont des CRD exécutées en Pods ; c'est le moteur d'OpenShift Pipelines, et Tekton Chains signe automatiquement chaque artefact produit (provenance SLSA).",
  "OpenShift est omniprésent dans les grands comptes français ; connaître Tekton te rend opérationnel le premier jour sur ces plateformes.",
  "<code>kubectl apply -f https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml</code> sur kind, puis une Task qui construit l'image CrisisShield avec Kaniko.")

n(13, "PIT (pitest) : mutation testing",
  "L'outil modifie ton code Java (inverse une condition, supprime un appel) et vérifie que les tests échouent ; s'ils passent encore, le mutant « survit » : la couverture était là, la vérification non.",
  "Distinguer couverture et efficacité des tests est une réponse d'expert ; un score de mutation dans le quality gate est très rare.",
  "<code>./mvnw org.pitest:pitest-maven:mutationCoverage</code> dans le conteneur Maven du pipeline, rapport HTML en artefact, seuil sur le score de mutation.")

n(14, "diffoscope et les builds reproductibles",
  "diffoscope compare deux artefacts (jar, image, paquet) au bit près et explique chaque différence : horodatage, ordre des entrées, chemins absolus. Avec <code>project.build.outputTimestamp</code> côté Maven et <code>SOURCE_DATE_EPOCH</code> côté BuildKit, deux builds du même commit deviennent identiques.",
  "La reproductibilité est l'ultime preuve d'intégrité de la chaîne (SLSA) ; savoir la mesurer et la corriger est une compétence de niche très valorisée.",
  "<code>docker run --rm -v \"$PWD:/w\" -w /w registry.salsa.debian.org/reproducible-builds/diffoscope a.jar b.jar</code> sur deux builds successifs du backend, puis corriger jusqu'à l'identité.")

n(15, "Flipt",
  "Feature flags open source, déclaratifs : les flags vivent dans des fichiers YAML du dépôt (mode GitOps), avec segmentation, rollouts pondérés, et un fournisseur OpenFeature pour Java et JavaScript.",
  "Des flags versionnés et revus comme du code, sans SaaS, c'est le choix des plateformes souveraines.",
  "<code>docker run --rm -p 8080:8080 docker.flipt.io/flipt/flipt</code>, puis le provider OpenFeature Flipt dans CrisisShield et le fichier <code>features.yaml</code> dans le dépôt de config.")

n(16, "Pulumi en Java ou Kotlin",
  "L'infrastructure décrite dans un vrai langage : boucles, types, tests JUnit, packages Maven, mêmes fournisseurs que Terraform (par pont), état stocké dans S3 ou Pulumi Cloud.",
  "Pour un expert Java, c'est un argument immédiat : « l'infra testée avec les mêmes outils que le code ». Peu de consultants IaC le pratiquent.",
  "<code>docker run --rm -it -v \"$PWD:/w\" -w /w pulumi/pulumi-java pulumi new aws-java</code> puis pointer le fournisseur AWS vers LocalStack et recréer le module réseau du TP 16.")

n(17, "Event-Driven Ansible",
  "Des rulebooks qui écoutent des sources d'événements (webhook Alertmanager, Kafka, Prometheus, Git) et déclenchent des playbooks quand une condition est vraie : remédiation automatique déterministe, pilotée par événements.",
  "C'est l'Ansible « exploitation moderne » (Ansible Automation Platform) ; savoir brancher une alerte sur une remédiation encadrée est exactement le sujet du chapitre 54.",
  "<code>docker run --rm -it -p 5000:5000 -v \"$PWD:/rb\" quay.io/ansible/ansible-rulebook ansible-rulebook -i /rb/inventory.yml --rulebook /rb/alertes.yml</code> avec une source webhook branchée sur Alertmanager.")

n(18, "Talos Linux",
  "Un système d'exploitation conçu uniquement pour Kubernetes : immuable, sans SSH ni shell, entièrement piloté par API (<code>talosctl</code>) et déclaré en YAML ; nœuds jetables, mises à jour atomiques, surface d'attaque minimale.",
  "L'immutabilité poussée au bout ; c'est ce que choisissent les plateformes sur site et edge exigeantes, et un sujet qui impressionne en entretien sécurité.",
  "<code>talosctl cluster create</code> (image <code>ghcr.io/siderolabs/talosctl</code>) crée un cluster Talos dans Docker ; compare avec kind et essaie d'obtenir un shell sur un nœud.")

n(19, "Digger",
  "Orchestration Terraform en GitOps à l'intérieur de ta CI existante : plan posté en commentaire de merge request, apply après approbation, verrouillage par MR, détection de dérive, sans serveur dédié contrairement à Atlantis.",
  "GitOps pour l'infrastructure sans nouveau composant à exploiter : un choix pragmatique que peu connaissent.",
  "Image <code>diggerhq/digger</code> dans un job GitLab du TP 16, avec le backend LocalStack ; observe le commentaire de plan et le verrou entre deux MR.")

n(20, "Cloud Custodian",
  "Des règles YAML évaluées sur les ressources cloud (AWS, Azure, GCP, Kubernetes) qui trouvent, notifient et corrigent : arrêter les instances non taguées, chiffrer les volumes, supprimer les adresses orphelines, planifiées en Lambda.",
  "Gouvernance et FinOps en code, avec action : très recherché, et complémentaire d'AWS Config qui ne fait que détecter.",
  "<code>docker run --rm -v \"$PWD:/w\" -w /w -e AWS_ENDPOINT_URL=http://localstack:4566 --network &lt;réseau&gt; cloudcustodian/c7n run -s out politique.yml</code> avec une règle qui marque les buckets sans tag <code>Owner</code>.")

n(21, "AWS Nitro Enclaves",
  "Une machine virtuelle isolée, sans réseau ni stockage persistant, à côté d'une instance EC2 : elle produit un document d'attestation signé, et KMS ne déchiffre une clé que si l'enclave est attestée. Traitement de secrets, signature, HSM logiciel, confidential computing.",
  "Ton expérience PKI/HSM plus le confidential computing : un créneau où presque personne ne se positionne en France.",
  "Sur une instance compatible (par exemple <code>m6i.xlarge</code>, quelques centimes) avec <code>nitro-cli</code>, construire l'enclave d'exemple, lire l'attestation, et documenter la comparaison avec un HSM.")

n(22, "Steampipe",
  "Interroger AWS, Azure, GCP, GitHub, Kubernetes en SQL : chaque API devient une table PostgreSQL virtuelle ; des mods prêts (CIS, ISO 27001, RGPD) produisent des rapports de conformité multi-cloud en minutes. Powerpipe pour les tableaux de bord.",
  "L'audit multi-cloud en SQL, c'est spectaculaire en démonstration client et ça remplace des heures de clics.",
  "<code>docker run --rm -it -e AWS_ENDPOINT_URL=http://localstack:4566 --network &lt;réseau&gt; turbot/steampipe query \"select name, region from aws_s3_bucket\"</code>, puis <code>steampipe check</code> avec le mod AWS Compliance.")

n(23, "Kepler et Cloud Carbon Footprint",
  "Kepler (CNCF) mesure par eBPF la consommation énergétique de chaque Pod et l'exporte dans Prometheus ; Cloud Carbon Footprint estime les émissions CO2 par compte cloud. C'est le GreenOps.",
  "Les DSI y sont désormais contraintes par la directive CSRD ; un consultant capable de l'outiller est rare et demandé.",
  "Helm <code>kepler</code> sur kind, dashboard Grafana « énergie par namespace », puis le lien avec OpenCost : coût et carbone par équipe côte à côte.")

n(24, "NetBird et Headscale",
  "Réseaux maillés WireGuard zero trust auto-hébergés : chaque machine, conteneur ou poste rejoint le maillage par identité OIDC (Keycloak), avec listes de contrôle par groupe, traversée de NAT et DNS interne, sans VPN central ni port ouvert.",
  "Relier site, clouds et postes en zero trust sans appliance : très différenciant face aux VPN classiques.",
  "Compose officiel de NetBird avec ton Keycloak comme IdP ; relie le conteneur « legacy » du TP 24 et une instance LocalStack au maillage et écris une ACL.")

n(25, "kwok (Kubernetes WithOut Kubelet)",
  "Simule des milliers de nœuds et de Pods sans kubelet ni conteneur : le control plane est réel, les nœuds sont factices. Idéal pour tester le scheduling, les opérateurs, l'autoscaling et les politiques à l'échelle sur un poste.",
  "Tester à 5 000 nœuds gratuitement, c'est un argument qui frappe quand on parle de plateformes à l'échelle.",
  "<code>docker run --rm -it -p 8080:8080 registry.k8s.io/kwok/cluster:v0.6.0-k8s.v1.31.0</code>, puis créer 1 000 nœuds et observer le comportement de tes politiques Kyverno et du scheduler.")

n(26, "Envoy Gateway",
  "L'implémentation de référence de Gateway API par le projet Envoy (CNCF) : HTTPRoute, TLSRoute, rate limiting, authentification JWT et externe, réécritures, sans annotations propriétaires.",
  "Gateway API est l'avenir des ingress ; en maîtriser une implémentation avant qu'elle ne devienne standard, c'est prendre de l'avance.",
  "Helm <code>oci://docker.io/envoyproxy/gateway-helm</code> sur kind, puis remplacer l'Ingress de CrisisShield par une Gateway et deux HTTPRoute avec limitation de débit par organisation.")

n(27, "Longhorn",
  "Stockage bloc distribué (CNCF) pour Kubernetes : répliques synchrones entre nœuds, instantanés, sauvegardes vers S3, interface de gestion ; conçu pour le sur site et l'edge, sans baie de stockage.",
  "Savoir fournir du stockage persistant fiable hors cloud est une compétence recherchée sur les plateformes souveraines.",
  "Installer <code>open-iscsi</code> dans les nœuds kind, Helm <code>longhorn</code>, StorageClass avec 3 répliques, puis rejouer le TP 27 avec CloudNativePG sur Longhorn et perdre un nœud.")

n(28, "Timoni",
  "Des modules d'application écrits en CUE (typage fort, validation, valeurs par défaut, contraintes) et distribués en OCI : l'alternative à Helm sans templates texte, par l'auteur de Flux.",
  "CUE et Timoni sont encore confidentiels ; en parler avec un exemple montre une compréhension des limites de Helm.",
  "<code>docker run --rm -it -v \"$PWD:/w\" -w /w ghcr.io/stefanprodan/timoni mod init crisisshield-api</code>, puis convertir le chart de l'API et publier le module dans ton registre OCI.")

n(29, "Kargo",
  "Promotion multi-environnements pour GitOps (par les créateurs d'Argo) : Warehouses qui surveillent images et charts, Freight (un lot versionné), Stages dev → staging → prod avec vérifications, en amont d'ArgoCD.",
  "La promotion est le chaînon manquant d'ArgoCD ; Kargo l'outille proprement et peu d'équipes l'ont mis en place.",
  "Helm <code>oci://ghcr.io/akuity/kargo-charts/kargo</code> sur kind, un Warehouse sur ton registre, trois Stages, et remplace le job de promotion manuel du TP 29.")

n(30, "Kmesh",
  "Un service mesh eBPF sans sidecar ni proxy par nœud pour le trafic L4 (compatible avec le control plane Istio), avec une latence quasi nulle ; à connaître aux côtés d'Istio ambient et de Cilium, en surveillant sa maturité.",
  "Comprendre le mouvement « sans sidecar » et ses trois implémentations te place dans les discussions d'architecture réseau avancées.",
  "Helm Kmesh sur un cluster kind avec un noyau récent ; compare la latence p99 de CrisisShield avec Istio sidecar, Istio ambient, Cilium et Kmesh dans un tableau.")

n(31, "Kueue",
  "Files d'attente de jobs pour Kubernetes (projet sigs) : quotas par équipe, priorités, préemption, partage équitable, admission en attendant les ressources ; conçu pour le batch et l'IA (entraînements, GPU), là où le scheduler seul ne suffit pas.",
  "Les charges IA arrivent partout ; savoir gouverner des GPU partagés entre équipes est une compétence neuve et rare.",
  "<code>kubectl apply -f https://github.com/kubernetes-sigs/kueue/releases/latest/download/manifests.yaml</code>, une ClusterQueue par équipe, dix Jobs soumis et l'ordre d'admission observé.")

n(32, "Vector",
  "Agent de logs et métriques en Rust (Datadog, open source) : ultra performant, avec le langage VRL pour parser, transformer, enrichir et surtout masquer les données personnelles à la source avant tout stockage.",
  "Le masquage RGPD à la collecte, prouvable, est un argument fort pour un profil DevSecOps ; Vector remplace Fluent Bit et Promtail.",
  "<code>docker run --rm -v \"$PWD/vector.yaml:/etc/vector/vector.yaml:ro\" timberio/vector:latest-alpine</code> avec une transformation VRL qui remplace les adresses e-mail par un hachage avant envoi vers Loki.")

n(33, "VictoriaMetrics",
  "Base de séries temporelles compatible Prometheus (remote write, PromQL étendu en MetricsQL) qui consomme jusqu'à dix fois moins de mémoire et de disque, avec un mode cluster simple ; alternative à Thanos et Mimir, très répandue en Europe de l'Est et chez les gros volumes.",
  "Savoir dimensionner et comparer Thanos, Mimir et VictoriaMetrics est une question de plateforme d'observabilité à l'échelle.",
  "<code>docker run -p 8428:8428 victoriametrics/victoria-metrics</code>, remote write depuis ton Prometheus, puis compare la consommation mémoire à charge égale.")

n(34, "Grafana Beyla",
  "Auto-instrumentation par eBPF : métriques RED et traces OpenTelemetry de n'importe quel processus (Java, Go, Node, binaire inconnu) sans agent, sans changement de code ni d'image, legacy compris.",
  "Observer une application qu'on n'a pas le droit de modifier est un cas de mission fréquent ; Beyla y répond en dix minutes.",
  "DaemonSet Beyla sur kind avec les métadonnées Kubernetes activées ; observe les traces du service « legacy » du TP 50 sans y toucher.")

n(35, "Robusta",
  "Enrichit chaque alerte Prometheus avec le contexte utile (logs du Pod, événements, graphes, dernier déploiement) et propose des remédiations en un clic dans Slack ou Teams ; son outil KRR recommande les requests à partir de l'usage réel.",
  "Réduire le temps de diagnostic de l'astreinte avec des alertes enrichies est une amélioration visible immédiatement par les équipes.",
  "Helm <code>robusta</code> sur kind branché sur ton Alertmanager et un webhook Slack de test ; déclenche un CrashLoop et lis l'alerte enrichie.")

n(36, "Dispatch (Netflix)",
  "Plateforme de gestion d'incident open source : création automatique des canaux, assignation des rôles, chronologie, tâches, notifications, rapports et post-mortems, intégrée à Slack, Jira et Google Workspace.",
  "Proposer un outil d'incident complet et gratuit à une organisation qui gère ses incidents par e-mail, c'est un livrable de mission apprécié.",
  "Compose du dépôt Netflix/dispatch, déclare un incident SEV2 fictif et exécute le processus du TP 36 dedans.")

n(37, "Bearer CLI",
  "Un SAST orienté données sensibles : il cartographie où transitent données personnelles et de santé dans le code (Java supporté), détecte leur fuite dans les logs, les envois vers des tiers, les stockages non chiffrés, et produit des rapports sécurité et vie privée.",
  "AppSec plus RGPD dans un seul outil : le croisement exact de ton positionnement.",
  "<code>docker run --rm -v \"$PWD:/tmp/scan\" bearer/bearer scan /tmp/scan --report privacy</code> sur le backend CrisisShield ; corrige les fuites détectées dans les logs.")

n(38, "Infisical et OpenBao",
  "Infisical : plateforme de secrets open source avec interface, versionnage, injection par CLI, agent ou opérateur Kubernetes, secrets dynamiques et PKI, plus simple à adopter que Vault. OpenBao : le fork communautaire de Vault sous la Linux Foundation, choix des organisations qui refusent la licence BSL.",
  "Savoir positionner Vault, OpenBao et Infisical selon le contexte (licence, souveraineté, taille d'équipe) est une réponse d'architecte.",
  "Compose d'Infisical, l'opérateur Kubernetes sur kind, et un secret de CrisisShield synchronisé ; puis remplace l'image Vault du TP 38 par <code>openbao/openbao</code> et vérifie la compatibilité.")

n(39, "KubeArmor",
  "Enforcement à l'exécution par les modules de sécurité du noyau (AppArmor, BPF-LSM) : il bloque, et pas seulement détecte, l'exécution de processus, l'accès à des fichiers ou le réseau par Pod, avec des politiques CRD et une découverte automatique du comportement normal.",
  "Falco alerte ; KubeArmor empêche. Savoir les combiner est une réponse qui dépasse le discours habituel.",
  "Helm <code>kubearmor</code> sur kind, une <code>KubeArmorPolicy</code> qui interdit tout shell dans les Pods de l'API, puis <code>kubectl exec</code> refusé et journalisé.")

n(40, "GUAC",
  "Graph for Understanding Artifact Composition (OpenSSF) : ingère SBOM, provenance SLSA, VEX, résultats de scan et signatures, et construit un graphe interrogeable : « quels artefacts déployés contiennent log4j-core 2.14 et par quel chemin ? ».",
  "Le SBOM sans graphe reste un fichier ; GUAC en fait un système de réponse rapide aux CVE, encore quasi inconnu en mission.",
  "Compose de GUAC, <code>guacone collect files sbom/</code> sur tes SBOM du TP 37, puis une requête GraphQL sur une dépendance.")

n(41, "OpenZiti",
  "Réseau zero trust applicatif open source : identités par certificat, services « invisibles » sans aucun port ouvert (dark), politiques par identité, et des SDK pour embarquer le réseau dans l'application elle-même (dont <code>ziti-sdk-jvm</code>).",
  "Zero trust concret jusque dans le code Java : un sujet de conférence, pas seulement d'entretien.",
  "Compose du quickstart OpenZiti, expose l'API CrisisShield comme service Ziti sans port publié et accède-la depuis un tunnel authentifié.")

n(42, "compliance-trestle",
  "L'outillage OSCAL d'IBM : catalogues, profils, définitions de composants et plans de sécurité écrits en Markdown et YAML dans Git, générés et validés en CI ; la conformité devient du code revu par merge request.",
  "OSCAL est adopté par le NIST et arrive en Europe ; savoir le manipuler te place en avance sur les missions de conformité.",
  "<code>docker run --rm -v \"$PWD:/w\" -w /w python:3.12-slim sh -c \"pip install compliance-trestle &amp;&amp; trestle init\"</code>, puis importe le catalogue NIST 800-53 et rédige un composant pour la passerelle CrisisShield.")

n(43, "Byteman",
  "Injection de fautes dans la JVM à chaud, sans modifier le code : des règles textuelles qui lèvent une exception dans une méthode précise, ajoutent une latence, corrompent une valeur ; le chaos engineering au niveau applicatif, en complément de Chaos Mesh.",
  "Le chaos réseau tout le monde en parle ; le chaos dans la JVM, presque personne. Et c'est ton langage.",
  "<code>-javaagent:byteman.jar=script:regles.btm</code> sur l'API avec une règle « lever IOException dans NotificationClient.send une fois sur trois », et vérifier que le fallback du TP 43 tient.")

n(44, "Kanister",
  "Sauvegardes applicatives pour Kubernetes (CNCF, Veeam) par Blueprints : hooks avant et après (gel, dump cohérent, restauration) spécifiques à chaque application stateful, intégrables à Velero et Kopia.",
  "Une sauvegarde de volume n'est pas une sauvegarde cohérente ; savoir le dire et l'outiller sépare les profils.",
  "Helm <code>kanister</code> sur kind, Blueprint PostgreSQL avec <code>pg_dump</code> vers MinIO, ActionSet de sauvegarde puis de restauration mesurée.")

n(45, "Cryostat",
  "JDK Flight Recorder à l'échelle sur Kubernetes : démarrer et collecter des enregistrements JFR sur tous les Pods Java, règles automatiques (CPU au-dessus de 80 % pendant 2 minutes déclenche un enregistrement), analyse et export vers Grafana.",
  "Le profilage Java en production, industrialisé : un différenciateur net pour un expert Java devenu DevOps.",
  "Opérateur Cryostat sur kind, JMX activé dans l'API, une règle automatique, et un enregistrement analysé pendant la charge k6 du TP 45.")

n(46, "Dapr",
  "Runtime applicatif distribué (CNCF) en sidecar : invocation de services, pub/sub (Kafka, RabbitMQ), état, secrets, workflows, résilience, via une API HTTP/gRPC identique quel que soit le langage ; SDK Java et Spring Boot.",
  "Découpler les applications des courtiers et des bases par une API standard, c'est l'architecture portable dont parlent les DSI ; peu l'ont vue tourner.",
  "<code>dapr init -k</code> sur kind (image <code>daprio/dapr</code>), composant pub/sub Kafka, et l'événement IncidentCreated publié via Dapr plutôt que le client Kafka direct ; compare le code.")

n(47, "pgroll",
  "Migrations PostgreSQL sans interruption qui servent deux versions du schéma en même temps (vues versionnées) : expand/contract automatisé, l'ancienne et la nouvelle application coexistent, rollback instantané tant que la migration n'est pas « complétée ».",
  "L'expand/contract outillé, c'est la réponse experte à « comment vous renommez une colonne en prod » ; peu d'équipes connaissent.",
  "<code>docker run --rm --network host ghcr.io/xataio/pgroll:latest init --postgres-url ...</code> puis <code>start</code> et <code>complete</code> sur le renommage de colonne du TP 15, avec les deux versions de l'API en parallèle.")

n(48, "Score",
  "Une spécification ouverte de charge de travail (<code>score.yaml</code>) indépendante de la plateforme : le développeur décrit conteneur, ressources (base, file, bucket) et variables ; <code>score-compose</code> génère du Compose pour le poste, <code>score-k8s</code> ou Humanitec/Kratix du Kubernetes pour la prod.",
  "C'est l'abstraction développeur dont parle le platform engineering, matérialisée par un standard ; en parler avec un exemple qui tourne est rare.",
  "<code>docker run --rm -v \"$PWD:/w\" -w /w ghcr.io/score-spec/score-compose:latest init</code>, un <code>score.yaml</code> pour l'API CrisisShield, génération Compose puis Kubernetes, et comparaison avec ta composition Crossplane.")

n(49, "Capsule",
  "Opérateur multi-locataire pour Kubernetes (Clastix, CNCF) : un Tenant regroupe des namespaces avec quotas, NetworkPolicies, registres autorisés, classes de stockage et RBAC délégués en libre-service, sans control plane par tenant ni cluster dédié.",
  "Le juste milieu entre namespaces bruts et clusters par client, industrialisé : une réponse précise à la question multi-tenant.",
  "Helm <code>capsule</code> sur kind, un Tenant « banque » avec ses contraintes, un propriétaire qui crée lui-même ses namespaces, et les tests d'isolation du TP 49 rejoués.")

n(50, "Konveyor (Kantra et Move2Kube)",
  "Boîte à outils de migration (Red Hat, CNCF) : Kantra analyse le code avec des règles (Java EE vers Quarkus ou Spring, WebLogic vers conteneur, cloud-readiness) et estime l'effort ; Move2Kube génère Dockerfiles et manifests à partir d'un WAR ou d'un Compose.",
  "Une migration outillée avec estimation chiffrée, c'est ce qu'un client attend d'un consultant ; connaître Konveyor évite de le faire à la main.",
  "<code>docker run --rm -v \"$PWD:/app\" quay.io/konveyor/kantra analyze --input /app --output /app/out --target quarkus</code> sur le legacy du TP 50, puis lis le rapport d'effort.")

n(51, "OpenFGA",
  "Autorisation fine relationnelle (modèle Zanzibar de Google, CNCF) : « l'utilisateur X peut-il consulter l'incident Y de l'organisation Z ? » se répond par un graphe de relations et un modèle DSL versionné dans Git, avec SDK Java et vérification en CI.",
  "La gouvernance des accès applicatifs au-delà des rôles, en code testable : un sujet où sécurité et architecture se rejoignent, encore peu maîtrisé.",
  "<code>docker run -p 8080:8080 openfga/openfga run</code>, le modèle d'autorisation de CrisisShield (organisations, zones, incidents), des tests <code>fga model test</code>, et le test d'IDOR du TP 41 réécrit dessus.")

n(52, "Apache DevLake",
  "Plateforme open source (Apache) qui collecte GitLab, GitHub, Jira, Jenkins, ArgoCD, PagerDuty et calcule les métriques DORA et d'ingénierie dans des dashboards Grafana prêts, avec définitions transparentes.",
  "Livrer les métriques DORA d'un client en une journée avec un outil de fondation Apache, c'est plus crédible qu'un script maison.",
  "Compose officiel de DevLake, connexion à ton GitLab local et à ArgoCD, et compare ses métriques DORA avec celles de ton service du TP 52.")

n(53, "mob.sh",
  "Un outil de mob et de pair programming à distance qui orchestre la rotation par Git (branches de travail temporaires, passage de main en une commande, minuteur) ; le rituel de coaching le plus concret qui existe.",
  "Coacher avec un outil et un rituel mesurable (une session par semaine, rotation toutes les dix minutes) plutôt qu'avec des slides : les équipes s'en souviennent.",
  "<code>mob start 10</code> et <code>mob next</code> dans un conteneur avec Git, en binôme sur un TP de ce cours ; intègre-le au programme de coaching du TP 53.")

n(54, "Signature de modèles et ML-BOM",
  "Le projet OpenSSF model-signing signe les poids de modèles avec Sigstore ; CycloneDX ML-BOM inventorie modèles, datasets et leurs dépendances ; on vérifie avant chargement et on bannit les formats exécutables (pickle) au profit de safetensors.",
  "La supply chain de l'IA est le prolongement naturel de SLSA et de ton positionnement LLM Security ; presque personne ne l'outille encore.",
  "Dans un conteneur <code>python:3.12</code> : <code>pip install model-signing</code>, signer un modèle safetensors, vérifier la signature dans la passerelle du TP 54 avant chargement, et générer un ML-BOM CycloneDX attaché à l'image.")

assert len(N) == 54

def block(ch):
    tech, quoi, pourquoi, essai = N[ch]
    return (f'<div class="niche"><span class="tag">Pour sortir du lot — {tech}</span>'
            f'<p>{quoi}</p><p><strong>Pourquoi ça différencie :</strong> {pourquoi}</p>'
            f'<p><strong>À essayer en une heure :</strong> {essai}</p></div>\n\n')

CSS_TOKENS_LIGHT = "--niche:#0E7C86; --niche-soft:#E1F4F6; --niche-line:#8CCFD6;"
CSS_TOKENS_DARK = "--niche:#66D3DD; --niche-soft:#0F2A2E; --niche-line:#1F5D64;"
CSS_RULES = """
/* ============ Technologie de niche ============ */
.niche{background:var(--niche-soft);border:1px solid var(--niche-line);border-left:4px solid var(--niche);border-radius:var(--radius);padding:.95rem 1.15rem;margin:1.3rem 0}
.niche .tag{font-weight:700;color:var(--niche);display:block;margin-bottom:.35rem}
.niche p{margin:.45rem 0}
@media print{.niche{background:none !important}}
</style>"""

files = [
 ("devops-niveau-0-fondations.html", range(1,7)),
 ("devops-niveau-1-conteneurs.html", range(7,11)),
 ("devops-niveau-2-ci-cd.html", range(11,16)),
 ("devops-niveau-3-infrastructure-as-code.html", range(16,20)),
 ("devops-niveau-4-cloud.html", range(20,25)),
 ("devops-niveau-5-kubernetes.html", range(25,32)),
 ("devops-niveau-6-observabilite.html", range(32,37)),
 ("devops-niveau-7-securite-devsecops.html", range(37,43)),
 ("devops-niveau-8-sre-architecture.html", range(43,49)),
 ("devops-niveau-9-expert-leadership.html", range(49,55)),
]
out = pathlib.Path('/mnt/user-data/outputs')
for fn, chs in files:
    p = out/fn
    s = p.read_text()
    if 'class="niche"' in s:
        print(fn, 'déjà fait'); continue
    parts = s.split('<div class="entretien">')
    assert len(parts) == len(chs)+1, (fn, len(parts))
    s = parts[0]
    for ch, rest in zip(chs, parts[1:]):
        s += block(ch) + '<div class="entretien">' + rest
    s = s.replace("--hero:#0F1B33; --ok:#1B7A4E;", "--hero:#0F1B33; --ok:#1B7A4E; " + CSS_TOKENS_LIGHT, 1)
    s = s.replace("--hero:#0B1220; --ok:#6CD19B; --shadow:none;", "--hero:#0B1220; --ok:#6CD19B; --shadow:none; " + CSS_TOKENS_DARK, 1)
    s = s.replace("</style>", CSS_RULES, 1)
    p.write_text(s)
    print(fn, s.count('class="niche"'))

# page d'accueil
p = out/'devops-parcours-complet.html'
s = p.read_text()
if 'technologies de niche' not in s:
    s = s.replace('<span>Chaque chapitre : cours, encadré entretien, exercices corrigés, TP</span>',
                  '<span>Chaque chapitre : cours, technologie de niche, encadré entretien, exercices corrigés, TP</span><span>54 technologies de niche pour sortir du lot</span>', 1)
    s = s.replace('<li><strong>Révision</strong>',
                  '<li><strong>Technologie de niche</strong> : chaque chapitre propose un outil rare mais sérieux, à essayer en une heure ; retiens-en dix que tu sais raconter avec un exemple, c\'est ce qui te distinguera en entretien et en avant-vente.</li>\n<li><strong>Révision</strong>', 1)
    p.write_text(s)
print('index ok')
