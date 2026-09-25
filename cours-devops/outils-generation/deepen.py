import re, pathlib

out = pathlib.Path('/mnt/user-data/outputs')

def insert_before_niche(s, ch, niche_tech, block):
    key = f'Pour sortir du lot — {niche_tech}'
    i = s.index(key); j = s.rfind('<div class="niche">', 0, i)
    assert j > s.index(f'<span class="chapnum">Chapitre {ch}</span>')
    return s[:j] + block + s[j:]

def add_exos(s, ch, exos):
    key = f'<div class="tp"><span class="tag">Travail pratique {ch}'
    assert key in s
    return s.replace(key, exos + key, 1)

def add_tp_steps(s, ch, steps_html):
    key = f'<div class="tp"><span class="tag">Travail pratique {ch}'
    i = s.index(key); j = s.index('</ol>', i)
    return s[:j] + steps_html + s[j:]

def add_rev(s, after_item, new_items):
    assert after_item in s, after_item[:40]
    return s.replace(after_item, after_item + new_items, 1)

# =====================================================================
# TERRAFORM — chapitre 16
# =====================================================================
TF = r'''<h3>16.7 Le langage, niveau mission<span class="badge tag-coeur">Par cœur</span></h3>
<pre><code># Expressions : for, if, splat, dynamic
locals {
  subnets      = { for k, v in var.subnets : k => v if v.enabled }              # filtrer une map
  subnet_ids   = [for s in aws_subnet.private : s.id]                           # liste depuis for_each
  tags_by_env  = merge(local.tags, var.environment == "prod" ? { Backup = "true" } : {})
  instance_type = var.environment == "prod" ? "m7g.large" : "t4g.small"
}

resource "aws_security_group" "api" {
  name   = "${local.name}-api"
  vpc_id = aws_vpc.main.id
  dynamic "ingress" {                                  # un bloc par élément, sans copier-coller
    for_each = var.allowed_ports
    content {
      from_port       = ingress.value
      to_port         = ingress.value
      protocol        = "tcp"
      security_groups = [aws_security_group.alb.id]
    }
  }
  lifecycle {
    create_before_destroy = true
    precondition {                                     # échoue au plan avec un message clair
      condition     = length(var.allowed_ports) > 0
      error_message = "allowed_ports ne peut pas être vide."
    }
  }
}

# Plusieurs régions ou comptes : alias de provider
provider "aws" { alias = "dr", region = "eu-west-1" }
resource "aws_s3_bucket" "replica" { provider = aws.dr, bucket = "${local.name}-replica" }
module "network_dr" { source = "../../modules/network", providers = { aws = aws.dr }, cidr = "10.30.0.0/16" }

# Assumer un rôle dans un autre compte
provider "aws" { alias = "security", assume_role { role_arn = "arn:aws:iam::222222222222:role/terraform" } }

# Vérifications continues (1.5+) : évaluées à chaque plan, ne bloquent pas, alertent
check "certificate_valid" {
  data "aws_acm_certificate" "api" { domain = "api.crisisshield.example" }
  assert {
    condition     = data.aws_acm_certificate.api.status == "ISSUED"
    error_message = "Le certificat de l'API n'est pas émis."
  }
}

# Refactoring déclaratif, sans toucher au state à la main
moved   { from = aws_instance.web,        to = module.service.aws_instance.web }
removed { from = aws_s3_bucket.legacy,    lifecycle { destroy = false } }      # 1.7+ : oublier sans détruire
import  { to = aws_s3_bucket.logs,        id = "crisisshield-logs" }

# Valeurs sensibles et éphémères
variable "db_password" { type = string, sensitive = true }                     # masqué dans plan et outputs
ephemeral "aws_secretsmanager_secret_version" "db" { secret_id = "crisisshield/prod/db" }   # 1.10+ : jamais écrit dans le state
output "db_endpoint" { value = aws_db_instance.main.endpoint }
output "db_password" { value = var.db_password, sensitive = true }</code></pre>
<ul>
<li><strong>Fonctions à connaître sans réfléchir</strong> : <code>merge</code>, <code>lookup</code>, <code>try</code>, <code>coalesce</code>, <code>cidrsubnet</code>, <code>templatefile</code>, <code>jsonencode</code>/<code>yamldecode</code>, <code>flatten</code>, <code>zipmap</code>, <code>setproduct</code>, <code>format</code>, <code>regex</code>, <code>can</code>. <code>terraform console</code> pour les tester sur le state réel.</li>
<li><strong>Types</strong> : <code>object({ name = string, size = optional(number, 20) })</code> avec valeurs par défaut ; <code>validation</code> sur chaque variable exposée par un module ; <code>nullable = false</code>.</li>
<li><strong>Modules</strong> : une interface minimale (peu de variables, des objets), des outputs pour tout ce qu'un autre module pourrait consommer, un <code>README</code> généré (<code>terraform-docs</code>), une version par tag Git ou registre privé, des exemples dans <code>examples/</code> qui servent de tests. Composer des petits modules plutôt qu'un module « tout-en-un » à 80 variables.</li>
<li><strong>Provisioners</strong> (<code>local-exec</code>, <code>remote-exec</code>) : dernier recours ; ils ne sont pas idempotents et cassent le modèle. Préférer <code>user_data</code>, Packer, Ansible, ou un opérateur.</li>
<li><strong>OpenTofu</strong> : mêmes fichiers ; en plus, chiffrement du state côté client, <code>for_each</code> sur les providers, fonctions fournies par des providers. Choix par licence et politique interne, pas par fonctionnalité.</li>
</ul>

<h3>16.8 Exploitation quotidienne, débogage, erreurs fréquentes<span class="badge tag-coeur">Par cœur</span></h3>
<pre><code>terraform plan -out=tfplan -input=false -lock-timeout=5m          # attendre un verrou plutôt qu'échouer
terraform apply tfplan                                            # jamais apply sans plan sauvegardé en prod
terraform plan -refresh=false                                     # rapide : ne relit pas le cloud (à ne pas faire avant un apply)
terraform plan -target=module.db                                  # chirurgie ; laisse le graphe incohérent, à réserver aux incidents
terraform apply -replace=aws_instance.web                         # forcer une recréation
terraform state list | grep aws_instance ; terraform state show ADRESSE
terraform state pull > backup.tfstate                             # sauvegarde avant toute manipulation
terraform providers lock -platform=linux_amd64 -platform=windows_amd64   # lockfile multi-plateforme (Git Bash + CI)
terraform graph | dot -Tsvg > graph.svg                           # dépendances, cycles
TF_LOG=DEBUG TF_LOG_PATH=tf.log terraform plan                    # appels API du provider
terraform test                                                    # fichiers *.tftest.hcl, avec mock_provider pour ne rien créer
terraform output -raw kubeconfig > ~/.kube/config                 # sortie brute
terraform fmt -recursive -check ; terraform validate              # en pre-commit et en CI</code></pre>
<div class="tablewrap"><table>
<tr><th>Symptôme</th><th>Cause probable</th><th>Remède</th></tr>
<tr><td><code>Error acquiring the state lock</code></td><td>Un apply précédent a été interrompu, ou un collègue applique en même temps</td><td>Vérifier qu'aucun apply ne tourne, puis <code>force-unlock ID</code> ; en CI, <code>resource_group</code> et <code>-lock-timeout</code></td></tr>
<tr><td><code>Provider produced inconsistent final plan</code></td><td>Le provider a changé une valeur après le plan (souvent un bug de provider ou une valeur calculée)</td><td>Relancer plan+apply ; épingler ou mettre à jour le provider ; isoler avec <code>-target</code> en dernier recours</td></tr>
<tr><td>Le plan veut recréer une ressource « sans raison »</td><td>Attribut à remplacement forcé (nom, AZ, type de stockage), <code>count</code> décalé, valeur qui change à chaque plan (timestamp, <code>uuid()</code>)</td><td>Lire la ligne <code># forces replacement</code> ; <code>for_each</code> ; <code>ignore_changes</code> sur ce que le cloud modifie (tags automatiques, <code>desired_count</code> géré par l'autoscaling)</td></tr>
<tr><td>Dérive permanente sur des tags ou des règles</td><td>Un autre système écrit sur la ressource (autoscaler, console, contrôleur)</td><td><code>ignore_changes</code> ciblé, ou une seule source de vérité</td></tr>
<tr><td><code>Cycle:</code> au plan</td><td>Deux ressources se référencent mutuellement (SG A → SG B → SG A)</td><td>Séparer les règles (<code>aws_security_group_rule</code>) ou casser la dépendance avec une ressource intermédiaire</td></tr>
<tr><td><code>depends_on</code> partout et plan lent</td><td>Dépendances implicites ignorées, state trop gros</td><td>Référencer les attributs, supprimer les <code>depends_on</code> inutiles, découper le state</td></tr>
<tr><td>Le state contient un secret en clair</td><td>Toute valeur d'attribut est stockée</td><td>Backend chiffré et accès restreint ; <code>ephemeral</code> ; générer le secret dans Vault/Secrets Manager plutôt que dans Terraform</td></tr>
<tr><td>Apply réussi mais rien ne marche</td><td>Terraform valide l'API, pas le fonctionnement</td><td>Smoke test après apply dans le pipeline ; <code>check</code> blocks ; Terratest pour un vrai test d'intégration</td></tr>
<tr><td>Le lockfile échoue en CI Linux après un init sous Windows</td><td>Hashes d'une seule plateforme</td><td><code>providers lock</code> avec les deux plateformes, commité</td></tr>
<tr><td>Le state a été supprimé ou corrompu</td><td>Bucket sans versioning, manipulation manuelle</td><td>Restaurer la version précédente du bucket ; sinon <code>import</code> ressource par ressource depuis les tags</td></tr>
</table></div>
<p>Méthode devant un plan inattendu : lire le plan en entier avant d'agir ; chercher <code>forces replacement</code> et <code>-/+</code> ; comparer avec <code>state show</code> ; ne jamais « appliquer pour voir » en production ; si la ressource est une base de données, s'arrêter et sauvegarder. Un <code>apply</code> en production se fait depuis la CI, après un plan revu, avec un plan sauvegardé, dans une fenêtre, avec un retour arrière connu (le commit précédent).</p>
'''
TF_EXOS = r'''<div class="exo"><span class="tag">Exercice 16.4</span>
<p>Un module doit créer N buckets à partir d'une liste de noms, chacun avec versioning si un booléen est vrai, et exposer la map nom → ARN. Écris-le avec <code>for_each</code>, <code>dynamic</code> ou une expression conditionnelle, et un output.</p>
<details><summary>Corrigé</summary><div class="sol"><pre><code>variable "buckets" { type = map(object({ versioned = optional(bool, false) })) }
resource "aws_s3_bucket" "b" { for_each = var.buckets, bucket = each.key }
resource "aws_s3_bucket_versioning" "v" {
  for_each = { for k, v in var.buckets : k => v if v.versioned }
  bucket   = aws_s3_bucket.b[each.key].id
  versioning_configuration { status = "Enabled" }
}
output "arns" { value = { for k, b in aws_s3_bucket.b : k => b.arn } }</code></pre></div></details></div>

<div class="exo"><span class="tag">Exercice 16.5</span>
<p>Le pipeline échoue avec <code>Error acquiring the state lock</code> depuis 20 minutes. Déroule ta procédure, avec les vérifications avant le <code>force-unlock</code>.</p>
<details><summary>Corrigé</summary><div class="sol">Lire le message : il donne l'ID du verrou, qui l'a posé, quand, et depuis quelle machine. Vérifier qu'aucun job ne tourne (pipelines en cours, un collègue en local). Si le poseur est un job mort depuis plus longtemps que la durée d'un apply, <code>terraform force-unlock ID</code> ; puis <code>plan</code> pour vérifier que le state est cohérent (un apply interrompu peut avoir créé des ressources non enregistrées : les importer). Prévention : <code>resource_group</code> en CI, <code>-lock-timeout</code>, et jamais d'apply local sur l'environnement de prod.</div></details></div>

'''
TF_TP = ('<li>Langage : réécris le module réseau avec <code>dynamic</code> pour les règles de security group, des variables typées <code>object</code> avec <code>optional</code> et <code>validation</code>, une <code>precondition</code>, un bloc <code>check</code>, et un alias de provider pour une seconde région LocalStack (deux conteneurs LocalStack ou deux régions du même). <code>terraform-docs</code> génère le README du module.</li>'
         '<li>Débogage : provoque et répare chacun des cas du tableau 16.8 que LocalStack permet (verrou orphelin, cycle de security groups, remplacement forcé, dérive de tags avec <code>ignore_changes</code>, lockfile multi-plateforme entre Git Bash et le conteneur CI). Note pour chacun la ligne du plan qui t\'a mis sur la piste.</li>'
         '<li>Tests : trois <code>.tftest.hcl</code> avec <code>mock_provider</code> (sans rien créer) sur le module réseau, plus un <code>terraform test</code> réel contre LocalStack en CI ; un <code>removed</code> block pour sortir une ressource du state sans la détruire.</li>')

# =====================================================================
# ANSIBLE — chapitre 17
# =====================================================================
AN = r'''<h3>17.7 Ansible en profondeur : variables, flux, stratégies<span class="badge tag-coeur">Par cœur</span></h3>
<p><strong>Précédence des variables</strong> (de la plus faible à la plus forte ; retenir les repères, pas les 22 niveaux) : <code>defaults/</code> d'un rôle &lt; <code>group_vars/all</code> &lt; <code>group_vars/&lt;groupe&gt;</code> &lt; <code>host_vars/</code> &lt; variables du play &lt; <code>vars/</code> d'un rôle &lt; variables de bloc et de tâche &lt; <code>set_fact</code> et <code>register</code> &lt; <code>--extra-vars</code> (toujours gagnant). Règle pratique : les rôles exposent leurs réglages dans <code>defaults/</code>, l'inventaire les surcharge, <code>-e</code> sert aux exécutions ponctuelles.</p>
<pre><code>- name: Déployer l'API avec reprise sur erreur
  hosts: web
  serial: "25%"                     # rolling : un quart des hôtes à la fois
  max_fail_percentage: 0            # on s'arrête au premier hôte en échec
  any_errors_fatal: true
  become: true
  tasks:
    - name: Retirer l'hôte du load balancer
      ansible.builtin.uri: { url: "https://lb.internal/api/drain/{{ inventory_hostname }}", method: POST }
      delegate_to: localhost         # exécuté depuis le contrôleur, pour chaque hôte

    - name: Déployer, avec retour arrière si échec
      block:
        - name: Nouvelle version
          community.docker.docker_compose_v2:
            project_src: /opt/crisisshield
          register: deploy
        - name: Attendre que l'API réponde
          ansible.builtin.uri: { url: "http://localhost:8080/actuator/health/readiness", status_code: 200 }
          register: health
          until: health.status == 200
          retries: 30
          delay: 2
      rescue:
        - name: Revenir à la version précédente
          ansible.builtin.command: /opt/crisisshield/rollback.sh
          changed_when: true
        - ansible.builtin.fail: { msg: "Déploiement annulé sur {{ inventory_hostname }}" }
      always:
        - name: Remettre l'hôte dans le load balancer
          ansible.builtin.uri: { url: "https://lb.internal/api/undrain/{{ inventory_hostname }}", method: POST }
          delegate_to: localhost

    - name: Tâche longue sans bloquer (async)
      ansible.builtin.command: /opt/tools/reindex.sh
      async: 1800
      poll: 0
      register: reindex
    - name: Vérifier plus tard
      ansible.builtin.async_status: { jid: "{{ reindex.ansible_job_id }}" }
      register: job
      until: job.finished
      retries: 60
      delay: 30

    - name: Une seule fois pour tout le groupe
      ansible.builtin.command: /opt/tools/notify-release.sh
      run_once: true
      delegate_to: "{{ groups['web'][0] }}"

    - name: Boucle sur une structure, avec libellé lisible
      ansible.builtin.user:
        name: "{{ item.name }}"
        groups: "{{ item.groups | join(',') }}"
      loop: "{{ users }}"
      loop_control: { label: "{{ item.name }}" }
      when: item.state | default('present') == 'present'

    - name: Idempotence forcée sur une commande
      ansible.builtin.command: /opt/tools/migrate.sh
      register: mig
      changed_when: "'applied' in mig.stdout"
      failed_when: mig.rc not in [0, 3]</code></pre>
<ul>
<li><strong>Stratégies</strong> : <code>linear</code> (défaut, tâche par tâche sur tous les hôtes), <code>free</code> (chaque hôte avance à son rythme : plus rapide, ordre non garanti), <code>debug</code>. <code>serial</code> et <code>throttle</code> contrôlent la vague et la concurrence.</li>
<li><strong>Filtres et lookups à connaître</strong> : <code>default</code>, <code>combine</code>, <code>dict2items</code>/<code>items2dict</code>, <code>selectattr</code>/<code>map(attribute=)</code>, <code>json_query</code>, <code>to_nice_yaml</code>, <code>b64encode</code>, <code>regex_replace</code>, <code>ipaddr</code> ; <code>lookup('file')</code>, <code>lookup('env')</code>, <code>lookup('ansible.builtin.password')</code>, <code>lookup('community.hashi_vault.hashi_vault')</code>. Tester dans un playbook avec <code>ansible.builtin.debug</code>.</li>
<li><strong>Templates</strong> : contrôle des blancs (<code>{%- -%}</code>), macros, <code>{{ ansible_managed }}</code> en entête, <code>validate:</code> sur les fichiers de config, <code>backup: true</code>.</li>
<li><strong>Tags et reprise</strong> : <code>--tags</code>, <code>--skip-tags</code>, <code>--start-at-task</code>, <code>--step</code>, <code>--limit @retry</code> (rejouer seulement les hôtes en échec).</li>
<li><strong>Vault</strong> : plusieurs identités (<code>--vault-id prod@prompt</code>), chiffrer une valeur plutôt qu'un fichier (<code>encrypt_string</code>) pour garder le diff lisible.</li>
</ul>

<h3>17.8 Performance, configuration, erreurs fréquentes<span class="badge tag-important">Important</span></h3>
<pre><code># ansible.cfg : ce qui change tout
[defaults]
inventory          = inventory/
forks              = 50                 # parallélisme (défaut 5 : trop bas)
gathering          = smart              # facts en cache
fact_caching       = jsonfile
fact_caching_connection = /tmp/facts
fact_caching_timeout = 3600
host_key_checking  = True               # False seulement en labo jetable
interpreter_python = auto_silent
stdout_callback    = yaml
retry_files_enabled = True
[ssh_connection]
pipelining         = True               # divise par deux le nombre de connexions SSH
ssh_args           = -o ControlMaster=auto -o ControlPersist=60s</code></pre>
<div class="tablewrap"><table>
<tr><th>Symptôme</th><th>Cause probable</th><th>Remède</th></tr>
<tr><td><code>UNREACHABLE</code></td><td>SSH : clé, utilisateur, port, host key inconnue, hôte non résolu</td><td><code>ansible HOTE -m ping -vvv</code> ; vérifier <code>ansible_user</code>, <code>ansible_ssh_private_key_file</code>, <code>ansible_port</code> ; <code>ssh-keyscan</code> dans <code>known_hosts</code></td></tr>
<tr><td><code>Missing sudo password</code></td><td><code>become</code> sans NOPASSWD</td><td><code>--ask-become-pass</code>, ou sudoers configuré par un rôle de bootstrap</td></tr>
<tr><td><code>/usr/bin/python: not found</code></td><td>Cible minimale sans Python</td><td><code>ansible.builtin.raw: apt-get install -y python3</code> en premier, <code>gather_facts: false</code> pour cette tâche</td></tr>
<tr><td>Le playbook est lent</td><td>forks à 5, pas de pipelining, facts recollectés à chaque play</td><td>Config ci-dessus ; <code>gather_facts: false</code> quand inutile ; <code>strategy: free</code> ; Mitogen pour aller plus loin</td></tr>
<tr><td><code>changed</code> à chaque exécution</td><td><code>shell</code>/<code>command</code> sans <code>creates</code>/<code>changed_when</code>, template avec horodatage</td><td>Modules idempotents ; <code>changed_when</code> ; retirer les valeurs volatiles des templates</td></tr>
<tr><td>Une variable n'a pas la valeur attendue</td><td>Précédence ; typo entre <code>group_vars/web.yml</code> et le nom du groupe</td><td><code>ansible-inventory --host HOTE</code> ; <code>debug: var=</code> ; <code>ansible-playbook --list-hosts</code></td></tr>
<tr><td>Le handler n'a pas tourné</td><td>Aucune tâche n'a notifié, ou le play a échoué avant la fin</td><td><code>meta: flush_handlers</code> pour forcer à un point précis ; <code>--force-handlers</code></td></tr>
<tr><td>Secret affiché dans les logs</td><td>Sortie de module non masquée</td><td><code>no_log: true</code> sur la tâche</td></tr>
<tr><td>Ça marche en local, pas en CI</td><td>Version d'Ansible ou de collection, clé SSH, <code>host_key_checking</code></td><td>Image Ansible épinglée, <code>requirements.yml</code> avec versions, clé dans Vault, <code>known_hosts</code> provisionné</td></tr>
</table></div>
<ul>
<li><strong>Windows</strong> : WinRM ou SSH, modules <code>ansible.windows.*</code>, <code>win_updates</code>, <code>win_feature</code> ; très demandé dans les DSI mixtes.</li>
<li><strong>À l'échelle</strong> : AWX (open source) ou Ansible Automation Platform (Red Hat) pour l'ordonnancement, les credentials, le RBAC, l'audit et les workflows ; Semaphore comme alternative légère ; <code>ansible-pull</code> pour des nœuds qui se configurent eux-mêmes depuis Git.</li>
<li><strong>Qualité</strong> : <code>ansible-lint</code> avec un profil (<code>production</code>), Molecule avec plusieurs scénarios (Debian, RHEL), <code>--check --diff</code> en merge request, noms complets des modules, collections épinglées.</li>
</ul>
'''
AN_EXOS = r'''<div class="exo"><span class="tag">Exercice 17.3</span>
<p>Un playbook de mise à jour touche 40 serveurs web derrière un load balancer. Écris le squelette qui garantit : jamais plus de 10 % hors service, arrêt global au premier échec, retrait et remise dans le load balancer, retour arrière automatique sur l'hôte en échec.</p>
<details><summary>Corrigé</summary><div class="sol"><code>serial: "10%"</code>, <code>max_fail_percentage: 0</code>, <code>any_errors_fatal: true</code> ; tâche de retrait en <code>delegate_to: localhost</code> ; <code>block</code> avec le déploiement et l'attente de readiness (<code>until</code>/<code>retries</code>), <code>rescue</code> qui exécute le rollback puis <code>fail</code>, <code>always</code> qui remet l'hôte dans le load balancer. C'est le playbook de la section 17.7.</div></details></div>

<div class="exo"><span class="tag">Exercice 17.4</span>
<p>Tu définis <code>api_version: 1.4.0</code> dans <code>group_vars/web.yml</code>, mais le playbook déploie <code>1.3.0</code>. Cite quatre endroits qui peuvent gagner sur ta valeur et la commande qui tranche.</p>
<details><summary>Corrigé</summary><div class="sol"><code>host_vars/</code> de l'hôte, <code>vars:</code> du play, <code>vars/main.yml</code> d'un rôle, un <code>set_fact</code> ou <code>--extra-vars</code> dans le pipeline. Trancher : <code>ansible-inventory --host HOTE --yaml</code> montre les variables d'inventaire ; une tâche <code>debug: var=api_version</code> au début du play montre la valeur effective, et <code>-vvv</code> montre les <code>-e</code> passés.</div></details></div>

'''
AN_TP = ('<li>Flux et stratégies : réécris le déploiement de l\'API avec <code>serial</code>, <code>block/rescue/always</code>, retrait et remise dans un « load balancer » simulé (le proxy nginx du TP 3, piloté par un endpoint ou un fichier), <code>until</code> sur la readiness, et un rollback. Provoque un échec sur un hôte et vérifie l\'arrêt global et le retour arrière. Compare la durée en <code>strategy: linear</code> et <code>free</code> avec <code>forks</code> à 5 puis à 50 et le pipelining.</li>'
         '<li>Variables : reproduis l\'exercice 17.4 en créant volontairement le conflit, tranche avec <code>ansible-inventory --host</code>, puis range les variables selon la règle (defaults du rôle, inventaire, extra-vars ponctuels). Deux identités de vault (<code>dev</code>, <code>prod</code>) et une valeur chiffrée inline.</li>'
         '<li>Erreurs : reproduis cinq lignes du tableau 17.8 (UNREACHABLE, Python absent, become, changed permanent, secret dans les logs) et corrige chacune ; <code>ansible-lint</code> profil <code>production</code> vert.</li>')

# =====================================================================
# KUBERNETES — chapitres 25 et 26
# =====================================================================
K25 = r'''<h3>25.5 kubectl expert et débogage méthodique<span class="badge tag-coeur">Par cœur</span></h3>
<pre><code># Lire précisément
kubectl get pods -o wide --sort-by=.metadata.creationTimestamp
kubectl get pods -A --field-selector=status.phase!=Running
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}'
kubectl get pods -o custom-columns='NOM:.metadata.name,NOEUD:.spec.nodeName,REDEMARRAGES:.status.containerStatuses[*].restartCount'
kubectl get events -A --sort-by=.lastTimestamp | tail -30 ; kubectl get events -w
kubectl get deploy api -o yaml | kubectl neat                 # sans le bruit (plugin krew)
kubectl explain pod.spec.containers.securityContext --recursive
kubectl api-resources --namespaced=true ; kubectl api-versions
kubectl auth can-i --list --as=system:serviceaccount:crisisshield:api
kubectl top pods --containers ; kubectl top nodes

# Agir avec précision
kubectl rollout restart deploy/api ; kubectl rollout status deploy/api --timeout=120s
kubectl set image deploy/api api=registry/api@sha256:... --record=false
kubectl scale deploy/api --replicas=0 ; kubectl patch deploy api -p '{"spec":{"template":{"metadata":{"annotations":{"redeploy":"'$(date +%s)'"}}}}}'
kubectl cordon NOEUD ; kubectl drain NOEUD --ignore-daemonsets --delete-emptydir-data ; kubectl uncordon NOEUD
kubectl cp crisisshield/api-xxx:/tmp/heap.hprof ./heap.hprof
kubectl exec -it api-xxx -c api -- sh ; kubectl debug -it api-xxx --image=nicolaka/netshoot --target=api
kubectl debug node/NOEUD -it --image=ubuntu           # shell sur le nœud, système de fichiers dans /host
kubectl port-forward svc/api 8080:80 ; kubectl proxy
kubectl delete pod api-xxx --grace-period=0 --force     # dernier recours pour un Terminating bloqué
kubectl patch pvc data -p '{"metadata":{"finalizers":null}}'   # finalizer bloquant, après avoir compris pourquoi

# Outils qui font gagner des heures (tous en conteneur ou en binaire dans ton image outillée)
k9s                     # interface texte : ressources, logs, shell, en un clic
stern -n crisisshield api   # logs de tous les Pods d'un service, colorés
kubectl krew install neat ctx ns tree view-secret sniff who-can   # plugins
kubectl tree deploy api ; kubectl view-secret api-db password ; kubectl who-can delete pods</code></pre>
<div class="tablewrap"><table>
<tr><th>État ou symptôme</th><th>Où regarder</th><th>Causes fréquentes</th></tr>
<tr><td><code>Pending</code></td><td><code>describe pod</code> → Events</td><td>Ressources insuffisantes, taint non tolérée, affinité impossible, PVC non lié, quota du namespace, PriorityClass basse</td></tr>
<tr><td><code>ImagePullBackOff</code> / <code>ErrImagePull</code></td><td>Events : <code>manifest unknown</code>, <code>unauthorized</code>, <code>timeout</code></td><td>Tag inexistant, registre privé sans <code>imagePullSecret</code>, réseau du nœud, digest d'une autre architecture</td></tr>
<tr><td><code>CrashLoopBackOff</code></td><td><code>logs --previous</code>, code de sortie dans <code>describe</code></td><td>Config manquante, port occupé, dépendance injoignable au démarrage, liveness trop agressive, entrypoint qui sort</td></tr>
<tr><td><code>OOMKilled</code> (137)</td><td><code>describe</code> → Last State ; <code>top pods</code></td><td>Limite mémoire trop basse, JVM sans <code>MaxRAMPercentage</code>, fuite</td></tr>
<tr><td><code>Evicted</code></td><td><code>describe pod</code> → message ; <code>describe node</code> → Conditions</td><td>Nœud en pression disque ou mémoire ; Pods BestEffort évincés en premier</td></tr>
<tr><td><code>Terminating</code> qui ne finit pas</td><td><code>get pod -o yaml</code> → finalizers ; kubelet du nœud</td><td>Finalizer d'un contrôleur mort, nœud injoignable, volume qui ne se détache pas</td></tr>
<tr><td>Service qui ne répond pas</td><td><code>get endpointslices</code> ; <code>describe svc</code></td><td>Sélecteur qui ne matche aucun label, Pods non prêts (readiness), mauvais <code>targetPort</code>, NetworkPolicy</td></tr>
<tr><td>Ingress 404 ou 503</td><td>Logs du contrôleur d'ingress ; <code>describe ingress</code></td><td><code>ingressClassName</code> absent, hôte ou chemin faux, Service inexistant, TLS secret manquant, backend non prêt</td></tr>
<tr><td>DNS ne résout pas</td><td><code>kubectl debug</code> netshoot : <code>nslookup api.crisisshield.svc</code> ; logs de CoreDNS</td><td>NetworkPolicy qui bloque le port 53, CoreDNS surchargé ou mal configuré, <code>ndots</code></td></tr>
<tr><td>PVC <code>Pending</code></td><td><code>describe pvc</code> ; <code>get storageclass</code></td><td>StorageClass absente ou sans provisioner, mode d'accès non supporté, zone différente du Pod (<code>WaitForFirstConsumer</code>)</td></tr>
<tr><td>Nœud <code>NotReady</code></td><td><code>describe node</code> ; <code>journalctl -u kubelet</code> sur le nœud</td><td>Kubelet arrêté, disque plein, CNI en panne, certificat expiré, réseau vers l'API</td></tr>
<tr><td>HPA n'agit pas</td><td><code>describe hpa</code> → <code>unknown</code></td><td>metrics-server absent, requests non définies, métrique custom absente</td></tr>
<tr><td>Rolling update bloqué</td><td><code>rollout status</code> ; <code>describe rs</code></td><td>Nouveaux Pods jamais prêts (readiness), PDB, ressources, <code>progressDeadlineSeconds</code> dépassé → <code>rollout undo</code></td></tr>
</table></div>
<p>Méthode, toujours dans cet ordre : <code>get</code> (quel objet, quel état), <code>describe</code> (les événements, en bas), <code>logs</code> (avec <code>--previous</code> si redémarrage), puis remonter la chaîne Ingress → Service → EndpointSlices → Pod → conteneur, et enfin le nœud. Ne jamais commencer par redémarrer : on perd l'information.</p>

<h3>25.6 Administrer le cluster : etcd, certificats, mises à jour, nœuds<span class="badge tag-important">Important</span></h3>
<pre><code># etcd : sauvegarde et restauration (kubeadm, kind ; sur un cluster managé c'est le fournisseur)
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /backup/etcd-$(date +%F).db
etcdctl snapshot status /backup/etcd-2026-09-21.db -w table
etcdctl snapshot restore /backup/etcd-2026-09-21.db --data-dir /var/lib/etcd-restore   # puis pointer le manifest static pod dessus

# Certificats (kubeadm) : expirent au bout d'un an
kubeadm certs check-expiration
kubeadm certs renew all && systemctl restart kubelet     # puis redémarrer les static pods du control plane

# Mise à jour (kubeadm) : une version mineure à la fois, control plane puis nœuds
apt-get install -y kubeadm=1.32.x-* ; kubeadm upgrade plan ; kubeadm upgrade apply v1.32.x
kubectl drain NOEUD --ignore-daemonsets ; apt-get install -y kubelet=1.32.x-* kubectl=1.32.x-* ; systemctl restart kubelet ; kubectl uncordon NOEUD
# Avant : détecter les API dépréciées dans tes manifests
docker run --rm -v "$PWD:/w" ghcr.io/fairwindsops/pluto detect-files -d /w

# Santé du control plane
kubectl get --raw='/readyz?verbose' ; kubectl get componentstatuses   # (déprécié mais encore lu)
kubectl -n kube-system logs kube-apiserver-control-plane --tail=100
kubectl get lease -n kube-node-lease                                   # battement de cœur des nœuds</code></pre>
<ul>
<li><strong>Cluster managé</strong> (EKS, AKS, GKE) : le control plane, etcd et ses sauvegardes, les certificats sont gérés ; te restent les nœuds (mise à jour par remplacement, chapitre 31), les add-ons (versions compatibles), les API dépréciées, et la cadence (une mineure tous les 4 mois, 14 mois de support : une mise à jour par trimestre).</li>
<li><strong>Nœuds</strong> : <code>cordon</code> avant toute intervention, <code>drain</code> respecte les PDB (d'où leur importance) ; un nœud qui ne se draine pas a un Pod sans contrôleur ou un PDB trop strict ; <code>kubectl debug node</code> ou SSM pour inspecter ; remplacer plutôt que réparer.</li>
<li><strong>Kubelet</strong> : <code>--eviction-hard</code>, réservations système (<code>--system-reserved</code>, <code>--kube-reserved</code>) pour que le nœud ne meure pas sous les Pods ; rotation des logs de conteneurs ; garbage collection des images.</li>
<li><strong>Sauvegarde applicative</strong> (Velero, chapitre 44) complète etcd : etcd restaure l'état du cluster, pas les données des volumes.</li>
<li><strong>Certifications</strong> : la CKA couvre exactement ces sections (25.5, 25.6, 26, 27) ; la CKS couvre les chapitres 39 à 41. Les passer valide ce parcours à peu de frais.</li>
</ul>
'''
K25_EXOS = r'''<div class="exo"><span class="tag">Exercice 25.3</span>
<p>Un Service <code>api</code> renvoie « connection refused » depuis le front, alors que <code>kubectl get pods</code> montre trois Pods <code>Running</code>. Donne, dans l'ordre, les quatre commandes qui localisent le problème et ce que chacune peut révéler.</p>
<details><summary>Corrigé</summary><div class="sol"><code>kubectl get endpointslices -l kubernetes.io/service-name=api</code> : vide → sélecteur du Service qui ne correspond pas aux labels des Pods, ou Pods non prêts. <code>kubectl describe svc api</code> : <code>targetPort</code> contre le port du conteneur. <code>kubectl get pods -o wide</code> avec la colonne READY : <code>0/1</code> → readiness en échec, voir <code>describe pod</code>. <code>kubectl debug</code> netshoot : <code>curl POD_IP:8080</code> direct puis <code>curl api:80</code> → distingue application, Service et NetworkPolicy.</div></details></div>

<div class="exo"><span class="tag">Exercice 25.4</span>
<p>Ton cluster kubeadm a un an ; ce matin <code>kubectl</code> répond <code>x509: certificate has expired</code>. Que fais-tu, et comment éviter que ça se reproduise ?</p>
<details><summary>Corrigé</summary><div class="sol">Sur le control plane : <code>kubeadm certs check-expiration</code>, <code>kubeadm certs renew all</code>, redémarrer les static pods (déplacer et remettre leurs manifests dans <code>/etc/kubernetes/manifests</code>) et le kubelet, régénérer le kubeconfig admin. Les applications ont continué de tourner ; seuls l'API et les contrôleurs étaient touchés. Prévention : alerte à 30 jours sur l'expiration (métriques de l'API server, cert-manager pour les certificats applicatifs), mise à jour du cluster au moins une fois par an (kubeadm renouvelle à chaque upgrade), ou cluster managé.</div></details></div>

'''
K25_TP = ('<li>Débogage méthodique : construis huit scénarios cassés sur CrisisShield (mauvais sélecteur de Service, <code>targetPort</code> faux, image inexistante, liveness sur la base, quota du namespace saturé, NetworkPolicy qui bloque le DNS, PVC sans StorageClass, PDB qui empêche un drain) sous forme de manifests <code>k8s/kata/casse-N.yaml</code> ; pour chacun, écris le diagnostic en trois commandes maximum et la correction. C\'est ton kata de révision CKA.</li>'
          '<li>Administration : sur kind, prends un snapshot etcd (depuis le conteneur du control plane), déploie un objet, restaure le snapshot et constate la disparition de l\'objet ; vérifie l\'expiration des certificats du control plane ; installe k9s, stern et cinq plugins krew dans ton image outillée ; passe le cluster d\'une version mineure à la suivante avec Pluto en amont.</li>')

K26 = r'''<h3>26.7 Manifests avancés : ce que le Deployment de référence ne montre pas<span class="badge tag-important">Important</span></h3>
<pre><code>spec:
  template:
    spec:
      initContainers:
        - name: migrate                                  # s'exécute et se termine avant l'application
          image: registry/api@sha256:...
          command: ["java", "-cp", "app.jar", "-Dloader.main=fr.crisisshield.Migrate", "org.springframework.boot.loader.launch.PropertiesLauncher"]
          envFrom: [{configMapRef: {name: api-config}}]
        - name: otel-agent                               # sidecar natif (1.29+) : démarre avant, s'arrête après l'app
          image: registry/otel-agent@sha256:...
          restartPolicy: Always
      containers:
        - name: api
          image: registry/api@sha256:...
          env:
            - name: POD_NAME
              valueFrom: {fieldRef: {fieldPath: metadata.name}}          # Downward API
            - name: NODE_NAME
              valueFrom: {fieldRef: {fieldPath: spec.nodeName}}
            - name: MEM_LIMIT
              valueFrom: {resourceFieldRef: {resource: limits.memory}}
          lifecycle:
            postStart: {exec: {command: ["sh", "-c", "echo started >> /tmp/lifecycle"]}}
            preStop:   {exec: {command: ["sh", "-c", "sleep 5"]}}
          volumeMounts:
            - {name: podinfo, mountPath: /etc/podinfo, readOnly: true}
            - {name: sa-token, mountPath: /var/run/secrets/tokens, readOnly: true}
      volumes:
        - name: podinfo
          downwardAPI:
            items: [{path: labels, fieldRef: {fieldPath: metadata.labels}}]
        - name: sa-token
          projected:                                       # jeton de SA à audience et durée limitées (pour Vault, l'IdP)
            sources:
              - serviceAccountToken: {path: vault, audience: vault, expirationSeconds: 3600}
      dnsPolicy: ClusterFirst
      dnsConfig: {options: [{name: ndots, value: "2"}]}   # moins de requêtes DNS inutiles pour les noms externes
      hostAliases: [{ip: "10.0.5.7", hostnames: [legacy.internal]}]
      enableServiceLinks: false                            # évite des dizaines de variables d'environnement inutiles
      priorityClassName: critical
      schedulerName: default-scheduler</code></pre>
<ul>
<li><strong>Init containers</strong> : migrations, attente d'une dépendance (préférer la readiness et les retries), préparation d'un volume. <strong>Sidecars natifs</strong> (<code>restartPolicy: Always</code> dans <code>initContainers</code>) : agents de logs, proxies, avec un ordre de démarrage et d'arrêt correct, ce qui règle le vieux problème des Jobs avec sidecar.</li>
<li><strong>Stratégies de mise à jour</strong> : Deployment <code>RollingUpdate</code> (<code>maxSurge</code>, <code>maxUnavailable</code>, <code>minReadySeconds</code>, <code>progressDeadlineSeconds</code>) ou <code>Recreate</code> ; StatefulSet <code>RollingUpdate</code> avec <code>partition</code> (canary manuel sur les réplicas d'index supérieur) ou <code>OnDelete</code> ; DaemonSet <code>RollingUpdate</code> avec <code>maxUnavailable</code>.</li>
<li><strong>Jobs</strong> : <code>completions</code>, <code>parallelism</code>, <code>completionMode: Indexed</code> (chaque Pod connaît son index), <code>backoffLimit</code>, <code>activeDeadlineSeconds</code>, <code>ttlSecondsAfterFinished</code>, <code>podFailurePolicy</code> (ne pas réessayer sur certains codes). CronJob : <code>concurrencyPolicy</code>, <code>startingDeadlineSeconds</code>, <code>timeZone</code>.</li>
<li><strong>Classes QoS</strong> : Guaranteed (requests = limits sur CPU et mémoire), Burstable, BestEffort ; ordre d'éviction inverse. Les bases en Guaranteed, les API en Burstable, jamais de BestEffort en production.</li>
<li><strong>Volumes éphémères génériques</strong> (<code>ephemeral:</code> avec <code>volumeClaimTemplate</code>) pour un scratch disque par Pod ; <code>emptyDir.medium: Memory</code> avec <code>sizeLimit</code> pour les secrets et le cache.</li>
<li><strong>Canary sans outil</strong> : deux Deployments (<code>api</code> 9 réplicas, <code>api-canary</code> 1 réplica) derrière le même Service : 10 % du trafic ; puis Argo Rollouts pour l'automatiser (chapitre 31).</li>
</ul>

<h3>26.8 Vingt questions d'entretien Kubernetes, avec la réponse courte<span class="badge tag-coeur">Par cœur</span></h3>
<div class="tablewrap"><table>
<tr><th>Question</th><th>Réponse attendue</th></tr>
<tr><td>Que se passe-t-il quand un nœud tombe ?</td><td>Après ~40 s le nœud passe NotReady ; après le <code>tolerationSeconds</code> par défaut (5 min) les Pods sont marqués pour éviction et recréés ailleurs par leurs contrôleurs ; les Pods d'un StatefulSet attendent la confirmation (volume RWO).</td></tr>
<tr><td>Deployment contre StatefulSet contre DaemonSet ?</td><td>Réplicas interchangeables ; identité et volume stables avec ordre ; un Pod par nœud.</td></tr>
<tr><td>Requests contre limits ?</td><td>Requests : réservation pour le scheduler et le partage CPU ; limits : plafond (OOMKill mémoire, throttling CPU). QoS selon leur égalité.</td></tr>
<tr><td>Liveness contre readiness contre startup ?</td><td>Redémarrer si bloqué ; retirer du trafic si indisponible ; protéger un démarrage lent.</td></tr>
<tr><td>Comment un Service trouve-t-il ses Pods ?</td><td>Par sélecteur de labels ; les EndpointSlices listent les Pods prêts ; kube-proxy (ou eBPF) programme le routage.</td></tr>
<tr><td>ClusterIP, NodePort, LoadBalancer, Ingress ?</td><td>Interne ; port sur chaque nœud ; équilibreur cloud par Service ; routage HTTP mutualisé derrière un seul équilibreur.</td></tr>
<tr><td>Que fait <code>kubectl apply</code> exactement ?</td><td>Envoi à l'API, authentification, RBAC, admission (mutation puis validation), écriture etcd, puis les contrôleurs réconcilient (chapitre 25).</td></tr>
<tr><td>Comment isoler deux équipes sur un cluster ?</td><td>Namespaces, RBAC, ResourceQuota, LimitRange, NetworkPolicy default-deny, PSA, politiques d'admission ; nœuds dédiés par taints si besoin.</td></tr>
<tr><td>Un Secret est-il chiffré ?</td><td>Encodé en base64 seulement ; chiffrement au repos à activer (KMS), RBAC, et un gestionnaire externe via External Secrets.</td></tr>
<tr><td>Comment déployer sans interruption ?</td><td>RollingUpdate avec <code>maxUnavailable: 0</code>, readiness, preStop, PDB, compatibilité N-1 du schéma.</td></tr>
<tr><td>Comment revenir en arrière ?</td><td><code>rollout undo</code> (ReplicaSet précédent conservé), ou <code>git revert</code> en GitOps ; par digest, sans rebuild.</td></tr>
<tr><td>Pourquoi un Pod reste Pending ?</td><td>Ressources, taints, affinités, PVC, quota, priorité ; <code>describe</code> le dit.</td></tr>
<tr><td>Que contient etcd et comment le sauvegarder ?</td><td>Tout l'état du cluster ; <code>etcdctl snapshot save</code>, ou le fournisseur en managé ; Velero pour les volumes.</td></tr>
<tr><td>Comment gérer la configuration par environnement ?</td><td>ConfigMaps et Secrets, Kustomize overlays ou Helm values, GitOps par environnement ; jamais une image par environnement.</td></tr>
<tr><td>Comment un Pod s'authentifie-t-il auprès d'un service externe ?</td><td>ServiceAccount et jeton projeté (audience, durée), fédéré vers IAM, Vault ou l'IdP ; jamais de clé statique.</td></tr>
<tr><td>Que fait un opérateur ?</td><td>Un contrôleur qui réconcilie une CRD et encode le savoir-faire d'exploitation d'une application (bascule, sauvegarde, mise à jour).</td></tr>
<tr><td>Comment mettre à jour un cluster ?</td><td>Une mineure à la fois, API dépréciées détectées avant, control plane puis nœuds par drain et remplacement, add-ons vérifiés, staging d'abord.</td></tr>
<tr><td>Comment limiter le rayon d'impact d'une maintenance de nœud ?</td><td>PDB, topologySpread, plusieurs réplicas, drain respectueux, autoscaler qui compense.</td></tr>
<tr><td>Helm ou Kustomize ?</td><td>Helm pour les paquets tiers et la distribution, Kustomize pour les variantes de ses applications ; les deux avec ArgoCD.</td></tr>
<tr><td>Que ferais-tu en premier sur un cluster que tu ne connais pas ?</td><td><code>get nodes</code>, <code>get pods -A</code> non Running, events récents, version et support, RBAC (qui est cluster-admin), sauvegardes etcd, PSA et politiques, coût ; puis les SLO de la plateforme (chapitre 43).</td></tr>
</table></div>
'''
K26_EXOS = r'''<div class="exo"><span class="tag">Exercice 26.4</span>
<p>Un Job de migration doit tourner avec un sidecar Vault Agent qui fournit les identifiants de base. Avec un sidecar classique, le Job ne se termine jamais. Pourquoi, et quelle est la solution moderne ?</p>
<details><summary>Corrigé</summary><div class="sol">Le Job attend que tous ses conteneurs se terminent ; le sidecar tourne indéfiniment. Solution depuis Kubernetes 1.29 : déclarer l'agent comme sidecar natif (<code>initContainers</code> avec <code>restartPolicy: Always</code>) : il démarre avant le conteneur principal et est arrêté automatiquement quand celui-ci se termine. Avant 1.29 : appel à l'endpoint d'arrêt de l'agent en fin de script, ou injection par init container seulement.</div></details></div>

'''
K26_TP = ('<li>Manifests avancés : ajoute à l\'API un init container de migration Flyway, un sidecar natif de collecte de logs, la Downward API pour <code>POD_NAME</code> dans les logs, un jeton de ServiceAccount projeté à audience <code>vault</code>, <code>ndots: 2</code>, <code>enableServiceLinks: false</code> ; un Job indexé de traitement par lots avec <code>podFailurePolicy</code> ; un canary manuel à deux Deployments derrière le même Service, mesuré avec une boucle curl. Vérifie la classe QoS de chaque Pod (<code>get pod -o jsonpath=\'{.status.qosClass}\'</code>) et corrige pour qu\'aucun ne soit BestEffort.</li>'
          '<li>Entretien : réponds aux vingt questions de la section 26.8 à voix haute, chronométrées à 45 secondes chacune ; enregistre-toi ; note celles où tu as hésité et reprends la section correspondante.</li>')

# =====================================================================
# Application
# =====================================================================
# --- Niveau 3 : Terraform et Ansible
p = out/'devops-03-infrastructure-as-code.html'; s = p.read_text()
assert '16.7 Le langage' not in s
s = insert_before_niche(s, 16, 'Pulumi en Java ou Kotlin', TF)
s = add_exos(s, 16, TF_EXOS); s = add_tp_steps(s, 16, TF_TP)
s = insert_before_niche(s, 17, 'Event-Driven Ansible', AN)
s = add_exos(s, 17, AN_EXOS); s = add_tp_steps(s, 17, AN_TP)
s = s.replace('<li>Tester, valider et sécuriser du code Terraform dans la CI</li>',
              '<li>Tester, valider et sécuriser du code Terraform dans la CI</li><li>Écrire du HCL avancé (dynamic, for, alias de providers, check, moved, ephemeral) et diagnostiquer les erreurs fréquentes</li>', 1)
s = s.replace('<li>Positionner Ansible par rapport à Terraform et aux conteneurs</li>',
              '<li>Positionner Ansible par rapport à Terraform et aux conteneurs</li><li>Maîtriser la précédence des variables, block/rescue, serial, delegate, async, les stratégies et la configuration de performance</li>', 1)
s = s.replace('<li>import, moved, state mv, force-unlock : les outils de réparation ; apply uniquement depuis la CI.</li>',
              '<li>import, moved, state mv, force-unlock : les outils de réparation ; apply uniquement depuis la CI.</li><li>Lire le plan en entier, chercher « forces replacement », ne jamais appliquer pour voir ; dynamic, for_each, alias de providers et check sont le quotidien.</li>', 1)
s = s.replace('<li>Dans un monde conteneurisé, il prépare les hôtes et orchestre les opérations ; il ne déploie plus l\'application.</li>',
              '<li>Dans un monde conteneurisé, il prépare les hôtes et orchestre les opérations ; il ne déploie plus l\'application.</li><li>defaults du rôle &lt; inventaire &lt; play &lt; tâche &lt; extra-vars ; serial et block/rescue/always pour les déploiements ; forks et pipelining pour la vitesse.</li>', 1)
s = add_rev(s, '<li><code>import</code>, <code>state mv</code>, <code>moved</code>, <code>force-unlock</code> : quand.</li>',
            '<li><code>dynamic</code>, <code>for_each</code> avec filtre, alias de providers, <code>check</code>, <code>removed</code>, <code>ephemeral</code> : un exemple chacun.</li><li>Cinq erreurs Terraform fréquentes et leur remède ; la méthode devant un plan inattendu.</li>')
s = add_rev(s, '<li>Ansible Vault contre HashiCorp Vault.</li>',
            '<li>Précédence des variables Ansible ; <code>block/rescue/always</code>, <code>serial</code>, <code>delegate_to</code>, <code>run_once</code>, <code>async</code>, <code>until</code>.</li><li>Les réglages d\'<code>ansible.cfg</code> qui changent la vitesse ; cinq erreurs fréquentes et leur remède.</li>')
p.write_text(s); print('niveau 3 :', re.findall(r'<h3>(1[67]\.\d) ', s))

# --- Niveau 5 : Kubernetes
p = out/'devops-05-kubernetes.html'; s = p.read_text()
assert '25.5 kubectl expert' not in s
s = insert_before_niche(s, 25, 'kwok (Kubernetes WithOut Kubelet)', K25)
s = add_exos(s, 25, K25_EXOS); s = add_tp_steps(s, 25, K25_TP)
s = insert_before_niche(s, 26, 'Envoy Gateway', K26)
s = add_exos(s, 26, K26_EXOS); s = add_tp_steps(s, 26, K26_TP)
s = s.replace('<li>Lancer un cluster local dans Docker et le piloter avec kubectl en conteneur</li>',
              '<li>Lancer un cluster local dans Docker et le piloter avec kubectl en conteneur</li><li>Diagnostiquer méthodiquement tout état de Pod, de Service ou de nœud, et administrer le cluster (etcd, certificats, mises à jour)</li>', 1)
s = s.replace('<li>Gérer configuration et secrets ; isoler par namespace, RBAC et NetworkPolicy</li>',
              '<li>Gérer configuration et secrets ; isoler par namespace, RBAC et NetworkPolicy</li><li>Utiliser init containers, sidecars natifs, Downward API, jetons projetés, stratégies de mise à jour et Jobs avancés ; répondre aux vingt questions d\'entretien</li>', 1)
s = s.replace('<li>describe (événements) puis logs --previous : les deux premiers réflexes devant un Pod malade.</li>',
              '<li>describe (événements) puis logs --previous : les deux premiers réflexes devant un Pod malade ; puis Ingress → Service → EndpointSlices → Pod → nœud, sans jamais redémarrer d\'abord.</li><li>etcd se sauvegarde, les certificats expirent, le cluster se met à jour une mineure à la fois : c\'est le programme de la CKA.</li>', 1)
s = s.replace('<li>Un Secret n\'est pas secret : chiffrement etcd, RBAC, et External Secrets plutôt que Git.</li>',
              '<li>Un Secret n\'est pas secret : chiffrement etcd, RBAC, et External Secrets plutôt que Git.</li><li>Init containers pour préparer, sidecars natifs pour accompagner, Downward API et jetons projetés pour l\'identité ; jamais de BestEffort en production.</li>', 1)
s = add_rev(s, '<li>Deployment, ReplicaSet, Pod : relations et responsabilités.</li>',
            '<li>Pour chacun des treize symptômes du tableau 25.5 : où regarder et deux causes.</li><li>Sauvegarder et restaurer etcd ; renouveler les certificats ; mettre à jour un cluster kubeadm ; drainer un nœud.</li>')
s = add_rev(s, '<li>NetworkPolicy default-deny : ce qu\'il faut rouvrir (DNS !) et quel CNI l\'applique.</li>',
            '<li>Init container contre sidecar natif ; Downward API ; jeton de ServiceAccount projeté ; classes QoS.</li><li>Les vingt questions de la section 26.8, en 45 secondes chacune.</li>')
p.write_text(s); print('niveau 5 :', re.findall(r'<h3>(2[56]\.\d) ', s))
