"""Préparer une mission de Tech Lead Java en MCO et MCS (17 chapitres). Contexte générique : grande institution
financière publique, application Java legacy. Usage : python3 mission_pages.py <dossier>"""
import sys, runpy, pathlib
g = runpy.run_path(pathlib.Path(__file__).with_name('front_gen.py'), run_name='front'); ch, page = g['ch'], g['page']
def T(rows, head): return '<div class="tablewrap"><table><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table></div>'

def CK(titre, items): return f'<p class="liste-titre">{titre}</p><ul class="liste-controle">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'
def ET(items): return '<ol class="etapes">' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>'
def QS(groupes):
    out, n = '', 1
    for theme, qs in groupes:
        out += f'<p class="liste-titre">{theme}</p><ol class="questions" start="{n}">' + ''.join(f'<li>{q}</li>' for q in qs) + '</ol>'; n += len(qs)
    return out
DK = "Tout en conteneur : WildFly (<code>quay.io/wildfly/wildfly</code>), Oracle Free (<code>gvenzl/oracle-free</code>), Rundeck, SonarQube, GitLab Runner et PowerShell (<code>mcr.microsoft.com/powershell</code>) tournent par Docker Compose ; rien n'est installé sur le poste."

MI = [
ch("Comprendre la mission : périmètre, acteurs, niveaux attendus", 'j',
 ["Le Tech Lead garantit que l'application tourne (MCO : évolutive, adaptative, corrective), qu'elle reste sûre (MCS : corriger les vulnérabilités remontées par les audits), et que chaque version passe proprement de l'intégration à la production.", "Il ne code pas seul : il pilote un centre de services (CDS) qui développe, travaille avec l'équipe DevOps, l'exploitation, l'architecte, la maîtrise d'œuvre et la maîtrise d'ouvrage, et appuie le support de niveau 2.", "Deux profils : expert (environnements, ordonnancement, exploitation, migrations, accréditations) et avancé (MCO/MCS, spécifications, suivi du CDS) ; les compétences exigées vont de Java 17 à l'ordonnancement."],
 ["Décrire le périmètre et les livrables de la mission", "Situer chaque acteur et ce qu'il attend du Tech Lead", "Évaluer ses écarts avec les niveaux exigés et bâtir un plan"],
 [("Les activités et leurs livrables", T([
    ("Faire fonctionner intégration et production", "suivi de l'ordonnancement, configuration, surveillance, module d'exploitation", "à chaque changement d'infrastructure ou version"),
    ("Mode opératoire testé et ISO", "installation jouée en intégration puis identique en production, vérification matinale des traitements", "chaque mise en production, chaque matin"),
    ("Nouveaux modules", "étude de solutions avec l'architecte et le CDS", "chaque demande d'évolution"),
    ("MCO et MCS", "Confluence, Jira, communication, CI/CD du CDS, revue de code, livrables, barrière SonarQube, POC, analyse des devis", "chaque évolution ou correctif"),
    ("Migrations techniques", "analyse et mise en place selon les standards de l'organisation, accompagnement", "chaque migration de composant"),
    ("Accréditations", "gestion des droits des utilisateurs avec leurs représentants", "à la demande")], ("Activité", "Actions et livrables", "Rythme")), None),
  ("Les niveaux exigés", "", T([
    ("WildFly 26 et plus", "expert", "partie 2"), ("Bash, PowerShell, Unix", "expert", "partie 4"), ("Ordonnancement", "expert", "partie 3"),
    ("Java 17 et plus", "avancé", "partie 6"), ("Python", "avancé", "partie 10"), ("GitLab CI, Jenkins, Confluence, Jira", "avancé", "parties 9 et 1"),
    ("XML", "avancé", "partie 8"), ("Struts 1", "autonome à avancé", "partie 7"), ("SQL, PL/SQL, Oracle", "autonome à avancé", "partie 5"),
    ("Services web REST et SOAP", "autonome", "partie 8"), ("Hibernate, Spring", "autonome à avancé", "partie 7")], ("Compétence", "Niveau exigé", "Où la travailler"))),
  ("Les cours du site à réutiliser", T([("WildFly 26 et plus", "partie 2", '<a href="devops-01-virtualisation-et-conteneurs.html">DevOps niveau 1 (conteneurs)</a>, <a href="devops-06-observabilite.html">DevOps niveau 6 (supervision, alertes)</a>, <a href="cours-41-keycloak-et-iam.html">Keycloak et IAM (LDAP, habilitations)</a>'),("Ordonnancement", "partie 3", '<a href="cours-62-talend.html">Talend (plans d’exécution)</a>, <a href="cours-61-data-platform-aws-talend.html">Data Platform (Airflow)</a>, <a href="cours-63-monitoring.html">Monitoring (Prometheus, ELK)</a>'),("Bash, PowerShell, Unix", "partie 4", '<a href="devops-00-fondations.html">DevOps niveau 0 (Linux, shell, Git)</a>, <a href="cours-71-perl.html">Perl (scripts legacy)</a>, <a href="devops-10-aide-memoire.html">Aide-mémoire des commandes</a>'),("SQL, PL/SQL, Oracle", "partie 5", '<a href="cours-11-struts-hibernate-jsp.html">Struts, Hibernate et JSP</a>, <a href="devops-08-sre-et-architecture.html">DevOps niveau 8 (SRE, incidents, bases en production)</a>'),("Java 17 et plus", "partie 6", '<a href="cours-12-kotlin.html">Kotlin (JVM)</a>, <a href="cours-13-java-pki-signature-electronique.html">Java PKI et signature électronique</a>, <a href="cours-21-microservices.html">Microservices (Spring Boot, REST, contrats)</a>'),("Struts 1, Spring, Hibernate", "partie 7", '<a href="cours-11-struts-hibernate-jsp.html">Struts, Hibernate et JSP</a>, <a href="cours-21-microservices.html">Microservices (Spring Boot, REST, contrats)</a>, <a href="cours-41-keycloak-et-iam.html">Keycloak et IAM (LDAP, habilitations)</a>'),("XML, services web REST et SOAP", "partie 8", '<a href="cours-13-java-pki-signature-electronique.html">Java PKI et signature électronique</a>, <a href="cours-21-microservices.html">Microservices (Spring Boot, REST, contrats)</a>'),("GitLab CI, Jenkins, SonarQube", "partie 9", '<a href="devops-02-integration-et-livraison-continues.html">DevOps niveau 2 (CI/CD, GitLab CI, Jenkins, SonarQube)</a>, <a href="devops-07-securite-devsecops.html">DevOps niveau 7 (DevSecOps, MCS)</a>, <a href="devops-03-infrastructure-as-code.html">DevOps niveau 3 (Ansible, infrastructure as code)</a>'),("Confluence, Jira, pilotage", "partie 1", '<a href="devops-09-expert-et-leadership.html">DevOps niveau 9 (leadership, gouvernance)</a>, <a href="cours-91-savoir-etre-de-zero-a-expert.html">Savoir-être</a>'),("Python", "partie 10", '<a href="cours-31-ia-agentique.html">IA agentique (Python)</a>, <a href="cours-61-data-platform-aws-talend.html">Data Platform (Airflow)</a>, <a href="cours-71-perl.html">Perl (scripts legacy)</a>'),("MCS, sécurité", "partie 1", '<a href="devops-07-securite-devsecops.html">DevOps niveau 7 (DevSecOps, MCS)</a>, <a href="cours-41-keycloak-et-iam.html">Keycloak et IAM (LDAP, habilitations)</a>'),("Entretien", "partie 11", '<a href="devops-11-fiches-entretien.html">Fiches entretien DevOps</a>, <a href="cours-92-savoir-etre-situations-et-attitudes.html">Savoir-être : situations</a>')], ("Compétence", "Dans cette page", "Cours déjà disponibles sur le site")), None),
  ("Mon plan de préparation", "On note son niveau réel pour chaque ligne (de 0 à 4), on commence par les écarts sur les compétences de niveau expert, et on termine chaque chapitre par son TP : une compétence n'est acquise que si on l'a pratiquée dans un conteneur, pas seulement lue.", ET(["<strong>Semaine 1</strong> : WildFly (partie 2) et environnements identiques (partie 1)", "<strong>Semaine 2</strong> : ordonnancement (partie 3), Unix, Bash et PowerShell (partie 4)", "<strong>Semaine 3</strong> : Oracle (partie 5), Java 17 (partie 6), Struts, Spring et Hibernate (partie 7)", "<strong>Semaine 4</strong> : XML et services web (partie 8), CI/CD (partie 9), Python (partie 10), sécurité applicative et pilotage du CDS (partie 1), entretien (partie 11)"]))],
 [("Quelle différence entre MCO « évolutive, adaptative et corrective » ?", "Corrective : réparer ce qui ne marche pas ; adaptative : suivre les changements de l'environnement (versions, infrastructure, réglementation) ; évolutive : ajouter ou modifier des fonctions. Les trois se planifient différemment, et la corrective urgente passe avant tout."),
  ("Question d'entretien : que fait un Tech Lead en MCO que ne fait pas un développeur ?", "Il garantit le fonctionnement de bout en bout : environnements, ordonnancement, mises en production testées et identiques, qualité et sécurité des livrables du CDS, arbitrages techniques, communication aux parties prenantes ; il code surtout pour les POC, les scripts et les corrections critiques.")],
 ("Ma grille de préparation", ["Remplir la grille d'auto-évaluation des onze compétences exigées.", "Classer les écarts, en commençant par les compétences de niveau expert.", "Construire son planning de quatre semaines et le relier aux TP de cette page."],
  "Attendu : une grille chiffrée, les trois écarts prioritaires identifiés, un planning daté ; à la fin, chaque ligne remontée au niveau exigé preuve à l'appui (TP réalisé).")),

ch("Le socle applicatif : cartographier une application Java legacy", 'j',
 ["L'architecture typique : pages JSP et actions Struts 1, services Spring, accès aux données par Hibernate, base Oracle, le tout packagé en WAR ou EAR et déployé sur WildFly, avec des traitements par lots ordonnancés.", "La première semaine sert à cartographier : modules, flux, dépendances, configurations par environnement, traitements, points de fragilité ; on n'améliore que ce qu'on a compris.", "Le résultat est un document vivant dans Confluence : schéma d'architecture, inventaire des composants et versions, liste des risques."],
 ["Reconnaître les couches d'une application legacy", "Cartographier une application inconnue en une semaine", "Produire l'inventaire technique et la liste des risques"],
 [("Les couches", "", '<div class="couches"><div><span>Navigateur, puis <strong>JSP et Struts 1</strong> : ActionServlet, Actions, ActionForms, Tiles</span><small>couche web, javax.servlet</small></div><div><span><strong>Services Spring</strong> : transactions, règles métier</span><small>beans annotés ou XML</small></div><div><span><strong>DAO Hibernate</strong> : sessions, mappings hbm.xml ou annotations</span><small>accès aux données</small></div><div><span><strong>Oracle</strong> : tables, séquences, PL/SQL</span><small>base de données</small></div><div class="a-cote"><span><strong>Déploiement</strong> : WAR ou EAR sur WildFly (datasource JNDI, sécurité, journaux) · <strong>à côté</strong> : services SOAP et REST, traitements par lots lancés par l\'ordonnanceur</span><small>exploitation</small></div></div>'),
  ("Cartographier en une semaine", "", T([
    ("Jour 1", "accès, dépôts, environnements, contacts", "liste des accès et des interlocuteurs"),
    ("Jour 2", "construire et lancer l'application en conteneur", "application qui démarre, versions relevées"),
    ("Jour 3", "modules, dépendances (mvn dependency:tree), configurations", "inventaire des composants et versions"),
    ("Jour 4", "flux, services exposés et appelés, traitements ordonnancés", "schéma des flux et de l'ordonnancement"),
    ("Jour 5", "journaux, incidents récents, rapport SonarQube, vulnérabilités", "liste des risques priorisés")], ("Moment", "Ce qu'on regarde", "Livrable"))),
  ("L'inventaire technique", "Chaque composant avec sa version, sa date de fin de support et son risque : Java, WildFly, Struts, Spring, Hibernate, pilote Oracle, bibliothèques. Les composants en fin de support alimentent le plan de migration (chapitres 4, 9 et 10) et le suivi MCS (chapitre 13).", r"""docker run --rm -v "$PWD:/app" -w /app -v m2:/root/.m2 maven:3.9-eclipse-temurin-17 mvn -q dependency:tree -DoutputFile=arbre.txt
docker run --rm -v "$PWD:/app" -w /app -v m2:/root/.m2 maven:3.9-eclipse-temurin-17 mvn -q versions:display-dependency-updates
grep -rE "struts|spring-core|hibernate-core|ojdbc" arbre.txt | sort -u""")],
 [("Tu arrives et on te demande un avis sur une évolution dès le deuxième jour. Que fais-tu ?", "Je donne un avis prudent et daté : ce que je sais, ce que je dois vérifier, et quand je reviendrai avec une réponse ferme ; puis je cartographie en priorité la partie concernée. Un avis ferme sans connaître l'existant est un risque pour tout le monde."),
  ("Question d'entretien : comment prends-tu en main une application que tu ne connais pas ?", "En la faisant tourner dans un environnement maîtrisé, en inventoriant composants, versions et flux, en lisant les incidents et les rapports qualité récents, puis en écrivant une page de synthèse avec les risques ; je propose les premières actions à la fin de la première semaine.")],
 ("Cartographier le module legacy de CrisisShield", ["Construire et lancer le module legacy (Struts 1, Spring, Hibernate) sur WildFly avec Oracle Free en Compose.", "Inventaire des composants et versions avec fin de support ; schéma des couches et des flux.", "Liste des dix risques principaux, classés par gravité et probabilité."],
  "Attendu : l'application démarre depuis le dépôt ; l'inventaire indique pour chaque composant sa version et son statut de support ; les risques sont reliés à une action proposée.")),

ch("WildFly (1) : installer, configurer, déployer", 's',
 ["WildFly tourne en mode autonome (standalone : un serveur, un fichier de configuration) ou en mode domaine (un contrôleur gère des groupes de serveurs et leurs profils).", "Toute la configuration vit dans standalone.xml (ou domain.xml) et se modifie par jboss-cli : on écrit des scripts, jamais de modifications à la main.", "Une application se déploie en WAR ou en EAR ; ses dépendances techniques (pilote Oracle, datasource, sécurité) sont fournies par le serveur."],
 ["Lancer WildFly en conteneur et comprendre sa structure", "Configurer module Oracle, pilote et datasource par jboss-cli", "Déployer et redéployer une application"],
 [("Lancer et explorer", DK, r"""# docker-compose.yml (extrait)
wildfly:
  image: quay.io/wildfly/wildfly:26.1.3.Final-jdk17        # version de l'existant ; la montée de version est au chapitre 4
  command: ["/opt/jboss/wildfly/bin/standalone.sh", "-b", "0.0.0.0", "-bmanagement", "0.0.0.0", "-c", "standalone-full.xml"]
  ports: ["8080:8080", "9990:9990"]
  environment: { DB_PASSWORD: "${DB_PASSWORD}" }
oracle:
  image: gvenzl/oracle-free:23-slim
  environment: { ORACLE_PASSWORD: "${ORACLE_PASSWORD}", APP_USER: crise, APP_USER_PASSWORD: "${DB_PASSWORD}" }
# structure : bin/ (scripts, jboss-cli), standalone/configuration/ (standalone*.xml), standalone/deployments/, standalone/log/, modules/"""),
  ("Module, pilote et datasource Oracle", "Le pilote Oracle est déclaré comme module, puis comme pilote JDBC, puis la datasource est créée avec validation des connexions et tri des exceptions propres à Oracle. Le script est idempotent : il ne crée que ce qui n'existe pas.", r"""# datasource-oracle.cli — lancé par : jboss-cli.sh --connect --file=datasource-oracle.cli
if (outcome != success) of /subsystem=datasources/jdbc-driver=oracle:read-resource
  module add --name=com.oracle --resources=/opt/drivers/ojdbc11.jar --dependencies=javax.api,javax.transaction.api
  /subsystem=datasources/jdbc-driver=oracle:add(driver-name=oracle,driver-module-name=com.oracle,driver-class-name=oracle.jdbc.OracleDriver)
end-if
if (outcome != success) of /subsystem=datasources/data-source=CriseDS:read-resource
  data-source add --name=CriseDS --jndi-name=java:jboss/datasources/CriseDS --driver-name=oracle \
    --connection-url=jdbc:oracle:thin:@//oracle:1521/FREEPDB1 --user-name=crise --password=${env.DB_PASSWORD} \
    --min-pool-size=5 --max-pool-size=30 --validate-on-match=true --background-validation=false \
    --valid-connection-checker-class-name=org.jboss.jca.adapters.jdbc.extensions.oracle.OracleValidConnectionChecker \
    --exception-sorter-class-name=org.jboss.jca.adapters.jdbc.extensions.oracle.OracleExceptionSorter --statistics-enabled=true
end-if
/subsystem=datasources/data-source=CriseDS:test-connection-in-pool
# production : mot de passe dans un magasin d'identifiants Elytron plutôt qu'en variable d'environnement"""),
  ("Déployer", "", r"""jboss-cli.sh --connect --command="deploy /tmp/crise.war --force"          # déployer ou remplacer
jboss-cli.sh --connect --command="deployment-info"                        # état des déploiements
jboss-cli.sh --connect --command="undeploy crise.war"                     # retirer
# mode domaine : deploy crise.war --server-groups=groupe-production
# configuration hors ligne (construction d'image) : embed-server --server-config=standalone-full.xml, puis les mêmes commandes""")],
 [("Pourquoi ne jamais modifier standalone.xml à la main en production ?", "Parce que la modification n'est ni tracée, ni rejouable, ni identique en intégration : on écrit un script jboss-cli versionné, joué d'abord en intégration puis en production, ce qui garantit des environnements ISO et un retour arrière possible."),
  ("Question d'entretien : mode autonome ou domaine ?", "Autonome : chaque serveur a sa configuration, simple, adapté aux conteneurs et à l'automatisation. Domaine : un contrôleur central gère profils et groupes de serveurs, pratique pour beaucoup de serveurs identiques sur machines virtuelles. Beaucoup d'organisations restent en autonome, industrialisé par scripts.")],
 ("WildFly configuré par script", ["WildFly 26 et Oracle Free en Compose ; script jboss-cli idempotent pour le module, le pilote et la datasource.", "Déployer l'application CrisisShield legacy et tester la connexion du pool.", "Rejouer le script deux fois et prouver qu'il ne change rien la seconde fois."],
  "Attendu : la datasource répond à test-connection-in-pool ; la seconde exécution du script ne modifie rien ; toute la configuration est dans le dépôt, aucun réglage manuel.")),

ch("WildFly (2) : exploiter, diagnostiquer, sécuriser, migrer", 's',
 ["Exploiter, c'est démarrer et arrêter proprement, lire les journaux, suivre les pools, les fils d'exécution et la mémoire, et savoir quoi faire quand l'application ralentit.", "Le diagnostic s'appuie sur des preuves : statistiques des pools, vidage des fils d'exécution (thread dump), vidage mémoire (heap dump), journaux du ramasse-miettes.", "Sécuriser (Elytron, TLS, console d'administration protégée) et migrer : WildFly 26 est la dernière version en Jakarta EE 8 (javax), les suivantes passent à jakarta, ce qui impacte directement Struts 1."],
 ["Démarrer, arrêter et superviser WildFly", "Diagnostiquer lenteurs, blocages et fuites", "Sécuriser le serveur et préparer la montée de version"],
 [("Exploiter et superviser", "", r"""jboss-cli.sh --connect --command=":shutdown(timeout=60)"                 # arrêt gracieux : les requêtes en cours finissent
jboss-cli.sh --connect --command=":reload"                                 # recharger la configuration
tail -F /opt/jboss/wildfly/standalone/log/server.log | grep -E "ERROR|WARN"
# pool de connexions : actives, disponibles, attente maximale
/subsystem=datasources/data-source=CriseDS/statistics=pool:read-resource(include-runtime=true)
# journaux : rotation par taille, niveau par catégorie
/subsystem=logging/size-rotating-file-handler=APP:add(file={path=crise.log,relative-to=jboss.server.log.dir},rotate-size=50m,max-backup-index=10)
/subsystem=logging/logger=fr.crise:add(level=INFO,handlers=[APP])"""),
  ("Diagnostiquer", "", T([
    ("Requêtes qui ne répondent plus", "pool épuisé (ActiveCount = MaxPoolSize), connexions non rendues", "thread dump, statistiques du pool, requêtes longues côté Oracle"),
    ("Lenteur progressive puis OutOfMemoryError", "fuite mémoire, sessions HTTP trop lourdes", "heap dump analysé (Eclipse MAT), journaux du GC"),
    ("Pics de CPU", "boucle, GC trop fréquent, expressions régulières", "thread dump répété, jcmd, JFR"),
    ("Démarrage en échec", "datasource injoignable, déploiement invalide", "server.log au démarrage, deployment-info"),
    ("Erreurs après mise en production", "configuration différente de l'intégration", "comparaison des configurations (chapitre 5)")], ("Symptôme", "Cause fréquente", "Preuve à collecter"))),
  ("Sécuriser et migrer", "Console d'administration sur un réseau d'administration, utilisateurs de gestion nominatifs, TLS via Elytron, secrets dans un magasin d'identifiants. Migration : WildFly 27 et suivants sont en Jakarta EE 10 (paquets jakarta.*) ; une application Struts 1 (javax.servlet) n'y tourne pas sans transformation : on choisit entre rester sur une base javax supportée, transformer les binaires, ou migrer la couche web.", r"""jcmd $(pgrep -f jboss-modules) Thread.print > fils.txt                        # vidage des fils d'exécution
jcmd $(pgrep -f jboss-modules) GC.heap_dump /tmp/crise.hprof                   # vidage mémoire (attention au volume)
# magasin d'identifiants Elytron pour le mot de passe de la base
/subsystem=elytron/credential-store=cs:add(location=cs.jceks,relative-to=jboss.server.config.dir,credential-reference={clear-text=${env.CS_PASSWORD}},create=true)
/subsystem=elytron/credential-store=cs:add-alias(alias=crise-db,secret-value=${env.DB_PASSWORD})
# migration : inventaire des javax.* (jdeps), Eclipse Transformer ou OpenRewrite pour javax → jakarta, tests complets""")],
 [("À 9 h, les utilisateurs signalent des pages qui tournent sans fin ; le serveur est « up ». Démarche ?", "Regarder les statistiques du pool (probablement épuisé), prendre deux ou trois vidages des fils d'exécution à quelques secondes d'intervalle pour voir où ils attendent, vérifier côté Oracle les sessions bloquées ou les requêtes longues ; soulager (tuer la requête bloquante, recharger si nécessaire) puis corriger la cause (connexion non rendue, index manquant)."),
  ("Question d'entretien : que change le passage de WildFly 26 à 27 et plus ?", "Le passage de Jakarta EE 8 à Jakarta EE 10 : les paquets javax.* deviennent jakarta.*. Toute dépendance restée en javax (comme Struts 1) ne fonctionne plus telle quelle ; la migration se prépare par un inventaire (jdeps), une transformation (Eclipse Transformer, OpenRewrite) et des tests complets en intégration.")],
 ("Incident de pool et plan de migration", ["Provoquer une fuite de connexions dans l'application, observer le pool, prendre des thread dumps et trouver la cause.", "Sécuriser : TLS, console protégée, magasin d'identifiants Elytron pour le mot de passe de la base.", "Plan de migration WildFly 26 → 31 : inventaire javax, options, risques, étapes, retour arrière."],
  "Attendu : la cause de la fuite est prouvée par les dumps ; aucun mot de passe en clair dans la configuration ; le plan de migration identifie Struts 1 comme point bloquant et propose trois options chiffrées.")),

ch("Environnements ISO et mise en production", 's',
 ["Un environnement ISO a la même configuration que la production, à l'exception de valeurs propres documentées (adresses, mots de passe, tailles) : tout le reste est identique et vérifiable.", "Le mode opératoire de mise en production est joué et validé en intégration, puis rejoué tel quel en production : mêmes scripts, même ordre, mêmes contrôles.", "Chaque mise en production a une fenêtre, une check-list, des contrôles après installation, un retour arrière prêt, et une communication aux parties prenantes."],
 ["Garantir l'ISO entre intégration et production", "Écrire un mode opératoire rejouable et vérifiable", "Conduire une mise en production avec contrôles et retour arrière"],
 [("Vérifier l'ISO", "On exporte la configuration de chaque environnement dans le même format, on remplace les valeurs propres par des variables, puis on compare : toute différence non documentée est un écart à corriger avant la mise en production.", r"""# export de la configuration WildFly (sous-systèmes utiles) de chaque environnement
for env in integration production; do
  jboss-cli.sh --controller=wildfly-$env:9990 --connect --command="/subsystem=datasources:read-resource(recursive=true)" > ds-$env.txt
done
sed -E 's/(integration|production)//g; s/password=.*$/password=***/' ds-integration.txt > a.txt
sed -E 's/(integration|production)//g; s/password=.*$/password=***/' ds-production.txt > b.txt
diff -u a.txt b.txt && echo "ISO : aucune différence non documentée"
# versions : application, WildFly, Java, pilote Oracle relevées dans la fiche de version"""),
  ("Le mode opératoire", "", T([
    ("Avant", "fiche de version, validation en intégration, sauvegarde, fenêtre et interlocuteurs confirmés", "go ou pas go"),
    ("Arrêt", "arrêt de l'ordonnancement concerné, arrêt gracieux du serveur", "traitements suspendus"),
    ("Installation", "scripts jboss-cli, scripts SQL numérotés, déploiement de l'artefact versionné", "journal d'installation"),
    ("Contrôles", "démarrage, test de connexion, parcours de recette rapide, journaux sans erreur", "procès-verbal de contrôles"),
    ("Reprise", "relance de l'ordonnancement, surveillance renforcée", "traitements repris"),
    ("Retour arrière", "artefact précédent, scripts SQL inverses ou restauration, décision tracée", "critères de déclenchement écrits"),
    ("Communication", "début, fin, résultat, points d'attention", "mail aux parties prenantes")], ("Étape", "Contenu", "Preuve"))),
  ("La communication", "", "texte::Objet : [Mise en production] Application — version 4.12.0 — jeudi 2 octobre, 20 h 00 à 22 h 00\n\nBonjour,\n\nLa version 4.12.0 sera installée en production jeudi de 20 h à 22 h (fenêtre validée).\nContenu : correction de trois anomalies (tickets APP-812, APP-815, APP-820) et mise à jour de sécurité du pilote Oracle.\nImpact : application indisponible pendant la fenêtre ; traitements de nuit décalés à 22 h 30.\nValidation : version installée et contrôlée en intégration le 29/09 (procès-verbal joint).\nRetour arrière : prêt, version 4.11.3, décision au plus tard à 21 h 30.\n\nUn message de fin d'intervention suivra.")],
 [("En production, la datasource a une taille de pool maximale de 20, contre 50 en intégration. Est-ce un écart ISO ?", "Oui, sauf si c'est une valeur propre documentée et justifiée (dimensionnement). Sinon, les tests de charge en intégration ne valent rien pour la production : on aligne, ou on documente la différence et on refait le test avec la valeur de production."),
  ("Question d'entretien : comment garantis-tu qu'une installation en production se passera comme en intégration ?", "Mêmes artefacts versionnés, mêmes scripts jouant la configuration, même ordre, environnements comparés automatiquement avant la mise en production, contrôles écrits après installation, et retour arrière préparé avec des critères de déclenchement.")],
 ("Mise en production simulée", ["Deux environnements WildFly + Oracle en Compose (intégration, production) configurés par les mêmes scripts.", "Comparaison automatique des configurations ; introduire un écart et le détecter.", "Jouer une mise en production complète avec check-list, contrôles, retour arrière déclenché puis mail de fin."],
  "Attendu : l'écart introduit est détecté avant l'installation ; le retour arrière ramène la version précédente en moins de quinze minutes ; le procès-verbal et les deux mails sont prêts à l'emploi.")),

ch("Ordonnancement de production : chaînes, vérification matinale, incidents", 's',
 ["L'ordonnanceur (Control-M, VTOM, Dollar Universe, IBM Workload Scheduler, Autosys…) enchaîne les traitements selon des dépendances, des calendriers, des fenêtres et des ressources.", "Chaque traitement ordonnancé suit des conventions : un code retour explicite, des journaux lisibles, une reprise possible sans doublon.", "Chaque matin, le Tech Lead vérifie le déroulement de la nuit en production puis en intégration, et corrige ou fait corriger avant l'arrivée des utilisateurs."],
 ["Comprendre les concepts communs aux ordonnanceurs", "Écrire des traitements ordonnançables", "Mener la vérification matinale et traiter les incidents"],
 [("Concepts communs", "", T([
    ("Job", "une commande ou un script, avec son code retour", "extraction_incidents.sh"),
    ("Chaîne (ou application, session)", "ensemble de jobs ordonnés", "chaîne de nuit « référentiel puis calculs puis éditions »"),
    ("Dépendance", "un job attend la fin (réussie) d'un autre", "calcul après extraction"),
    ("Condition, événement", "attente d'un fichier ou d'un signal", "fichier du partenaire arrivé"),
    ("Calendrier", "jours d'exécution, jours fériés, fin de mois", "jours ouvrés seulement"),
    ("Fenêtre et heure limite", "plage autorisée, heure de fin attendue", "entre 21 h et 5 h, fin avant 6 h"),
    ("Ressource", "limite de parallélisme ou de verrou", "un seul job sur la base à la fois"),
    ("Reprise", "relance d'un job ou de la suite", "reprise au job en échec")], ("Concept", "Rôle", "Exemple"))),
  ("Un traitement ordonnançable", "Le script échoue clairement (code retour non nul), écrit un journal horodaté, refuse de tourner deux fois en même temps, et se relance sans doublon.", r"""#!/usr/bin/env bash
set -Eeuo pipefail
JOB=extraction_incidents; LOG=/var/log/batch/${JOB}_$(date +%Y%m%d_%H%M%S).log
exec > >(tee -a "$LOG") 2>&1
exec 9>/var/lock/$JOB.lock; flock -n 9 || { echo "$(date -Is) ERREUR déjà en cours"; exit 3; }
trap 'echo "$(date -Is) ERREUR ligne $LINENO"; exit 2' ERR
echo "$(date -Is) DEBUT $JOB date_traitement=${1:?date attendue}"
sqlplus -s -L "crise/${DB_PASSWORD}@//oracle:1521/FREEPDB1" @extraction.sql "$1" || exit 2
n=$(wc -l < /data/sortie/incidents_$1.csv); [ "$n" -gt 1 ] || { echo "$(date -Is) ERREUR fichier vide"; exit 4; }
echo "$(date -Is) FIN $JOB lignes=$n"; exit 0
# codes : 0 succès, 2 erreur technique, 3 déjà en cours, 4 anomalie de données (documentés dans le dossier d'exploitation)"""),
  ("La vérification matinale", "", CK("Check-list de 8 h 00 : production, puis intégration (20 minutes)", ["Plan de la nuit : tous les jobs terminés ? aucun en erreur, en attente ou en retard ?", "Jobs en erreur : code retour, journal, cause probable, relance possible sans risque ?", "Heures limites respectées ? fichiers sortants livrés aux partenaires ?", "Volumes cohérents (nombre de lignes par rapport à la veille) ?", "Serveurs : WildFly démarré, pools sains, espace disque, journaux sans erreur nouvelle", "Base : sauvegarde de la nuit réussie, aucune session bloquante", "Actions : relances effectuées, tickets Jira ouverts, message aux parties prenantes si impact", "Tout écart non expliqué devient un ticket"]))],
 [("Le job de calcul de la nuit a fini en erreur à 3 h ; les éditions qui en dépendent ne sont pas parties. Il est 8 h. Que fais-tu ?", "Je lis le journal et le code retour, je vérifie qu'une relance est sans risque (idempotence, données d'entrée présentes), je relance le calcul puis la suite de la chaîne, je préviens les utilisateurs du retard des éditions, j'ouvre un ticket pour la cause et j'ajoute le cas à la check-list s'il est nouveau."),
  ("Question d'entretien : qu'est-ce qu'un bon traitement ordonnancé ?", "Un traitement qui renvoie un code retour fiable et documenté, écrit un journal exploitable, ne peut pas tourner deux fois en même temps, se relance sans effet de bord, contrôle ses volumes, et dont la conduite à tenir en cas d'échec est écrite.")],
 ("Une nuit de traitements", ["Rundeck en conteneur (outil libre proche des ordonnanceurs du marché) : chaîne de quatre jobs avec dépendances, heure limite et notification.", "Scripts conformes aux conventions (codes retour, verrou, journal, contrôle de volume).", "Simuler trois incidents (job en erreur, fichier vide, dépassement d'horaire) et dérouler la vérification matinale."],
  "Attendu : chaque incident est détecté par la check-list et traité en moins de quinze minutes ; les relances ne créent aucun doublon ; un compte rendu matinal type est rédigé.")),

ch("Unix, Bash et PowerShell pour l'exploitation", 's',
 ["Le niveau expert en scripts d'exploitation, c'est écrire des scripts robustes (mode strict, pièges d'erreur, verrous, journaux, codes retour) et diagnostiquer vite un serveur.", "Les commandes de diagnostic reviennent toujours : processus, mémoire, disques, réseau, journaux, services ; on les connaît par cœur.", "Côté Windows, PowerShell manipule des objets : services, tâches planifiées, journaux d'événements, administration à distance."],
 ["Écrire des scripts Bash de qualité production", "Diagnostiquer un serveur Unix en quelques minutes", "Administrer services et journaux Windows avec PowerShell"],
 [("Diagnostic en cinq minutes", "", r"""uptime; free -h; df -h; df -i                                  # charge, mémoire, disques, inodes
ps aux --sort=-%cpu | head; ps aux --sort=-%mem | head          # processus gourmands
systemctl status wildfly; journalctl -u wildfly --since "1 hour ago" -p err
ss -tlnp; ss -tn state established '( dport = :1521 )' | wc -l  # ports ouverts, connexions vers Oracle
lsof -p $(pgrep -f jboss-modules) | wc -l                        # descripteurs ouverts par WildFly
find /var/log -type f -size +500M -mmin -60                      # fichiers qui grossissent vite
strace -f -p <pid> -e trace=network -o trace.txt                 # appels système réseau d'un processus bloqué
tcpdump -i any port 1521 -c 50                                   # trafic vers la base (avec autorisation)"""),
  ("Des scripts robustes", "Mode strict, piège sur erreur, options analysées avec getopts, fonctions, journal horodaté, mode essai à blanc, et ShellCheck en CI ; les tests se font avec bats.", r"""#!/usr/bin/env bash
set -Eeuo pipefail; IFS=$'\n\t'
usage(){ echo "usage : $0 -d DOSSIER [-j JOURS] [-n]"; exit 1; }
JOURS=30; ESSAI=0
while getopts "d:j:nh" o; do case $o in d) DOSSIER=$OPTARG;; j) JOURS=$OPTARG;; n) ESSAI=1;; *) usage;; esac; done
[ -d "${DOSSIER:-}" ] || usage
log(){ printf '%s %s\n' "$(date -Is)" "$*"; }
while IFS= read -r -d '' f; do
  if [ $ESSAI -eq 1 ]; then log "à supprimer : $f"; else rm -- "$f" && log "supprimé : $f"; fi
done < <(find "$DOSSIER" -type f -name '*.log' -mtime +"$JOURS" -print0)
# CI : docker run --rm -v "$PWD:/mnt" koalaman/shellcheck:stable scripts/*.sh"""),
  ("PowerShell", "PowerShell manipule des objets et non du texte : on filtre, trie et exporte sans analyse de chaînes. Pour s'entraîner en conteneur, l'image PowerShell tourne sous Linux ; les commandes propres à Windows (services, journaux d'événements) se testent sur une machine Windows.", r"""Get-Service -Name 'Wildfly*' | Where-Object Status -ne 'Running' | Restart-Service -PassThru
Get-WinEvent -FilterHashtable @{LogName='Application'; Level=2; StartTime=(Get-Date).AddHours(-12)} |
  Select-Object TimeCreated, ProviderName, Message -First 20
Get-ScheduledTask -TaskPath '\Crise\' | Get-ScheduledTaskInfo | Where-Object LastTaskResult -ne 0
Invoke-Command -ComputerName srv-app-01, srv-app-02 -ScriptBlock { Get-PSDrive C | Select-Object Used, Free }
Get-ChildItem D:\logs -Filter *.log | Where-Object LastWriteTime -lt (Get-Date).AddDays(-30) | Remove-Item -WhatIf
# entraînement : docker run --rm -it mcr.microsoft.com/powershell pwsh""")],
 [("Un script de purge a supprimé des fichiers hors du dossier prévu. Quelles protections ont manqué ?", "Le mode strict (variable vide non détectée : rm -rf \"$DOSSIER/\"*), la vérification que le dossier existe et est celui attendu, le mode essai à blanc, la recherche avec -print0 et la suppression fichier par fichier journalisée, et ShellCheck qui signale ces risques."),
  ("Question d'entretien : que regardes-tu en premier sur un serveur qui rame ?", "Charge et CPU (uptime, top), mémoire et échange, espace disque et inodes, entrées-sorties, processus gourmands, journaux récents du service, connexions réseau vers les dépendances ; en quelques minutes on sait si c'est la machine, l'application ou une dépendance.")],
 ("Boîte à outils d'exploitation", ["Trois scripts Bash robustes (purge, contrôle d'espace disque, relance contrôlée de WildFly) avec tests bats et ShellCheck.", "Un script de diagnostic en cinq minutes qui produit un rapport horodaté.", "Deux scripts PowerShell (services et journaux d'événements) testés en conteneur pour la partie portable."],
  "Attendu : ShellCheck ne signale rien ; le mode essai à blanc est présent partout où l'on supprime ; le rapport de diagnostic suffit à décider en moins de cinq minutes.")),

ch("Oracle : SQL, PL/SQL et diagnostic", 's',
 ["Le Tech Lead lit et écrit du SQL avancé, comprend le PL/SQL de l'application (procédures, packages, déclencheurs) et sait diagnostiquer une lenteur ou un blocage.", "Les vues dynamiques (v$session, v$sql) montrent qui fait quoi et qui bloque qui ; DBMS_XPLAN affiche le plan réel d'une requête.", "Data Pump exporte et importe un schéma ; les scripts SQL de livraison sont numérotés, rejouables et accompagnés de leur retour arrière."],
 ["Écrire du SQL et du PL/SQL propres à Oracle", "Diagnostiquer sessions, verrous et requêtes lentes", "Livrer des scripts SQL sûrs et manipuler Data Pump"],
 [("PL/SQL de production", "Un package regroupe les traitements ; BULK COLLECT et FORALL traitent par lots au lieu de ligne à ligne ; les exceptions sont journalisées puis relancées.", r"""CREATE OR REPLACE PACKAGE BODY crise_purge AS
  PROCEDURE purger_incidents(p_avant IN DATE, p_nb OUT NUMBER) IS
    TYPE t_ids IS TABLE OF incident.id%TYPE;
    v_ids t_ids;
    CURSOR c IS SELECT id FROM incident WHERE statut = 'CLOS' AND date_cloture < p_avant;
  BEGIN
    p_nb := 0;
    OPEN c;
    LOOP
      FETCH c BULK COLLECT INTO v_ids LIMIT 5000;
      EXIT WHEN v_ids.COUNT = 0;
      FORALL i IN 1 .. v_ids.COUNT DELETE FROM incident_evenement WHERE incident_id = v_ids(i);
      FORALL i IN 1 .. v_ids.COUNT DELETE FROM incident WHERE id = v_ids(i);
      p_nb := p_nb + SQL%ROWCOUNT;
      COMMIT;                                                   -- validation par lot : reprise possible
    END LOOP;
    CLOSE c;
  EXCEPTION
    WHEN OTHERS THEN
      journal_erreur('crise_purge.purger_incidents', SQLERRM);   -- procédure autonome de journalisation
      RAISE;
  END purger_incidents;
END crise_purge;"""),
  ("Diagnostiquer", "", r"""-- sessions actives et qui bloque qui
SELECT sid, serial#, username, status, event, blocking_session, sql_id, seconds_in_wait
FROM v$session WHERE username IS NOT NULL AND status = 'ACTIVE' ORDER BY seconds_in_wait DESC;
-- plan réel d'une requête lente (après exécution)
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR('&sql_id', NULL, 'ALLSTATS LAST'));
-- requêtes les plus coûteuses depuis le démarrage
SELECT sql_id, executions, ROUND(elapsed_time/1e6) s, SUBSTR(sql_text, 1, 80) FROM v$sql ORDER BY elapsed_time DESC FETCH FIRST 10 ROWS ONLY;
-- statistiques à jour ?
SELECT table_name, last_analyzed, num_rows FROM user_tables ORDER BY last_analyzed NULLS FIRST;"""),
  ("Livrer et sauvegarder", "Chaque livraison SQL est un script numéroté (V4_12_0__…), idempotent quand c'est possible, testé en intégration, avec son script inverse ; Flyway ou Liquibase tiennent l'historique. Data Pump sauvegarde un schéma avant une opération risquée.", r"""expdp crise/"$DB_PASSWORD"@//oracle:1521/FREEPDB1 schemas=CRISE directory=DATA_PUMP_DIR dumpfile=crise_avant_4_12.dmp logfile=crise_exp.log
impdp crise/"$DB_PASSWORD"@//oracle:1521/FREEPDB1 schemas=CRISE directory=DATA_PUMP_DIR dumpfile=crise_avant_4_12.dmp remap_schema=CRISE:CRISE_COPIE
# entraînement : docker run -d -p 1521:1521 -e ORACLE_PASSWORD=… gvenzl/oracle-free:23-slim""")],
 [("La purge de nuit tourne depuis cinq heures au lieu de vingt minutes. Démarche ?", "Regarder dans v$session ce qu'elle attend (verrou, entrée-sortie), son plan réel avec DBMS_XPLAN (index manquant sur incident_evenement.incident_id ?), la présence d'une session bloquante ; puis corriger (index, traitement par lots, statistiques) et tester en intégration avant la nuit suivante."),
  ("Question d'entretien : pourquoi BULK COLLECT et FORALL ?", "Pour traiter par lots et réduire les allers-retours entre les moteurs PL/SQL et SQL : on gagne souvent un ordre de grandeur sur les gros volumes ; la clause LIMIT borne la mémoire, et une validation par lot permet la reprise.")],
 ("Oracle au quotidien", ["Oracle Free en conteneur ; package de purge avec BULK COLLECT, FORALL et journalisation.", "Provoquer un blocage entre deux sessions et une requête lente ; les diagnostiquer avec v$session et DBMS_XPLAN.", "Script de livraison numéroté avec retour arrière, sauvegarde Data Pump avant exécution."],
  "Attendu : la session bloquante est identifiée en moins de deux minutes ; la requête lente est corrigée preuve à l'appui (plan avant et après) ; le script inverse ramène exactement l'état initial.")),

ch("Java 17 et plus : langage, JVM et migration", 's',
 ["Java 17 (et 21) apporte records, classes scellées, pattern matching, blocs de texte et une meilleure JVM ; savoir les utiliser et les expliquer est attendu au niveau avancé.", "La JVM se règle et se diagnostique : ramasse-miettes G1 ou ZGC, mémoire adaptée au conteneur, Java Flight Recorder, jcmd.", "Migrer de Java 8 ou 11 vers 17 ou 21, c'est inventorier les API retirées et internes, mettre à jour les dépendances, et outiller la transformation (jdeps, jdeprscan, OpenRewrite)."],
 ["Utiliser les apports du langage de Java 17 à 21", "Régler et diagnostiquer la JVM", "Conduire une migration de version de Java"],
 [("Le langage moderne", "", r'''public record Incident(long id, String zone, Gravite gravite) {
  public Incident { Objects.requireNonNull(zone); }                    // validation dans le constructeur compact
}
public sealed interface Evenement permits Declare, Escalade, Clos {}
public record Declare(long id) implements Evenement {}
public record Escalade(long id, int niveau) implements Evenement {}
public record Clos(long id) implements Evenement {}
String libelle(Evenement e) {
  return switch (e) {                                                  // exhaustif grâce à sealed (Java 21)
    case Declare d  -> "déclaré " + d.id();
    case Escalade s -> "escaladé au niveau " + s.niveau();
    case Clos c     -> "clos " + c.id();
  };
}
String requete = """
    SELECT id, zone FROM incident
    WHERE statut = 'OUVERT'
    """;'''),
  ("La JVM", "", r"""JAVA_OPTS="-XX:+UseG1GC -XX:MaxRAMPercentage=75 -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/dumps \
  -Xlog:gc*:file=/logs/gc.log:time,uptime:filecount=5,filesize=20m"
jcmd <pid> VM.flags ; jcmd <pid> GC.heap_info ; jcmd <pid> Thread.print
jcmd <pid> JFR.start duration=120s filename=/tmp/crise.jfr        # enregistrement de deux minutes, analysé dans JDK Mission Control"""),
  ("Migrer", "", T([
    ("Inventorier", "jdeps --jdk-internals, jdeprscan --release 17", "liste des API internes et retirées"),
    ("Mettre à jour les dépendances", "versions compatibles Java 17 (bibliothèques, plugins Maven)", "build vert"),
    ("Transformer", "OpenRewrite (recettes de migration), corrections à la main", "code compilé en 17"),
    ("Tester", "tests unitaires, d'intégration, de charge en intégration", "mêmes résultats qu'avant"),
    ("Déployer", "JVM 17 en intégration, puis production, retour arrière prêt", "production sur Java 17")], ("Étape", "Outils", "Preuve")))],
 [("Après passage à Java 17, une bibliothèque lève InaccessibleObjectException. Pourquoi, et que faire ?", "Java 17 encapsule fortement les API internes du JDK : la bibliothèque utilise la réflexion sur un paquet interne. On la met à jour (solution durable) ; à défaut, on ouvre le paquet précis avec --add-opens, documenté comme dette à résorber."),
  ("Question d'entretien : que t'apportent les records et les classes scellées ?", "Les records réduisent les objets de données à une ligne, immuables, avec equals et hashCode corrects ; les classes scellées ferment une hiérarchie, ce qui rend les switch exhaustifs et vérifiés par le compilateur. Le code est plus court et plus sûr.")],
 ("Migration Java 11 → 17 d'un module", ["Inventaire jdeps et jdeprscan sur le module legacy de CrisisShield.", "Mise à jour des dépendances, recettes OpenRewrite, compilation et tests en Java 17.", "Réglages JVM pour le conteneur, enregistrement JFR sous charge, comparaison avant et après."],
  "Attendu : le module compile et passe ses tests en Java 17 ; aucune option --add-opens non documentée ; le rapport compare temps de réponse et mémoire avant et après.")),

ch("Struts 1, Spring et Hibernate dans l'existant", 's',
 ["Struts 1 est en fin de support depuis 2013 : on doit savoir le lire (struts-config.xml, Actions, ActionForms, Validator, Tiles), le maintenir, et réduire ses risques de sécurité connus.", "Spring apporte l'injection de dépendances et les transactions ; les pièges classiques sont l'appel interne qui contourne le proxy transactionnel et les transactions trop longues.", "Hibernate masque le SQL : il faut surveiller les requêtes générées (N+1), les sessions ouvertes trop longtemps, et les mappings hérités en hbm.xml."],
 ["Lire et maintenir une application Struts 1", "Éviter les pièges de Spring et d'Hibernate", "Réduire les risques de Struts 1 et préparer sa sortie"],
 [("Lire Struts 1", "", r"""<!-- struts-config.xml -->
<form-beans>
  <form-bean name="incidentForm" type="fr.crise.web.IncidentForm"/>
</form-beans>
<action-mappings>
  <action path="/incident/enregistrer" type="fr.crise.web.EnregistrerIncidentAction"
          name="incidentForm" scope="request" validate="true" input="/incident/saisie.jsp">
    <forward name="succes" path="/incident/liste.do" redirect="true"/>
  </action>
</action-mappings>
<plug-in className="org.apache.struts.validator.ValidatorPlugIn">
  <set-property property="pathnames" value="/WEB-INF/validator-rules.xml,/WEB-INF/validation.xml"/>
</plug-in>
// l'Action délègue au service Spring, jamais de logique métier dans la couche web
public ActionForward execute(ActionMapping m, ActionForm f, HttpServletRequest req, HttpServletResponse res) {
  incidentService.enregistrer(((IncidentForm) f).versCommande());
  return m.findForward("succes");
}"""),
  ("Réduire les risques de Struts 1", "Des vulnérabilités connues ne seront jamais corrigées (par exemple la manipulation du chargeur de classes par un paramètre « class » des ActionForms, CVE-2014-0114). On filtre en entrée ce qui n'est pas attendu, on durcit, on surveille, et on planifie la sortie écran par écran.", r"""// filtre de servlet : rejeter tout paramètre qui vise la classe ou le chargeur de classes
public void doFilter(ServletRequest rq, ServletResponse rs, FilterChain c) throws IOException, ServletException {
  for (String p : Collections.list(rq.getParameterNames()))
    if (p.matches("(?i)(.*\\.|^)class(\\..*|$)")) { ((HttpServletResponse) rs).sendError(400); return; }
  c.doFilter(rq, rs);
}
// + WAF en amont, Validator strict, mises à jour de commons-beanutils, analyse de dépendances en CI
// sortie : écrans migrés un par un vers Spring MVC derrière les mêmes URL (étranglement)"""),
  ("Spring et Hibernate : les pièges", "", T([
    ("Appel interne à une méthode @Transactional", "le proxy est contourné : pas de transaction", "appeler par un autre bean, ou revoir le découpage"),
    ("Transaction trop longue", "verrous tenus, pool bloqué", "transactions courtes, pas d'appel réseau dedans"),
    ("N+1 Hibernate", "une requête par ligne affichée", "fetch join, batch-size, projection"),
    ("LazyInitializationException", "session fermée avant l'accès", "charger ce qu'il faut dans le service"),
    ("hbm.xml et annotations mélangés", "mappings incohérents", "un seul style par entité, tests de mapping"),
    ("Cache de second niveau mal réglé", "données périmées affichées", "cache réservé aux référentiels, expiration")], ("Piège", "Effet", "Parade")))],
 [("Une méthode enregistrer() annotée @Transactional appelle this.journaliser(), elle aussi @Transactional(REQUIRES_NEW). Le journal disparaît avec le rollback. Pourquoi ?", "L'appel via this ne passe pas par le proxy Spring : l'annotation de journaliser() est ignorée et tout tourne dans la même transaction. On déplace journaliser() dans un autre bean, appelé via le proxy."),
  ("Question d'entretien : que proposes-tu pour une application Struts 1 en production ?", "À court terme, réduire le risque : filtres d'entrée contre les vulnérabilités connues, WAF, dépendances à jour, surveillance. À moyen terme, sortir par étapes : écrans migrés vers Spring MVC derrière les mêmes URL, services Spring réutilisés, tests de caractérisation avant chaque écran.")],
 ("Maintenir et sécuriser la couche web legacy", ["Ajouter un écran Struts 1 complet (form-bean, action, validation, forward) qui délègue à un service Spring.", "Mettre le filtre contre la manipulation du chargeur de classes et le prouver par un test.", "Trouver et corriger un N+1 Hibernate et un piège transactionnel Spring."],
  "Attendu : l'écran fonctionne et valide ses entrées ; la requête avec class.classLoader est refusée (400) ; le nombre de requêtes SQL de l'écran liste passe de N+1 à 2.")),

ch("XML et services web SOAP et REST", 'c',
 ["XML reste partout dans ce type de contexte : configurations, échanges avec les partenaires, services SOAP ; il faut le valider (XSD), l'interroger (XPath), le transformer (XSLT).", "Un analyseur XML mal configuré est vulnérable (XXE : lecture de fichiers, requêtes internes) : on désactive les entités externes par défaut.", "SOAP décrit ses contrats en WSDL (Apache CXF ou l'implémentation de WildFly), REST en OpenAPI ; les deux se testent avec des outils comme SoapUI et des tests automatisés."],
 ["Valider, interroger et transformer du XML", "Configurer un analyseur XML sans XXE", "Consommer et exposer des services SOAP et REST"],
 [("Valider et interroger", "", r"""SchemaFactory sf = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
sf.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, ""); sf.setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");
Validator v = sf.newSchema(new File("incident.xsd")).newValidator();
v.validate(new StreamSource(new File("incident.xml")));                 // lève une exception si invalide
XPath xp = XPathFactory.newInstance().newXPath();
String zone = xp.evaluate("/incident/localisation/zone", doc);
# en ligne de commande : xmllint --noout --schema incident.xsd incident.xml ; xmllint --xpath '//zone/text()' incident.xml"""),
  ("Sans XXE", "", r"""DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);   // refuse tout DOCTYPE
f.setFeature("http://xml.org/sax/features/external-general-entities", false);
f.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
f.setXIncludeAware(false); f.setExpandEntityReferences(false);
// attaque type : <!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><incident>&e;</incident>"""),
  ("SOAP et REST", "", r"""// SOAP (Jakarta XML Web Services ; javax.jws sous WildFly 26) : contrat publié en WSDL
@WebService(serviceName = "IncidentService", targetNamespace = "urn:crise:incidents:v1")
public class IncidentSoap {
  @WebMethod public IncidentDto lire(@WebParam(name = "id") long id) { return service.lire(id); }
}
// client : wsimport ou cxf-codegen-plugin génère les classes depuis le WSDL ; délais configurés sur le client
// REST (JAX-RS, RESTEasy dans WildFly)
@Path("/v1/incidents") @Produces(MediaType.APPLICATION_JSON)
public class IncidentRest {
  @GET @Path("{id}") public IncidentDto lire(@PathParam("id") long id) { return service.lire(id); }
}
# tests : SoapUI (projets versionnés), ou tests d'intégration avec Testcontainers et un WildFly de test""")],
 [("Un partenaire envoie un XML contenant un DOCTYPE avec une entité SYSTEM. Que doit faire l'application ?", "Le refuser : l'analyseur est configuré pour interdire les DOCTYPE (disallow-doctype-decl) ; sinon, l'entité pourrait lire un fichier du serveur ou appeler une adresse interne (XXE). On journalise l'événement comme tentative suspecte."),
  ("Question d'entretien : SOAP ou REST pour un nouvel échange ?", "REST et JSON pour la plupart des nouveaux échanges, plus simples ; SOAP reste pertinent quand le partenaire l'impose, ou quand on a besoin de contrats stricts et de WS-Security. Dans l'existant, on maintient SOAP proprement plutôt que de tout réécrire.")],
 ("Échanges XML sûrs", ["Valider un flux XML d'incidents par XSD, en extraire des valeurs par XPath, le transformer en CSV par XSLT.", "Analyseur durci : prouver que l'attaque XXE échoue.", "Exposer le même service en SOAP et en REST sur WildFly ; tests SoapUI et test d'intégration."],
  "Attendu : un XML invalide est rejeté avec un message clair ; la charge XXE est refusée et journalisée ; les deux services renvoient les mêmes données.")),

ch("CI/CD et barrière qualité : GitLab CI, Jenkins, SonarQube", 's',
 ["La chaîne du CDS construit, teste, analyse (SonarQube, dépendances) et publie un artefact versionné ; le déploiement en intégration est automatisé, la production reste déclenchée et tracée.", "La barrière qualité SonarQube porte sur le nouveau code : couverture, duplications, fiabilité, sécurité, points sensibles revus ; un livrable qui ne la passe pas n'est pas accepté.", "Jenkins reste courant à côté de GitLab : il faut savoir lire et maintenir un Jenkinsfile, et migrer progressivement si c'est la stratégie."],
 ["Construire une chaîne GitLab CI complète pour une application Java", "Régler et faire respecter la barrière qualité", "Lire et maintenir un pipeline Jenkins"],
 [("GitLab CI", "", r"""stages: [build, test, qualite, paquet, integration, production]
variables: { MAVEN_OPTS: "-Dmaven.repo.local=.m2" }
cache: { key: m2, paths: [.m2/] }
build:   { stage: build, image: "maven:3.9-eclipse-temurin-17", script: ["mvn -B -DskipTests package"], artifacts: { paths: [target/*.war] } }
tests:   { stage: test, image: "maven:3.9-eclipse-temurin-17", script: ["mvn -B verify"], artifacts: { reports: { junit: target/surefire-reports/*.xml } } }
sonar:
  stage: qualite
  image: "maven:3.9-eclipse-temurin-17"
  script: ["mvn -B sonar:sonar -Dsonar.qualitygate.wait=true -Dsonar.host.url=$SONAR_URL -Dsonar.token=$SONAR_TOKEN"]
dependances:
  stage: qualite
  image: "maven:3.9-eclipse-temurin-17"
  script: ["mvn -B org.owasp:dependency-check-maven:check -DfailBuildOnCVSS=7"]
integration:
  stage: integration
  image: "registry.interne/outils-wildfly:26"
  script: ["jboss-cli.sh --controller=$WILDFLY_INT --connect --file=config/integration.cli", "jboss-cli.sh --controller=$WILDFLY_INT --connect --command=\"deploy target/crise.war --force\""]
  environment: { name: integration }
production:
  stage: production
  when: manual
  rules: [ { if: $CI_COMMIT_TAG } ]
  environment: { name: production }
  script: ["./deploiement/production.sh $CI_COMMIT_TAG"]      # même script que l'intégration, mode opératoire tracé"""),
  ("La barrière qualité", "", T([
    ("Couverture du nouveau code", "au moins 80 %", "tests écrits avec la fonctionnalité"),
    ("Lignes dupliquées du nouveau code", "au plus 3 %", "factorisation"),
    ("Fiabilité, sécurité, maintenabilité", "note A sur le nouveau code", "aucun bogue ni vulnérabilité ajoutés"),
    ("Points sensibles de sécurité", "100 % revus", "décision tracée pour chacun"),
    ("Dérogation", "exceptionnelle, écrite, datée", "validée par le Tech Lead")], ("Condition", "Seuil courant", "Ce que cela garantit"))),
  ("Jenkins", "", r"""pipeline {
  agent { docker { image 'maven:3.9-eclipse-temurin-17' } }
  options { timeout(time: 30, unit: 'MINUTES'); buildDiscarder(logRotator(numToKeepStr: '30')) }
  stages {
    stage('Build')   { steps { sh 'mvn -B -DskipTests package' } }
    stage('Tests')   { steps { sh 'mvn -B verify' } post { always { junit 'target/surefire-reports/*.xml' } } }
    stage('Qualité') { steps { withSonarQubeEnv('sonar') { sh 'mvn -B sonar:sonar' } } }
    stage('Barrière'){ steps { timeout(time: 10, unit: 'MINUTES') { waitForQualityGate abortPipeline: true } } }
  }
}""")],
 [("Le CDS livre une version dont la barrière échoue sur la couverture du nouveau code « parce que c'est urgent ». Que fais-tu ?", "Je ne l'accepte pas en l'état sauf dérogation écrite, datée et justifiée par un risque métier réel ; je demande les tests manquants dans un délai court, et je trace la décision dans Jira. Accepter sans cadre revient à supprimer la barrière."),
  ("Question d'entretien : pourquoi la barrière qualité porte-t-elle sur le nouveau code ?", "Parce qu'on ne peut pas exiger de rattraper tout l'existant d'un coup : on garantit que chaque changement est propre, et la dette diminue au fil des modifications. Sur l'existant, on cible les points à risque par un plan séparé.")],
 ("Chaîne complète du CDS", ["GitLab (ou GitLab Runner) et SonarQube en conteneurs ; pipeline build, tests, Sonar avec attente de la barrière, dépendances, intégration automatique, production manuelle.", "Régler la barrière sur le nouveau code ; livrer une modification sans tests et la voir refusée.", "Traduire le pipeline en Jenkinsfile et comparer."],
  "Attendu : la modification sans tests est bloquée par la barrière ; l'intégration se déploie seule ; la production ne part que sur un tag, manuellement, avec le même script.")),

ch("MCS : de l'audit au correctif déployé", 's',
 ["Le maintien en condition de sécurité transforme les alertes des outils d'audit (SonarQube, analyse de dépendances, analyse d'images, tests d'intrusion, scans d'infrastructure) en correctifs livrés et prouvés.", "On trie selon l'exploitabilité réelle : gravité (CVSS), probabilité d'exploitation (EPSS, catalogue des vulnérabilités exploitées), exposition du composant, et disponibilité d'un correctif.", "Chaque vulnérabilité a un ticket, un propriétaire, un délai selon sa gravité, un correctif ou une mesure compensatoire, et une preuve de fermeture."],
 ["Collecter et trier les vulnérabilités de toutes les sources", "Planifier et suivre la remédiation", "Traiter les cas sans correctif (dérogations, mesures compensatoires)"],
 [("Les sources", "", T([
    ("SonarQube", "vulnérabilités et points sensibles du code", "revue et correction par le CDS"),
    ("dependency-check, Trivy", "bibliothèques et images vulnérables", "mise à jour de version"),
    ("Test d'intrusion", "failles exploitables de bout en bout", "correctif applicatif ou de configuration"),
    ("Scans d'infrastructure", "système, middleware, TLS", "correctifs système, WildFly, Java"),
    ("Bulletins de sécurité", "avis des éditeurs (Java, WildFly, Oracle)", "veille et planification")], ("Source", "Ce qu'elle trouve", "Réponse type"))),
  ("Trier et planifier", "", T([("Critique, exploitée ou exposée sur Internet", "72 heures", "correctif ou mesure compensatoire"), ("Critique non exposée, ou élevée exposée", "15 jours", "correctif planifié en urgence"), ("Élevée non exposée, ou moyenne", "prochaine version (60 jours au plus)", "lot de mises à jour"), ("Faible", "avec les évolutions du composant", "suivi"), ("Pour chaque ligne", "ticket Jira avec le label MCS", "composant, version corrigée, propriétaire, date cible, preuve de fermeture")], ("Situation", "Délai (à adapter à la politique)", "Réponse"))),
  ("Sans correctif", "Pour un composant en fin de support (Struts 1) ou un correctif impossible à court terme, on documente une dérogation : risque, mesures compensatoires (filtre, WAF, isolement réseau, surveillance), date de réexamen, validation par le responsable de la sécurité ; la dérogation n'est jamais permanente.", None)],
 [("Un scan remonte 300 vulnérabilités sur l'application. Par où commences-tu ?", "Par le tri : je regroupe par composant (souvent quelques bibliothèques expliquent la majorité), je priorise ce qui est exploité, exposé et critique, je vérifie les faux positifs, puis je planifie des lots de mises à jour testés en intégration ; le reste suit la grille de délai."),
  ("Question d'entretien : comment prouves-tu qu'une vulnérabilité est corrigée ?", "Par un nouveau scan qui ne la remonte plus sur la version déployée, et quand c'est possible par un test qui reproduisait l'exploitation et échoue désormais ; la preuve est jointe au ticket avant sa fermeture.")],
 ("Campagne MCS", ["Lancer dependency-check, Trivy et SonarQube sur le module legacy ; consolider dans un tableau.", "Trier avec la grille, créer les tickets, corriger un lot de dépendances et redéployer en intégration.", "Rédiger une dérogation pour Struts 1 avec mesures compensatoires et date de réexamen."],
  "Attendu : un tableau consolidé sans doublons, trié ; le lot de mises à jour ferme ses vulnérabilités preuve à l'appui ; la dérogation est complète et datée.")),

ch("Piloter un centre de services : revues, livrables, devis, POC", 's',
 ["Le Tech Lead est le garant technique face au CDS : il relit le code, vérifie les livrables, fait respecter les lignes de développement et la barrière qualité.", "Analyser un devis, c'est vérifier périmètre, hypothèses, chiffrage, risques et oublis (tests, documentation, sécurité, réversibilité) avant qu'il soit validé.", "Les POC servent à lever un doute technique vite et à moindre coût ; les spécifications techniques décrivent les règles de gestion techniques à respecter."],
 ["Mener une revue de code et une vérification de livrable", "Analyser un devis et formuler des remarques utiles", "Cadrer un POC et rédiger des spécifications techniques"],
 [("Revue de code et livrables", "", CK("Revue de code du CDS", ["Conforme aux lignes de développement : couches, nommage, gestion d'erreurs, journaux", "Pas de logique métier dans les Actions Struts ; transactions dans les services", "Requêtes : paramètres liés (pas de concaténation), pas de N+1, index nécessaires livrés", "Sécurité : entrées validées, sorties échappées, pas de secret, droits vérifiés côté serveur", "Tests présents et utiles ; barrière SonarQube verte sur le nouveau code"]) + CK("Vérification d'un livrable", ["Artefact versionné et fiche de version", "Scripts SQL et de configuration numérotés, avec leur retour arrière", "Mode opératoire, notes de version, documentation à jour"])),
  ("Analyser un devis", "", T([
    ("Périmètre", "tout le besoin est-il couvert, rien de plus ?", "« le devis ne couvre pas la reprise des données »"),
    ("Hypothèses", "explicites et réalistes ?", "« l'hypothèse d'un environnement disponible au jour 1 est à confirmer »"),
    ("Chiffrage", "cohérent avec des tâches comparables (abaques, historique)", "« 12 jours pour cet écran contre 5 sur l'écran similaire »"),
    ("Oublis fréquents", "tests, documentation, sécurité, performance, recette, garantie", "« aucun temps prévu pour les tests de non-régression »"),
    ("Risques", "identifiés, avec parade", "« dépendance à la montée de version de WildFly non mentionnée »"),
    ("Livrables", "listés, avec critères d'acceptation", "« critère : barrière qualité verte, mode opératoire rejoué »")], ("Point", "Question", "Exemple de remarque"))),
  ("POC et spécifications", "Un POC a une question précise, une durée bornée, des critères de réussite et une conclusion écrite (on garde, on jette, on approfondit). Une spécification technique décrit les règles à respecter : interfaces, formats, performances, sécurité, exploitation (journaux, codes retour, ordonnancement).", None)],
 [("Le CDS propose 40 jours pour une évolution que tu estimes à 20. Comment le traites-tu ?", "Sans conflit : je demande le détail par tâche, je compare aux abaques et à l'historique, je repère les écarts (hypothèses, risques surestimés, périmètre élargi), et je formule des remarques précises ; la discussion aboutit à un chiffrage justifié ou à un périmètre revu."),
  ("Question d'entretien : comment fais-tu respecter la qualité par un prestataire ?", "Par des règles écrites et partagées (lignes de développement, barrière qualité, liste de revue), appliquées systématiquement, des retours précis et rapides, des indicateurs suivis dans le temps, et un dialogue régulier ; la qualité se négocie au début, pas à la livraison.")],
 ("Une semaine de pilotage du CDS", ["Revue de code d'une merge request volontairement imparfaite : dix remarques classées.", "Analyse d'un devis fictif : remarques écrites sur périmètre, hypothèses, chiffrage, oublis, risques.", "Cadrage d'un POC d'une page et d'une spécification technique d'une page."],
  "Attendu : les remarques sont précises et actionnables ; l'analyse du devis relève au moins quatre oublis ou incohérences ; le POC a un critère de réussite mesurable.")),

ch("Documentation, Jira, Confluence, communication et accréditations", 'c',
 ["La documentation vit dans Confluence avec des modèles communs : mode opératoire, dossier d'exploitation, runbook par incident, fiche de version, décisions d'architecture.", "Jira trace tout : évolutions, anomalies, MCS, mises en production ; des filtres JQL et des tableaux de bord donnent la situation en un coup d'œil.", "Les accréditations suivent un processus : demande, validation par le représentant des utilisateurs, attribution, traçabilité, revue périodique et retrait ; la réversibilité impose une documentation qui permet à un autre de reprendre."],
 ["Structurer la documentation d'exploitation dans Confluence", "Piloter l'activité avec Jira et JQL", "Gérer les accréditations et préparer la réversibilité"],
 [("Confluence : les modèles", "", T([
    ("Dossier d'exploitation", "architecture, serveurs, flux, ordonnancement, sauvegardes, contacts", "à chaque changement d'infrastructure"),
    ("Mode opératoire", "installation pas à pas, contrôles, retour arrière", "à chaque version"),
    ("Runbook", "par alerte ou incident : symptôme, vérifications, action sûre, escalade", "après chaque incident"),
    ("Fiche de version", "contenu, tickets, scripts, dépendances, validations", "à chaque version"),
    ("Décision d'architecture", "contexte, options, décision, conséquences", "à chaque choix structurant")], ("Modèle", "Contenu", "Mise à jour"))),
  ("Jira et JQL", "", r"""project = APP AND type = Bug AND priority in (Highest, High) AND statusCategory != Done ORDER BY created DESC
project = APP AND labels = MCS AND duedate < endOfWeek() AND statusCategory != Done          -- MCS en retard cette semaine
project = APP AND fixVersion = "4.12.0" AND statusCategory != Done                           -- reste à faire de la version
project = APP AND status changed to "Livré" during (startOfMonth(), now()) AND assignee in membersOf("cds")
Tableau de bord : anomalies ouvertes par gravité, MCS par échéance, versions en cours, délai moyen de correction"""),
  ("Accréditations et réversibilité", "", ET(["<strong>Demande</strong> par ticket : qui, quel rôle, quel environnement, pourquoi, jusqu'à quand", "<strong>Validation</strong> par le représentant des utilisateurs finaux (propriétaire métier)", "<strong>Attribution</strong> (groupe d'annuaire ou rôle applicatif), selon le moindre privilège", "<strong>Traçabilité</strong> : ticket, date, valideur, auteur de l'attribution", "<strong>Revue périodique</strong> des droits (trimestrielle), retrait au départ ou au changement de poste", "<strong>Séparation des tâches</strong> : personne ne valide ses propres droits"]) + '<p><strong>Réversibilité</strong> : dossier d\'exploitation, modes opératoires, runbooks, inventaire et accès à jour, et sessions de transfert planifiées avec le repreneur.</p>')],
 [("Un utilisateur demande en urgence les droits d'administration en production « pour débloquer un dossier ». Que fais-tu ?", "Je ne court-circuite pas le processus : je trace la demande, je la fais valider par le représentant des utilisateurs, et je propose le droit minimal nécessaire, limité dans le temps ; si l'urgence est réelle, une procédure d'urgence écrite existe, avec retrait et revue a posteriori."),
  ("Question d'entretien : à quoi reconnais-tu une bonne documentation d'exploitation ?", "À ce qu'une personne qui ne connaît pas l'application peut installer une version, traiter un incident courant et reprendre l'exploitation en la suivant ; elle est à jour, versionnée, et mise à l'épreuve lors des exercices.")],
 ("Kit documentaire et pilotage", ["Rédiger les cinq modèles Confluence (en Markdown dans le dépôt pour l'exercice) remplis pour CrisisShield.", "Écrire dix filtres JQL et le tableau de bord de pilotage (sur un Jira de test ou sur papier).", "Formaliser le processus d'accréditation et un modèle de revue trimestrielle des droits."],
  "Attendu : une personne extérieure installe une version avec le mode opératoire seul ; le tableau de bord répond à « où en est-on ? » en une minute ; la revue des droits trouve au moins un droit à retirer dans le jeu de test.")),

ch("Python pour automatiser l'exploitation", 'c',
 ["Python automatise ce qui se répète : vérification matinale, analyse de journaux, contrôles de cohérence, rapports, appels aux API (WildFly, ordonnanceur, Jira).", "Un script d'exploitation Python a des arguments, des journaux, des codes retour, des délais sur chaque appel réseau et des tests.", "python-oracledb se connecte à Oracle sans client installé ; l'API de gestion HTTP de WildFly permet de lire l'état du serveur en JSON."],
 ["Écrire des scripts d'exploitation Python fiables", "Interroger WildFly, Oracle et Jira par leurs API", "Automatiser la vérification matinale"],
 [("Un contrôle automatisé", "", r"""#!/usr/bin/env python3
import argparse, logging, sys, requests
from requests.auth import HTTPDigestAuth
import oracledb
log = logging.getLogger("controle"); logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
def pool_wildfly(hote, utilisateur, mdp):
    r = requests.post(f"http://{hote}:9990/management", auth=HTTPDigestAuth(utilisateur, mdp), timeout=10,
                      json={"operation": "read-resource", "include-runtime": True,
                            "address": [{"subsystem": "datasources"}, {"data-source": "CriseDS"}, {"statistics": "pool"}]})
    r.raise_for_status(); return r.json()["result"]
def sessions_bloquees(dsn, utilisateur, mdp):
    with oracledb.connect(user=utilisateur, password=mdp, dsn=dsn) as c, c.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM v$session WHERE blocking_session IS NOT NULL"); return cur.fetchone()[0]
if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--wildfly"); a.add_argument("--dsn"); x = a.parse_args()
    anomalies = 0
    p = pool_wildfly(x.wildfly, "controle", sys.stdin.readline().strip())
    if p["ActiveCount"] >= 0.9 * p["MaxUsedCount"]: log.warning("pool presque saturé : %s", p["ActiveCount"]); anomalies += 1
    # … sessions bloquées, espace disque, jobs en erreur via l'API de l'ordonnanceur, fichiers attendus …
    sys.exit(1 if anomalies else 0)"""),
  ("Analyser des journaux", "", r"""import re, collections, pathlib
MOTIF = re.compile(r"^(?P<date>\S+ \S+) (?P<niveau>ERROR|WARN) \[(?P<classe>[^\]]+)\] (?P<message>.*)")
compte = collections.Counter()
for ligne in pathlib.Path("server.log").read_text(encoding="utf-8", errors="replace").splitlines():
    if (m := MOTIF.match(ligne)): compte[(m["niveau"], m["classe"], m["message"][:60])] += 1
for (niveau, classe, message), n in compte.most_common(15): print(f"{n:6} {niveau:5} {classe} {message}")"""),
  ("Jira et rapports", "Le script de vérification matinale crée un ticket Jira pour chaque anomalie (API REST de Jira avec un jeton), et envoie un résumé ; tout tourne dans un conteneur python:3.12-slim lancé par l'ordonnanceur à 7 h 45, avant la vérification humaine.", None)],
 [("Le script de contrôle reste bloqué indéfiniment une nuit sur dix. Cause probable ?", "Un appel réseau sans délai d'expiration (API ou base injoignable) : chaque appel doit avoir un timeout, et le script un délai global géré par l'ordonnanceur ; on journalise l'étape en cours pour savoir où il s'arrête."),
  ("Question d'entretien : qu'as-tu automatisé dans tes missions précédentes ?", "Un exemple mesuré : la vérification matinale passée de 45 à 10 minutes grâce à un script qui collecte l'état des jobs, des serveurs et de la base et ouvre les tickets, la vérification humaine se concentrant sur les anomalies.")],
 ("Vérification matinale automatisée", ["Script Python qui lit l'état de WildFly (API de gestion), d'Oracle (python-oracledb) et des jobs Rundeck (API), et produit un rapport.", "Création automatique de tickets (Jira de test ou fichier) pour chaque anomalie.", "Tests pytest avec des réponses simulées ; lancement par l'ordonnanceur en conteneur."],
  "Attendu : le rapport tient sur un écran ; chaque appel a un délai ; les tests passent sans réseau ; le temps de la vérification humaine est divisé au moins par trois.")),

ch("Entretien et premiers jours de mission", 'e',
 ["L'entretien teste trois choses : la maîtrise technique du socle (WildFly, ordonnancement, Unix, Oracle, Java), la posture de Tech Lead (MCO, MCS, pilotage du CDS), et la fiabilité au quotidien.", "Chaque réponse s'appuie sur une situation réelle, racontée en STAR avec des chiffres ; on termine par ce qu'on ferait dans leur contexte.", "Les trente premiers jours se préparent : prise en main, vérification matinale maîtrisée, première mise en production accompagnée, premières améliorations proposées."],
 ["Présenter son profil en deux minutes pour ce besoin", "Répondre aux questions techniques et de posture", "Préparer son plan des 30, 60 et 90 premiers jours"],
 [("Le pitch de deux minutes", "", ET(["<strong>Qui je suis</strong> : Tech Lead Java depuis 14 ans, MCO et MCS d'applications critiques, DevSecOps.", "<strong>Le socle</strong> : Java 17, Spring, Hibernate, applications legacy (Struts), serveurs d'applications, Oracle, scripts d'exploitation, ordonnancement, CI/CD GitLab et SonarQube.", "<strong>Une réussite chiffrée</strong> : par exemple une mise en production fiabilisée (retours arrière de 4 à 0 par an), ou une vérification matinale automatisée (de 45 à 10 minutes).", "<strong>La posture</strong> : garant technique, pilotage d'un centre de services, qualité et sécurité par le processus.", "<strong>Pour ce poste</strong> : environnements identiques entre intégration et production, sécurité des composants en fin de support, plan de migration."])),
  ("Plan des 30, 60 et 90 jours", "", T([
    ("30 jours", "cartographie, accès, vérification matinale maîtrisée, première mise en production accompagnée", "inventaire, risques, check-list à jour"),
    ("60 jours", "mises en production menées, revue du CDS installée, campagne MCS lancée", "barrière appliquée, vulnérabilités triées"),
    ("90 jours", "plan de migration (WildFly, Java, Struts) proposé, automatisations en place", "feuille de route validée")], ("Horizon", "Objectifs", "Preuves"))),
  ("Quarante questions d'entretien", "", QS([("WildFly", ["Mode autonome ou domaine ?", "Configurer une datasource Oracle ?", "Pourquoi jboss-cli plutôt que l'édition à la main ?", "Pool épuisé : que faire ?", "Thread dump ou heap dump : quand ?", "Sécuriser la console d'administration ?", "Passer de WildFly 26 à 27 et plus : quel impact ?", "Garantir des environnements identiques entre intégration et production ?"]),
  ("Ordonnancement", ["Dépendance, condition, calendrier : quelles différences ?", "Qu'est-ce qu'un bon traitement ordonnancé ?", "Déroule ta vérification matinale.", "Job en erreur à 3 h, éditions bloquées : que fais-tu à 8 h ?", "Relancer sans créer de doublon ?"]),
  ("Unix, Bash et PowerShell", ["Serveur lent : tes cinq premières commandes ?", "À quoi reconnais-tu un script robuste ?", "Disque plein à cause des journaux : que fais-tu ?", "PowerShell : gérer services et journaux d'événements ?"]),
  ("Oracle", ["Trouver qui bloque qui ?", "Lire un plan d'exécution ?", "Pourquoi BULK COLLECT et FORALL ?", "Livrer un script SQL sans risque ?"]),
  ("Java", ["Records et classes scellées : que t'apportent-ils ?", "Migrer de Java 11 à 17 ?", "Régler la JVM dans un conteneur ?"]),
  ("Struts, Spring et Hibernate", ["Lire un struts-config.xml ?", "Quels risques avec Struts 1 ?", "Pourquoi un @Transactional peut-il être contourné ?", "Détecter et corriger un N+1 ?"]),
  ("XML et services web", ["Qu'est-ce qu'une attaque XXE et comment l'éviter ?", "SOAP ou REST pour un nouvel échange ?"]),
  ("CI/CD et qualité", ["Décris ta chaîne type.", "Pourquoi une barrière sur le nouveau code ?", "Jenkins ou GitLab CI ?"]),
  ("Sécurité applicative", ["Trier 300 vulnérabilités ?", "Prouver qu'une vulnérabilité est corrigée ?", "Quand et comment accorder une dérogation ?"]),
  ("Pilotage", ["Comment mènes-tu une revue de code du CDS ?", "Comment analyses-tu un devis ?", "Accréditations demandées en urgence : que fais-tu ?", "À quoi ressemble ta documentation d'exploitation idéale ?"])]) + '<p><strong>Méthode de réponse</strong> : une situation réelle, l\'action menée, un résultat chiffré, puis « dans votre contexte, je ferais… ».</p>')],
 [("On te demande : « Racontez une mise en production qui s'est mal passée. »", "STAR sans esquive : le contexte (version, fenêtre), ce qui a échoué (écart de configuration non détecté), la décision (retour arrière à l'heure prévue), le résultat (service rétabli, communication faite), et ce qui a changé ensuite (comparaison automatique des configurations avant chaque mise en production)."),
  ("Question d'entretien : quelles questions poses-tu à la fin ?", "Sur le contexte réel : l'ordonnanceur utilisé, le rythme des mises en production, l'état des composants en fin de support et la stratégie de migration, la maturité de la chaîne du CDS, les principaux irritants actuels ; cela montre qu'on se projette et aide à préparer les premiers jours.")],
 ("Répétition générale", ["Enregistrer son pitch de deux minutes et le réécouter.", "Répondre à voix haute aux quarante questions, dix chronométrées, en s'appuyant sur les TP de cette page.", "Rédiger son plan des 30, 60 et 90 jours sur une page."],
  "Attendu : chaque réponse tient en moins de deux minutes avec un exemple chiffré ; le plan est concret et daté ; les TP réalisés servent de preuves en entretien.")),
]

# ---------- assemblage en parties : la mission, un cours par technologie, l'entretien ----------
_t = runpy.run_path(str(pathlib.Path(__file__).with_name('mission_tech.py')), run_name='mt')
def partie(lst, n, titre, resume):
    lst[0]['partie'] = (n, titre, resume); return lst
P = []
P += partie([MI[0], MI[1], MI[4], MI[12], MI[13], MI[14]], 1, "La mission", "Périmètre et niveaux exigés, prise en main de l'application, environnements identiques et mises en production, sécurité applicative (MCS), pilotage du centre de services, documentation, Jira, Confluence et accréditations. <strong>Pour aller plus loin</strong> : <a href=\"devops-09-expert-et-leadership.html\">DevOps niveau 9 (leadership, gouvernance)</a>, <a href=\"devops-07-securite-devsecops.html\">DevOps niveau 7 (DevSecOps, MCS)</a>, <a href=\"cours-41-keycloak-et-iam.html\">Keycloak et IAM (LDAP, habilitations)</a>, <a href=\"cours-91-savoir-etre-de-zero-a-expert.html\">Savoir-être</a>.")
P += partie(_t['WILDFLY'], 2, "WildFly — de zéro à expert", "Niveau exigé : expert. Sept chapitres : architecture et installation, modèle de gestion et jboss-cli, datasources Oracle et pools, déploiement et classloading, exploitation et diagnostic, sécurité Elytron et TLS, haute disponibilité, mode domaine et migration vers Jakarta EE 10. <strong>Pour aller plus loin</strong> : <a href=\"devops-01-virtualisation-et-conteneurs.html\">DevOps niveau 1 (conteneurs)</a>, <a href=\"devops-06-observabilite.html\">DevOps niveau 6 (supervision, alertes)</a>, <a href=\"cours-41-keycloak-et-iam.html\">Keycloak et IAM (LDAP, habilitations)</a>, <a href=\"cours-63-monitoring.html\">Monitoring (Prometheus, ELK)</a>.")
P += partie(_t['ORDO'], 3, "Ordonnancement — de zéro à expert", "Niveau exigé : expert. Six chapitres : concepts et dates d'exploitation, conception de chaînes robustes, traitements ordonnançables, outils du marché et équivalences, exploitation quotidienne et incidents, industrialisation et migration d'ordonnanceur. <strong>Pour aller plus loin</strong> : <a href=\"cours-62-talend.html\">Talend (plans d’exécution)</a>, <a href=\"cours-61-data-platform-aws-talend.html\">Data Platform (Airflow)</a>, <a href=\"cours-63-monitoring.html\">Monitoring (Prometheus, ELK)</a>.")
P += partie(_t['UNIX'], 4, "Unix, Bash et PowerShell — de zéro à expert", "Niveau exigé : expert. Six chapitres : système de fichiers, droits et processus, Bash complet, traitement de texte et de journaux, exploitation et diagnostic d'un serveur, PowerShell pour Windows, qualité et sécurité des scripts. <strong>Pour aller plus loin</strong> : <a href=\"devops-00-fondations.html\">DevOps niveau 0 (Linux, shell, Git)</a>, <a href=\"cours-71-perl.html\">Perl (scripts legacy)</a>, <a href=\"devops-10-aide-memoire.html\">Aide-mémoire des commandes</a>.")
P += partie([MI[7]], 5, "Oracle : SQL et PL/SQL", "Niveau exigé : autonome à avancé. Cours détaillé en cours de rédaction : SQL avancé, PL/SQL, transactions et verrous, plans d'exécution, livraisons et Data Pump. <strong>Pour aller plus loin</strong> : <a href=\"cours-11-struts-hibernate-jsp.html\">Struts, Hibernate et JSP</a>, <a href=\"devops-08-sre-et-architecture.html\">DevOps niveau 8 (SRE, incidents, bases en production)</a>.")
P += partie([MI[8]], 6, "Java 17 et plus", "Niveau exigé : avancé. Cours détaillé en cours de rédaction : langage moderne, JVM, concurrence, outillage et migrations. <strong>Pour aller plus loin</strong> : <a href=\"cours-12-kotlin.html\">Kotlin (JVM)</a>, <a href=\"cours-13-java-pki-signature-electronique.html\">Java PKI et signature électronique</a>, <a href=\"cours-21-microservices.html\">Microservices (Spring Boot, REST, contrats)</a>.")
P += partie([MI[9]], 7, "Struts 1, Spring et Hibernate", "Niveau exigé : autonome à avancé. Cours détaillés en cours de rédaction : un cours par technologie. <strong>Pour aller plus loin</strong> : <a href=\"cours-11-struts-hibernate-jsp.html\">Struts, Hibernate et JSP</a>, <a href=\"cours-21-microservices.html\">Microservices (Spring Boot, REST, contrats)</a>, <a href=\"cours-41-keycloak-et-iam.html\">Keycloak et IAM (LDAP, habilitations)</a>.")
P += partie([MI[10]], 8, "XML et services web REST et SOAP", "Niveau exigé : avancé pour XML, autonome pour les services web. Cours détaillé en cours de rédaction. <strong>Pour aller plus loin</strong> : <a href=\"cours-13-java-pki-signature-electronique.html\">Java PKI et signature électronique</a>, <a href=\"cours-21-microservices.html\">Microservices (Spring Boot, REST, contrats)</a>.")
P += partie([MI[11]], 9, "GitLab CI, Jenkins et SonarQube", "Niveau exigé : avancé. Cours détaillé en cours de rédaction. <strong>Pour aller plus loin</strong> : <a href=\"devops-02-integration-et-livraison-continues.html\">DevOps niveau 2 (CI/CD, GitLab CI, Jenkins, SonarQube)</a>, <a href=\"devops-07-securite-devsecops.html\">DevOps niveau 7 (DevSecOps, MCS)</a>, <a href=\"devops-03-infrastructure-as-code.html\">DevOps niveau 3 (Ansible, infrastructure as code)</a>.")
P += partie([MI[15]], 10, "Python pour l'exploitation", "Niveau exigé : avancé à autonome. Cours détaillé en cours de rédaction. <strong>Pour aller plus loin</strong> : <a href=\"cours-31-ia-agentique.html\">IA agentique (Python)</a>, <a href=\"cours-61-data-platform-aws-talend.html\">Data Platform (Airflow)</a>, <a href=\"cours-71-perl.html\">Perl (scripts legacy)</a>.")
_q = runpy.run_path(str(pathlib.Path(__file__).with_name('mission_qr.py')), run_name='mq')
P += partie(_q['ENTRETIEN'], 11, "Entretien : questions et réponses", "Environ 140 questions avec réponses modèles, classées par thème : la mission et le rôle, WildFly, ordonnancement et exploitation, Oracle, Java et frameworks, XML et services web, CI/CD et outils, sécurité et migrations, pilotage du CDS, mises en situation et questions à poser. Clique sur une question pour voir la réponse." + ' <strong>Pour aller plus loin</strong> : <a href="devops-11-fiches-entretien.html">Fiches entretien DevOps</a>, <a href="cours-92-savoir-etre-situations-et-attitudes.html">Savoir-être : situations</a>, <a href="devops-09-expert-et-leadership.html">DevOps niveau 9 (leadership, gouvernance)</a>.')
MI = P

d = sys.argv[1]
page('cours-81-mission-tech-lead-java-mco-mcs.html', "Préparer une mission de Tech Lead Java en MCO et MCS", "Quarante et un chapitres en onze parties pour se préparer en profondeur à une mission de Tech Lead (niveaux expert et avancé) sur une application Java legacy dans une grande institution financière publique : périmètre et niveaux attendus, cartographie d'une application Struts, Spring, Hibernate et Oracle, WildFly de l'installation à la migration, environnements ISO et mises en production, ordonnancement et vérification matinale, Unix, Bash et PowerShell, Oracle SQL et PL/SQL, Java 17 et plus, services web SOAP et REST, CI/CD et barrière SonarQube, MCS, pilotage d'un centre de services, documentation, Jira, Confluence et accréditations, automatisation en Python, et préparation de l'entretien. Tout tourne en conteneur ; chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 110 h de travail · un cours détaillé par technologie exigée ; les parties 5 à 10 sont complétées au fil des livraisons.", MI, [('cours-11-struts-hibernate-jsp.html', 'Struts, Hibernate et JSP'), ('devops-02-integration-et-livraison-continues.html', 'DevOps niveau 2'), ('devops-07-securite-devsecops.html', 'DevOps niveau 7'), ('cours-71-perl.html', 'Perl')])
