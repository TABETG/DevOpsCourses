"""Planches manga du niveau 7 (chapitres 37 à 42). Usage : python3 manga9.py <page niveau 7>"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from manga_gabarit import strip3, apply

STRIPS = [
 ("c37", strip3("mg37", "400 alertes, zéro correction", "Chapitre 37",
   dict(term=["$ trivy fs . && semgrep ci", "412 vulnérabilités", "  dont 38 critiques"], bulle=["On a un scanner,", "on est en", "sécurité."]),
   dict(term=["trois mois plus tard :", "412 → 451 vulnérabilités", "0 corrigée, rapport ignoré"], rack=False, nuit=False, who='mika', expr='angry', pose='hips', sfx="451"),
   "prioriser, puis bloquer", ["atteignable ? exploitée (KEV) ?", "EPSS et exposition réelle", "bloquer le nouveau critique", "l'existant : plan daté"],
   "Un scanner qui sort 400 alertes sans tri n'en fait corriger aucune : on priorise par exploitabilité et exposition, on bloque seulement le nouveau critique, et l'existant suit un plan daté.")),
 ("c38", strip3("mg38", "le mot de passe de 2019", "Chapitre 38",
   dict(term=["DB_PASSWORD=Crisis2019!", "# le même en dev, recette, prod", "# connu de 23 personnes"], bulle=["Il marche partout,", "on ne le change", "pas."]),
   dict(term=["ancien prestataire, 2026 :", "psql -h prod-db -U app", "connexion acceptée"], sfx="accès"),
   "des secrets qui expirent", ["Vault : identifiants dynamiques", "durée de vie d'une heure", "un secret par environnement", "rotation automatique"],
   "Un mot de passe statique partagé finit toujours par sortir : Vault délivre des identifiants dynamiques, propres à chaque application et chaque environnement, qui expirent seuls.")),
 ("c39", strip3("mg39", "privileged, pour que ça marche", "Chapitre 39",
   dict(term=["securityContext:", "  privileged: true", "# sinon l'agent ne démarre pas"], bulle=["C'était bloqué,", "maintenant", "ça marche."]),
   dict(term=["pod compromis via une CVE", "nsenter -t 1 -m -u -n -i sh", "root sur le nœud, tous les Pods"], sfx="évasion"),
   "le moindre privilège, imposé", ["Pod Security : restricted", "Kyverno refuse privileged", "runAsNonRoot, drop ALL", "exception documentée et datée"],
   "Un conteneur privilégié compromis donne l'hôte et tous ses voisins : le profil restricted est imposé par le cluster, et toute exception est documentée, justifiée et datée.")),
 ("c40", strip3("mg40", "le tag v4 a changé", "Chapitre 40",
   dict(term=["- uses: tiers/changed-files@v4", "# le tag v4 : stable, non ?", "permissions: write-all"], bulle=["Un tag majeur,", "c'est sûr", "et à jour."]),
   dict(term=["le tag v4 réécrit par un attaquant", "script : printenv | base64", "secrets dans les logs publics"], sfx="volé"),
   "épingler et restreindre", ["uses: …@3f4a9c1…  (SHA du commit)", "permissions minimales", "OIDC, pas de secret long", "provenance SLSA signée"],
   "Un tag se déplace, un condensat non : on épingle les actions par leur SHA, on donne au jeton les permissions minimales, et on signe la provenance de ce qu'on construit.")),
 ("c41", strip3("mg41", "expiré dimanche à 3 h", "Chapitre 41",
   dict(term=["api.crisis.fr", "  certificat valable 1 an", "  renouvellement : manuel"], bulle=["Rappel dans", "l'agenda,", "tout va bien."]),
   dict(term=["dimanche 03 h 00 :", "x509: certificate has expired", "API, mobile, partenaires : KO"], sfx="expiré"),
   "des certificats qui se renouvellent", ["cert-manager ou ACME", "durée courte (90 jours)", "alerte à 30 jours", "inventaire de tous les certificats"],
   "Un renouvellement manuel finit par être oublié : cert-manager renouvelle seul des certificats courts, une alerte prévient trente jours avant, et un inventaire recense tout ce qui expire.")),
 ("c42", strip3("mg42", "l'audit aux captures d'écran", "Chapitre 42",
   dict(term=["audit ISO 27001 dans 3 semaines", "preuves : captures d'écran", "  de 140 contrôles"], who='mika', expr='shock', pose='head', bulle=["On va y passer", "toutes nos", "soirées."]),
   dict(term=["jour J : preuve n° 87", "  datée de l'an dernier", "écart majeur"], rack=False, nuit=False, who='kai', expr='shock', sfx="écart"),
   "la conformité comme code", ["contrôle → règle automatisée", "preuves collectées par la CI", "tableau de bord continu", "l'audit devient une lecture"],
   "Des preuves rassemblées à la main avant l'audit sont incomplètes et datées : chaque contrôle devient une règle automatisée, la CI collecte les preuves en continu, et l'audit se contente de les lire.")),
]

if __name__ == '__main__': apply(sys.argv[1], STRIPS)
