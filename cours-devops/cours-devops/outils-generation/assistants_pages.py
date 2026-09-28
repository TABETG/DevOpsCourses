"""Cours Assistants IA pour développeurs : GitHub Copilot, Claude, ChatGPT (9 chapitres). Usage : python3 assistants_pages.py <dossier>"""
import sys, runpy, pathlib
g = runpy.run_path(pathlib.Path(__file__).with_name('front_gen.py'), run_name='front'); ch, page = g['ch'], g['page']
def T(rows, head): return '<div class="tablewrap"><table><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table></div>'
EVO = "Les offres et les fonctions de ces outils évoluent vite : les principes de ce cours restent, les noms de menus et de réglages se vérifient dans la documentation de ton abonnement."

AS = [
ch("Panorama et bon usage des assistants IA", 'j',
 ["Trois familles d'outils : la complétion dans l'éditeur, la conversation (chat) et les agents qui lisent le dépôt, lancent des commandes et proposent des modifications.", "GitHub Copilot vit dans l'IDE et GitHub ; Claude se décline en conversation (claude.ai), en agent de code (Claude Code) et en API ; ChatGPT en conversation, projets, GPTs personnalisés et agent de code.", "La règle d'or : tu restes responsable de tout ce que tu livres ; l'assistant propose, tu comprends, tu testes, tu décides."],
 ["Situer complétion, conversation et agent", "Choisir l'outil selon la tâche", "Adopter les réflexes de vérification"],
 [("Trois familles d'outils", T([
    ("Complétion", "suggestions pendant la frappe", "Copilot dans l'IDE", "petit code répétitif, tests, conversions"),
    ("Conversation", "questions, explications, brouillons", "claude.ai, ChatGPT, Copilot Chat", "comprendre, concevoir, déboguer, écrire"),
    ("Agent de code", "lit le dépôt, modifie, lance les tests", "Claude Code, mode agent de Copilot, agent de code de ChatGPT", "tâches multi-fichiers, avec relecture")], ("Famille", "Ce qu'elle fait", "Exemples", "Pour quoi")), None),
  ("Ce qu'ils font bien, et moins bien", "Ils excellent sur ce qui est courant et bien documenté : syntaxe, tests, conversions, explications, premiers jets. Ils se trompent avec assurance sur ce qui est rare, récent ou propre à ton contexte : versions de bibliothèques, règles métier, sécurité fine. Plus la tâche est précise et vérifiable, plus le gain est sûr.", None),
  ("Les réflexes", EVO, """Avant d'accepter du code proposé
[ ] je comprends chaque ligne (sinon je demande une explication ligne par ligne)
[ ] les tests passent, et j'en ajoute un pour le cas nouveau
[ ] les versions de bibliothèques et les API existent vraiment (vérifiées dans la documentation)
[ ] aucune donnée sensible n'a été envoyée pour l'obtenir
[ ] l'analyse statique et la revue de code passent, comme pour du code écrit à la main""")],
 [("Un collègue fusionne une méthode proposée par l'assistant sans la relire : elle appelle une fonction de bibliothèque qui n'existe pas dans votre version. Quelle règle a manqué ?", "Comprendre et tester avant d'accepter : l'assistant invente parfois des API plausibles. Compilation, tests et relecture auraient arrêté l'erreur ; la responsabilité reste celle du développeur qui livre."),
  ("Question d'entretien : comment utilises-tu les assistants IA au quotidien ?", "Pour ce qui est vérifiable : tests, conversions, explications, premiers jets, relecture de mon propre code ; je donne le contexte, je demande un plan avant le code sur les tâches larges, et je vérifie tout par la compilation, les tests et la revue.")],
 ("Carte de mes usages", ["Lister dix tâches de ta semaine et, pour chacune, l'outil le plus adapté (complétion, conversation, agent) ou aucun.", "Essayer trois de ces tâches avec deux outils différents ; noter le temps et les corrections nécessaires.", "Écrire ta liste personnelle de réflexes de vérification."],
  "Attendu : un tableau tâche / outil / gain / risque ; au moins une tâche où l'assistant ne vaut pas la peine ; une liste de réflexes de cinq lignes, affichable près de l'écran.")),

ch("Bien demander : contexte, contraintes, plan", 'j',
 ["La qualité de la réponse dépend du contexte donné : le but, le code concerné, les contraintes (version, style, performances), et à quoi on reconnaîtra que c'est réussi.", "Pour une tâche large, on demande d'abord un plan, on le corrige, puis on fait coder étape par étape.", "On fait aussi expliquer, critiquer et tester : l'assistant est un bon relecteur de ton code et un bon générateur de cas limites."],
 ["Formuler une demande de code précise", "Travailler en plan, puis en étapes", "Utiliser l'assistant comme relecteur et testeur"],
 [("Une bonne demande", "On donne le rôle du code, l'extrait concerné, les contraintes et le critère d'acceptation, en demandant de poser des questions si quelque chose manque. Une demande vague produit un code générique à refaire.", """Contexte : service Spring Boot 3, Java 21, PostgreSQL ; classe IncidentService ci-dessous.
Objectif : ajouter l'escalade d'un incident (niveau croissant, incident ouvert seulement).
Contraintes : pas de nouvelle dépendance ; exceptions métier existantes (IncidentClosException) ; style du fichier.
Critère : tests JUnit pour les trois cas (succès, incident clos, niveau non croissant).
Avant d'écrire le code, propose un plan en trois étapes et pose tes questions s'il manque une information.
<code> … extrait de IncidentService … </code>"""),
  ("Plan, puis étapes", "Pour une modification qui touche plusieurs fichiers : demander l'analyse et un plan, le relire, le corriger, puis faire exécuter une étape à la fois avec les tests entre chaque étape. On garde la main sur l'architecture, l'assistant exécute.", None),
  ("Relire, critiquer, tester", "Les demandes les plus rentables sont souvent inverses : « relis ce code comme un relecteur exigeant », « quels cas limites ne sont pas testés ? », « explique cette méthode héritée ligne par ligne », « propose trois façons de faire et leurs compromis ».", """Relis cette méthode comme un relecteur sénior : erreurs, cas limites, sécurité, lisibilité.
Classe tes remarques par gravité et propose une correction seulement pour les deux plus graves.
---
Écris les tests JUnit des cas limites de parseDateSignalement : null, vide, fuseaux, dates impossibles, formats hérités.
---
Explique ce job Struts 1 ligne par ligne, puis dis ce qui risque de casser si on migre l'action vers Spring MVC.""")],
 [("« Écris-moi une API de gestion d'incidents » donne un code générique inutilisable. Comment reformuler ?", "Donner le contexte réel (pile, modèle existant, conventions), l'objectif précis, les contraintes et le critère d'acceptation, et demander un plan avant le code ; puis avancer étape par étape avec les tests."),
  ("Question d'entretien : quelle est ta demande la plus utile à un assistant de code ?", "Souvent pas « écris », mais « relis » ou « trouve les cas limites » : il repère des oublis rapidement, et c'est facile à vérifier ; pour écrire, je demande un plan avant le code.")],
 ("Même tâche, trois demandes", ["Réaliser la même évolution de CrisisShield avec une demande vague, une demande précise, puis plan et étapes.", "Comparer : corrections nécessaires, tests obtenus, temps total.", "Construire ta bibliothèque de cinq demandes types (fonctionnalité, relecture, tests, explication, refactoring)."],
  "Attendu : la demande précise avec plan demande nettement moins de corrections ; les cinq demandes types sont réutilisables telles quelles dans l'équipe.")),

ch("GitHub Copilot au quotidien et en équipe", 'c',
 ["Copilot propose des complétions dans l'éditeur, répond dans Copilot Chat, agit en mode agent sur le dépôt, et peut relire une pull request.", "Les instructions de dépôt (.github/copilot-instructions.md) et les fichiers de prompts partagent les conventions de l'équipe avec l'outil.", "Côté entreprise : exclusion de contenus sensibles, filtre des suggestions proches de code public, politiques par organisation, journal d'audit."],
 ["Utiliser complétion, chat, agent et relecture de Copilot", "Partager les conventions de l'équipe avec l'outil", "Configurer Copilot pour une organisation"],
 [("Les usages", EVO, T([
    ("Complétion", "écrire le test à partir de son nom, compléter un motif répétitif", "accepter mot par mot, relire"),
    ("Copilot Chat", "expliquer, générer, corriger avec le fichier ouvert en contexte", "désigner les fichiers utiles"),
    ("Mode agent", "modification sur plusieurs fichiers, lancement des tests", "branche dédiée, relecture du diff"),
    ("Relecture de pull request", "premier passage de relecture automatique", "complète la relecture humaine, ne la remplace pas")], ("Usage", "Exemple", "Bonne pratique"))),
  ("Les instructions de dépôt", "Un fichier d'instructions dans le dépôt donne à Copilot les règles du projet : pile, conventions, interdits. Des fichiers de prompts partagent les demandes répétées (écrire un test, ajouter un point d'API) avec toute l'équipe.", """# .github/copilot-instructions.md
- Java 21, Spring Boot 3 ; tests JUnit 5 et Testcontainers ; pas de Lombok.
- Exceptions métier du paquet fr.crisis.domaine ; jamais de RuntimeException générique.
- Toute nouvelle route : validation Bean Validation, ProblemDetail pour les erreurs, test d'autorisation.
- Tout se lance par Docker Compose ; ne jamais proposer d'installation locale.
- Aucun secret en clair : variables d'environnement ou Vault.
# .github/prompts/nouveau-test.prompt.md : demande partagée « écrire les tests d'une classe du domaine »"""),
  ("Configurer pour une organisation", "Les administrateurs choisissent les dépôts et fichiers exclus (secrets, données clients), activent le filtre qui bloque les suggestions identiques à du code public, fixent les politiques (modèles, fonctions autorisées) et suivent l'usage. L'accès se donne par équipe, avec une courte formation.", None)],
 [("Copilot propose, dans un fichier de configuration, une chaîne qui ressemble à une clé d'API. Que fais-tu ?", "Je ne l'accepte pas : les secrets viennent de l'environnement ou d'un coffre. Je vérifie que le dépôt a une détection de secrets en CI, et que les fichiers sensibles sont exclus des contenus envoyés à l'outil."),
  ("Question d'entretien : comment déploies-tu Copilot dans une équipe ?", "Par un pilote avec des mesures, des instructions de dépôt partagées, des exclusions de contenus sensibles, le filtre de code public, une relecture humaine inchangée, et une formation courte sur les bons usages et les limites.")],
 ("Copilot outillé pour CrisisShield", ["Écrire le fichier d'instructions du dépôt et deux fichiers de prompts partagés.", "Réaliser une évolution en mode agent sur une branche, relire le diff, compléter les tests.", "Rédiger la configuration d'organisation souhaitée : exclusions, filtre de code public, politiques."],
  "Attendu : les propositions respectent les conventions du fichier d'instructions ; l'évolution passe la CI après relecture ; la configuration d'organisation tient sur une page.")),

ch("Claude pour les développeurs : conversation, Claude Code, API", 'c',
 ["claude.ai sert à réfléchir, concevoir et écrire, avec des projets qui gardent le contexte et des artefacts qu'on fait évoluer.", "Claude Code est un agent de code dans le terminal (et l'IDE) : il lit le dépôt, planifie, modifie, lance les commandes et les tests, dans les limites de permissions que tu fixes.", "Le dépôt se prépare pour l'agent : fichier CLAUDE.md de conventions, commandes et compétences partagées, automatismes (hooks) de sécurité, serveurs MCP utiles."],
 ["Utiliser les projets et artefacts de claude.ai", "Mener une tâche avec Claude Code : explorer, planifier, coder, vérifier", "Préparer un dépôt pour un agent de code, en sécurité"],
 [("claude.ai pour le développeur", "Un projet regroupe les documents de référence (architecture, conventions, extraits de code) et les conversations ; les artefacts produisent documents, schémas et petits outils qu'on itère. C'est l'outil pour concevoir, écrire une ADR ou préparer une revue.", None),
  ("Claude Code, pas à pas", "Le déroulé qui marche : faire explorer le code sans rien modifier, demander un plan et le relire, faire coder par étapes avec les tests, puis faire relire le diff et rédiger la description de la MR. Les permissions limitent ce que l'agent peut lancer sans demander.", """# dans le conteneur de développement (Docker), à la racine du dépôt
claude
> Lis le module incidents et explique comment une escalade est traitée, sans rien modifier.
> Propose un plan pour ajouter l'escalade automatique après 30 minutes sans prise en charge.
> Applique l'étape 1 seulement, puis lance les tests du module.
> Relis ton diff comme un relecteur sénior et rédige la description de la MR."""),
  ("Préparer le dépôt", EVO, """CLAUDE.md                       conventions, commandes de build et de test, interdits (lu à chaque session)
.claude/settings.json          permissions et automatismes (hooks), par exemple bloquer la lecture de .env
.claude/commands/revue.md      commande partagée « /revue » : relecture selon la liste de l'équipe
.claude/skills/securite/SKILL.md  compétence réutilisable : revue de sécurité applicative
.mcp.json                      serveurs MCP du projet (lecture seule de préférence : tickets, documentation)
# règle : l'agent travaille sur une branche, la MR et la relecture humaine décident""")],
 [("Claude Code a modifié quarante fichiers d'un coup et la MR est impossible à relire. Qu'est-ce qui a manqué ?", "Un plan découpé en étapes, avec une étape par demande et les tests entre chaque ; et des MR petites. L'agent peut beaucoup, c'est au développeur de fixer la taille des pas."),
  ("Question d'entretien : comment sécurises-tu un agent de code sur un dépôt ?", "Permissions limitées (commandes autorisées, confirmation pour le reste), automatismes qui bloquent secrets et commandes dangereuses, travail sur une branche dans un conteneur, serveurs MCP en lecture seule, et relecture humaine de chaque MR.")],
 ("Dépôt prêt pour un agent", ["Écrire le CLAUDE.md de CrisisShield (pile, commandes Docker, tests, interdits).", "Ajouter un automatisme qui bloque la lecture de .env et une commande partagée de relecture.", "Mener une évolution complète : exploration, plan relu, étapes testées, MR relue."],
  "Attendu : l'agent refuse de lire .env ; l'évolution arrive en MR de moins de 400 lignes, tests compris ; la description de MR est exploitable telle quelle.")),

ch("ChatGPT, Gemini, Mistral et modèles locaux", 'c',
 ["ChatGPT offre conversation, projets, GPTs personnalisés, analyse de fichiers et un agent de code ; Gemini s'intègre à l'écosystème Google ; Mistral propose des modèles européens ; des modèles ouverts tournent en local.", "Le bon outil dépend de la tâche, des données manipulées, du contrat et du coût, pas de la mode : on compare sur ses propres cas.", "Un modèle local (Ollama en conteneur) sert quand les données ne doivent pas sortir, au prix d'une qualité souvent moindre."],
 ["Comparer les assistants sur ses propres tâches", "Créer un assistant personnalisé pour une tâche répétée", "Faire tourner un modèle local pour les données sensibles"],
 [("Comparer honnêtement", "", T([
    ("Qualité sur tes tâches", "même jeu de dix tâches pour chaque outil", "noter les corrections nécessaires"),
    ("Intégration", "IDE, dépôt, outils de l'entreprise", "l'outil utilisé est celui qui est intégré"),
    ("Données et contrat", "où vont les données, entraînement, rétention", "offres entreprise, réglages vérifiés"),
    ("Coût", "licence par poste ou usage à la consommation", "rapporté au gain mesuré")], ("Critère", "Comment l'évaluer", "À retenir"))),
  ("Un assistant personnalisé", "Pour une tâche répétée (rédiger un post-mortem, relire une MR selon la liste de l'équipe), on crée un assistant avec ses consignes et ses documents de référence : un GPT personnalisé, un projet claude.ai, ou une commande partagée dans le dépôt.", """Assistant « Post-mortem CrisisShield »
Consignes : structure (chronologie, impact chiffré, causes en cinq pourquoi, actions datées avec propriétaire), ton sans blâme,
           aucune donnée personnelle, questions si une information manque.
Documents : modèle de post-mortem de l'équipe, deux exemples anonymisés.
Usage : coller la chronologie brute ; relire et compléter ; jamais publier sans relecture."""),
  ("Un modèle local", "Ollama fait tourner des modèles ouverts dans un conteneur ; l'éditeur ou un script l'interroge sur le réseau local. On l'évalue sur les mêmes tâches : il est souvent suffisant pour résumer, reformuler ou classer, moins pour du code complexe.", """docker run -d --name ollama -p 11434:11434 -v ollama:/root/.ollama ollama/ollama
docker exec ollama ollama pull qwen2.5-coder:7b
curl -s http://localhost:11434/api/generate -d '{"model":"qwen2.5-coder:7b","prompt":"Résume ce journal d'"'"'erreurs : …","stream":false}'""")],
 [("L'équipe hésite entre trois assistants et chacun défend le sien. Comment trancher ?", "Par un essai mesuré : les mêmes dix tâches réelles, les mêmes critères (corrections nécessaires, temps, intégration, contrat de données, coût), et une décision écrite ; les goûts personnels ne sont pas un critère."),
  ("Question d'entretien : quand utiliser un modèle local ?", "Quand les données ne peuvent pas sortir (code client sous accord, données personnelles) et que la tâche le permet ; on mesure la qualité sur ses cas, et on garde un outil en ligne sous contrat pour le reste.")],
 ("Banc d'essai des assistants", ["Dix tâches réelles de CrisisShield, lancées sur deux assistants en ligne et un modèle local en conteneur.", "Tableau : corrections, temps, adéquation, risques de données, coût.", "Un assistant personnalisé pour les post-mortems, testé sur un incident simulé."],
  "Attendu : un choix argumenté par tâche, pas un vainqueur unique ; le modèle local couvre au moins les tâches de résumé ; l'assistant post-mortem produit un brouillon conforme au modèle.")),

ch("Cas d'usage du développeur", 'c',
 ["Les gains les plus sûrs : tests, documentation, conversions et migrations mécaniques, requêtes SQL et expressions régulières, lecture de code hérité, analyse de journaux, scripts.", "Sur le code hérité, on fait d'abord comprendre et écrire des tests de caractérisation, puis on change par petites étapes.", "Chaque usage a son contrôle : les tests pour le code, l'exécution pour le SQL, un échantillon relu pour la documentation."],
 ["Utiliser l'assistant sur les tâches où il rapporte le plus", "Moderniser du code hérité sans régression", "Associer à chaque usage son contrôle"],
 [("Où il rapporte", "", T([
    ("Tests", "tests unitaires et cas limites d'une classe", "ils passent, et échouent si on casse le code"),
    ("Code hérité", "expliquer une action Struts ou un job Talend", "comparaison avec l'exécution réelle"),
    ("Migration", "Java 8 vers 21, javax vers jakarta, JUnit 4 vers 5", "compilation et suite de tests complète"),
    ("SQL", "requête, plan d'exécution commenté, index", "exécution sur une copie et EXPLAIN"),
    ("Journaux", "résumer 2 000 lignes d'erreurs, regrouper par cause", "retour aux lignes citées"),
    ("Documentation", "README, ADR, description de MR", "relecture par un humain")], ("Usage", "Exemple", "Contrôle"))),
  ("Moderniser du code hérité", "D'abord faire expliquer le code et ses effets, puis faire écrire des tests de caractérisation qui figent le comportement actuel, ensuite seulement modifier par petites étapes, en relançant les tests. L'assistant accélère chaque étape, il ne supprime aucune étape.", """Étape 1 : « Explique l'action IncidentAction (Struts 1) : entrées, sorties, effets en base. »
Étape 2 : « Écris des tests de caractérisation HTTP qui figent le comportement actuel des trois écrans. »
Étape 3 : « Propose la version Spring MVC de l'écran liste seulement ; garde les mêmes URL et le même rendu. »
Étape 4 : les tests de caractérisation passent sur l'ancienne et la nouvelle version → écran suivant"""),
  ("Analyser un incident", "On colle des journaux anonymisés, une trace, une requête lente : l'assistant propose des hypothèses et les vérifications à faire, que l'on mène soi-même. Il accélère le diagnostic sans remplacer la preuve.", None)],
 [("On demande à l'assistant de migrer tout un module Java 8 vers Java 21 d'un coup ; la compilation passe mais trois comportements ont changé. Qu'aurait-il fallu ?", "Des tests couvrant le comportement avant la migration, une migration par étapes mécaniques (dépendances, javax vers jakarta, API retirées), et la suite complète de tests à chaque étape ; « ça compile » n'est pas « ça marche pareil »."),
  ("Question d'entretien : un exemple concret où l'IA t'a fait gagner du temps ?", "Un exemple mesuré : les tests de caractérisation d'un écran hérité écrits en une heure au lieu d'une journée, relus et complétés, qui ont permis de migrer l'écran sans régression ; avec ce que j'ai dû corriger.")],
 ("Moderniser un écran hérité avec l'assistant", ["Faire expliquer un écran Struts de CrisisShield (ou un job Talend) et vérifier l'explication.", "Faire écrire les tests de caractérisation, les relire et les compléter.", "Migrer l'écran en petites étapes ; mesurer le temps et les corrections."],
  "Attendu : les mêmes tests passent avant et après ; le journal des étapes montre ce que l'assistant a fait et ce qui a été corrigé ; le temps total est comparé à une estimation sans assistant.")),

ch("Sécurité et confidentialité", 's',
 ["Ce qui ne part jamais vers un assistant en ligne sans accord : secrets, données personnelles, code ou données d'un client sous confidentialité.", "Le code généré peut être vulnérable ou copié : il passe les mêmes contrôles que le reste (analyse statique, dépendances, secrets, revue), et les licences se vérifient.", "Les agents ouvrent de nouvelles attaques : instructions cachées dans des fichiers du dépôt ou des tickets, extensions et serveurs MCP douteux, commandes exécutées sans contrôle."],
 ["Savoir ce qu'on peut envoyer à quel outil", "Contrôler le code généré comme n'importe quel code", "Protéger un agent de code contre les injections"],
 [("Ce qu'on envoie, ou pas", "", T([
    ("Secrets (clés, mots de passe, jetons)", "jamais", "détection de secrets, fichiers exclus"),
    ("Données personnelles", "non, ou anonymisées", "jeux de données fictifs"),
    ("Code d'un client", "selon le contrat et l'outil autorisé", "outil sous contrat d'entreprise"),
    ("Code interne ordinaire", "outil autorisé par l'entreprise", "réglages de confidentialité vérifiés"),
    ("Code public, documentation", "oui", "citer la source si on la réutilise")], ("Contenu", "Vers un assistant en ligne", "Parade"))),
  ("Le code généré", "Il contient les mêmes défauts que le code humain, parfois plus : injection SQL, validation absente, dépendances obsolètes, secrets factices recopiés. Analyse statique, analyse des dépendances, détection de secrets et relecture s'appliquent sans exception ; pour les gros extraits, on vérifie l'origine et la licence.", """# les contrôles de la CI ne changent pas selon l'auteur du code
semgrep ci          # analyse statique (règles OWASP)
trivy fs .          # dépendances et configuration
gitleaks detect     # secrets
# + relecture humaine ; filtre de code public activé côté Copilot pour l'organisation"""),
  ("Les attaques propres aux agents", "Un fichier du dépôt, un ticket ou une page lue par l'agent peut contenir des instructions cachées ; une extension ou un serveur MCP peut exfiltrer. Parades : l'agent n'a pas accès aux secrets, ses commandes sensibles demandent confirmation, il travaille en conteneur sur une branche, et ses outils sont audités.", None)],
 [("Un développeur colle dans un assistant grand public le code d'un client et un extrait de base avec des noms réels, « pour aller plus vite ». Quels problèmes ?", "Violation possible de la confidentialité contractuelle et du RGPD, selon les réglages de l'outil ; il fallait un outil autorisé sous contrat d'entreprise, des données anonymisées ou fictives, et en cas de doute l'accord du client."),
  ("Question d'entretien : le code généré par IA est-il sûr ?", "Ni plus ni moins que du code écrit par un inconnu : il passe l'analyse statique, l'analyse des dépendances, la détection de secrets et la relecture ; on vérifie aussi les API inventées et les licences des gros extraits.")],
 ("Politique d'usage sûre", ["Rédiger la politique d'une page : outils autorisés, ce qu'on envoie ou non, contrôles obligatoires.", "Tester une injection cachée dans un fichier du dépôt face à un agent, puis mettre les parades (secrets inaccessibles, confirmation, conteneur).", "Passer un lot de code généré dans semgrep, trivy et gitleaks ; corriger ce qui sort."],
  "Attendu : la politique est applicable dès demain ; l'injection échoue après parades ; au moins un défaut réel est trouvé et corrigé dans le code généré.")),

ch("Industrialiser en équipe : politique, formation, mesure", 's',
 ["Un déploiement réussi tient à la méthode, pas aux licences : un pilote, des conventions partagées, une formation courte, une relecture inchangée et des mesures.", "On mesure avant et après : délai des MR, taux de défauts, temps de revue, satisfaction des développeurs ; les métriques DORA et SPACE donnent le cadre.", "On choisit l'offre selon les besoins : licences par poste pour l'IDE, offre entreprise pour la confidentialité, agents pour les tâches multi-fichiers."],
 ["Monter un pilote d'assistants IA avec des mesures", "Écrire la politique et les conventions d'équipe", "Présenter les résultats et décider de la suite"],
 [("Le pilote", "Deux équipes volontaires, six semaines, des objectifs clairs (tests, documentation, code hérité), une formation de deux heures, des conventions dans les dépôts, et des mesures avant et après. Les résultats décident de l'extension, pas l'enthousiasme.", """Pilote « assistants IA » : 6 semaines, 2 équipes
Semaine 0 : mesures de référence (délai de MR, défauts, temps de revue, sondage)
Semaine 1 : formation de 2 h (bons usages, limites, sécurité) ; instructions de dépôt et CLAUDE.md
Semaines 2 à 5 : usage réel, journal des cas marquants (gains et erreurs)
Semaine 6 : mesures, sondage, retour d'expérience, recommandation écrite"""),
  ("Mesurer sans se tromper", "", T([
    ("Délai d'une MR", "de l'ouverture à la fusion", "baisse attendue, à confirmer"),
    ("Taux de défauts", "incidents et bogues liés aux changements", "ne doit pas monter"),
    ("Temps de revue", "effort des relecteurs", "attention s'il monte"),
    ("Satisfaction", "sondage court", "utile mais insuffisant seul"),
    ("Lignes de code", "volume produit", "à ne pas utiliser comme objectif")], ("Mesure", "Définition", "Lecture"))),
  ("Décider", "La recommandation écrite dit où l'outil rapporte, où il ne rapporte pas, les risques observés et leurs parades, le coût rapporté au gain, et le plan d'extension. Une présentation de dix minutes à la direction suffit, chiffres à l'appui.", None)],
 [("La direction achète des licences pour tous sans formation ni conventions ; trois mois après, les résultats sont inégaux et deux incidents viennent de code non relu. Que proposes-tu ?", "Reprendre avec la méthode : conventions et instructions de dépôt, formation courte, relecture humaine obligatoire rappelée, contrôles de CI inchangés, et des mesures par équipe pour cibler les usages qui rapportent."),
  ("Question d'entretien : comment mesures-tu l'apport d'un assistant IA ?", "Avant et après, sur des indicateurs de livraison et de qualité (délai des MR, défauts, temps de revue) plus un sondage ; jamais sur les lignes de code, et en regardant aussi ce qui se dégrade.")],
 ("Pilote sur CrisisShield", ["Mesures de référence sur un mois de MR du projet.", "Conventions (instructions Copilot, CLAUDE.md), formation d'une heure pour deux collègues, quatre semaines d'usage.", "Recommandation d'une page et présentation de dix minutes."],
  "Attendu : un tableau avant/après sur quatre mesures ; au moins un usage abandonné faute de gain ; une recommandation que la direction peut valider telle quelle.")),

ch("Devenir expert et en parler en entretien", 'e',
 ["L'expert choisit la taille des pas : spécification d'abord, tests d'abord, agents en parallèle sur des tâches indépendantes, et relecture systématique.", "Il connaît les limites : contexte, connaissances datées, inventions, sécurité ; il sait quand ne pas utiliser l'outil.", "En entretien, il montre des résultats mesurés, explique son propre code, et parle de gouvernance autant que de productivité."],
 ["Pratiquer des méthodes de travail avancées", "Expliquer les limites et les risques avec précision", "Préparer ses réponses d'entretien sur les assistants IA"],
 [("Méthodes avancées", "La spécification d'abord : on écrit ce qui est attendu (comportement, tests d'acceptation), l'agent code jusqu'à ce que les tests passent. Plusieurs agents peuvent avancer en parallèle sur des tâches indépendantes, chacun sur sa branche. On garde de petites MR et la relecture humaine.", """Méthode « spécification et tests d'abord »
1. j'écris la spécification courte et les tests d'acceptation (ou je les fais proposer, puis je les corrige)
2. l'agent implémente jusqu'à ce que les tests passent, sur une branche
3. l'agent relit son diff ; je relis ensuite ; MR de moins de 400 lignes
4. je note dans la MR ce qui a été généré et ce que j'ai corrigé"""),
  ("Trente questions d'entretien", "", """1 Complétion, chat, agent ? Suggestions, conversation, tâches sur le dépôt. 2 Qui est responsable du code ? Celui qui le livre. 3 Bonne demande ? Contexte, objectif, contraintes, critère. 4 Tâche large ? Plan d'abord, puis étapes. 5 Usage le plus rentable ? Relire, tester, expliquer. 6 Instructions de dépôt ? Conventions partagées avec l'outil. 7 Mode agent ? Multi-fichiers, sur une branche, relu. 8 Relecture par l'IA ? En plus de l'humain, jamais à la place. 9 CLAUDE.md ? Conventions lues par Claude Code. 10 Hooks ? Automatismes : bloquer, lancer les tests. 11 Serveurs MCP ? Outils et contexte, en lecture seule de préférence. 12 Projets claude.ai ? Contexte partagé pour concevoir. 13 GPT personnalisé ? Assistant pour une tâche répétée. 14 Modèle local ? Données sensibles, qualité à mesurer. 15 Choisir un outil ? Essai mesuré sur ses tâches. 16 Code hérité ? Comprendre, tests de caractérisation, petites étapes. 17 Migration ? Étapes mécaniques, suite de tests. 18 SQL généré ? Exécuté sur une copie avec EXPLAIN. 19 Secrets ? Jamais envoyés. 20 Données personnelles ? Anonymisées ou fictives. 21 Code client ? Outil sous contrat, accord du client. 22 Code généré vulnérable ? Mêmes contrôles de CI. 23 Licences ? Vérifier l'origine des gros extraits. 24 Injection via le dépôt ? Secrets inaccessibles, confirmations. 25 Déployer en équipe ? Pilote, conventions, formation, mesures. 26 Mesurer ? Délai des MR, défauts, revue, sondage. 27 Lignes de code ? Pas un objectif. 28 Limites ? Contexte, inventions, connaissances datées. 29 Quand ne pas l'utiliser ? Tâche non vérifiable ou données interdites. 30 Ce qui fait l'expert ? Petits pas, preuves, gouvernance.""")],
 [("En entretien : « l'IA va-t-elle remplacer les développeurs ? » Comment réponds-tu ?", "Sans slogan : elle automatise une part croissante de l'écriture de code, ce qui déplace la valeur vers la compréhension du besoin, l'architecture, la vérification, la sécurité et la responsabilité ; je montre comment je l'utilise et ce que je vérifie."),
  ("Question d'entretien : pouvez-vous expliquer ce code que vous avez livré avec un assistant ?", "Oui, ligne par ligne, avec les choix faits et les corrections apportées : c'est la condition pour le livrer. Un développeur qui ne peut pas expliquer son code ne l'a pas relu.")],
 ("Portfolio assistants IA", ["Une évolution de CrisisShield menée en spécification et tests d'abord, avec un agent, en MR de moins de 400 lignes.", "Une note d'une page : méthode, mesures, corrections, risques et parades.", "Répondre à voix haute aux trente questions, dix d'entre elles chronométrées."],
  "Attendu : la MR montre ce qui a été généré et corrigé ; la note peut être montrée à un recruteur ; les réponses tiennent en moins d'une minute et s'appuient sur des exemples réels.")),
]

d = sys.argv[1]
page('cours-32-assistants-ia-copilot-claude-chatgpt.html', 'Assistants IA pour développeurs : GitHub Copilot, Claude, ChatGPT — de zéro à expert', "Neuf chapitres pour utiliser les assistants IA de façon efficace et sûre : complétion, conversation et agents, bien formuler une demande, GitHub Copilot au quotidien et en organisation, Claude (claude.ai, Claude Code, API) et la préparation d'un dépôt pour un agent, ChatGPT, Gemini, Mistral et modèles locaux, cas d'usage du développeur (tests, code hérité, migrations, SQL, journaux), sécurité et confidentialité, industrialisation en équipe avec mesures, méthodes d'expert et 30 questions d'entretien. Fil conducteur : CrisisShield ; chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 25 h de travail · aucun prérequis au-delà du développement ; complète le cours IA agentique, qui apprend à construire avec les LLM.", AS, [('cours-31-ia-agentique.html', 'IA agentique'), ('devops-09-expert-et-leadership.html', 'DevOps niveau 9')])
