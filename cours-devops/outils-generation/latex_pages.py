"""Cours LaTeX de zéro à expert (9 chapitres), orienté génération et composition de documents.
Usage : python3 latex_pages.py <dossier>"""
import sys, runpy, pathlib
g = runpy.run_path(pathlib.Path(__file__).with_name('front_gen.py'), run_name='front'); ch, page = g['ch'], g['page']
def T(rows, head): return '<div class="tablewrap"><table><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table></div>'
DK = "Tout en conteneur : <code>alias latexmk='docker run --rm -v \"$PWD:/doc\" -w /doc texlive/texlive:latest latexmk'</code> ; aucune distribution TeX installée sur le poste."

LX = [
ch("Démarrer : TeX, LaTeX, moteurs et premier document", 'j',
 ["LaTeX décrit la structure d'un document (titres, paragraphes, tableaux) et laisse le moteur composer la mise en page : le résultat est régulier, typographiquement soigné et reproductible.", "Trois moteurs : pdfLaTeX (historique), XeLaTeX et LuaLaTeX (Unicode et polices système) ; LuaLaTeX est le choix par défaut pour un document moderne.", "latexmk relance la compilation autant de fois que nécessaire (références, table des matières, bibliographie) : c'est la commande à utiliser, en conteneur."],
 ["Choisir un moteur et compiler en conteneur", "Écrire un premier document structuré", "Comprendre le cycle de compilation"],
 [("Un premier document", DK, r"""% rapport.tex
\documentclass[11pt,a4paper]{article}
\usepackage[french]{babel}          % césure, guillemets, espaces fines à la française
\usepackage{fontspec}                % polices Unicode (LuaLaTeX ou XeLaTeX)
\setmainfont{TeX Gyre Pagella}
\title{Rapport d'incidents de la semaine}
\author{Cellule de crise}
\date{\today}
\begin{document}
\maketitle
\tableofcontents
\section{Synthèse}
Cette semaine, \textbf{42 incidents} ont été déclarés, dont 3 de gravité P1.
\section{Détail par zone}
\end{document}
% docker run --rm -v "$PWD:/doc" -w /doc texlive/texlive:latest latexmk -lualatex rapport.tex"""),
  ("Les moteurs", "", T([
    ("pdfLaTeX", "historique, rapide, très compatible", "polices limitées, Unicode partiel"),
    ("XeLaTeX", "Unicode, polices système", "un peu plus lent"),
    ("LuaLaTeX", "Unicode, polices système, programmable en Lua", "choix par défaut pour un nouveau document")], ("Moteur", "Points forts", "À retenir"))),
  ("Le cycle de compilation", "Une première passe écrit les références dans des fichiers auxiliaires (.aux, .toc) ; une seconde les utilise ; la bibliographie ajoute un passage par biber. latexmk détecte ce qui a changé et enchaîne les passes ; latexmk -c nettoie les fichiers auxiliaires.", None)],
 [("La table des matières reste vide après une compilation. Pourquoi ?", "Elle est construite à partir du fichier .toc écrit lors de la passe précédente : il faut compiler deux fois, ce que latexmk fait automatiquement."),
  ("Question d'entretien : pourquoi LaTeX plutôt qu'un traitement de texte pour générer des documents ?", "Parce que le document est du texte : il se génère, se versionne dans Git, se compile de façon reproductible en conteneur, et la mise en page est cohérente d'un document à l'autre, même avec des centaines de rapports générés.")],
 ("Premier rapport compilé en conteneur", ["Écrire rapport.tex (titre, table des matières, deux sections) avec babel en français et une police Unicode.", "Compiler avec latexmk et LuaLaTeX dans l'image texlive, puis nettoyer.", "Comparer la sortie avec pdfLaTeX pour la même source."],
  "Attendu : le PDF contient une table des matières à jour, des guillemets et espaces à la française ; la compilation fonctionne sur n'importe quel poste avec Docker, sans installation.")),

ch("Texte, structure et typographie française", 'j',
 ["La structure passe par des commandes sémantiques : sections, listes, emphase ; on décrit le rôle du texte, la présentation vient de la classe et des réglages.", "Le français demande babel (ou polyglossia) : césure, espaces avant les ponctuations doubles, guillemets ; csquotes gère les citations, siunitx les nombres et unités.", "Dix caractères sont spéciaux (# $ % & ~ _ ^ \\ { }) : ils s'échappent, ce qui devient crucial quand le texte vient de données."],
 ["Structurer un document avec des commandes sémantiques", "Composer correctement en français", "Échapper les caractères spéciaux"],
 [("Structure et listes", "", r"""\section{Incidents majeurs}
\subsection{Zone N1}
\begin{itemize}
  \item Fuite de gaz rue des Lilas : \emph{évacuation} de 40 personnes.
  \item Inondation du sous-sol de la mairie.
\end{itemize}
\begin{enumerate}
  \item Sécuriser le périmètre.
  \item Prévenir les riverains.
\end{enumerate}
\paragraph{À retenir.} Deux incidents P1 sur trois concernent la zone N1."""),
  ("Typographie française", "babel en français place les espaces fines avant ; : ! ?, césure en français et libelle les éléments (« Table des matières », « Figure »). csquotes produit les bons guillemets, siunitx espace correctement nombres et unités.", r"""\usepackage[french]{babel}
\usepackage{csquotes}                       % \enquote{…} → « … »
\usepackage[locale=FR]{siunitx}             % \num{12345.6} → 12 345,6 ; \SI{3,5}{\kilo\metre}
Le préfet a déclaré : \enquote{la situation est sous contrôle}.
Débit mesuré : \SI{12.5}{\cubic\metre\per\second} ; population : \num{48250} habitants."""),
  ("Les caractères spéciaux", "", T([
    ("#", "\\#", "paramètre de macro"), ("$", "\\$", "mode mathématique"), ("%", "\\%", "commentaire"), ("&amp;", "\\&amp;", "séparateur de colonne"),
    ("_", "\\_", "indice en mathématiques"), ("^", "\\textasciicircum{}", "exposant"), ("~", "\\textasciitilde{}", "espace insécable"),
    ("\\", "\\textbackslash{}", "début de commande"), ("{ }", "\\{ \\}", "groupe")], ("Caractère", "À écrire", "Rôle en LaTeX")))],
 [("Un nom de fichier « rapport_final_2026.pdf » cité dans le texte provoque une erreur « Missing $ inserted ». Pourquoi ?", "Le tiret bas est un caractère spécial (indice en mathématiques) : il faut l'échapper (\\_) ou utiliser \\texttt{} avec un paquet comme url ou \\detokenize. Tout texte venant de données doit être échappé systématiquement."),
  ("Question d'entretien : babel ou polyglossia ?", "Les deux gèrent les langues ; babel est le plus répandu et fonctionne avec tous les moteurs, y compris LuaLaTeX, et c'est aujourd'hui le choix recommandé ; polyglossia reste présent dans des documents XeLaTeX plus anciens.")],
 ("Compte rendu d'incident", ["Rédiger un compte rendu structuré (sections, listes, paragraphe de synthèse) en français correct.", "Nombres et unités avec siunitx, citations avec csquotes.", "Insérer un texte contenant les dix caractères spéciaux, correctement échappés."],
  "Attendu : compilation sans avertissement ; espaces fines et guillemets français corrects ; les caractères spéciaux s'affichent tels quels.")),

ch("Mise en page : classes, marges, en-têtes, page de titre", 'c',
 ["La classe fixe le type de document (article, report, book, ou les classes KOMA-Script plus modernes) ; les paquets ajustent le reste.", "geometry règle format et marges, fancyhdr ou scrlayer-scrpage les en-têtes et pieds de page, titlesec l'apparence des titres.", "Une page de titre et une mise en page d'entreprise se définissent une fois et servent à tous les documents (chapitre 7)."],
 ["Choisir une classe et régler format et marges", "Créer en-têtes et pieds de page", "Composer une page de titre"],
 [("Format, marges, en-têtes", "", r"""\documentclass[11pt,a4paper]{scrartcl}         % KOMA-Script, adapté au format européen
\usepackage[margin=2.2cm,top=2.8cm]{geometry}
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{CrisisShield — Rapport hebdomadaire}
\fancyhead[R]{\leftmark}
\fancyfoot[C]{Page \thepage}
\fancyfoot[R]{Diffusion restreinte}
\renewcommand{\headrulewidth}{0.4pt}"""),
  ("Titres et colonnes", "titlesec modifie l'apparence des titres de section ; multicol compose une partie en plusieurs colonnes ; \\newpage et \\clearpage contrôlent les sauts de page.", r"""\usepackage{titlesec}
\titleformat{\section}{\Large\bfseries\color{bleucrise}}{\thesection}{0.6em}{}
\usepackage{multicol}
\begin{multicols}{2}
  Synthèse courte composée sur deux colonnes…
\end{multicols}"""),
  ("Une page de titre", "", r"""\begin{titlepage}
  \centering
  \includegraphics[width=4cm]{logo-crisisshield}\par\vspace{2cm}
  {\Huge\bfseries Rapport d'incidents\par}\vspace{0.5cm}
  {\Large Semaine 39 — 2026\par}\vfill
  {\large Cellule de crise — préfecture N1\par}
  {\small Document généré automatiquement le \today\par}
\end{titlepage}""")],
 [("Les marges changent d'un rapport à l'autre parce que chaque rédacteur les ajuste. Que proposes-tu ?", "Une classe ou un paquet d'entreprise (chapitre 7) qui fixe geometry, en-têtes, polices et couleurs ; les documents ne contiennent plus que leur contenu, et la mise en page est identique partout."),
  ("Question d'entretien : article, report ou KOMA-Script ?", "article pour un document court, report ou book pour un document à chapitres ; les classes KOMA-Script (scrartcl, scrreprt) sont pensées pour le format européen et plus configurables, un bon choix pour des documents d'entreprise.")],
 ("Mise en page du rapport hebdomadaire", ["Classe scrartcl, marges, en-têtes et pieds de page avec mention de diffusion.", "Titres colorés avec titlesec, synthèse sur deux colonnes.", "Page de titre avec logo et date de génération."],
  "Attendu : en-têtes présents sur toutes les pages sauf la page de titre ; marges identiques à la charte ; le document tient sur la mise en page prévue.")),

ch("Tableaux, figures et références croisées", 'c',
 ["Les tableaux lisibles suivent booktabs (trois filets, pas de lignes verticales) ; tabularx ajuste la largeur, longtable coupe un tableau sur plusieurs pages.", "Figures et tableaux sont des flottants : LaTeX choisit leur place ; on leur donne une légende et une étiquette, et on y renvoie par \\ref ou \\cref.", "graphicx insère les images (PDF, PNG) ; subcaption regroupe plusieurs images sous une légende."],
 ["Composer des tableaux lisibles, y compris longs", "Placer figures et images avec légendes", "Faire des renvois automatiques"],
 [("Un tableau lisible", "", r"""\usepackage{booktabs,tabularx,longtable}
\begin{table}[htbp]
  \centering
  \caption{Incidents par zone et par gravité}\label{tab:zones}
  \begin{tabularx}{\linewidth}{X r r r}
    \toprule
    Zone & P1 & P2 & P3 \\
    \midrule
    N1 & 2 & 5 & 11 \\
    S3 & 1 & 3 & 20 \\
    \bottomrule
  \end{tabularx}
\end{table}
% tableau de plusieurs pages : longtable, avec \endhead pour répéter l'en-tête"""),
  ("Figures et images", "", r"""\usepackage{graphicx,subcaption}
\begin{figure}[htbp]
  \centering
  \begin{subfigure}{0.48\linewidth}\includegraphics[width=\linewidth]{carte-n1.pdf}\caption{Zone N1}\end{subfigure}\hfill
  \begin{subfigure}{0.48\linewidth}\includegraphics[width=\linewidth]{carte-s3.pdf}\caption{Zone S3}\end{subfigure}
  \caption{Localisation des incidents}\label{fig:cartes}
\end{figure}"""),
  ("Renvois automatiques", "\\label pose une étiquette, \\ref et \\pageref renvoient au numéro et à la page ; cleveref ajoute le mot (« tableau 2 », « figure 3 ») ; hyperref rend tous les renvois cliquables dans le PDF.", r"""\usepackage{hyperref}
\usepackage[french,noabbrev]{cleveref}
Comme le montre le \cref{tab:zones}, la zone S3 concentre les incidents P3 (voir aussi la \cref{fig:cartes}).""")],
 [("Un tableau de 300 lignes déborde en bas de page et disparaît. Que faire ?", "Un environnement table ne se coupe pas : on utilise longtable (ou xltabular pour la largeur automatique), qui coupe sur plusieurs pages et répète l'en-tête avec \\endhead."),
  ("Question d'entretien : pourquoi une figure n'apparaît-elle pas là où je l'ai placée ?", "Parce que c'est un flottant : LaTeX la place selon les options (h, t, b, p) et la place disponible. On donne des options souples (htbp), on renvoie par \\cref au lieu de « ci-dessous », et on évite de forcer avec H sauf nécessité.")],
 ("Tableaux et figures du rapport", ["Tableau des incidents par zone avec booktabs et tabularx.", "Liste complète des incidents en longtable, en-tête répété.", "Figure avec deux sous-figures, renvois par cleveref, liens hyperref."],
  "Attendu : aucun débordement de page ; tous les renvois résolus (aucun « ?? ») ; en-tête répété sur chaque page du tableau long.")),

ch("Mathématiques, code et schémas", 'c',
 ["amsmath est la référence pour les formules : alignements, équations numérotées, matrices.", "listings compose du code source avec coloration ; minted colore mieux mais exige l'exécution de commandes externes, à éviter dans une chaîne de génération automatique.", "TikZ dessine des schémas et pgfplots des graphiques à partir de données : tout reste en texte, versionnable et reproductible."],
 ["Écrire des formules correctement", "Composer du code source lisible", "Dessiner des schémas et des graphiques à partir de données"],
 [("Formules", "", r"""\usepackage{amsmath}
Le taux de disponibilité vaut
\begin{equation}\label{eq:dispo}
  D = 1 - \frac{t_{\text{indisponible}}}{t_{\text{total}}}
\end{equation}
\begin{align}
  \text{budget d'erreur} &= (1 - 0{,}999) \times 30 \times 24 \times 60 \\
                         &\approx 43{,}2~\text{minutes par mois}
\end{align}"""),
  ("Code source", "", r"""\usepackage{listings,xcolor}
\lstset{basicstyle=\ttfamily\small, keywordstyle=\color{blue}\bfseries, commentstyle=\color{gray},
        breaklines=true, frame=single, numbers=left, numberstyle=\tiny}
\begin{lstlisting}[language=Java, caption={Escalade d'un incident}]
public void escalader(int niveau) {
    if (statut != Statut.OUVERT) throw new IllegalStateException("incident clos");
    this.niveau = niveau;
}
\end{lstlisting}
% minted : plus joli, mais nécessite -shell-escape → à proscrire pour des données non maîtrisées"""),
  ("Schémas et graphiques", "", r"""\usepackage{tikz,pgfplots}
\pgfplotsset{compat=1.18}
\begin{tikzpicture}
  \begin{axis}[ybar, xlabel=Jour, ylabel=Incidents, symbolic x coords={lun,mar,mer,jeu,ven}, xtick=data, width=10cm, height=5cm]
    \addplot table[x=jour, y=nb, col sep=semicolon] {incidents-par-jour.csv};
  \end{axis}
\end{tikzpicture}
% le graphique est recalculé à chaque compilation à partir du CSV généré par l'extraction""")],
 [("Pourquoi éviter minted dans un générateur de rapports ?", "Parce qu'il exige l'option -shell-escape, qui autorise le document à exécuter des commandes système : avec du contenu venant de données, c'est une porte d'entrée. listings n'exécute rien et suffit pour la plupart des besoins."),
  ("Question d'entretien : comment mets-tu un graphique à jour chaque semaine sans le redessiner ?", "Le graphique est décrit avec pgfplots et lit ses données dans un CSV produit par l'extraction ; chaque compilation redessine le graphique à partir des nouvelles données, sans intervention.")],
 ("Indicateurs du rapport", ["Formule de disponibilité et calcul du budget d'erreur avec amsmath.", "Extrait de code Java avec listings.", "Graphique pgfplots des incidents par jour, lu dans un CSV."],
  "Attendu : formules numérotées et renvoyées par \\cref ; le graphique change quand le CSV change ; aucune compilation ne nécessite -shell-escape.")),

ch("Bibliographie, liens, index et glossaire", 's',
 ["biblatex avec biber gère la bibliographie à partir d'un fichier .bib : styles, tri, citations dans le texte.", "hyperref rend le PDF navigable : table des matières, renvois et URL cliquables, métadonnées du document.", "imakeidx produit un index, glossaries un glossaire et une liste des sigles, utiles pour les documents longs et techniques."],
 ["Gérer une bibliographie avec biblatex et biber", "Produire un PDF navigable avec métadonnées", "Ajouter index et glossaire des sigles"],
 [("Bibliographie", "", r"""% references.bib
@report{anssi-guide, author = {{ANSSI}}, title = {Guide d'hygiène informatique}, year = {2017}, institution = {ANSSI}}
@online{rgpd, title = {Règlement général sur la protection des données}, url = {https://eur-lex.europa.eu/eli/reg/2016/679/oj}, urldate = {2026-09-26}}
% document
\usepackage[backend=biber,style=authoryear]{biblatex}
\addbibresource{references.bib}
Les recommandations de l'\textcite{anssi-guide} s'appliquent\autocite{rgpd}.
\printbibliography[heading=bibintoc]"""),
  ("Un PDF navigable", "", r"""\usepackage[pdfusetitle,colorlinks=true,linkcolor=bleucrise,urlcolor=bleucrise]{hyperref}
\hypersetup{pdfauthor={Cellule de crise}, pdfsubject={Rapport hebdomadaire}, pdfkeywords={incidents, crise, semaine 39}}
\url{https://crisis.fr/tableau-de-bord}"""),
  ("Index et glossaire", "", r"""\usepackage{imakeidx}\makeindex
\usepackage[acronym,toc]{glossaries}\makeglossaries
\newacronym{rpo}{RPO}{objectif de point de reprise}
\newacronym{rto}{RTO}{objectif de temps de reprise}
Le \gls{rpo} visé est de 15 minutes\index{reprise}.
\printglossaries  \printindex
% latexmk sait lancer makeglossaries et makeindex si on lui déclare les règles (fichier latexmkrc)""")],
 [("La bibliographie reste vide alors que les citations sont dans le texte. Cause probable ?", "biber n'a pas été lancé (ou le fichier .bib n'est pas trouvé) : latexmk le lance automatiquement si biblatex est configuré avec backend=biber ; on lit le fichier .blg pour les erreurs de biber."),
  ("Question d'entretien : pourquoi renseigner les métadonnées du PDF ?", "Pour l'archivage, la recherche documentaire et l'accessibilité : titre, auteur, sujet et mots-clés sont lus par les outils de gestion documentaire, et exigés par certains formats d'archive comme PDF/A.")],
 ("Rapport de référence complet", ["Bibliographie biblatex de cinq sources (guides, règlements, articles).", "PDF navigable avec métadonnées et liens colorés à la charte.", "Glossaire de dix sigles et un index ; compilation complète par latexmk."],
  "Attendu : toutes les citations résolues, la bibliographie dans la table des matières ; les sigles développés à la première occurrence ; les métadonnées visibles dans les propriétés du PDF.")),

ch("Macros, environnements et classe d'entreprise", 's',
 ["Une macro nomme une intention (\\incident{P1}{…}) au lieu de répéter une mise en forme : on change la présentation à un seul endroit.", "\\NewDocumentCommand (désormais intégré au noyau LaTeX) déclare des commandes aux arguments optionnels et obligatoires lisibles ; \\NewDocumentEnvironment fait de même pour les environnements.", "Une classe (.cls) ou un paquet (.sty) d'entreprise regroupe polices, couleurs, marges, en-têtes et macros : les documents ne contiennent plus que le contenu."],
 ["Écrire des macros et environnements robustes", "Construire une classe d'entreprise", "Versionner et distribuer la charte LaTeX"],
 [("Macros et environnements", "", r"""\NewDocumentCommand{\incident}{O{P3} m m}{%   gravité optionnelle, zone et titre obligatoires
  \par\noindent\textbf{[#1]}~\textsc{#2} — #3\par}
\NewDocumentEnvironment{alerte}{O{Attention}}{%
  \begin{tcolorbox}[colback=red!5, colframe=red!60!black, title={#1}]}{\end{tcolorbox}}
\incident[P1]{N1}{Fuite de gaz rue des Lilas}
\begin{alerte}[Consigne]
  Ne jamais communiquer les données nominatives hors de la cellule.
\end{alerte}"""),
  ("Une classe d'entreprise", "", r"""% crisis-rapport.cls
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{crisis-rapport}[2026/09/26 v1.2 Rapports CrisisShield]
\DeclareOption{confidentiel}{\def\crisis@diffusion{Confidentiel}}
\def\crisis@diffusion{Diffusion restreinte}
\ProcessOptions\relax
\LoadClass[11pt,a4paper]{scrartcl}
\RequirePackage[french]{babel}\RequirePackage{fontspec}\RequirePackage{xcolor}
\RequirePackage[margin=2.2cm,top=2.8cm]{geometry}\RequirePackage{fancyhdr}\RequirePackage{booktabs}
\setmainfont{TeX Gyre Pagella}
\definecolor{bleucrise}{HTML}{2563EB}
\pagestyle{fancy}\fancyhf{}\fancyfoot[C]{\thepage}\fancyfoot[R]{\crisis@diffusion}
% document : \documentclass[confidentiel]{crisis-rapport}"""),
  ("Versionner et distribuer", "La classe vit dans un dépôt Git avec un numéro de version, des exemples et un test de compilation en CI ; l'image Docker de génération l'embarque (dans un répertoire TEXMFHOME), si bien que tous les documents compilent avec la même version.", None)],
 [("Vingt modèles de rapport copient le même préambule de 80 lignes, chacun légèrement modifié. Que proposes-tu ?", "Une classe d'entreprise versionnée qui contient ce préambule une fois, avec des options pour les variantes (confidentiel, interne) ; les modèles ne gardent que leur contenu, et la CI compile chaque modèle à chaque changement de la classe."),
  ("Question d'entretien : \\newcommand ou \\NewDocumentCommand ?", "\\newcommand suffit pour une macro simple à un argument optionnel au plus ; \\NewDocumentCommand gère plusieurs arguments optionnels, des étoiles, des délimiteurs, avec une syntaxe claire, et fait désormais partie du noyau LaTeX.")],
 ("Charte LaTeX de CrisisShield", ["Classe crisis-rapport.cls : polices, couleurs, marges, en-têtes, option confidentiel.", "Trois macros métier (incident, alerte, indicateur) avec arguments optionnels.", "Dépôt de la classe, exemple compilé en CI, image Docker qui l'embarque."],
  "Attendu : un rapport ne contient plus aucun réglage de mise en page ; changer la couleur dans la classe change tous les rapports ; la CI échoue si l'exemple ne compile plus.")),

ch("Générer des documents automatiquement", 's',
 ["Une chaîne de génération : extraire les données, remplir un modèle .tex (Jinja2 en Python, Template Toolkit en Perl), compiler en conteneur, publier le PDF.", "Toute donnée insérée dans le document est échappée : un caractère spécial casse la compilation, et une commande injectée (\\input, \\write18) peut lire des fichiers ou exécuter du code.", "La compilation automatique est isolée : sans exécution de commandes externes, fichiers accessibles restreints, délai maximal, conteneur sans réseau."],
 ["Construire une chaîne données, modèle, PDF", "Échapper les données et empêcher l'injection LaTeX", "Compiler de façon isolée et reproductible"],
 [("Un modèle Jinja2 pour LaTeX", "Les délimiteurs de Jinja2 sont changés pour ne pas entrer en conflit avec les accolades de LaTeX ; un filtre d'échappement s'applique à chaque valeur.", r"""# generer.py (dans un conteneur python:3.12-slim)
import jinja2, re
ECHAP = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
         '~': r'\textasciitilde{}', '^': r'\textasciicircum{}', '\\': r'\textbackslash{}'}
def tex(v): return re.sub(r'[&%$#_{}~^\\]', lambda m: ECHAP[m.group(0)], str(v))
env = jinja2.Environment(block_start_string='((*', block_end_string='*))', variable_start_string='(((',
                         variable_end_string=')))', comment_start_string='((#', comment_end_string='#))',
                         loader=jinja2.FileSystemLoader('modeles'), autoescape=False)
env.filters['tex'] = tex
open('sortie/rapport.tex', 'w').write(env.get_template('rapport.tex.j2').render(incidents=incidents, semaine=39))
# modele : ((* for i in incidents *)) \incident[((( i.gravite|tex )))]{((( i.zone|tex )))}{((( i.titre|tex )))} ((* endfor *))"""),
  ("Compiler de façon isolée", "", r"""# aucune commande externe, lecture et écriture limitées, pas de réseau, délai maximal
docker run --rm --network none --read-only --tmpfs /tmp \
  -v "$PWD/sortie:/doc" -w /doc -e openin_any=p -e openout_any=p \
  texlive/texlive:latest timeout 120 latexmk -lualatex -no-shell-escape -interaction=nonstopmode -halt-on-error rapport.tex
# openin_any=p / openout_any=p : interdit de lire ou d'écrire hors du répertoire de travail (mode « paranoïaque »)"""),
  ("La chaîne complète", "", T([
    ("Extraire", "requête SQL ou API, données validées", "Python ou Perl, en conteneur"),
    ("Remplir", "modèle .tex avec échappement de chaque valeur", "Jinja2, Template Toolkit"),
    ("Compiler", "latexmk isolé, délai, arrêt à la première erreur", "image texlive épinglée"),
    ("Contrôler", "PDF produit, nombre de pages, texte attendu", "pdfinfo, pdftotext"),
    ("Publier", "archive, envoi, dépôt documentaire", "S3, GED, e-mail"),
    ("Tracer", "données, version du modèle, date, empreinte du PDF", "journal de génération")], ("Étape", "Contenu", "Outils")))],
 [("Un titre d'incident saisi par un utilisateur contient \\input{/etc/passwd}. Que se passe-t-il sans précaution, et avec ta chaîne ?", "Sans échappement, LaTeX exécuterait la commande et insérerait le fichier dans le PDF. Avec la chaîne, la barre oblique inverse est échappée (le texte s'affiche tel quel), et même en cas d'oubli, openin_any=p et le conteneur isolé empêchent de lire hors du répertoire de travail."),
  ("Question d'entretien : comment industrialises-tu la génération de 5 000 attestations PDF par nuit ?", "Modèle LaTeX versionné, données extraites et validées, échappement systématique, compilation parallèle en conteneurs isolés (sans réseau, sans commandes externes, avec délai), contrôle de chaque PDF, et journal qui relie chaque document à ses données et à la version du modèle.")],
 ("Générateur de rapports hebdomadaires", ["Extraction des incidents (CSV ou base en conteneur), modèle Jinja2 avec échappement.", "Compilation isolée : --network none, -no-shell-escape, openin_any=p, délai, arrêt sur erreur.", "Contrôles du PDF et journal de génération ; tester un titre piégé."],
  "Attendu : le titre piégé s'affiche en texte, rien n'est lu hors du répertoire ; un PDF est produit par zone ; le journal relie chaque PDF à ses données et à la version du modèle.")),

ch("Diagnostic, qualité, archivage et entretien", 'e',
 ["Une erreur LaTeX se lit dans le fichier .log : la ligne commence par un point d'exclamation et indique la ligne du source ; les avertissements (Overfull hbox, références indéfinies) signalent les défauts de mise en page.", "La production exige des documents reproductibles (version de TeX Live épinglée, date figée), accessibles (PDF balisé) et archivables (PDF/A).", "En entretien, on parle d'une chaîne de génération réelle : volumes, fiabilité, sécurité, et temps gagné."],
 ["Diagnostiquer erreurs et avertissements", "Produire des PDF reproductibles, accessibles et archivables", "Répondre aux questions d'entretien sur LaTeX"],
 [("Lire les erreurs", "", T([
    ("! Undefined control sequence", "commande inconnue ou paquet manquant", "vérifier l'orthographe, charger le paquet"),
    ("! Missing $ inserted", "caractère mathématique hors du mode math (_ ^)", "échapper le caractère"),
    ("! LaTeX Error: File … not found", "fichier ou paquet absent", "chemin, image, paquet dans l'image Docker"),
    ("Overfull \\hbox", "ligne trop longue (mot non coupé, URL)", "\\url, césure, reformuler"),
    ("Reference … undefined", "étiquette absente ou compilation incomplète", "latexmk, vérifier \\label"),
    ("Runaway argument", "accolade non fermée", "équilibrer les accolades")], ("Message", "Cause fréquente", "Réponse"))),
  ("Reproductible, accessible, archivable", "L'image TeX Live est épinglée par version ; SOURCE_DATE_EPOCH fige la date pour obtenir le même PDF à chaque compilation ; le paquet pdfx produit du PDF/A pour l'archivage ; le balisage du PDF (projet de balisage de LaTeX, avec LuaLaTeX) améliore l'accessibilité.", r"""# PDF identique à chaque compilation
SOURCE_DATE_EPOCH=1790380800 FORCE_SOURCE_DATE=1 latexmk -lualatex rapport.tex
# PDF/A-2b pour l'archivage
\usepackage[a-2b]{pdfx}          % avec un fichier rapport.xmpdata (titre, auteur, langue)
# balisage pour l'accessibilité (récent, avec LuaLaTeX) : \DocumentMetadata{lang=fr-FR, pdfstandard=A-2b, testphase=phase-III}"""),
  ("Trente questions d'entretien", "", r"""1 LaTeX ? Décrire la structure, laisser composer. 2 Moteurs ? pdfLaTeX, XeLaTeX, LuaLaTeX. 3 latexmk ? Relancer les passes nécessaires. 4 Préambule ? Réglages avant \begin{document}. 5 babel ? Langue, césure, typographie. 6 Caractères spéciaux ? # $ % & ~ _ ^ \ { }. 7 csquotes ? Guillemets. 8 siunitx ? Nombres et unités. 9 Classe ? Type de document. 10 KOMA-Script ? Classes européennes configurables. 11 geometry ? Format et marges. 12 fancyhdr ? En-têtes et pieds. 13 booktabs ? Tableaux lisibles. 14 longtable ? Tableau sur plusieurs pages. 15 Flottant ? Placé par LaTeX. 16 \label et \cref ? Renvois automatiques. 17 hyperref ? PDF navigable. 18 amsmath ? Formules. 19 listings ou minted ? Sans ou avec exécution externe. 20 TikZ, pgfplots ? Schémas et graphiques en texte. 21 biblatex et biber ? Bibliographie. 22 glossaries ? Sigles et glossaire. 23 \NewDocumentCommand ? Macros aux arguments clairs. 24 Classe d'entreprise ? Charte en un seul endroit. 25 Génération ? Données, modèle, compilation. 26 Échappement ? Chaque valeur insérée. 27 Injection LaTeX ? \input, \write18 ; échapper, isoler. 28 Compilation isolée ? Sans réseau, sans shell-escape, openin_any=p, délai. 29 Reproductible ? Image épinglée, SOURCE_DATE_EPOCH. 30 Archivage ? PDF/A avec pdfx.""")],
 [("La génération de nuit produit un PDF de deux pages au lieu de trente, sans erreur apparente. Démarche ?", "Lire le .log : sans -halt-on-error, LaTeX a pu continuer après une erreur ; vérifier aussi les données (extraction vide ?). Correction durable : -halt-on-error, contrôle du nombre de pages et du texte attendu après compilation, alerte si le contrôle échoue."),
  ("Question d'entretien : raconte une chaîne de génération de documents que tu as mise en place.", "STAR : le besoin (volumes, délai), la chaîne (extraction, modèle, échappement, compilation isolée, contrôles), un incident et sa correction, le résultat chiffré (temps de production, taux d'échec, documents conformes à l'archivage).")],
 ("Projet final : la chaîne de rapports en production", ["Classe d'entreprise, modèle, générateur et compilation isolée, réunis dans un dépôt avec CI.", "PDF reproductibles (image épinglée, date figée), PDF/A, contrôles automatiques après compilation.", "Tableau de diagnostic des erreurs rencontrées ; trente questions répondues à voix haute."],
  "Attendu : deux compilations successives donnent un PDF identique au bit près ; le PDF/A passe un validateur ; une erreur dans les données arrête la chaîne avec un message clair.")),
]

d = sys.argv[1]
page('cours-75-latex.html', 'LaTeX — de zéro à expert', "Neuf chapitres pour composer et générer des documents avec LaTeX : moteurs et compilation en conteneur, structure et typographie française, mise en page et page de titre, tableaux, figures et renvois, formules, code et graphiques (TikZ, pgfplots), bibliographie, index et glossaire, macros et classe d'entreprise, génération automatique depuis des données (Jinja2, échappement, compilation isolée contre l'injection), diagnostic, PDF reproductibles et archivables (PDF/A). Tout tourne en conteneur ; chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 30 h de travail · prérequis : aucun ; utile avec les cours Perl et Python pour la génération.", LX, [('cours-71-perl.html', 'Perl'), ('devops-00-fondations.html', 'DevOps niveau 0')])
