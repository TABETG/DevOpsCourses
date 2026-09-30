"""Préparer une mission de gestionnaire d'application (RUN) Perl et LaTeX. Contexte générique.
Reprend les cours complets Perl, LaTeX et Unix, ajoute la mission RUN, SQL et MongoDB, TCL, Python, Java, JavaScript,
git et Docker, exploitation et recette technique, et une banque de questions-réponses.
Usage : python3 mission2_pages.py <dossier>"""
import sys, runpy, pathlib, os
ICI = pathlib.Path(__file__).parent
g = runpy.run_path(str(ICI / 'front_gen.py'), run_name='front'); ch, page = g['ch'], g['page']
def T(rows, head): return '<div class="tablewrap"><table><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table></div>'
def CK(titre, items): return f'<p class="liste-titre">{titre}</p><ul class="liste-controle">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'
def ET(items): return '<ol class="etapes">' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>'
def QR(items): return '<div class="qr">' + ''.join(f'<details class="qr-item"><summary>{q}</summary><div class="rep">{r}</div></details>' for q, r in items) + '</div>'
A = lambda f, l: f'<a href="{f}">{l}</a>'
def charger(fichier, cle):                     # reprendre les chapitres d'un autre cours sans régénérer sa page
    ancien = sys.argv[:]; os.makedirs('/tmp/sans-effet/cours-devops', exist_ok=True); sys.argv = ['x', '/tmp/sans-effet/cours-devops']   # le générateur n'accepte qu'un dossier nommé cours-devops
    import shutil; shutil.copy(ICI.parent / 'devops-00-fondations.html' if (ICI.parent / 'devops-00-fondations.html').exists() else '/home/claude/work/cours-devops/devops-00-fondations.html', '/tmp/sans-effet/cours-devops/')
    try: return runpy.run_path(str(ICI / fichier), run_name='lib')[cle]
    finally: sys.argv = ancien
DK = "Tout en conteneur : PostgreSQL, MongoDB, Perl, TeX Live, Python et TCL tournent par Docker Compose, rien n'est installé sur le poste."

# ============================ PARTIE 1 : LA MISSION RUN ============================
RUN = [
ch("Comprendre le poste : gestionnaire d'application en RUN", 'j',
 ["Le gestionnaire d'application en RUN fait vivre une application en production : il traite les demandes et les évolutions, diagnostique les incidents, réalise extractions et petits développements, coordonne les mises en production et informe les référents.", "Il travaille au carrefour des référents métier, des équipes d'infrastructure, des prestataires et éditeurs, et du support ; sa valeur tient à sa connaissance de l'application et à sa rigueur.", "Le socle attendu : Perl en priorité, LaTeX si possible, des bases de Python, TCL, Java et JavaScript, SQL et MongoDB, Linux et le shell, git et Docker, et les bonnes pratiques d'exploitation et de recette."],
 ["Décrire les activités d'un gestionnaire d'application en RUN", "Situer les acteurs et les types de demandes", "Évaluer ses écarts avec les compétences attendues"],
 [("Les activités attendues", T([
    ("Traiter demandes courantes et évolutions", "hors projet et en mode projet", "partie 1, chapitre 2"),
    ("Requêtes d'extraction et développements", "SQL, MongoDB, scripts Perl et Python", "parties 2, 5, 7"),
    ("Qualifier et diagnostiquer un incident", "et suivre sa résolution", "partie 1, chapitre 3 ; partie 4"),
    ("Coordonner les mises en production", "acteurs internes et externes", "partie 1, chapitre 5"),
    ("Analyser la documentation", "technique et fonctionnelle", "partie 1, chapitre 5"),
    ("Communiquer aux référents", "changements et dysfonctionnements", "partie 1, chapitre 5")], ("Activité", "Précision", "Où la travailler")), None),
  ("Les compétences et leur niveau", "", T([
    ("Perl", "principal", "partie 2 (cours complet)", A('cours-71-perl.html', 'cours Perl')),
    ("LaTeX", "si possible", "partie 3 (cours complet)", A('cours-75-latex.html', 'cours LaTeX')),
    ("Linux, shell, commandes GNU", "base", "partie 4", A('devops-00-fondations.html', 'DevOps niveau 0') + ', ' + A('devops-10-aide-memoire.html', 'aide-mémoire')),
    ("SQL et MongoDB", "connaissance", "partie 5", A('cours-61-data-platform-aws-talend.html', 'Data Platform')),
    ("TCL", "connaissance", "partie 6", "—"),
    ("Python, Java, JavaScript", "connaissance", "partie 7", A('cours-31-ia-agentique.html', 'IA agentique (Python)') + ', ' + A('cours-13-java-pki-signature-electronique.html', 'Java PKI') + ', ' + A('cours-01-react.html', 'React')),
    ("git et Docker", "base", "partie 8", A('devops-00-fondations.html', 'DevOps niveau 0 (Git)') + ', ' + A('devops-01-virtualisation-et-conteneurs.html', 'niveau 1 (Docker)')),
    ("Exploitation et recette technique", "bonnes pratiques", "partie 9", A('devops-06-observabilite.html', 'niveau 6') + ', ' + A('devops-08-sre-et-architecture.html', 'niveau 8')),
    ("Entretien", "", "partie 10", A('cours-92-savoir-etre-situations-et-attitudes.html', 'Savoir-être : situations'))], ("Compétence", "Niveau attendu", "Dans cette page", "Cours du site"))),
  ("Le vocabulaire du RUN", "", T([
    ("Demande", "besoin standard (extraction, accès, paramétrage)", "traitée selon un délai convenu"),
    ("Évolution", "modification de l'application", "estimée, planifiée, recettée"),
    ("Incident", "interruption ou dégradation du service", "rétablir vite, puis comprendre"),
    ("Problème", "cause d'incidents répétés", "analyse de fond, correction durable"),
    ("Changement", "toute modification de la production", "planifié, validé, tracé"),
    ("Niveaux de support", "N1 (accueil), N2 (application), N3 (expertise, éditeur)", "le gestionnaire d'application est souvent au N2")], ("Terme", "Sens", "Traitement")))],
 [("Quelle différence entre RUN et BUILD ?", "Le BUILD construit (projets, nouvelles fonctions) ; le RUN fait fonctionner ce qui existe : demandes, incidents, maintenance, mises en production. Le gestionnaire d'application en RUN participe aussi à des évolutions « en mode projet », mais sa priorité reste la continuité du service."),
  ("Question d'entretien : que fait un gestionnaire d'application ?", "Il est le référent technique d'une application en production : il traite demandes et évolutions, diagnostique et suit les incidents, réalise extractions et scripts, coordonne les mises en production et informe les référents, en s'appuyant sur une connaissance fine de l'application et de sa documentation.")],
 ("Ma grille de préparation", ["Noter son niveau (0 à 4) sur chaque compétence du tableau.", "Choisir les trois parties à travailler en priorité (Perl d'abord).", "Préparer trois exemples vécus : un incident diagnostiqué, une extraction délicate, une mise en production coordonnée."],
  "Attendu : une grille chiffrée, un ordre de travail, et trois histoires STAR prêtes pour l'entretien.")),

ch("Traiter les demandes courantes et les évolutions", 'c',
 ["Chaque demande suit le même cycle : réception, qualification, estimation, réalisation, validation par le demandeur, clôture tracée.", "On distingue la demande standard (traitée vite, selon un mode opératoire), l'évolution (estimée et recettée) et le projet (planifié avec les autres acteurs).", "La priorité se décide sur l'impact et l'urgence, pas sur qui crie le plus fort ; et on dit tôt quand un délai ne peut pas être tenu."],
 ["Qualifier et prioriser une demande", "Estimer et planifier une évolution", "Tracer et clôturer proprement"],
 [("Le cycle d'une demande", "", ET(["<strong>Réception</strong> : ticket créé (jamais une demande orale seule), demandeur et besoin identifiés", "<strong>Qualification</strong> : demande standard, évolution ou projet ; informations manquantes demandées tout de suite", "<strong>Estimation</strong> : charge, risques, dépendances ; accord du demandeur si c'est une évolution", "<strong>Réalisation</strong> : selon le mode opératoire, en environnement de test d'abord", "<strong>Validation</strong> par le demandeur (recette si évolution)", "<strong>Clôture</strong> : ticket mis à jour, documentation complétée, délai mesuré"])),
  ("Prioriser", "", T([
    ("Impact fort, urgence forte", "service bloqué pour beaucoup d'utilisateurs", "immédiat"),
    ("Impact fort, urgence faible", "échéance réglementaire dans un mois", "planifié en priorité"),
    ("Impact faible, urgence forte", "gêne ponctuelle d'un utilisateur", "rapide si simple"),
    ("Impact faible, urgence faible", "confort, amélioration", "file normale")], ("Situation", "Exemple", "Traitement"))),
  ("Une fiche d'analyse", "", "texte::Demande : APP-1234 — ajout d'une colonne « date de clôture » dans l'export mensuel\nType : évolution (modification du script d'export Perl et du modèle LaTeX du rapport)\nDemandeur : référent gestion, validation par le même\nAnalyse : script export_mensuel.pl (requête SQL + modèle rapport.tex) ; impact sur deux autres rapports : non\nCharge estimée : 1,5 jour (développement 0,5, tests 0,5, recette et mise en production 0,5)\nRisques : volume du mois de décembre ; format des dates\nPlanning : recette le 12, mise en production le 15 avec la version mensuelle\nDocumentation à mettre à jour : dossier d'exploitation, fiche de l'export")],
 [("Un référent te demande une extraction « pour hier » par téléphone. Que fais-tu ?", "Je lui demande de créer le ticket (ou je le crée pour lui) avec le besoin précis, je qualifie l'urgence réelle, et je traite selon la priorité ; une demande sans trace ne peut être ni suivie, ni justifiée, ni reproduite."),
  ("Question d'entretien : comment gères-tu plusieurs demandes urgentes en même temps ?", "Je les classe par impact et urgence, je traite d'abord ce qui bloque le service, j'informe chaque demandeur du délai réaliste, et je fais arbitrer par le responsable si deux urgences se valent ; je ne promets pas ce que je ne peux pas tenir.")],
 ("Une semaine de demandes", ["Qualifier dix demandes fictives (standard, évolution, projet) et les prioriser.", "Rédiger la fiche d'analyse de deux évolutions.", "Clôturer chaque ticket avec sa trace et son temps passé."],
  "Attendu : chaque demande a un type, une priorité justifiée et un délai annoncé ; les fiches d'analyse identifient impacts et risques.")),

ch("Qualifier, diagnostiquer un incident et suivre sa résolution", 's',
 ["Un incident se traite en deux temps : rétablir le service le plus vite possible (contournement), puis comprendre et corriger la cause.", "Le diagnostic suit une méthode : symptôme précis, périmètre, chronologie (qu'est-ce qui a changé ?), hypothèses, preuves (journaux, données, versions), conclusion.", "Le gestionnaire d'application suit l'incident jusqu'au bout, même quand la correction dépend d'un autre acteur, et informe les référents à chaque étape."],
 ["Qualifier un incident et fixer sa priorité", "Diagnostiquer avec méthode et preuves", "Suivre la résolution et communiquer"],
 [("La méthode", "", ET(["<strong>Symptôme</strong> : qu'est-ce qui ne marche pas, pour qui, depuis quand, message exact", "<strong>Périmètre</strong> : tous les utilisateurs ou certains ? une fonction ou toute l'application ?", "<strong>Chronologie</strong> : qu'est-ce qui a changé récemment (mise en production, données, infrastructure, calendrier) ?", "<strong>Hypothèses</strong> classées de la plus probable à la moins probable", "<strong>Preuves</strong> : journaux, données, versions, reproduction en test", "<strong>Contournement</strong> si possible, puis <strong>correction</strong> et vérification", "<strong>Clôture</strong> : cause, action, durée d'impact ; problème ouvert si l'incident peut revenir"])),
  ("Les premiers gestes techniques", "", r"""tail -n 200 /var/log/appli/traitement.log | grep -E "ERROR|FATAL|died"      # dernières erreurs
grep -n "ERROR" traitement.log | awk -F: '{print $1}' | head -1                  # première erreur de la nuit
ls -lt /data/entree | head                                                        # fichiers arrivés, tailles, heures
psql -c "SELECT statut, COUNT(*) FROM dossier WHERE maj > now() - interval '1 day' GROUP BY statut;"
git log --since="3 days ago" --oneline                                            # ce qui a changé dans le code
docker compose ps ; docker compose logs --since 1h appli                          # état des services en conteneur"""),
  ("Suivre et communiquer", "", "texte::Objet : [Incident] Génération des courriers PDF interrompue — en cours de traitement\n\nBonjour,\n\nDepuis 7 h 40, la génération des courriers PDF échoue pour les dossiers du jour.\nImpact : les courriers du jour ne sont pas envoyés ; les autres fonctions de l'application fonctionnent.\nCause identifiée : un caractère spécial non échappé dans une donnée bloque la composition LaTeX.\nAction : correction du script d'échappement en cours de test ; relance prévue à 11 h.\nProchain point : 11 h 15, ou plus tôt si la situation évolue.")],
 [("Les courriers PDF ne sortent plus depuis ce matin. Par quoi commences-tu ?", "Je précise le symptôme (tous les courriers ou certains, message d'erreur), je regarde le journal de génération et le fichier .log de LaTeX de la première génération en échec, je cherche ce qui a changé (données, modèle, version), je propose un contournement (écarter le dossier fautif) et j'informe les référents."),
  ("Question d'entretien : comment suis-tu un incident qui dépend d'un prestataire ?", "Je garde le ticket, je fournis au prestataire toutes les preuves, je fixe un point régulier, j'informe les référents de l'avancement, et je vérifie moi-même la correction en test puis en production avant de clôturer.")],
 ("Incidents simulés", ["Trois incidents injectés dans un environnement de test : script Perl en échec, génération LaTeX bloquée, extraction SQL trop lente.", "Pour chacun : méthode complète, preuves, contournement, correction, message aux référents.", "Ouvrir un « problème » pour l'incident qui peut revenir."],
  "Attendu : chaque incident est expliqué preuve à l'appui ; les messages sont clairs pour un non-technicien ; le problème décrit la correction durable.")),

ch("Réaliser des extractions et des petits développements", 'c',
 ["Une extraction se prépare : besoin précis, données minimales, requête testée sur un environnement de test, volumes vérifiés, format convenu, destinataire autorisé.", "Les données personnelles demandent des précautions : besoin légitime, minimisation, transfert sécurisé, conservation limitée ; en cas de doute, on demande l'avis du responsable des données.", "Les petits développements (scripts Perl ou Python, requêtes, modèles) suivent les règles du code : dépôt git, relecture, tests, livraison tracée."],
 ["Préparer une extraction fiable et conforme", "Écrire un script d'extraction réutilisable", "Livrer un petit développement proprement"],
 [("Préparer une extraction", "", CK("Avant de lancer une extraction", ["Besoin écrit et validé : quelles données, quel périmètre, quelle période, pour qui", "Données minimales : uniquement les colonnes nécessaires, anonymisées si possible", "Requête testée sur un environnement de test, volumes cohérents", "Exécution avec un compte en lecture seule, hors des heures de forte charge si l'extraction est lourde", "Format convenu (CSV, séparateur, encodage UTF-8), fichier nommé et daté", "Transfert sécurisé au destinataire autorisé, trace dans le ticket"])),
  ("Un script d'extraction", "Un script paramétré et journalisé remplace les copier-coller de requêtes : il se relance, se relit et se teste.", r"""#!/usr/bin/env perl
use v5.36; use DBI; use Text::CSV; use Getopt::Long;
GetOptions(\my %o, 'mois=s', 'sortie=s') && $o{mois} =~ /^\d{4}-\d{2}$/ or die "usage : $0 --mois AAAA-MM --sortie fichier.csv\n";
my $dbh = DBI->connect("dbi:Pg:dbname=appli;host=$ENV{PGHOST}", $ENV{PGUSER}, $ENV{PGPASSWORD}, { RaiseError => 1, ReadOnly => 1 });
my $sth = $dbh->prepare(q{SELECT d.numero, d.statut, to_char(d.cree_le, 'YYYY-MM-DD') FROM dossier d
                          WHERE to_char(d.cree_le, 'YYYY-MM') = ? ORDER BY d.numero});
$sth->execute($o{mois});
my $csv = Text::CSV->new({ binary => 1, sep_char => ';', eol => "\n" });
open my $out, '>:encoding(UTF-8)', $o{sortie} or die "$o{sortie} : $!";
$csv->print($out, [qw(numero statut date_creation)]); my $n = 0;
while (my $r = $sth->fetchrow_arrayref) { $csv->print($out, $r); $n++ }
close $out; say "$n lignes extraites pour $o{mois}"; exit($n ? 0 : 4);"""),
  ("Livrer proprement", "Même un petit script passe par le dépôt git (branche, relecture), a un test minimal, une documentation d'usage, et se livre par la procédure prévue ; on ne dépose jamais un script modifié à la main sur un serveur de production.", None)],
 [("Un référent demande « toute la base clients » pour une analyse. Que réponds-tu ?", "Je reviens au besoin réel : quelles informations, sur quel périmètre, pour quel usage ; je propose une extraction minimale, anonymisée si possible, et je vérifie qu'il est autorisé à recevoir ces données ; un export complet de données personnelles n'est presque jamais justifié."),
  ("Question d'entretien : comment fiabilises-tu une extraction récurrente ?", "Je la transforme en script versionné, paramétré, journalisé, avec contrôle du nombre de lignes et un format stable, planifié si besoin ; ainsi elle est reproductible, relisible et vérifiable.")],
 ("Extractions de la mission", ["PostgreSQL et MongoDB en conteneur avec des données fictives.", "Trois extractions (SQL, MongoDB, jointure des deux dans un script) livrées en CSV UTF-8.", "Une extraction transformée en script versionné avec test et documentation."],
  "Attendu : chaque extraction répond au besoin écrit, avec des volumes vérifiés ; aucune donnée personnelle inutile ; le script se relance à l'identique.")),

ch("Coordonner les mises en production, analyser la documentation, communiquer", 's',
 ["Une mise en production coordonnée réunit plusieurs acteurs (éditeur ou prestataire, infrastructure, métier) : planning partagé, rôles clairs, point de décision (go ou pas go), retour arrière prêt.", "Analyser la documentation technique et fonctionnelle, c'est en extraire ce qui compte pour le RUN : ce qui change, les prérequis, les impacts, les modes opératoires, les risques.", "Communiquer aux référents les changements et les dysfonctionnements se fait par des messages courts, réguliers et compréhensibles."],
 ["Coordonner une mise en production à plusieurs acteurs", "Tirer l'essentiel d'une documentation", "Rédiger les communications aux référents"],
 [("Coordonner", "", CK("Préparation d'une mise en production", ["Planning partagé : date, fenêtre, étapes, qui fait quoi", "Livrables reçus et vérifiés (version, notes de version, scripts, mode opératoire)", "Recette technique et fonctionnelle validée, procès-verbal signé", "Point de décision la veille : go ou pas go, critères écrits", "Retour arrière préparé et testé, décision au plus tard à une heure fixée", "Contrôles après installation définis, vérification par les référents", "Messages d'annonce, de fin et de résultat préparés"])),
  ("Analyser une documentation", "", T([
    ("Notes de version", "fonctions changées, anomalies corrigées, limites connues", "ce qui doit être recetté et annoncé"),
    ("Prérequis", "versions, paramètres, accès, espace disque", "ce qui doit être prêt avant"),
    ("Mode opératoire", "étapes, contrôles, retour arrière", "ce qui sera joué et par qui"),
    ("Impacts", "données, interfaces, traitements, utilisateurs", "qui prévenir, quoi surveiller"),
    ("Documentation fonctionnelle", "règles de gestion, écrans, cas particuliers", "cas de recette et questions au métier")], ("Section", "Ce qu'on y cherche", "Ce qu'on en fait"))),
  ("Communiquer aux référents", "", "texte::Objet : [Changement] Version 3.8 de l'application — installation jeudi 20 h – 22 h\n\nBonjour,\n\nLa version 3.8 sera installée jeudi de 20 h à 22 h.\nCe qui change pour vous : nouvel export des dossiers clos ; correction du calcul des délais sur les courriers de relance.\nPendant l'intervention : application indisponible.\nAprès l'intervention : merci de vérifier vendredi matin l'export des dossiers clos ; tout écart est à signaler par ticket.\nUn message confirmera la fin de l'intervention.")],
 [("Le prestataire livre la veille de la mise en production sans notes de version. Que fais-tu ?", "Je demande immédiatement les notes de version et le mode opératoire, et je rends visible le risque au point de décision : sans savoir ce qui change, on ne peut ni recetter ni prévenir les référents ; si l'information n'arrive pas à temps, je propose de reporter."),
  ("Question d'entretien : comment communiques-tu un dysfonctionnement à des non-techniciens ?", "En trois points : ce qui ne marche pas pour eux, ce que l'on fait et quand on revient vers eux ; sans jargon, avec un contournement s'il existe, et des messages réguliers jusqu'au rétablissement.")],
 ("Une mise en production coordonnée", ["Planifier une mise en production fictive avec trois acteurs (prestataire, infrastructure, métier) : planning, rôles, critères de go.", "Analyser des notes de version fournies et en tirer impacts, recette et messages.", "Rédiger les trois messages (annonce, fin, incident) et le compte rendu."],
  "Attendu : un planning clair, des critères de décision écrits, une recette ciblée sur ce qui change, des messages compréhensibles par un référent métier.")),
]

# ============================ PARTIE 5 : SQL ET MONGODB ============================
DATA = [
ch("SQL pour les extractions et le diagnostic", 'c',
 ["Les extractions reposent sur quelques constructions maîtrisées : jointures, regroupements, fonctions de fenêtre, expressions de table (WITH), gestion des dates et des valeurs nulles.", "Une requête d'extraction se vérifie : nombre de lignes, doublons introduits par une jointure, valeurs nulles, bornes de dates.", "Toute modification de données se fait dans une transaction, après avoir compté les lignes concernées, avec l'accord prévu et une sauvegarde de ce qui change."],
 ["Écrire des requêtes d'extraction justes", "Éviter les pièges (doublons, nulls, dates)", "Modifier des données en production sans risque"],
 [("Les constructions utiles", DK, r"""-- dossiers par statut et par mois, avec le rang des mois les plus chargés
WITH par_mois AS (
  SELECT date_trunc('month', cree_le) AS mois, statut, COUNT(*) AS nb
  FROM dossier WHERE cree_le >= DATE '2026-01-01' GROUP BY 1, 2
)
SELECT mois, statut, nb, RANK() OVER (PARTITION BY statut ORDER BY nb DESC) AS rang FROM par_mois ORDER BY mois, statut;
-- dernier courrier de chaque dossier (fonction de fenêtre)
SELECT * FROM (SELECT c.*, ROW_NUMBER() OVER (PARTITION BY dossier_id ORDER BY envoye_le DESC) AS n FROM courrier c) t WHERE n = 1;
-- export CSV sans accès au serveur : \copy (SELECT …) TO 'export.csv' WITH (FORMAT csv, HEADER, DELIMITER ';')"""),
  ("Les pièges", "", T([
    ("Jointure qui multiplie les lignes", "un dossier a plusieurs courriers", "compter avant et après, agréger ou ROW_NUMBER"),
    ("NULL dans une comparaison", "WHERE statut <> 'CLOS' exclut les NULL", "IS NULL explicite, COALESCE"),
    ("Bornes de dates", "BETWEEN inclut minuit du dernier jour seulement", ">= début AND < lendemain"),
    ("NOT IN avec des NULL", "renvoie zéro ligne", "NOT EXISTS"),
    ("Tri absent", "ordre imprévisible", "ORDER BY explicite")], ("Piège", "Exemple", "Parade"))),
  ("Modifier sans risque", "", r"""BEGIN;
SELECT COUNT(*) FROM dossier WHERE statut = 'EN_ATTENTE' AND cree_le < DATE '2025-01-01';   -- 1 243 attendu ?
CREATE TABLE sauvegarde_app_1234 AS SELECT * FROM dossier WHERE statut = 'EN_ATTENTE' AND cree_le < DATE '2025-01-01';
UPDATE dossier SET statut = 'ARCHIVE' WHERE statut = 'EN_ATTENTE' AND cree_le < DATE '2025-01-01';   -- même nombre de lignes ?
COMMIT;      -- ou ROLLBACK si le nombre diffère ; ticket APP-1234 mis à jour avec la requête et le résultat""")],
 [("Ton extraction compte 12 000 lignes au lieu des 8 000 attendues. Première vérification ?", "Une jointure qui multiplie les lignes (relation un-à-plusieurs) : je compte les lignes de la table principale seule, puis après chaque jointure, et je corrige par un regroupement, EXISTS ou ROW_NUMBER."),
  ("Question d'entretien : comment fais-tu une mise à jour de données en production ?", "Sur demande tracée et validée, dans une transaction : je compte les lignes concernées, je sauvegarde ce qui va changer, j'exécute, je vérifie le nombre, puis je valide ; la requête et le résultat vont dans le ticket.")],
 ("Extractions SQL", ["PostgreSQL en conteneur avec des données fictives ; cinq extractions demandées par des référents.", "Vérifier chaque extraction (lignes, doublons, bornes) ; export CSV avec \\copy.", "Une mise à jour de masse en transaction avec sauvegarde, puis son retour arrière."],
  "Attendu : chaque extraction est juste et vérifiée ; la mise à jour et son retour arrière ramènent exactement l'état initial.")),

ch("MongoDB : documents, requêtes et agrégations", 'c',
 ["MongoDB stocke des documents JSON (BSON) dans des collections, sans schéma imposé : un même champ peut manquer ou changer de type d'un document à l'autre.", "On interroge avec find (filtres, projection, tri, limite) et on calcule avec le pipeline d'agrégation ($match, $group, $project, $unwind, $lookup).", "Les index rendent les requêtes rapides ; explain() montre si une requête utilise un index ou parcourt toute la collection."],
 ["Interroger une collection avec filtres et projections", "Calculer avec le pipeline d'agrégation", "Vérifier l'usage des index et exporter des données"],
 [("Requêtes", DK, r"""docker run -d --name mongo -p 27017:27017 mongo:7
docker exec -it mongo mongosh
use appli
db.dossiers.find({ statut: "OUVERT", "adresse.departement": { $in: ["75", "92"] } }, { numero: 1, statut: 1, _id: 0 }).sort({ creeLe: -1 }).limit(20)
db.dossiers.countDocuments({ piecesJointes: { $exists: true, $not: { $size: 0 } } })
db.dossiers.find({ historique: { $elemMatch: { action: "RELANCE", date: { $gte: ISODate("2026-09-01") } } } })
db.dossiers.find({ nom: { $regex: "^dup", $options: "i" } })            // expression régulière : à éviter sur de gros volumes sans index adapté"""),
  ("Agrégations", "", r"""db.dossiers.aggregate([
  { $match: { creeLe: { $gte: ISODate("2026-01-01") } } },
  { $group: { _id: { mois: { $dateToString: { format: "%Y-%m", date: "$creeLe" } }, statut: "$statut" }, nb: { $sum: 1 } } },
  { $sort: { "_id.mois": 1 } }
])
db.dossiers.aggregate([                                                    // un document par pièce jointe
  { $unwind: "$piecesJointes" },
  { $group: { _id: "$piecesJointes.type", total: { $sum: 1 }, tailleMoyenne: { $avg: "$piecesJointes.taille" } } }
])
db.courriers.aggregate([ { $lookup: { from: "dossiers", localField: "dossierId", foreignField: "_id", as: "dossier" } }, { $limit: 5 } ])"""),
  ("Index et exports", "", r"""db.dossiers.createIndex({ statut: 1, creeLe: -1 })
db.dossiers.find({ statut: "OUVERT" }).sort({ creeLe: -1 }).explain("executionStats")   // IXSCAN (index) ou COLLSCAN (parcours complet)
docker exec mongo mongoexport --db appli --collection dossiers --type csv --fields numero,statut,creeLe --query '{"statut":"CLOS"}' --out /tmp/clos.csv""")],
 [("Une requête sur les dossiers ouverts met 20 secondes. Que regardes-tu ?", "explain(\"executionStats\") : si le plan est un COLLSCAN, aucun index ne sert ; je crée un index adapté au filtre et au tri (par exemple { statut: 1, creeLe: -1 }) après validation, et je compare le temps avant et après."),
  ("Question d'entretien : différence entre une base relationnelle et MongoDB ?", "Le relationnel impose un schéma et des jointures entre tables ; MongoDB stocke des documents souples, souvent imbriqués, et privilégie la lecture d'un document complet. Les jointures existent ($lookup) mais coûtent ; on modélise selon les accès.")],
 ("Requêtes MongoDB", ["MongoDB en conteneur avec une collection de dossiers fictifs (champs imbriqués, tableaux).", "Cinq requêtes find et trois agrégations demandées par des référents.", "Créer un index, comparer explain() avant et après, exporter en CSV."],
  "Attendu : les résultats correspondent aux besoins ; le plan passe de COLLSCAN à IXSCAN ; l'export CSV s'ouvre correctement dans un tableur.")),

ch("MongoDB en exploitation", 's',
 ["En production, MongoDB tourne en jeu de réplicas : un primaire reçoit les écritures, les secondaires répliquent et prennent le relais par élection en cas de panne.", "Les sauvegardes (mongodump et mongorestore, ou sauvegardes de l'infrastructure) se testent par restauration ; la supervision suit opérations lentes, retard de réplication, connexions et espace disque.", "Les incidents courants : requête sans index, opération longue qui bloque, disque plein, retard de réplication, droits insuffisants."],
 ["Comprendre le jeu de réplicas et ses garanties", "Sauvegarder, restaurer et superviser", "Diagnostiquer les incidents courants"],
 [("Réplicas et garanties", "", T([
    ("Jeu de réplicas", "primaire et secondaires, élection automatique", "rs.status()"),
    ("writeConcern", "niveau de confirmation d'une écriture", "« majority » pour les données importantes"),
    ("readPreference", "où lire (primaire, secondaires)", "secondaires possibles pour les extractions lourdes"),
    ("Retard de réplication", "écart entre primaire et secondaires", "rs.printSecondaryReplicationInfo()")], ("Notion", "Rôle", "Commande ou réglage"))),
  ("Sauvegarder et superviser", "", r"""mongodump --uri "$MONGO_URI" --db appli --gzip --archive=/sauvegardes/appli_$(date +%F).gz
mongorestore --uri "$MONGO_URI_TEST" --gzip --archive=/sauvegardes/appli_2026-09-29.gz --nsFrom 'appli.*' --nsTo 'restauration.*'   # test de restauration
mongostat --uri "$MONGO_URI" 5          # opérations par seconde, connexions, mémoire
mongotop --uri "$MONGO_URI" 10          # temps passé par collection
db.serverStatus().connections ; db.stats()"""),
  ("Diagnostiquer", "", r"""db.currentOp({ secs_running: { $gte: 30 } })                 // opérations en cours depuis plus de 30 s
db.killOp(<opid>)                                             // arrêter une opération (après accord)
db.setProfilingLevel(1, { slowms: 200 })                      // journaliser les requêtes de plus de 200 ms
db.system.profile.find().sort({ ts: -1 }).limit(5)
db.getUsers() ; db.getRoles({ showBuiltinRoles: false })      // comptes et rôles de la base""")],
 [("L'application ralentit fortement ; db.currentOp() montre une agrégation qui tourne depuis 40 minutes. Que fais-tu ?", "J'identifie son origine (extraction lancée par qui ?), je préviens et j'arrête l'opération avec killOp après accord, puis je fais relancer l'extraction sur un secondaire ou hors des heures de forte charge, avec un index adapté."),
  ("Question d'entretien : comment vérifies-tu qu'une sauvegarde MongoDB est bonne ?", "En la restaurant régulièrement dans un environnement de test et en contrôlant le nombre de documents et quelques données clés ; une sauvegarde jamais restaurée n'est qu'une hypothèse.")],
 ("Exploiter MongoDB", ["Jeu de réplicas de trois nœuds en Compose ; arrêter le primaire et observer l'élection.", "Sauvegarde mongodump, restauration dans une autre base, contrôle des volumes.", "Provoquer une opération longue, la trouver avec currentOp, l'arrêter ; activer le profilage des requêtes lentes."],
  "Attendu : l'application continue après l'élection ; la restauration donne les mêmes volumes ; l'opération longue est trouvée et arrêtée en moins de deux minutes.")),
]

# ============================ PARTIE 6 : TCL ============================
TCL = [
ch("TCL : lire, corriger et maintenir des scripts", 'c',
 ["TCL (Tool Command Language) est un langage de script ancien, encore présent dans des outils d'automatisation et d'exploitation : tout y est commande, et tout est chaîne.", "Trois règles suffisent à le lire : $ substitue une variable, [ ] exécute une commande et la remplace par son résultat, { } empêche toute substitution alors que \" \" la permet.", "On y trouve listes, dictionnaires, procédures, expressions régulières, fichiers et exécution de commandes, avec catch ou try pour les erreurs."],
 ["Lire un script TCL grâce à ses règles de substitution", "Manipuler listes, dictionnaires, fichiers et procédures", "Gérer les erreurs et exécuter des commandes"],
 [("Les règles de base", "Pour s'entraîner : docker run --rm -it alpine:3.20 sh -c \"apk add --no-cache tcl && tclsh\".", r"""set fichier "rapport.csv"                      ;# variable
puts "Traitement de $fichier"                  ;# substitution de variable dans des guillemets
puts {Pas de substitution ici : $fichier}      ;# accolades : texte littéral
set n [llength [split "a;b;c" ";"]]            ;# crochets : résultat d'une commande (3)
if {$n > 2} { puts "plus de deux champs" } elseif {$n == 0} { puts "vide" } else { puts "court" }
foreach zone {N1 N2 S3} { puts "zone $zone" }
set total [expr {$n * 10 + 2}]                  ;# calcul : toujours expr entre accolades"""),
  ("Listes, dictionnaires, procédures, fichiers", "", r"""set zones [list N1 N2 S3]; lappend zones S4; puts [lindex $zones end]
set seuils [dict create N1 10 S3 25]; dict set seuils N2 12; puts [dict get $seuils S3]
proc gravite {texte {defaut P3}} {
    if {[regexp -nocase {gaz|incendie} $texte]} { return P1 }
    return $defaut
}
set f [open "incidents.csv" r]
while {[gets $f ligne] >= 0} { lassign [split $ligne ";"] id zone titre; puts "$id [gravite $titre]" }
close $f"""),
  ("Erreurs et commandes", "", r"""if {[catch {exec gzip -- $fichier} erreur]} { puts stderr "gzip a échoué : $erreur"; exit 2 }
try {
    set f [open $chemin r]
} on error {msg} {
    puts stderr "lecture impossible : $msg"; exit 2
} finally { catch {close $f} }
set sortie [exec ls -l /data/entree]           ;# exec lance le programme sans shell : pas d'injection par ; ou |""")],
 [("Pourquoi expr {$a + $b} plutôt que expr $a + $b ?", "Avec les accolades, TCL compile l'expression et ne substitue qu'une fois : c'est plus rapide et plus sûr ; sans accolades, une variable contenant du texte malveillant pourrait être évaluée comme une commande."),
  ("Question d'entretien : comment aborderais-tu un script TCL que tu ne connais pas ?", "Je le lance en test avec des entrées connues, je lis les procédures et les appels exec (effets de bord), je repère les chemins et les identifiants en dur, j'ajoute des traces (puts) si besoin, et je documente ce qu'il fait avant de le modifier.")],
 ("Maintenir un script TCL", ["Lancer tclsh en conteneur ; lire un script d'exploitation fourni et le documenter.", "Corriger deux anomalies (substitution mal placée, erreur non gérée).", "Ajouter une procédure et un traitement d'erreur avec catch ou try."],
  "Attendu : la documentation décrit entrées, sorties et effets ; les anomalies sont corrigées et testées ; le script sort avec un code non nul en cas d'erreur.")),

ch("TCL et Expect : automatiser les outils interactifs", 's',
 ["Expect, écrit en TCL, automatise les programmes interactifs (invites de commande, outils qui posent des questions) : il lance le programme (spawn), attend un texte (expect) et répond (send).", "C'est puissant mais fragile : délais, messages qui changent, mots de passe ; chaque script prévoit délais d'attente, cas d'erreur et journal.", "Quand c'est possible, on préfère une interface non interactive (API, options en ligne de commande) ; sinon Expect, ou son équivalent Python pexpect."],
 ["Écrire un script Expect robuste", "Sécuriser les identifiants et gérer les délais", "Choisir entre Expect, pexpect et une interface non interactive"],
 [("Un script Expect", "", r"""#!/usr/bin/expect -f
set timeout 20
log_file -a /var/log/appli/export_expect.log
spawn ftp serveur-historique.interne
expect {
    "Name*:"      { send "$env(FTP_USER)\r" }
    timeout       { puts stderr "pas d'invite de connexion"; exit 2 }
}
expect "Password:" ; send "$env(FTP_PASSWORD)\r"
expect {
    "ftp>"        { send "get export_du_jour.csv\r" }
    "Login failed" { puts stderr "identifiants refusés"; exit 3 }
    timeout       { puts stderr "délai dépassé après connexion"; exit 2 }
}
expect "ftp>" ; send "bye\r" ; expect eof"""),
  ("Robustesse et sécurité", "", T([
    ("Délais", "set timeout, branche timeout dans chaque expect", "le script ne reste jamais bloqué"),
    ("Messages variables", "motifs larges (*), plusieurs branches", "moins de faux échecs"),
    ("Identifiants", "variables d'environnement ou coffre, jamais en clair", "pas de fuite dans le dépôt"),
    ("Journal", "log_file, sans les mots de passe (log_user 0 au moment de l'envoi)", "diagnostic possible"),
    ("Codes retour", "exit avec des codes documentés", "exploitable par l'ordonnanceur")], ("Point", "Pratique", "Bénéfice"))),
  ("L'équivalent Python", "pexpect reprend les mêmes idées en Python ; quand le système distant offre une API ou un transfert non interactif (sftp avec clé, curl), on remplace l'automatisation d'écran par cette interface, plus fiable.", r"""import os, pexpect
c = pexpect.spawn("ftp serveur-historique.interne", timeout=20, encoding="utf-8")
c.expect("Name.*:"); c.sendline(os.environ["FTP_USER"])
c.expect("Password:"); c.sendline(os.environ["FTP_PASSWORD"])
i = c.expect(["ftp>", "Login failed", pexpect.TIMEOUT])
if i != 0: raise SystemExit(2)
c.sendline("get export_du_jour.csv"); c.expect("ftp>"); c.sendline("bye")""")],
 [("Un script Expect de nuit reste bloqué jusqu'au matin une fois par semaine. Cause probable ?", "Un expect sans branche timeout (ou un délai trop long) face à un message inattendu : on ajoute set timeout et une branche timeout avec sortie en erreur dans chaque expect, et l'on journalise l'étape atteinte."),
  ("Question d'entretien : quand utiliser Expect ?", "Pour automatiser un outil qui n'offre qu'une interface interactive, en dernier recours ; je privilégie une API ou une commande non interactive, et sinon j'écris un script Expect avec délais, gestion d'erreurs, journal et identifiants hors du code.")],
 ("Automatiser un outil interactif", ["Un service interactif simulé en conteneur (ftp ou programme qui pose des questions).", "Script Expect robuste : délais, branches d'erreur, journal sans mot de passe, codes retour.", "Même automatisation en pexpect, puis comparaison avec une solution non interactive."],
  "Attendu : le script ne reste jamais bloqué ; aucun mot de passe dans les journaux ni dans le dépôt ; la comparaison conclut sur la solution la plus fiable.")),
]

# ============================ PARTIE 7 : PYTHON, JAVA, JAVASCRIPT ============================
LANG = [
ch("Python pour le RUN : scripts, traitements, extractions", 'c',
 ["Python sert au RUN pour les scripts de traitement et d'extraction : lecture et écriture de CSV et JSON, appels aux bases (PostgreSQL, MongoDB), fichiers, journaux.", "Un script d'exploitation Python a des arguments (argparse), un journal (logging), des codes retour, des délais sur chaque appel réseau, et tourne dans un conteneur avec ses dépendances.", "Lire une trace d'erreur (traceback) de bas en haut donne la cause : la dernière ligne dit quoi, les lignes au-dessus disent où."],
 ["Écrire un script de traitement Python fiable", "Interroger PostgreSQL et MongoDB depuis Python", "Lire une trace d'erreur et corriger"],
 [("Un script de traitement", "", r"""#!/usr/bin/env python3
import argparse, csv, logging, sys
import psycopg, pymongo
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
a = argparse.ArgumentParser(); a.add_argument("--mois", required=True); a.add_argument("--sortie", required=True); x = a.parse_args()
with psycopg.connect(connect_timeout=10) as c, c.cursor() as cur:        # paramètres de connexion lus dans PGHOST, PGUSER…
    cur.execute("SELECT numero, statut FROM dossier WHERE to_char(cree_le, 'YYYY-MM') = %s", (x.mois,))
    dossiers = cur.fetchall()
pieces = pymongo.MongoClient(serverSelectionTimeoutMS=5000).appli.pieces
with open(x.sortie, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter=";"); w.writerow(["numero", "statut", "pieces"])
    for numero, statut in dossiers: w.writerow([numero, statut, pieces.count_documents({"numero": numero})])
logging.info("%d dossiers exportés", len(dossiers)); sys.exit(0 if dossiers else 4)
# docker run --rm -v "$PWD:/w" -w /w --env-file .env python:3.12-slim sh -c "pip install -q psycopg[binary] pymongo && python export.py --mois 2026-09 --sortie export.csv\""""),
  ("Lire une trace d'erreur", "", r"""Traceback (most recent call last):
  File "/w/export.py", line 12, in <module>
    for numero, statut in dossiers: w.writerow([numero, statut, pieces.count_documents({"numero": numero})])
  File ".../pymongo/collection.py", line …, in count_documents
pymongo.errors.ServerSelectionTimeoutError: mongo:27017: [Errno -2] Name or service not known
# lecture : dernière ligne = la cause (le nom « mongo » n'est pas résolu) ; au-dessus = où (ligne 12 du script)
# action : vérifier l'adresse de MongoDB dans la configuration et le réseau Docker"""),
  ("Bonnes pratiques", "Dépendances figées (requirements.txt), environnement isolé (conteneur ou virtualenv), pas de secret dans le code, tests (pytest) sur les fonctions de traitement, et le même script en test et en production.", None)],
 [("Un script Python s'arrête avec UnicodeDecodeError sur un fichier d'entrée. Que fais-tu ?", "Je vérifie l'encodage réel du fichier (file -i, ou échantillon), j'ouvre avec le bon encodage (encoding='latin-1' ou 'utf-8-sig'), et je traite les caractères invalides selon la règle convenue ; je documente l'encodage attendu avec le fournisseur du fichier."),
  ("Question d'entretien : Perl ou Python pour un nouveau script ?", "Pour du neuf, souvent Python (bibliothèques, compétences disponibles) ; si l'écosystème existant est en Perl avec des modules maison, rester en Perl peut être plus cohérent. Je décide sur la maintenance et l'équipe.")],
 ("Script Python de la mission", ["Script qui croise PostgreSQL et MongoDB et produit un CSV, lancé en conteneur.", "Journal, arguments, codes retour, délais sur les connexions.", "Deux tests pytest ; provoquer et lire trois traces d'erreur."],
  "Attendu : le script produit le même résultat à chaque exécution ; chaque trace d'erreur est expliquée ; les tests passent en conteneur.")),

ch("Java pour le RUN : lire, diagnostiquer, corriger", 'c',
 ["En RUN, Java se lit plus qu'il ne s'écrit : traces d'exception, journaux, configuration, et parfois une correction ciblée suivie d'une reconstruction.", "Une trace d'exception se lit par la cause la plus profonde (« Caused by » en bas) : c'est elle qui explique le problème.", "Les incidents Java courants : NullPointerException, OutOfMemoryError, ClassNotFoundException, délais de connexion, et la JVM se diagnostique avec jcmd."],
 ["Lire une trace d'exception Java", "Reconnaître les erreurs Java courantes et leur cause", "Reconstruire et vérifier une petite correction en conteneur"],
 [("Lire une trace", "", r"""ERROR [DossierService] Échec de l'export du dossier 2026-0042
org.springframework.dao.DataAccessResourceFailureException: impossible d'obtenir une connexion
    at … DossierService.exporter(DossierService.java:87)
    …
Caused by: java.sql.SQLTransientConnectionException: Connection is not available, request timed out after 30000ms
    at com.zaxxer.hikari.pool.HikariPool.createTimeoutException(HikariPool.java:…)
# lecture : la cause profonde (dernier « Caused by ») = pool de connexions épuisé ou base injoignable
# vérifier : état de la base, nombre de connexions, requêtes longues, autre traitement en cours"""),
  ("Les erreurs courantes", "", T([
    ("NullPointerException", "donnée absente non prévue", "ligne indiquée, donnée d'entrée en cause"),
    ("OutOfMemoryError", "volume trop gros, fuite mémoire", "taille du traitement, -Xmx, vidage mémoire"),
    ("ClassNotFoundException, NoSuchMethodError", "bibliothèque absente ou en mauvaise version", "contenu du paquet, dépendances"),
    ("Délai de connexion dépassé", "base ou service injoignable, pool épuisé", "réseau, pool, dépendance"),
    ("Erreur de format de date ou de nombre", "donnée inattendue", "valeur fautive dans le journal")], ("Erreur", "Cause fréquente", "Où chercher"))),
  ("Reconstruire et vérifier", "", r"""docker run --rm -v "$PWD:/app" -w /app -v m2:/root/.m2 maven:3.9-eclipse-temurin-17 mvn -q -DskipTests=false verify
jcmd $(pgrep -f appli.jar) VM.flags ; jcmd $(pgrep -f appli.jar) Thread.print > fils.txt     # réglages et fils d'exécution
java -jar appli.jar --version                                                               # version réellement déployée""")],
 [("Un traitement Java échoue avec OutOfMemoryError uniquement en fin de mois. Hypothèse ?", "Le volume de fin de mois dépasse la mémoire prévue (tout est chargé d'un coup) : court terme, augmenter la mémoire après mesure ; durable, traiter par lots dans le code, avec un test sur un volume de fin de mois."),
  ("Question d'entretien : comment lis-tu une trace d'exception ?", "Je descends jusqu'au dernier « Caused by », qui donne la cause réelle, puis je remonte vers la première ligne de notre code (notre paquet) pour savoir où elle s'est produite ; je relie ensuite à la donnée ou à l'événement du moment.")],
 ("Diagnostiquer une application Java", ["Application Java fournie en conteneur ; provoquer trois erreurs (donnée nulle, base arrêtée, mémoire insuffisante).", "Lire chaque trace, trouver la cause, proposer la correction.", "Corriger une erreur, reconstruire avec Maven en conteneur, vérifier."],
  "Attendu : chaque cause est trouvée à partir de la trace seule ; la correction est testée ; la version déployée est vérifiée.")),

ch("JavaScript pour le RUN : navigateur, Node.js, scripts", 'c',
 ["Côté navigateur, les outils de développement (console, réseau) montrent les erreurs JavaScript et les appels qui échouent : c'est le premier réflexe face à un écran qui ne répond pas.", "Côté serveur, Node.js exécute des scripts (utilitaires, petites API) avec npm pour les dépendances ; on lit package.json pour savoir comment lancer et quelles versions sont attendues.", "Les incidents courants : erreur JavaScript bloquante, appel d'API refusé (CORS, droits), cache du navigateur sur une ancienne version, version de Node incompatible."],
 ["Diagnostiquer un problème d'écran avec les outils du navigateur", "Lancer et lire un projet Node.js", "Écrire un petit script JavaScript de traitement"],
 [("Dans le navigateur", "", T([
    ("Console", "erreurs JavaScript (TypeError, ReferenceError), avertissements", "l'écran est blanc ou un bouton ne fait rien"),
    ("Réseau", "appels en échec (400, 401, 403, 500), temps de réponse", "données qui ne s'affichent pas"),
    ("En-têtes", "Cache-Control, CORS, cookies", "ancienne version affichée, appel refusé"),
    ("Application", "stockage local, cookies de session", "session incohérente")], ("Onglet", "Ce qu'on y voit", "Quand"))),
  ("Node.js", "", r"""cat package.json                           # scripts (start, test, build), dépendances, version de Node attendue (engines)
docker run --rm -v "$PWD:/app" -w /app node:22-slim sh -c "npm ci && npm test"
docker run --rm -v "$PWD:/app" -w /app node:22-slim node scripts/verifier_export.js /app/export.json
npm ls --depth=0 ; npm audit --omit=dev     # dépendances installées, vulnérabilités connues"""),
  ("Un petit script de vérification", "", r"""// scripts/verifier_export.js : vérifie qu'un export JSON est complet
const fs = require("fs");
const [, , chemin] = process.argv;
const donnees = JSON.parse(fs.readFileSync(chemin, "utf8"));
const sansNumero = donnees.filter(d => !d.numero);
console.log(`${donnees.length} dossiers, ${sansNumero.length} sans numéro`);
process.exit(sansNumero.length ? 1 : 0);""")],
 [("Un utilisateur voit une ancienne version de l'écran après la mise en production. Que vérifies-tu ?", "Le cache : rechargement forcé (Ctrl+F5), en-têtes de cache des fichiers JavaScript et CSS, noms de fichiers versionnés ; si seul cet utilisateur est concerné, c'est son cache, sinon la configuration du serveur ou du proxy."),
  ("Question d'entretien : que fais-tu face à un écran blanc ?", "J'ouvre la console du navigateur pour l'erreur JavaScript et l'onglet réseau pour les appels en échec ; selon ce que je vois, c'est le code de l'écran, une API qui répond mal, ou un fichier non chargé.")],
 ("JavaScript en RUN", ["Page web de test avec une erreur JavaScript et un appel d'API en échec : les diagnostiquer avec les outils du navigateur.", "Lancer un projet Node.js en conteneur, lire son package.json, exécuter ses tests.", "Écrire un script Node de vérification d'export JSON."],
  "Attendu : les deux problèmes sont expliqués avec la capture de la console et du réseau ; le projet Node tourne en conteneur ; le script renvoie un code non nul sur un export incomplet.")),
]

# ============================ PARTIE 8 : GIT ET DOCKER ============================
GITDOCKER = [
ch("git et Docker au quotidien du RUN", 'c',
 ["git sert à suivre ce qui a changé et à livrer proprement : branches, commits lisibles, demandes de fusion relues, étiquettes de version ; log, blame et bisect aident à trouver quand un problème est apparu.", "Docker fait tourner les outils et les applications de façon identique partout : images, conteneurs, volumes, réseau, Compose pour plusieurs services.", "Diagnostiquer un conteneur : état, journaux, entrée dans le conteneur, ressources, configuration injectée."],
 ["Utiliser git pour livrer et pour enquêter", "Faire tourner et diagnostiquer des conteneurs", "Combiner git et Docker pour un environnement de test reproductible"],
 [("git pour livrer et enquêter", "", r"""git switch -c correction/app-1234-export
git add export_mensuel.pl && git commit -m "APP-1234 : ajoute la date de clôture à l'export mensuel"
git push -u origin correction/app-1234-export        # puis demande de fusion relue
git log --oneline --since="2 weeks ago" -- export_mensuel.pl    # ce qui a changé sur ce fichier
git blame -L 40,60 export_mensuel.pl                             # qui a modifié ces lignes, et quand
git bisect start ; git bisect bad ; git bisect good v3.7        # trouver le commit qui a introduit le problème
git revert <commit>                                              # annuler proprement un changement déjà partagé
git tag -a v3.8 -m "version 3.8" && git push origin v3.8"""),
  ("Docker pour tester et diagnostiquer", "", r"""docker compose up -d ; docker compose ps               # services et état
docker compose logs --since 30m appli                   # journaux récents
docker compose exec appli sh                            # entrer dans le conteneur
docker stats --no-stream                                # processeur et mémoire par conteneur
docker inspect appli --format '{{json .Config.Env}}'    # configuration injectée (attention aux secrets)
docker compose down -v                                  # tout arrêter et supprimer les volumes de test"""),
  ("Un environnement de test reproductible", "Le dépôt contient un docker-compose.yml qui monte la base (PostgreSQL, MongoDB) avec des données fictives et les outils (Perl, TeX Live, Python) : toute l'équipe reproduit un incident ou teste une évolution dans le même environnement, en une commande.", None)],
 [("Un rapport est faux depuis une date inconnue. Comment trouves-tu le changement en cause ?", "Avec git bisect entre une version connue bonne et la version actuelle, en testant le rapport à chaque étape (automatiquement si possible) : git désigne le commit fautif en quelques essais."),
  ("Question d'entretien : à quoi te sert Docker en RUN ?", "À reproduire un incident dans un environnement identique, à faire tourner outils et bases de test sans rien installer, et à livrer des scripts avec leurs dépendances exactes ; en production, selon l'architecture du site.")],
 ("Environnement de la mission", ["docker-compose.yml avec PostgreSQL, MongoDB et les outils Perl, TeX Live, Python, chargés de données fictives.", "Branche, commit et demande de fusion pour une petite évolution ; étiquette de version.", "Retrouver avec git bisect le commit qui a cassé un rapport."],
  "Attendu : l'environnement démarre en une commande ; la demande de fusion est lisible ; bisect désigne le bon commit.")),
]

# ============================ PARTIE 9 : EXPLOITATION ET RECETTE ============================
EXPLOIT = [
ch("Bonnes pratiques de l'exploitation", 's',
 ["Une application bien exploitée est documentée (dossier d'exploitation, runbooks), surveillée (alertes utiles), sauvegardée (restaurations testées) et changée avec méthode (changements planifiés et tracés).", "Les traitements récurrents ont un propriétaire, un planning, des contrôles et une conduite à tenir en cas d'échec.", "On mesure pour s'améliorer : incidents par gravité, délai de rétablissement, demandes traitées dans les délais, changements réussis."],
 ["Appliquer les bonnes pratiques d'exploitation au quotidien", "Tenir le dossier d'exploitation et les runbooks", "Suivre des indicateurs utiles"],
 [("Les pratiques", "", CK("Une application bien exploitée", ["Dossier d'exploitation à jour : architecture, serveurs, flux, traitements, sauvegardes, contacts", "Runbook par incident courant : symptôme, vérifications, action sûre, escalade", "Supervision : alertes sur les symptômes utilisateurs et les traitements en échec, reliées au bon destinataire", "Journaux lisibles, conservés et exploités", "Sauvegardes vérifiées par des restaurations régulières", "Changements planifiés, testés, tracés, avec retour arrière", "Accès nominatifs, droits minimaux, secrets hors des scripts", "Traitements récurrents avec contrôles de volume et codes retour"])),
  ("Un runbook", "", "texte::Runbook : génération des courriers PDF en échec\nSymptôme : alerte « génération PDF : échecs > 0 » ou courriers absents à 8 h\nVérifications :\n  1. journal de génération : /var/log/appli/courriers_AAAAMMJJ.log (première erreur)\n  2. fichier .log de LaTeX du dossier en échec (ligne commençant par « ! »)\n  3. donnée du dossier en cause (caractère spécial, champ vide)\nAction sûre : écarter le dossier en cause (liste d'exclusion), relancer la génération des autres\nNe pas faire : modifier le modèle LaTeX en production\nEscalade : responsable de l'application ; prestataire si le modèle est en cause\nAprès : ticket avec la cause, correction de l'échappement par une évolution"),
  ("Les indicateurs", "", T([
    ("Incidents par gravité", "combien, lesquels reviennent", "problèmes à ouvrir"),
    ("Délai de rétablissement", "du signalement au service rétabli", "efficacité des runbooks"),
    ("Demandes dans les délais", "part des demandes traitées à temps", "charge et priorisation"),
    ("Changements réussis", "sans incident ni retour arrière", "qualité des mises en production")], ("Indicateur", "Ce qu'il mesure", "Ce qu'il déclenche")))],
 [("La même anomalie revient chaque mois en fin de traitement. Que proposes-tu ?", "D'ouvrir un problème : analyser la cause de fond (volume, donnée, calendrier), corriger durablement par une évolution, et en attendant écrire un runbook pour traiter l'incident vite et sans risque."),
  ("Question d'entretien : quelles sont pour toi les bonnes pratiques de l'exploitation ?", "Documenter (dossier d'exploitation, runbooks), surveiller ce qui compte pour les utilisateurs, sauvegarder et tester la restauration, changer avec méthode et traçabilité, sécuriser les accès, et mesurer pour s'améliorer.")],
 ("Mettre une application sous contrôle", ["Rédiger le dossier d'exploitation d'une application fictive (Perl, LaTeX, SQL, MongoDB).", "Écrire trois runbooks (génération PDF, extraction en échec, base lente).", "Définir quatre indicateurs et leur source."],
  "Attendu : une personne qui ne connaît pas l'application traite un incident courant avec le runbook seul ; les indicateurs sont calculables.")),

ch("Bonnes pratiques d'une recette technique", 's',
 ["La recette technique vérifie qu'une version fonctionne techniquement dans un environnement proche de la production : installation, performances, sécurité, exploitabilité, reprise, en plus du bon fonctionnement.", "Elle suit un plan : objectifs, périmètre, cas de test, jeux de données, environnements, critères d'entrée et de sortie ; les anomalies sont qualifiées par gravité.", "Elle se conclut par un procès-verbal : ce qui a été testé, les anomalies ouvertes et leur gravité, la décision (acceptée, acceptée avec réserves, refusée)."],
 ["Construire un plan de recette technique", "Exécuter les tests et qualifier les anomalies", "Rédiger le procès-verbal et la décision"],
 [("Le plan de recette", "", T([
    ("Installation", "mode opératoire joué tel quel, contrôles après installation", "installation sans intervention non prévue"),
    ("Non-régression", "fonctions existantes clés, rapports, extractions", "résultats identiques à la version précédente"),
    ("Nouvelles fonctions", "cas nominaux et cas limites", "conformes à la documentation"),
    ("Performances", "traitements lourds, volumes de fin de mois", "durées dans les limites convenues"),
    ("Exploitabilité", "journaux, supervision, codes retour, relance, sauvegarde", "exploitable par le runbook"),
    ("Retour arrière", "désinstallation ou retour à la version précédente", "retour possible et chronométré")], ("Volet", "Contenu", "Critère de succès"))),
  ("Qualifier les anomalies", "", T([
    ("Bloquante", "empêche la mise en production", "fonction majeure en échec, perte de données"),
    ("Majeure", "gêne importante, contournement difficile", "rapport faux sur un cas fréquent"),
    ("Mineure", "gêne limitée, contournement simple", "libellé erroné, mise en page"),
    ("Suggestion", "amélioration", "confort")], ("Gravité", "Définition", "Exemple"))),
  ("Le procès-verbal", "", "texte::Procès-verbal de recette technique — version 3.8\nPériode : du 8 au 12 septembre ; environnement : recette (identique à la production)\nTesté : installation (mode opératoire v3.8), 42 cas de non-régression, 6 cas nouveaux, traitement de fin de mois (volume réel), exploitabilité, retour arrière\nRésultats : 47 cas réussis, 1 échec (anomalie APP-1302, mineure : libellé de colonne)\nPerformances : traitement de fin de mois en 38 min (limite : 60 min)\nRetour arrière : testé, 12 min\nDécision : acceptée avec réserve (APP-1302 corrigée dans la version suivante)\nValidé par : gestionnaire d'application, référent métier, responsable de l'application")],
 [("La recette révèle une anomalie majeure la veille de la mise en production. Que fais-tu ?", "Je la qualifie précisément (impact, fréquence, contournement), je la présente au point de décision avec les options (corriger et reporter, livrer avec contournement documenté, retirer la fonction), et je fais décider par les bons responsables, par écrit."),
  ("Question d'entretien : que teste une recette technique que ne teste pas une recette fonctionnelle ?", "L'installation selon le mode opératoire, les performances sur des volumes réels, l'exploitabilité (journaux, supervision, relance, sauvegarde), la sécurité et le retour arrière : tout ce qui fait qu'une version tient en production, au-delà des fonctions.")],
 ("Recette technique d'une version", ["Plan de recette d'une version fictive (six volets, cas de test, jeux de données).", "Exécuter la recette dans l'environnement Docker de la mission et qualifier les anomalies trouvées.", "Rédiger le procès-verbal et la décision."],
  "Attendu : le plan couvre les six volets ; chaque anomalie a une gravité justifiée ; le procès-verbal permet de décider sans autre document.")),
]

# ============================ PARTIE 10 : ENTRETIEN ============================
BREF = lambda theme: ["Chaque question a une réponse modèle cachée : réponds à voix haute, puis compare.", f"Les réponses donnent la structure attendue ({theme}) ; remplace les exemples par les tiens, chiffrés.", "Une bonne réponse tient en une à deux minutes : le principe, un exemple réel, ce que tu ferais dans leur contexte."]
OBJ = ["Répondre avec assurance aux questions de ce thème", "Illustrer chaque réponse par un exemple vécu", "Relier la réponse au contexte de la mission"]
TP = lambda theme: (f"Répétition « {theme} »", ["Masquer les réponses et répondre à voix haute en moins de deux minutes.", "Relire le chapitre de cours des réponses hésitantes, puis recommencer.", "Écrire trois exemples personnels chiffrés pour ce thème."], "Attendu : réponses claires, structurées et illustrées ; trois exemples prêts.")
ENTRETIEN = [
ch("Entretien 1 — Le poste et la posture RUN", 'e', BREF("posture de gestionnaire d'application"), OBJ,
 [("Questions et réponses", QR([
   ("Présentez-vous.", "Deux minutes : mon expérience de gestionnaire d'application ou de développeur en RUN, le socle (Perl, SQL, Linux, scripts, et LaTeX si pratiqué), un exemple chiffré (incident résolu, extraction fiabilisée, mise en production coordonnée), et pourquoi cette mission."),
   ("Qu'est-ce que le RUN pour vous ?", "Faire fonctionner l'application au quotidien pour ses utilisateurs : demandes, incidents, extractions, maintenance, mises en production ; avec une priorité à la continuité de service et à la traçabilité."),
   ("Quelle différence entre une demande, un incident et un problème ?", "Une demande est un besoin standard ; un incident une interruption ou dégradation du service à rétablir vite ; un problème la cause d'incidents répétés, à analyser et corriger durablement."),
   ("Comment priorisez-vous votre travail ?", "Par impact et urgence : ce qui bloque le service d'abord, puis les échéances fortes ; je rends visibles les arbitrages et j'annonce des délais réalistes."),
   ("Comment qualifiez-vous un incident ?", "Symptôme exact, périmètre (qui, quoi), début, changements récents, impact métier ; cela donne la priorité et oriente le diagnostic."),
   ("Comment travaillez-vous avec les référents métier ?", "Je les tiens informés des changements et des dysfonctionnements par des messages clairs et réguliers, je fais valider les demandes et les recettes, et je traduis leurs besoins en actions techniques précises."),
   ("Comment travaillez-vous avec des prestataires ou des éditeurs ?", "Avec des tickets précis et documentés (preuves, journaux, reproduction), des points réguliers, et une vérification de leurs livrables (notes de version, modes opératoires) avant toute mise en production."),
   ("L'offre parle de curiosité et de recherche en autonomie : comment faites-vous ?", "Je lis la documentation et le code (grep, git log), je reproduis dans un environnement de test, je cherche dans les tickets passés, et je sollicite les bonnes personnes avec une question précise et ce que j'ai déjà vérifié."),
   ("Comment analysez-vous une documentation technique ?", "J'en extrais ce qui change, les prérequis, les impacts, le mode opératoire et les risques ; j'en tire les cas de recette et les messages aux référents."),
   ("Qu'avez-vous appris de vos cinq ans et plus en RUN ?", "La rigueur (tout tracer, tout tester en recette), la communication (prévenir tôt), et la valeur de l'automatisation (scripts et runbooks qui évitent les erreurs répétées) ; à illustrer par tes exemples."),
   ("Êtes-vous à l'aise avec des technologies anciennes ?", "Oui : Perl, TCL ou LaTeX ne me font pas peur ; je sais les lire, les fiabiliser et les documenter, et je sais aussi dire quand une modernisation se justifie."),
   ("Comment gérez-vous le stress d'un incident en production ?", "Par la méthode : qualifier, rétablir d'abord, communiquer régulièrement, puis analyser ; un runbook et un collègue en binôme valent mieux que la précipitation."),
  ]), None)],
 [("Question piège : « Le RUN n'est-il pas répétitif pour vous ? »", "Ce qui est répétitif s'automatise ; le reste, ce sont des incidents et des évolutions toujours différents, où la connaissance de l'application fait gagner des heures aux utilisateurs."),
  ("Termine en trente secondes : pourquoi vous ?", "Parce que je maîtrise le socle (Perl, SQL, Linux) et la méthode du RUN, que je sais communiquer avec les métiers, et que je fiabilise ce que je touche.")],
 TP("posture RUN")),

ch("Entretien 2 — Perl et LaTeX", 'e', BREF("Perl et LaTeX"), OBJ,
 [("Perl", QR([
   ("Pourquoi use strict et use warnings ?", "Pour attraper les erreurs tôt : variables non déclarées, fautes de frappe, usages douteux ; use v5.36 les active avec say et les signatures."),
   ("Qu'est-ce que le contexte en Perl ?", "Une même expression renvoie autre chose en contexte scalaire ou liste : un tableau vaut sa taille en scalaire, ses éléments en liste ; c'est une source classique de surprises."),
   ("Comment déboguez-vous un script Perl inconnu ?", "perltidy pour le lire, perl -c pour la syntaxe, exécution en test sur des entrées connues, traces (warn, Data::Dumper), et perl -d pour avancer pas à pas."),
   ("Comment évitez-vous l'injection SQL avec DBI ?", "Toujours des paramètres (prepare avec ?, puis execute avec les valeurs), jamais de concaténation ; RaiseError pour échouer sur erreur, transactions pour les écritures multiples."),
   ("Comment lancez-vous une commande système sans risque ?", "Avec la forme liste de system (arguments séparés, sans shell), en vérifiant le code de retour ; jamais de chaîne construite à partir de données externes."),
   ("Expression régulière gourmande ou non gourmande ?", ".* prend le plus possible, .*? le moins possible ; pour masquer une valeur, on vise précisément (\\S+ ou [^;]+)."),
   ("Que sont les références ?", "Des scalaires qui pointent vers un tableau, un hachage ou une fonction ; elles permettent les structures imbriquées (liste de hachages), qu'on parcourt avec -> ou la syntaxe postfixée."),
   ("Comment gérez-vous les modules CPAN ?", "Dans un cpanfile versionné, installés avec cpanm dans l'image Docker de l'application, pour avoir les mêmes versions partout."),
   ("Comment fiabilisez-vous un vieux script sans le réécrire ?", "Tests de caractérisation sur des entrées réelles, strict et warnings ajoutés, corrections des avertissements, Perl::Critic et Perl::Tidy, puis découpage en modules si besoin."),
   ("Quelles options de la ligne de commande utilisez-vous ?", "-n et -p pour boucler sur les lignes, -i pour modifier en place (avec sauvegarde), -l pour les fins de ligne, -a et -F pour découper en colonnes, -e pour le code."),
  ]), None),
  ("LaTeX", QR([
   ("Comment compilez-vous un document LaTeX ?", "Avec latexmk (qui enchaîne les passes, la bibliographie, l'index) et le moteur adapté (LuaLaTeX pour l'Unicode et les polices), dans une image TeX Live en conteneur pour que ce soit reproductible."),
   ("La génération d'un PDF échoue : que regardez-vous ?", "Le fichier .log : la première ligne commençant par « ! » donne l'erreur et la ligne du source ; souvent un caractère spécial non échappé dans une donnée, un paquet manquant ou une accolade non fermée."),
   ("Quels caractères faut-il échapper ?", "# $ % & ~ _ ^ \\ { } : toute donnée insérée dans un modèle passe par une fonction d'échappement unique."),
   ("Comment générez-vous des documents à partir de données ?", "Un modèle .tex (Jinja2 en Python ou Template Toolkit en Perl) rempli avec des valeurs échappées, compilé en conteneur isolé, contrôlé (nombre de pages, texte attendu), avec un journal qui relie chaque PDF à ses données."),
   ("Qu'est-ce que l'injection LaTeX ?", "Une donnée contenant une commande (\\input d'un fichier, \\write18 pour exécuter) interprétée par LaTeX ; on échappe les données, on compile sans shell-escape et avec des lectures et écritures restreintes (openin_any et openout_any à p)."),
   ("Comment modifiez-vous la mise en page de tous les documents ?", "Dans la classe ou le paquet d'entreprise (marges, polices, en-têtes, couleurs), pas dans chaque document ; on compile tous les modèles en CI après chaque changement."),
   ("Tableau qui déborde sur plusieurs pages ?", "longtable (ou xltabular) au lieu d'un tableau flottant, avec l'en-tête répété par \\endhead."),
   ("PDF pour l'archivage ?", "PDF/A avec le paquet pdfx et des métadonnées ; et une compilation reproductible (image épinglée, date figée par SOURCE_DATE_EPOCH)."),
  ]), None)],
 [("Question piège : « Réécririez-vous les scripts Perl en Python ? »", "Pas par principe : je fiabilise d'abord (tests, strict, modules), et je ne réécris que sur des critères mesurés (maintenance, compétences, risques), script par script."),
  ("Explique en trente secondes à quoi sert LaTeX ici.", "À composer automatiquement des documents soignés (courriers, rapports) à partir des données de l'application, avec une mise en page commune et reproductible.")],
 TP("Perl et LaTeX")),

ch("Entretien 3 — Linux, SQL, MongoDB, Python, TCL, Java, JavaScript, git, Docker", 'e', BREF("socle technique"), OBJ,
 [("Questions et réponses", QR([
   ("Un serveur est lent : vos premières commandes ?", "uptime et top (charge, processus), free et vmstat (mémoire, attente disque), df -h et df -i (disques), iostat, puis les journaux du service ; en quelques minutes je sais où chercher."),
   ("Comment cherchez-vous une erreur dans des journaux ?", "grep avec contexte (-B, -A), zgrep sur les compressés, awk pour filtrer une période ou une colonne, et tail -F pour suivre en direct."),
   ("Quelles commandes GNU utilisez-vous le plus ?", "grep, sed, awk, find, sort, uniq, cut, xargs, tar, gzip, rsync, curl, ssh, et les outils de diagnostic (ps, top, df, du, ss, lsof)."),
   ("Qu'est-ce qu'un script shell robuste ?", "Mode strict (set -Eeuo pipefail), variables entre guillemets, options vérifiées, journal, codes retour documentés, mode essai à blanc pour ce qui supprime, et ShellCheck."),
   ("Une jointure SQL renvoie trop de lignes : pourquoi ?", "Une relation un-à-plusieurs multiplie les lignes ; je compte avant et après chaque jointure et j'agrège ou j'utilise EXISTS."),
   ("Comment modifiez-vous des données en production ?", "Sur demande validée, dans une transaction : compter, sauvegarder ce qui change, exécuter, vérifier, valider ; tout est tracé dans le ticket."),
   ("MongoDB : comment savez-vous si une requête utilise un index ?", "explain(\"executionStats\") : IXSCAN signifie un index, COLLSCAN un parcours complet de la collection."),
   ("MongoDB : à quoi sert le pipeline d'agrégation ?", "À calculer en étapes ($match pour filtrer, $group pour regrouper, $project pour façonner, $unwind pour éclater les tableaux, $lookup pour joindre)."),
   ("Comment sauvegardez-vous MongoDB ?", "mongodump et mongorestore (ou les sauvegardes de l'infrastructure), avec des restaurations de test régulières pour prouver que la sauvegarde est bonne."),
   ("Python : comment lisez-vous une trace d'erreur ?", "De bas en haut : la dernière ligne donne la cause, les lignes au-dessus disent où ; je remonte jusqu'à la première ligne de notre code."),
   ("TCL : quelles sont les règles de substitution ?", "$ pour une variable, [ ] pour le résultat d'une commande, { } pour empêcher toute substitution, \" \" pour la permettre ; et expr toujours entre accolades."),
   ("À quoi sert Expect ?", "À automatiser un programme interactif (spawn, expect, send), avec délais et branches d'erreur ; en dernier recours, quand aucune interface non interactive n'existe."),
   ("Java : comment lisez-vous une trace d'exception ?", "Je descends au dernier « Caused by » pour la cause, puis je remonte à la première ligne de notre code pour l'endroit ; je relie à la donnée du moment."),
   ("JavaScript : un écran ne répond pas, que faites-vous ?", "Console du navigateur pour l'erreur JavaScript, onglet réseau pour les appels en échec (codes, temps), puis je vérifie le cache si une ancienne version s'affiche."),
   ("git : comment trouvez-vous quand un bug est apparu ?", "git log sur le fichier, git blame sur les lignes, et git bisect entre une version bonne et la version actuelle."),
   ("git : comment annulez-vous un changement déjà partagé ?", "Avec git revert, qui crée un commit inverse, plutôt qu'une réécriture de l'historique partagé."),
   ("Docker : comment diagnostiquez-vous un conteneur ?", "docker compose ps, logs, exec pour entrer, stats pour les ressources, inspect pour la configuration."),
   ("Pourquoi Docker pour vos tests ?", "Pour reproduire un incident dans un environnement identique, sans rien installer, et partager le même environnement avec l'équipe."),
  ]), None)],
 [("Question piège : « Vous n'avez jamais fait de TCL en production. »", "C'est vrai (si c'est le cas), mais ses règles tiennent en quelques lignes ; je l'ai pratiqué en conteneur, et je sais lire, tester et documenter un script avant de le modifier."),
  ("Explique en trente secondes la différence entre SQL et MongoDB.", "SQL : tables, schéma, jointures ; MongoDB : documents souples, souvent imbriqués, lus d'un bloc ; chacun se modélise selon ses accès.")],
 TP("socle technique")),

ch("Entretien 4 — Incidents, mises en production, exploitation, recette", 'e', BREF("mises en situation"), OBJ,
 [("Mises en situation", QR([
   ("Les courriers PDF ne sont pas partis ce matin. Déroulez.", "Qualifier (tous ou certains, depuis quand), journal de génération et .log de LaTeX, donnée en cause, contournement (écarter le dossier, relancer les autres), message aux référents, correction durable par une évolution (échappement), ticket clos avec la cause."),
   ("Une extraction mensuelle est fausse. Comment le détectez-vous et le corrigez-vous ?", "Contrôles de volume par rapport au mois précédent, vérification des jointures et des bornes de dates, comparaison avec une source de référence ; correction dans le script versionné, relance, message aux destinataires."),
   ("Vous coordonnez une mise en production avec un prestataire et l'infrastructure : comment ?", "Planning partagé, rôles, livrables vérifiés, recette validée, point de décision avec critères, retour arrière prêt, contrôles après installation et messages aux référents."),
   ("La mise en production échoue à mi-parcours.", "J'applique le critère de retour arrière prévu, je rétablis la version précédente, j'informe les référents, puis j'analyse la cause avec les acteurs avant de replanifier."),
   ("Un référent signale un dysfonctionnement non reproductible.", "Je recueille des précisions (heure, utilisateur, données, capture), je cherche dans les journaux autour de l'heure, je tente de reproduire avec les mêmes données ; je le tiens informé même si la cause n'est pas encore trouvée."),
   ("On vous demande une modification directe en base « pour aller vite ».", "Je la fais tracer et valider, je l'exécute en transaction avec sauvegarde de ce qui change, et je propose ensuite une correction durable pour éviter de recommencer."),
   ("Quelles sont vos bonnes pratiques d'exploitation ?", "Dossier d'exploitation et runbooks à jour, supervision utile, sauvegardes testées, changements tracés, accès maîtrisés, indicateurs suivis."),
   ("Que contient une recette technique ?", "Installation selon le mode opératoire, non-régression, nouvelles fonctions, performances sur volumes réels, exploitabilité (journaux, relance, sauvegarde), retour arrière, et un procès-verbal avec décision."),
   ("Comment qualifiez-vous une anomalie de recette ?", "Bloquante, majeure, mineure ou suggestion, selon l'impact et l'existence d'un contournement ; la gravité conditionne la décision de mise en production."),
   ("Un incident revient chaque mois. Que faites-vous ?", "J'ouvre un problème, j'analyse la cause de fond, je propose une correction durable, et j'écris un runbook en attendant."),
   ("Comment documentez-vous ce que vous faites ?", "Tickets complets (analyse, actions, résultat), dossier d'exploitation et runbooks mis à jour après chaque incident ou changement, fiches des scripts et extractions."),
  ]), None),
  ("Questions à poser en fin d'entretien", QR([
   ("Quels sont les traitements et documents générés (Perl, LaTeX) les plus critiques ?", "Tu identifies le cœur de l'activité et tu te projettes."),
   ("Comment sont organisés les tickets, les mises en production et la recette ?", "Tu évalues la maturité des processus et ta marge d'amélioration."),
   ("Quels sont les incidents récurrents aujourd'hui ?", "Tu relies ton expérience à leurs problèmes concrets."),
   ("Qui sont les acteurs avec qui je travaillerai (référents, prestataires, infrastructure) ?", "Tu prépares ton intégration et tu montres ton sens de la coordination."),
  ]), None)],
 [("Question piège : « Qu'est-ce qui pourrait vous faire échouer ? »", "Vouloir tout changer sans connaître l'existant : je commence par comprendre, documenter et fiabiliser."),
  ("Termine en trente secondes.", "Je résume leurs enjeux tels que je les ai compris, en quoi mon expérience y répond, et je dis mon intérêt, avant de demander les prochaines étapes.")],
 TP("mises en situation")),
]

# ============================ ASSEMBLAGE ============================
PERL = charger('perl_pages.py', 'PL'); LATEX = charger('latex_pages.py', 'LX')
UNIXC = charger('mission_tech.py', 'UNIX'); UNIXC = [UNIXC[0], UNIXC[1], UNIXC[2], UNIXC[3], UNIXC[5]]   # sans PowerShell
PL_ = lambda *ks: ' <strong>Pour aller plus loin</strong> : ' + ', '.join(ks) + '.'
def partie(lst, n, titre, resume): lst[0]['partie'] = (n, titre, resume); return lst
P = []
P += partie(RUN, 1, "La mission : gestionnaire d'application en RUN", "Le poste et ses activités, les demandes et évolutions, le diagnostic des incidents, les extractions et petits développements, la coordination des mises en production, la documentation et la communication aux référents." + PL_(A('devops-08-sre-et-architecture.html', 'DevOps niveau 8 (incidents)'), A('cours-92-savoir-etre-situations-et-attitudes.html', 'Savoir-être : situations')))
P += partie(PERL, 2, "Perl — de zéro à expert (cours complet)", "Compétence principale. Les dix chapitres du cours Perl : ligne de commande, contextes, expressions régulières, fichiers et système sans injection, références, modules et CPAN, Moo, tests, DBI, reprise d'un script legacy." + PL_(A('cours-71-perl.html', 'cours Perl avec ses fiches visuelles')))
P += partie(LATEX, 3, "LaTeX — de zéro à expert (cours complet)", "Compétence souhaitée. Les neuf chapitres du cours LaTeX : compilation en conteneur, typographie, mise en page, tableaux et graphiques, classe d'entreprise, génération sûre à partir de données, diagnostic et PDF/A." + PL_(A('cours-75-latex.html', 'cours LaTeX avec ses fiches visuelles')))
P += partie(UNIXC, 4, "Linux, shell et commandes GNU", "Connaissance de base exigée. Système de fichiers, droits et processus, Bash complet, traitement de texte et de journaux (grep, sed, awk, jq), diagnostic d'un serveur, qualité et sécurité des scripts." + PL_(A('devops-00-fondations.html', 'DevOps niveau 0'), A('devops-10-aide-memoire.html', 'aide-mémoire'), A('cours-81-mission-tech-lead-java-mco-mcs.html', 'page Mission Tech Lead (PowerShell)')))
P += partie(DATA, 5, "SQL et MongoDB", "Extractions et diagnostic en SQL, requêtes et agrégations MongoDB, exploitation de MongoDB (réplicas, sauvegardes, supervision, incidents)." + PL_(A('cours-61-data-platform-aws-talend.html', 'Data Platform'), A('devops-08-sre-et-architecture.html', 'DevOps niveau 8 (bases en production)')))
P += partie(TCL, 6, "TCL et Expect", "Lire, corriger et maintenir des scripts TCL ; automatiser des outils interactifs avec Expect, et son équivalent Python pexpect.")
P += partie(LANG, 7, "Python, Java et JavaScript", "Le niveau utile en RUN : scripts de traitement Python, lecture et diagnostic d'une application Java, outils du navigateur et Node.js pour JavaScript." + PL_(A('cours-31-ia-agentique.html', 'IA agentique (Python)'), A('cours-13-java-pki-signature-electronique.html', 'Java PKI'), A('cours-01-react.html', 'React'), A('cours-02-angular.html', 'Angular'), A('cours-03-vue.html', 'Vue')))
P += partie(GITDOCKER, 8, "git et Docker", "Livrer et enquêter avec git ; tester et diagnostiquer avec Docker ; un environnement de test reproductible pour la mission." + PL_(A('devops-00-fondations.html', 'DevOps niveau 0 (Git)'), A('devops-01-virtualisation-et-conteneurs.html', 'DevOps niveau 1 (Docker)')))
P += partie(EXPLOIT, 9, "Exploitation et recette technique", "Les bonnes pratiques de l'exploitation (dossier d'exploitation, runbooks, supervision, sauvegardes, changements, indicateurs) et d'une recette technique (plan, anomalies, procès-verbal)." + PL_(A('devops-06-observabilite.html', 'DevOps niveau 6 (supervision)'), A('devops-08-sre-et-architecture.html', 'DevOps niveau 8 (SRE)')))
P += partie(ENTRETIEN, 10, "Entretien : questions et réponses", "Soixante-trois questions avec réponses modèles : le poste et la posture RUN, Perl et LaTeX, le socle technique, les mises en situation et les questions à poser. Clique sur une question pour voir la réponse." + PL_(A('devops-11-fiches-entretien.html', 'Fiches entretien'), A('cours-92-savoir-etre-situations-et-attitudes.html', 'Savoir-être : situations')))

d = sys.argv[1]
page('cours-82-mission-gestionnaire-application-perl-latex.html', "Préparer une mission de gestionnaire d'application (RUN) Perl et LaTeX",
     "Une page complète pour préparer une mission longue de gestionnaire d'application en RUN, avec Perl comme compétence principale et LaTeX pour la composition de documents : la mission (demandes, incidents, extractions, mises en production, communication), les cours complets Perl et LaTeX, Linux et le shell, SQL et MongoDB, TCL et Expect, Python, Java et JavaScript au niveau utile, git et Docker, l'exploitation et la recette technique, et une banque de questions-réponses pour l'entretien. Tout tourne en conteneur ; chaque chapitre a ses exercices corrigés et un travail pratique.",
     "≈ 110 h de travail · profil recherché : plus de cinq ans d'expérience en RUN.", P,
     [('cours-71-perl.html', 'Perl'), ('cours-75-latex.html', 'LaTeX'), ('cours-81-mission-tech-lead-java-mco-mcs.html', 'Mission Tech Lead Java')])
