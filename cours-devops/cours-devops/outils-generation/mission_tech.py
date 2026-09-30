"""Cours détaillés par technologie pour la page Mission : WildFly (7), Ordonnancement (6), Unix, Bash et PowerShell (6)."""
import runpy, pathlib
g = runpy.run_path(pathlib.Path(__file__).with_name('front_gen.py'), run_name='front'); ch = g['ch']
def T(rows, head): return '<div class="tablewrap"><table><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table></div>'
def CK(titre, items): return f'<p class="liste-titre">{titre}</p><ul class="liste-controle">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'
def ET(items): return '<ol class="etapes">' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>'

# ============================ WILDFLY ============================
WILDFLY = [
ch("WildFly 1 — Fondamentaux : architecture, versions, installation", 'j',
 ["WildFly est le serveur d'applications Jakarta EE open source de Red Hat ; JBoss EAP en est la version supportée commercialement, construite sur la même base.", "Il est fait de modules (JBoss Modules) et de sous-systèmes (web, datasources, sécurité, journaux, messagerie), tous pilotés par un modèle de gestion unique : fichier XML, ligne de commande, console, API HTTP.", "WildFly 26 est la dernière version en Jakarta EE 8 (paquets javax) ; à partir de 27, Jakarta EE 10 (paquets jakarta) : ce seuil structure toutes les migrations."],
 ["Expliquer l'architecture de WildFly et ses versions", "Installer et lancer WildFly en conteneur avec la bonne configuration", "Se repérer dans les répertoires, les ports et les fichiers de configuration"],
 [("Versions et Jakarta EE", T([
    ("WildFly 26 (2022)", "Jakarta EE 8, paquets javax.*", "dernière version javax ; plus maintenue par le projet"),
    ("WildFly 27 et plus", "Jakarta EE 10, paquets jakarta.*", "migration du code et des bibliothèques nécessaire"),
    ("JBoss EAP 7.4", "Jakarta EE 8 (javax)", "support éditeur, base proche de WildFly 23 à 26"),
    ("JBoss EAP 8", "Jakarta EE 10 (jakarta)", "support éditeur, base proche de WildFly 27 et plus")], ("Version", "Plateforme", "À retenir")), None),
  ("Installer et lancer", "Le serveur se lance avec une configuration (-c), une adresse d'écoute publique (-b) et une adresse de gestion (-bmanagement), qu'on limite au réseau d'administration hors laboratoire. Un utilisateur de gestion se crée avec add-user.sh.", r"""# docker-compose.yml
services:
  wildfly:
    image: quay.io/wildfly/wildfly:26.1.3.Final-jdk17
    command: ["/opt/jboss/wildfly/bin/standalone.sh", "-c", "standalone-full.xml", "-b", "0.0.0.0", "-bmanagement", "0.0.0.0"]
    ports: ["8080:8080", "9990:9990"]
docker compose up -d
docker compose exec wildfly /opt/jboss/wildfly/bin/add-user.sh -u admin-tl -p "$MGMT_PASSWORD" --silent   # utilisateur de gestion
docker compose exec wildfly /opt/jboss/wildfly/bin/jboss-cli.sh --connect --command=":read-attribute(name=product-version)"
# décalage de tous les ports (plusieurs instances sur une machine) : -Djboss.socket.binding.port-offset=100"""),
  ("Répertoires, ports, configurations", "", T([
    ("bin/", "standalone.sh, domain.sh, jboss-cli.sh, add-user.sh, standalone.conf (options JVM)", "lancement et outils"),
    ("standalone/configuration/", "standalone.xml, standalone-full.xml, -ha, -full-ha, fichiers de propriétés", "configuration du mode autonome"),
    ("standalone/deployments/", "dépôt par copie (scanner de déploiement)", "à éviter en production, préférer la CLI"),
    ("standalone/log/", "server.log, journaux applicatifs", "exploitation"),
    ("modules/", "modules du serveur et modules ajoutés (pilote Oracle)", "classes partagées"),
    ("Ports", "8080 HTTP, 8443 HTTPS, 9990 gestion (console, API, CLI)", "gestion jamais exposée au public")], ("Élément", "Contenu", "Usage")))],
 [("Quelle configuration choisir entre standalone.xml et standalone-full.xml ?", "standalone.xml contient le profil web (servlets, JPA, CDI…) ; standalone-full.xml ajoute la messagerie (JMS avec Artemis) et d'autres services Jakarta EE complets. On prend la plus petite qui couvre les besoins de l'application, et les variantes -ha pour le cluster."),
  ("Question d'entretien : WildFly ou JBoss EAP ?", "Même base technique : WildFly évolue vite, sans support ; JBoss EAP est la version stabilisée et supportée par Red Hat, avec correctifs de sécurité sur la durée. En production critique, EAP ou une version de WildFly suivie de près ; le choix dépend du contrat de support et de la politique de l'organisation.")],
 ("Premier WildFly", ["Lancer WildFly 26 en conteneur avec standalone-full.xml ; créer un utilisateur de gestion.", "Relever version, ports, configuration active et sous-systèmes par la CLI.", "Lancer une seconde instance avec un décalage de ports."],
  "Attendu : la console répond sur 9990 avec l'utilisateur créé ; la CLI renvoie la version ; les deux instances tournent sans conflit de ports.")),

ch("WildFly 2 — Le modèle de gestion et jboss-cli", 'c',
 ["Tout se configure par des adresses (/subsystem=datasources/data-source=X) et des opérations (:read-resource, :add, :write-attribute, :remove) : c'est le même modèle pour la CLI, la console et l'API HTTP.", "Les scripts jboss-cli sont versionnés, idempotents (if … of … read-resource), groupés en lots (batch) et paramétrés par fichier de propriétés : le même script configure l'intégration et la production.", "Certaines modifications demandent un rechargement (reload-required) ; embed-server permet de configurer hors ligne, par exemple pendant la construction d'une image."],
 ["Lire et modifier le modèle de gestion", "Écrire des scripts jboss-cli idempotents et paramétrés", "Gérer rechargements, configuration hors ligne et API HTTP"],
 [("Lire le modèle", "", r"""jboss-cli.sh --connect
[standalone@localhost:9990 /] /subsystem=undertow:read-resource(recursive=true)
[standalone@localhost:9990 /] /subsystem=datasources/data-source=CriseDS:read-attribute(name=max-pool-size)
[standalone@localhost:9990 /] /subsystem=logging:read-children-names(child-type=logger)
[standalone@localhost:9990 /] :read-attribute(name=server-state)           # running, reload-required, restart-required
[standalone@localhost:9990 /] /subsystem=datasources/data-source=CriseDS:read-operation-names"""),
  ("Un script idempotent et paramétré", "Le script ne crée que ce qui manque et lit ses valeurs dans un fichier de propriétés par environnement ; les modifications sont groupées en lot pour être appliquées ensemble ou pas du tout.", r"""# config/commun.cli — lancé par : jboss-cli.sh --connect --file=config/commun.cli --properties=config/integration.properties
batch
if (outcome != success) of /system-property=crise.env:read-resource
  /system-property=crise.env:add(value=${crise.env})
end-if
/system-property=crise.env:write-attribute(name=value, value=${crise.env})
/subsystem=undertow/server=default-server/http-listener=default:write-attribute(name=max-post-size, value=${crise.max.post})
/subsystem=logging/logger=fr.crise:write-attribute(name=level, value=${crise.log.niveau})
run-batch
:reload
# config/integration.properties : crise.env=integration, crise.max.post=10485760, crise.log.niveau=DEBUG
# config/production.properties  : crise.env=production,  crise.max.post=10485760, crise.log.niveau=INFO"""),
  ("Hors ligne et API HTTP", "embed-server démarre un serveur sans réseau pour appliquer un script à la configuration, idéal pendant la construction d'une image ; l'API HTTP de gestion accepte les mêmes opérations en JSON, pratique pour les contrôles automatisés.", r"""jboss-cli.sh --commands="embed-server --server-config=standalone-full.xml,run-batch --file=/tmp/commun.cli,stop-embedded-server"
curl -s --digest -u "admin-tl:$MGMT_PASSWORD" http://wildfly:9990/management -H "Content-Type: application/json" \
  -d '{"operation":"read-attribute","address":[{"subsystem":"datasources"},{"data-source":"CriseDS"}],"name":"enabled"}'""")],
 [("Après ton script, :read-attribute(name=server-state) renvoie reload-required. Que faire ?", "La configuration persistée a changé mais n'est pas encore active : on planifie un :reload (quelques secondes d'indisponibilité) dans la fenêtre prévue, ou on l'inclut en fin de script ; certaines modifications exigent même un redémarrage complet (restart-required)."),
  ("Question d'entretien : comment garantis-tu une configuration identique entre intégration et production ?", "Un seul jeu de scripts jboss-cli versionnés, idempotents, paramétrés par un fichier de propriétés par environnement ; les valeurs propres sont documentées, et un export comparé automatiquement vérifie l'absence d'écart avant chaque mise en production.")],
 ("Configuration par scripts", ["Écrire commun.cli (propriétés système, écouteur HTTP, niveau de journal) et deux fichiers de propriétés.", "L'appliquer en intégration et en production (deux conteneurs), puis rejouer sans effet.", "Appliquer le même script hors ligne dans un Dockerfile avec embed-server."],
  "Attendu : les deux environnements ne diffèrent que par les propriétés documentées ; la seconde exécution ne change rien ; l'image construite démarre déjà configurée.")),

ch("WildFly 3 — Datasources, pilote Oracle et pools de connexions", 's',
 ["Le pilote Oracle est installé comme module, déclaré comme pilote JDBC, puis utilisé par une datasource exposée en JNDI (java:jboss/datasources/CriseDS).", "Le pool se dimensionne (min, max, délais) et se protège : validation des connexions, tri des exceptions Oracle, délai d'attente, détection des fuites.", "Les statistiques du pool (connexions actives, disponibles, attente maximale) sont la première chose à regarder quand l'application ralentit."],
 ["Installer le pilote Oracle et créer une datasource", "Régler et protéger un pool de connexions", "Lire les statistiques et diagnostiquer un pool"],
 [("Pilote et datasource", "", r"""# datasource-oracle.cli (idempotent)
if (outcome != success) of /subsystem=datasources/jdbc-driver=oracle:read-resource
  module add --name=com.oracle --resources=/opt/drivers/ojdbc11.jar --dependencies=javax.api,javax.transaction.api
  /subsystem=datasources/jdbc-driver=oracle:add(driver-name=oracle,driver-module-name=com.oracle,driver-class-name=oracle.jdbc.OracleDriver)
end-if
if (outcome != success) of /subsystem=datasources/data-source=CriseDS:read-resource
  data-source add --name=CriseDS --jndi-name=java:jboss/datasources/CriseDS --driver-name=oracle \
    --connection-url=jdbc:oracle:thin:@//oracle:1521/FREEPDB1 --user-name=crise --password=${env.DB_PASSWORD} \
    --min-pool-size=5 --max-pool-size=30 --blocking-timeout-wait-millis=5000 --idle-timeout-minutes=10 \
    --validate-on-match=true --background-validation=false \
    --valid-connection-checker-class-name=org.jboss.jca.adapters.jdbc.extensions.oracle.OracleValidConnectionChecker \
    --exception-sorter-class-name=org.jboss.jca.adapters.jdbc.extensions.oracle.OracleExceptionSorter \
    --statistics-enabled=true
end-if
/subsystem=datasources/data-source=CriseDS:test-connection-in-pool"""),
  ("Régler le pool", "", T([
    ("min-pool-size / max-pool-size", "connexions ouvertes au minimum et au maximum", "max aligné sur la capacité de la base et le nombre de fils"),
    ("blocking-timeout-wait-millis", "attente maximale d'une connexion libre", "échouer vite plutôt que bloquer"),
    ("validate-on-match / background-validation", "vérifier la connexion avant usage, ou en tâche de fond", "élimine les connexions mortes après un redémarrage d'Oracle"),
    ("exception-sorter", "reconnaître les erreurs Oracle fatales", "retire la connexion cassée du pool"),
    ("idle-timeout-minutes", "fermer les connexions inactives", "évite les coupures par le pare-feu"),
    ("track-statements, détection des fuites", "signaler les connexions non fermées", "à activer pour diagnostiquer")], ("Réglage", "Rôle", "Pourquoi"))),
  ("Statistiques et diagnostic", "", r"""/subsystem=datasources/data-source=CriseDS/statistics=pool:read-resource(include-runtime=true)
# ActiveCount (en usage), AvailableCount (libres), MaxUsedCount (pic), MaxWaitTime (attente la plus longue), TimedOut
/subsystem=datasources/data-source=CriseDS:flush-invalid-connection-in-pool     # retirer les connexions invalides
/subsystem=datasources/data-source=CriseDS:flush-all-connection-in-pool        # tout renouveler (avec prudence)
# fuites : /subsystem=jca/cached-connection-manager=cached-connection-manager:write-attribute(name=debug,value=true)""")],
 [("Après un redémarrage d'Oracle cette nuit, l'application renvoie des erreurs « connexion fermée » jusqu'au redémarrage de WildFly. Que manque-t-il ?", "La validation des connexions (validate-on-match ou validation en tâche de fond) et le tri des exceptions Oracle : le pool aurait détecté et remplacé les connexions mortes. On les active, et on teste en redémarrant Oracle en intégration."),
  ("Question d'entretien : comment dimensionnes-tu un pool ?", "À partir du nombre de requêtes simultanées réellement utiles et de la capacité de la base (sessions, processeurs), pas au maximum possible ; un pool trop grand déplace la contention vers la base. On mesure les pics (MaxUsedCount, MaxWaitTime) sous charge et on ajuste.")],
 ("Pool robuste", ["Pilote Oracle en module et datasource par script idempotent, statistiques activées.", "Redémarrer Oracle pendant que l'application tourne ; vérifier le retour automatique sans erreur durable.", "Provoquer un épuisement du pool et le diagnostiquer par les statistiques."],
  "Attendu : après le redémarrage d'Oracle, les erreurs cessent d'elles-mêmes en quelques secondes ; l'épuisement est visible (ActiveCount = max, MaxWaitTime élevé) et expliqué.")),

ch("WildFly 4 — Déployer : WAR, EAR, classloading, JNDI, messagerie", 's',
 ["Une application se déploie en WAR (web) ou en EAR (plusieurs modules) ; en production, par la CLI ou la chaîne de livraison, jamais par copie manuelle.", "WildFly isole les applications par modules : une bibliothèque embarquée peut entrer en conflit avec celle du serveur ; jboss-deployment-structure.xml règle exclusions et dépendances.", "Les ressources partagées (datasources, files JMS Artemis, propriétés) sont nommées en JNDI et injectées ; une application Struts et Spring embarque ses bibliothèques dans WEB-INF/lib."],
 ["Déployer, remplacer et retirer une application", "Résoudre les conflits de classes avec jboss-deployment-structure.xml", "Configurer JNDI et files de messages pour une application"],
 [("Déployer", "", r"""jboss-cli.sh --connect --command="deploy /livraisons/crise-4.12.0.war --name=crise.war --runtime-name=crise.war --force"
jboss-cli.sh --connect --command="deployment-info --name=crise.war"
jboss-cli.sh --connect --command="undeploy crise.war --keep-content"          # retirer sans supprimer le contenu
# scanner de déploiement (développement) : copier crise.war dans standalone/deployments/ ; fichiers témoins .deployed, .failed
# le nom d'exécution fixe le contexte web (/crise) : garder le même nom d'une version à l'autre"""),
  ("Conflits de classes", "Une erreur NoSuchMethodError ou ClassCastException au démarrage signale souvent deux versions d'une même bibliothèque (celle de l'application et celle du serveur). On exclut le module du serveur, ou on retire la copie embarquée, et on déclare explicitement les modules nécessaires.", r"""<!-- WEB-INF/jboss-deployment-structure.xml -->
<jboss-deployment-structure>
  <deployment>
    <exclude-subsystems>
      <subsystem name="jpa"/>                 <!-- l'application embarque sa propre version d'Hibernate -->
    </exclude-subsystems>
    <exclusions>
      <module name="org.apache.log4j"/>        <!-- l'application fournit sa configuration de journaux -->
    </exclusions>
    <dependencies>
      <module name="com.oracle"/>               <!-- pilote Oracle fourni par le serveur -->
    </dependencies>
  </deployment>
</jboss-deployment-structure>"""),
  ("JNDI et messagerie", "La datasource s'obtient par son nom JNDI ; avec standalone-full.xml, Artemis fournit files et sujets JMS, créés par script et utilisés par l'application.", r"""jms-queue add --queue-address=NotificationsQueue --entries=java:/jms/queue/Notifications
/subsystem=messaging-activemq/server=default/jms-queue=NotificationsQueue:read-resource(include-runtime=true)   # messages en attente
// Spring : <jee:jndi-lookup id="dataSource" jndi-name="java:jboss/datasources/CriseDS"/>
// Java EE / Jakarta EE : @Resource(lookup = "java:jboss/datasources/CriseDS") DataSource ds;""")],
 [("L'application démarre en intégration mais échoue en production avec NoSuchMethodError dans Hibernate. Cause probable ?", "Un conflit de versions : l'application embarque une version d'Hibernate différente de celle fournie par le serveur, et l'ordre de chargement diffère (ou la configuration n'est pas ISO). On exclut le sous-système JPA du serveur dans jboss-deployment-structure.xml, ou on s'aligne sur la version fournie, et on vérifie l'ISO des configurations."),
  ("Question d'entretien : comment déploies-tu en production sur WildFly ?", "Par un script de la chaîne de livraison qui déploie un artefact versionné par la CLI (deploy --force avec un nom d'exécution stable), précédé des scripts de configuration et suivi de contrôles automatiques ; jamais par copie dans le répertoire deployments.")],
 ("Déploiement maîtrisé", ["Déployer l'application CrisisShield legacy par la CLI avec un nom d'exécution stable ; remplacer par la version suivante.", "Provoquer un conflit de bibliothèque et le résoudre avec jboss-deployment-structure.xml.", "Créer une file JMS par script, y envoyer et consommer des messages."],
  "Attendu : le remplacement de version se fait sans changer l'URL ; le conflit est expliqué et résolu ; la file affiche le nombre de messages en attente dans la CLI.")),

ch("WildFly 5 — Exploiter et diagnostiquer", 's',
 ["Exploiter, c'est démarrer et arrêter proprement (service systemd, arrêt gracieux, suspension), régler les journaux et surveiller pools, fils d'exécution, mémoire et temps de réponse.", "Le diagnostic s'appuie sur des preuves : statistiques, vidages des fils d'exécution (plusieurs, espacés), vidage mémoire, journaux du ramasse-miettes, journaux d'accès.", "Chaque symptôme courant a sa démarche : pool épuisé, fils bloqués, fuite mémoire, CPU saturé, démarrage en échec."],
 ["Installer WildFly comme service et l'arrêter proprement", "Configurer journaux et supervision", "Diagnostiquer les incidents courants avec des preuves"],
 [("Service et arrêt propre", "", r"""# /etc/systemd/system/wildfly.service (hors conteneur)
[Unit]
Description=WildFly
After=network.target
[Service]
User=wildfly
Environment=JAVA_OPTS="-Xms2g -Xmx2g -XX:+UseG1GC -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/dumps"
ExecStart=/opt/wildfly/bin/standalone.sh -c standalone-full.xml -b 10.0.1.20 -bmanagement 10.9.0.20
ExecStop=/opt/wildfly/bin/jboss-cli.sh --connect --controller=10.9.0.20:9990 --command=":shutdown(suspend-timeout=60)"
TimeoutStopSec=120
[Install]
WantedBy=multi-user.target
# suspendre (terminer les requêtes en cours, refuser les nouvelles) avant une opération : :suspend(suspend-timeout=60), puis :resume"""),
  ("Journaux et supervision", "", r"""/subsystem=logging/size-rotating-file-handler=APP:add(file={path=crise.log,relative-to=jboss.server.log.dir},rotate-size=50m,max-backup-index=20,autoflush=true)
/subsystem=logging/logger=fr.crise:add(level=INFO,handlers=[APP])
/subsystem=logging/json-formatter=JSON:add(pretty-print=false)                 # journaux structurés pour la supervision
/subsystem=undertow/server=default-server/host=default-host/setting=access-log:add(pattern="%h %t \"%r\" %s %b %D")   # %D : durée
# métriques : point de terminaison sur le port de gestion (/metrics), collecté par Prometheus ; santé : /health (selon la version)"""),
  ("Diagnostiquer", "", T([
    ("Pages qui tournent sans fin", "pool épuisé, requêtes longues, verrous en base", "statistiques du pool, trois vidages des fils à 10 s d'intervalle, sessions Oracle"),
    ("Lenteur progressive puis OutOfMemoryError", "fuite mémoire, sessions HTTP trop grosses, cache non borné", "vidage mémoire (Eclipse MAT), journaux du GC"),
    ("CPU à 100 %", "boucle, GC permanent, expression régulière coûteuse", "top -H, vidages des fils, jcmd GC.heap_info, JFR"),
    ("Démarrage en échec", "datasource injoignable, déploiement invalide, port occupé", "server.log au démarrage, deployment-info, ss -tlnp"),
    ("Erreurs après mise en production", "écart de configuration, bibliothèque manquante", "comparaison des configurations, fiche de version")], ("Symptôme", "Cause fréquente", "Preuves à collecter")))],
 [("Tu dois prendre des vidages des fils d'exécution pendant un incident : combien et pourquoi ?", "Trois ou quatre, espacés de dix secondes environ : un seul montre une photo ; plusieurs montrent si des fils restent bloqués au même endroit (attente d'une connexion, d'un verrou, d'un appel externe) ou si le système avance."),
  ("Question d'entretien : comment arrêtes-tu WildFly sans perdre de requêtes ?", "Par une suspension ou un arrêt gracieux (:shutdown avec suspend-timeout) : le serveur termine les requêtes en cours et refuse les nouvelles, derrière un répartiteur qui retire l'instance du service ; jamais un kill -9 sauf blocage avéré.")],
 ("Exploitation de WildFly", ["Service systemd (ou équivalent en conteneur) avec arrêt gracieux ; journaux par taille et au format JSON ; journal d'accès avec durées.", "Provoquer une fuite mémoire et un blocage ; collecter vidage mémoire, vidages des fils et journaux du GC.", "Rédiger les runbooks « pool épuisé » et « OutOfMemoryError »."],
  "Attendu : l'arrêt ne coupe aucune requête en cours ; la fuite est trouvée dans le vidage mémoire ; chaque runbook tient sur une page et s'applique sans connaître l'application.")),

ch("WildFly 6 — Sécurité : Elytron, TLS, gestion et durcissement", 's',
 ["Depuis WildFly 25, toute la sécurité passe par Elytron : domaines de sécurité, royaumes (fichiers, LDAP, base de données), fabriques d'authentification HTTP, contextes TLS.", "L'interface de gestion est la cible la plus sensible : utilisateurs nominatifs, réseau d'administration, TLS, audit des opérations.", "Le durcissement se fait par une liste vérifiée : contenus d'exemple retirés, en-têtes de sécurité, journaux d'accès, secrets dans un magasin d'identifiants, veille des vulnérabilités."],
 ["Configurer l'authentification applicative avec Elytron et LDAP", "Activer TLS sur l'application et la gestion", "Appliquer et vérifier une liste de durcissement"],
 [("Elytron et LDAP", "", r"""/subsystem=elytron/dir-context=annuaire:add(url="ldaps://ldap.interne:636",principal="cn=svc-crise,ou=services,dc=interne",credential-reference={store=cs,alias=ldap-svc})
/subsystem=elytron/ldap-realm=annuaire-realm:add(dir-context=annuaire,identity-mapping={rdn-identifier=uid,search-base-dn="ou=personnes,dc=interne",attribute-mapping=[{filter-base-dn="ou=groupes,dc=interne",filter="(member={1})",from=cn,to=Roles}]})
/subsystem=elytron/security-domain=crise-sd:add(realms=[{realm=annuaire-realm}],default-realm=annuaire-realm,permission-mapper=default-permission-mapper)
/subsystem=elytron/http-authentication-factory=crise-http:add(security-domain=crise-sd,http-server-mechanism-factory=global,mechanism-configurations=[{mechanism-name=FORM}])
/subsystem=undertow/application-security-domain=crise:add(http-authentication-factory=crise-http)
# l'application déclare le domaine « crise » (jboss-web.xml) et ses rôles dans web.xml"""),
  ("TLS", "", r"""/subsystem=elytron/key-store=serveur-ks:add(path=serveur.p12,relative-to=jboss.server.config.dir,credential-reference={store=cs,alias=ks},type=PKCS12)
/subsystem=elytron/key-manager=serveur-km:add(key-store=serveur-ks,credential-reference={store=cs,alias=ks})
/subsystem=elytron/server-ssl-context=serveur-ssl:add(key-manager=serveur-km,protocols=["TLSv1.3","TLSv1.2"])
/subsystem=undertow/server=default-server/https-listener=https:write-attribute(name=ssl-context,value=serveur-ssl)
# gestion : /core-service=management/management-interface=http-interface:write-attribute(name=ssl-context,value=serveur-ssl)"""),
  ("Durcissement", "", CK("Liste de durcissement de WildFly", ["Interface de gestion liée au réseau d'administration, en TLS, utilisateurs nominatifs, audit des opérations activé", "Contenu d'accueil (welcome-content) et applications d'exemple retirés", "En-têtes de sécurité (HSTS, X-Content-Type-Options, X-Frame-Options) ajoutés par filtres Undertow", "Journal d'accès activé, conservé et exploité", "Secrets dans un magasin d'identifiants Elytron, aucun mot de passe en clair dans les fichiers", "Version de Java et de WildFly suivie, bulletins de sécurité lus, correctifs planifiés", "Comptes système dédiés sans droits d'administration de la machine"]))],
 [("La console de gestion est accessible depuis le réseau bureautique avec un compte partagé. Priorités ?", "Lier l'interface de gestion au réseau d'administration (et TLS), remplacer le compte partagé par des utilisateurs nominatifs, activer l'audit des opérations et relire l'historique, puis appliquer le reste de la liste de durcissement."),
  ("Question d'entretien : qu'apporte Elytron ?", "Un modèle de sécurité unique pour l'application, la gestion et TLS : domaines, royaumes interchangeables (fichiers, LDAP, JDBC, jetons), magasins d'identifiants pour les secrets ; il remplace l'ancien sous-système de sécurité, supprimé depuis WildFly 25.")],
 ("Sécuriser WildFly", ["Authentification de l'application par un annuaire OpenLDAP en conteneur via Elytron.", "TLS sur l'écouteur HTTPS et sur l'interface de gestion ; mots de passe dans le magasin d'identifiants.", "Dérouler la liste de durcissement et produire la preuve de chaque point."],
  "Attendu : la connexion à l'application passe par l'annuaire et les rôles sont appliqués ; aucune connexion en clair sur la gestion ; chaque point de la liste est prouvé par une commande ou une capture.")),

ch("WildFly 7 — Haute disponibilité, mode domaine et migration", 'e',
 ["La haute disponibilité passe par plusieurs instances derrière un répartiteur, avec sessions répliquées (Infinispan) dans les configurations -ha, et des déploiements successifs sans interruption.", "Le mode domaine centralise profils, groupes de serveurs et déploiements pour un parc de machines ; beaucoup d'équipes préfèrent le mode autonome industrialisé par scripts.", "Migrer de WildFly 26 à 27 et plus impose le passage aux paquets jakarta : c'est un projet (inventaire, transformation, tests, retour arrière), pas une mise à jour."],
 ["Mettre en place deux instances avec sessions répliquées", "Comprendre et utiliser le mode domaine", "Planifier une montée de version majeure de WildFly"],
 [("Haute disponibilité", "", r"""# deux instances en standalone-ha.xml derrière un répartiteur (Apache mod_cluster, HAProxy ou le répartiteur de la plateforme)
standalone.sh -c standalone-ha.xml -Djboss.node.name=noeud1 -b 10.0.1.21 -bprivate 10.0.2.21
standalone.sh -c standalone-ha.xml -Djboss.node.name=noeud2 -b 10.0.1.22 -bprivate 10.0.2.22
# application distribuable : <distributable/> dans web.xml → sessions HTTP répliquées par Infinispan
# mise en production sans interruption : retirer un nœud du répartiteur, suspendre, déployer, contrôler, remettre ; puis l'autre"""),
  ("Le mode domaine", "", r"""domain.sh --host-config=host-master.xml                      # contrôleur de domaine
/server-group=crise-prod:add(profile=full-ha, socket-binding-group=full-ha-sockets)
/host=machine1/server-config=crise1:add(group=crise-prod, socket-binding-port-offset=0)
deploy crise.war --server-groups=crise-prod                   # déploiement sur tout le groupe
/server-group=crise-prod:restart-servers                       # redémarrage du groupe"""),
  ("Migrer vers WildFly 27 et plus", "", ET(["<strong>Inventaire</strong> : dépendances javax.* (jdeps), bibliothèques sans version jakarta (Struts 1 en tête), configurations spécifiques", "<strong>Choix</strong> : rester sur une base javax supportée (JBoss EAP 7.4), transformer les binaires (Eclipse Transformer), ou migrer le code (OpenRewrite) et remplacer les bibliothèques", "<strong>Configuration</strong> : scripts jboss-cli rejoués sur la nouvelle version, écarts corrigés (sous-systèmes renommés, options retirées)", "<strong>Tests</strong> : non-régression, charge et sécurité en intégration", "<strong>Bascule</strong> : fenêtre dédiée, ancienne version prête au retour arrière, surveillance renforcée", "<strong>Nettoyage</strong> : documentation, runbooks et dossier d'exploitation mis à jour"]))],
 [("On te demande de « passer sur WildFly 31 le mois prochain » alors que l'application utilise Struts 1. Que réponds-tu ?", "Que Struts 1 dépend de javax.servlet et ne tourne pas tel quel sur Jakarta EE 10 : je propose trois options chiffrées (rester sur une base javax supportée le temps de migrer la couche web, transformer les binaires avec des tests poussés, ou migrer la couche web), avec un calendrier réaliste et un POC pour valider l'option retenue."),
  ("Question d'entretien : mode domaine ou autonome industrialisé ?", "Le domaine apporte une gestion centrale d'un parc homogène ; l'autonome, piloté par scripts versionnés et une chaîne de livraison, s'intègre mieux aux conteneurs et à l'automatisation. Je choisis selon le parc, les compétences de l'exploitation et les standards de l'organisation.")],
 ("Haute disponibilité et plan de migration", ["Deux instances standalone-ha derrière HAProxy en Compose, sessions répliquées ; arrêter un nœud sans perdre la session.", "Déploiement successif nœud par nœud sans interruption.", "Dossier de migration 26 → 31 : inventaire, trois options, POC, calendrier, retour arrière."],
  "Attendu : la session utilisateur survit à l'arrêt d'un nœud ; le déploiement successif ne provoque aucune erreur côté client ; le dossier de migration est présentable à un comité.")),
]

# ============================ ORDONNANCEMENT ============================
ORDO = [
ch("Ordonnancement 1 — Concepts : jobs, chaînes, plans, dates d'exploitation", 'j',
 ["Un ordonnanceur lance des traitements (jobs) selon des règles : dépendances, calendriers, fenêtres, ressources, conditions ; il en garde l'historique et alerte en cas d'échec.", "Le plan du jour est calculé à partir des définitions et des calendriers ; chaque exécution a un statut (en attente, en cours, terminé, en erreur, forcé, annulé).", "La date d'exploitation (date de traitement) n'est pas la date système : une chaîne de nuit qui passe minuit traite toujours le jour prévu."],
 ["Maîtriser le vocabulaire commun des ordonnanceurs", "Lire un plan et les statuts des jobs", "Distinguer date d'exploitation et date système"],
 [("Le vocabulaire commun", T([
    ("Job (tâche, uproc)", "une commande ou un script, avec son code retour", "extraction_incidents.sh"),
    ("Chaîne (application, session, dossier, flux)", "jobs ordonnés et dépendants", "référentiels puis calculs puis éditions"),
    ("Plan (plan du jour)", "exécutions prévues pour une date d'exploitation", "plan du 29/09"),
    ("Dépendance", "un job attend la fin réussie d'un autre", "calcul après extraction"),
    ("Condition, événement", "attente d'un fichier, d'un signal, d'une autre chaîne", "fichier du partenaire arrivé"),
    ("Calendrier", "jours d'exécution (ouvrés, fériés, fin de mois)", "jours ouvrés seulement"),
    ("Fenêtre, heure limite", "plage autorisée, heure de fin attendue", "de 21 h à 5 h, fin avant 6 h"),
    ("Ressource", "limite de parallélisme ou exclusivité", "un seul job sur la base à la fois"),
    ("Forçage, mise en attente, annulation", "actions manuelles de l'exploitation", "à tracer et justifier")], ("Terme", "Signification", "Exemple")), None),
  ("Les statuts et le plan", "Chaque matin on lit le plan de la nuit par statut : les jobs terminés en succès, ceux en erreur (avec leur code retour), ceux restés en attente (condition non remplie, dépendance en erreur) et ceux en retard par rapport à leur heure limite.", None),
  ("Date d'exploitation", "Le script reçoit la date à traiter en paramètre au lieu de calculer « aujourd'hui » : une relance le lendemain retraite le bon jour, et une chaîne qui passe minuit ne change pas de date en cours de route.", r"""# mauvais : la date change si le job passe minuit ou s'il est relancé le lendemain
JOUR=$(date +%Y%m%d)
# bon : la date d'exploitation est fournie par l'ordonnanceur (variable ou paramètre du job)
JOUR=${1:?date d'exploitation attendue (AAAAMMJJ)}
[[ $JOUR =~ ^[0-9]{8}$ ]] || { echo "date invalide : $JOUR"; exit 2; }""")],
 [("Une chaîne de nuit démarrée à 23 h 30 produit un fichier daté du lendemain pour la moitié des jobs. Pourquoi ?", "Les scripts calculent la date système au lieu d'utiliser la date d'exploitation : ceux qui démarrent après minuit prennent la date suivante. On passe la date d'exploitation en paramètre à chaque job, fournie par l'ordonnanceur."),
  ("Question d'entretien : quelle différence entre une dépendance et une condition ?", "Une dépendance relie deux jobs (l'un attend la fin réussie de l'autre) ; une condition attend un événement extérieur ou une autre chaîne (fichier arrivé, signal, fin d'une chaîne d'un autre domaine). Les deux bloquent le démarrage, mais se diagnostiquent différemment.")],
 ("Lire un plan", ["Représenter la chaîne de nuit de CrisisShield (dix jobs) : dépendances, conditions, calendrier, heures limites.", "Adapter trois scripts pour recevoir la date d'exploitation en paramètre et la valider.", "Simuler une relance le lendemain et vérifier que le bon jour est traité."],
  "Attendu : un schéma clair de la chaîne ; les scripts refusent une date absente ou invalide ; la relance du lendemain retraite exactement la date d'origine.")),

ch("Ordonnancement 2 — Concevoir une chaîne robuste", 'c',
 ["Une bonne chaîne est découpée en jobs courts et relançables, avec des points de reprise, un parallélisme maîtrisé et des dépendances explicites.", "Les calendriers et fenêtres traduisent les contraintes métier : jours ouvrés, fériés, fin de mois, fin d'année, heures limites des partenaires.", "Les dépendances entre chaînes de domaines différents se font par conditions ou fichiers témoins documentés, jamais par des horaires supposés."],
 ["Découper une chaîne en jobs relançables", "Exprimer calendriers, fenêtres et heures limites", "Relier des chaînes entre elles sans fragilité"],
 [("Découper", "", T([
    ("Un job fait une chose", "extraire, contrôler, transformer, charger, éditer", "relance ciblée"),
    ("Points de reprise", "état persisté entre les étapes", "reprendre à l'étape 9, pas tout refaire"),
    ("Contrôles entre étapes", "volumes, présence, cohérence", "arrêter tôt plutôt que propager"),
    ("Parallélisme", "jobs indépendants en parallèle, bornés par des ressources", "gagner du temps sans saturer la base"),
    ("Nettoyage", "job final de purge des fichiers temporaires", "pas d'accumulation")], ("Principe", "Mise en œuvre", "Bénéfice"))),
  ("Calendriers et fenêtres", "Chaque chaîne a son calendrier (jours ouvrés du pays, fermetures, fin de mois), sa fenêtre et ses heures limites, avec la conduite à tenir en cas de dépassement. Les cas particuliers (fin d'année, changement d'heure, jours fériés glissants) sont listés et testés à l'avance.", None),
  ("Relier des chaînes", "", r"""Chaîne « référentiel » (autre équipe)   ──fin OK──▶  fichier témoin /echanges/referentiel_AAAAMMJJ.ok
Chaîne « nuit_crise » : job 1 attend la condition (fichier témoin du jour) jusqu'à 01 h 30
   si absent à 01 h 30 : alerte à l'astreinte et à l'équipe « référentiel », plan de repli documenté
Règle : pas de dépendance cachée par l'horaire (« normalement ils ont fini à 1 h »)""")],
 [("La chaîne de nuit échoue à l'étape 9 sur 10 ; la relancer demande six heures car tout repart du début. Que changer ?", "Découper en jobs relançables avec des points de reprise (état intermédiaire persisté, écritures idempotentes) : la relance repart de l'étape 9. On ajoute aussi des contrôles entre étapes pour échouer plus tôt."),
  ("Question d'entretien : comment gères-tu une dépendance vers une chaîne d'une autre équipe ?", "Par une condition explicite (fichier témoin ou événement de fin), avec une heure limite, une alerte partagée et un plan de repli documenté ; jamais par un horaire supposé, qui casse le jour où l'autre chaîne prend du retard.")],
 ("Concevoir la chaîne de nuit", ["Redécouper une chaîne monolithique en jobs relançables avec points de reprise.", "Définir calendrier, fenêtre, heures limites et conditions inter-chaînes.", "Lister et tester les cas particuliers : fin de mois, férié, changement d'heure."],
  "Attendu : une relance à l'étape 9 ne rejoue que la fin ; chaque cas particulier a un comportement vérifié ; les dépendances inter-chaînes sont toutes explicites.")),

ch("Ordonnancement 3 — Écrire des traitements ordonnançables", 'c',
 ["L'ordonnanceur ne sait que ce que le job lui dit : son code retour. Un code 0 doit vouloir dire « succès vérifié », et chaque autre code a un sens documenté.", "Un lanceur commun impose les mêmes conventions à tous les jobs : journal horodaté, verrou contre les doubles lancements, délai maximal, variables d'environnement, nettoyage.", "Un traitement ordonnancé contrôle ses entrées et ses sorties (volumes, présence, cohérence) et se relance sans doublon."],
 ["Définir et appliquer une convention de codes retour", "Écrire un lanceur commun pour tous les jobs", "Contrôler volumes et cohérence, et garantir la relance sans doublon"],
 [("Les codes retour", T([
    ("0", "succès vérifié (contrôles passés)", "suite de la chaîne"),
    ("1", "anomalie métier (données incohérentes)", "analyse fonctionnelle, pas de relance aveugle"),
    ("2", "erreur technique (base, réseau, disque)", "relance après correction"),
    ("3", "déjà en cours (verrou)", "vérifier l'autre exécution"),
    ("4", "entrée absente ou vide", "vérifier l'amont"),
    ("5", "délai maximal dépassé", "analyser la lenteur")], ("Code", "Sens", "Conduite à tenir")), None),
  ("Un lanceur commun", "", r"""#!/usr/bin/env bash
# lanceur.sh JOB DATE_EXPLOITATION -- commande…   (appelé par l'ordonnanceur pour chaque job)
set -Eeuo pipefail
JOB=$1; JOUR=$2; shift 3
LOG=/var/log/batch/${JOB}_${JOUR}_$(date +%H%M%S).log
exec > >(tee -a "$LOG") 2>&1
exec 9>/var/lock/batch_$JOB.lock; flock -n 9 || { echo "$(date -Is) $JOB déjà en cours"; exit 3; }
trap 'echo "$(date -Is) ERREUR $JOB ligne $LINENO"; exit 2' ERR
echo "$(date -Is) DEBUT $JOB jour=$JOUR hote=$(hostname)"
timeout --signal=TERM "${DELAI_MAX:-3600}" "$@" "$JOUR" || { rc=$?; [ $rc -eq 124 ] && exit 5; exit $rc; }
echo "$(date -Is) FIN $JOB code=0"
# nettoyage des journaux de plus de 30 jours par le job de purge de fin de chaîne"""),
  ("Contrôler et relancer sans doublon", "", r"""n=$(wc -l < "/data/sortie/incidents_$JOUR.csv")
[ "$n" -gt 1 ] || { echo "fichier vide"; exit 4; }
hier=$(cat "/data/suivi/volume_incidents.last" 2>/dev/null || echo "$n")
(( n * 2 < hier )) && { echo "volume divisé par plus de deux ($hier → $n)"; exit 1; }
echo "$n" > /data/suivi/volume_incidents.last
# chargement idempotent : table temporaire puis MERGE (ou suppression du jour puis insertion), jamais un simple ajout rejoué""")],
 [("Un job renvoie toujours 0 car la dernière commande du script est un echo. Quelle conséquence, et quelle correction ?", "L'ordonnanceur croit au succès même quand une étape a échoué, et la suite de la chaîne traite des données fausses. On active le mode strict (set -Eeuo pipefail), on vérifie chaque étape, on sort explicitement avec le bon code, et un test vérifie le code en cas d'échec."),
  ("Question d'entretien : que doit faire un script avant de dire « succès » ?", "Vérifier son résultat : fichier produit et non vide, volume cohérent avec l'historique, lignes rejetées sous un seuil, table chargée au bon compte ; le code 0 signifie « contrôlé », pas seulement « arrivé au bout ».")],
 ("Normaliser les jobs de la chaîne", ["Écrire le lanceur commun (journal, verrou, délai, codes) et y faire passer tous les jobs.", "Ajouter à chaque job ses contrôles de volume et de cohérence.", "Rendre les chargements idempotents ; relancer deux fois le même jour."],
  "Attendu : chaque job produit un journal nommé et horodaté ; un double lancement renvoie 3 ; la double relance ne crée aucun doublon ; un fichier vide renvoie 4.")),

ch("Ordonnancement 4 — Les outils du marché et leurs équivalences", 's',
 ["Les ordonnanceurs d'entreprise (Control-M, VTOM, Dollar Universe, IBM Workload Scheduler, Autosys) partagent les mêmes concepts sous des noms différents ; on transpose ses réflexes d'un outil à l'autre.", "Chaque outil offre une console et une ligne de commande pour lister, relancer, forcer, mettre en attente ; on apprend en priorité les commandes que l'exploitation du site autorise.", "Les outils libres (cron, systemd timers, Rundeck, Airflow) servent à s'entraîner et couvrent les besoins plus simples."],
 ["Transposer le vocabulaire d'un ordonnanceur à l'autre", "Utiliser les actions courantes en console et en ligne de commande", "S'entraîner sur un outil libre en conteneur"],
 [("Équivalences", "", T([
    ("Control-M (BMC)", "job, dossier (folder)", "conditions entrantes et sortantes, calendriers", "console Control-M/EM, API d'automatisation"),
    ("VTOM (Absyss)", "job, application, environnement", "liens, ressources, dates d'exploitation", "console, commandes vt…"),
    ("Dollar Universe (Broadcom)", "uproc, session, tâche", "conditions, ressources, calendriers", "console Univiewer, commandes uxl…"),
    ("IBM Workload Scheduler", "job, job stream", "dépendances, ressources, calendriers", "conman, console Web"),
    ("Autosys (Broadcom)", "job, box", "conditions (success, failure), calendriers", "JIL, autorep, sendevent"),
    ("Rundeck / Airflow (libres)", "job, workflow ou DAG", "dépendances, planification", "interface Web, API, CLI")], ("Outil", "Objets", "Enchaînement", "Accès"))),
  ("Actions courantes (exemple Autosys)", "La syntaxe diffère selon l'outil et la version ; les actions, elles, sont toujours les mêmes : consulter, relancer, forcer, mettre en attente, lire le journal.", r"""autorep -J 'nuit_crise%' -q                 # définitions des jobs de la chaîne (JIL)
autorep -J 'nuit_crise%'                    # statuts : SU (succès), FA (échec), RU (en cours), OI/OH (en attente)
sendevent -E FORCE_STARTJOB -J nuit_crise_calcul     # relancer un job (après analyse)
sendevent -E JOB_ON_ICE -J nuit_crise_editions        # mettre en attente sans bloquer la suite
sendevent -E CHANGE_STATUS -s SUCCESS -J nuit_crise_calcul   # forcer en succès : exceptionnel, tracé, justifié
# Control-M, VTOM, Dollar Universe : mêmes actions, avec leurs propres commandes et droits"""),
  ("S'entraîner avec Rundeck", "", r"""docker run -d --name rundeck -p 4440:4440 rundeck/rundeck:5.7.0
# projet « crise », jobs : extraction → contrôle → calcul → éditions (workflow avec étapes et gestion d'erreur)
# notifications sur échec et sur dépassement de durée ; historique et journaux par exécution
# API : curl -H "X-Rundeck-Auth-Token: $TOKEN" http://localhost:4440/api/41/project/crise/executions?statusFilter=failed""")],
 [("Tu arrives sur un site en Dollar Universe alors que tu connais Control-M. Comment te mets-tu à niveau vite ?", "En transposant les concepts (uproc et session contre job et dossier, conditions, calendriers), en demandant la documentation d'exploitation du site et les droits prévus, et en observant la vérification matinale avec l'exploitant ; en une semaine, on sait lire le plan, analyser un échec et proposer une relance."),
  ("Question d'entretien : que penses-tu du forçage en succès d'un job en erreur ?", "C'est exceptionnel : on ne force que si l'on sait que le résultat attendu existe par ailleurs ou n'est pas nécessaire à la suite, avec une trace (ticket), une justification et l'accord du responsable ; sinon, on corrige et on relance.")],
 ("Une chaîne dans Rundeck", ["Rundeck en conteneur ; chaîne de quatre jobs utilisant le lanceur commun.", "Notifications d'échec et de dépassement de durée ; consultation par l'API.", "Tableau d'équivalence des commandes entre Rundeck et l'ordonnanceur que tu vises."],
  "Attendu : la chaîne s'exécute et s'arrête proprement sur erreur ; l'API liste les exécutions en échec ; le tableau d'équivalence tient sur une page.")),

ch("Ordonnancement 5 — Exploiter au quotidien : vérification matinale et incidents", 's',
 ["La vérification matinale, faite en production puis en intégration, est un rituel : même check-list, même ordre, même compte rendu.", "Face à un job en erreur : qualifier, décider (relancer, forcer, mettre en attente, escalader), exécuter, tracer, communiquer.", "Les pièges connus se préparent : fins de mois et d'année, changements d'heure, jours fériés, retards des partenaires."],
 ["Mener la vérification matinale et rédiger son compte rendu", "Traiter un incident d'ordonnancement de bout en bout", "Anticiper les cas particuliers du calendrier"],
 [("La vérification matinale", "", CK("Check-list de 8 h 00 : production, puis intégration", ["Plan de la nuit : tous les jobs terminés, aucun en erreur, en attente ou en retard ?", "Jobs en erreur : code retour, journal, cause probable, relance possible sans risque ?", "Heures limites respectées, fichiers livrés aux partenaires ?", "Volumes cohérents avec la veille ?", "Serveurs d'applications et base : services démarrés, pools sains, espace disque, sauvegarde de la nuit réussie", "Actions : relances faites, tickets ouverts, message aux parties prenantes si impact"])),
  ("Traiter un incident", "", ET(["<strong>Qualifier</strong> : quel job, quel code retour, depuis quand, quel impact en aval et pour les utilisateurs", "<strong>Diagnostiquer</strong> : journal du job, journaux applicatifs, état de la base et des dépendances", "<strong>Décider</strong> : relancer (si idempotent et cause levée), reprendre à un point, forcer (exceptionnel), mettre en attente, escalader", "<strong>Exécuter</strong> et surveiller jusqu'à la fin de la chaîne", "<strong>Tracer</strong> : ticket Jira avec la cause, l'action, la durée d'impact", "<strong>Communiquer</strong> : message aux utilisateurs concernés, puis correction de fond planifiée"])),
  ("Les cas particuliers", "", T([
    ("Changement d'heure (mars, octobre)", "un job à 2 h 30 ne s'exécute pas, ou deux fois", "pas de planification entre 2 h et 3 h, ou fuseau UTC"),
    ("Fin de mois, fin d'année", "volumes multipliés, traitements supplémentaires", "tests à blanc, fenêtres élargies, astreinte renforcée"),
    ("Jours fériés", "chaîne lancée un jour chômé ou pas lancée un jour ouvré", "calendrier maintenu et relu chaque année"),
    ("Retard d'un partenaire", "condition jamais remplie", "heure limite, alerte, plan de repli")], ("Cas", "Risque", "Parade")))],
 [("Il est 8 h 10 ; le job d'éditions attend depuis 4 h une condition venant d'une autre équipe, qui n'est pas remplie. Que fais-tu ?", "Je vérifie l'état de la chaîne amont (en erreur, en retard ?), je contacte l'équipe concernée, je préviens les utilisateurs du retard des éditions, et j'applique le plan de repli documenté s'il existe ; je ne force pas la condition sans l'accord de l'équipe amont, et je trace tout dans un ticket."),
  ("Question d'entretien : que contient ton compte rendu de vérification matinale ?", "Le statut global (vert, orange, rouge), les jobs en erreur ou en retard avec cause, action et état, l'impact pour les utilisateurs, les tickets ouverts et les points à surveiller ; il part à la même heure chaque jour, aux mêmes destinataires.")],
 ("Une semaine de vérifications", ["Dérouler la check-list chaque matin sur la chaîne Rundeck pendant cinq jours simulés (avec incidents injectés).", "Traiter chaque incident selon les six étapes et rédiger le compte rendu du jour.", "Tester le passage à l'heure d'hiver et une fin de mois."],
  "Attendu : chaque incident est traité en moins de quinze minutes avec sa trace ; les cinq comptes rendus ont la même forme ; les cas particuliers se comportent comme prévu.")),

ch("Ordonnancement 6 — Industrialiser : chaînes comme code, tests, supervision", 'e',
 ["Les définitions des chaînes sont du code : exportées, versionnées, relues en MR et déployées par la chaîne de livraison, identiques en intégration et en production.", "Une modification de chaîne se teste en intégration avec des dates d'exploitation simulées, y compris les cas particuliers, avant d'arriver en production.", "La supervision surveille les heures limites (délais de fin) et remonte les alertes au bon endroit ; les migrations entre ordonnanceurs se font par inventaire, correspondance et exécution en parallèle."],
 ["Versionner et déployer les définitions de chaînes", "Tester une chaîne avant la production", "Superviser les heures limites et préparer une migration d'ordonnanceur"],
 [("Les chaînes comme code", "Selon l'outil : export XML ou JSON des définitions, API d'automatisation (Control-M), fichiers JIL (Autosys), DAG Python (Airflow). Le principe ne change pas : le dépôt est la référence, la chaîne de livraison applique.", r"""# Airflow : la chaîne est un fichier Python versionné
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
with DAG("nuit_crise", start_date=datetime(2026, 9, 1), schedule="0 21 * * 1-5", catchup=False,
         default_args={"retries": 1, "retry_delay": timedelta(minutes=10), "sla": timedelta(hours=8)}) as dag:
    extraction = BashOperator(task_id="extraction", bash_command="lanceur.sh extraction {{ ds_nodash }} -- extraction.sh")
    calcul     = BashOperator(task_id="calcul",     bash_command="lanceur.sh calcul {{ ds_nodash }} -- calcul.sh")
    editions   = BashOperator(task_id="editions",   bash_command="lanceur.sh editions {{ ds_nodash }} -- editions.sh")
    extraction >> calcul >> editions            # {{ ds_nodash }} : la date d'exploitation, jamais la date système"""),
  ("Tester et superviser", "", CK("Avant de livrer une modification de chaîne", ["Définition relue en MR (dépendances, calendriers, ressources, codes retour attendus)", "Exécution complète en intégration avec la date d'exploitation du jour et une date simulée de fin de mois", "Relance d'un job au milieu de la chaîne sans doublon", "Heures limites et alertes vérifiées (notification reçue)", "Documentation d'exploitation et runbooks mis à jour"])),
  ("Migrer d'ordonnanceur", "", ET(["<strong>Inventaire</strong> : toutes les chaînes, jobs, calendriers, conditions, ressources, avec leurs propriétaires", "<strong>Correspondance</strong> : concepts et objets de l'ancien outil vers le nouveau, cas non transposables identifiés", "<strong>Conversion</strong> : automatisée quand c'est possible, relue chaîne par chaîne", "<strong>Exécution en parallèle</strong> (le nouvel outil en simulation) et comparaison des plans et des résultats", "<strong>Bascule</strong> par lots de chaînes, avec retour arrière", "<strong>Formation</strong> de l'exploitation et mise à jour des procédures"]))],
 [("Une chaîne a été modifiée directement dans la console de production ; l'intégration a une version différente. Risques et correction ?", "Les tests en intégration ne valent plus rien et la modification n'est ni relue ni tracée. On réaligne à partir de la définition de production exportée, on la versionne, et désormais toute modification passe par le dépôt et la livraison, en intégration d'abord."),
  ("Question d'entretien : comment testes-tu une modification de chaîne ?", "En intégration, avec les mêmes définitions qu'en production, une date d'exploitation normale et des dates simulées pour les cas particuliers, une relance au milieu, la vérification des alertes et des heures limites ; puis livraison par le dépôt.")],
 ("Chaîne industrialisée", ["Chaîne de nuit écrite en DAG Airflow (ou export Rundeck) dans un dépôt, avec lanceur commun et date d'exploitation.", "Tests en intégration : jour normal, fin de mois, relance au milieu ; alertes sur heure limite.", "Plan de migration d'un ordonnanceur à un autre pour dix chaînes."],
  "Attendu : la chaîne se déploie depuis le dépôt ; les trois tests passent ; l'alerte de dépassement est reçue ; le plan de migration prévoit une exécution en parallèle.")),
]

# ============================ UNIX, BASH, POWERSHELL ============================
UNIX = [
ch("Unix 1 — Système de fichiers, droits, utilisateurs, processus", 'j',
 ["Sous Unix, tout est fichier : l'arborescence commence à /, les droits se lisent par propriétaire, groupe et autres (lecture, écriture, exécution).", "Chaque processus a un propriétaire, un parent, des fichiers ouverts et reçoit des signaux : TERM demande l'arrêt propre, KILL l'impose sans rien terminer.", "Sur les serveurs d'entreprise, on croise surtout Red Hat et parfois AIX : mêmes principes, quelques commandes différentes."],
 ["Se repérer dans l'arborescence et les droits", "Gérer utilisateurs, groupes et privilèges", "Observer et arrêter correctement des processus"],
 [("Droits et arborescence", "", r"""ls -l /opt/wildfly/standalone/configuration/standalone.xml
-rw-r----- 1 wildfly wildfly 42012 sept. 29 07:58 standalone.xml    # lecture/écriture propriétaire, lecture groupe, rien pour les autres
chmod 640 standalone.xml ; chown wildfly:wildfly standalone.xml
umask 027                                   # droits par défaut des nouveaux fichiers : 640 et répertoires 750
getfacl /data/echanges ; setfacl -m g:exploitation:rx /data/echanges     # droits fins par listes de contrôle d'accès
find /opt/wildfly -perm -o+w -type f        # fichiers modifiables par tout le monde : à corriger
# arborescence utile : /etc (configuration), /var/log (journaux), /opt (applications), /tmp (temporaire), /proc (processus)"""),
  ("Utilisateurs et privilèges", "Chaque service tourne sous un compte dédié sans connexion interactive ; les administrateurs passent par sudo avec des règles précises et journalisées, jamais par un compte root partagé.", r"""useradd --system --shell /sbin/nologin --home /opt/wildfly wildfly
# /etc/sudoers.d/exploitation : autoriser seulement ce qui est nécessaire
%exploitation ALL=(root) NOPASSWD: /bin/systemctl restart wildfly, /bin/systemctl status wildfly
sudo -l                                     # ce que j'ai le droit de faire
id ; groups ; last -n 10                    # qui suis-je, mes groupes, dernières connexions"""),
  ("Processus et signaux", "", r"""ps -ef | grep [j]boss-modules              # le processus WildFly (les crochets évitent de trouver le grep)
ps -o pid,ppid,user,etime,%cpu,%mem,cmd -p <pid>
kill -TERM <pid>                            # demande d'arrêt propre (le programme termine ses tâches)
kill -KILL <pid>                            # arrêt immédiat : dernier recours, rien n'est terminé proprement
nohup ./traitement.sh > traitement.log 2>&1 &   # détacher un traitement de la session
# AIX : ps -ef, topas (au lieu de top), errpt (journal d'erreurs système), lsattr / chdev (paramètres)""")],
 [("Pourquoi éviter kill -9 sur WildFly ?", "Parce que le processus ne peut rien terminer : transactions en cours interrompues, fichiers non vidés, verrous et journaux de transactions laissés en l'état. On arrête par la CLI (arrêt gracieux) ou par kill -TERM, et -KILL seulement si le processus ne répond plus, en le traçant."),
  ("Question d'entretien : comment donnes-tu à l'exploitation le droit de redémarrer un service sans lui donner root ?", "Par une règle sudo limitée à la commande exacte (systemctl restart du service), pour le groupe d'exploitation, journalisée ; les comptes de service n'ont pas de connexion interactive.")],
 ("Poste d'exploitation Unix", ["Conteneur Rocky Linux : compte de service sans connexion, droits corrects sur une arborescence applicative.", "Règle sudo limitée pour un groupe d'exploitation ; vérifier ce qui est permis et refusé.", "Lancer, observer et arrêter proprement un traitement long ; comparer TERM et KILL sur un script qui écrit un fichier."],
  "Attendu : aucun fichier modifiable par tous ; le groupe d'exploitation peut redémarrer le service et rien d'autre ; l'arrêt par TERM laisse un fichier complet, KILL un fichier tronqué.")),

ch("Unix 2 — Bash de zéro à expert", 'c',
 ["Bash se maîtrise par ses règles : guillemets autour des variables, expansions de paramètres, tests [[ ]], codes retour, fonctions, tableaux.", "Un script de production commence par le mode strict (set -Eeuo pipefail), piège les erreurs (trap) et lit ses options (getopts).", "Les constructions avancées (substitution de processus, here-docs, tableaux associatifs) rendent les scripts plus courts et plus sûrs."],
 ["Écrire des scripts Bash corrects (guillemets, tests, boucles, fonctions)", "Appliquer le mode strict, les pièges et getopts", "Utiliser les constructions avancées de Bash"],
 [("Les bases qui évitent les pièges", "", r"""fichier="rapport du jour.csv"
cp "$fichier" /archives/                     # toujours des guillemets : sinon le nom est coupé aux espaces
nom=${fichier%.csv} ; ext=${fichier##*.}     # expansions : suppression de suffixe, extension
: "${DB_HOST:?DB_HOST non défini}"           # arrêter si la variable manque
defaut=${NIVEAU:-INFO}                       # valeur par défaut
if [[ -f $fichier && $(wc -l < "$fichier") -gt 1 ]]; then echo "fichier non vide"; fi
for f in /data/entree/*.xml; do [[ -e $f ]] || continue; traiter "$f"; done
declare -A seuils=([N1]=10 [S3]=25) ; echo "${seuils[N1]}"    # tableau associatif"""),
  ("Mode strict, pièges, options", "", r"""#!/usr/bin/env bash
set -Eeuo pipefail                            # erreur → arrêt ; variable non définie → arrêt ; échec dans un tube → arrêt
IFS=$'\n\t'
trap 'echo "erreur ligne $LINENO (code $?)" >&2' ERR
trap 'rm -rf "$TMPDIR_JOB"' EXIT             # nettoyage garanti, même en cas d'erreur
TMPDIR_JOB=$(mktemp -d)
usage(){ echo "usage : $0 -e ENV [-n] fichiers…" >&2; exit 64; }
ESSAI=0
while getopts "e:nh" opt; do case $opt in e) ENV=$OPTARG;; n) ESSAI=1;; *) usage;; esac; done
shift $((OPTIND-1)); [[ ${ENV:-} =~ ^(integration|production)$ ]] || usage
log(){ printf '%s [%s] %s\n' "$(date -Is)" "$ENV" "$*"; }"""),
  ("Constructions avancées", "", r"""diff <(sort liste_integration.txt) <(sort liste_production.txt)      # substitution de processus
mapfile -t serveurs < serveurs_$ENV.txt                               # lire un fichier dans un tableau
for s in "${serveurs[@]}"; do ssh -o BatchMode=yes "$s" 'systemctl is-active wildfly'; done
cat > /tmp/requete.sql <<'SQL'
SELECT COUNT(*) FROM incident WHERE statut = 'OUVERT';
SQL
( cd /data/entree && tar czf "/archives/entree_$(date +%F).tgz" . )    # sous-shell : le cd ne fuit pas""")],
 [("Pourquoi rm -rf $DOSSIER/* est-il dangereux, et comment l'écrire ?", "Si DOSSIER est vide ou non défini, la commande devient rm -rf /* ; sans guillemets, un nom avec espace est coupé. On écrit : : \"${DOSSIER:?}\" puis rm -rf -- \"${DOSSIER:?}\"/* après avoir vérifié que le dossier est celui attendu, avec set -u et un mode essai à blanc."),
  ("Question d'entretien : que fait set -Eeuo pipefail ?", "-e arrête le script à la première erreur, -u refuse les variables non définies, -o pipefail fait échouer un tube si une commande du tube échoue, -E propage le piège ERR dans les fonctions ; c'est la base d'un script qui échoue clairement au lieu de continuer à moitié.")],
 ("Scripts Bash de production", ["Réécrire un vieux script sans guillemets ni contrôles avec le mode strict, trap, getopts et fonctions.", "Comparer deux listes de configurations par substitution de processus.", "Écrire la boucle d'état des services sur une liste de serveurs lue par mapfile."],
  "Attendu : ShellCheck ne signale rien ; le script échoue proprement sur option invalide (code 64) ; le nettoyage est fait même en cas d'erreur.")),

ch("Unix 3 — Traiter du texte et des journaux : grep, sed, awk, jq", 'c',
 ["Les journaux se fouillent avec grep (motifs, contexte), se transforment avec sed, se résument avec awk (colonnes, totaux, regroupements) et se lisent en JSON avec jq.", "Sur un serveur de production, on filtre d'abord (par période, par fichier compressé) pour ne pas saturer les disques ni le processeur.", "Ces outils se combinent en tubes : chaque étape réduit le volume avant la suivante."],
 ["Chercher efficacement dans des journaux volumineux", "Transformer et résumer du texte avec sed et awk", "Exploiter des journaux JSON avec jq"],
 [("Chercher", "", r"""grep -n "ERROR" server.log | tail -20                          # dernières erreurs avec numéros de ligne
grep -B3 -A10 "OutOfMemoryError" server.log                   # contexte avant et après
zgrep -c "ERROR" server.log.2026-09-2*.gz                     # dans les journaux compressés, sans les décompresser
awk '$2 >= "02:00:00" && $2 <= "03:30:00"' server.log | grep -E "ERROR|WARN"   # une fenêtre horaire
nice -n 19 ionice -c3 grep -c "timeout" /var/log/app/*.log    # priorité basse sur un serveur chargé"""),
  ("Transformer et résumer", "", r"""sed -i.bak 's/^timeout=30$/timeout=60/' application.properties           # modification en place avec sauvegarde
sed -n '/DEBUT nuit_crise/,/FIN nuit_crise/p' batch.log                   # extraire un bloc
awk -F';' 'NR>1 {n[$2]++; t[$2]+=$4} END {for (z in n) printf "%s %d %.1f\n", z, n[z], t[z]/n[z]}' incidents.csv | sort -k2 -nr
awk '{print $9}' access.log | sort | uniq -c | sort -nr | head   # répartition des codes HTTP
awk '$NF > 2000000 {print $7, $NF/1000 " ms"}' access.log | sort -k2 -nr | head   # requêtes de plus de 2 s (%D en µs)"""),
  ("JSON avec jq", "", r"""jq -r 'select(.niveau == "ERROR") | [.t, .service, .message] | @tsv' crise.json.log | tail
jq -s 'group_by(.service) | map({service: .[0].service, erreurs: length})' erreurs.json
curl -s http://wildfly:9990/metrics | grep -E "^base_memory_usedHeap|^vendor_datasource"   # métriques au format texte""")],
 [("Tu dois compter les erreurs de la nuit dans 40 Go de journaux sur un serveur de production chargé. Comment procèdes-tu ?", "Je cible les fichiers de la période, je lis les compressés avec zgrep, je filtre d'abord par heure puis par motif, et je lance en priorité basse (nice, ionice) ; si possible, je copie les fichiers utiles sur une machine d'analyse plutôt que de travailler sur la production."),
  ("Question d'entretien : awk ou un script Python pour analyser des journaux ?", "awk pour une réponse rapide en ligne de commande (compter, grouper, filtrer par colonne) ; Python quand l'analyse devient complexe, doit être réutilisée, testée ou produire un rapport : les deux se complètent.")],
 ("Analyse des journaux de CrisisShield", ["Extraire les erreurs d'une fenêtre horaire dans des journaux compressés.", "Rapport awk : répartition des codes HTTP et les dix requêtes les plus lentes à partir du journal d'accès.", "Rapport jq sur les journaux JSON : erreurs par service."],
  "Attendu : chaque rapport tient en une commande documentée ; les résultats sont vérifiés sur un échantillon ; aucune commande ne décompresse les journaux sur le disque.")),

ch("Unix 4 — Exploiter et diagnostiquer un serveur", 's',
 ["Le diagnostic suit un ordre : charge et processeur, mémoire, disques et inodes, entrées-sorties, réseau, processus, journaux du service.", "systemd pilote les services (démarrage, arrêt, journaux, relance automatique) ; cron et les minuteurs systemd planifient ; logrotate garde les disques sous contrôle.", "Pour les cas difficiles : lsof (fichiers et connexions ouverts), strace (appels système), tcpdump (trafic), openssl (certificats)."],
 ["Diagnostiquer un serveur en cinq minutes", "Gérer services, planifications et rotation des journaux", "Utiliser les outils de diagnostic avancés"],
 [("Diagnostic en cinq minutes", "", r"""uptime ; nproc                               # charge moyenne rapportée au nombre de processeurs
top -o %CPU -n 1 | head -15 ; top -H -p <pid> -n 1 | head    # processus et fils les plus gourmands
free -h ; vmstat 1 5                         # mémoire, échange, file d'attente, attente d'entrées-sorties (wa)
df -h ; df -i                                # espace disque et inodes
iostat -xz 1 3                               # disques saturés (%util)
ss -tlnp ; ss -tn state established '( dport = :1521 )' | wc -l   # ports ouverts, connexions vers Oracle
journalctl -u wildfly --since "1 hour ago" -p err"""),
  ("Services, planification, rotation", "", r"""systemctl status wildfly ; systemctl restart wildfly ; systemctl enable wildfly
systemctl list-timers                        # minuteurs systemd planifiés
crontab -l -u batch                           # planifications cron d'un compte
# /etc/logrotate.d/crise
/var/log/app/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate                              # si l'application ne sait pas rouvrir son fichier
}"""),
  ("Outils avancés", "", r"""lsof -p <pid> | wc -l ; lsof -i :8080         # fichiers et connexions ouverts
strace -f -p <pid> -e trace=network,read,write -o /tmp/trace.txt      # où un processus est bloqué
tcpdump -i any -nn port 1521 -c 100 -w /tmp/oracle.pcap               # trafic vers la base (avec autorisation)
openssl s_client -connect api.partenaire.fr:443 -servername api.partenaire.fr </dev/null | openssl x509 -noout -dates -subject
curl -v --max-time 10 https://api.partenaire.fr/sante                  # test de bout en bout avec détail
dig +short api.partenaire.fr                                           # résolution DNS""")],
 [("Le serveur est « lent », la charge est à 12 pour 4 processeurs mais le processeur est peu utilisé. Hypothèse ?", "Des processus en attente d'entrées-sorties (colonne wa de vmstat élevée, iostat avec %util proche de 100 %) : disque saturé, par exemple par un journal qui grossit ou une sauvegarde ; on identifie le processus (iotop, lsof) et on agit sur la cause."),
  ("Question d'entretien : comment évites-tu le disque plein à cause des journaux ?", "Rotation par logrotate (ou par l'application), compression, rétention définie, alerte d'espace disque à 80 %, et journaux applicatifs sur un volume séparé du système ; on vérifie aussi les journaux au niveau DEBUG laissés actifs.")],
 ("Serveur sous contrôle", ["Script de diagnostic en cinq minutes produisant un rapport horodaté.", "Service systemd avec relance automatique, rotation logrotate, minuteur systemd pour un traitement.", "Simuler un disque saturé en écriture et un service bloqué sur le réseau ; les diagnostiquer avec iostat, lsof et strace."],
  "Attendu : le rapport de diagnostic suffit à orienter l'analyse ; la rotation fonctionne (forcée avec logrotate -f) ; les deux incidents sont expliqués preuve à l'appui.")),

ch("Unix 5 — PowerShell pour l'exploitation Windows", 's',
 ["PowerShell manipule des objets, pas du texte : on filtre avec Where-Object, on choisit avec Select-Object, on exporte en CSV ou JSON sans découper des chaînes.", "Les tâches d'exploitation Windows passent par lui : services, tâches planifiées, journaux d'événements, disques, administration à distance.", "Un script PowerShell de production arrête sur erreur ($ErrorActionPreference = 'Stop'), gère ses exceptions (try, catch) et se teste avec Pester."],
 ["Utiliser le pipeline d'objets de PowerShell", "Administrer services, tâches, journaux et machines distantes", "Écrire des scripts PowerShell robustes et testés"],
 [("Le pipeline d'objets", "", r"""Get-Process java | Sort-Object WorkingSet64 -Descending | Select-Object Id, ProcessName, @{n='Mo';e={[int]($_.WorkingSet64/1MB)}} -First 5
Get-ChildItem D:\logs -Filter *.log | Where-Object Length -gt 100MB | Select-Object Name, Length, LastWriteTime
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | Select-Object DeviceID, @{n='Libre %';e={[int](100*$_.FreeSpace/$_.Size)}}
Import-Csv .\incidents.csv -Delimiter ';' | Group-Object zone | Sort-Object Count -Descending
Get-Service | Where-Object Status -eq 'Stopped' | Export-Csv services_arretes.csv -NoTypeInformation"""),
  ("Administrer", "", r"""Get-Service -Name 'Wildfly*' ; Restart-Service -Name WildflyCrise -PassThru
Get-WinEvent -FilterHashtable @{LogName='Application'; Level=2; StartTime=(Get-Date).AddHours(-12)} | Select-Object TimeCreated, ProviderName, Message -First 20
$action  = New-ScheduledTaskAction -Execute 'pwsh.exe' -Argument '-File D:\scripts\purge.ps1'
$declen  = New-ScheduledTaskTrigger -Daily -At 22:00
Register-ScheduledTask -TaskName 'Crise\Purge' -Action $action -Trigger $declen -User 'SVC-CRISE' -RunLevel Limited
Get-ScheduledTask -TaskPath '\Crise\' | Get-ScheduledTaskInfo | Where-Object LastTaskResult -ne 0
Invoke-Command -ComputerName srv-app-01, srv-app-02 -ScriptBlock { Get-Service WildflyCrise | Select-Object MachineName, Status }"""),
  ("Scripts robustes et tests", "", r"""[CmdletBinding(SupportsShouldProcess)]
param([Parameter(Mandatory)][string]$Dossier, [int]$Jours = 30)
$ErrorActionPreference = 'Stop'
try {
    Get-ChildItem $Dossier -Filter *.log | Where-Object LastWriteTime -lt (Get-Date).AddDays(-$Jours) |
      ForEach-Object { if ($PSCmdlet.ShouldProcess($_.FullName, 'Supprimer')) { Remove-Item $_.FullName } }
} catch { Write-Error "purge en échec : $_"; exit 2 }
# lancement à blanc : .\purge.ps1 -Dossier D:\logs -WhatIf
# Pester : Describe 'purge' { It 'ne supprime rien avec -WhatIf' { … } } ; entraînement : docker run --rm -it mcr.microsoft.com/powershell pwsh""")],
 [("Get-Process java | Stop-Process a arrêté tous les programmes Java du serveur, pas seulement WildFly. Comment l'éviter ?", "En ciblant précisément (par identifiant de processus, nom de service ou ligne de commande via Get-CimInstance Win32_Process), en testant d'abord avec -WhatIf, et en passant par Stop-Service pour un service ; un pipeline d'objets agit sur tout ce qu'il reçoit."),
  ("Question d'entretien : pourquoi PowerShell plutôt que des fichiers .bat ?", "Parce qu'il manipule des objets (plus de découpage de texte fragile), accède à tout le système (services, journaux, CIM, registre), gère les erreurs et le mode essai à blanc, s'administre à distance et se teste avec Pester : les scripts sont plus sûrs et plus lisibles.")],
 ("Boîte à outils PowerShell", ["Rapport d'état d'un serveur Windows : services, disques, tâches planifiées en échec, erreurs de la nuit.", "Script de purge avec paramètres, -WhatIf, gestion d'erreurs et code de sortie.", "Tests Pester des parties portables, lancés en conteneur."],
  "Attendu : le rapport tient sur un écran et s'exporte en CSV ; la purge ne supprime rien avec -WhatIf ; les tests Pester passent dans le conteneur.")),

ch("Unix 6 — Scripts d'exploitation : qualité, sécurité, industrialisation", 'e',
 ["Un script d'exploitation est un logiciel : il a un en-tête, une aide, des journaux, des codes retour, un mode essai à blanc, des tests, et il vit dans un dépôt avec relecture.", "La sécurité des scripts : aucun secret en clair, droits minimaux, entrées validées, chemins vérifiés, pas d'évaluation de données externes.", "L'industrialisation : analyse (ShellCheck, PSScriptAnalyzer), tests (bats, Pester), livraison par la chaîne de livraison vers les serveurs, identique en intégration et en production."],
 ["Appliquer une convention de qualité à tous les scripts", "Sécuriser les scripts d'exploitation", "Tester et livrer les scripts comme du code"],
 [("La convention", "", CK("Chaque script d'exploitation", ["En-tête : rôle, auteur, usage, codes retour, dépendances", "Option d'aide (-h) et message d'usage", "Mode strict (Bash) ou $ErrorActionPreference = 'Stop' (PowerShell)", "Journal horodaté, niveau et contexte (environnement, hôte)", "Mode essai à blanc pour toute action destructive", "Codes retour documentés et testés", "Aucune valeur propre à un environnement en dur : fichier de paramètres"])),
  ("Sécurité des scripts", "", T([
    ("Secret en clair", "MDP=Prod2026! dans le script", "coffre (Vault, gestionnaire d'identifiants), variable injectée, read -s"),
    ("Évaluation de données", "eval \"$ligne_du_fichier\"", "jamais d'eval sur une entrée externe"),
    ("Chemin non vérifié", "rm -rf \"$1\"/*", "liste blanche, realpath, préfixe attendu"),
    ("Droits trop larges", "script lancé en root", "compte dédié, sudo limité à la commande"),
    ("Fichiers temporaires prévisibles", "/tmp/export.txt", "mktemp, droits restreints, nettoyage par trap")], ("Risque", "Exemple", "Parade"))),
  ("Tester et livrer", "", r"""# tests bats : tests/purge.bats
@test "refuse un dossier hors de /data" {
  run ./purge.sh -d /etc -j 30
  [ "$status" -eq 64 ]
}
@test "mode essai à blanc : rien n'est supprimé" {
  touch -d '40 days ago' "$BATS_TMPDIR/vieux.log"
  run ./purge.sh -d "$BATS_TMPDIR" -j 30 -n
  [ -f "$BATS_TMPDIR/vieux.log" ]
}
# CI : docker run --rm -v "$PWD:/mnt" koalaman/shellcheck:stable scripts/*.sh
#      docker run --rm -v "$PWD:/code" -w /code bats/bats:latest tests/
#      livraison : paquet versionné (ou dépôt) déployé sur les serveurs par la chaîne, identique en intégration et en production""")],
 [("Tu hérites de 60 scripts sans tests, avec des mots de passe en clair. Par où commences-tu ?", "Par les secrets : je les retire (coffre ou variables injectées) et je fais changer les mots de passe exposés ; puis je versionne tout, je passe ShellCheck, et j'ajoute des tests en commençant par les scripts critiques (purges, mises en production, chaînes de nuit)."),
  ("Question d'entretien : un script d'exploitation doit-il passer en revue de code ?", "Oui : il agit sur la production, souvent avec des droits élevés ; il suit les mêmes règles que le code applicatif (dépôt, MR, analyse, tests, livraison), avec une attention particulière aux suppressions, aux droits et aux secrets.")],
 ("Industrialiser les scripts", ["Dépôt des scripts avec convention appliquée à cinq scripts existants.", "Retirer tous les secrets, ajouter ShellCheck et PSScriptAnalyzer en CI.", "Tests bats et Pester des chemins critiques ; livraison automatisée vers deux environnements."],
  "Attendu : aucun secret dans le dépôt (vérifié par gitleaks) ; analyse et tests verts en CI ; les deux environnements reçoivent exactement la même version des scripts.")),
]
