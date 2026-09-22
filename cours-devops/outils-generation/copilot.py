import re, pathlib, html

p = pathlib.Path('/mnt/user-data/outputs/devops-niveau-9-expert-leadership.html')
s = p.read_text()
assert '54.5 GitHub Copilot' not in s, 'déjà fait'

NEW = r'''<h3>54.5 GitHub Copilot pour le développeur : installation, configuration, usage<span class="badge tag-coeur">Par cœur</span></h3>
<p>Copilot est l'assistant de code le plus déployé en entreprise, et celui qu'on te demandera de déployer, d'administrer et de former. Ce qu'il faut savoir en septembre 2026 ; les détails de facturation et de modèles évoluent tous les trimestres, vérifie la page officielle avant une mission.</p>
<div class="tablewrap"><table>
<tr><th>Offre</th><th>Pour qui</th><th>Ce qui change</th></tr>
<tr><td>Free, Pro, Pro+, Max</td><td>Individuels</td><td>Sans administration ; hors SSO et hors politiques d'entreprise : à interdire sur du code professionnel</td></tr>
<tr><td>Business (19 $ par utilisateur et par mois)</td><td>Organisations</td><td>Politiques d'administration, gestion des sièges, exclusions de contenu, données non conservées pour l'entraînement, indemnisation propriété intellectuelle</td></tr>
<tr><td>Enterprise (39 $ par utilisateur et par mois, exige GitHub Enterprise Cloud)</td><td>Grandes organisations</td><td>Tout Business, plus SSO SAML, journaux d'audit, bases de connaissance sur les dépôts, politiques au niveau entreprise qui s'imposent aux organisations, suivi d'usage avancé</td></tr>
</table></div>
<p><strong>Facturation depuis le 1er juin 2026</strong> : usage à la consommation. Chaque siège inclut une dotation mensuelle de <em>GitHub AI Credits</em> (1 crédit = 0,01 $ ; 19 $ inclus pour Business, 39 $ pour Enterprise), décomptés selon les tokens consommés et le modèle choisi. Les complétions de code et les suggestions d'édition restent illimitées ; le chat, le mode agent, la revue de code, le CLI et l'agent cloud consomment des crédits. L'administrateur fixe les plafonds et décide si le dépassement payant est autorisé ; sinon, Copilot se met en pause jusqu'au mois suivant, avec des alertes à 75, 90 et 100 % du budget.</p>

<h4>Installation et configuration (poste développeur)</h4>
<ul>
<li><strong>IDE</strong> : extension « GitHub Copilot » et « GitHub Copilot Chat » dans VS Code, plugin dans IntelliJ et les IDE JetBrains, support Visual Studio, Neovim, Xcode, Eclipse ; connexion avec le compte GitHub rattaché à l'organisation (SSO obligatoire en Enterprise). Vérifier que le siège est attribué : icône Copilot active en bas de l'IDE.</li>
<li><strong>Copilot CLI</strong> et Copilot sur github.com (chat sur un dépôt, une PR, une issue) ; l'agent cloud qui prend une issue, ouvre une branche et propose une pull request ; la revue de code automatique sur les PR.</li>
<li><strong>Configuration du dépôt</strong> : un fichier <code>.github/copilot-instructions.md</code> donne le contexte permanent (stack, conventions, ce qu'il ne faut jamais faire) ; des fichiers de prompts réutilisables (<code>.github/prompts/*.prompt.md</code>) pour les tâches récurrentes ; des instructions par chemin (<code>.github/instructions/*.instructions.md</code> avec <code>applyTo</code>) ; des agents personnalisés et des serveurs MCP déclarés pour donner accès aux outils internes (chapitre 54.1). Tout cela est versionné, revu, et c'est ce qui fait la différence entre un Copilot utile et un Copilot bavard.</li>
<li><strong>Réglages personnels</strong> : modèle par défaut (les modèles disponibles dépendent des politiques de l'organisation), complétions activées par langage, télémétrie selon la politique, raccourcis.</li>
</ul>
<pre><code># .github/copilot-instructions.md — exemple pour CrisisShield
Projet : plateforme de gestion de crise. Backend Spring Boot 3 / Java 21, frontend React 18 + TypeScript, PostgreSQL 16, Kafka, Keycloak.
Conventions : architecture hexagonale, records Java pour les DTO, tests JUnit 5 + Testcontainers (jamais H2), Conventional Commits en français.
Interdits : jamais de secret ni d'URL de prod dans le code ; jamais de requête SQL concaténée ; jamais de désactivation CSRF ou de CORS en * ; pas de dépendance non présente dans le pom.xml sans le signaler.
Sécurité : toute entrée utilisateur est validée ; les logs ne contiennent aucune donnée personnelle ; les endpoints exigent une autorisation par objet (organisation).
Quand tu proposes du code : explique les choix, cite les fichiers touchés, propose les tests correspondants.</code></pre>

<h4>Copilot Chat, génération, refactoring, tests</h4>
<div class="tablewrap"><table>
<tr><th>Usage</th><th>Comment</th><th>Ce qui marche, ce qui ne marche pas</th></tr>
<tr><td>Complétion</td><td>Écrire un commentaire ou une signature de méthode, accepter par morceaux (Tab, Ctrl+→)</td><td>Excellent pour le code répétitif et les tests ; à relire ligne par ligne sur la logique métier et la sécurité</td></tr>
<tr><td>Chat dans l'IDE</td><td>Commandes <code>/explain</code>, <code>/fix</code>, <code>/tests</code>, <code>/doc</code> ; références <code>#file</code>, <code>#selection</code>, <code>@workspace</code>, <code>@terminal</code></td><td>La qualité dépend du contexte fourni : sélection précise, fichiers pertinents, instructions du dépôt</td></tr>
<tr><td>Mode agent</td><td>Une tâche en langage naturel ; l'agent lit, modifie plusieurs fichiers, lance les tests et itère ; tu valides chaque modification</td><td>Bon pour une fonctionnalité bien cadrée avec tests ; dangereux sans tests ni revue ; consomme des crédits</td></tr>
<tr><td>Refactoring</td><td>Sélectionner, demander une transformation précise (extraire, renommer, migrer une API), exiger les tests avant et après</td><td>Vérifier le comportement avec la suite de tests, pas avec l'œil</td></tr>
<tr><td>Tests</td><td><code>/tests</code> sur une classe ; demander les cas limites et les cas d'erreur explicitement</td><td>Copilot génère des tests qui passent, pas forcément des tests qui vérifient : relire les assertions</td></tr>
<tr><td>Revue de code</td><td>Revue automatique de la PR, avec les instructions du dépôt</td><td>Trouve le répétitif (nommage, cas oubliés) ; ne remplace pas la revue humaine sur le design et la sécurité</td></tr>
<tr><td>Agent cloud</td><td>Assigner une issue à Copilot ; il ouvre une PR à revoir</td><td>Pour les tâches bornées (dépendance, correction simple, documentation) ; la PR passe par le pipeline et la revue comme toute autre</td></tr>
</table></div>

<h4>Bonnes pratiques d'équipe</h4>
<ol>
<li>Copilot propose, la revue et le pipeline disposent : tout code généré passe par la même merge request, les mêmes tests, les mêmes analyses de sécurité (niveau 7). C'est la seule garantie qui tienne.</li>
<li>Le contexte dans le dépôt (instructions, prompts, exemples) vaut plus que le talent de chacun à écrire des prompts ; il se maintient comme du code.</li>
<li>Ne jamais accepter une dépendance ou une API que l'on ne connaît pas sans la vérifier : les hallucinations de bibliothèques (« slopsquatting ») sont un vecteur d'attaque réel.</li>
<li>Petites tâches, tests d'abord, relire chaque diff ; le mode agent sur une base sans tests produit de la dette rapidement.</li>
<li>Mesurer (section 54.7) et partager les prompts qui marchent dans un dépôt d'équipe.</li>
</ol>

<h3>54.6 GitHub Copilot Enterprise : administrer, habiliter, gouverner<span class="badge tag-coeur">Par cœur</span></h3>
<p>C'est le rôle qu'on confie au DevSecOps ou au Tech Lead : rendre Copilot disponible, sûr, et mesuré. Tout se règle dans les paramètres de l'entreprise et des organisations GitHub ; les politiques d'entreprise s'imposent aux organisations, qui peuvent restreindre davantage, jamais élargir.</p>
<div class="tablewrap"><table>
<tr><th>Domaine</th><th>Ce que l'administrateur règle</th><th>Recommandation</th></tr>
<tr><td>Licences et sièges</td><td>Attribution par utilisateur, par équipe ou à toute l'organisation ; retrait automatique des inactifs ; sièges Business ou Enterprise</td><td>Attribuer par équipe GitHub liée à l'annuaire (SSO/SCIM), revue mensuelle des sièges inactifs (rapport d'usage), pas de compte personnel sur du code professionnel</td></tr>
<tr><td>Politiques de fonctionnalités</td><td>Chat dans l'IDE, Copilot sur github.com, CLI, mode agent, agent cloud, revue de code, extensions, modèles autorisés, aperçus techniques</td><td>Activer par vagues (IDE d'abord, agents ensuite) ; liste blanche de modèles validés par la sécurité ; aperçus désactivés en prod</td></tr>
<tr><td>Confidentialité et propriété intellectuelle</td><td>Filtre des suggestions correspondant à du code public (avec ou sans indication de licence), exclusions de contenu (fichiers et dépôts jamais envoyés au modèle), conservation des données</td><td>Filtre de correspondance activé ; exclure secrets, dépôts sensibles, données de clients ; documenter que les prompts et complétions Business/Enterprise ne servent pas à l'entraînement et que l'indemnisation PI s'applique sous conditions</td></tr>
<tr><td>Consommation et budget</td><td>Plafond mensuel d'AI Credits, autorisation ou non du dépassement payant, alertes à 75, 90, 100 %, budgets par organisation ou centre de coût</td><td>Dépassement interdit par défaut, budgets par équipe, revue mensuelle avec le FinOps (chapitre 23) : le modèle choisi pilote la dépense</td></tr>
<tr><td>Suivi d'usage</td><td>Tableau de bord d'usage, API de métriques (utilisateurs actifs, suggestions acceptées, par langage, par IDE, par modèle, par équipe), journal d'audit des changements de politique</td><td>Exporter chaque mois vers ton outil de mesure (chapitre 52), croiser avec DORA et la satisfaction</td></tr>
<tr><td>Bases de connaissance (Enterprise)</td><td>Ensembles de dépôts de documentation que le chat peut interroger</td><td>Une base par domaine (plateforme, sécurité, conventions), alimentée par les <code>docs/</code> et ADR du niveau 9</td></tr>
<tr><td>Identité</td><td>SSO SAML, SCIM, tokens et accès des agents et comptes de service</td><td>Les agents consomment des crédits et accèdent aux dépôts : mêmes règles d'habilitation que les humains, revue trimestrielle</td></tr>
</table></div>
<p><strong>Déploiement type en entreprise</strong> : cadrage (cas d'usage, périmètre de code exclu, avis juridique et sécurité) ; pilote de 20 à 50 développeurs volontaires pendant 8 semaines avec mesure avant/après ; politiques et instructions de dépôt prêtes avant l'ouverture ; formation d'une heure par équipe (prompts, contexte, revue) ; ouverture par vagues avec budget ; revue mensuelle usage, coût, satisfaction, incidents. La sécurité et le juridique sont dans la boucle dès le cadrage, pas au moment du déploiement.</p>
<div class="entretien"><strong>En entretien</strong> — « Vous déployez Copilot Enterprise chez nous, par où commencez-vous ? » Cadrage avec sécurité et juridique (exclusions, filtre de code public, conservation des données), politiques d'entreprise (fonctionnalités et modèles autorisés, dépassement interdit), sièges par équipe via SSO, instructions de dépôt versionnées, pilote mesuré, formation courte, ouverture par vagues, revue mensuelle usage et coût. Et la phrase clé : « Copilot passe par la même merge request et le même pipeline que tout le monde ».</div>

<h3>54.7 IA générative pour développeurs : prompts, contexte, sécurité, confidentialité, limites, adoption<span class="badge tag-coeur">Par cœur</span></h3>
<h4>Écrire des prompts qui donnent du code juste</h4>
<ul>
<li><strong>Le contexte d'abord</strong> : rôle et projet, fichiers concernés, contraintes (version, bibliothèques, style), exemple de ce qui existe déjà ; sans contexte, le modèle invente une convention.</li>
<li><strong>Une tâche précise et vérifiable</strong> : « ajoute un endpoint POST /incidents avec validation Bean Validation, réponse 201 et test MockMvc pour les cas nominal, invalide et non autorisé » plutôt que « fais l'API incidents ».</li>
<li><strong>Le résultat attendu</strong> : format (diff, fichier complet), ce qu'il ne faut pas toucher, les tests à fournir, l'explication des choix.</li>
<li><strong>Itérer</strong> : demander d'abord un plan ou la liste des fichiers touchés, valider, puis le code ; demander « quels cas limites ai-je oubliés ? » ; faire relire par le modèle avec un autre rôle (relecteur sécurité).</li>
<li><strong>Prompts réutilisables</strong> versionnés dans le dépôt (<code>.github/prompts/</code>) : génération de tests, revue de sécurité, migration d'API, rédaction d'ADR ; l'équipe les améliore par merge request.</li>
</ul>
<pre><code># .github/prompts/revue-securite.prompt.md
Tu es relecteur sécurité. Analyse #selection selon OWASP Top 10 et ASVS niveau 2.
Pour chaque problème : gravité, ligne, explication, correction proposée sous forme de diff.
Vérifie en particulier : validation des entrées, contrôle d'accès par objet, secrets, journalisation de données personnelles, requêtes SQL, désérialisation.
Termine par la liste des tests de sécurité à ajouter.</code></pre>

<h4>Sécurité et confidentialité du code</h4>
<div class="tablewrap"><table>
<tr><th>Risque</th><th>Réalité</th><th>Mesure</th></tr>
<tr><td>Fuite de code ou de secrets vers le fournisseur</td><td>Tout ce qui est dans le contexte part chez le fournisseur ; en Business/Enterprise il n'est pas conservé pour l'entraînement, mais il transite et peut être journalisé</td><td>Exclusions de contenu, pas de secret dans les dépôts (déjà le niveau 7), masquage à la source, outils individuels interdits, contrat et localisation des données vérifiés</td></tr>
<tr><td>Code généré vulnérable</td><td>Les modèles reproduisent les motifs fréquents, y compris les mauvais (concaténation SQL, MD5, CORS ouvert)</td><td>Analyses SAST/SCA obligatoires, instructions de dépôt avec les interdits, revue humaine, prompt de relecture sécurité</td></tr>
<tr><td>Dépendance hallucinée</td><td>Un paquet inexistant proposé peut être créé par un attaquant (slopsquatting)</td><td>Proxy de dépendances à liste d'autorisation, vérification de chaque nouvelle dépendance, SCA</td></tr>
<tr><td>Propriété intellectuelle et licences</td><td>Reproduction de code public sous licence</td><td>Filtre de correspondance avec code public, indemnisation contractuelle, revue des suggestions longues</td></tr>
<tr><td>Injection par le contexte</td><td>Un fichier, une issue ou une page lue par l'agent contient des instructions malveillantes</td><td>Agents en lecture seule par défaut, écriture par PR revue, outils minimaux, isolation (chapitre 54.4)</td></tr>
<tr><td>Confiance excessive</td><td>Le code « a l'air bon » et les tests générés passent</td><td>Relire les assertions, mutation testing (chapitre 13), pairing sur le code critique, taux d'échec des changements surveillé</td></tr>
</table></div>

<h4>Les limites, à dire aux équipes</h4>
<p>Le modèle ne connaît pas ton système (sauf ce que tu lui donnes), il ne sait pas ce qu'il ne sait pas, il est daté (versions, API dépréciées), il optimise la plausibilité et non la vérité, il est moins fiable sur le code rare, le concurrent, le cryptographique et le métier ; et son coût augmente avec le contexte. L'IA accélère l'expert et fait produire au débutant du code qu'il ne comprend pas : l'organisation doit investir dans la relecture et la formation autant que dans les licences.</p>

<h4>Mesurer l'adoption et la valeur</h4>
<div class="tablewrap"><table>
<tr><th>Niveau</th><th>Indicateurs</th><th>Source</th></tr>
<tr><td>Activation</td><td>Sièges attribués et actifs, utilisateurs actifs par semaine, par équipe et par IDE</td><td>Tableau de bord et API de métriques Copilot</td></tr>
<tr><td>Usage</td><td>Suggestions acceptées (taux et lignes), sessions de chat, tâches d'agent, PR de l'agent cloud fusionnées, crédits consommés par modèle</td><td>API de métriques, facturation</td></tr>
<tr><td>Résultat</td><td>Délai commit → production, fréquence de déploiement, taux d'échec des changements, temps de revue, bugs en production, couverture de tests (avant/après, par équipe pilote et témoin)</td><td>DORA (chapitre 52), qualité (chapitre 13)</td></tr>
<tr><td>Expérience</td><td>Satisfaction, temps gagné estimé, tâches sur lesquelles c'est utile ou nuisible</td><td>Enquête trimestrielle (SPACE)</td></tr>
<tr><td>Risque</td><td>Findings de sécurité sur du code généré, dépendances refusées, incidents liés</td><td>DefectDojo, SCA, post-mortems</td></tr>
</table></div>
<p>Le taux d'acceptation seul ne dit rien (on accepte puis on réécrit) ; la valeur se lit dans les métriques de flux et de qualité, à périmètre comparable, sur un trimestre. Un déploiement réussi montre un délai de livraison qui baisse sans que le taux d'échec ne monte, et un coût par développeur connu et accepté.</p>
'''
m = re.search(r'<div class="niche"><span class="tag"><span class="badge badge-niche">Techno de niche</span>Pour sortir du lot — Signature de modèles', s)
assert m
s = s[:m.start()] + NEW + s[m.start():]

# objectifs et résumé
s = s.replace('<li>Sécuriser les applications et agents LLM : OWASP LLM Top 10, isolation, gouvernance</li>',
              '<li>Sécuriser les applications et agents LLM : OWASP LLM Top 10, isolation, gouvernance</li><li>Installer, configurer et bien utiliser GitHub Copilot ; l\'administrer en entreprise (licences, politiques, budget, suivi) ; former les équipes à l\'IA générative (prompts, sécurité, limites, mesure)</li>', 1)
s = s.replace('<li>Passerelle LLM, evals en CI, observabilité GenAI, OWASP LLM Top 10 avec l\'injection indirecte en fil rouge.</li>',
              '<li>Passerelle LLM, evals en CI, observabilité GenAI, OWASP LLM Top 10 avec l\'injection indirecte en fil rouge.</li><li>Copilot : le contexte dans le dépôt vaut plus que les prompts ; en entreprise, politiques, exclusions, budget de crédits et suivi d\'usage ; tout code généré passe par la même merge request et le même pipeline.</li>', 1)

# exercices
EXOS = r'''<div class="exo"><span class="tag">Exercice 54.3</span>
<p>Le RSSI refuse Copilot : « notre code partira chez Microsoft ». Réponds en trois arguments vérifiables et deux mesures.</p>
<details><summary>Corrigé</summary><div class="sol">Arguments : en Business/Enterprise, prompts et complétions ne sont pas conservés pour l'entraînement (contrat, à faire figurer dans l'analyse de risque) ; les exclusions de contenu empêchent l'envoi des fichiers et dépôts désignés ; le filtre de code public et l'indemnisation couvrent le risque de licence. Mesures : liste des dépôts et chemins exclus validée par la sécurité, comptes individuels interdits (seuls les sièges d'entreprise via SSO), et le rappel que les secrets n'ont de toute façon rien à faire dans les dépôts (niveau 7). Proposer un pilote sur des dépôts non sensibles avec revue du journal d'audit.</div></details></div>

<div class="exo"><span class="tag">Exercice 54.4</span>
<p>La facture Copilot a doublé en un mois. Quelles sont les trois causes probables et les réglages qui les maîtrisent ?</p>
<details><summary>Corrigé</summary><div class="sol">Usage massif du mode agent et de l'agent cloud (consommateurs de crédits), choix de modèles premium coûteux par défaut, revue de code automatique sur toutes les PR. Réglages : plafond de crédits et dépassement interdit, liste des modèles autorisés avec un modèle standard par défaut, revue automatique limitée aux dépôts qui en ont besoin, budgets par équipe et rapport mensuel d'usage par modèle ; puis formation : petites tâches, contexte précis, pas de relance en boucle.</div></details></div>

'''
s = s.replace('<div class="tp"><span class="tag">Travail pratique 54', EXOS + '<div class="tp"><span class="tag">Travail pratique 54', 1)

# étapes de TP
old = '<li>Rédige la fiche produit et l\'architecture de la passerelle comme livrable de mission'
new = ('<li><strong>Copilot développeur</strong> : sur CrisisShield, écris <code>.github/copilot-instructions.md</code>, trois prompts réutilisables (tests, revue sécurité, ADR), une instruction par chemin pour le frontend ; fais générer par le mode agent un endpoint complet avec tests, puis passe-le dans le pipeline du niveau 7 et note ce que les analyses attrapent ; compare le même travail sans instructions de dépôt.</li>'
       '<li><strong>Copilot Enterprise</strong> (sur une organisation GitHub d\'essai, ou en dossier si tu n\'as pas de licence) : rédige la politique d\'entreprise (fonctionnalités, modèles, filtre de code public, exclusions, budget et dépassement), le processus d\'attribution des sièges par équipe SSO, un script qui interroge l\'API de métriques Copilot et alimente ton service DORA du TP 52, et le rapport mensuel usage et coût.</li>'
       '<li><strong>Formation IA générative</strong> : construis une session de deux heures pour une équipe (prompts avec contexte, sécurité et confidentialité, limites, mesure), avec un atelier pratique sur CrisisShield et un questionnaire avant/après ; c\'est un livrable vendable en mission.</li>\n' + old)
assert old in s; s = s.replace(old, new, 1)

# révision
s = s.replace('<li>LLMOps (passerelle, evals, observabilité, coût) et OWASP LLM Top 10 avec l\'injection indirecte ; AI Act.</li>',
              '<li>LLMOps (passerelle, evals, observabilité, coût) et OWASP LLM Top 10 avec l\'injection indirecte ; AI Act.</li><li>Copilot : offres et facturation aux crédits, configuration du dépôt (instructions, prompts, agents), usages qui marchent et pièges ; administration Enterprise (sièges, politiques, exclusions, budget, métriques) ; déploiement par pilote et vagues ; mesurer l\'adoption par le flux et la qualité, pas par le taux d\'acceptation.</li>', 1)
s = s.replace('IA appliquée au DevOps : AIOps, LLM dans les pipelines, sécurité des agents</h2>', 'IA appliquée au DevOps : AIOps, LLM dans les pipelines, sécurité des agents, GitHub Copilot</h2>', 1)
p.write_text(s); print('54 :', re.findall(r'<h3>(54\.\d) ', s))

ip = pathlib.Path('/mnt/user-data/outputs/devops-parcours-complet.html'); t = ip.read_text()
t = t.replace('conduite du changement, IA appliquée au DevOps. Projet final.', 'conduite du changement, IA appliquée au DevOps et GitHub Copilot (usage, Enterprise, adoption). Projet final.', 1)
ip.write_text(t); print('index ok')
