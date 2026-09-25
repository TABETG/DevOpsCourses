import re, pathlib

p = pathlib.Path('/mnt/user-data/outputs/devops-08-sre-et-architecture.html')
s = p.read_text()
assert '43.2 Le quotidien' not in s, 'déjà fait'

NEW = r'''<h3>43.1 Le modèle SRE<span class="badge tag-coeur">Par cœur</span></h3>
<p>Le Site Reliability Engineering (Google, 2003, formalisé dans le livre de 2016) est une implémentation du DevOps qui traite l'exploitation comme un problème d'ingénierie logicielle : des ingénieurs qui écrivent du code pour faire tourner les systèmes, avec des objectifs mesurés et un budget explicite pour l'échec.</p>
<div class="tablewrap"><table>
<tr><th>Principe</th><th>Ce qu'il signifie</th><th>Où tu l'as vu</th></tr>
<tr><td>SLO et budget d'erreur</td><td>La fiabilité est un objectif chiffré, négocié avec le produit, ni plus ni moins ; le budget se dépense</td><td>Chapitre 35</td></tr>
<tr><td>Toil plafonné à 50 %</td><td>Le travail manuel, répétitif, sans valeur durable est mesuré ; au-delà de la moitié du temps, on automatise ou on rend le service à l'équipe de développement</td><td>Cette section</td></tr>
<tr><td>Post-mortems sans blâme</td><td>Chaque incident significatif produit des actions suivies ; on améliore le système, pas les coupables</td><td>Chapitre 36</td></tr>
<tr><td>Ingénierie de release</td><td>Déploiements progressifs, reproductibles, réversibles ; la livraison est un système, pas un rituel</td><td>Niveaux 2 et 5</td></tr>
<tr><td>Surveillance par symptômes</td><td>Alerter sur ce que l'utilisateur subit ; les causes vont en tickets</td><td>Chapitre 35</td></tr>
<tr><td>Planification de capacité</td><td>Prévoir la demande et la provisionner avant qu'elle n'arrive, avec des tests de charge</td><td>Chapitre 45</td></tr>
<tr><td>Simplicité</td><td>Chaque composant ajouté est une source de pannes ; retirer vaut souvent mieux qu'ajouter</td><td>Partout</td></tr>
</table></div>
<ul>
<li><strong>Le toil, concrètement</strong> : redémarrer un service à la main, appliquer un patch serveur par serveur, agrandir un disque sur ticket, créer un compte, copier une base pour un environnement de test, répondre à la même question sur Slack. Test : est-ce manuel, répétitif, automatisable, sans jugement, et sans valeur qui reste une fois fait ? Le mesurer (tickets, temps déclaré par semaine) est la première étape ; le réduire, un objectif trimestriel.</li>
<li><strong>Revue de lancement (Production Readiness Review)</strong> : avant qu'un service ne soit pris en charge, une checklist : SLO définis, observabilité, runbooks, capacité estimée, dépendances connues, plan de rollback, sécurité validée, astreinte identifiée, sauvegardes testées. Sans revue, pas de support SRE : c'est le levier qui rend les équipes produit responsables.</li>
<li><strong>Modèles d'organisation</strong> : SRE centralisée (une équipe pour plusieurs services, cohérence, risque de goulot), SRE intégrée (un ou deux SRE dans chaque équipe produit, proche du terrain, risque de dilution), équipe plateforme (chapitre 48 ; la SRE construit l'outillage que les équipes consomment). La plupart des organisations combinent : une équipe plateforme et fiabilité, des correspondants dans les équipes.</li>
<li><strong>Le contrat</strong> : la SRE prend en charge un service si celui-ci respecte la revue de lancement et la politique de budget d'erreur ; elle peut le rendre si le toil ou les incidents dépassent ce qui est soutenable. À l'inverse, elle s'engage sur l'astreinte, les SLO et l'amélioration continue. Ce contrat écrit évite l'exploitation subie.</li>
</ul>

<h3>43.2 Le quotidien d'un Tech Lead SRE<span class="badge tag-coeur">Par cœur</span></h3>
<p>Le Tech Lead SRE est responsable de la fiabilité d'un périmètre (une plateforme, un domaine de services) et de l'équipe qui l'assure. Il ne fait pas tout lui-même : il décide, arbitre, mesure, et rend les autres capables. C'est le rôle que visent tes missions, et celui qu'on te demandera de décrire en entretien.</p>
<div class="tablewrap"><table>
<tr><th>Responsabilité</th><th>Concrètement</th><th>Livrable</th></tr>
<tr><td>Porter les SLO</td><td>Définir les SLI avec le produit, fixer et réviser les SLO, publier le budget d'erreur, faire appliquer la politique (gel des changements quand le budget est épuisé)</td><td>Document SLO par service, politique de budget d'erreur signée</td></tr>
<tr><td>Arbitrer fiabilité contre fonctionnalités</td><td>Négocier chaque trimestre la part du temps consacrée à la fiabilité ; refuser un lancement qui échoue à la revue de lancement ; dire non avec des chiffres</td><td>Feuille de route fiabilité trimestrielle</td></tr>
<tr><td>Réduire le toil</td><td>Inventorier, mesurer, prioriser l'automatisation ; rendre à l'équipe de développement ce qui génère du toil structurel</td><td>Registre du toil, objectif trimestriel (par exemple moins de 30 %)</td></tr>
<tr><td>Tenir l'astreinte soutenable</td><td>Rotation, charge (moins de deux pages par semaine et par personne), qualité des alertes, runbooks, passation, compensation ; supprimer les alertes sans action</td><td>Manuel d'astreinte, revue mensuelle des alertes</td></tr>
<tr><td>Commander les incidents majeurs</td><td>Tenir ou déléguer le rôle de commandant, garantir la communication, exiger le post-mortem et la fermeture des actions</td><td>Post-mortems publiés, actions suivies dans le backlog</td></tr>
<tr><td>Revoir l'architecture pour la fiabilité</td><td>Participer aux revues (RFC, ADR) avec la question « comment ça tombe, et comment on s'en aperçoit ? » ; exiger timeouts, idempotence, dégradation, tests de charge</td><td>Avis écrit sur chaque RFC, checklist de revue de lancement</td></tr>
<tr><td>Capacité et coût</td><td>Prévoir la charge, dimensionner, suivre le coût par unité ; le FinOps est de la fiabilité économique</td><td>Plan de capacité annuel, revue de coût mensuelle</td></tr>
<tr><td>Reprise d'activité</td><td>RTO/RPO définis, sauvegardes testées, PRA exécuté au moins une fois par an, game days trimestriels</td><td>PRA, rapports de test, calendrier de chaos</td></tr>
<tr><td>Faire grandir l'équipe</td><td>Binômage, shadowing d'astreinte, dojos, security champions, revues de code d'automatisation ; recruter sur la capacité à écrire du code d'exploitation</td><td>Plan de montée en compétence, grille de recrutement</td></tr>
<tr><td>Rendre compte</td><td>Un tableau de bord et une page par mois pour la direction : SLO tenus, budget, incidents, toil, coût, risques, décisions à prendre</td><td>Rapport mensuel de fiabilité</td></tr>
</table></div>

<h4>Les rituels qui structurent la semaine</h4>
<ul>
<li><strong>Quotidien</strong> (15 min) : état des SLO, alertes de la nuit, incidents ouverts, changements risqués du jour.</li>
<li><strong>Hebdomadaire — revue de fiabilité</strong> (45 min) : budgets d'erreur consommés, incidents et post-mortems de la semaine, actions en retard, alertes bruyantes à supprimer, toil de la semaine, passation d'astreinte.</li>
<li><strong>Hebdomadaire — revue des changements</strong> : les déploiements et migrations à risque de la semaine suivante, avec fenêtre et plan de retour.</li>
<li><strong>Mensuel</strong> : revue des SLO avec le produit, revue de coût, rapport à la direction, revue des accès (conformité).</li>
<li><strong>Trimestriel</strong> : revues de lancement des nouveaux services, feuille de route fiabilité, game day ou test de PRA, enquête de charge de l'astreinte.</li>
</ul>

<h4>Une semaine type</h4>
<div class="tablewrap"><table>
<tr><th>Jour</th><th>Matin</th><th>Après-midi</th></tr>
<tr><td>Lundi</td><td>Point quotidien ; lecture des alertes du week-end ; passation d'astreinte</td><td>Revue de fiabilité hebdomadaire ; priorisation des actions de post-mortem</td></tr>
<tr><td>Mardi</td><td>Revue d'une RFC (nouveau service de notifications) : questions de résilience, SLO proposés</td><td>Binômage sur l'automatisation d'un runbook (toil : redémarrage manuel)</td></tr>
<tr><td>Mercredi</td><td>Revue des changements de la semaine suivante ; validation d'une migration de schéma</td><td>Analyse de capacité : projection du trafic à 6 mois, demande de quotas</td></tr>
<tr><td>Jeudi</td><td>Incident SEV2 : commandement, puis délégation ; communication</td><td>Rédaction du post-mortem avec l'équipe ; actions créées</td></tr>
<tr><td>Vendredi</td><td>Revue de coût mensuelle ; préparation du rapport de fiabilité</td><td>Dojo d'équipe (chaos engineering sur staging) ; pas de déploiement risqué le vendredi après-midi</td></tr>
</table></div>
<p>Répartition visée : un tiers en ingénierie (automatisation, architecture), un tiers en exploitation (incidents, revues, astreinte), un tiers en organisation (rituels, coaching, direction). Si l'exploitation dépasse la moitié, le toil ou les incidents mangent l'amélioration : c'est le signal d'alarme du rôle.</p>

<h4>Les décisions qu'il arbitre</h4>
<ul>
<li>« Le budget d'erreur est épuisé, le produit veut quand même livrer vendredi. » → La politique s'applique : livraison reportée, ou acceptée avec des mesures compensatoires écrites (canary, fenêtre, astreinte renforcée) et l'accord du sponsor. Jamais un oui tacite.</li>
<li>« Cette alerte réveille l'astreinte trois fois par semaine sans action. » → Supprimée ou rétrogradée en ticket dès la revue hebdomadaire, sans attendre.</li>
<li>« Ce service demande un support SRE mais n'a ni SLO ni runbook. » → Refus de prise en charge, checklist de revue de lancement fournie, accompagnement proposé.</li>
<li>« Multi-région ou pas ? » → Pas avant que le RTO/RPO ne soit chiffré par le métier et que le multi-AZ ne soit prouvé par un test.</li>
<li>« On automatise ou on embauche ? » → Le registre du toil répond : si 40 % du temps est du toil, embaucher ajoute du toil.</li>
<li>« Qui est responsable de la fiabilité de ce microservice ? » → L'équipe qui l'a écrit ; la SRE fournit la plateforme, les standards et l'aide, pas la responsabilité.</li>
</ul>

<h4>Les métriques qu'il suit chaque semaine</h4>
<p>SLO tenus et budget restant par service ; nombre d'incidents par sévérité et MTTD/MTTA/MTTR ; pages par personne et par semaine, part d'alertes sans action ; actions de post-mortem ouvertes de plus de 30 jours ; part de toil déclarée ; métriques DORA du périmètre ; coût par unité ; date du dernier test de restauration et de PRA ; services sans revue de lancement.</p>

<h4>Les 30 premiers jours en mission</h4>
<ol>
<li><strong>Semaine 1 — écouter et mesurer</strong> : entretiens (équipe, développeurs, produit, direction), lecture des six derniers mois d'incidents et d'alertes, inventaire des services et de leurs propriétaires, état des sauvegardes et des accès. Livrable : un état des lieux d'une page avec les trois risques majeurs.</li>
<li><strong>Semaine 2 — arrêter l'hémorragie</strong> : supprimer les alertes sans action, mettre un runbook sur les cinq alertes les plus fréquentes, vérifier qu'une restauration fonctionne, sécuriser l'accès d'urgence. Livrable : astreinte allégée, preuve de restauration.</li>
<li><strong>Semaine 3 — poser le cadre</strong> : SLO sur les deux services les plus critiques, politique de budget d'erreur proposée au produit, modèle de post-mortem et première revue hebdomadaire de fiabilité. Livrable : documents SLO, premier rapport hebdomadaire.</li>
<li><strong>Semaine 4 — la feuille de route</strong> : registre du toil, plan de réduction trimestriel, checklist de revue de lancement, calendrier des game days et du test de PRA, rapport mensuel à la direction avec trois décisions à prendre. Livrable : feuille de route fiabilité à 90 jours.</li>
</ol>

<div class="entretien"><strong>En entretien</strong> — « Que fait un Tech Lead SRE au quotidien ? » Réponse en trois blocs : porter les SLO et arbitrer avec le produit (budget d'erreur) ; rendre l'exploitation soutenable (toil mesuré et automatisé, astreinte sous deux pages par semaine, post-mortems fermés) ; concevoir pour la panne (revues d'architecture, capacité, PRA testé). Puis les rituels (revue de fiabilité hebdomadaire, rapport mensuel) et ton plan de 30 jours. Ton passé de Tech Lead et de Scrum Master rend crédible la partie arbitrage et rituels : appuie dessus.</div>

<h3>43.3 Patrons de résilience<span class="badge tag-coeur">Par cœur</span></h3>'''

# remplacer 43.1 (jusqu'au titre 43.2 Patrons) par le nouveau bloc
start = s.index('<h3>43.1 SRE : le reste du modèle')
m = re.search(r'<h3>43\.2 Patrons de résilience<span class="badge[^<]*</span></h3>', s)
assert m and m.start() > start
s = s[:start] + NEW + s[m.end():]
# renuméroter 43.3 Chaos → 43.4
s = s.replace('<h3>43.3 Chaos engineering', '<h3>43.4 Chaos engineering', 1)

# objectifs, résumé
s = s.replace('<li>Appliquer les principes SRE au-delà des SLO : toil, automatisation, revue de lancement</li>',
              '<li>Expliquer le modèle SRE complet : principes, toil, revue de lancement, modèles d\'organisation, contrat de prise en charge</li><li>Décrire le rôle du Tech Lead SRE : responsabilités, rituels, livrables, décisions, plan des 30 premiers jours</li>', 1)
s = s.replace('<li>Toil, revue de lancement, politique de budget d\'erreur : définitions et usage.</li>',
              '<li>SRE : la fiabilité comme objectif chiffré, le toil plafonné à 50 %, la revue de lancement comme contrat.</li><li>Tech Lead SRE : porter les SLO, arbitrer avec le produit, rendre l\'astreinte soutenable, concevoir pour la panne, rendre compte ; un tiers ingénierie, un tiers exploitation, un tiers organisation.</li>', 1)

# exercices supplémentaires avant le TP 43
EXOS = r'''<div class="exo"><span class="tag">Exercice 43.3</span>
<p>Tu arrives comme Tech Lead SRE. L'astreinte reçoit 25 pages par semaine, 80 % sans action ; le produit veut livrer une refonte dans deux semaines ; aucune restauration n'a été testée depuis un an. Dans quel ordre traites-tu ces trois sujets, et pourquoi ?</p>
<details><summary>Corrigé</summary><div class="sol">1) La restauration : un risque de perte définitive prime sur tout ; un test prend une journée. 2) Les alertes : supprimer celles sans action allège l'astreinte en une semaine et rend l'équipe disponible pour le reste. 3) La refonte : elle ne se décide pas sans SLO ni budget d'erreur ; proposer une revue de lancement accélérée et un déploiement canary avec rollback, plutôt qu'un refus frontal ou un oui tacite. Le tout documenté dans l'état des lieux de la semaine 1.</div></details></div>

<div class="exo"><span class="tag">Exercice 43.4</span>
<p>L'équipe SRE passe 60 % de son temps à créer des environnements de test pour les développeurs, à la main. Deux options : embaucher un troisième SRE, ou consacrer un trimestre à l'automatisation. Argumente avec les principes SRE.</p>
<details><summary>Corrigé</summary><div class="sol">C'est du toil (manuel, répétitif, automatisable, sans valeur durable) à 60 %, au-dessus du plafond de 50 % : embaucher ajouterait une personne à faire du toil. Le principe dit d'automatiser (environnements en libre-service : template, ApplicationSet par merge request, chapitre 48) et, si l'automatisation n'est pas possible à court terme, de rendre la tâche à l'équipe de développement avec l'outillage. Le trimestre d'automatisation se justifie par le calcul : 60 % de deux personnes récupérés chaque trimestre suivant.</div></details></div>

'''
s = s.replace('<div class="tp"><span class="tag">Travail pratique 43', EXOS + '<div class="tp"><span class="tag">Travail pratique 43', 1)

# étapes de TP
old = '<li>Production Readiness Review : rédige la checklist de CrisisShield et remplis-la honnêtement à partir des niveaux précédents ; liste les manques.</li>'
new = old + ('<li>Rôle de Tech Lead SRE, en vrai : rédige pour CrisisShield le manuel d\'astreinte (rotation fictive, seuils, passation, runbooks référencés), la politique de budget d\'erreur (une page, signée par un « produit » fictif), le registre du toil (liste les tâches manuelles qu\'il te reste dans les TP précédents, avec temps estimé) et la feuille de route fiabilité à 90 jours. Tiens une revue de fiabilité hebdomadaire pendant les trois semaines suivantes du parcours, avec le compte rendu dans <code>docs/reliability/</code>.</li>'
             '<li>Rapport mensuel de fiabilité (une page) à partir des données réelles de tes TP : SLO, budget, incidents, toil, coût, trois décisions à prendre. C\'est le document que tu montreras en entretien pour illustrer le rôle.</li>')
assert old in s; s = s.replace(old, new, 1)

# révision
s = s.replace('<li>Toil, revue de lancement, politique de budget d\'erreur : définitions et usage.</li>',
              '<li>Le modèle SRE : sept principes, le toil et son plafond, la revue de lancement, les modèles d\'organisation, le contrat de prise en charge.</li><li>Tech Lead SRE : dix responsabilités avec leur livrable, les rituels, la répartition du temps, trois décisions typiques, le plan des 30 premiers jours.</li>', 1)
# accroche du niveau
s = s.replace('résilience et chaos engineering, haute disponibilité', 'modèle SRE et rôle du Tech Lead SRE, résilience et chaos engineering, haute disponibilité', 1)
p.write_text(s)
print('sections 43 :', re.findall(r'<h3>(43\.\d) ', s))

ip = pathlib.Path('/mnt/user-data/outputs/devops-parcours-complet.html'); t = ip.read_text()
t = t.replace('<p>Résilience et chaos engineering, haute disponibilité et PRA', '<p>Modèle SRE et rôle du Tech Lead SRE, résilience et chaos engineering, haute disponibilité et PRA', 1)
ip.write_text(t); print('index ok')
