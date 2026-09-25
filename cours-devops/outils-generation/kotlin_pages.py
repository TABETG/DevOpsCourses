"""Cours Kotlin (backend, Spring Boot, Ktor, coroutines). Usage : python3 kotlin_pages.py <dossier>"""
import sys, runpy, pathlib
g = runpy.run_path(pathlib.Path(__file__).with_name('front_gen.py'), run_name='front'); ch, page = g['ch'], g['page']
GR = "Tout en conteneur : <code>alias gradle='docker run --rm -v \"$PWD:/app\" -w /app -v gradle-cache:/root/.gradle gradle:8.10-jdk21 gradle'</code> ; l'application tourne dans <code>eclipse-temurin:21-jre</code> par Compose."

KT = [
ch("Démarrer : syntaxe, types, null safety", 'j',
 ["Kotlin compile vers la JVM (et JS, natif) ; il est concis, typé statiquement avec inférence, et surtout sûr vis-à-vis de null : le type dit si la valeur peut être absente.", "<code>val</code> (immuable) par défaut, <code>var</code> quand nécessaire ; fonctions de premier ordre, expressions (<code>if</code>, <code>when</code> renvoient une valeur), templates de chaînes.", "Le projet se crée avec Gradle en Kotlin DSL, tout en conteneur ; le code Java existant s'appelle directement."],
 ["Écrire du Kotlin idiomatique : val, when, expressions, templates", "Utiliser la null safety (?, ?., ?:, !!, let) sans abus", "Créer et exécuter un projet Gradle Kotlin en Docker"],
 [("Bases", "", """fun main() {
    val nom = "CrisisShield"                 // inféré String, immuable
    var compteur = 0; compteur += 1           // mutable seulement si nécessaire
    val priorite = when (compteur) { 0 -> "aucune"; in 1..3 -> "basse"; else -> "haute" }   // when = expression
    println("$nom : $compteur incident(s), priorité ${priorite.uppercase()}")
    fun carre(x: Int): Int = x * x            // fonction expression ; fonctions locales autorisées
    val ids = listOf(3, 1, 2).sorted().map { it * 2 }.filter { it > 2 }   // collections immuables par défaut
    val (a, b) = 1 to 2                        // déstructuration, Pair
    val entier: Int = "42".toIntOrNull() ?: 0  // conversion sûre + Elvis
}"""),
  ("Null safety", "", """var titre: String = "Fuite"          // ne peut pas être null : titre = null ne compile pas
var zone: String? = null               // nullable explicite
val longueur = zone?.length            // Int? : null si zone est null (appel sûr)
val z = zone ?: "inconnue"            // Elvis : valeur par défaut
zone?.let { println("zone $it") }     // exécute seulement si non null
val force = zone!!.length              // lève NullPointerException si null : à bannir hors tests
fun affiche(z: String?) { if (z != null) println(z.length) }   // smart cast : dans le if, z est String
// interop Java : les types venant de Java sont « platform types » (String!) : annoter le Java (@Nullable/@NotNull) ou traiter comme nullable
// lateinit var service: IncidentService   → pour l'injection ; lève UninitializedPropertyAccessException si lu avant"""),
  ("Projet Gradle en conteneur", GR, """// build.gradle.kts
plugins { kotlin("jvm") version "2.0.21"; application }
repositories { mavenCentral() }
dependencies { testImplementation(kotlin("test")) }
kotlin { jvmToolchain(21) }
application { mainClass.set("fr.crisis.MainKt") }
# gradle init --type kotlin-application --dsl kotlin ; gradle build ; gradle run ; gradle test""")],
 [("Pourquoi <code>val</code> par défaut ?", "L'immuabilité rend le code plus sûr (pas de réaffectation surprise), plus lisible et compatible avec la concurrence ; on passe en <code>var</code> seulement quand une réaffectation est nécessaire, et le relecteur le voit."),
  ("Question d'entretien : que fait <code>!!</code> et quand est-ce acceptable ?", "Il affirme que la valeur n'est pas null et lève NPE sinon : acceptable dans un test ou quand une invariante garantit la non-nullité et qu'un échec doit être bruyant ; ailleurs, <code>?:</code>, <code>?.let</code>, <code>requireNotNull</code> avec message.")],
 ("Premier module Kotlin", ["Projet Gradle Kotlin DSL en conteneur ; modèle <code>Incident</code> avec priorité en <code>enum class</code>, fonctions pures de tri et de filtre.", "Parseur de lignes CSV tolérant (nullables, <code>toIntOrNull</code>, <code>runCatching</code>) avec tests <code>kotlin.test</code>.", "Comparer avec l'équivalent Java (lignes, classes, null checks)."],
  "Attendu : le parseur ne lève jamais d'exception sur une ligne cassée (elle est rejetée dans une liste), les tests couvrent le vide, le null et le type faux ; le fichier Kotlin fait ~40 % du Java équivalent sans perte de lisibilité.")),

ch("Classes, data classes, objets, interfaces", 'j',
 ["<code>class</code> avec constructeur primaire et propriétés déclarées inline ; <code>data class</code> génère equals/hashCode/toString/copy ; <code>sealed</code> pour les hiérarchies fermées ; <code>object</code> pour le singleton, <code>companion object</code> pour le statique.", "Les classes sont finales par défaut (<code>open</code> pour hériter) ; les interfaces peuvent avoir des implémentations par défaut ; la délégation (<code>by</code>) remplace l'héritage pour composer.", "Visibilité : <code>private</code>, <code>internal</code> (module), <code>protected</code>, <code>public</code> par défaut."],
 ["Modéliser un domaine avec data, sealed, enum et value classes", "Utiliser objets, companion, délégation et propriétés calculées", "Comprendre final par défaut et l'interop avec Spring/Hibernate"],
 [("Modèle de domaine", "", """enum class Priorite(val poids: Int) { P1(3), P2(2), P3(1) }
@JvmInline value class IncidentId(val valeur: Long)                // type fort sans allocation
data class Incident(val id: IncidentId, val titre: String, val priorite: Priorite, val zone: String? = null, val statut: Statut = Statut.Ouvert) {
    init { require(titre.length in 3..200) { "titre entre 3 et 200 caractères" } }
    val critique: Boolean get() = priorite == Priorite.P1      // propriété calculée
    fun cloturer() = copy(statut = Statut.Ferme)                 // immuable : copy
}
sealed interface Statut { data object Ouvert : Statut; data object Ferme : Statut; data class Escalade(val niveau: Int) : Statut }
fun libelle(s: Statut) = when (s) { Statut.Ouvert -> "ouvert"; Statut.Ferme -> "fermé"; is Statut.Escalade -> "escaladé ${s.niveau}" }   // exhaustif : le compilateur refuse un cas manquant
class IncidentService(private val repo: IncidentRepository) : Journalisable by ConsoleJournal() {   // délégation d'interface
    companion object { const val MAX_PAR_PAGE = 50; fun vide() = IncidentService(EnMemoire()) }
    fun ouverts() = repo.tous().filter { it.statut == Statut.Ouvert }
}
object Horloge { fun maintenant() = java.time.Instant.now() }     // singleton"""),
  ("Interop et frameworks", "Spring, Hibernate et Mockito ont besoin de classes ouvertes et de constructeurs sans argument : les plugins <code>kotlin-spring</code> (allopen sur @Component, @Transactional…) et <code>kotlin-jpa</code> (noarg sur @Entity) règlent ça à la compilation. Une data class n'est pas une bonne entité JPA (equals/hashCode sur tous les champs, copy) : entité = <code>class</code> avec <code>var</code> pour les champs modifiables, ou des DTO data class à part.", None)],
 [("Pourquoi une <code>value class</code> pour l'identifiant ?", "Elle empêche de confondre deux Long (id d'incident et id de zone) à la compilation, sans coût à l'exécution (inlinée en Long)."),
  ("Question d'entretien : data class ou class pour une entité JPA ?", "Class : l'entité a une identité et un cycle de vie, pas une égalité structurelle ; equals/hashCode générés sur tous les champs cassent les Set et le lazy loading ; on réserve data class aux DTO et aux valeurs.")],
 ("Domaine CrisisShield en Kotlin", ["Modèle complet : value classes, enum avec propriétés, sealed pour le statut, data classes pour les DTO, entité JPA en class avec kotlin-jpa.", "Tests : exhaustivité du when (ajout d'un statut → erreur de compilation), copy et immuabilité, require dans init.", "Délégation d'une interface de journalisation."],
  "Attendu : ajouter <code>Statut.Suspendu</code> fait échouer la compilation de <code>libelle</code> (preuve de l'exhaustivité) ; l'entité JPA compile avec le plugin noarg sans constructeur explicite ; aucun <code>!!</code> dans le module.")),

ch("Fonctions, lambdas, collections, extensions", 'c',
 ["Fonctions d'ordre supérieur, lambdas avec <code>it</code>, références (<code>::f</code>), paramètres nommés et par défaut, <code>inline</code> et <code>reified</code>.", "Collections : lecture seule contre mutable, séquences paresseuses pour les gros flux, opérations (map, filter, groupBy, associateBy, fold, zip, windowed, chunked).", "Extensions : ajouter des fonctions à des types existants ; fonctions de portée (<code>let</code>, <code>run</code>, <code>apply</code>, <code>also</code>, <code>with</code>) ; DSL par lambdas avec récepteur."],
 ["Écrire et utiliser des fonctions d'ordre supérieur et inline", "Manipuler les collections et séquences efficacement", "Créer des extensions et un mini DSL"],
 [("Fonctions et collections", "", """fun <T> List<T>.deuxieme(): T? = getOrNull(1)                        // extension générique
fun Incident.estUrgent() = priorite == Priorite.P1 && statut == Statut.Ouvert
inline fun <reified T> List<Any>.deType(): List<T> = filterIsInstance<T>()   // reified : le type survit à l'exécution
val parZone: Map<String, List<Incident>> = incidents.groupBy { it.zone ?: "sans zone" }
val index: Map<IncidentId, Incident> = incidents.associateBy { it.id }
val total = incidents.sumOf { it.priorite.poids }; val top = incidents.sortedByDescending { it.priorite.poids }.take(5)
val gros = (1..1_000_000).asSequence().map { it * 2 }.filter { it % 3 == 0 }.first()   // paresseux : une seule passe, s'arrête au premier
fun notifier(incident: Incident, canal: String = "slack", urgent: Boolean = incident.estUrgent()) { … }
notifier(i, urgent = true)                                              // paramètre nommé
val ouverts = incidents.filter(Incident::estUrgent)                       // référence de fonction
// portée : val i = Incident(...).apply { println(titre) }  (this, renvoie l'objet) ; i.also { log(it) } (it, renvoie l'objet) ; i.let { it.titre } (renvoie le résultat) ; with(i) { titre + zone } ; run { … }"""),
  ("Mini DSL", "", """class IncidentBuilder { var titre = ""; var priorite = Priorite.P2; private val contacts = mutableListOf<String>()
    fun contact(email: String) { contacts += email }
    fun build() = Incident(IncidentId(0), titre, priorite) to contacts.toList() }
fun incident(bloc: IncidentBuilder.() -> Unit) = IncidentBuilder().apply(bloc).build()   // lambda avec récepteur
val (inc, contacts) = incident { titre = "Fuite gaz"; priorite = Priorite.P1; contact("astreinte@crisis.fr") }
// même mécanisme que Gradle Kotlin DSL, Ktor routing, kotlinx.html""")],
 [("Quand une <code>Sequence</code> plutôt qu'une <code>List</code> ?", "Quand la chaîne d'opérations est longue sur beaucoup d'éléments, ou qu'on s'arrête tôt (first, take) : la séquence évite les listes intermédiaires ; sur de petites collections, la liste est plus simple et plus rapide."),
  ("Question d'entretien : apply, also, let, run — lequel choisir ?", "apply/also configurent et renvoient l'objet (this / it) ; let/run transforment et renvoient le résultat ; let sert surtout au null-check. Règle : ne pas les imbriquer.")],
 ("Bibliothèque d'extensions et DSL", ["Extensions sur Incident et sur les collections (statistiques par zone, top N), séquences pour un fichier de 1 M de lignes avec mesure mémoire.", "DSL de construction de scénario de crise (incidents, équipes, affectations) avec lambdas à récepteur et <code>@DslMarker</code>.", "Tests et benchmark list contre sequence."],
  "Attendu : le traitement du fichier de 1 M de lignes tient en 50 Mo avec séquences contre 400 Mo en listes ; le DSL refuse à la compilation un <code>contact</code> hors d'un bloc <code>incident</code> grâce à <code>@DslMarker</code>.")),

ch("Coroutines : concurrence structurée, flows, channels", 'c',
 ["Une coroutine est une fonction suspendable légère (des milliers par thread) ; <code>suspend</code> marque les fonctions qui peuvent attendre sans bloquer ; les dispatchers choisissent où (Default = CPU, IO = blocant, Main = UI).", "Concurrence structurée : toute coroutine vit dans un scope ; l'annulation se propage ; <code>coroutineScope</code>, <code>async/await</code>, <code>withTimeout</code>, <code>SupervisorJob</code> pour isoler les échecs.", "Flow : flux froid asynchrone (map, filter, buffer, collect) ; StateFlow/SharedFlow pour l'état partagé ; Channel pour les files entre coroutines."],
 ["Écrire du code asynchrone lisible avec suspend, async, scopes", "Gérer annulation, timeouts, erreurs et dispatchers correctement", "Utiliser Flow pour des flux d'événements et de données"],
 [("Concurrence structurée", "", """suspend fun chargerIncident(id: IncidentId): Incident = withContext(Dispatchers.IO) { repo.find(id) }   // appel bloquant isolé sur IO
suspend fun tableauDeBord(zone: String): TableauDeBord = coroutineScope {
    val incidents = async { api.incidents(zone) }          // parallèle
    val equipes = async { api.equipes(zone) }
    val meteo = async { withTimeoutOrNull(800) { meteoApi.get(zone) } }   // optionnel : null si trop lent
    TableauDeBord(incidents.await(), equipes.await(), meteo.await())     // si l'un échoue, les autres sont annulés (structurée)
}
val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default + CoroutineName("notifications"))   // un enfant qui échoue n'annule pas les frères
scope.launch { runCatching { notifier(i) }.onFailure { log.error("notification", it) } }
// annulation : coopérative : les fonctions suspend de la bibliothèque vérifient ; dans une boucle CPU : ensureActive() / yield()
// pièges : GlobalScope (pas de cycle de vie), runBlocking en production (bloque un thread), catch de CancellationException (la relancer), Dispatchers.IO pour du CPU"""),
  ("Flow", "", """fun evenements(): Flow<Evenement> = flow { while (true) { emit(source.suivant()); delay(100) } }   // froid : démarre à collect
evenements().filter { it.type == "ESCALADE" }.map { it.incidentId }.buffer(64).collect { escalader(it) }
val etat = MutableStateFlow<List<Incident>>(emptyList()); etat.update { it + nouveau }   // StateFlow : dernière valeur, pour l'état partagé
val bus = MutableSharedFlow<Evenement>(replay = 0, extraBufferCapacity = 100)             // SharedFlow : diffusion
callbackFlow { val l = Listener { trySend(it) }; source.add(l); awaitClose { source.remove(l) } }   // adapter un callback
// Channel : val file = Channel<Tache>(capacity = 100) ; producteur file.send(t) ; consommateurs for (t in file) { … } ; fermeture file.close()
// tests : runTest { advanceTimeBy(1000) } avec kotlinx-coroutines-test ; Turbine pour les flows""")],
 [("<code>async</code> dans <code>coroutineScope</code> : si le deuxième appel échoue, que devient le premier ?", "Il est annulé : l'exception d'un enfant annule le scope et tous ses enfants, puis remonte. Pour tolérer l'échec d'un enfant, <code>supervisorScope</code> ou <code>runCatching</code> dans l'enfant."),
  ("Question d'entretien : coroutines contre threads virtuels Java 21 ?", "Les threads virtuels rendent le code bloquant pas cher sans changer le code ; les coroutines apportent en plus la concurrence structurée, l'annulation, les flows et un modèle explicite. Les deux coexistent (Dispatchers.IO peut utiliser des threads virtuels).")],
 ("Agrégateur asynchrone", ["Tableau de bord qui appelle trois API en parallèle avec timeout partiel ; test avec <code>runTest</code> et horloge virtuelle.", "Flux d'événements Kafka (ou simulé) en Flow avec buffer, retry avec backoff (<code>retryWhen</code>), état en StateFlow.", "Reproduire les trois pièges (GlobalScope, runBlocking, catch de CancellationException) et les corriger."],
  "Attendu : le tableau de bord répond en 800 ms même si la météo met 5 s (null) ; le test à horloge virtuelle dure 10 ms ; la fuite de GlobalScope est mise en évidence par un test qui compte les coroutines actives.")),

ch("Spring Boot en Kotlin : API REST, JPA, sécurité, tests", 's',
 ["Spring Boot supporte Kotlin nativement : constructeurs comme injection, plugins spring/jpa, Jackson Kotlin module, coroutines dans WebFlux, DSL de configuration (beans, security, router).", "Contrôleurs concis (data classes, valeurs par défaut, null safety alignée sur la validation), services immuables, repositories avec Kotlin (nullables au lieu d'Optional).", "Tests : JUnit 5 + MockK (plutôt que Mockito), Kotest en option, Testcontainers ; <code>@SpringBootTest</code> avec constructeur injecté."],
 ["Écrire une API Spring Boot idiomatique en Kotlin", "Configurer JPA, la sécurité et Jackson correctement pour Kotlin", "Tester avec MockK et Testcontainers"],
 [("API et persistance", "", """// build.gradle.kts : plugins kotlin("jvm"), kotlin("plugin.spring"), kotlin("plugin.jpa"), id("org.springframework.boot") ; dependencies : spring-boot-starter-web, -data-jpa, -validation, -security, jackson-module-kotlin, kotlin-reflect
@Entity class IncidentEntity(@Id @GeneratedValue var id: Long? = null, var titre: String, @Enumerated(EnumType.STRING) var priorite: Priorite, var zone: String? = null, @Version var version: Int = 0)
interface IncidentRepository : JpaRepository<IncidentEntity, Long> { fun findByZone(zone: String): List<IncidentEntity>; fun findFirstByTitre(titre: String): IncidentEntity? }   // nullable au lieu d'Optional
data class CreerIncident(@field:NotBlank @field:Size(min = 3, max = 200) val titre: String, val priorite: Priorite = Priorite.P2, val zone: String? = null)
data class IncidentDto(val id: Long, val titre: String, val priorite: Priorite, val zone: String?) { companion object { fun of(e: IncidentEntity) = IncidentDto(e.id!!, e.titre, e.priorite, e.zone) } }
@Service class IncidentService(private val repo: IncidentRepository) {
    @Transactional(readOnly = true) fun liste(zone: String?) = (zone?.let(repo::findByZone) ?: repo.findAll()).map(IncidentDto::of)
    @Transactional fun creer(cmd: CreerIncident) = IncidentDto.of(repo.save(IncidentEntity(titre = cmd.titre, priorite = cmd.priorite, zone = cmd.zone)))
}
@RestController @RequestMapping("/api/incidents") class IncidentController(private val service: IncidentService) {
    @GetMapping fun liste(@RequestParam zone: String?) = service.liste(zone)
    @PostMapping @ResponseStatus(HttpStatus.CREATED) fun creer(@Valid @RequestBody cmd: CreerIncident) = service.creer(cmd)
    @ExceptionHandler(IllegalArgumentException::class) fun bad(e: IllegalArgumentException) = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, e.message ?: "requête invalide")
}
// sécurité en DSL : http { authorizeHttpRequests { authorize("/api/**", authenticated); authorize(anyRequest, denyAll) }; oauth2ResourceServer { jwt { } }; csrf { disable() } }
// Jackson : jackson-module-kotlin pour les data classes sans constructeur vide ; un champ non nullable absent du JSON → MissingKotlinParameterException → 400 (cohérent avec la null safety)"""),
  ("Tests", "", """class IncidentServiceTest {
    private val repo = mockk<IncidentRepository>(); private val service = IncidentService(repo)
    @Test fun `creer renvoie le dto`() { every { repo.save(any()) } answers { firstArg<IncidentEntity>().apply { id = 42 } }
        val dto = service.creer(CreerIncident("Fuite", Priorite.P1)); assertEquals(42, dto.id); verify(exactly = 1) { repo.save(any()) } }
}
@SpringBootTest(webEnvironment = RANDOM_PORT) @Testcontainers class IncidentApiIT(@Autowired val rest: TestRestTemplate) {   // injection par constructeur
    companion object { @Container @JvmStatic val pg = PostgreSQLContainer("postgres:16"); @DynamicPropertySource @JvmStatic fun props(r: DynamicPropertyRegistry) { r.add("spring.datasource.url", pg::getJdbcUrl); … } }
    @Test fun `POST puis GET`() { val r = rest.postForEntity("/api/incidents", CreerIncident("Fuite gaz", Priorite.P1), IncidentDto::class.java); assertEquals(HttpStatus.CREATED, r.statusCode) }
}""")],
 [("Pourquoi <code>id: Long? = null</code> dans l'entité et <code>e.id!!</code> dans le DTO ?", "L'id n'existe pas avant la persistance (nullable honnête) ; une fois sauvegardée l'entité en a un, et le <code>!!</code> documente l'invariante (ou <code>requireNotNull(e.id)</code> avec message)."),
  ("Question d'entretien : MockK ou Mockito en Kotlin ?", "MockK est conçu pour Kotlin : classes finales, fonctions suspend, objets, extensions, DSL <code>every { } returns</code> ; Mockito demande le plugin inline et reste moins naturel.")],
 ("API CrisisShield en Spring Boot Kotlin", ["Projet Gradle Kotlin avec plugins spring/jpa, API incidents complète (validation, ProblemDetail, sécurité JWT en DSL), Flyway, Docker Compose.", "Tests unitaires MockK, tests d'intégration Testcontainers avec constructeur injecté, couverture Kover.", "Comparer avec la version Java du parcours : lignes, lisibilité, gestion des nulls."],
  "Attendu : un JSON sans <code>titre</code> renvoie 400 par la null safety sans annotation supplémentaire ; les tests d'intégration tournent en conteneur en < 30 s ; Kover ≥ 80 % sur les services.")),

ch("Ktor et alternatives légères ; interop Java ; multiplateforme", 's',
 ["Ktor : serveur et client HTTP en coroutines, routing en DSL, plugins (sérialisation, auth, CORS, logging), sans réflexion ni conteneur lourd : démarrage en 100 ms, idéal pour les services légers et natifs.", "Interop Java : appeler Kotlin depuis Java (<code>@JvmStatic</code>, <code>@JvmOverloads</code>, <code>@JvmName</code>, <code>@file:JvmName</code>), appeler Java depuis Kotlin (platform types, SAM), coexistence dans le même module Gradle.", "Kotlin Multiplatform partage la logique (domaine, validation, clients) entre JVM, Android, iOS, JS, natif : utile pour un SDK ou une application mobile, pas pour un backend seul."],
 ["Écrire un service Ktor avec routing, sérialisation et authentification", "Rendre une bibliothèque Kotlin agréable à utiliser depuis Java", "Savoir situer Kotlin Multiplatform et Kotlin/Native"],
 [("Ktor", "", """fun main() = embeddedServer(Netty, port = 8080) {
    install(ContentNegotiation) { json() }                              // kotlinx.serialization : @Serializable data class
    install(CallLogging); install(StatusPages) { exception<IllegalArgumentException> { call, e -> call.respond(HttpStatusCode.BadRequest, mapOf("detail" to e.message)) } }
    install(Authentication) { jwt("keycloak") { verifier(jwkProvider, issuer); validate { JWTPrincipal(it.payload) } } }
    routing { authenticate("keycloak") { route("/api/incidents") {
        get { call.respond(service.liste(call.request.queryParameters["zone"])) }
        post { val cmd = call.receive<CreerIncident>(); call.respond(HttpStatusCode.Created, service.creer(cmd)) }
        get("{id}") { val id = call.parameters["id"]?.toLongOrNull() ?: throw IllegalArgumentException("id"); call.respond(service.get(id) ?: return@get call.respond(HttpStatusCode.NotFound)) }
    } } }
}.start(wait = true)
// client : HttpClient(CIO) { install(ContentNegotiation) { json() } }.get("https://api…/incidents") { parameter("zone", "N1") }.body<List<IncidentDto>>()
// tests : testApplication { client.get("/api/incidents").apply { assertEquals(HttpStatusCode.OK, status) } }
// Exposed (SQL DSL/DAO) ou jOOQ pour la base ; Koin pour l'injection ; GraalVM natif possible (démarrage 30 ms)"""),
  ("Interop Java", "", """// Kotlin appelable proprement depuis Java
@file:JvmName("Incidents")                                   // Java : Incidents.trier(list) au lieu de IncidentsKt
fun trier(xs: List<Incident>): List<Incident> = xs.sortedBy { it.priorite }
class Notifieur { companion object { @JvmStatic fun defaut() = Notifieur() }               // Java : Notifieur.defaut()
    @JvmOverloads fun envoyer(msg: String, canal: String = "slack", urgent: Boolean = false) {} }   // surcharges Java générées
@Throws(IOException::class) fun lire(path: String): String = File(path).readText()          // Java voit l'exception checked
// depuis Kotlin : les lambdas → interfaces SAM Java (Runnable, Comparator) ; Optional<T> → T? avec .orElse(null) ; getters/setters Java → propriétés""")],
 [("Ktor ou Spring Boot pour un nouveau service ?", "Spring Boot si l'écosystème (sécurité, data, actuator, équipe) compte ; Ktor pour un service léger, natif, à démarrage rapide, ou quand on veut tout en coroutines sans réflexion. Les deux sont productifs en Kotlin."),
  ("Question d'entretien : que devient une fonction de niveau fichier en Java ?", "Une méthode statique d'une classe <code>NomDuFichierKt</code> (ou le nom donné par <code>@file:JvmName</code>) ; les paramètres par défaut ne sont pas vus sans <code>@JvmOverloads</code>.")],
 ("Service Ktor et bibliothèque partagée", ["Service Notification en Ktor (routing, JSON, JWT Keycloak, StatusPages) avec tests <code>testApplication</code> ; image native GraalVM en conteneur, temps de démarrage mesuré.", "Bibliothèque de domaine Kotlin consommée par un module Java (annotations Jvm*), avec tests Java.", "Note d'une page : quand Kotlin Multiplatform ; prototype d'un module <code>commonMain</code> de validation compilé JVM + JS."],
  "Attendu : Ktor JVM démarre en ~150 ms, natif en ~30 ms ; le module Java compile sans <code>Kt</code> ni surcharge manquante ; la validation commune s'exécute dans un test JVM et dans un test JS.")),

ch("Qualité, performance, production et migration depuis Java", 'e',
 ["Qualité : ktlint/detekt, warnings comme erreurs, <code>explicitApi</code> pour les bibliothèques, Kover pour la couverture, Dokka pour la documentation ; conventions de nommage et de fichiers.", "Performance : inline pour les lambdas chaudes, éviter l'autoboxing (<code>IntArray</code>, primitives), séquences pour les gros flux, coroutines dimensionnées, profilage identique à Java (JFR, async-profiler) ; la JVM reste la même.", "Migration Java → Kotlin : fichier par fichier (convertisseur IntelliJ puis nettoyage), tests d'abord, interop garantie ; un mois de rodage sur un module avant de généraliser."],
 ["Mettre en place la quality gate Kotlin", "Écrire du Kotlin performant et le profiler", "Conduire une migration progressive Java → Kotlin et l'argumenter"],
 [("Quality gate et build", "", """// build.gradle.kts
plugins { kotlin("jvm") version "2.0.21"; id("org.jlleitschuh.gradle.ktlint") version "12.1.1"; id("io.gitlab.arturbosch.detekt") version "1.23.7"; id("org.jetbrains.kotlinx.kover") version "0.8.3"; id("org.jetbrains.dokka") version "1.9.20" }
kotlin { jvmToolchain(21); compilerOptions { allWarningsAsErrors.set(true); freeCompilerArgs.add("-Xjsr305=strict") } }   // strict : les annotations de nullité Java deviennent des types
kover { reports { verify { rule { minBound(80) } } } }
detekt { config.setFrom("detekt.yml"); buildUponDefaultConfig = true }
# CI : gradle ktlintCheck detekt test koverVerify build ; image : eclipse-temurin:21-jre + jar, ou native-image
# Dockerfile multi-étapes : gradle:8.10-jdk21 (build, cache /root/.gradle) → eclipse-temurin:21-jre-alpine, USER 10001, ENTRYPOINT ["java","-XX:MaxRAMPercentage=75","-jar","/app/app.jar"]"""),
  ("Performance et migration", "", """// pièges de performance : List<Int> (boxing) → IntArray ; lambdas non inline dans une boucle chaude → inline fun ; String += en boucle → buildString ; runBlocking dans un contrôleur → suspend ; Dispatchers.IO limité à 64 threads par défaut (limitedParallelism si besoin)
// mesurer : kotlinx-benchmark (JMH), JFR : java -XX:StartFlightRecording=duration=60s,filename=rec.jfr ; async-profiler en conteneur ; le bytecode Kotlin se lit avec javap ou l'outil « Show Kotlin Bytecode »
// migration : 1) activer Kotlin dans le module Java existant (plugins, jvmToolchain) 2) nouveaux fichiers en Kotlin 3) convertir les classes les plus modifiées, tests inchangés 4) nettoyer (!!, platform types, data classes, when) 5) mesurer (lignes, bugs null, temps de build) ; le build Gradle compile Kotlin puis Java ; attention au temps de compilation (kapt → KSP), aux plugins Lombok (à retirer), à Jackson (module kotlin)
// argumenter : null safety (fin des NPE en prod), concision (−30 à −40 %), coroutines, interop totale, même JVM et mêmes outils ; risques : compétence équipe, temps de build, deux langages pendant la transition""")],
 [("Le build Kotlin est deux fois plus lent que le Java : que faire ?", "Activer le daemon et le cache Gradle, la compilation incrémentale, remplacer kapt par KSP, découper en modules, vérifier la version du compilateur (K2 est bien plus rapide)."),
  ("Question d'entretien : pourquoi choisir Kotlin pour un backend en 2026 ?", "Null safety, concision, coroutines, DSL, interop Java totale, support Spring/Ktor de premier plan, même JVM et mêmes outils d'exploitation ; le coût est la montée en compétence et la vigilance sur le build. C'est un choix de productivité et de fiabilité, pas de mode.")],
 ("Projet final : CrisisShield Kotlin en production", ["Quality gate complète (ktlint, detekt, Kover 80 %, warnings en erreurs, Dokka) en GitLab CI ; image durcie ; déploiement Kubernetes avec le Deployment de référence du parcours.", "Profil JFR d'un endpoint chaud, une optimisation mesurée (boxing ou inline), benchmark avant/après.", "Migration d'un module Java du parcours vers Kotlin, tests inchangés et verts, note de retour d'expérience avec chiffres."],
  "Attendu : pipeline vert avec les cinq contrôles ; l'optimisation mesurée (par exemple IntArray : −60 % d'allocations) documentée ; le module migré a 35 % de lignes en moins, tous les tests Java existants passent, et la note liste trois pièges rencontrés (platform types, Lombok, Jackson).")),
]

d = sys.argv[1]
page('cours-05-kotlin.html', 'Kotlin — de zéro à expert', "Sept chapitres pour maîtriser Kotlin côté backend : syntaxe et null safety, classes et modèle de domaine (data, sealed, value classes), fonctions, collections et DSL, coroutines et flows, Spring Boot en Kotlin (API, JPA, sécurité, MockK, Testcontainers), Ktor et interop Java, qualité, performance et migration depuis Java. Projet fil conducteur : CrisisShield. Tout en Docker (Gradle, JDK 21), chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 35 h de travail · prérequis : Java confirmé, Docker Desktop · complète le cours Struts/Hibernate (persistance) et le niveau 2 du parcours (CI).", KT, [('cours-04-struts-hibernate-jsp.html', 'Struts, Hibernate et JSP'), ('cours-06-java-pki-signature-electronique.html', 'Java PKI')])
