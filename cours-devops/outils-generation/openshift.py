import re, pathlib, html

out = pathlib.Path('/mnt/user-data/outputs')

SEC = r'''<h3>25.7 OpenShift : ce qui change par rapport à Kubernetes<span class="badge tag-coeur">Par cœur</span></h3>
<p>OpenShift (Red Hat) est Kubernetes plus une plateforme complète et opiniâtre : système d'exploitation immuable, opérateurs pour tout, registre, build, CI/CD, GitOps, mesh, monitoring, logs, sécurité et console intégrés, avec support éditeur. C'est la distribution dominante dans les administrations, les banques et les grands comptes français ; OKD en est la version communautaire. Tout ce que tu sais de Kubernetes s'applique ; ce qui suit est ce qu'il faut savoir en plus, et ce qui te fera échouer si tu l'ignores.</p>
<div class="tablewrap"><table>
<tr><th>Sujet</th><th>Kubernetes standard</th><th>OpenShift</th></tr>
<tr><td>Nœuds</td><td>Linux au choix</td><td>Red Hat CoreOS immuable, configuré par MachineConfig, mis à jour par l'opérateur de version (OTA) ; pas de SSH pour configurer</td></tr>
<tr><td>Client</td><td><code>kubectl</code></td><td><code>oc</code> (surcouche de kubectl : login, projets, routes, builds, <code>oc adm</code>) ; <code>kubectl</code> fonctionne aussi</td></tr>
<tr><td>Isolation</td><td>Namespace</td><td>Project (namespace avec annotations, quotas et rôles par défaut) ; <code>oc new-project</code></td></tr>
<tr><td>Exposition HTTP</td><td>Ingress ou Gateway API</td><td>Route (objet historique, TLS edge / passthrough / reencrypt, sous-domaine automatique <code>*.apps.cluster</code>) ; Ingress et Gateway API supportés aussi</td></tr>
<tr><td>Sécurité des Pods</td><td>Pod Security Admission</td><td>Security Context Constraints (SCC) : <code>restricted-v2</code> par défaut, qui interdit root et impose un <strong>UID arbitraire</strong> par projet ; PSA aussi présent</td></tr>
<tr><td>Images et build</td><td>Registre externe, build en CI</td><td>Registre intégré, ImageStream (référence stable vers une image, déclencheurs), BuildConfig et Source-to-Image ; aujourd'hui remplacés par OpenShift Pipelines (Tekton) et Shipwright</td></tr>
<tr><td>Déploiement</td><td>Deployment</td><td>Deployment (DeploymentConfig est déprécié depuis 4.14 ; migrer)</td></tr>
<tr><td>Add-ons</td><td>À installer et exploiter</td><td>Opérateurs par OLM depuis OperatorHub : Pipelines (Tekton), GitOps (ArgoCD), Service Mesh (Istio), Logging (Loki), monitoring (Prometheus, Alertmanager, Grafana intégrés), Serverless (Knative), Virtualization (KubeVirt), Compliance, cert-manager, ACS (sécurité, ex StackRox), ACM (multi-clusters), Quay (registre)</td></tr>
<tr><td>Console</td><td>Aucune par défaut</td><td>Console web complète, vues administrateur et développeur, terminal web</td></tr>
<tr><td>Installation</td><td>kubeadm, kOps, managé</td><td>IPI (l'installateur crée l'infrastructure : AWS, Azure, GCP, vSphere, Nutanix, bare metal) ou UPI (tu fournis l'infrastructure) ; Assisted Installer ; managé : ROSA (AWS), ARO (Azure), OpenShift Dedicated</td></tr>
<tr><td>Mises à jour</td><td>Une mineure à la fois, à la main ou par le fournisseur</td><td>Canaux (stable, fast, eus), un clic ou <code>oc adm upgrade</code>, orchestrées par le Cluster Version Operator, nœuds redémarrés par vagues ; versions de support étendu (EUS) pour sauter une mineure</td></tr>
<tr><td>Licence</td><td>Gratuit</td><td>Abonnement par cœur (ou par socket bare metal) ; OKD gratuit sans support ; le coût se justifie par le support et l'intégration</td></tr>
</table></div>

<h4>Le piège numéro un : l'UID arbitraire</h4>
<pre><code># Sous restricted-v2, le Pod tourne avec un UID aléatoire dans la plage du projet (ex. 1000680000), groupe 0.
# Une image qui suppose un utilisateur fixe ou écrit dans un répertoire non accessible échoue : "permission denied", "unable to find user".
# Dockerfile compatible OpenShift : tout ce que l'application écrit appartient au groupe root et est accessible en écriture au groupe
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --chown=1001:0 target/app.jar app.jar
RUN mkdir -p /app/tmp &amp;&amp; chgrp -R 0 /app &amp;&amp; chmod -R g=u /app
USER 1001
ENTRYPOINT ["java", "-jar", "app.jar"]
# Ne pas mettre runAsUser dans le manifest (l'admission le refuse) ; laisser OpenShift choisir.
# Vérifier : oc get pod X -o jsonpath='{.metadata.annotations.openshift\.io/scc}'  →  restricted-v2
# Besoin de plus (port &lt; 1024, capability) : demander une SCC dédiée liée à un ServiceAccount, jamais "anyuid" partout.</code></pre>

<h4>oc au quotidien</h4>
<pre><code>oc login --web https://api.cluster:6443 ; oc whoami ; oc whoami --show-console   # connexion (OIDC), identité, URL console
oc projects ; oc project crisisshield ; oc new-project lab --display-name="Labo"       # projets
oc get all ; oc status ; oc describe pod X ; oc logs -f deploy/api ; oc rsh deploy/api  # comme kubectl, plus le résumé et le shell
oc expose svc api ; oc create route edge api --service=api --hostname=api.apps.cluster ; oc get routes   # Route TLS terminée
oc adm policy add-scc-to-user nonroot-v2 -z api -n crisisshield      # SCC pour un ServiceAccount
oc adm policy add-role-to-user edit alice -n crisisshield             # RBAC par projet
oc adm top nodes ; oc adm node-logs NOEUD -u kubelet ; oc debug node/NOEUD   # nœuds (chroot /host dans le debug)
oc adm upgrade ; oc adm upgrade --to=4.19.5 ; oc get clusterversion ; oc get co   # mise à jour, opérateurs de cluster (tous Available)
oc get mcp ; oc get machineconfig ; oc get machines -n openshift-machine-api     # pools de configuration, machines
oc adm must-gather                                    # collecte pour le support Red Hat
oc get scc ; oc get csr ; oc adm certificate approve X   # SCC, certificats des nœuds
oc process -f template.yaml -p NAME=x | oc apply -f -    # templates (historique) ; Helm et Kustomize fonctionnent aussi
oc image mirror ; oc adm release mirror                  # environnements déconnectés (fréquent dans le public)
oc get pipelinerun ; tkn pipelinerun logs -f X ; oc get applications -n openshift-gitops   # Pipelines, GitOps</code></pre>

<h4>Ce qu'un DevOps ou un Tech Lead y fait différemment</h4>
<ul>
<li><strong>Images</strong> : compatibles UID arbitraire (ci-dessus), non root, ports hauts ; base images UBI (Universal Base Image) de Red Hat quand le support l'exige ; registre Quay ou registre intégré avec ImageStreams si l'organisation les utilise.</li>
<li><strong>Livraison</strong> : OpenShift Pipelines (Tekton, chapitre 12 niche) ou une CI externe (GitLab) qui pousse l'image, puis OpenShift GitOps (ArgoCD) ; Routes gérées comme les Ingress ; le monitoring des applications par ServiceMonitor dans la pile intégrée (activer <code>enableUserWorkload</code>).</li>
<li><strong>Sécurité et conformité</strong> : SCC plutôt que PSA pour les exceptions, Compliance Operator (profils CIS, ANSSI, DISA STIG) qui produit les preuves du chapitre 42, ACS pour la posture et la détection, réseau par NetworkPolicy et OVN-Kubernetes (multi-tenant, egress IP), audit intégré.</li>
<li><strong>Exploitation</strong> : ne jamais modifier un nœud à la main (MachineConfig), suivre <code>oc get co</code> avant et après toute opération, planifier les mises à jour par canal EUS, etcd sauvegardé par <code>cluster-backup.sh</code> sur un control plane, <code>must-gather</code> pour le support, dimensionner les control planes (trois, machines dédiées).</li>
<li><strong>Multi-clusters et hybride</strong> : ACM pour gouverner des dizaines de clusters (politiques, GitOps, observabilité) ; ROSA et ARO quand l'organisation est sur AWS ou Azure ; OpenShift Virtualization pour héberger des VM à côté des conteneurs, ce qui en fait aussi une cible de sortie de VMware (chapitre 7.4).</li>
<li><strong>Coût</strong> : l'abonnement par cœur pousse à dimensionner juste (requests réalistes, autoscaling, chapitre 31) ; le support Red Hat est ce que l'organisation achète, il faut savoir l'utiliser (cas, must-gather, base de connaissances).</li>
</ul>

<h4>S'entraîner sans rien installer</h4>
<p>Le <strong>Developer Sandbox for Red Hat OpenShift</strong> est un cluster partagé gratuit (compte Red Hat, projet dédié, durée limitée et renouvelable) : suffisant pour tout ce qui est applicatif (déployer CrisisShield, Routes, SCC, Pipelines, GitOps). Pour l'administration (mises à jour, MachineConfig), il faut un vrai cluster : OpenShift Local (CRC) sur une machine de labo de 16 Go, ou un cluster de formation en mission. Certifications utiles : EX280 (administrateur OpenShift), EX288 (développeur), EX380 (automatisation et intégration) ; l'EX280 est celle que les recruteurs français reconnaissent.</p>
<div class="entretien"><strong>En entretien</strong> — « Vous connaissez OpenShift ? » Réponse en quatre temps : c'est Kubernetes plus une plateforme intégrée avec support (CoreOS, opérateurs, Pipelines, GitOps, monitoring, ACS) ; les différences concrètes que je gère : Projects, Routes, SCC et UID arbitraire, <code>oc</code>, mises à jour par canal ; les pièges : images qui supposent un UID, DeploymentConfig déprécié, modifier un nœud à la main ; et la valeur : conformité (Compliance Operator), multi-clusters (ACM), Virtualization pour sortir de VMware. Puis un exemple vécu ou le TP 25.</div>
'''
EXOS = r'''<div class="exo"><span class="tag">Exercice 25.5</span>
<p>Ton image CrisisShield, qui tourne sur kind, échoue sur OpenShift avec <code>java.io.IOException: Permission denied</code> à l'écriture d'un fichier temporaire. Diagnostic et correction sans demander de SCC.</p>
<details><summary>Corrigé</summary><div class="sol">La SCC restricted-v2 exécute le conteneur avec un UID arbitraire et le groupe 0 ; le répertoire appartient à l'utilisateur fixé dans le Dockerfile et n'est pas accessible en écriture au groupe. Correction dans le Dockerfile : <code>chgrp -R 0 /app &amp;&amp; chmod -R g=u /app</code> sur tout ce que l'application écrit, <code>USER 1001</code> sans <code>runAsUser</code> dans le manifest ; ou un volume <code>emptyDir</code> pour <code>/tmp</code>. Vérifier avec <code>oc get pod -o jsonpath='{.metadata.annotations.openshift\.io/scc}'</code>. Demander anyuid serait la mauvaise réponse : elle contourne la protection.</div></details></div>

<div class="exo"><span class="tag">Exercice 25.6</span>
<p>Après <code>oc adm upgrade</code>, la mise à jour est bloquée à 60 % depuis deux heures. Où regardes-tu, dans l'ordre ?</p>
<details><summary>Corrigé</summary><div class="sol"><code>oc get clusterversion -o yaml</code> (conditions et message) ; <code>oc get co</code> pour trouver l'opérateur de cluster en Degraded ou Progressing et <code>oc describe co X</code> ; <code>oc get mcp</code> pour un pool de machines bloqué (un nœud qui ne se draine pas à cause d'un PDB ou d'un Pod sans contrôleur : <code>oc get nodes</code>, <code>oc describe node</code>) ; les alertes de la console ; puis <code>must-gather</code> et un cas de support si nécessaire. Ne jamais redémarrer un nœud à la main pendant une mise à jour.</div></details></div>

'''
TP = ('<li>OpenShift : crée un compte sur le Developer Sandbox for Red Hat OpenShift, connecte-toi avec <code>oc login --web</code> depuis ton conteneur outillé (installe <code>oc</code> dedans), déploie CrisisShield avec les manifests du TP 26 adaptés (Deployment, Route edge, ServiceMonitor si disponible), corrige l\'image pour la SCC restricted-v2 (exercice 25.5) et prouve-le par l\'annotation SCC du Pod ; ajoute un PipelineRun Tekton minimal et une Application OpenShift GitOps si l\'opérateur est proposé dans le sandbox ; documente les différences rencontrées avec kind dans <code>docs/openshift.md</code>.</li>')

p = out/'devops-niveau-5-kubernetes.html'; s = p.read_text()
assert '25.7 OpenShift' not in s
key = 'Pour sortir du lot — kwok'; i = s.index(key); j = s.rfind('<div class="niche">', 0, i)
s = s[:j] + SEC + s[j:]
s = s.replace('<div class="tp"><span class="tag">Travail pratique 25', EXOS + '<div class="tp"><span class="tag">Travail pratique 25', 1)
i = s.index('<div class="tp"><span class="tag">Travail pratique 25'); j = s.index('</ol>', i); s = s[:j] + TP + s[j:]
s = s.replace('<li>Diagnostiquer méthodiquement tout état de Pod, de Service ou de nœud, et administrer le cluster (etcd, certificats, mises à jour)</li>',
              '<li>Diagnostiquer méthodiquement tout état de Pod, de Service ou de nœud, et administrer le cluster (etcd, certificats, mises à jour)</li><li>Travailler sur OpenShift : Projects, Routes, SCC et UID arbitraire, <code>oc</code>, opérateurs Red Hat, mises à jour par canal</li>', 1)
s = s.replace('<li>etcd se sauvegarde, les certificats expirent, le cluster se met à jour une mineure à la fois : c\'est le programme de la CKA.</li>',
              '<li>etcd se sauvegarde, les certificats expirent, le cluster se met à jour une mineure à la fois : c\'est le programme de la CKA.</li><li>OpenShift = Kubernetes + plateforme intégrée avec support ; ce qui change : Projects, Routes, SCC (UID arbitraire), oc, opérateurs, mises à jour par canal.</li>', 1)
s = s.replace('<li>Sauvegarder et restaurer etcd ; renouveler les certificats ; mettre à jour un cluster kubeadm ; drainer un nœud.</li>',
              '<li>Sauvegarder et restaurer etcd ; renouveler les certificats ; mettre à jour un cluster kubeadm ; drainer un nœud.</li><li>OpenShift : les onze différences du tableau 25.7, le Dockerfile compatible UID arbitraire, dix commandes <code>oc</code>, la méthode devant une mise à jour bloquée.</li>', 1)
s = s.replace('Architecture de Kubernetes et cluster local</h2>', 'Architecture de Kubernetes, cluster local, OpenShift</h2>', 1)
if 'Kubernetes « vanilla » ou OpenShift' not in s:
    s = s.replace('<tr><td><strong>Que ferais-tu en premier sur un cluster que tu ne connais pas ?</strong></td>',
                  '<tr><td><strong>Kubernetes « vanilla » ou OpenShift ?</strong></td><td>OpenShift quand l\'organisation veut le support, l\'intégration (Pipelines, GitOps, monitoring, ACS, Compliance) et la conformité, et accepte l\'abonnement par cœur ; Kubernetes managé ou Talos quand elle a l\'équipe plateforme et veut la liberté et le coût ; les applications se portent de l\'un à l\'autre si les images respectent l\'UID arbitraire et si l\'exposition passe par Ingress ou Gateway API.</td></tr>\n<tr><td><strong>Que ferais-tu en premier sur un cluster que tu ne connais pas ?</strong></td>', 1)
p.write_text(s); print('25 :', re.findall(r'<h3>(25\.\d) ', s))

# aide-mémoire
p = out/'devops-aide-memoire.html'; s = p.read_text()
if 'id="openshift"' not in s:
    esc = html.escape
    cmds = [("oc login --web https://api.cluster:6443 ; oc whoami --show-console","connexion et console"),("oc project ns ; oc new-project lab","projets"),("oc get all ; oc status ; oc rsh deploy/api","résumé du projet ; shell"),
            ("oc create route edge api --service=api --hostname=…","Route TLS terminée"),("oc adm policy add-scc-to-user nonroot-v2 -z api -n ns","SCC pour un ServiceAccount"),("oc get pod X -o jsonpath='{.metadata.annotations.openshift\\.io/scc}'","quelle SCC s'applique"),
            ("oc get co ; oc get clusterversion ; oc adm upgrade --to=4.19.5","santé des opérateurs ; mise à jour"),("oc get mcp ; oc debug node/N","pools de configuration ; nœud"),("oc adm must-gather","collecte pour le support"),
            ("tkn pipelinerun logs -f X ; oc get applications -n openshift-gitops","Pipelines ; GitOps"),("oc adm release mirror ; oc image mirror","cluster déconnecté")]
    bps = ["Images compatibles UID arbitraire (groupe 0, g=u), non root, ports hauts ; jamais anyuid pour contourner.",
           "Deployment (pas DeploymentConfig), Ingress ou Gateway API quand la portabilité compte, Routes sinon ; ServiceMonitor dans la pile intégrée.",
           "Ne jamais toucher un nœud à la main : MachineConfig ; oc get co avant et après toute opération ; mises à jour par canal EUS planifiées.",
           "Compliance Operator et ACS pour produire les preuves ; NetworkPolicy et egress IP par OVN ; SCC dédiées liées à un ServiceAccount.",
           "S'entraîner sur le Developer Sandbox ; EX280 pour la crédibilité en France."]
    art = ('<article id="openshift"><div class="chaphead"><span class="chapnum">Niveau 5, chapitre 25</span></div><h2>OpenShift (oc)</h2>'
           '<div class="tablewrap"><table class="cmd"><tr><th>Commande</th><th>Ce qu\'elle fait</th></tr>' + ''.join(f'<tr><td>{esc(c)}</td><td>{esc(d)}</td></tr>' for c,d in cmds) + '</table></div>'
           '<div class="bp"><strong>Bonnes pratiques</strong><ol>' + ''.join(f'<li>{esc(b)}</li>' for b in bps) + '</ol></div></article>\n')
    s = s.replace('<article id="helm">', art + '<article id="helm">', 1)
    s = s.replace('<a href="#helm">Helm et Kustomize</a>', '<a href="#openshift">OpenShift</a><a href="#helm">Helm et Kustomize</a>', 1)
    p.write_text(s); print('aide-mémoire : OpenShift ajouté')

# carte des compétences
p = out/'devops-parcours-complet.html'; s = p.read_text()
if 'OpenShift' not in s:
    s = s.replace('<tr><td><strong>Kubernetes</strong></td><td>Niveau 5 entier : <a href="devops-niveau-5-kubernetes.html#c25">architecture, kubectl expert, administration (25)</a>',
                  '<tr><td><strong>Kubernetes et OpenShift</strong></td><td>Niveau 5 entier : <a href="devops-niveau-5-kubernetes.html#c25">architecture, kubectl expert, administration, OpenShift (25)</a>', 1)
    s = s.replace('<p>Architecture, cluster kind local, objets fondamentaux', '<p>Architecture, cluster kind local, OpenShift, objets fondamentaux', 1)
    p.write_text(s); print('carte ok')

# fiches entretien : régénérer (nouvel encadré 25.7 et question 26.8)
src = pathlib.Path('/home/claude/interview.py').read_text()
gen = src.split("# ---------------- page de révision « Entretien » ----------------")[1].split("# lien depuis la page d'accueil")[0]
exec(gen, {'re':re, 'pathlib':pathlib, 'html':html, 'out':out})
