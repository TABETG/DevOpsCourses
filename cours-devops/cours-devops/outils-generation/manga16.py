"""Planches manga du cours Kotlin (7 chapitres). Usage : python3 manga16.py <page>"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from manga_gabarit import strip3, apply
F = lambda *a: strip3(*a)
N = dict(rack=False, nuit=False)
STRIPS = [
 ("c1", F("mgk1", "des !! partout", "Kotlin 1",
   dict(term=["val zone = req.zone!!", "val id = user!!.id!!", "// le compilateur se tait"], bulle=["Ça compile,", "c'est le", "principal."]),
   dict(term=["NullPointerException", "  at IncidentService.kt:42", "en production, un dimanche"], sfx="NPE"),
   "traiter l'absence", ["?: valeur par défaut", "?.let { … }", "requireNotNull(x) { \"message\" }", "!! seulement dans les tests"],
   "!! transforme chaque null en exception : on traite l'absence avec ?:, ?.let ou requireNotNull avec un message, et !! reste dans les tests.")),
 ("c2", F("mgk2", "la data class entité", "Kotlin 2",
   dict(term=["@Entity data class", "  Incident(val id: Long?,", "  var titre: String, …)"], bulle=["equals et copy", "gratuits !"]),
   dict(term=["set.add(i); i.titre = \"x\"", "set.contains(i) → false", "et le lazy chargé partout"], **N, who='mika', expr='angry', pose='hips', sfx="false"),
   "entité = class", ["class avec plugin kotlin-jpa", "equals/hashCode sur l'id stable", "data class pour les DTO", "value class pour les identifiants"],
   "Une data class compare tous ses champs : comme entité, elle se perd dans les Set et déclenche le chargement paresseux ; l'entité est une class, les DTO sont des data classes.")),
 ("c3", F("mgk3", "un million de listes intermédiaires", "Kotlin 3",
   dict(term=["lignes.map { parse(it) }", "  .filter { it.valide }", "  .map { it.zone }.first()"], bulle=["Lisible et", "fonctionnel."]),
   dict(term=["fichier de 1 M de lignes", "3 listes de 1 M en mémoire", "OutOfMemoryError"], sfx="OOM"),
   "paresseux quand c'est gros", ["lignes.asSequence()", "une seule passe", "s'arrête au premier trouvé", "List pour les petites tailles"],
   "Chaque map ou filter sur une liste en crée une nouvelle : sur de gros volumes, asSequence traite élément par élément et s'arrête dès que possible.")),
 ("c4", F("mgk4", "GlobalScope, lancé et oublié", "Kotlin 4",
   dict(term=["GlobalScope.launch {", "  notifier(incident)", "}"], bulle=["Ça part en", "arrière-plan."]),
   dict(term=["requête annulée : la tâche", "  continue ; exceptions perdues", "  3 000 coroutines orphelines"], sfx="3 000"),
   "concurrence structurée", ["un scope lié au cycle de vie", "coroutineScope { async … }", "SupervisorJob si isolé", "l'annulation se propage"],
   "Une coroutine lancée dans GlobalScope n'a pas de parent : elle survit à la requête et perd ses erreurs ; chaque coroutine vit dans un scope qui l'annule avec lui.")),
 ("c5", F("mgk5", "@Transactional sans effet", "Kotlin 5",
   dict(term=["@Service class IncidentService", "  @Transactional", "  fun cloturer(id: Long)"], bulle=["Comme en", "Java."]),
   dict(term=["classe finale : pas de proxy", "rollback absent après erreur", "données à moitié écrites"], **N, who='kai', expr='shock', sfx="final"),
   "ouvrir pour Spring", ["plugin kotlin(\"plugin.spring\")", "plugin kotlin(\"plugin.jpa\")", "test d'intégration du rollback"],
   "Les classes Kotlin sont finales : sans le plugin kotlin-spring, Spring ne peut pas créer ses proxys et les annotations transactionnelles n'ont aucun effet.")),
 ("c6", F("mgk6", "le null venu de Java", "Kotlin 6",
   dict(term=["val nom: String =", "  javaClient.getNom()", "// type plateforme String!"], bulle=["Kotlin garantit", "le non-null."]),
   dict(term=["getNom() renvoie null", "NullPointerException", "  à la frontière Java"], sfx="NPE"),
   "annoter la frontière", ["@Nullable / @NotNull côté Java", "-Xjsr305=strict", "traiter String! comme String?", "adapter dans une seule couche"],
   "Les valeurs venant de Java ont un type plateforme que Kotlin ne vérifie pas : on annote le Java, on active jsr305 strict, et on traite ces valeurs comme nullables.")),
 ("c7", F("mgk7", "le convertisseur automatique", "Kotlin 7",
   dict(term=["IntelliJ : Convert Java", "  to Kotlin (tout le projet)", "  1 200 fichiers"], bulle=["Un clic et", "on est en", "Kotlin."]),
   dict(term=["4 800 !! générés", "build 2× plus lent (kapt)", "Lombok et Jackson en conflit"], **N, who='mika', expr='shock', sfx="4 800"),
   "migrer fichier par fichier", ["nouveaux fichiers en Kotlin", "convertir les plus modifiés", "nettoyer !!, data, when", "KSP au lieu de kapt"],
   "Une conversion automatique globale produit du Kotlin qui pense en Java : on migre progressivement les fichiers les plus modifiés, on nettoie à la main, et on remplace kapt par KSP.")),
]
if __name__ == '__main__': apply(sys.argv[1], STRIPS)
