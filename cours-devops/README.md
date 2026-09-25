# DevOps Courses

Parcours DevOps de zéro à expert (10 niveaux, 54 chapitres, 54 travaux pratiques corrigés) et 10 cours complémentaires, en HTML statique. Fil conducteur : la plateforme CrisisShield. Tout se lance en Docker.

Ouvrir `index.html` dans un navigateur : aucune installation, aucun serveur.

## Contenu

| Fichiers | Contenu |
|---|---|
| `index.html` | Accueil : commencer, parcours DevOps, développement, cloud et données, savoir-être, réviser, méthode |
| `devops-00-…` à `devops-09-…` | Les dix niveaux du parcours (fondations → expert et leadership) |
| `devops-10-aide-memoire.html`, `devops-11-fiches-entretien.html` | Révision : commandes, bonnes pratiques, questions d'entretien |
| `cours-01` à `cours-03` | Frontend : React, Angular, Vue |
| `cours-04` à `cours-06` | Java et JVM : Struts/Hibernate/JSP, Kotlin, Java PKI et signature électronique |
| `cours-07`, `cours-08` | Cloud et données : Cloud AWS/Azure/GCP, Data Platform AWS/Talend/Airflow |
| `cours-09`, `cours-10` | Savoir-être : progression de zéro à expert, situations et attitudes |
| `corrections/tpNN-….html` | Les 54 corrections de travaux pratiques |
| `site-00-charte-graphique.html` | Charte graphique : composants, couleurs, règles, exemples |
| `images/` | Schémas et fiches visuelles (WebP) |
| `outils-generation/` | Scripts qui génèrent et maintiennent les pages |

Chaque chapitre : « En 30 secondes », une planche manga sur le piège du chapitre, objectifs, sections, code, exercices corrigés, travail pratique. Fonctions communes : sommaire numéroté avec chapitre courant, lecture rapide, mode sombre, code façon IDE (coloration, repli des blocs longs), images agrandissables, progression enregistrée dans le navigateur.

## Outils de génération (en Docker)

```bash
alias py='docker run --rm -v "$PWD:/w" -w /w python:3.12-slim python'
py outils-generation/restyle.py .          # applique la charte (barre, pied de page, styles, scripts) à toutes les pages
py outils-generation/charte_page.py .      # régénère la charte graphique
py outils-generation/corr_toc.py corrections   # sommaire des étapes sur les corrections
py outils-generation/digest.py devops-05-kubernetes.html niveau-05   # sous-parties repliables, paragraphes longs
py outils-generation/manga7.py devops-05-kubernetes.html              # planches manga d'une page (manga2 à manga21)
```

| Script | Rôle |
|---|---|
| `restyle.py` | Charte commune : barre et menus groupés, pied de page, CSS, visionneuse, coloration, sommaire, lecture rapide, accessibilité |
| `site-highlight.js` | Coloration syntaxique légère, sans dépendance |
| `digest.py` | Lisibilité : audit, galerie, sous-parties repliables, découpe des paragraphes longs (recettes par page) |
| `manga_engine.py`, `manga_gabarit.py`, `manga2.py` à `manga21.py` | Planches manga : moteur de dessin, gabarit en trois cases, données par page |
| `front_gen.py` + `front_pages.py`, `pki_pages.py`, `data_pages.py`, `struts_pages.py`, `kotlin_pages.py`, `soft_pages.py`, `soft2_pages.py` | Génération des cours complémentaires |
| `corr_gen*.py`, `corr_tp02.py`, `corr_toc.py` | Génération des corrections |
| `revise.py`, `revise_answers.py` | Réponses attendues aux questions de révision |
| `addfig.py`, `addfig_h3.py`, `addfig_at.py` | Insertion d'images dans un chapitre |
| `charte_page.py` | Charte graphique avec exemples vivants |
| `localize.py`, `prep_online.py` | Passage entre la version locale et la version en ligne |

Règles de la charte (détail dans `site-00-charte-graphique.html`) : une planche manga par chapitre, code replié au-delà de 34 lignes, sections de plus de 700 mots découpées en sous-parties repliables, paragraphes de 90 mots au plus, une seule affiche par sujet dans le fil, contrastes WCAG 2 AA en clair et en sombre.
