"""Planches manga du niveau 6 (chapitres 32 à 36). Usage : python3 manga8.py <page niveau 6>"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from manga_gabarit import strip3, apply

STRIPS = [
 ("c32", strip3("mg32", "le mot de passe dans les logs", "Chapitre 32",
   dict(term=['log.info("login {} {}",', '  user, password);', '# pour déboguer, vite fait'], bulle=["Je l'enlèverai", "après la", "mise en prod."]),
   dict(term=["Loki, 30 jours de rétention :", "login alice S3cret!", "lisible par 40 personnes"], rack=False, nuit=False, who='mika', expr='angry', pose='hips', sfx="fuite"),
   "des logs sûrs et utiles", ["JSON structuré, traceId", "jamais de secret ni de PII", "masquage dans le collecteur", "rétention et accès limités"],
   "Un log est une donnée comme une autre, copiée et conservée : jamais de secret ni de donnée personnelle, un format structuré avec l'identifiant de trace, et un masquage dans le collecteur.")),
 ("c33", strip3("mg33", "un label par utilisateur", "Chapitre 33",
   dict(term=["http_requests_total{", '  user_id="…",', '  path="/incidents/4821"}'], bulle=["Comme ça, on", "voit tout, pour", "chaque client."]),
   dict(term=["séries actives : 12 millions", "prometheus : OOMKilled", "tableaux de bord vides"], sfx="OOM"),
   "des labels bornés", ["route, méthode, statut : oui", "user_id, URL brute : non", "le détail → traces, exemplars", "alerte sur la cardinalité"],
   "Chaque combinaison de labels crée une série : un identifiant d'utilisateur ou une URL brute en label fait exploser Prometheus ; le détail par requête appartient aux traces.")),
 ("c34", strip3("mg34", "la trace coupée en deux", "Chapitre 34",
   dict(term=["api → kafka → worker", "# producteur instrumenté", "# consommateur : rien"], bulle=["La trace ira", "jusqu'au bout,", "non ?"]),
   dict(term=["Tempo : trace a1b2… 3 spans", "worker : trace 9f8e… orpheline", "où est passé l'incident 4821 ?"], rack=False, nuit=False, who='kai', expr='shock', sfx="?"),
   "propager le contexte", ["traceparent W3C dans les en-têtes", "Kafka : en-têtes du message", "instrumenter le consommateur", "une trace de bout en bout"],
   "Une trace ne traverse une file que si le contexte voyage avec le message : l'en-tête traceparent part dans les en-têtes Kafka et le consommateur le reprend.")),
 ("c35", strip3("mg35", "réveillé pour un CPU à 80 %", "Chapitre 35",
   dict(term=["alert: CPUHigh", "  expr: cpu > 80 %", "  for: 1m   # 25 alertes par nuit"], who='mika', bulle=["Ça sonne encore,", "je mets en", "silencieux."]),
   dict(term=["03 h 12 : paiement en erreur 30 %", "aucune alerte : pas de règle", "client : « depuis 2 h »"], who='mika', sfx="silence"),
   "alerter sur le symptôme", ["SLO : 99,9 % de succès", "burn rate rapide et lent", "chaque alerte a un runbook", "le reste : ticket, pas page"],
   "Une alerte doit signifier qu'un utilisateur souffre et qu'il faut agir : on alerte sur la consommation du budget d'erreur, chaque page a un runbook, et le bruit part en ticket.")),
 ("c36", strip3("mg36", "c'est la faute à Sam", "Chapitre 36",
   dict(term=["post-mortem incident 17", "cause : Sam a lancé", "  le mauvais script"], who='mika', bulle=["Au moins on", "sait qui a", "fait l'erreur."]),
   dict(term=["incident 18 : trois semaines", "  après, même panne", "personne n'a rien dit"], rack=True, who='kai', expr='shock', sfx="silence"),
   "sans blâme, sur le système", ["qu'est-ce qui a laissé passer ?", "garde-fou manquant, pas faute", "actions datées et suivies", "le post-mortem est publié"],
   "Désigner un coupable garantit qu'on ne saura plus rien la prochaine fois : le post-mortem cherche le garde-fou manquant, produit des actions datées, et il est lu par tous.")),
]

if __name__ == '__main__': apply(sys.argv[1], STRIPS)
