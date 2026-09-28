"""Régénère la charte graphique (site-00-charte-graphique.html) avec tous les composants du site et des exemples vivants.
Usage : python3 charte_page.py <dossier du site>"""
import sys, re, base64, pathlib, html as H
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from manga_gabarit import strip3, CSS as MANGA_CSS
d = pathlib.Path(sys.argv[1]); p = d / 'site-00-charte-graphique.html'; s = p.read_text()
a = s.index('<header class="hero">'); b = s.index("<script>(function(){try{var t=localStorage")

def svg_img(w, h, fond, titre, sous):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="{fond}"/><rect x="24" y="24" width="{w-48}" height="{h//5}" rx="14" fill="#0B1220"/><text x="{w/2}" y="{24+h//10+10}" font-family="sans-serif" font-size="{max(18,w//16)}" font-weight="700" fill="#fff" text-anchor="middle">{titre}</text>' + ''.join(f'<rect x="40" y="{h//5+60+i*(h//9)}" width="{w-80}" height="{h//14}" rx="8" fill="#fff" opacity=".85"/>' for i in range(5)) + f'<text x="{w/2}" y="{h-30}" font-family="sans-serif" font-size="{max(14,w//26)}" fill="#0B1220" text-anchor="middle">{sous}</text></svg>'
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()

yaml = "\n".join(["# compose.yaml : exemple de 40 lignes (repli automatique au-delà de 34)", "name: crisisshield", "services:"] + sum([[f"  service{i}:", f"    image: registry.local/crisis/service{i}:1.4.{i}", "    restart: unless-stopped"] for i in range(1, 13)], []) + ["volumes:", "  pgdata: {}"])
longue = "docker run --rm -it --read-only --cap-drop ALL --security-opt no-new-privileges -e JAVA_OPTS=\"-XX:MaxRAMPercentage=75\" -p 8080:8080 crisisshield/api:1.4.2   # une ligne trop longue revient à la ligne en gardant son alignement"
demo = strip3("mgcharte", "le gabarit en trois cases", "Charte",
   dict(term=["case 1 : la situation", "  un geste réaliste", "  qui semble raisonnable"], bulle=["Ça me paraît", "une bonne idée."]),
   dict(term=["case 2 : la conséquence", "  chiffrée, concrète", "  souvent de nuit"], sfx="aïe"),
   "case 3 : la bonne pratique", ["trois ou quatre lignes", "des gestes vérifiables", "le Sensei et Kaï", "  la légende résume la leçon"],
   "Chaque planche suit le même gabarit : la situation, la conséquence, la bonne pratique ; la légende dit la leçon en une phrase.")

def tile(ic, t, d_, meta, check=True):
    return f'<div class="tile"><div class="tile-head"><span class="ic">{ic}</span><h3><a href="#accueil">{t}</a></h3></div><p>{d_}</p><div class="tile-foot"><span class="meta">{meta}</span>' + ('<label><input type="checkbox"> Terminé</label>' if check else '') + '</div></div>'

corps = f'''<header class="hero"><div class="in"><div class="level">Charte graphique · maquette de référence</div><h1>Une seule charte pour tout le site</h1>
<p class="lead">Chaque page (accueil, niveaux, cours, aide-mémoire, fiches, corrections) applique ces composants, ces couleurs et ces règles. Toute évolution se fait ici d'abord, puis se propage par <code>outils-generation/restyle.py</code>.</p>
<div class="meta"><span>Barre et menus groupés</span><span>Sommaire numéroté</span><span>Code façon IDE</span><span>Planches manga</span><span>Lecture rapide</span><span>Clair / sombre</span></div></div></header>
<div class="single">
<nav class="toc"><strong>Sommaire</strong><ol><li><a href="#structure">Structure d'une page</a></li><li><a href="#couleurs">Couleurs et typographie</a></li><li><a href="#chapitre">Composants d'un chapitre</a></li><li><a href="#code">Blocs de code</a></li><li><a href="#replier">Sections longues</a></li><li><a href="#images">Images et visionneuse</a></li><li><a href="#manga">Planches manga</a></li><li><a href="#accueil">Accueil et tuiles</a></li><li><a href="#regles">Règles</a></li></ol></nav>

<article id="structure"><div class="chaphead"><span class="chapnum">Charte</span><span class="badge lvl-junior">Structure</span></div><h2>Structure d'une page</h2>
<pre><code>BARRE (collante) : logo · Accueil · Parcours DevOps ▾ (4 phases) · Cours ▾ (4 groupes) · Aide-mémoire · Entretien · Lecture rapide · ◐
BANDEAU : pastille de contexte · titre · résumé (70 caractères de large) · une ligne de métadonnées
SOMMAIRE (collant, 270 px)        │ CONTENU : une carte par chapitre
  pastille numérotée par entrée   │   Chapitre N + niveau · titre · En 30 secondes · planche manga
  couleur selon le niveau         │   objectifs · sections · code · exercices · TP
  chapitre courant surligné       │
PIED DE PAGE : présentation · parcours · cours · réviser
Sous 900 px : menu hamburger, sommaire en tête sur deux colonnes, une seule colonne de contenu</code></pre>
<p>Le bandeau ne porte ni bouton ni rangées de pastilles : la navigation vit dans la barre, le thème dans le bouton ◐, la lecture rapide dans son bouton.</p></article>

<article id="couleurs"><div class="chaphead"><span class="chapnum">Charte</span><span class="badge lvl-confirme">Couleurs</span></div><h2>Couleurs et typographie</h2>
<div class="tablewrap"><table><tr><th>Jeton</th><th>Clair</th><th>Sombre</th><th>Usage</th></tr>
<tr><td><code>--hero</code> / <code>--hero-2</code></td><td>#0B1220 → #132A57</td><td>#070D1A → #0F2148</td><td>barre, bandeau, pied de page</td></tr>
<tr><td><code>--accent</code> / <code>--accent-ink</code></td><td>#2563EB / #1E40AF</td><td>#60A5FA / #93C5FD</td><td>liens, titres de section, sommaire, En 30 secondes</td></tr>
<tr><td><code>--bg</code> / <code>--paper</code></td><td>#F4F6FA / #FFFFFF</td><td>#0B1220 / #111A2E</td><td>fond de page / cartes</td></tr>
<tr><td>code</td><td colspan="2">fond #0D1117 · mots-clés #FF7B72 · chaînes #A5D6FF · commentaires #8B949E · fonctions #D2A8FF · types #FFA657 · nombres #79C0FF · annotations #F2CC60 · clés et invites #7EE787</td><td>thème IDE commun</td></tr>
<tr><td>rubriques de l'accueil</td><td colspan="2">commencer #0F766E · parcours #1D4ED8 · développement #7C3AED · cloud et données #0369A1 · savoir-être #C2410C · réviser #475569</td><td>filet et icône des tuiles</td></tr></table></div>
<p>Texte : <strong>Inter</strong> 16,5 px, interligne 1,65. Code : <strong>JetBrains Mono</strong>. Titres : h1 dans le bandeau, h2 de chapitre 1,65 rem, h3 1,15 rem avec filet gauche. Cartes arrondies à 12 px, blocs à 10 px, une seule ombre douce.</p></article>

<article id="chapitre"><div class="chaphead"><span class="chapnum">Chapitre 1</span><span class="badge lvl-senior">Composants</span></div><h2>Composants d'un chapitre</h2>
<div class="bref"><span class="tag">En 30 secondes</span><ol><li>Le bloc « En 30 secondes » ouvre chaque chapitre : trois phrases.</li><li>Juste dessous : la planche manga du chapitre.</li></ol></div>
<div class="objectifs"><strong>À la fin de ce chapitre, tu sauras</strong><ul><li>Reconnaître chaque composant</li><li>Les réutiliser sans en inventer d'autres</li></ul></div>
<div class="exo"><span class="tag">Exercice 1.1</span><p>Une question courte ; le corrigé est replié.</p><details><summary>Corrigé</summary><div class="sol">Réponse courte, puis explication.</div></details></div>
<div class="tp"><span class="tag">Travail pratique 1</span><ol><li>Étapes numérotées.</li><li>Livrable explicite.</li></ol><details><summary>Correction type</summary><div class="sol">Commandes et preuve attendue.</div></details></div>
<p><span class="badge lvl-junior">Junior</span> <span class="badge lvl-confirme">Confirmé</span> <span class="badge lvl-senior">Senior</span> <span class="badge lvl-expert">Expert</span> <span class="badge tag-coeur">Par cœur</span> <span class="badge tag-important">Important</span> <span class="badge tag-contexte">Bon à savoir</span></p></article>

<article id="code"><div class="chaphead"><span class="chapnum">Charte</span><span class="badge lvl-expert">Code</span></div><h2>Blocs de code</h2>
<p>Thème IDE, coloration automatique (bash, YAML, Dockerfile, Java, Kotlin, JS/TS, Python, SQL, HCL, HTML), bouton Copier. Une ligne trop longue revient à la ligne <em>en gardant son indentation</em> ; le bouton « ⇤ Une ligne » bascule vers le défilement.</p>
<pre><code>{H.escape(longue)}</code></pre>
<p>Au-delà de 34 lignes, le bloc est replié avec « Afficher les N lignes ».</p>
<pre><code>{H.escape(yaml)}</code></pre></article>

<article id="replier"><div class="chaphead"><span class="chapnum">Charte</span><span class="badge lvl-junior">Sections</span></div><h2>Sections longues</h2>
<p>Une section de plus de 700 mots découpée en sous-parties devient une suite de panneaux repliables : le premier ouvert, les autres affichent « afficher ». Un paragraphe ne dépasse pas 90 mots ; au-delà, il est coupé à la phrase la plus proche du milieu.</p>
<details class="sub" open><summary>Première sous-partie (ouverte)</summary><p>Le contenu reste dans la page : rien n'est supprimé, tout est à un clic.</p></details>
<details class="sub"><summary>Deuxième sous-partie</summary><p>Le mode <strong>Lecture rapide</strong> (bouton de la barre) va plus loin : il ne garde de chaque chapitre que le résumé, les objectifs, les titres et les schémas ; un clic sur un titre déplie le chapitre.</p></details></article>

<article id="images"><div class="chaphead"><span class="chapnum">Charte</span><span class="badge lvl-confirme">Images</span></div><h2>Images et visionneuse</h2>
<p>Toute image s'ouvre en plein écran (zoom ×2, nouvel onglet, Échap pour fermer). Une affiche en portrait est limitée à 680 px de haut dans la page. Une seule affiche par sujet dans le fil du cours ; les autres vont dans une galerie en fin de chapitre.</p>
<figure class="fig zoomable" id="charte-affiche"><img src="{svg_img(600, 850, '#DBEAFE', 'Affiche en portrait', 'limitée à 680 px, clic pour agrandir')}" alt="Exemple d'affiche en portrait" loading="lazy" decoding="async"><figcaption>Une affiche en portrait : visible en entier, lisible en grand.</figcaption></figure>
<div class="gallery" id="gal-charte"><strong>Fiches visuelles du chapitre — clique pour agrandir</strong><div class="g-items">
<figure class="fig zoomable"><img src="{svg_img(480, 360, '#DCFCE7', 'Fiche A', 'vignette de galerie')}" alt="Fiche A"><figcaption>Première fiche complémentaire.</figcaption></figure>
<figure class="fig zoomable"><img src="{svg_img(480, 360, '#FEF3C7', 'Fiche B', 'vignette de galerie')}" alt="Fiche B"><figcaption>Deuxième fiche complémentaire.</figcaption></figure>
<figure class="fig zoomable"><img src="{svg_img(480, 360, '#FCE7F3', 'Fiche C', 'vignette de galerie')}" alt="Fiche C"><figcaption>Troisième fiche complémentaire.</figcaption></figure></div></div></article>

<article id="manga"><div class="chaphead"><span class="chapnum">Charte</span><span class="badge lvl-senior">Manga</span></div><h2>Planches manga</h2>
<p>Une planche par chapitre, sous « En 30 secondes », sur le piège du chapitre. Personnages : Kaï (développeur), Mika (collègue), Sensei Ohno (mentor). Les textes sont bornés par le gabarit : 36 caractères par ligne de terminal, 19 par ligne de bulle, 38 par ligne d'encadré.</p>
{demo}</article>

<article id="accueil"><div class="chaphead"><span class="chapnum">Charte</span><span class="badge lvl-expert">Accueil</span></div><h2>Accueil et tuiles</h2>
<p>L'accueil est fait de rubriques identiques : titre, une phrase, sous-groupes étiquetés, puis des tuiles de même format, trois par ligne, une couleur par rubrique. Toute la tuile est cliquable ; la case « Terminé » alimente la progression du sommaire.</p>
<div class="grp-label">Sous-groupe d'exemple</div>
<div class="tiles s-dev">{tile('⚛', 'Titre de la tuile', "Une description d'une ou deux lignes : ce qu'on y apprend.", '11 chapitres · ≈ 45 h')}{tile('K', 'Deuxième tuile', 'Même structure, même hauteur que ses voisines.', '7 chapitres · ≈ 35 h')}{tile('📎', 'Tuile sans case', "Pour une page de révision, pas de case « Terminé ».", 'Par technologie', check=False)}</div></article>

<article id="regles"><div class="chaphead"><span class="chapnum">Charte</span><span class="badge lvl-expert">Règles</span></div><h2>Règles</h2>
<ol><li>Une seule barre de navigation, identique partout, avec des menus groupés (phases du parcours, groupes de cours) et la page courante surlignée.</li>
<li>Un sommaire collant, numéroté, avec le chapitre courant surligné, sur toute page longue (niveaux, cours, corrections, accueil).</li>
<li>Un chapitre = une carte : En 30 secondes, planche manga, objectifs, sections, exercices, TP.</li>
<li>Code : thème IDE commun, repli au-delà de 34 lignes, retour à la ligne avec indentation conservée.</li>
<li>Sections de plus de 700 mots découpées en sous-parties repliables ; paragraphes de 90 mots au plus.</li>
<li>Une affiche par sujet dans le fil ; les autres en galerie ; toute image agrandissable.</li>
<li>Pas de nouveau composant sans l'ajouter ici d'abord ; clair et sombre vérifiés à 360 et 1280 px à chaque livraison.</li></ol></article>
<div class="footnav"><a href="index.html">← Accueil</a></div>
</div>
'''
s = s[:a] + corps + s[b:]
s = re.sub(r'<style id="charte-demo">.*?</style>\n?', '', s, flags=re.S)
if 'Planches manga' not in s: s = s.replace('</style>', MANGA_CSS, 1)
p.write_text(s); print('charte régénérée')
