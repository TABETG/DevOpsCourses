import re, pathlib

p = pathlib.Path('/mnt/user-data/outputs/devops-niveau-8-sre-architecture.html')
s = p.read_text()
assert '43.3 SRE de plateforme' not in s, 'déjà fait'

NEW = r'''<h3>43.3 SRE de plateforme : la fiabilité comme produit<span class="badge tag-coeur">Par cœur</span></h3>
<p>« Platform SRE » ou « SRE platform engineering » recouvre deux choses qu'il faut distinguer, car on te demandera les deux :</p>
<ol>
<li><strong>La SRE de la plateforme</strong> : la plateforme interne (Kubernetes, CI, registre, ArgoCD, Vault, Keycloak, observabilité) est elle-même un service avec des utilisateurs (les équipes produit), des SLO, une astreinte, des post-mortems. Quand elle tombe, tout le monde tombe : son rayon d'impact impose des standards plus stricts qu'à n'importe quelle application.</li>
<li><strong>La plateforme de fiabilité</strong> : l'équipe SRE ne surveille pas chaque service à la main ; elle construit des capacités en libre-service que les équipes consomment, pour que la fiabilité soit le chemin par défaut (le golden path du chapitre 48, appliqué à la fiabilité).</li>
</ol>

<h4>Les SLO de la plateforme elle-même</h4>
<div class="tablewrap"><table>
<tr><th>Composant</th><th>SLI</th><th>SLO typique</th><th>Pourquoi ça compte</th></tr>
<tr><td>API Kubernetes</td><td>Disponibilité, latence p99 des requêtes</td><td>99,95 %, p99 &lt; 1 s</td><td>Sans elle, plus de déploiement ni d'autoscaling ; les applications continuent de servir</td></tr>
<tr><td>CI/CD</td><td>Taux de succès hors échec de tests, durée p95 d'un pipeline, délai d'attente d'un runner</td><td>&gt; 98 %, p95 &lt; 10 min, attente &lt; 2 min</td><td>Un pipeline lent ou capricieux détruit la fréquence de déploiement de toutes les équipes</td></tr>
<tr><td>Registre d'images</td><td>Disponibilité des pulls, latence</td><td>99,95 %</td><td>Un registre en panne empêche tout redémarrage de Pod</td></tr>
<tr><td>ArgoCD</td><td>Délai entre commit sur le dépôt de config et synchronisation</td><td>p95 &lt; 3 min</td><td>C'est le chemin de déploiement et de rollback</td></tr>
<tr><td>Vault / gestionnaire de secrets</td><td>Disponibilité, latence</td><td>99,99 %</td><td>Sans lui, les Pods ne démarrent plus (secrets dynamiques)</td></tr>
<tr><td>IdP (Keycloak)</td><td>Disponibilité des connexions, latence du jeton</td><td>99,95 %</td><td>Sans lui, plus personne ne se connecte, ni les humains ni les services</td></tr>
<tr><td>Observabilité</td><td>Délai d'ingestion des logs et métriques, disponibilité des requêtes</td><td>ingestion &lt; 60 s, 99,9 %</td><td>Un monitoring en panne est un incident invisible ; il s'héberge hors du cluster qu'il surveille</td></tr>
<tr><td>Environnements en libre-service</td><td>Délai de création d'un service ou d'une base conforme</td><td>&lt; 15 min, succès &gt; 95 %</td><td>C'est la mesure d'adoption de la plateforme</td></tr>
</table></div>
<p>Règles propres à la plateforme : changements de plateforme en canary (un cluster ou un nœud d'abord, puis la flotte), fenêtres de maintenance annoncées et gel avant les périodes critiques des équipes, dépendances circulaires interdites (la plateforme ne doit pas dépendre d'un service qu'elle héberge : l'IdP de l'astreinte, la documentation et l'outil d'incident vivent ailleurs), accès d'urgence hors plateforme, et un SLA interne publié : les équipes savent ce qu'elles peuvent attendre et où s'arrête la responsabilité de la plateforme.</p>

<h4>La plateforme de fiabilité : ce que la SRE offre en libre-service</h4>
<div class="tablewrap"><table>
<tr><th>Capacité</th><th>Ce que l'équipe produit obtient sans ticket</th><th>Outils</th><th>Vu au</th></tr>
<tr><td>SLO as code</td><td>Un fichier de quelques lignes → recording rules, alertes de burn rate, dashboard, budget d'erreur</td><td>Sloth, Pyrra, Grafana SLO</td><td>Chapitre 35</td></tr>
<tr><td>Observabilité par défaut</td><td>Logs, métriques, traces et dashboards générés à la création du service</td><td>OpenTelemetry Operator, templates Grafana, Beyla</td><td>Niveau 6</td></tr>
<tr><td>Livraison progressive</td><td>Canary et rollback automatique sur métriques, sans configuration par équipe</td><td>Argo Rollouts, Flagger, Kargo</td><td>Chapitres 15, 29</td></tr>
<tr><td>Résilience par défaut</td><td>Timeouts, retries, circuit breakers au niveau réseau ; bibliothèque applicative standard</td><td>Mesh, Resilience4j en starter interne</td><td>Chapitres 30, 43</td></tr>
<tr><td>Chaos en libre-service</td><td>Catalogue d'expériences à lancer sur staging, avec mesure des SLO</td><td>Chaos Mesh, Litmus</td><td>Chapitre 43</td></tr>
<tr><td>Sauvegarde et restauration</td><td>Chaque base créée par la plateforme est sauvegardée, testée, restaurable en libre-service</td><td>CloudNativePG, Velero, Kanister, compositions Crossplane</td><td>Chapitres 27, 44, 48</td></tr>
<tr><td>Tests de charge</td><td>Scénario k6 standard exécutable en CI contre un environnement éphémère</td><td>k6 Operator</td><td>Chapitre 45</td></tr>
<tr><td>Gestion d'incident</td><td>Déclaration en une commande, canal, rôles, chronologie, post-mortem généré</td><td>Dispatch, incident.io, Grafana OnCall</td><td>Chapitre 36</td></tr>
<tr><td>Runbooks automatisés</td><td>Les remédiations éprouvées deviennent des actions exécutables et tracées</td><td>Event-Driven Ansible, Argo Workflows, Robusta</td><td>Chapitres 17, 54</td></tr>
<tr><td>Capacité et coût</td><td>Recommandations de requests, coût et carbone par service, quotas</td><td>VPA, KRR, OpenCost, Kepler</td><td>Chapitres 23, 31</td></tr>
<tr><td>Scorecard de fiabilité</td><td>Chaque service voit son niveau de préparation à la production et ce qui lui manque</td><td>Backstage tech-insights</td><td>Chapitre 48</td></tr>
</table></div>
<pre><code># Ce que « fiabilité par défaut » veut dire pour un développeur : un fichier, tout le reste est généré
# slo.yaml à la racine du service, consommé par le template de la plateforme
service: crisisshield-api
owner: team-incidents
slos:
  - name: disponibilite
    objective: 99.9
    sli: { errors: 'http_server_requests_seconds_count{status=~"5.."}', total: 'http_server_requests_seconds_count' }
  - name: latence
    objective: 95
    sli: { good: 'http_server_requests_seconds_bucket{le="0.3"}', total: 'http_server_requests_seconds_count' }
rollout: { strategy: canary, steps: [10, 50, 100], analysis: [disponibilite, latence] }
alerts: { page: burn-rate-fast, ticket: burn-rate-slow, receiver: team-incidents }
backup: { schedule: daily, retention: 30d, restore-test: weekly }</code></pre>
<p>Résultat : le service a des SLO, des alertes justes, un dashboard, un déploiement canary analysé et des sauvegardes testées le jour de sa création, sans que l'équipe ait lu les niveaux 5 à 8. C'est la définition d'une plateforme de fiabilité réussie.</p>

<h4>Le rôle du Tech Lead SRE dans une organisation plateforme</h4>
<ul>
<li><strong>Posture produit</strong> : les équipes sont des clients ; on mesure l'adoption (part des services avec SLO, avec canary, avec sauvegarde testée), le délai de création d'un service fiable, la satisfaction, et la tendance du MTTR des équipes utilisatrices, pas seulement celle de la plateforme.</li>
<li><strong>Organisation</strong> (Team Topologies) : la SRE peut être une équipe plateforme à part entière, ou une équipe habilitante qui outille et forme (chapitre 53) ; dans les deux cas, la responsabilité de la fiabilité d'un service reste à l'équipe qui le développe, la plateforme lui en donne les moyens.</li>
<li><strong>Feuille de route</strong> : chaque capacité de la table ci-dessus est un produit avec un propriétaire, une version, une documentation et un canal de support ; on livre la capacité la plus demandée d'abord (souvent l'observabilité par défaut et les SLO as code), et on retire celles que personne n'adopte.</li>
<li><strong>Standards</strong> : la revue de lancement devient une scorecard automatique ; les politiques as code (chapitre 51) rendent les bonnes pratiques obligatoires sans revue humaine.</li>
<li><strong>Frontière</strong> : la plateforme n'exploite pas les applications ; elle exploite la plateforme et fournit les outils. Quand une équipe demande « pouvez-vous gérer notre astreinte ? », la réponse est une capacité (outil d'incident, alertes générées, formation), pas une prise en charge.</li>
</ul>

<div class="entretien"><strong>En entretien</strong> — « Quelle est la différence entre SRE et platform engineering ? » Le platform engineering construit une plateforme interne en libre-service ; la SRE garantit la fiabilité par des objectifs mesurés. Ils se rejoignent : la plateforme est un service qui a besoin de SRE (ses propres SLO, son astreinte, son canary), et la SRE passe à l'échelle en devenant une plateforme (SLO as code, observabilité par défaut, livraison progressive, incident tooling). Le Tech Lead SRE d'aujourd'hui pilote les deux : la fiabilité de la plateforme, et la fiabilité en libre-service pour les équipes.</div>

<h3>43.4 Patrons de résilience<span class="badge tag-coeur">Par cœur</span></h3>'''

m = re.search(r'<h3>43\.3 Patrons de résilience<span class="badge[^<]*</span></h3>', s)
assert m
s = s[:m.start()] + NEW + s[m.end():]
s = s.replace('<h3>43.4 Chaos engineering', '<h3>43.5 Chaos engineering', 1)

# objectifs, résumé
s = s.replace('<li>Décrire le rôle du Tech Lead SRE : responsabilités, rituels, livrables, décisions, plan des 30 premiers jours</li>',
              '<li>Décrire le rôle du Tech Lead SRE : responsabilités, rituels, livrables, décisions, plan des 30 premiers jours</li><li>Concevoir la SRE de plateforme : SLO de la plateforme elle-même et capacités de fiabilité en libre-service</li>', 1)
s = s.replace('<li>Tech Lead SRE : porter les SLO, arbitrer avec le produit, rendre l\'astreinte soutenable, concevoir pour la panne, rendre compte ; un tiers ingénierie, un tiers exploitation, un tiers organisation.</li>',
              '<li>Tech Lead SRE : porter les SLO, arbitrer avec le produit, rendre l\'astreinte soutenable, concevoir pour la panne, rendre compte ; un tiers ingénierie, un tiers exploitation, un tiers organisation.</li><li>SRE de plateforme : la plateforme a ses propres SLO et son canary ; la fiabilité devient un produit en libre-service (SLO as code, observabilité par défaut, livraison progressive, incidents outillés).</li>', 1)

# exercice
EXO = r'''<div class="exo"><span class="tag">Exercice 43.5</span>
<p>Une équipe produit demande à la SRE de « prendre en charge l'astreinte » de son nouveau service. Réponds en Tech Lead SRE d'une organisation plateforme.</p>
<details><summary>Corrigé</summary><div class="sol">La responsabilité reste à l'équipe ; la plateforme lui donne les moyens : création du service par le template (SLO as code, alertes de burn rate, dashboard, canary, sauvegardes), outil d'incident avec rôles et post-mortem générés, manuel d'astreinte type, shadowing avec un SRE pendant deux semaines, et une scorecard qui montre ce qui manque avant la mise en production. Si le service ne passe pas la revue de lancement, il n'est pas mis en production. La SRE prend l'astreinte de la plateforme, pas celle des applications.</div></details></div>

'''
s = s.replace('<div class="tp"><span class="tag">Travail pratique 43', EXO + '<div class="tp"><span class="tag">Travail pratique 43', 1)

# étape de TP
old = '<li>Rapport mensuel de fiabilité (une page)'
new = ('<li>SRE de plateforme : définis et mesure les SLO de ta plateforme kind (API Kubernetes, ArgoCD délai de synchronisation, registre, Vault, Keycloak, ingestion Loki) avec Sloth et un dashboard « santé de la plateforme » ; puis fais de la fiabilité un libre-service : le template de service du TP 48 doit lire un <code>slo.yaml</code> et générer SLO, alertes, dashboard, Rollout canary et sauvegarde. Crée un service fictif par le template et prouve qu\'il est « fiable par défaut » en moins de 15 minutes, sans toucher au cluster.</li>\n' + old)
assert old in s; s = s.replace(old, new, 1)

# révision
s = s.replace('<li>Tech Lead SRE : dix responsabilités avec leur livrable, les rituels, la répartition du temps, trois décisions typiques, le plan des 30 premiers jours.</li>',
              '<li>Tech Lead SRE : dix responsabilités avec leur livrable, les rituels, la répartition du temps, trois décisions typiques, le plan des 30 premiers jours.</li><li>SRE de plateforme : les SLO de la plateforme (huit composants), les règles propres au rayon d\'impact, les onze capacités de fiabilité en libre-service, la frontière avec les équipes produit.</li>', 1)
p.write_text(s)
print('sections 43 :', re.findall(r'<h3>(43\.\d) ', s))
