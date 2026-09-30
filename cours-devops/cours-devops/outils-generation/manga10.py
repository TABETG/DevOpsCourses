"""Planches manga du niveau 8 (chapitres 43 à 48). Usage : python3 manga10.py <page niveau 8>"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from manga_gabarit import strip3, apply
STRIPS = [
 ("c43", strip3("mg43", "le chaos sans hypothèse", "Chapitre 43",
   dict(term=["vendredi 16 h :", "kubectl delete pod -l app=db", "# « pour voir ce que ça fait »"], bulle=["Netflix le fait,", "on peut le faire."]),
   dict(term=["base primaire perdue", "bascule : 14 min", "clients : erreurs 500"], sfx="14 min"),
   "une expérience, pas un pari", ["hypothèse écrite et mesurable", "rayon d'impact limité", "critère d'arrêt, retour prêt", "game day planifié, équipe prévenue"],
   "Le chaos engineering est une expérience contrôlée : une hypothèse, un rayon d'impact réduit, un critère d'arrêt, un créneau annoncé ; sinon c'est simplement une panne provoquée.")),
 ("c44", strip3("mg44", "la sauvegarde jamais restaurée", "Chapitre 44",
   dict(term=["pg_dump chaque nuit : OK", "rétention : 30 jours", "restauration testée : jamais"], bulle=["Les sauvegardes", "sont vertes", "depuis deux ans."]),
   dict(term=["jour du sinistre :", "pg_restore : fichier tronqué", "dernière bonne : il y a 11 jours"], sfx="11 j"),
   "une sauvegarde = une restauration", ["restauration testée chaque mois", "RPO et RTO mesurés, pas promis", "copie hors du compte (immuable)", "runbook PRA rejoué en game day"],
   "Une sauvegarde qu'on n'a jamais restaurée n'est qu'un espoir : la restauration se teste chaque mois, le RPO et le RTO se mesurent, et une copie immuable vit hors du compte principal.")),
 ("c45", strip3("mg45", "testé à dix utilisateurs", "Chapitre 45",
   dict(term=["k6 run --vus 10 test.js", "  depuis le poste, en recette", "p95 : 120 ms  → validé"], bulle=["Ça tient,", "on met en prod."]),
   dict(term=["lundi 9 h : 600 utilisateurs", "pool de connexions saturé", "p99 : 14 s, erreurs 503"], sfx="503"),
   "tester comme la production", ["profil de charge réaliste", "paliers jusqu'à la rupture", "p95, p99, erreurs, saturation", "k6 dans la CI, seuils bloquants"],
   "Un test de charge à dix utilisateurs ne dit rien sur six cents : on rejoue un profil réaliste par paliers jusqu'à la rupture, et des seuils de p95 et d'erreurs bloquent le pipeline.")),
 ("c46", strip3("mg46", "vingt microservices, trois développeurs", "Chapitre 46",
   dict(term=["services : 20", "dépôts : 20, pipelines : 20", "équipe : 3 développeurs"], bulle=["Comme les grands,", "c'est moderne !"]),
   dict(term=["une fonctionnalité =", "  7 services modifiés", "  7 déploiements synchronisés"], rack=False, nuit=False, who='kai', expr='shock', sfx="×7"),
   "découper selon les équipes", ["d'abord un monolithe modulaire", "modules aux frontières nettes", "extraire quand une équipe", "  le justifie (charge, rythme)"],
   "Des microservices qui doivent être déployés ensemble forment un monolithe distribué : on commence modulaire, et on n'extrait un service que lorsqu'une équipe ou une charge le justifie.")),
 ("c47", strip3("mg47", "l'index qui bloque tout", "Chapitre 47",
   dict(term=["V12__index.sql", "CREATE INDEX idx_zone", "  ON incident(zone);  # 40 M lignes"], bulle=["Un index, ça", "ne peut que", "aider."]),
   dict(term=["verrou sur incident : 9 min", "écritures en attente : 3 000", "API : délai dépassé"], sfx="9 min"),
   "migrer sans bloquer", ["CREATE INDEX CONCURRENTLY", "lock_timeout = 2 s", "expand / contract", "tester sur une copie de prod"],
   "Sur une grosse table, un index créé normalement verrouille les écritures : CONCURRENTLY, un lock_timeout court et des migrations expand/contract testées sur une copie de production.")),
 ("c48", strip3("mg48", "le portail vide", "Chapitre 48",
   dict(term=["Backstage installé", "  modèles : 14", "  développeurs consultés : 0"], who='mika', expr='smile', bulle=["Six mois de", "travail, ils vont", "adorer."]),
   dict(term=["trois mois plus tard :", "  2 projets créés via le portail", "  38 créés à la main"], rack=False, nuit=False, who='mika', expr='shock', sfx="2 / 40"),
   "la plateforme est un produit", ["interroger les équipes d'abord", "un chemin doré, pas quatorze", "mesurer l'adoption", "facultatif, mais plus simple"],
   "Une plateforme construite sans ses utilisateurs reste vide : on part des irritants des équipes, on livre un premier chemin doré, et on mesure l'adoption comme un produit.")),
]
if __name__ == '__main__': apply(sys.argv[1], STRIPS)
