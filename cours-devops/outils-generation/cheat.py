import re, pathlib, html

out = pathlib.Path('/mnt/user-data/outputs')
H = html.escape

S = []  # (id, titre, niveau/chapitre, commandes[(cmd, desc)], bonnes pratiques[])

S.append(("linux","Linux","Niveau 0, chapitre 2",[
("ls -la /etc","liste avec fichiers cachés et détails"),("find / -name '*.conf' -size +10k 2>/dev/null","cherche par nom et taille, erreurs masquées"),("du -sh /var/* ; df -h ; df -i","taille par répertoire ; espace disque ; inodes"),
("chmod 750 f ; chown app:deploy f","droits propriétaire/groupe/autres ; propriétaire et groupe"),("useradd -m -s /bin/bash alice ; usermod -aG sudo alice","crée un utilisateur avec home ; l'ajoute à un groupe"),
("ps -ef --forest ; top ; htop","processus en arbre ; temps réel"),("kill -15 PID ; kill -9 PID","arrêt propre (SIGTERM) ; forcé (SIGKILL)"),("nohup ./long.sh & ; jobs ; fg","survit à la déconnexion ; tâches du shell"),
("cmd > out 2>&1 ; cmd | tee log","stdout et stderr vers un fichier ; afficher et enregistrer"),("grep -rn ERROR /var/log ; grep -E '^(WARN|ERROR)' f","recherche récursive avec numéros ; regex étendue"),
("awk '{print $1}' f | sort | uniq -c | sort -rn | head","top des valeurs d'une colonne"),("sed -i 's/8080/9090/g' f","remplacement sur place"),("cut -d: -f1 /etc/passwd","colonne par séparateur"),("tail -f app.log ; head -n 20 f ; wc -l f","suivre ; premières lignes ; compter"),
("apt update && apt install -y curl","paquets Debian/Ubuntu"),("systemctl status|restart|enable svc","état ; redémarrage ; au démarrage"),("journalctl -u nginx -f --since '1 hour ago'","journal d'un service, en direct"),
("uptime ; free -h ; vmstat 1 ; iostat -x 1","charge ; mémoire ; CPU et swap ; disque"),("ss -tulpn ; lsof -p PID ; dmesg | tail","ports en écoute ; fichiers ouverts ; messages noyau"),
],[
"Diagnostic dans cet ordre : uptime (charge), top (CPU ou wait), free (swap), df (disque, inodes), ss (le service écoute-t-il), journalctl (erreurs). Une méthode, pas une liste.",
"Tout refuser par défaut : droits minimaux, pas de 777, pas de root pour les applications, sudo tracé.",
"Pratiquer dans un conteneur Ubuntu, jamais dans Git Bash ni MobaXterm (émulations Windows sans ss ni systemd).",
"En conteneur, PID 1 gère SIGTERM (forme exec de l'ENTRYPOINT) sinon Docker tue après 10 s.",
"Automatiser tout ce qui est fait deux fois ; documenter ce qui est fait une fois.",
]))

S.append(("bash","Bash et Python","Niveau 0, chapitre 4",[
("#!/usr/bin/env bash ; set -euo pipefail ; IFS=$'\\n\\t'","en-tête d'un script sérieux : arrêt sur erreur, variable non définie, erreur dans un pipe"),("trap cleanup EXIT","nettoyage quoi qu'il arrive"),("while getopts \"e:v\" opt; do … done","options -e valeur, -v"),
("\"${var:-defaut}\" ; \"${var:?message}\" ; \"${f##*/}\"","valeur par défaut ; obligatoire ; nom de fichier"),("[[ -f \"$f\" ]] ; [[ -z \"$s\" ]] ; (( n > 3 ))","tests fichier, chaîne vide, numérique"),("for s in \"${servers[@]}\"; do … done","boucle sur un tableau, éléments cités"),
("until cmd; do sleep 2; done","réessayer jusqu'au succès"),("docker run --rm -v \"$PWD:/mnt\" koalaman/shellcheck script.sh","analyse statique"),("docker run --rm -v \"$PWD:/code\" bats/bats test/","tests de scripts Bash"),
("docker run --rm -v \"$PWD:/w\" -w /w python:3.12-slim sh -c \"pip install -q requests && python tool.py\"","Python sans installation locale"),("subprocess.run([\"docker\",\"ps\"], capture_output=True, text=True, check=True)","commande système depuis Python"),("pytest -q ; monkeypatch.setattr(requests, \"get\", faux)","tests et doublure"),
],[
"Toujours citer les variables, [[ ]] plutôt que [ ], $( ) plutôt que les backticks, fonctions courtes, codes de retour explicites.",
"Bash pour enchaîner des commandes ; Python dès qu'il y a du JSON, de la logique, des appels HTTP ou plus de 100 lignes. jq entre les deux.",
"Un script de production a des arguments, une aide, des logs horodatés, un nettoyage et des tests.",
"yaml.safe_load, jamais yaml.load ; timeouts sur tout appel réseau ; argparse pour les arguments.",
"Le local est interdit : chaque outil tourne dans un conteneur avec le répertoire monté.",
]))

S.append(("git","Git","Niveau 0, chapitre 5",[
("git status ; git diff ; git diff --staged","état ; modifications ; ce qui est indexé"),("git add -p ; git commit -m \"feat(api): …\"","ajouter par morceaux ; commit conventionnel"),("git log --oneline --graph --all ; git show HEAD~2","historique ; détail d'un commit"),
("git switch -c feature/x ; git switch main && git pull","créer une branche ; revenir à jour"),("git rebase main ; git rebase -i HEAD~4","rejouer sur main ; réécrire ses commits locaux"),("git merge --no-ff feature/x","fusionner en gardant la trace"),
("git rebase --continue|--abort","après résolution de conflit ; annuler"),("git reflog ; git reset --hard HEAD@{3}","retrouver un état perdu"),("git revert abc123","annuler un commit poussé, sans réécrire"),("git reset --soft HEAD~1 ; git commit --amend","défaire le dernier commit local ; le corriger"),
("git stash ; git stash pop","mettre de côté ; restaurer"),("git cherry-pick abc123","appliquer un commit précis"),("git bisect start ; git bisect bad ; git bisect good v1.2","trouver le commit fautif"),("git tag -a v1.4.0 -m \"…\" && git push --tags","marquer une version"),
("git config --global gpg.format ssh ; commit.gpgsign true","commits signés"),("docker run --rm -v \"$PWD:/repo\" zricethezav/gitleaks detect -s /repo","détecter les secrets"),("git ls-tree --name-only -r origin/develop","fichiers d'une branche distante"),
],[
"Rebase sur sa branche locale ; merge ou squash pour intégrer ; jamais de rebase sur une branche partagée ; revert et non reset sur main.",
"Petites branches courtes (moins de deux jours), Conventional Commits, merge request obligatoire, branches protégées, pipeline vert requis.",
"Un secret commité est compromis même supprimé de l'historique : le révoquer.",
".gitignore pour .env, clés, certificats ; .gitattributes avec eol=lf sous Windows, sinon les scripts cassent dans les conteneurs.",
"Le reflog est le filet de sécurité : rien n'est perdu pendant 90 jours.",
]))

S.append(("docker","Docker","Niveau 1, chapitre 8",[
("docker run -d --name web -p 8080:80 --restart unless-stopped nginx:1.27","lancer en arrière-plan avec port publié"),("winpty docker run -it --rm ubuntu:24.04 bash","shell jetable (winpty sous Git Bash)"),("docker exec -it web sh ; docker logs -f --tail 100 web","entrer ; suivre les logs"),
("docker inspect web | jq '.[0].State'","code de sortie, OOMKilled"),("docker stats ; docker top web ; docker events --since 10m","consommation ; processus ; événements"),("docker stop web ; docker rm -f web","arrêt propre ; suppression forcée"),
("docker build -t api:1.0.0 . ; --target build ; --no-cache","construire ; s'arrêter à une étape ; sans cache"),("docker buildx build --platform linux/amd64,linux/arm64 -t img --push .","multi-architecture"),("docker history img ; docker image inspect img | jq '.[0].RootFS.Layers'","couches"),
("docker network create backend ; docker run --network backend …","réseau avec DNS entre conteneurs"),("docker volume create pgdata ; -v pgdata:/var/lib/postgresql/data","volume nommé persistant"),("docker run --rm -v pgdata:/data -v \"$PWD:/b\" alpine tar czf /b/pg.tgz -C /data .","sauvegarder un volume"),
("docker run --user 1000:1000 --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges --memory 512m --pids-limit 200 img","conteneur durci"),("docker run --rm -it --network container:api nicolaka/netshoot","outils réseau dans le namespace d'un conteneur"),("docker system df ; docker system prune -af --volumes","espace ; nettoyage (attention aux volumes)"),
("docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock wagoodman/dive img","explorer les couches"),("docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --severity HIGH,CRITICAL --exit-code 1 --ignore-unfixed img","scanner"),
],[
"Dockerfile multi-étapes, base minimale épinglée (jamais latest), ce qui change le moins en premier (cache), .dockerignore, une couche RUN par groupe, USER non root, HEALTHCHECK, ENTRYPOINT en forme exec.",
"Un secret copié puis effacé est toujours dans l'image ; secrets de build par --mount=type=secret, secrets d'exécution par fichier ou gestionnaire.",
"Un réseau par pile, seule l'entrée publie un port, la base jamais ; volumes nommés pour ce qui doit survivre.",
"Durcir : non root, lecture seule, capabilities retirées, no-new-privileges, limites mémoire et PID ; jamais --privileged ni le socket Docker dans une application.",
"Déboguer : logs, inspect, entrypoint sh, netshoot, events ; 137 = SIGKILL (OOM), 143 = SIGTERM.",
]))

S.append(("compose","Docker Compose","Niveau 1, chapitre 9",[
("docker compose up -d --build ; docker compose down ; down -v","démarrer ; arrêter ; avec les volumes (données perdues)"),("docker compose ps ; logs -f api ; exec api sh","état ; logs ; shell"),("docker compose config","fichier résolu (variables, surcharges)"),
("docker compose run --rm api sh -c \"./mvnw test\"","commande ponctuelle"),("docker compose pull && docker compose up -d","mettre à jour les images"),("docker compose --profile tools up -d","services optionnels"),
("docker compose -f compose.yaml -f compose.prod.yaml up -d","surcharge de production"),("docker compose kill db ; docker compose start db","simuler une panne"),("docker compose up -d --scale worker=3","plusieurs instances"),
],[
"depends_on avec condition: service_healthy, sinon Compose n'attend que le démarrage ; l'application retente de toute façon.",
"Secrets en fichiers (secrets:), pas en variables ; healthchecks partout ; durcissement de chaque service comme avec docker run.",
"Deux réseaux (frontend, backend) pour que le front ne joigne pas la base ; un seul port publié.",
"compose.override.yaml pour le développement, profils pour l'outillage, .env non commité avec un .env.example.",
"Compose pilote un hôte : pas de HA ni de rolling update ; au-delà, Kubernetes.",
]))

S.append(("kubectl","Kubernetes et kubectl","Niveau 5, chapitres 25 à 31",[
("kubectl get pods -A --field-selector=status.phase!=Running","tout ce qui ne tourne pas"),("kubectl describe pod X","événements en bas : à lire en premier"),("kubectl logs -f deploy/api ; kubectl logs X --previous","logs ; conteneur précédent (CrashLoop)"),
("kubectl get events -A --sort-by=.lastTimestamp | tail -30","événements récents"),("kubectl apply -f k8s/ ; kubectl diff -f k8s/ ; kubectl apply -k overlays/prod","appliquer ; diff ; Kustomize"),("kubectl explain deploy.spec.strategy --recursive","documentation d'un champ"),
("kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}'","extraire un champ"),("kubectl get pods -o custom-columns='NOM:.metadata.name,NOEUD:.spec.nodeName'","colonnes choisies"),("kubectl rollout status|history|undo deploy/api ; rollout restart deploy/api","suivre ; historique ; revenir ; redémarrer"),
("kubectl scale deploy/api --replicas=3 ; kubectl set image deploy/api api=img@sha256:…","réplicas ; image par digest"),("kubectl exec -it deploy/api -- sh ; kubectl debug -it X --image=nicolaka/netshoot --target=api","shell ; conteneur éphémère de debug"),("kubectl port-forward svc/api 8080:80","accès local"),
("kubectl top pods --containers ; kubectl top nodes","consommation (metrics-server)"),("kubectl auth can-i --list --as=system:serviceaccount:ns:api","permissions d'un compte"),("kubectl cordon N ; kubectl drain N --ignore-daemonsets --delete-emptydir-data ; kubectl uncordon N","maintenance d'un nœud"),
("kubectl get endpointslices -l kubernetes.io/service-name=api","les Pods derrière un Service"),("kubectl debug node/N -it --image=ubuntu","shell sur un nœud"),("kubectl delete pod X --grace-period=0 --force","Terminating bloqué, en dernier recours"),
("kind create cluster --config kind-config.yaml ; kind load docker-image img","cluster local ; charger une image"),("k9s ; stern -n ns api ; kubectl krew install neat ctx ns tree","outils du quotidien"),("etcdctl snapshot save f ; kubeadm certs check-expiration ; kubeadm upgrade plan","administration"),
],[
"Méthode : get, describe, logs --previous, puis Ingress → Service → EndpointSlices → Pod → nœud ; jamais redémarrer d'abord.",
"Deployment de référence : startup/liveness/readiness (liveness sans dépendance externe), requests toujours, limite mémoire = request, pas de limite CPU, preStop sleep, non root, lecture seule, drop ALL, PDB, topologySpread.",
"Un Secret n'est pas secret : chiffrement etcd, RBAC, External Secrets ; NetworkPolicy default-deny puis ouverture (DNS compris).",
"Helm pour les paquets tiers (diff, --atomic, versions épinglées), Kustomize pour ses overlays ; tout en GitOps par ArgoCD, promotion par merge request, rollback par revert.",
"Mises à jour : une mineure à la fois, API dépréciées détectées (Pluto), nœuds remplacés, staging d'abord ; etcd sauvegardé ; certificats surveillés.",
]))

S.append(("helm","Helm et Kustomize","Niveau 5, chapitre 28",[
("helm repo add x URL ; helm repo update ; helm search repo pg","dépôts"),("helm show values x/chart > values.yaml","valeurs par défaut à relire"),("helm upgrade --install rel x/chart -n ns -f values.yaml --version 1.2.3 --atomic","installer ou mettre à jour, rollback si échec"),
("helm diff upgrade rel x/chart -f values.yaml","différences avant d'appliquer (plugin)"),("helm template rel x/chart -f values.yaml | kubectl apply --dry-run=server -f -","rendre et valider"),("helm list -A ; helm history rel ; helm rollback rel 2","releases ; révisions ; retour"),
("helm lint ; helm unittest . ; helm test rel","qualité et tests"),("helm push chart-1.0.0.tgz oci://registry/charts","publier en OCI"),("kubectl kustomize overlays/prod | kubectl diff -f -","rendu et diff Kustomize"),
],[
"Toujours --version épinglé, helm diff avant upgrade, --atomic, relire les values par défaut (LoadBalancer, ClusterRole admin…).",
"Checksum du ConfigMap en annotation pour forcer le rolling ; hooks pre-upgrade pour les migrations ; values.schema.json.",
"Scanner les manifests rendus (Trivy config, Kyverno CLI) avant de les appliquer.",
"Kustomize : base plus overlays, image par digest, configMapGenerator avec hash ; pas de logique conditionnelle, c'est voulu.",
]))

S.append(("terraform","Terraform / OpenTofu","Niveau 3, chapitre 16",[
("terraform init ; terraform fmt -recursive -check ; terraform validate","initialiser ; formater ; valider"),("terraform plan -out=tfplan -input=false -lock-timeout=5m","plan sauvegardé, attend un verrou"),("terraform apply tfplan","appliquer exactement le plan revu"),
("terraform plan -refresh=false ; -target=module.db ; apply -replace=aws_instance.web","rapide ; chirurgie ; forcer une recréation"),("terraform state list ; state show ADR ; state mv A B ; state rm ADR ; state pull > backup","lire et manipuler le state"),("terraform import ADR ID ; bloc import { to, id } + plan -generate-config-out","adopter l'existant"),
("terraform force-unlock ID","verrou orphelin, après vérification"),("terraform apply -refresh-only","réconcilier avec la réalité"),("terraform plan -detailed-exitcode","code 2 = dérive (job nocturne)"),
("terraform test ; terraform console ; terraform graph | dot -Tsvg","tests ; expressions ; dépendances"),("terraform providers lock -platform=linux_amd64 -platform=windows_amd64","lockfile multi-plateforme"),("TF_LOG=DEBUG terraform plan","appels du provider"),
("docker run --rm -v \"$PWD:/w\" -w /w --network N hashicorp/terraform:1.9 plan","Terraform en conteneur"),("docker run --rm -v \"$PWD:/w\" aquasec/trivy config /w ; checkov -d .","sécurité de la configuration"),("terraform-docs markdown . > README.md ; infracost breakdown --path .","documentation ; coût"),
],[
"State distant, chiffré, verrouillé, versionné, jamais commité ; un state par environnement et par domaine ; apply uniquement depuis la CI avec resource_group.",
"for_each plutôt que count ; variables typées avec validation ; modules à interface minimale, versionnés, documentés ; alias de providers pour multi-région et multi-compte.",
"Lire le plan en entier, chercher « forces replacement » ; prevent_destroy sur les bases ; ignore_changes sur ce qu'un autre système modifie ; jamais d'apply « pour voir ».",
"Secrets : sensitive, ephemeral, ou générés dans Vault/Secrets Manager ; jamais dans tfvars commités.",
"Refactoring déclaratif (moved, removed, import) plutôt que state à la main ; sauvegarde du state avant toute manipulation.",
]))

S.append(("ansible","Ansible","Niveau 3, chapitre 17",[
("ansible all -i inventory.ini -m ping ; -m shell -a uptime --become","test de connexion ; commande ad hoc"),("ansible-playbook -i inventory/prod.ini playbooks/web.yml --check --diff","simulation avec diff"),("ansible-playbook … --limit web1 --tags nginx -e api_version=1.4.0","cibler ; filtrer ; variables"),
("ansible-playbook … --start-at-task 'X' ; --limit @site.retry","reprendre ; rejouer les hôtes en échec"),("ansible-inventory --host web1 --yaml ; --graph","variables résolues d'un hôte ; groupes"),("ansible-vault create|edit f ; encrypt_string 'S' --name k ; --vault-id prod@prompt","secrets"),
("ansible-galaxy collection install -r requirements.yml ; ansible-galaxy init role","collections ; squelette de rôle"),("ansible-lint --profile production ; molecule test","qualité ; tests de rôle"),("ansible-playbook -vvv …","déboguer la connexion"),
("docker run --rm -it -v \"$PWD:/w\" -w /w -v ~/.ssh:/root/.ssh:ro willhallonline/ansible:2.17-alpine ansible-playbook …","Ansible en conteneur"),
],[
"Idempotence : relancer ne change rien ; modules plutôt que shell (creates:, changed_when: sinon) ; handlers pour recharger uniquement si changement.",
"Précédence : defaults du rôle < inventaire < play < tâche < extra-vars ; ansible-inventory --host pour trancher.",
"Déploiement : serial, max_fail_percentage 0, block/rescue/always, retrait du load balancer par delegate_to, until sur la readiness.",
"ansible.cfg : forks 50, pipelining, facts en cache, host_key_checking activé hors labo ; no_log sur les tâches sensibles.",
"Rôles à responsabilité unique, testés avec Molecule, collections épinglées ; inventaire dynamique par tags pour relier à Terraform.",
]))

S.append(("aws","AWS CLI","Niveau 4, chapitres 20 et 21",[
("docker run --rm -it -v \"$HOME/.aws:/root/.aws\" amazon/aws-cli sso login --profile sandbox","connexion SSO, sans clé statique"),("aws sts get-caller-identity","qui suis-je"),("aws s3 ls ; aws s3 cp f s3://b/ ; aws s3 sync dir s3://b/","objets"),
("aws ec2 describe-instances --query 'Reservations[].Instances[].[InstanceId,State.Name]' --output table","lister avec filtre JMESPath"),("aws ecs update-service --cluster c --service s --force-new-deployment","redéployer un service"),("aws logs tail /crisisshield/api --follow","logs CloudWatch en direct"),
("aws secretsmanager get-secret-value --secret-id x","lire un secret"),("aws iam simulate-principal-policy --policy-source-arn ROLE --action-names s3:GetObject","tester une permission"),("aws ce get-cost-and-usage --time-period … --granularity MONTHLY --metrics UnblendedCost","coûts"),
("AWS_ENDPOINT_URL=http://localstack:4566 aws s3 mb s3://x ; awslocal s3 ls","LocalStack"),
],[
"Jamais de clé d'accès statique : Identity Center pour les humains, rôles pour les charges, OIDC pour la CI ; MFA sur root puis root jamais utilisé.",
"Un compte par environnement et par domaine, budgets et alertes avant la première ressource, SCP sur les régions.",
"VPC trois niveaux sur trois AZ, security groups par référence, endpoints plutôt que NAT, RDS non public avec Secrets Manager.",
"Tout en Terraform ; console en lecture seule ; CloudTrail, Config, GuardDuty, Security Hub activés dès le départ.",
"FinOps : tags obligatoires, éteindre hors heures, redimensionner, Graviton et Spot, engagements en dernier.",
]))

S.append(("vault","Vault et secrets","Niveau 7, chapitre 38",[
("vault status ; vault login -method=oidc","état ; connexion humaine"),("vault kv put kv/app/prod/smtp user=x password=y ; vault kv get -version=2 kv/app/prod/smtp","secret statique versionné"),("vault policy write app - < policy.hcl","politique"),
("vault auth enable kubernetes ; vault write auth/kubernetes/role/api bound_service_account_names=api … ttl=1h","identité des Pods"),("vault secrets enable database ; vault write database/roles/api … default_ttl=1h ; vault read database/creds/api","identifiants dynamiques"),("vault write -f database/rotate-root/crisis","plus personne ne connaît le mot de passe root"),
("vault secrets enable transit ; vault write transit/encrypt/k plaintext=$(base64…) ; vault write -f transit/keys/k/rotate","chiffrement as a service"),("vault secrets enable pki ; vault write pki_int/issue/services common_name=api.ns.svc ttl=24h","certificats courts"),("vault lease revoke ID ; vault audit enable file file_path=stdout","révoquer ; audit"),
("vault operator raft snapshot save f","sauvegarde"),("kubeseal < secret.yaml > sealed.yaml ; sops -e -i secrets.yaml","chiffrer dans Git (sans gestionnaire)"),("docker run --rm -v \"$PWD:/repo\" zricethezav/gitleaks detect -s /repo","détection de secrets"),
],[
"Hiérarchie : supprimer le secret (identité) > dynamique de courte durée > statique centralisé et tourné > chiffré dans Git.",
"Aucun secret dans le code, les images, les variables de CI ni les logs ; External Secrets pour livrer aux Pods ; audit activé et collecté.",
"HA Raft, auto-unseal par KMS, procédure de recouvrement et token root scellé (break-glass) documentés et testés.",
"KMS et chiffrement d'enveloppe pour les données ; HSM pour les clés critiques ; rotation planifiée.",
"Un secret fuité est révoqué immédiatement ; on cherche ensuite d'où il vient.",
]))

S.append(("supply","Sécurité des images et de la chaîne : Trivy, Syft, Cosign","Niveaux 1 et 7, chapitres 10 et 40",[
("trivy image --severity HIGH,CRITICAL --exit-code 1 --ignore-unfixed img","scanner et bloquer en CI"),("trivy config . ; trivy fs .","IaC ; dépendances"),("syft img -o cyclonedx-json > sbom.json ; grype sbom:sbom.json --fail-on high","SBOM ; scanner un SBOM"),
("cosign sign --yes img@sha256:… ; cosign verify img@… --certificate-identity … --certificate-oidc-issuer …","signature keyless ; vérification"),("cosign attest --yes --predicate sbom.json --type cyclonedx img@… ; cosign verify-attestation --type cyclonedx img@…","attestations"),("cosign attach sbom --sbom sbom.json img@…","attacher le SBOM"),
("docker run --rm -v \"$PWD:/w\" ghcr.io/fairwindsops/pluto detect-files -d /w","API Kubernetes dépréciées"),("kyverno test . ; kyverno apply policies/ --resource manifests/","politiques en CI"),("kube-bench ; kubescape scan","posture du cluster"),
],[
"Trois questions par artefact : d'où vient-il (provenance), a-t-il été modifié (signature), que contient-il (SBOM).",
"latest interdit : tags immuables, déploiement par digest vérifié à l'admission (Kyverno mutateDigest).",
"Build unique sur runner éphémère sans socket Docker (Kaniko, BuildKit rootless), SBOM et provenance à chaque build, signature keyless liée au job de la branche main.",
"Actions, images de job et dépendances épinglées par SHA ou digest ; proxy de dépendances à liste d'autorisation.",
"Prioriser par EPSS, KEV et reachability ; VEX pour documenter le non-exploitable ; SLA de correction par sévérité.",
]))

S.append(("tls","TLS, PKI, réseau : openssl, curl, dig","Niveau 0 chapitre 3, niveau 7 chapitre 41",[
("openssl s_client -connect h:443 -servername h -showcerts </dev/null","chaîne envoyée par le serveur (SNI)"),("openssl x509 -in c.crt -noout -text ; -subject -issuer -dates -ext subjectAltName","lire un certificat"),("openssl verify -CAfile chain.pem c.crt","valider la chaîne"),
("openssl req -x509 -newkey rsa:2048 -nodes -keyout k -out c -days 365 -subj \"/CN=lab\"","auto-signé de labo"),("openssl pkcs12 -export -in c.crt -inkey k -certfile chain.pem -out c.p12","PEM vers PKCS#12 (Java)"),("keytool -importcert -alias racine -file root.crt -keystore truststore.p12 -storetype PKCS12","truststore Java"),
("curl -v https://h ; curl -I ; curl -sf -o /dev/null -w '%{http_code} %{time_total}\\n' URL","dialogue complet ; en-têtes ; code et temps"),("curl --resolve h:443:10.0.5.7 https://h","tester un nom sur une IP"),("dig +short h A ; dig @8.8.8.8 h ; getent hosts h","DNS"),
("nc -zv h 5432 ; ss -tulpn ; ip route","port ouvert ; écoute ; routage"),("tcpdump -i any port 5432 -w cap.pcap","capture"),
],[
"Diagnostiquer dans l'ordre DNS → TCP → TLS → HTTP ; le 502 vient du reverse proxy.",
"Les SAN font foi ; le serveur envoie feuille et intermédiaires, jamais la racine ; certificats courts renouvelés automatiquement plutôt que révocation.",
"Jamais -k ni de TrustManager qui accepte tout : ajouter la racine interne au bon magasin (système, JVM, applicatif).",
"Inventaire et alerte d'expiration à 30 et 14 jours ; racine hors ligne, intermédiaire en ligne, cérémonie documentée, HSM pour les clés critiques.",
]))

S.append(("pg","PostgreSQL","Niveaux 0 et 8, chapitres 6, 27 et 47",[
("docker exec -it pg psql -U postgres -d shop","client"),("\\dt ; \\d+ table ; \\l ; \\du","tables ; détail ; bases ; rôles"),("EXPLAIN ANALYZE SELECT …","plan réel : Seq Scan sur une grosse table = index manquant"),
("CREATE INDEX CONCURRENTLY idx ON t(col)","index sans verrouiller"),("SET lock_timeout='3s'; ALTER TABLE t ADD CONSTRAINT … NOT VALID; ALTER TABLE t VALIDATE CONSTRAINT …","contrainte sans bloquer"),("SELECT * FROM pg_stat_activity WHERE state='idle in transaction'","sessions bloquantes"),
("SELECT query, total_exec_time FROM pg_stat_statements ORDER BY 2 DESC LIMIT 10","requêtes les plus coûteuses"),("SELECT relname, n_dead_tup FROM pg_stat_user_tables ORDER BY 2 DESC","bloat, autovacuum"),("pg_dump -U u -Fc db > f.dump ; pg_restore -U u -d db f.dump","sauvegarde logique ; restauration"),
("pg_isready -U u -d db","healthcheck"),("kubectl cnpg status db ; kubectl cnpg backup db","opérateur CloudNativePG"),
],[
"Migrations versionnées (Flyway) compatibles N-1 : expand/contract ; lock_timeout et statement_timeout ; index concurrents ; NOT VALID puis VALIDATE ; lots pour les mises à jour massives.",
"PgBouncer devant la base, pools applicatifs petits ; lecture répartie avec read-your-writes.",
"Partitionner par date avant de sharder ; archiver le froid ; autovacuum et wraparound surveillés.",
"Sauvegardes vers stockage objet, restauration testée automatiquement ; une sauvegarde non testée n'existe pas.",
"Rôles par usage, pas de superuser applicatif, TLS, pgaudit si référentiel.",
]))

S.append(("ci","GitLab CI (mots-clés) et outils de build","Niveau 2, chapitres 12 à 14",[
("stages / image / script / rules / needs / artifacts / cache / environment / when: manual / resource_group","les mots-clés d'un job"),("rules: - if: $CI_PIPELINE_SOURCE == \"merge_request_event\" ; changes: [scripts/**]","déclencher finement"),("needs: [unit-tests]","DAG : ne pas attendre toute l'étape"),
("artifacts: { reports: { junit: … }, expire_in: 1 week }","rapports dans la MR"),("id_tokens: { X: { aud: sigstore } }","OIDC vers Vault, AWS, Sigstore"),("include: / extends: / !reference","factoriser"),
("./mvnw -q verify ; ./mvnw org.pitest:pitest-maven:mutationCoverage","build, tests ; mutation testing"),("npm ci ; npm run build ; npm audit signatures","front reproductible"),("docker run --rm -v \"$PWD:/w\" -w /w semgrep/semgrep semgrep ci --config auto","SAST"),
("semantic-release ; commitlint ; renovate","version, changelog ; format des commits ; mises à jour"),("docker run --rm -e AWS_ENDPOINT_URL … infracost/infracost breakdown --path .","coût dans la MR"),
],[
"Construire une fois, déployer partout : une image par commit, taguée par SHA, promue par digest ; jamais de rebuild par environnement.",
"Feedback en moins de 10 minutes : paralléliser, cacher, découper les tests, échouer vite ; le cache n'est jamais nécessaire, l'artefact peut l'être.",
"Aucun secret statique en CI : OIDC ; runners éphémères sans socket Docker ; images de job et actions épinglées.",
"Quality gate sur le nouveau code, Testcontainers plutôt que H2, analyses de sécurité d'abord en observation puis bloquantes.",
"Lockfiles partout, Renovate avec auto-merge des correctifs, semantic-release, proxy Nexus.",
]))

S.append(("obs","Observabilité : Prometheus, Loki, OpenTelemetry, k6","Niveau 6",[
("sum by (service) (rate(http_server_requests_seconds_count[5m]))","débit"),("100 * sum(rate(…{status=~\"5..\"}[5m])) / sum(rate(…[5m]))","taux d'erreur"),("histogram_quantile(0.95, sum by (le) (rate(…_bucket[5m])))","latence p95 (jamais de moyenne)"),
("container_memory_working_set_bytes / container_spec_memory_limit_bytes > 0.9","OOM imminent"),("topk(10, count by (__name__)({__name__=~\".+\"}))","cardinalité"),("{namespace=\"ns\", app=\"api\"} | json | level=\"ERROR\"","LogQL : filtrer par label d'abord"),
("{ name = \"escalate\" && duration > 1s }","TraceQL"),("promtool check rules rules.yml ; amtool alert ; amtool silence add …","valider ; alertes ; silences"),("docker run --rm -i -v \"$PWD:/w\" grafana/k6 run /w/load.js --out experimental-prometheus-rw","charge"),
("kubectl annotate deploy api instrumentation.opentelemetry.io/inject-java=true","auto-instrumentation OTel"),
],[
"Logs JSON sur stdout avec trace_id, sans données sensibles ; Loki avec peu de labels ; rétention par type.",
"RED pour les services, USE pour les ressources ; pas de moyenne de latence ; pas d'identifiant en label.",
"OpenTelemetry pour tout, Collector agent + gateway, tail sampling ; corréler logs, métriques, traces par trace_id et exemplars.",
"Alerter sur le burn rate (symptôme) avec runbook ; causes en ticket ; revue mensuelle du bruit ; moins de deux pages par semaine et par personne.",
"Post-mortem sans blâme en cinq jours, actions suivies ; game days.",
]))

# ---------- rendu ----------
head = re.sub(r'<title>[^<]*</title>', '<title>Aide-mémoire — commandes et bonnes pratiques</title>', re.search(r'^.*?</head>', (out/'devops-00-fondations.html').read_text(), flags=re.S).group(0))
extra = """
.pagenav{display:flex;flex-wrap:wrap;gap:.6rem;margin-bottom:1rem;font-size:.9rem}
.pagenav a{color:#fff;text-decoration:none;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);padding:.3rem .75rem;border-radius:6px}
.pagenav a:hover{background:rgba(255,255,255,.2);color:#fff}
.cmd td:first-child{font-family:"JetBrains Mono",monospace;font-size:.82em;white-space:pre-wrap;word-break:break-word;width:52%}
.bp{background:var(--tp-soft);border-left:4px solid var(--tp);border-radius:0 var(--radius) var(--radius) 0;padding:.8rem 1rem;margin:1rem 0}
.bp strong{color:var(--tp);display:block;margin-bottom:.3rem}
.bp ol{margin:0;padding-left:1.3rem}
.jump{display:flex;flex-wrap:wrap;gap:.4rem;margin:1rem 0}
.jump a{text-decoration:none;font-size:.85rem;background:var(--paper);border:1px solid var(--line);border-radius:999px;padding:.25rem .7rem}
.jump a:hover{background:var(--accent-soft)}
.filter{width:100%;font:inherit;padding:.6rem .8rem;border:1px solid var(--line-strong);border-radius:8px;background:var(--paper);color:var(--ink);margin:.5rem 0 1rem}
body{padding-bottom:2rem}
@media print{.pagenav,.jump,.filter{display:none}}
</style>"""
head = head.replace('</style>', extra, 1)
body = '''<body>
<header class="hero"><div class="in">
<div class="pagenav"><a href="index.html">← Accueil du parcours</a><a href="devops-11-fiches-entretien.html">Fiches entretien</a></div>
<div class="level">Aide-mémoire</div>
<h1>Toutes les commandes à connaître, et les bonnes pratiques par technologie</h1>
<p class="lead">Seize technologies, les commandes du quotidien avec ce qu'elles font, et cinq bonnes pratiques par outil : ce que le parcours enseigne, condensé pour l'usage en mission. À imprimer, ou à filtrer.</p>
</div></header>
<div class="single">
<input class="filter" id="filter" type="search" placeholder="Filtrer : tape un mot (rebase, jsonpath, lock, serial…)" aria-label="Filtrer l'aide-mémoire">
<div class="jump">''' + ''.join(f'<a href="#{i}">{H(t)}</a>' for i,t,_,_,_ in S) + '</div>\n'
for i,t,ref,cmds,bps in S:
    body += f'<article id="{i}"><div class="chaphead"><span class="chapnum">{H(ref)}</span></div><h2>{H(t)}</h2>'
    body += '<div class="tablewrap"><table class="cmd"><tr><th>Commande</th><th>Ce qu\'elle fait</th></tr>'
    body += ''.join(f'<tr><td>{H(c)}</td><td>{H(d)}</td></tr>' for c,d in cmds)
    body += '</table></div>'
    body += '<div class="bp"><strong>Bonnes pratiques</strong><ol>' + ''.join(f'<li>{H(b)}</li>' for b in bps) + '</ol></div></article>\n'
body += '''</div>
<script>
(function(){
  var root=document.documentElement; try{ var t=localStorage.getItem('devops-theme'); if(t) root.setAttribute('data-theme',t); }catch(e){}
  document.querySelectorAll('table').forEach(function(t){ var rows=t.rows; if(!rows.length) return; var head=rows[0]; if(!head.querySelector('th')) return; head.classList.add('head');
    var labels=Array.prototype.map.call(head.cells,function(c){return c.textContent.trim();});
    for(var i=1;i<rows.length;i++){ var cells=rows[i].cells; for(var j=0;j<cells.length;j++){ if(cells[j].tagName==='TD') cells[j].setAttribute('data-label',labels[j]||''); } } t.classList.add('stack'); });
  var f=document.getElementById('filter');
  f.addEventListener('input',function(){ var q=f.value.trim().toLowerCase();
    document.querySelectorAll('article').forEach(function(a){ var any=false;
      a.querySelectorAll('table.cmd tr:not(.head)').forEach(function(r){ var ok=!q||r.textContent.toLowerCase().indexOf(q)>=0; r.style.display=ok?'':'none'; if(ok) any=true; });
      a.querySelectorAll('.bp li').forEach(function(l){ var ok=!q||l.textContent.toLowerCase().indexOf(q)>=0; l.style.display=ok?'':'none'; if(ok) any=true; });
      a.style.display=any?'':'none'; });
  });
})();
</script>
</body></html>'''
(out/'devops-10-aide-memoire.html').write_text(head + '\n' + body)
print('aide-mémoire :', sum(len(c) for _,_,_,c,_ in S), 'commandes,', sum(len(b) for _,_,_,_,b in S), 'bonnes pratiques')

ip = out/'devops-parcours-complet.html'; t = ip.read_text()
if 'devops-10-aide-memoire.html' not in t:
    t = t.replace('<h2>Réviser pour un entretien</h2>',
                  '<h2>Aide-mémoire</h2>\n<p>Toutes les commandes à connaître avec ce qu\'elles font, et cinq bonnes pratiques par technologie, sur une page filtrable : <a href="devops-10-aide-memoire.html"><strong>ouvrir l\'aide-mémoire</strong></a>.</p>\n<h2>Réviser pour un entretien</h2>', 1)
    ip.write_text(t); print('index ok')
