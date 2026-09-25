"""Cours Microservices de zéro à expert (13 chapitres). Usage : python3 microservices_pages.py <dossier>"""
import sys, runpy, pathlib
g = runpy.run_path(pathlib.Path(__file__).with_name('front_gen.py'), run_name='front'); ch, page = g['ch'], g['page']
def T(rows, head): return '<div class="tablewrap"><table><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table></div>'
MVN = "Tout en conteneur : <code>alias mvn='docker run --rm -v \"$PWD:/app\" -w /app -v m2:/root/.m2 maven:3.9-eclipse-temurin-21 mvn'</code>, et chaque service tourne dans <code>eclipse-temurin:21-jre</code> par Docker Compose."

MS = [
ch("Fondamentaux : monolithe, monolithe modulaire, microservices", 'j',
 ["Un microservice est déployable seul, possède ses données et porte une responsabilité métier claire ; l'ensemble communique par le réseau.", "Le bénéfice est organisationnel (équipes autonomes, livraisons indépendantes) ; le coût est technique (réseau, cohérence, observabilité, exploitation).", "Par défaut, un monolithe modulaire bien découpé ; on extrait un service quand une équipe, une charge ou un rythme de livraison le justifie."],
 ["Distinguer monolithe, monolithe modulaire et microservices sans caricature", "Lister les coûts réels d'un système distribué", "Décider d'extraire un service avec des critères mesurables"],
 [("Trois architectures", T([
    ("Déploiement", "un seul artefact", "un seul artefact, modules isolés", "un artefact par service"),
    ("Données", "une base, tables partagées", "une base, un schéma par module", "une base par service"),
    ("Équipes", "une équipe, ou plusieurs qui se gênent", "une équipe par module", "une équipe par service ou groupe de services"),
    ("Complexité", "faible au départ, croît avec la taille", "faible, frontières contrôlées", "élevée dès le premier service"),
    ("Quand", "prototype, petit produit", "choix par défaut", "plusieurs équipes, besoins de charge ou de rythme distincts")], ("Critère", "Monolithe", "Monolithe modulaire", "Microservices")), None),
  ("Les illusions du réseau", "Le réseau n'est ni fiable, ni instantané, ni gratuit, ni sûr, et sa topologie change. Un appel de méthode devient un appel qui peut échouer, être lent ou arriver deux fois : il faut des délais d'expiration, des nouvelles tentatives bornées, de l'idempotence, du chiffrement et de l'observabilité dès le premier service.", """// dans un monolithe : un appel de méthode, dans la même transaction
incidentService.escalader(id);
// en microservices : un appel réseau, qui peut échouer, traîner ou être rejoué
restClient.post().uri("http://alertes/escalades")
    .header("Idempotency-Key", cle)          // rejouable sans doublon
    .body(new Escalade(id, niveau))
    .retrieve().toBodilessEntity();           // + délai d'expiration configuré sur le client"""),
  ("Quand extraire un service", "Les bonnes raisons : une équipe dédiée qui livre à son rythme, une charge très différente du reste, un besoin d'isolation (sécurité, conformité), une technologie spécifique. Les contre-indications : une petite équipe, un domaine encore instable, pas d'automatisation ni d'observabilité.", """Grille d'extraction (un service ne sort que si au moins deux critères sont vrais)
[ ] une équipe dédiée, qui livre plus souvent que le reste
[ ] une charge différente (×10 en pointe, ou calcul lourd)
[ ] une exigence d'isolation (données sensibles, conformité)
[ ] une frontière de domaine stable depuis six mois
Pré-requis non négociables : CI/CD par service, traces distribuées, tableau de bord, astreinte""")],
 [("Une équipe de quatre développeurs veut découper son application en douze microservices dès le départ. Que lui conseilles-tu ?", "Un monolithe modulaire : des modules aux frontières contrôlées (Spring Modulith ou ArchUnit), un schéma par module, puis l'extraction du module qui aura un vrai besoin. Douze services pour quatre personnes, c'est trois services par personne à exploiter, déployer et surveiller."),
  ("Question d'entretien : qu'est-ce qu'un monolithe distribué ?", "Des services qu'il faut modifier et déployer ensemble, couplés par une base partagée ou des chaînes d'appels synchrones : on paie le coût du distribué sans l'autonomie. Le test simple : peut-on déployer un service seul, sans prévenir les autres ?")],
 ("Monolithe modulaire CrisisShield", ["Découper CrisisShield (Spring Boot) en modules incidents, alertes, équipes et notifications avec Spring Modulith.", "Écrire les règles qui interdisent les dépendances non prévues et les faire échouer en CI.", "Rédiger une ADR : les critères qui déclencheraient l'extraction d'un module en service."],
  "Attendu : la vérification Spring Modulith échoue si notifications lit directement les tables d'incidents ; chaque module expose une API interne et publie des événements ; l'ADR liste trois critères mesurables (équipe dédiée, charge décuplée, livraison hebdomadaire contre mensuelle).")),

ch("Découper : domaine, bounded contexts, context map", 'c',
 ["On découpe selon le métier, pas selon les couches techniques : un bounded context a son vocabulaire, son modèle et son équipe.", "L'event storming fait apparaître événements, commandes et agrégats ; les frontières naturelles sont là où le vocabulaire change.", "La context map décrit les relations entre contextes : client-fournisseur, conformiste, couche anticorruption ; le noyau partagé est à éviter."],
 ["Animer un event storming et en tirer des bounded contexts", "Modéliser un agrégat avec ses invariants et ses événements", "Dessiner une context map et choisir chaque relation"],
 [("Du vocabulaire aux frontières", "Quand un même mot change de sens, on change de contexte : pour la cellule de crise, un « incident » a une gravité et une zone ; pour le support, c'est un ticket avec un demandeur. Deux modèles, deux contextes, reliés par des événements plutôt que par une table commune.", """Contextes de CrisisShield (issus de l'event storming)
Incidents      : IncidentDéclaré, IncidentEscaladé, IncidentClos        (agrégat Incident)
Mobilisation   : ÉquipeAffectée, ÉquipeLibérée                          (agrégat Équipe)
Alertes        : AlerteÉmise, SeuilFranchi                              (agrégat Règle)
Notifications  : NotificationEnvoyée, NotificationÉchouée               (pas d'agrégat métier : support)
Identité       : délégué à Keycloak                                     (générique : acheté, pas développé)"""),
  ("Agrégats et invariants", "Un agrégat protège ses règles : on ne le modifie que par ses méthodes, dans une seule transaction, et il publie des événements. Il est petit : une commande ne touche qu'un agrégat ; plusieurs agrégats se coordonnent par événements.", """public class Incident {                                 // racine d'agrégat
  private final IncidentId id; private Statut statut = Statut.OUVERT; private int niveau = 1;
  private final List<Object> evenements = new ArrayList<>();
  public void escalader(int nouveauNiveau) {
    if (statut != Statut.OUVERT) throw new IllegalStateException("incident clos");   // invariant
    if (nouveauNiveau <= niveau) throw new IllegalArgumentException("niveau croissant");
    niveau = nouveauNiveau;
    evenements.add(new IncidentEscalade(id, niveau, Instant.now()));                   // fait publié
  }
  public List<Object> evenementsAPublier() { return List.copyOf(evenements); }
}"""),
  ("La context map", "Chaque flèche dit qui dépend de qui et comment : une couche anticorruption traduit le modèle d'un système externe pour ne pas le laisser contaminer le vôtre ; un client-fournisseur négocie le contrat ; un conformiste l'accepte tel quel.", """┌────────────┐  événements   ┌──────────────┐
│ Incidents  │ ────────────▶ │ Mobilisation │   client-fournisseur
└─────┬──────┘               └──────────────┘
      │ événements
      ▼
┌────────────┐   ACL    ┌──────────────────────┐
│ Alertes    │ ◀─────── │ Météo-France (externe)│  couche anticorruption
└────────────┘          └──────────────────────┘
Notifications : conformiste des événements publiés ; Identité : Keycloak (générique)""")],
 [("Une équipe propose trois services : « frontend », « métier » et « base de données ». Qu'en penses-tu ?", "C'est un découpage par couches techniques : chaque fonctionnalité touche les trois services, qui se déploient ensemble. On découpe par capacité métier (incidents, mobilisation, alertes), chaque service ayant sa propre interface, sa logique et ses données."),
  ("Question d'entretien : qu'est-ce qu'un bounded context ?", "La frontière dans laquelle un modèle et son vocabulaire sont cohérents ; au-delà, les mêmes mots peuvent avoir un autre sens. Un microservice correspond souvent à un bounded context, ou à une partie, jamais à plusieurs contextes mélangés.")],
 ("Event storming sur CrisisShield", ["Animer une session de 90 minutes (ou la simuler) : événements en orange, commandes en bleu, agrégats en jaune, systèmes externes en rose.", "En tirer quatre ou cinq bounded contexts et le glossaire de chacun.", "Dessiner la context map et justifier chaque relation dans une ADR."],
  "Attendu : une trentaine d'événements au passé ; des frontières placées là où le vocabulaire change ; une couche anticorruption devant chaque système externe ; aucun noyau partagé sans justification écrite.")),

ch("Communication synchrone : REST, gRPC, contrats", 'c',
 ["Un appel synchrone couple les disponibilités : si le service appelé tombe ou ralentit, l'appelant attend ou échoue.", "Le contrat est explicite (OpenAPI, protobuf), versionné, rétrocompatible, avec des erreurs normalisées et des clés d'idempotence pour les écritures.", "Toujours un délai d'expiration ; jamais une chaîne de cinq appels synchrones pour répondre à un utilisateur."],
 ["Concevoir une API REST qui évolue sans casser ses clients", "Appeler un service avec délais, idempotence et erreurs lisibles", "Choisir entre REST et gRPC"],
 [("Un contrat qui évolue sans casser", "Ajouter un champ optionnel est sans risque ; supprimer ou renommer un champ casse les clients. Le client lit avec tolérance (il ignore l'inconnu), le fournisseur n'enlève rien sans période de dépréciation, et une version majeure coexiste avec l'ancienne le temps de la migration.", """# openapi.yaml (extrait)
paths:
  /v1/incidents/{id}/escalades:
    post:
      parameters:
        - { name: Idempotency-Key, in: header, required: true, schema: { type: string, format: uuid } }
      responses:
        "202": { description: escalade acceptée }
        "409": { description: incident clos, content: { application/problem+json: { schema: { $ref: "#/components/schemas/Problem" } } } }
# règle : ajout de champ = compatible ; suppression ou renommage = nouvelle version /v2, et /v1 dépréciée avec l'en-tête Deprecation"""),
  ("Appeler un service proprement", MVN, """@Bean RestClient alertesClient(RestClient.Builder b) {
  var http = HttpClient.newBuilder().connectTimeout(Duration.ofMillis(500)).build();
  var rf = new JdkClientHttpRequestFactory(http); rf.setReadTimeout(Duration.ofSeconds(2));   // jamais de délai infini
  return b.baseUrl("http://alertes:8080").requestFactory(rf).build();
}
public void escalader(IncidentId id, int niveau) {
  alertes.post().uri("/v1/incidents/{id}/escalades", id.valeur())
    .header("Idempotency-Key", UUID.nameUUIDFromBytes((id + ":" + niveau).getBytes()).toString())   // même clé si rejoué
    .body(new Escalade(niveau)).retrieve()
    .onStatus(s -> s.value() == 409, (req, resp) -> { throw new IncidentClosException(id); })          // ProblemDetail lu, pas ignoré
    .toBodilessEntity();
}"""),
  ("REST ou gRPC", "REST et JSON conviennent aux API publiques et aux navigateurs ; gRPC apporte un contrat fort, du binaire compact, du streaming et de la génération de code, utile entre services internes à fort trafic. Dans les deux cas : délais, idempotence et compatibilité ascendante.", """// incidents.proto : les numéros de champ ne changent jamais, on n'en réutilise jamais
syntax = "proto3";
service Incidents { rpc Escalader(EscaladeRequest) returns (EscaladeReponse); }
message EscaladeRequest { string incident_id = 1; int32 niveau = 2; string cle_idempotence = 3; }
message EscaladeReponse { bool acceptee = 1; }""")],
 [("Un service appelle quatre autres services en série pour afficher une page : que se passe-t-il pour la disponibilité ?", "Elle se multiplie : 99,9 % à la puissance cinq donne 99,5 %, soit dix fois plus d'indisponibilité, et les latences s'additionnent. On parallélise les appels, on met en cache, on passe en asynchrone ou on maintient une vue locale alimentée par événements."),
  ("Question d'entretien : pourquoi une clé d'idempotence ?", "Parce qu'une nouvelle tentative après un délai dépassé peut rejouer une écriture déjà faite. Le serveur mémorise la clé et renvoie le même résultat sans refaire l'action : on peut réessayer sans créer de doublon.")],
 ("API d'escalade entre deux services", ["Service Incidents et service Alertes en Spring Boot, en Compose ; contrat OpenAPI versionné, vérifié en CI (openapi-diff).", "Client avec délais, clé d'idempotence stockée côté serveur (table idempotence), erreurs ProblemDetail.", "Rejouer dix fois la même requête et couper le service Alertes pendant l'appel : aucun doublon, erreur lisible."],
  "Attendu : dix requêtes identiques produisent une seule escalade ; un changement de contrat qui supprime un champ fait échouer openapi-diff en CI ; Alertes arrêté donne une erreur en deux secondes, pas un blocage.")),

ch("Communication asynchrone : événements et Kafka", 'c',
 ["Un événement dit ce qui s'est passé (IncidentEscaladé) ; une commande demande une action (EnvoyerNotification) : les confondre crée du couplage.", "Kafka garantit l'ordre par partition : la clé de message (l'identifiant d'incident) garde les événements d'un même incident dans l'ordre.", "La livraison est « au moins une fois » : chaque consommateur doit être idempotent, et le schéma des événements évolue de façon compatible."],
 ["Publier des événements ordonnés et versionnés", "Écrire un consommateur idempotent avec file des messages en échec", "Faire évoluer un schéma sans casser les consommateurs"],
 [("Topics, partitions, groupes", "Un topic est découpé en partitions ; l'ordre n'existe qu'au sein d'une partition ; tous les messages d'une même clé vont dans la même partition. Un groupe de consommateurs se partage les partitions : pour lire plus vite, on ajoute des consommateurs, dans la limite du nombre de partitions.", """# compose : Kafka en mode KRaft
kafka: { image: apache/kafka:3.8.0, ports: ["9092:9092"] }
# producteur Spring : la clé = l'identifiant d'incident → ordre garanti par incident
kafka.send("incidents.evenements.v1", incident.id().toString(), new IncidentEscalade(id, niveau, maintenant));
# réglages producteur : acks=all, enable.idempotence=true, retries élevés (pas de doublon côté broker)"""),
  ("Un consommateur idempotent", "Le même message peut arriver deux fois (redémarrage, rééquilibrage). On mémorise l'identifiant de l'événement dans la même transaction que l'effet ; un doublon est reconnu et ignoré. Les messages qui échouent après quelques tentatives partent dans un topic d'échec, surveillé.", """@KafkaListener(topics = "incidents.evenements.v1", groupId = "notifications")
@Transactional
public void surEvenement(IncidentEscalade e, @Header(KafkaHeaders.RECEIVED_KEY) String cle) {
  if (!dejaTraites.insererSiAbsent(e.eventId())) return;   // INSERT … ON CONFLICT DO NOTHING : doublon ignoré
  notifications.preparer(e);                               // effet dans la même transaction
}
@Bean DefaultErrorHandler erreurs(KafkaTemplate<?, ?> t) {
  return new DefaultErrorHandler(new DeadLetterPublishingRecoverer(t), new ExponentialBackOff(500, 2.0) {{ setMaxElapsedTime(10_000); }});
}   // après ~10 s d'échecs : topic incidents.evenements.v1.DLT, alerte si non vide"""),
  ("Faire évoluer un schéma", "Un événement publié est un contrat avec des consommateurs inconnus. On ajoute des champs optionnels, on ne supprime ni ne renomme ; le registre de schémas vérifie la compatibilité avant publication, et un changement incompatible passe par un nouveau topic versionné.", """# registre de schémas (Apicurio ou Confluent) : compatibilité BACKWARD sur le sujet
curl -X PUT -d '{"compatibility":"BACKWARD"}' http://registry:8081/config/incidents.evenements.v1-value
# en CI : le nouveau schéma est testé contre le registre avant la fusion
curl -X POST -d @IncidentEscalade.avsc http://registry:8081/compatibility/subjects/incidents.evenements.v1-value/versions/latest
# incompatible → topic incidents.evenements.v2, double publication le temps de migrer les consommateurs""")],
 [("Pourquoi utiliser l'identifiant d'incident comme clé de message ?", "Pour que tous les événements d'un même incident aillent dans la même partition, donc soient lus dans l'ordre (déclaré, puis escaladé, puis clos). Sans clé, un « clos » peut être traité avant un « escaladé »."),
  ("Question d'entretien : exactly-once, ça existe ?", "Kafka offre des transactions entre topics Kafka, mais dès qu'un effet sort de Kafka (base, e-mail), on vise « au moins une fois » plus un consommateur idempotent : c'est ce qui garantit l'effet unique de bout en bout.")],
 ("Notifications pilotées par événements", ["Incidents publie IncidentEscaladé avec la clé d'incident ; Notifications consomme et prépare un message.", "Rendre le consommateur idempotent (table des événements traités) et configurer le topic d'échec avec une alerte.", "Faire évoluer le schéma (champ optionnel zone) avec contrôle de compatibilité en CI ; tenter un renommage et le voir refusé."],
  "Attendu : un redémarrage du consommateur au milieu d'un lot ne crée aucune notification en double ; un message invalide finit dans le topic d'échec après dix secondes et déclenche une alerte ; le renommage de champ est refusé par le registre.")),

ch("Données distribuées : une base par service, saga, outbox", 's',
 ["Chaque service possède ses données : aucun autre ne lit ni n'écrit ses tables ; on partage par API ou par événements.", "Sans transaction distribuée, une opération sur plusieurs services est une saga : une suite d'étapes locales avec des compensations en cas d'échec.", "Écrire en base puis publier un événement peut échouer à moitié : le modèle outbox écrit l'événement dans la même transaction, un relais le publie ensuite."],
 ["Expliquer pourquoi la base partagée tue l'autonomie", "Concevoir une saga orchestrée avec ses compensations", "Mettre en place l'outbox transactionnel avec Debezium"],
 [("Une base par service", "Une table partagée est un contrat invisible : renommer une colonne casse un service qu'on ne connaît pas, et deux équipes ne peuvent plus livrer seules. Chaque service a sa base (ou au minimum son schéma avec des droits séparés) ; les autres passent par son API ou ses événements.", """-- chaque service a son utilisateur de base et ne voit que son schéma
CREATE ROLE svc_incidents LOGIN PASSWORD :'pw_incidents';
CREATE SCHEMA incidents AUTHORIZATION svc_incidents;
REVOKE ALL ON SCHEMA incidents FROM PUBLIC;          -- mobilisation ne peut pas lire incidents.*
-- besoin de données d'un autre service : son API, ou une copie locale alimentée par ses événements"""),
  ("La saga orchestrée", "Ouvrir une cellule de crise demande trois étapes dans trois services. L'orchestrateur envoie chaque commande, attend la réponse et, si une étape échoue, déclenche les compensations des étapes réussies, dans l'ordre inverse. Chaque étape et chaque compensation sont idempotentes.", """Saga « ouvrir une cellule de crise » (orchestrateur dans Incidents)
1. Mobilisation : réserver l'équipe        compensation : libérer l'équipe
2. Communication : créer le canal de crise  compensation : archiver le canal
3. Notifications : prévenir les astreintes  (dernière étape : pas de compensation)
échec en 2 → libérer l'équipe → saga en état ÉCHOUÉE, visible et relançable
état de la saga persisté (table saga, étape courante) : un redémarrage reprend où il en était"""),
  ("Le modèle outbox", "On insère l'événement dans une table outbox dans la même transaction que la modification métier ; Debezium lit le journal de PostgreSQL et publie les lignes dans Kafka. Plus d'écriture double : soit les deux sont faits, soit aucun.", """@Transactional
public void escalader(IncidentId id, int niveau) {
  var incident = repo.charger(id); incident.escalader(niveau); repo.save(incident);
  outbox.save(new OutboxEvent(UUID.randomUUID(), "Incident", id.toString(), "IncidentEscalade", json(incident.evenementsAPublier())));
}   // un seul COMMIT : métier + événement
# connecteur Debezium (Kafka Connect) : routage des lignes outbox vers les topics
{ "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
  "table.include.list": "incidents.outbox",
  "transforms": "outbox", "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter" }""")],
 [("Pourquoi ne pas simplement enregistrer en base puis appeler kafka.send() ?", "Si l'application tombe entre les deux, la base est modifiée sans événement (ou l'inverse si on publie d'abord) : les autres services divergent en silence. L'outbox met l'événement dans la même transaction que la donnée."),
  ("Question d'entretien : chorégraphie ou orchestration ?", "La chorégraphie (chacun réagit aux événements) convient à deux ou trois étapes ; au-delà, le déroulé devient invisible. L'orchestration centralise l'état et les compensations dans un seul endroit, plus facile à suivre et à relancer.")],
 ("Saga et outbox sur CrisisShield", ["Séparer les bases d'Incidents et de Mobilisation (deux schémas, deux rôles), vérifier qu'aucune requête ne traverse.", "Implémenter la saga « ouvrir une cellule de crise » avec état persisté et compensations.", "Mettre en place l'outbox et Debezium en Compose ; couper l'application entre deux étapes et vérifier la reprise."],
  "Attendu : l'échec provoqué de l'étape 2 libère l'équipe réservée et passe la saga en ÉCHOUÉE ; un arrêt brutal pendant la saga reprend au redémarrage ; aucun événement perdu ni doublé entre la base et Kafka sur mille escalades.")),

ch("Lire à travers les services : composition, CQRS, event sourcing", 's',
 ["Quand une page a besoin des données de plusieurs services, on compose les appels en parallèle, ou on construit une vue de lecture alimentée par leurs événements.", "Le CQRS sépare le modèle d'écriture (qui protège les règles) du modèle de lecture (optimisé pour les requêtes) ; la vue est cohérente à terme.", "L'event sourcing stocke les événements comme source de vérité : puissant pour l'audit, coûteux à exploiter ; à réserver aux domaines qui en ont besoin."],
 ["Composer des appels en parallèle avec des délais", "Construire une vue de lecture par projection d'événements", "Décider quand l'event sourcing se justifie"],
 [("La composition d'API", "Pour quelques services et un besoin temps réel, le BFF appelle les services en parallèle, avec un délai par appel et une réponse partielle si l'un est lent. Au-delà de trois ou quatre sources, ou pour des requêtes lourdes, une vue dédiée s'impose.", """// BFF : appels parallèles, réponse partielle si un service est lent
var incidents = CompletableFuture.supplyAsync(() -> incidentsApi.ouverts(zone), pool).orTimeout(800, MILLISECONDS);
var equipes   = CompletableFuture.supplyAsync(() -> mobilisationApi.disponibles(zone), pool).orTimeout(800, MILLISECONDS);
var meteo     = CompletableFuture.supplyAsync(() -> alertesApi.vigilance(zone), pool).completeOnTimeout(null, 500, MILLISECONDS);
return new TableauDeBord(incidents.join(), equipes.join(), meteo.join());   // la météo peut manquer, pas le reste"""),
  ("Une vue de lecture par projection", "Un service de lecture consomme les événements des autres et tient à jour une table taillée pour l'écran : une ligne par incident avec son équipe et sa vigilance. La vue a quelques secondes de retard : on l'affiche, avec l'heure de mise à jour.", """@KafkaListener(topics = {"incidents.evenements.v1", "mobilisation.evenements.v1"}, groupId = "tableau-de-bord")
@Transactional
public void projeter(ConsumerRecord<String, Evenement> r) {
  if (!dejaTraites.insererSiAbsent(r.value().eventId())) return;
  switch (r.value()) {
    case IncidentDeclare e -> vue.inserer(e.incidentId(), e.zone(), e.gravite(), e.date());
    case EquipeAffectee e  -> vue.affecterEquipe(e.incidentId(), e.equipe(), e.date());
    case IncidentClos e    -> vue.clore(e.incidentId(), e.date());
    default -> { }
  }
}   // reconstruire la vue : remettre le groupe au début du topic, vider la table, rejouer"""),
  ("Event sourcing : quand", "L'état n'est plus stocké : on le recalcule à partir des événements. On y gagne un historique complet et la possibilité de reconstruire toute vue ; on y perd en simplicité (schémas d'événements éternels, instantanés, requêtes). Justifié pour l'audit réglementaire ou un domaine centré sur l'historique ; sinon, l'outbox suffit.", None)],
 [("La vue du tableau de bord affiche un incident clos il y a trente secondes comme ouvert. Est-ce un bug ?", "Pas forcément : c'est la cohérence à terme. On affiche l'heure de dernière mise à jour, on surveille le retard de la projection (lag du groupe de consommateurs), et on alerte s'il dépasse le seuil convenu, par exemple dix secondes."),
  ("Question d'entretien : CQRS veut-il dire event sourcing ?", "Non : on peut séparer lecture et écriture avec une vue alimentée par l'outbox, sans stocker l'état sous forme d'événements. L'event sourcing est un choix supplémentaire, à justifier séparément.")],
 ("Tableau de bord de crise", ["BFF qui compose trois services en parallèle avec délais et réponse partielle.", "Service de lecture qui projette les événements d'Incidents et de Mobilisation dans une table dédiée.", "Mesurer le retard de la projection et reconstruire la vue en rejouant les topics."],
  "Attendu : le tableau de bord répond en moins de 300 ms à partir de la vue ; la météo lente n'empêche pas l'affichage ; la vue reconstruite à partir de zéro est identique à l'originale ; une alerte se déclenche si le retard dépasse dix secondes.")),

ch("Résilience : délais, nouvelles tentatives, disjoncteur, cloisons", 's',
 ["Chaque appel a un délai d'expiration, et la somme reste inférieure au délai de l'appelant : c'est le budget de latence.", "Les nouvelles tentatives sont bornées, espacées avec un aléa, et réservées aux opérations idempotentes ; sinon elles amplifient la panne.", "Le disjoncteur arrête d'appeler un service en échec ; les cloisons empêchent un service lent de consommer tous les fils d'exécution."],
 ["Fixer un budget de latence et des délais cohérents", "Configurer nouvelles tentatives, disjoncteur et cloisons avec Resilience4j", "Provoquer une panne réseau et vérifier que le système se dégrade proprement"],
 [("Budget et délais", "Si l'utilisateur attend au plus deux secondes, le BFF donne 1,5 s à ses appels, chaque service 800 ms aux siens. Sans délai, un service lent bloque des fils d'exécution jusqu'à épuisement, et la panne remonte toute la chaîne.", """Budget de latence (du plus haut au plus bas)
navigateur : 2 000 ms → BFF : 1 500 ms → Incidents : 800 ms → base : 300 ms
règle : délai de l'appelé < délai de l'appelant ; propager l'échéance (en-tête ou contexte gRPC deadline)"""),
  ("Resilience4j", "Les nouvelles tentatives utilisent un recul exponentiel avec aléa, le disjoncteur s'ouvre au-delà d'un taux d'échec et laisse passer quelques essais après un délai, la cloison limite les appels simultanés vers une dépendance.", """resilience4j:
  retry.instances.alertes: { maxAttempts: 3, waitDuration: 200ms, enableExponentialBackoff: true, exponentialBackoffMultiplier: 2, enableRandomizedWait: true }
  circuitbreaker.instances.alertes: { slidingWindowSize: 20, failureRateThreshold: 50, slowCallDurationThreshold: 1s, waitDurationInOpenState: 10s, permittedNumberOfCallsInHalfOpenState: 3 }
  bulkhead.instances.alertes: { maxConcurrentCalls: 20, maxWaitDuration: 0 }
---
@Retry(name = "alertes") @CircuitBreaker(name = "alertes", fallbackMethod = "vigilanceInconnue") @Bulkhead(name = "alertes")
public Vigilance vigilance(String zone) { return alertesClient.vigilance(zone); }
Vigilance vigilanceInconnue(String zone, Throwable t) { return Vigilance.inconnue(zone); }   // dégradé, affiché comme tel"""),
  ("Tester la dégradation", "La résilience se prouve : Toxiproxy ajoute de la latence ou coupe la connexion entre deux services, et l'on vérifie que l'utilisateur obtient une réponse dégradée rapide plutôt qu'une page qui tourne.", """# compose : toxiproxy entre incidents et alertes
toxiproxy: { image: ghcr.io/shopify/toxiproxy:2.9.0 }
docker compose exec toxiproxy /toxiproxy-cli toxic add -t latency -a latency=3000 alertes
# attendu : disjoncteur ouvert en quelques secondes, vigilance « inconnue », p99 du tableau de bord < 2 s
docker compose exec toxiproxy /toxiproxy-cli toxic remove -n latency_downstream alertes""")],
 [("Une panne de 30 secondes sur Alertes devient une panne de 10 minutes sur tout le système. Hypothèse ?", "Une tempête de nouvelles tentatives : chaque niveau réessaie trois fois, sans aléa, et multiplie la charge par 27 sur un service déjà en difficulté, qui ne peut plus redémarrer. Remède : tentatives à un seul niveau, recul avec aléa, disjoncteur, budget de nouvelles tentatives."),
  ("Question d'entretien : à quoi sert un disjoncteur ?", "À cesser d'appeler un service qui échoue, pour ne pas bloquer ses propres ressources et laisser l'autre récupérer ; après un délai, quelques appels d'essai décident de le refermer.")],
 ("Panne provoquée, dégradation maîtrisée", ["Placer Toxiproxy entre Incidents et Alertes ; mesurer le tableau de bord sans protection avec trois secondes de latence injectée.", "Ajouter délais, nouvelles tentatives, disjoncteur, cloison et repli ; rejouer la même panne.", "Tableau avant/après : temps de réponse, fils d'exécution occupés, erreurs vues par l'utilisateur."],
  "Attendu : sans protection, p99 au-delà de 30 s et fils d'exécution saturés ; avec, disjoncteur ouvert en moins de dix secondes, réponse dégradée en moins de deux secondes, et récupération automatique après suppression de la latence.")),

ch("Passerelle d'API, BFF, découverte et configuration", 'c',
 ["La passerelle d'API est la porte d'entrée : routage, authentification, limitation de débit, observabilité ; elle ne contient aucune logique métier.", "Un BFF (backend for frontend) adapte les API à un client précis (web, mobile) : il compose et simplifie, sans reprendre les règles du domaine.", "Dans Kubernetes, la découverte passe par les Services et le DNS ; la configuration par variables, ConfigMaps et un coffre pour les secrets."],
 ["Configurer une passerelle fine (routage, jetons, débit)", "Délimiter ce qui revient au BFF et au service", "Organiser découverte et configuration dans Kubernetes"],
 [("Une passerelle fine", "Si la passerelle calcule des remises ou valide des règles métier, chaque changement métier passe par elle : elle devient un monolithe central. Elle route, vérifie le jeton, limite le débit et trace ; le reste appartient aux services.", """# Spring Cloud Gateway : routage, jeton relayé, limitation de débit
spring.cloud.gateway.routes:
  - id: incidents
    uri: http://incidents:8080
    predicates: [ "Path=/api/incidents/**" ]
    filters:
      - TokenRelay=
      - name: RequestRateLimiter
        args: { redis-rate-limiter.replenishRate: 50, redis-rate-limiter.burstCapacity: 100, key-resolver: "#{@parUtilisateur}" }
      - StripPrefix=1"""),
  ("Le BFF", "Le BFF web assemble le tableau de bord en un appel ; le BFF mobile renvoie une version allégée. Chacun appartient à l'équipe du client concerné, et aucune règle métier n'y est dupliquée : il appelle les services, qui décident.", None),
  ("Découverte et configuration", "Un Service Kubernetes donne un nom DNS stable devant des Pods qui changent : plus besoin de registre comme Eureka. La configuration vient de l'environnement (profils, variables), les secrets d'un coffre (Vault ou External Secrets), jamais de l'image.", """# un service appelle simplement http://alertes:8080 (même espace de noms) ou http://alertes.crise.svc.cluster.local
apiVersion: v1
kind: Service
metadata: { name: alertes, namespace: crise }
spec: { selector: { app: alertes }, ports: [ { port: 8080, targetPort: 8080 } ] }
---
env:
  - { name: SPRING_PROFILES_ACTIVE, value: prod }
  - { name: ALERTES_URL, value: "http://alertes:8080" }
  - { name: DB_PASSWORD, valueFrom: { secretKeyRef: { name: incidents-db, key: password } } }   # alimenté par External Secrets""")],
 [("L'équipe veut mettre la vérification « un incident clos ne peut pas être escaladé » dans la passerelle, « pour la faire une seule fois ». Réponse ?", "Non : c'est une règle du domaine Incidents, elle vit dans l'agrégat Incident. La passerelle ne connaît pas l'état des incidents ; y mettre du métier la transforme en goulot et duplique les règles."),
  ("Question d'entretien : pourquoi un BFF plutôt qu'une API générique ?", "Parce que chaque client a ses besoins (volume, forme, performances) : un BFF par client évite une API générique pleine de paramètres, et laisse l'équipe du client évoluer sans attendre les équipes des services.")],
 ("Porte d'entrée de CrisisShield", ["Spring Cloud Gateway devant Incidents et Mobilisation : routage, relais du jeton, limitation de débit par utilisateur avec Redis.", "BFF web qui compose le tableau de bord ; BFF mobile allégé.", "Déploiement Kubernetes : Services DNS, configuration par profils, secrets via External Secrets."],
  "Attendu : au-delà de 100 requêtes en rafale, la passerelle renvoie 429 ; aucun appel sans jeton ne passe ; le BFF mobile renvoie une réponse trois fois plus légère ; aucun secret dans les images (vérifié par Trivy).")),

ch("Sécurité entre services", 's',
 ["L'utilisateur s'authentifie une fois (OIDC, Keycloak) ; chaque service valide lui-même le jeton : signature, émetteur, audience, expiration.", "Entre services, on ne fait pas suivre un jeton qui ouvre tout : échange de jeton pour une audience précise, ou identité de service (client credentials, mTLS).", "Zéro confiance : le réseau interne n'est pas sûr ; chiffrement mTLS, politiques réseau et autorisation à chaque service."],
 ["Configurer chaque service comme serveur de ressources OAuth2", "Choisir entre jeton propagé, échange de jeton et identité de service", "Chiffrer et restreindre les échanges internes"],
 [("Chaque service valide son jeton", "Un service qui fait confiance à « ce qui vient de la passerelle » est ouvert à quiconque atteint le réseau interne. Chacun vérifie la signature, l'émetteur, l'audience (le jeton m'est-il destiné ?) et les droits pour l'action demandée.", """spring.security.oauth2.resourceserver.jwt:
  issuer-uri: https://sso.crisis.fr/realms/crisis
  audiences: [ incidents ]                               # un jeton pour « mobilisation » est refusé ici
---
@Bean SecurityFilterChain api(HttpSecurity http) throws Exception {
  return http.authorizeHttpRequests(a -> a
      .requestMatchers(HttpMethod.POST, "/v1/incidents/*/escalades").hasAuthority("SCOPE_incidents:escalader")
      .anyRequest().authenticated())
    .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults())).build();
}"""),
  ("Appeler un autre service au nom de l'utilisateur", "Propager le jeton de l'utilisateur donne au service appelé tout ce que ce jeton permet. L'échange de jeton (RFC 8693) produit un jeton limité à l'audience du service appelé ; pour un traitement sans utilisateur, le service utilise sa propre identité.", """# échange de jeton auprès de Keycloak : audience restreinte à mobilisation
curl -s https://sso.crisis.fr/realms/crisis/protocol/openid-connect/token \\
  -d grant_type=urn:ietf:params:oauth:grant-type:token-exchange \\
  -d client_id=incidents -d client_secret="$CLIENT_SECRET" \\
  -d subject_token="$JETON_UTILISATEUR" -d audience=mobilisation
# traitement de nuit, sans utilisateur : client credentials avec un rôle minimal
-d grant_type=client_credentials -d client_id=projection-nuit"""),
  ("mTLS et politiques réseau", "Le mTLS prouve l'identité du service appelant et chiffre l'échange ; un maillage (Istio, Linkerd) ou SPIFFE le gère automatiquement. Les NetworkPolicies limitent qui peut parler à qui : notifications n'a aucune raison de joindre la base d'incidents.", """apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: strict, namespace: crise }
spec: { mtls: { mode: STRICT } }
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: incidents-db, namespace: crise }
spec:
  podSelector: { matchLabels: { app: incidents-db } }
  ingress: [ { from: [ { podSelector: { matchLabels: { app: incidents } } } ] } ]   # seul incidents joint sa base""")],
 [("Un service interne compromis réutilise le jeton d'un utilisateur pour appeler tous les autres services. Qu'est-ce qui aurait dû l'en empêcher ?", "La vérification d'audience dans chaque service (le jeton n'était destiné qu'à un seul), l'échange de jeton pour les appels suivants, des portées minimales, et des NetworkPolicies qui limitent les chemins possibles."),
  ("Question d'entretien : que vérifie un service qui reçoit un JWT ?", "La signature avec la clé publique de l'émetteur (JWKS), l'émetteur, l'audience, l'expiration, puis les portées ou rôles pour l'action ; il refuse l'algorithme none et ne fait confiance à aucun en-tête ajouté par un intermédiaire.")],
 ("Sécuriser les échanges de CrisisShield", ["Keycloak en Compose ; chaque service configuré en serveur de ressources avec audience et portées.", "Échange de jeton pour l'appel Incidents vers Mobilisation ; identité de service pour la projection de nuit.", "mTLS strict et NetworkPolicies dans le cluster ; tests d'intrusion simples."],
  "Attendu : un jeton destiné à Mobilisation est refusé par Incidents (401) ; un appel direct à la base d'incidents depuis notifications échoue (NetworkPolicy) ; en mTLS strict, un Pod hors maillage ne joint plus aucun service.")),

ch("Observabilité distribuée", 's',
 ["Une requête traverse plusieurs services : sans trace distribuée, un incident se diagnostique à coups de grep sur neuf journaux.", "Le contexte de trace (traceparent W3C) voyage dans les en-têtes HTTP et dans les en-têtes des messages Kafka ; OpenTelemetry l'instrumente sans modifier le code.", "Par service : métriques RED (débit, erreurs, durée), journaux avec l'identifiant de trace, SLO ; pour l'utilisateur : un SLO par parcours."],
 ["Propager le contexte de trace en synchrone et en asynchrone", "Relier traces, métriques et journaux par l'identifiant de trace", "Définir des SLO par service et par parcours utilisateur"],
 [("OpenTelemetry sans toucher au code", "L'agent Java instrumente Spring, JDBC, RestClient et Kafka ; chaque service envoie ses traces au collecteur, qui les route vers Tempo ou Jaeger, et ses métriques vers Prometheus.", """# compose (extrait) : même agent pour tous les services Java
incidents:
  image: crisisshield/incidents:1.4.2
  environment:
    JAVA_TOOL_OPTIONS: "-javaagent:/otel/opentelemetry-javaagent.jar"
    OTEL_SERVICE_NAME: incidents
    OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
    OTEL_PROPAGATORS: tracecontext,baggage
  volumes: [ "./otel:/otel:ro" ]
otel-collector: { image: otel/opentelemetry-collector-contrib:0.110.0, volumes: [ "./otel-collector.yaml:/etc/otelcol-contrib/config.yaml" ] }"""),
  ("Relier les trois signaux", "Chaque ligne de journal porte l'identifiant de trace ; un clic dans Grafana passe de la métrique au journal, puis à la trace complète. Le tableau de bord par service affiche les métriques RED et le budget d'erreur restant.", """# logback : l'identifiant de trace dans chaque ligne (JSON)
<pattern>{"t":"%d{ISO8601}","niveau":"%level","service":"incidents","traceId":"%X{trace_id}","spanId":"%X{span_id}","msg":"%message"}%n</pattern>
# PromQL : taux d'erreur par service (RED)
sum by (service) (rate(http_server_requests_seconds_count{status=~"5.."}[5m])) / sum by (service) (rate(http_server_requests_seconds_count[5m]))
# SLO de parcours « déclarer un incident » : 99,5 % des déclarations acceptées en moins d'une seconde, mesurées à la passerelle"""),
  ("Ce qu'on regarde en premier", "Quand un parcours se dégrade : la carte des services pour voir où se trouve l'erreur, la trace la plus lente pour voir quel appel domine, puis les journaux de ce service filtrés sur l'identifiant de trace. On mesure aussi le retard des consommateurs Kafka, souvent la cause silencieuse.", None)],
 [("Une trace s'arrête au producteur Kafka : le consommateur crée une nouvelle trace. Pourquoi ?", "Le contexte n'est pas propagé dans les en-têtes du message, ou le consommateur n'est pas instrumenté. Avec l'agent OpenTelemetry sur les deux services et des en-têtes conservés par le broker, la trace continue."),
  ("Question d'entretien : pourquoi un SLO par parcours et pas seulement par service ?", "Parce que l'utilisateur vit un parcours qui traverse plusieurs services : chacun peut respecter son SLO et le parcours échouer quand même. Le SLO de parcours, mesuré à l'entrée, dit ce que l'utilisateur vit ; ceux des services aident à trouver la cause.")],
 ("Voir une requête de bout en bout", ["Agent OpenTelemetry sur tous les services, collecteur, Tempo, Prometheus, Loki, Grafana en Compose.", "Suivre une déclaration d'incident : passerelle, Incidents, Kafka, Notifications, dans une seule trace.", "Tableau de bord RED par service, SLO du parcours « déclarer un incident », alerte sur le retard des consommateurs."],
  "Attendu : une seule trace de la passerelle jusqu'à la notification, Kafka compris ; depuis un pic d'erreurs, trois clics mènent à la ligne de journal fautive ; l'alerte de retard se déclenche quand on arrête Notifications.")),

ch("Tester des microservices : contrats, composants, bout en bout", 's',
 ["Les tests de bout en bout sur un environnement partagé sont lents, fragiles et toujours cassés : on les réduit au strict nécessaire.", "Chaque service est testé comme un composant, avec ses vraies dépendances en conteneur (Testcontainers) et les autres services simulés.", "Les tests de contrat pilotés par le consommateur (Pact) prouvent que fournisseur et consommateur s'entendent, avant tout déploiement."],
 ["Construire la pyramide de tests d'un microservice", "Écrire un contrat consommateur et le vérifier côté fournisseur", "Bloquer un déploiement incompatible avec can-i-deploy"],
 [("La pyramide d'un microservice", "À la base les tests unitaires du domaine, puis les tests de composant (le service entier, sa base et Kafka en conteneurs, les autres services simulés), puis les contrats. Quelques parcours de bout en bout seulement, en supervision synthétique sur les environnements réels.", """Pyramide d'un service
  quelques parcours de bout en bout (supervision synthétique, Playwright)
  contrats consommateur / fournisseur (Pact, HTTP et messages)
  tests de composant : le service + PostgreSQL + Kafka (Testcontainers), dépendances simulées (WireMock)
  tests unitaires du domaine (agrégats, règles), les plus nombreux"""),
  ("Un contrat piloté par le consommateur", "Le consommateur écrit ce qu'il attend du fournisseur ; le contrat est publié dans un broker ; le fournisseur le rejoue dans sa CI. Si le fournisseur change une réponse utilisée, son build échoue avant la mise en production, sans environnement partagé.", """// côté consommateur (Incidents) : ce que j'attends de Mobilisation
@Pact(consumer = "incidents", provider = "mobilisation")
RequestResponsePact equipeDisponible(PactDslWithProvider b) {
  return b.given("une équipe disponible en zone N1")
    .uponReceiving("demande d'équipes disponibles").path("/v1/equipes").query("zone=N1&disponible=true").method("GET")
    .willRespondWith().status(200).body(newJsonArrayMinLike(1, e -> e.stringType("id", "eq-7").stringType("nom", "Alpha")).build())
    .toPact();
}
# côté fournisseur (Mobilisation) : vérification des contrats publiés, puis autorisation de déployer
pact-broker can-i-deploy --pacticipant mobilisation --version "$CI_COMMIT_SHA" --to-environment production"""),
  ("Des environnements éphémères", "Plutôt qu'un environnement d'intégration partagé que tout le monde casse, chaque MR peut démarrer le service et ses dépendances dans un espace de noms temporaire, détruit après les tests.", None)],
 [("L'environnement d'intégration commun est cassé deux jours sur trois et bloque toutes les équipes. Que proposes-tu ?", "Déplacer la confiance vers des tests qui ne dépendent pas de lui : tests de composant avec Testcontainers, contrats Pact vérifiés en CI et can-i-deploy avant chaque déploiement ; garder quelques parcours de bout en bout en supervision synthétique."),
  ("Question d'entretien : que teste un contrat que ne teste pas un test unitaire ?", "L'accord entre deux services qui évoluent séparément : la forme des requêtes et des réponses réellement utilisées par le consommateur. Un test unitaire de chaque côté peut passer alors que les deux ne se comprennent plus.")],
 ("Contrats entre Incidents et Mobilisation", ["Tests de composant d'Incidents avec PostgreSQL et Kafka en Testcontainers, Mobilisation simulé par WireMock.", "Contrat Pact HTTP côté Incidents, vérification côté Mobilisation, broker Pact en Compose ; contrat de message pour IncidentEscaladé.", "can-i-deploy dans les deux pipelines ; casser volontairement le champ nom côté Mobilisation."],
  "Attendu : le renommage du champ nom fait échouer la vérification du fournisseur et can-i-deploy bloque le déploiement ; aucun test ne dépend d'un environnement partagé ; la suite complète tourne en moins de cinq minutes.")),

ch("Déployer et exploiter : autonomie, compatibilité, plateforme", 's',
 ["Un service est autonome s'il se déploie seul, à tout moment : cela exige la compatibilité avec la version précédente de ses API et de ses événements.", "Kubernetes fournit sondes, budgets d'interruption et mise à l'échelle ; la livraison progressive (canary) limite l'impact d'une mauvaise version.", "Une plateforme interne offre un chemin tout tracé : modèle de service, pipeline, observabilité et sécurité par défaut."],
 ["Garantir la compatibilité N-1 des API et des événements", "Déployer un service avec sondes, budget d'interruption et canary", "Construire un modèle de service réutilisable par toutes les équipes"],
 [("La compatibilité N-1", "Pendant un déploiement, l'ancienne et la nouvelle version coexistent, côté fournisseur comme côté consommateur. On ajoute avant de retirer (expand/contract), pour les colonnes, les champs d'API et les événements, et on ne retire qu'une fois tous les consommateurs migrés.", """Renommer le champ « gravite » en « severite » sans rien casser
v1 : publie gravite
v2 : publie gravite ET severite                       (expand)
     consommateurs migrés un par un vers severite     (contrats Pact le vérifient)
v3 : ne publie plus que severite                      (contract), quand plus aucun contrat n'utilise gravite"""),
  ("Un déploiement sûr", MVN, """apiVersion: apps/v1
kind: Deployment
metadata: { name: incidents, namespace: crise }
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: incidents
          image: registry.local/crisis/incidents@sha256:9c4d…         # par digest
          resources: { requests: { cpu: 250m, memory: 512Mi }, limits: { memory: 512Mi } }
          readinessProbe: { httpGet: { path: /actuator/health/readiness, port: 8080 } }
          livenessProbe:  { httpGet: { path: /actuator/health/liveness,  port: 8080 } }
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: incidents }
spec: { minAvailable: 2, selector: { matchLabels: { app: incidents } } }"""),
  ("Canary et plateforme", "Argo Rollouts envoie d'abord 10 % du trafic à la nouvelle version, compare taux d'erreur et latence à la version stable, puis élargit ou revient en arrière seul. La plateforme fournit le modèle : dépôt, pipeline, tableau de bord, alertes et politiques de sécurité déjà branchés.", """strategy:
  canary:
    steps: [ { setWeight: 10 }, { pause: { duration: 5m } }, { analysis: { templates: [ { templateName: taux-erreur } ] } }, { setWeight: 50 }, { pause: { duration: 10m } } ]
# modèle de service (Backstage ou cookiecutter) : Spring Boot, Dockerfile durci, pipeline, OpenTelemetry, SLO, NetworkPolicy""")],
 [("Six services doivent être déployés ensemble « sinon ça casse ». Que faut-il changer ?", "Rendre chaque changement compatible avec la version précédente (expand/contract sur API, événements et schémas), vérifier la compatibilité par contrats, et supprimer les dépendances de version croisées : un service doit pouvoir partir seul, à tout moment."),
  ("Question d'entretien : pourquoi un PodDisruptionBudget ?", "Pour qu'une opération volontaire (drainage d'un nœud, mise à jour du cluster) ne supprime pas trop de Pods à la fois : avec minAvailable à 2 sur 3, Kubernetes attend qu'un Pod soit prêt ailleurs avant d'en retirer un autre.")],
 ("Déploiement autonome et progressif", ["Déployer Incidents et Mobilisation dans kind avec sondes, ressources, PDB et HPA.", "Renommer un champ d'événement en expand/contract, sans déploiement synchronisé, vérifié par les contrats.", "Canary Argo Rollouts avec analyse Prometheus ; publier une version qui renvoie 5 % d'erreurs."],
  "Attendu : chaque service se déploie seul pendant qu'un test de charge tourne, sans erreur ; le renommage se fait en trois versions sans casser aucun consommateur ; la version fautive est retirée automatiquement à 10 % du trafic.")),

ch("Migrer un monolithe, organiser les équipes, éviter les pièges", 'e',
 ["On migre par étranglement : la passerelle envoie une route après l'autre vers le nouveau service, le monolithe rétrécit, et le retour arrière reste possible à chaque étape.", "L'organisation précède l'architecture (loi de Conway) : des équipes alignées sur les flux métier, une équipe plateforme, des équipes d'appui.", "Les pièges connus : monolithe distribué, base partagée, services bavards, nano-services, absence d'observabilité, migration en big bang."],
 ["Planifier l'extraction d'un service d'un monolithe, données comprises", "Aligner équipes et services (Team Topologies)", "Reconnaître les anti-patterns et répondre aux questions d'entretien"],
 [("Étrangler le monolithe", "On commence par un contexte peu couplé et utile (notifications). La passerelle route une URL vers le nouveau service ; les données sont copiées par CDC, puis le nouveau service devient propriétaire et le monolithe lit par API. Chaque étape est réversible par un simple changement de route.", """Extraction de Notifications, étape par étape
1. passerelle devant le monolithe (aucun changement visible)
2. nouveau service Notifications ; CDC (Debezium) copie les tables notifications du monolithe
3. route /api/notifications → nouveau service en lecture ; écritures toujours dans le monolithe
4. écritures basculées vers le service ; le monolithe consomme ses événements (couche anticorruption)
5. tables supprimées du monolithe quand plus rien ne les lit ; retour arrière possible jusqu'à l'étape 4"""),
  ("Équipes et services", "Une équipe alignée sur un flux métier possède ses services de bout en bout (code, déploiement, astreinte) ; l'équipe plateforme lui fournit les outils en libre-service ; une équipe d'appui l'aide à monter en compétence. Un service sans équipe propriétaire est déjà un problème.", T([
    ("Monolithe distribué", "services déployés ensemble", "compatibilité N-1, contrats"),
    ("Base partagée", "tables lues par plusieurs services", "une base par service, API ou événements"),
    ("Services bavards", "dix appels pour une page", "composition, vue de lecture, frontières revues"),
    ("Nano-services", "un service par fonction", "regrouper par bounded context"),
    ("Aveugle", "pas de traces ni de SLO", "OpenTelemetry avant le deuxième service"),
    ("Big bang", "tout réécrire d'un coup", "étranglement, route par route")], ("Piège", "Symptôme", "Remède"))),
  ("Trente questions d'entretien", "", """1 Microservice ? Déployable seul, ses données, une capacité métier. 2 Quand ne pas en faire ? Petite équipe, domaine instable, pas d'automatisation. 3 Monolithe modulaire ? Un déploiement, modules aux frontières contrôlées. 4 Bounded context ? Frontière de cohérence d'un modèle et de son vocabulaire. 5 Agrégat ? Unité de cohérence, modifiée en une transaction, publie des événements. 6 Loi de Conway ? L'architecture reflète l'organisation. 7 Synchrone ou asynchrone ? Synchrone pour une réponse immédiate, asynchrone pour découpler. 8 Idempotence ? Rejouer sans effet de bord ; clé d'idempotence. 9 Versionner une API ? Ajouts compatibles, suppression = nouvelle version, dépréciation. 10 REST ou gRPC ? Public et navigateur : REST ; interne à fort trafic : gRPC. 11 Ordre dans Kafka ? Par partition ; clé = identifiant métier. 12 Exactly-once ? Au moins une fois + consommateur idempotent. 13 Schéma d'événement ? Registre, compatibilité BACKWARD. 14 Base par service ? Autonomie ; partage par API ou événements. 15 Saga ? Étapes locales + compensations. 16 Orchestration ou chorégraphie ? Au-delà de trois étapes, orchestration. 17 Outbox ? Événement dans la même transaction, relais CDC. 18 CQRS ? Modèle de lecture séparé, cohérent à terme. 19 Event sourcing ? État recalculé depuis les événements ; audit. 20 Budget de latence ? Délai de l'appelé < délai de l'appelant. 21 Tempête de tentatives ? Tentatives multipliées ; recul, aléa, disjoncteur. 22 Disjoncteur ? Cesser d'appeler un service en échec. 23 Cloison ? Limiter les ressources par dépendance. 24 Passerelle ? Routage, jeton, débit ; pas de métier. 25 BFF ? Une API par client. 26 Sécurité interne ? Audience, échange de jeton, mTLS, NetworkPolicy. 27 Trace distribuée ? traceparent en HTTP et en-têtes Kafka. 28 Tests de contrat ? Le consommateur décrit, le fournisseur vérifie, can-i-deploy. 29 Déploiement autonome ? Compatibilité N-1, expand/contract. 30 Migrer un monolithe ? Étranglement, CDC, route par route.""")],
 [("La direction veut « passer en microservices » en réécrivant l'application en un an. Que réponds-tu ?", "Qu'une réécriture complète livre tard et court après un métier qui bouge ; je propose l'étranglement : une passerelle, un premier contexte peu couplé extrait en trois mois avec des mesures (fréquence de livraison, incidents), puis décision de continuer ou non sur ces chiffres."),
  ("Question d'entretien : comment sais-tu que ton découpage est mauvais ?", "Quand une fonctionnalité oblige à modifier et déployer plusieurs services ensemble, quand les services s'appellent en boucle, ou quand deux équipes se disputent un même service : les frontières ne suivent pas le métier ou l'organisation.")],
 ("Extraire Notifications du monolithe", ["Passerelle devant le monolithe CrisisShield ; nouveau service Notifications ; CDC Debezium des tables concernées.", "Bascule en cinq étapes, avec retour arrière testé à chaque étape.", "Bilan chiffré (fréquence de livraison, temps de déploiement, incidents) et ADR de décision pour la suite."],
  "Attendu : chaque étape se fait sans interruption de service et se défait par un changement de route ; les tables sont supprimées du monolithe seulement quand plus aucune requête ne les lit ; le bilan montre des livraisons de Notifications indépendantes du reste.")),
]

d = sys.argv[1]
page('cours-08-microservices.html', 'Microservices — de zéro à expert', "Treize chapitres pour concevoir, construire et exploiter des microservices sans tomber dans le monolithe distribué : quand en faire, découper avec le DDD, communication synchrone et asynchrone (REST, gRPC, Kafka), données distribuées (base par service, saga, outbox), CQRS, résilience, passerelle et BFF, sécurité entre services, observabilité distribuée, tests de contrat, déploiement autonome, migration d'un monolithe et organisation des équipes. Fil conducteur : CrisisShield en Spring Boot, tout en Docker ; chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 45 h de travail · prérequis : Java et Spring Boot, Docker ; utile avant les niveaux 5 à 8 du parcours DevOps.", MS, [('cours-05-kotlin.html', 'Kotlin'), ('devops-05-kubernetes.html', 'DevOps niveau 5'), ('devops-07-securite-devsecops.html', 'DevOps niveau 7')])
