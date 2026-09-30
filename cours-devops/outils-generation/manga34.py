"""Planches manga de la page Mission (41 chapitres) : reprend manga33 et ajoute les 10 chapitres d'entretien.
Usage : python3 manga34.py <page>"""
import sys, pathlib, runpy
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from manga_gabarit import strip3, apply
F = lambda *a: strip3(*a)
N = dict(rack=False, nuit=False)
m33 = runpy.run_path(str(pathlib.Path(__file__).with_name('manga33.py')), run_name='lib')
BASE = [svg for cid, svg in m33['STRIPS']][:31]           # les 31 premiers chapitres restent identiques
ENT = [
 F("mge1", "le pitch improvisé", "Entretien 1",
   dict(term=["« présentez-vous »", "  … cinq minutes de CV", "  dans l'ordre chronologique"], bulle=["Alors, en", "2010…"]),
   dict(term=["le jury décroche", "  rien sur le poste", "  aucune réussite chiffrée"], **N, who='mika', expr='shock', sfx="zzz"),
   "deux minutes, cinq points", ["qui je suis", "le socle technique", "une réussite chiffrée", "pourquoi ce poste"],
   "Une présentation qui déroule le CV perd l'auditoire : cinq points en deux minutes, reliés au poste."),
 F("mge2", "la réponse de manuel", "Entretien 2",
   dict(term=["« pool épuisé ? »", "  « il faut augmenter", "  max-pool-size »"], bulle=["C'est la", "solution."]),
   dict(term=["« et si la cause est", "  une connexion non rendue ? »", "  … silence"], **N, who='kai', expr='shock', sfx="?"),
   "diagnostiquer avant d'agir", ["statistiques du pool", "vidages des fils", "sessions Oracle", "cause puis correctif"],
   "Augmenter un réglage sans diagnostic masque la cause : on montre sa démarche de preuve avant la solution."),
 F("mge3", "le forçage assumé", "Entretien 3",
   dict(term=["« un job bloque la suite ? »", "  « je le force en OK »"], bulle=["C'est plus", "rapide."]),
   dict(term=["le recruteur note :", "  « risque de données fausses", "  en aval »"], sfx="OK ?"),
   "analyser, corriger, relancer", ["qualifier l'erreur", "relance sans risque", "forçage exceptionnel et tracé", "communication"],
   "Répondre « je force » inquiète un recruteur : on explique l'analyse, la relance sûre, et le forçage comme exception tracée."),
 F("mge4", "« je ne suis pas DBA »", "Entretien 4",
   dict(term=["« une requête est lente ? »", "  « je transmets au DBA »"], bulle=["Ce n'est pas", "mon rôle."]),
   dict(term=["« et en attendant,", "  que regardez-vous ? »", "  … pas de réponse"], **N, who='mika', expr='shock', sfx="…"),
   "diagnostiquer, puis collaborer", ["sql_id et plan réel", "statistiques et index", "correctif applicatif", "DBA pour le reste"],
   "Un Tech Lead ne se défausse pas : il diagnostique ce qui relève de l'application et travaille avec les DBA pour le reste."),
 F("mge5", "tout réécrire", "Entretien 5",
   dict(term=["« et Struts 1 ? »", "  « on réécrit tout", "  en Spring Boot »"], bulle=["Six mois,", "pas plus."]),
   dict(term=["le jury pense :", "  « risque maximal", "  sur une appli critique »"], **N, who='kai', expr='shock', sfx="risque"),
   "sécuriser, puis migrer par étapes", ["filtres et WAF d'abord", "tests de caractérisation", "écran par écran", "POC et chiffrage"],
   "Proposer une réécriture complète d'une application critique inquiète : on sécurise, puis on migre par étapes mesurées."),
 F("mge6", "« TLS suffit »", "Entretien 6",
   dict(term=["« sécuriser un service SOAP ? »", "  « on met du HTTPS »"], bulle=["C'est", "chiffré."]),
   dict(term=["« et la signature", "  des messages relayés ? »", "  … hésitation"], sfx="?"),
   "transport et message", ["TLS pour le transport", "WS-Security pour le message", "XSD et analyseur durci", "contrat versionné"],
   "TLS protège une connexion, pas un message relayé ou à signer : on distingue sécurité du transport et du message."),
 F("mge7", "la barrière négociable", "Entretien 7",
   dict(term=["« barrière rouge et urgence ? »", "  « on livre, on verra »"], bulle=["Le métier", "attend."]),
   dict(term=["le recruteur note :", "  « ne tiendra pas", "  la qualité du CDS »"], **N, who='mika', expr='angry', pose='hips', sfx="rouge"),
   "une règle, des dérogations tracées", ["dérogation écrite et datée", "risque métier justifié", "corrections exigées", "suivi dans Jira"],
   "Céder sur la barrière qualité en entretien fait douter de ta tenue face au CDS : règle ferme, dérogations rares et tracées."),
 F("mge8", "l'inventaire absent", "Entretien 8",
   dict(term=["« faille critique vendredi soir ? »", "  « je cherche où", "  la bibliothèque est utilisée »"], bulle=["Ça prendra", "la nuit."]),
   dict(term=["« vous n'avez pas", "  d'inventaire des dépendances ? »", "  … gêne"], sfx="SBOM ?"),
   "savoir en minutes", ["inventaire des dépendances", "exposition connue", "mesure immédiate", "correctif testé puis tracé"],
   "Sans inventaire, une faille critique se traite à l'aveugle : on sait en minutes si l'on est concerné, puis on protège, corrige et trace."),
 F("mge9", "le devis signé", "Entretien 9",
   dict(term=["« analyser un devis ? »", "  « je fais confiance", "  au CDS »"], bulle=["Ils sont", "experts."]),
   dict(term=["le jury pense :", "  « il validera tout »", "  (tests et doc hors devis)"], **N, who='kai', expr='shock', sfx="hors devis"),
   "lire comme un contrat", ["périmètre, hypothèses", "chiffrage comparé", "oublis : tests, doc, sécurité", "remarques écrites"],
   "Faire confiance sans vérifier n'est pas du pilotage : on montre comment on lit un devis et ce qu'on y cherche."),
 F("mge10", "l'erreur qu'on n'a jamais faite", "Entretien 10",
   dict(term=["« racontez une erreur »", "  « je n'en fais pas", "  vraiment »"], bulle=["Je suis", "rigoureux."]),
   dict(term=["le jury note :", "  « manque de recul", "  et de sincérité »"], **N, who='mika', expr='shock', sfx="…"),
   "une vraie erreur, une vraie leçon", ["ce qui s'est passé", "la correction", "le coût", "le garde-fou mis en place"],
   "Prétendre ne jamais se tromper inquiète : une erreur assumée et le garde-fou qu'elle a produit montrent la maturité."),
]
STRIPS = [(f"c{i}", svg) for i, svg in enumerate(BASE + ENT, 1)]
if __name__ == '__main__': apply(sys.argv[1], STRIPS)
