"""Planches manga de la page Mission gestionnaire d'application Perl et LaTeX (44 chapitres).
Reprend les planches des cours Perl, LaTeX et Unix, et en ajoute 20. Usage : python3 manga35.py <page>"""
import sys, pathlib, runpy
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from manga_gabarit import strip3, apply
F = lambda *a: strip3(*a)
N = dict(rack=False, nuit=False)
ld = lambda f: runpy.run_path(str(pathlib.Path(__file__).with_name(f)), run_name='lib')
PERL = [svg for _, svg in ld('manga30.py')['STRIPS']]
LATEX = [svg for _, svg in ld('manga31.py')['STRIPS']]
m33 = ld('manga33.py'); U = [m33['NEUF']['U1'], m33['ANC']['c7'], m33['NEUF']['U3'], m33['NEUF']['U4'], m33['NEUF']['U6']]
RUN = [
 F("mgr1", "le poste mal compris", "RUN 1",
   dict(term=["« gestionnaire d'application ? »", "  « je développe des", "  nouvelles fonctions »"], bulle=["C'est du", "BUILD, non ?"]),
   dict(term=["première semaine :", "  incidents, demandes, extractions", "  aucune n'est suivie"], **N, who='mika', expr='shock', sfx="RUN"),
   "le service d'abord", ["demandes et incidents", "extractions et scripts", "mises en production", "communication aux référents"],
   "En RUN, la continuité du service passe avant les nouveautés : demandes, incidents, extractions et mises en production suivies de bout en bout."),
 F("mgr2", "la demande au téléphone", "RUN 2",
   dict(term=["« tu peux me sortir la liste ?", "  c'est urgent »", "  (au téléphone)"], bulle=["Je le fais", "tout de suite."]),
   dict(term=["trois jours plus tard :", "  « ce n'était pas ça »", "  aucune trace de la demande"], **N, who='kai', expr='shock', sfx="?"),
   "tout passe par un ticket", ["besoin écrit et précis", "qualification et priorité", "délai annoncé", "validation et clôture"],
   "Une demande orale se perd et se contredit : ticket, besoin précis, priorité et validation écrite."),
 F("mgr3", "corriger sans comprendre", "RUN 3",
   dict(term=["courriers PDF en échec", "  « je relance tout »", "  (sans lire le journal)"], bulle=["Ça passera", "peut-être."]),
   dict(term=["relance : même échec", "  2 heures perdues", "  référents sans nouvelles"], sfx="×2"),
   "une méthode, des preuves", ["symptôme et périmètre", "qu'est-ce qui a changé ?", "journal et donnée en cause", "contournement et message"],
   "Relancer sans comprendre reproduit l'échec : symptôme, chronologie, preuves, puis contournement et information des référents."),
 F("mgr4", "l'export complet", "RUN 4",
   dict(term=["« envoie-moi toute la base »", "  export de 400 000 personnes", "  par e-mail"], bulle=["C'est ce", "qu'il a", "demandé."]),
   dict(term=["fichier transféré à un tiers", "  données personnelles exposées", "  déclaration obligatoire"], **N, who='mika', expr='shock', sfx="RGPD"),
   "le besoin, pas plus", ["besoin réel et autorisé", "colonnes minimales", "transfert sécurisé", "trace dans le ticket"],
   "Une extraction se limite au besoin réel et autorisé : données minimales, transfert sécurisé, trace."),
 F("mgr5", "la version livrée sans notes", "RUN 5",
   dict(term=["prestataire : version livrée", "  la veille à 18 h", "  sans notes de version"], bulle=["On installe", "quand même."]),
   dict(term=["lendemain :", "  un rapport a changé de format", "  référents non prévenus"], sfx="surprise"),
   "coordonner avec des critères", ["livrables vérifiés", "recette sur ce qui change", "point de décision", "messages aux référents"],
   "Sans notes de version, on ne recette ni ne prévient personne : on vérifie les livrables et on décide au point de go."),
]
DATA = [
 F("mgd1", "la jointure qui multiplie", "Données 1",
   dict(term=["SELECT … FROM dossier", "  JOIN courrier …", "  12 000 lignes"], bulle=["Il y a", "8 000 dossiers."]),
   dict(term=["export envoyé", "  dossiers comptés deux fois", "  chiffres faux en comité"], **N, who='kai', expr='shock', sfx="×1,5"),
   "vérifier chaque extraction", ["compter avant et après la jointure", "agréger ou EXISTS", "bornes de dates", "contrôle de volume"],
   "Une jointure un-à-plusieurs multiplie les lignes : on compte à chaque étape avant d'envoyer une extraction."),
 F("mgd2", "la requête sans index", "Données 2",
   dict(term=["db.dossiers.find({statut:…})", "  .sort({creeLe:-1})", "  20 secondes"], bulle=["MongoDB est", "rapide."]),
   dict(term=["explain() : COLLSCAN", "  2 millions de documents lus", "  pour 20 résultats"], sfx="COLL"),
   "le bon index", ["explain(\"executionStats\")", "index sur filtre et tri", "validation avant création", "mesure avant et après"],
   "Sans index adapté, MongoDB lit toute la collection : explain() le montre, un index sur le filtre et le tri le corrige."),
 F("mgd3", "l'agrégation de 40 minutes", "Données 3",
   dict(term=["extraction lancée à 10 h", "  sur le primaire", "  en pleine journée"], bulle=["Juste un", "export."]),
   dict(term=["application ralentie", "  pour tous les utilisateurs", "  opération toujours en cours"], **N, who='mika', expr='angry', pose='hips', sfx="40 min"),
   "extraire sans nuire", ["currentOp puis killOp", "extraction sur un secondaire", "hors heures de charge", "index adapté"],
   "Une extraction lourde sur le primaire en journée pénalise tout le monde : on la déplace sur un secondaire ou hors des heures de charge."),
]
TCL = [
 F("mgtc1", "les accolades et les guillemets", "TCL 1",
   dict(term=["puts {Fichier : $fichier}", "  # affiche $fichier", "  tel quel"], bulle=["La variable", "ne marche", "pas !"]),
   dict(term=["rapport avec « $fichier »", "  au lieu du nom", "  envoyé aux référents"], sfx="$"),
   "connaître les substitutions", ["$ : variable", "[ ] : commande", "{ } : aucune substitution", "\" \" : substitutions"],
   "En TCL, les accolades empêchent toute substitution : trois règles suffisent à lire et corriger un script."),
 F("mgtc2", "le expect sans délai", "TCL 2",
   dict(term=["expect \"ftp>\"", "  # aucune branche timeout", "  script de nuit"], bulle=["Le serveur", "répond", "toujours."]),
   dict(term=["message inattendu", "  script bloqué jusqu'au matin", "  fichier du jour manquant"], **N, who='kai', expr='shock', sfx="∞"),
   "des délais partout", ["set timeout", "branche timeout", "sortie en erreur", "journal de l'étape"],
   "Un expect sans délai attend pour toujours un texte qui ne viendra pas : délai, branche d'erreur, journal."),
]
LANG = [
 F("mglg1", "l'encodage inconnu", "Python",
   dict(term=["open(fichier).read()", "  UnicodeDecodeError", "  en production"], bulle=["Chez moi,", "ça marche."]),
   dict(term=["fichier du partenaire", "  en Latin-1", "  traitement arrêté"], sfx="é?"),
   "l'encodage est un contrat", ["vérifier l'encodage réel", "encoding explicite", "règle pour les caractères invalides", "documenter avec le fournisseur"],
   "Un fichier lu avec le mauvais encodage fait tomber le traitement : on vérifie, on précise l'encodage, et on le documente."),
 F("mglg2", "la première ligne de la trace", "Java",
   dict(term=["DataAccessException…", "  (première ligne lue)", "  « c'est la base »"], bulle=["J'appelle", "le DBA."]),
   dict(term=["Caused by : pool épuisé", "  par un traitement parallèle", "  la base allait bien"], **N, who='mika', expr='shock', sfx="Caused"),
   "lire jusqu'à la cause", ["dernier « Caused by »", "première ligne de notre code", "donnée du moment", "preuve avant d'escalader"],
   "La première ligne d'une trace n'est souvent qu'un symptôme : la cause est au dernier « Caused by »."),
 F("mglg3", "l'écran d'hier", "JavaScript",
   dict(term=["après la mise en production :", "  « rien n'a changé »", "  pour un utilisateur"], bulle=["La version", "n'est pas", "passée ?"]),
   dict(term=["son navigateur :", "  ancien JavaScript en cache", "  les autres voient la nouvelle"], sfx="cache"),
   "vérifier le cache", ["rechargement forcé", "en-têtes de cache", "fichiers versionnés", "console et réseau"],
   "Une ancienne version affichée chez un seul utilisateur est souvent son cache : rechargement forcé et fichiers versionnés."),
]
GD = [
 F("mggd1", "le script modifié sur le serveur", "git et Docker",
   dict(term=["vi /opt/scripts/export.pl", "  (en production)", "  aucun commit"], bulle=["Petite", "correction."]),
   dict(term=["livraison suivante :", "  correction écrasée", "  le bug revient"], **N, who='kai', expr='shock', sfx="écrasé"),
   "tout passe par git", ["branche et commit", "demande de fusion relue", "livraison par la procédure", "étiquette de version"],
   "Un script corrigé directement sur le serveur disparaît à la livraison suivante : tout passe par git et la procédure."),
]
EXPLOIT = [
 F("mgex1", "la sauvegarde jamais restaurée", "Exploitation",
   dict(term=["sauvegarde : « OK »", "  chaque nuit depuis 2 ans", "  jamais restaurée"], bulle=["On est", "protégés."]),
   dict(term=["jour de la restauration :", "  fichiers vides depuis 6 mois", "  données perdues"], **N, who='mika', expr='shock', sfx="vide"),
   "restaurer pour prouver", ["restauration de test régulière", "contrôle des volumes", "runbook de restauration", "alerte si échec"],
   "Une sauvegarde jamais restaurée n'est qu'une hypothèse : on restaure régulièrement en test et on contrôle."),
 F("mgex2", "la recette du bon cas", "Recette",
   dict(term=["recette : 3 cas nominaux", "  « tout est vert »", "  volume de test : 50 dossiers"], bulle=["C'est", "validé."]),
   dict(term=["fin de mois en production :", "  traitement de 4 heures", "  au lieu de 40 minutes"], sfx="4 h"),
   "recetter ce qui casse", ["non-régression", "volumes réels", "exploitabilité", "retour arrière testé"],
   "Une recette sur quelques cas faciles ne prouve rien : volumes réels, non-régression, exploitabilité et retour arrière."),
]
ENT = [
 F("mgen1", "réciter le CV", "Entretien 1",
   dict(term=["« présentez-vous »", "  … liste chronologique", "  de tous les postes"], bulle=["En 2012…"]),
   dict(term=["le recruteur décroche", "  rien sur le RUN", "  aucun exemple"], **N, who='mika', expr='shock', sfx="zzz"),
   "deux minutes, un fil", ["expérience RUN", "socle Perl, SQL, Linux", "un exemple chiffré", "pourquoi cette mission"],
   "Une présentation qui déroule le CV perd l'auditoire : un fil, un exemple, un lien avec le poste."),
 F("mgen2", "« Perl, j'en ai fait un peu »", "Entretien 2",
   dict(term=["« et en Perl ? »", "  « j'en ai fait un peu", "  il y a longtemps »"], bulle=["Ça revient", "vite."]),
   dict(term=["« lisez ce script »", "  références, contexte, regex", "  … hésitation"], **N, who='kai', expr='shock', sfx="Perl"),
   "prouver par la pratique", ["cours Perl et TP faits", "script fiabilisé à montrer", "one-liners maîtrisés", "DBI avec paramètres"],
   "Pour la compétence principale, « un peu » ne suffit pas : on montre des scripts lus, fiabilisés et testés."),
 F("mgen3", "« je ne connais pas TCL »", "Entretien 3",
   dict(term=["« et TCL ? »", "  « jamais utilisé »", "  (et rien d'autre)"], bulle=["C'est vieux."]),
   dict(term=["le recruteur note :", "  « peu curieux »", "  (curiosité exigée)"], sfx="?"),
   "montrer la curiosité", ["les trois règles de substitution", "TP en conteneur", "Expect et ses pièges", "plan pour monter en compétence"],
   "Ne pas connaître un outil n'est pas grave ; ne rien en dire l'est : montrer ce qu'on a appris et comment on progresse."),
 F("mgen4", "pas de question à poser", "Entretien 4",
   dict(term=["« avez-vous des questions ? »", "  « non, tout est clair »"], bulle=["Merci."]),
   dict(term=["le recruteur note :", "  « peu projeté", "  dans la mission »"], **N, who='mika', expr='shock', sfx="…"),
   "préparer ses questions", ["traitements critiques", "processus de mise en production", "incidents récurrents", "acteurs de la mission"],
   "Ne poser aucune question donne l'image de quelqu'un qui ne se projette pas : quatre questions préparées sur leur contexte."),
]
TOUS = RUN + PERL + LATEX + U + DATA + TCL + LANG + GD + EXPLOIT + ENT
STRIPS = [(f"c{i}", svg) for i, svg in enumerate(TOUS, 1) if not (16 <= i <= 24)]   # chapitres LaTeX : fiches visuelles à la place des planches
if __name__ == '__main__': apply(sys.argv[1], STRIPS)
