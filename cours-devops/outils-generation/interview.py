import re, pathlib, html

out = pathlib.Path('/mnt/user-data/outputs')

def insert_before_niche(s, ch, niche_tech, block):
    key = f'Pour sortir du lot — {niche_tech}'
    i = s.index(key); j = s.rfind('<div class="niche">', 0, i)
    assert j > s.index(f'<span class="chapnum">Chapitre {ch}</span>')
    return s[:j] + block + s[j:]

def qa_table(rows):
    t = '<div class="tablewrap"><table><tr><th>Question</th><th>Réponse attendue</th></tr>'
    for q, a in rows: t += f'<tr><td><strong>{q}</strong></td><td>{a}</td></tr>'
    return t + '</table></div>'

def theme(title, rows):
    return f'<h4>{title}</h4>' + qa_table(rows)

# ---------------- 53.6 Tech Lead ----------------
TL = '<h3>53.6 Trente questions d\'entretien Tech Lead, avec la réponse attendue<span class="badge tag-coeur">Par cœur</span></h3>'
TL += '''<p><strong>Comment répondre, quelle que soit la question</strong> : une méthode (deux ou trois étapes), un exemple vécu en format STAR (situation, tâche, action, résultat) avec un chiffre, et ce que tu ferais différemment. Quatre-vingt-dix secondes, pas plus. Le recruteur d'un Tech Lead ne cherche pas la bonne réponse technique, il cherche quelqu'un qui décide avec des critères, qui rend les arbitrages explicites, qui protège l'équipe et qui assume ses erreurs. Prépare une histoire vraie par thème ci-dessous ; c'est la seule préparation qui compte.</p>'''
TL += theme('Leadership sans autorité', [
 ("Qu'est-ce qu'un Tech Lead, pour vous ?", "Le responsable de la qualité technique et de la capacité à livrer d'une équipe, sans en être le manager : il décide de l'architecture avec l'équipe, arbitre la dette, protège le flux de travail, fait grandir les gens, et code encore, sur ce qui débloque les autres. Le senior optimise son travail ; le Tech Lead optimise le résultat de l'équipe."),
 ("Comment faites-vous accepter une décision technique à une équipe qui n'est pas d'accord ?", "Exposer le problème et les contraintes avant la solution, écouter les alternatives, décider avec des critères écrits (ADR), puis « disagree and commit » : chacun s'engage sur la décision même s'il aurait choisi autrement, avec une date de revue où l'on regarde les faits."),
 ("Comment gérez-vous un désaccord avec l'architecte ou votre manager ?", "Faits et risques chiffrés, pas d'opinions ; proposer une expérimentation bornée pour trancher ; si ça ne suffit pas, escalader avec une recommandation claire, puis se ranger derrière la décision et la porter devant l'équipe."),
 ("Un développeur senior conteste vos choix devant toute l'équipe.", "Sur le moment : reconnaître ce qui est valide, ramener aux critères, proposer d'en discuter à deux. En privé : cadrer la forme (le désaccord est bienvenu, le mode ne l'est pas) et lui donner un rôle dans la décision. Ne jamais répondre sur le terrain de l'ego."),
 ("Comment dites-vous non à un product owner ?", "Jamais un non sec : montrer le coût (délai, risque, dette), proposer une alternative (périmètre réduit, autre date, feature flag), et rendre l'arbitrage explicite pour que le sponsor décide en connaissance de cause. Le Tech Lead informe et propose ; le produit priorise."),
 ("Comment influencez-vous sans autorité hiérarchique ?", "Crédibilité technique démontrée, alliances avec les personnes influentes, décisions portées par ceux qui les appliqueront, choix des batailles, et la règle « une solution à 80 % adoptée vaut mieux qu'une parfaite refusée »."),
])
TL += theme('Décisions techniques', [
 ("Comment choisissez-vous une technologie ?", "Le besoin d'abord, puis des critères pondérés : maturité, compétences de l'équipe, exploitabilité, coût, sécurité, réversibilité ; un PoC borné dans le temps ; une ADR ; et la question « comment en sortira-t-on ? » avant d'y entrer."),
 ("Comment gérez-vous la dette technique ?", "Inventaire avec le coût d'intérêt de chaque dette (incidents, temps perdu, risque) ; part fixe du temps (20 %) ou objectifs trimestriels ; dette visible dans le backlog comme le reste ; lien avec les incidents et les fins de support ; on ne rembourse pas tout, on rembourse ce qui coûte."),
 ("Monolithe ou microservices ?", "Monolithe modulaire par défaut ; extraction par domaine quand une équipe, une contrainte d'échelle ou de technologie le justifie ; le coût des microservices est opérationnel (réseau, données réparties, observabilité) et il faut une plateforme pour l'absorber (chapitre 46)."),
 ("Comment garantissez-vous la qualité du code ?", "Définition of done écrite, revue obligatoire sous 24 h par quelqu'un qui n'a pas écrit, tests en CI avec quality gate sur le nouveau code, linters pour le style (jamais en revue humaine), pairing sur les sujets difficiles, et des mesures : taux d'échec des changements, bugs en production."),
 ("Comment faites-vous une revue de code utile ?", "Petites merge requests (moins de 400 lignes), revue rapide, commentaires sur ce qui compte (conception, sécurité, tests, lisibilité), ton bienveillant et questions plutôt qu'ordres, distinction entre bloquant et suggestion, et l'auteur explique son intention dans la description."),
 ("Comment produisez-vous une estimation fiable ?", "Décomposer en petits lots, comparer à du connu, exprimer en fourchette avec les hypothèses, mesurer le réel pour calibrer, et surtout réduire la taille des lots : une estimation d'un jour est fiable, une de trois mois ne l'est jamais."),
])
TL += theme('Livraison et priorisation', [
 ("Le projet est en retard, que faites-vous ?", "Le rendre visible tôt avec les faits ; réduire le périmètre plutôt que la qualité ; refuser les heures supplémentaires structurelles qui créent les bugs de la semaine suivante ; replanifier avec le produit ; chercher la cause (estimation, dépendance, périmètre mouvant) pour la prochaine fois."),
 ("Comment priorisez-vous entre fonctionnalités, dette, sécurité et incidents ?", "Incidents d'abord ; sécurité par niveau de risque avec un SLA de correction ; dette par coût d'intérêt ; le budget d'erreur arbitre entre vitesse et fiabilité ; une règle de proportion annoncée (par exemple 60/20/20) plutôt que des négociations à chaque sprint."),
 ("Comment gérez-vous une mise en production risquée ?", "Petits lots, feature flags pour séparer déploiement et activation, canary ou blue/green, fenêtre annoncée, rollback testé avant, astreinte prévenue, communication ; et la question « comment saura-t-on que ça a marché ? » avant de déployer."),
 ("La production est cassée après votre déploiement.", "Rollback d'abord, comprendre ensuite ; communiquer à cadence fixe ; post-mortem sans blâme dans la semaine avec des actions suivies ; et dire publiquement ce qu'on a appris. Un Tech Lead qui cache un incident perd l'équipe."),
 ("Comment gérez-vous les demandes urgentes en cours de sprint ?", "Une seule porte d'entrée, une classification (incident, sécurité, engagement client, autre), une capacité réservée aux imprévus, et pour tout ce qui entre, ce qui sort, décidé avec le produit ; puis mesurer la part d'imprévus pour la réduire."),
])
TL += theme('Les personnes', [
 ("Comment faites-vous monter en compétence un junior ?", "Objectifs explicites à trois mois, pairing régulier, merge requests guidées avec feedback détaillé, responsabilités croissantes (une fonctionnalité de bout en bout, puis une astreinte en shadowing), feedback court et fréquent, et le droit à l'erreur dans un cadre sûr (CI, revue, staging)."),
 ("Un membre de l'équipe sous-performe.", "Comprendre avant d'agir : contexte personnel, clarté des attentes, compétences, motivation. Feedback factuel et privé, plan avec objectifs et échéance, implication du manager, suivi hebdomadaire. La plupart du temps, c'est un problème de clarté ou de placement, pas de compétence."),
 ("Deux développeurs sont en conflit.", "Écouter chacun séparément, ramener aux faits et aux intérêts plutôt qu'aux positions, prendre la décision technique avec des critères explicites, poser des règles d'équipe (revue, communication), et intervenir vite : un conflit qui dure contamine l'équipe."),
 ("Comment recrutez-vous ?", "Fiche de poste honnête, exercice réaliste et court (pas d'algorithmique hors sol), entretien structuré avec une grille écrite, plusieurs évaluateurs, décision collective, réponse rapide et argumentée au candidat ; on recrute la capacité d'apprendre et le comportement en équipe autant que la technique."),
 ("Comment gérez-vous une équipe distribuée ?", "Écrit par défaut (ADR, RFC, décisions dans le dépôt), rituels courts et à heure fixe, documentation vivante, pairing à distance, confiance par résultats plutôt que par présence, et des moments synchrones réservés à ce qui en a besoin."),
 ("Comment donnez-vous un feedback difficile ?", "Vite, en privé, sur des faits observés et leur impact, en demandant le point de vue de l'autre, avec une attente claire pour la suite ; et le feedback positif en public, régulier, spécifique."),
])
TL += theme('Communication et parties prenantes', [
 ("Comment expliquez-vous un sujet technique à la direction ?", "En risque, coût, délai et options, avec une recommandation et une décision à prendre ; une page, pas de jargon, un schéma ; le détail technique en annexe pour ceux qui le veulent."),
 ("Comment annoncez-vous une mauvaise nouvelle ?", "Tôt (plus tôt que confortable), avec les faits, l'impact, les options et une recommandation ; sans excuse ni blâme ; et un rendez-vous de suivi. La mauvaise nouvelle qui sort tard est la seule qui coûte un poste."),
 ("Comment travaillez-vous avec la sécurité ?", "Sécurité intégrée dans le pipeline plutôt qu'en audit final, un security champion dans l'équipe, arbitrages explicites par niveau de risque avec le RSSI, preuves automatiques ; et le refus argumenté et écrit de ce qui est dangereux."),
 ("Comment mesurez-vous que votre équipe va bien ?", "Métriques de flux (DORA, temps de revue, taille des lots), de fiabilité (incidents, pages d'astreinte), et humaines (satisfaction, rotation, participation aux revues) ; une revue mensuelle où l'on décide quelque chose à partir de ces chiffres."),
])
TL += theme('Vous', [
 ("Quelle part de votre temps codez-vous ?", "Entre 30 et 50 %, sur ce qui débloque l'équipe ou sur les sujets structurants, jamais sur le chemin critique d'une livraison ; le reste en revue, architecture, coaching et coordination. Un Tech Lead qui code 90 % ne dirige pas ; à 0 %, il perd la crédibilité et le contact."),
 ("Votre plus grosse erreur de Tech Lead ?", "Une vraie, racontée en STAR, avec ce qu'elle a coûté et ce qui a changé durablement dans ta façon de faire. Le recruteur teste la lucidité, pas la perfection."),
 ("Qu'est-ce qui vous distingue d'un développeur senior ?", "Le senior est responsable de son code ; le Tech Lead est responsable du résultat de l'équipe : les décisions, le flux, les gens, et la relation avec le produit et la direction."),
 ("Pourquoi voulez-vous être Tech Lead ?", "Pour l'impact au-delà de son propre code, le goût des arbitrages et des décisions d'architecture, et le plaisir de voir les autres progresser ; avec une histoire qui le prouve."),
])
TL += '<div class="entretien"><strong>Pour t\'entraîner</strong> — Tire trois questions au hasard, réponds à voix haute en 90 secondes chacune, enregistre-toi, écoute : cherche le critère de décision, le chiffre et l\'histoire dans chaque réponse. Fais-le dix fois avant un entretien. Tes quatorze ans de Tech Lead et de Scrum Master contiennent toutes les histoires nécessaires ; le travail est de les mettre en forme.</div>\n'

# ---------------- 43.6 Tech Lead SRE / DevOps ----------------
SRE = '<h3>43.6 Quinze questions d\'entretien Tech Lead SRE et DevOps<span class="badge tag-coeur">Par cœur</span></h3>'
SRE += qa_table([
 ("Comment organisez-vous l'astreinte ?", "Rotation hebdomadaire à cinq ou six, primaire et secondaire, moins de deux pages par semaine et par personne comme objectif d'équipe, alertes uniquement sur les symptômes avec runbook, compensation, passation hebdomadaire ; et quand la charge dépasse, la fiabilité passe avant les fonctionnalités."),
 ("Que faites-vous dans les dix premières minutes d'un incident majeur ?", "Déclarer, prendre ou attribuer le commandement, ouvrir le canal, mesurer l'impact, mitiger avant de comprendre (rollback du dernier changement en premier suspect), communiquer une première fois, nommer un scribe."),
 ("Comment convainquez-vous le produit d'investir dans la fiabilité ?", "Avec un budget d'erreur : on négocie un SLO, on le mesure, et quand le budget est consommé la règle s'applique sans discussion ; avec le coût des incidents en heures et en clients ; et avec un pilote qui montre que la fiabilité accélère la livraison."),
 ("Une équipe refuse de définir des SLO.", "Commencer par mesurer sans objectif (un SLI, un dashboard), montrer ce que les utilisateurs vivent, puis proposer un SLO réaliste dérivé de la mesure ; ne pas imposer 99,9 % à une équipe qui fait 98 % : le premier SLO est descriptif, il devient prescriptif ensuite."),
 ("Comment réduisez-vous le MTTR ?", "Détection plus tôt (alertes de symptômes), diagnostic plus rapide (traces, logs corrélés, runbooks), mitigation plus simple (rollback en une commande, feature flags), et post-mortems qui suppriment les causes récurrentes. Mesurer chaque étape séparément."),
 ("Comment décidez-vous d'automatiser une tâche ?", "Le registre du toil : fréquence × durée × nombre de personnes, comparé au coût d'automatisation ; on automatise ce qui revient, ce qui réveille l'astreinte, ce qui est source d'erreur humaine ; on documente ce qui est trop rare pour être automatisé."),
 ("Un post-mortem révèle qu'une personne a fait une erreur.", "La question n'est pas qui, mais ce qui a rendu l'erreur possible et son impact si grand : accès direct à la production, absence de confirmation, pas de canary. Les actions portent sur le système ; la personne participe à les définir. Sans cela, personne ne dira plus la vérité dans un post-mortem."),
 ("Comment évaluez-vous la maturité DevOps d'une équipe ?", "Les métriques DORA sur trois mois, un modèle de maturité par axe (culture, livraison, infrastructure, observabilité, sécurité, fiabilité, mesure), des entretiens et l'observation d'un déploiement et d'un incident ; puis une feuille de route en trois horizons."),
 ("Comment mettez-vous en place la CI/CD dans une équipe qui déploie à la main ?", "Pipeline minimal en une semaine (build, tests, image), déploiement automatique en staging, puis en production sur un service peu risqué, avec rollback ; mesurer la fréquence et le délai avant et après ; les développeurs écrivent le pipeline avec toi, pas pour toi."),
 ("Qu'est-ce que vous refusez de mettre en production ?", "Ce qui n'a pas passé la revue de lancement : sans SLO, sans observabilité, sans rollback, sans sauvegarde testée, sans propriétaire d'astreinte, ou avec une vulnérabilité critique exploitable. Le refus est écrit, avec la liste de ce qui manque et une offre d'aide."),
 ("Comment gérez-vous le coût cloud avec les équipes ?", "Coût attribué par équipe (tags, comptes), visible dans leur dashboard, revue mensuelle, Infracost dans les merge requests, leviers dans l'ordre (éteindre, redimensionner, architecture, engagement), et une unité de coût pour distinguer croissance et gaspillage."),
 ("Comment faites-vous coexister sécurité et vitesse ?", "En rendant la sécurité automatique et par défaut : analyses dans le pipeline, images durcies fournies, secrets gérés, politiques d'admission ; bloquer seulement sur le critique, tout expliquer, proposer la correction ; la sécurité qui ralentit est contournée."),
 ("Quelle est votre stratégie de rollback ?", "Image précédente conservée et référencée par digest, rollback en une commande ou un revert Git, testé à chaque déploiement en staging, migrations de schéma compatibles N-1 pour que le rollback du code suffise, et un critère de déclenchement automatique (burn rate) sur les canaries."),
 ("Comment introduisez-vous Kubernetes dans une organisation qui n'en a pas ?", "Seulement si le besoin est là (plusieurs services, plusieurs équipes, élasticité) ; cluster managé, plateforme minimale (GitOps, observabilité, politiques) avant la première application, une équipe pilote volontaire, golden path pour les suivantes, et une équipe plateforme identifiée pour l'exploiter."),
 ("Comment rendez-vous compte à la direction ?", "Une page par mois : SLO tenus, budget d'erreur, incidents et tendance, toil, coût, risques, et trois décisions à prendre ; les chiffres viennent des systèmes, pas de saisies manuelles."),
])

# ---------------- 42.5 DevSecOps ----------------
SEC = '<h3>42.5 Quinze questions d\'entretien DevSecOps<span class="badge tag-coeur">Par cœur</span></h3>'
SEC += qa_table([
 ("Comment intégrez-vous la sécurité sans ralentir les équipes ?", "Au plus tôt et automatiquement : pre-commit et IDE, analyses dans le pipeline avec bruit maîtrisé et correction proposée, images et modules durcis fournis par la plateforme, politiques d'admission ; bloquant seulement sur le critique avec correctif disponible ; le reste en ticket avec SLA."),
 ("SAST, DAST, SCA, scan d'image : différences et place dans le pipeline ?", "SAST lit le code (injection) au commit ; SCA lit les dépendances (CVE) au commit et en continu ; le scan d'image lit l'OS et les paquets après le build ; DAST attaque l'application déployée sur staging (en-têtes, authentification, configuration). Résultats agrégés dans un outil de gestion des vulnérabilités."),
 ("Une CVE critique sort ce matin dans une bibliothèque Java très répandue. Déroulé ?", "Interroger les SBOM pour savoir quelles images la contiennent (secondes), vérifier l'exploitabilité (version, reachability, KEV), mitiger si nécessaire (WAF, flag), corriger par mise à jour de dépendance via Renovate, rebuild, redéploiement par pipeline, vérification, et un VEX pour ce qui n'est pas affecté. Communication aux parties prenantes à chaque étape."),
 ("Comment gérez-vous les secrets ?", "Supprimer le secret quand une identité suffit (rôle IAM, OIDC en CI, SPIFFE), sinon secret dynamique de courte durée (Vault database, PKI), sinon secret statique centralisé avec rotation livré par External Secrets, et en dernier recours chiffré dans Git (SOPS, Sealed Secrets) avec ses limites énoncées ; détection de secrets en pre-commit et en CI ; un secret fuité est révoqué, pas supprimé de l'historique seulement."),
 ("Comment sécurisez-vous la chaîne d'approvisionnement ?", "Dépendances épinglées et proxifiées, build unique sur runner éphémère sans socket Docker, SBOM et provenance SLSA attestés, signature keyless Sigstore, vérification à l'admission par Kyverno, déploiement par digest, actions et images de job épinglées par SHA ; XZ et tj-actions comme exemples."),
 ("Modélisation des menaces : comment faites-vous concrètement ?", "Un atelier d'une heure par fonctionnalité sensible avec les développeurs, un diagramme de flux de données avec les frontières de confiance, STRIDE pour lister les menaces, chaque menace devient une exigence ASVS puis, si possible, un test automatisé ; versionné dans le dépôt, revu à chaque changement d'architecture."),
 ("Comment traitez-vous les faux positifs et le bruit des outils ?", "Mode observation d'abord, tri des résultats, règles adaptées au contexte, fichiers d'exceptions justifiés et datés, priorisation par EPSS, KEV et reachability, VEX pour documenter, et une mesure : la part de findings qui donnent lieu à une action. Un outil qui produit 200 alertes inexploitables est désactivé en une semaine."),
 ("Comment convainquez-vous les développeurs de faire de la sécurité ?", "En leur donnant les outils dans leur flux (pas un portail à part), des messages qui expliquent et proposent la correction, des security champions formés dans chaque équipe, des chiffres partagés, et en reconnaissant publiquement les corrections ; jamais en faisant la police."),
 ("Un développeur a commité une clé AWS dans un dépôt public.", "Révoquer la clé immédiatement (elle est compromise en minutes, même supprimée après), vérifier CloudTrail pour tout usage, faire tourner ce qui en dépend, nettoyer l'historique, post-mortem sans blâme : pourquoi une clé statique existait (préférer les rôles), pourquoi la détection de secrets n'a pas bloqué."),
 ("Zero trust en une phrase, et trois mesures concrètes.", "Ne jamais faire confiance implicitement au réseau : chaque accès est authentifié, autorisé, chiffré et journalisé. Mesures : identité forte avec MFA résistant au phishing et SSO, mTLS et identités de charges de travail (SPIFFE), accès administrateur juste-à-temps et enregistré à la place du VPN."),
 ("Comment prouvez-vous la conformité ISO 27001 à un auditeur ?", "Chaque contrôle applicable est traduit en politique, implémentation et preuve automatique (merge requests approuvées, rapports de scan, revues d'accès, tests de restauration, politiques en enforce), collectées par script chaque mois et signées ; l'auditeur reçoit des échantillons en minutes, pas en semaines."),
 ("Sécuriser un cluster Kubernetes en cinq mesures.", "Authentification OIDC et RBAC strict avec audit ; Pod Security Standards restricted par namespace ; politiques d'admission (registre interne, images signées, ressources) ; NetworkPolicies default-deny et secrets gérés hors etcd ; détection à l'exécution (Falco) et posture mesurée (kube-bench, Trivy Operator). Méthode : audit, warn, enforce."),
 ("Comment sécurisez-vous une application ou un agent LLM ?", "OWASP LLM Top 10 avec l'injection indirecte en fil rouge ; passerelle LLM comme point de contrôle (authentification, quotas, masquage, journalisation, coût) ; RAG avec contrôle d'accès aux documents ; agents en lecture seule par défaut, écriture via merge request, outils minimaux, isolation ; evals et red teaming automatisés en CI ; observabilité des appels ; classification AI Act."),
 ("Pentest, bug bounty, scan automatique : quand quoi ?", "Le scan automatique en continu pour le connu ; le pentest humain une fois par an et à chaque changement majeur pour la logique métier et les enchaînements ; le bug bounty quand la maturité permet de traiter le flux, pour la découverte continue par des tiers. Les trois se complètent."),
 ("Votre premier mois comme DevSecOps dans une entreprise.", "Semaine 1 : inventaire (dépôts, pipelines, images, secrets, accès) et entretiens. Semaine 2 : les gains rapides sans friction (détection de secrets, scan d'images en observation, MFA sur les comptes à privilèges, sauvegardes testées). Semaine 3 : modélisation des menaces sur le service le plus critique, SLA de correction, agrégation des résultats. Semaine 4 : feuille de route à 90 jours, premiers security champions, rapport à la direction avec trois décisions."),
])

# ---------------- application ----------------
p = out/'devops-niveau-9-expert-leadership.html'; s = p.read_text(); assert '53.6 Trente questions' not in s
s = insert_before_niche(s, 53, 'mob.sh', TL)
s = s.replace('<li>Communiquer avec la direction, la sécurité, les métiers et les équipes dans leur langue</li>',
              '<li>Communiquer avec la direction, la sécurité, les métiers et les équipes dans leur langue</li><li>Répondre aux trente questions d\'entretien Tech Lead avec une méthode, un chiffre et une histoire</li>', 1)
s = s.replace('<li>Parler à la direction, au RSSI, aux développeurs : la même chose, trois langues.</li>',
              '<li>Parler à la direction, au RSSI, aux développeurs : la même chose, trois langues.</li><li>Les trente questions Tech Lead de la section 53.6, en 90 secondes chacune, avec une histoire STAR par thème.</li>', 1)
p.write_text(s); print('53 :', re.findall(r'<h3>(53\.\d) ', s))

p = out/'devops-niveau-8-sre-architecture.html'; s = p.read_text(); assert '43.6 Quinze questions' not in s
s = insert_before_niche(s, 43, 'Byteman', SRE)
s = s.replace('<li>SRE de plateforme : les SLO de la plateforme (huit composants), les règles propres au rayon d\'impact, les onze capacités de fiabilité en libre-service, la frontière avec les équipes produit.</li>',
              '<li>SRE de plateforme : les SLO de la plateforme (huit composants), les règles propres au rayon d\'impact, les onze capacités de fiabilité en libre-service, la frontière avec les équipes produit.</li><li>Les quinze questions Tech Lead SRE de la section 43.6.</li>', 1)
p.write_text(s); print('43 :', re.findall(r'<h3>(43\.\d) ', s))

p = out/'devops-niveau-7-securite-devsecops.html'; s = p.read_text(); assert '42.5 Quinze questions' not in s
s = insert_before_niche(s, 42, 'compliance-trestle', SEC)
s = s.replace('<li>ISO 27001, SOC 2, RGPD, NIS2, DORA, SecNumCloud : nature, cible, et comment tu produis les preuves.</li>',
              '<li>ISO 27001, SOC 2, RGPD, NIS2, DORA, SecNumCloud : nature, cible, et comment tu produis les preuves.</li><li>Les quinze questions DevSecOps de la section 42.5.</li>', 1)
p.write_text(s); print('42 :', re.findall(r'<h3>(42\.\d) ', s))

# ---------------- page de révision « Entretien » ----------------
head = re.sub(r'<title>[^<]*</title>', '<title>Fiches entretien — tout le parcours</title>', re.search(r'^.*?</head>', (out/'devops-niveau-0-fondations.html').read_text(), flags=re.S).group(0))
extra = """
.pagenav{display:flex;flex-wrap:wrap;gap:.6rem;margin-bottom:1rem;font-size:.9rem}
.pagenav a{color:#fff;text-decoration:none;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);padding:.3rem .75rem;border-radius:6px}
.pagenav a:hover{background:rgba(255,255,255,.2);color:#fff}
.entretien .src{display:block;font-size:.8rem;color:var(--muted);margin-top:.4rem}
body{padding-bottom:2rem}
@media print{.pagenav{display:none}}
</style>"""
head = head.replace('</style>', extra, 1)
levels = [("devops-niveau-0-fondations.html","Niveau 0 — Fondations"),("devops-niveau-1-conteneurs.html","Niveau 1 — Conteneurs"),("devops-niveau-2-ci-cd.html","Niveau 2 — CI/CD"),
 ("devops-niveau-3-infrastructure-as-code.html","Niveau 3 — Infrastructure as Code"),("devops-niveau-4-cloud.html","Niveau 4 — Cloud"),("devops-niveau-5-kubernetes.html","Niveau 5 — Kubernetes"),
 ("devops-niveau-6-observabilite.html","Niveau 6 — Observabilité"),("devops-niveau-7-securite-devsecops.html","Niveau 7 — Sécurité DevSecOps"),("devops-niveau-8-sre-architecture.html","Niveau 8 — SRE et architecture"),("devops-niveau-9-expert-leadership.html","Niveau 9 — Expert et leadership")]
body = '''<body>
<header class="hero"><div class="in">
<div class="pagenav"><a href="index.html">← Accueil du parcours</a></div>
<div class="level">Révision</div>
<h1>Fiches entretien : tout le parcours en une page</h1>
<p class="lead">Les 54 encadrés « En entretien » du cours, puis les quatre banques de questions-réponses : trente questions Tech Lead, quinze Tech Lead SRE et DevOps, quinze DevSecOps, vingt Kubernetes. À travailler à voix haute, chronométré, la veille d'un entretien.</p>
<div class="meta"><span>Méthode : une réponse = un critère de décision + un chiffre + une histoire STAR, en 90 secondes</span></div>
</div></header>
<div class="single">
<article><div class="chaphead"><span class="chapnum">Les cinq réponses de trois minutes</span><span class="badge tag-coeur">Par cœur</span></div>
<h2>À dérouler sans support</h2>
<ol>
<li>Concevoir l'infrastructure AWS d'une application web avec base de données (chapitre 21).</li>
<li>Déployer sans interruption avec une migration de schéma (chapitres 15 et 47).</li>
<li>Sécuriser un cluster Kubernetes (chapitre 39).</li>
<li>Gérer les secrets, de l'identité au chiffrement dans Git (chapitre 38).</li>
<li>Sécuriser une application ou un agent LLM (chapitre 54).</li>
</ol></article>
'''
for fn, title in levels:
    s = (out/fn).read_text()
    arts = re.findall(r'<span class="chapnum">Chapitre (\d+)</span>.*?<h2>(.*?)</h2>(.*?)(?=<span class="chapnum">Chapitre|<section class="rev")', s, flags=re.S)
    body += f'<article><div class="chaphead"><span class="chapnum">{html.escape(title)}</span></div><h2>Encadrés « En entretien »</h2>'
    for num, h2, chunk in arts:
        h2t = re.sub(r'<[^>]+>', '', h2)
        for m in re.finditer(r'<div class="entretien">(.*?)</div>', chunk, flags=re.S):
            body += f'<div class="entretien">{m.group(1)}<span class="src">Chapitre {num} — {html.escape(h2t)} · <a href="{fn}#c{num}">ouvrir</a></span></div>'
    body += '</article>\n'
# banques de questions
banks = [("devops-niveau-9-expert-leadership.html", r'<h3>53\.6 Trente questions.*?(?=<div class="niche">)', "Trente questions Tech Lead", "Niveau 9, chapitre 53"),
         ("devops-niveau-8-sre-architecture.html", r'<h3>43\.6 Quinze questions.*?(?=<div class="niche">)', "Quinze questions Tech Lead SRE et DevOps", "Niveau 8, chapitre 43"),
         ("devops-niveau-7-securite-devsecops.html", r'<h3>42\.5 Quinze questions.*?(?=<div class="niche">)', "Quinze questions DevSecOps", "Niveau 7, chapitre 42"),
         ("devops-niveau-5-kubernetes.html", r'<h3>26\.8 Vingt questions.*?(?=<div class="niche">)', "Vingt questions Kubernetes", "Niveau 5, chapitre 26")]
for fn, pat, title, src in banks:
    s = (out/fn).read_text(); m = re.search(pat, s, flags=re.S); assert m, title
    block = re.sub(r'<h3>.*?</h3>', '', m.group(0), count=1, flags=re.S)
    body += f'<article><div class="chaphead"><span class="chapnum">{src}</span><span class="badge tag-coeur">Par cœur</span></div><h2>{title}</h2>{block}</article>\n'
body += '''</div>
<script>
(function(){ var root=document.documentElement; try{ var t=localStorage.getItem('devops-theme'); if(t) root.setAttribute('data-theme',t); }catch(e){}
  document.querySelectorAll('table').forEach(function(t){ var rows=t.rows; if(!rows.length) return; var head=rows[0]; if(!head.querySelector('th')) return; head.classList.add('head');
    var labels=Array.prototype.map.call(head.cells,function(c){return c.textContent.trim();});
    for(var i=1;i<rows.length;i++){ var cells=rows[i].cells; for(var j=0;j<cells.length;j++){ if(cells[j].tagName==='TD') cells[j].setAttribute('data-label',labels[j]||''); } } t.classList.add('stack'); });
})();
</script>
</body></html>'''
(out/'devops-fiches-entretien.html').write_text(head + '\n' + body)
print('fiches entretien :', (out/'devops-fiches-entretien.html').stat().st_size, 'octets')

# lien depuis la page d'accueil
ip = out/'devops-parcours-complet.html'; t = ip.read_text()
if 'devops-fiches-entretien.html' not in t:
    t = t.replace('<h2>Les cinq réponses à savoir dérouler en trois minutes</h2>',
                  '<h2>Réviser pour un entretien</h2>\n<p>Une page compile tout ce qui sert en entretien : les 54 encadrés « En entretien », trente questions Tech Lead, quinze Tech Lead SRE et DevOps, quinze DevSecOps, vingt Kubernetes, avec la réponse attendue. <a href="devops-fiches-entretien.html"><strong>Ouvrir les fiches entretien</strong></a>.</p>\n<h2>Les cinq réponses à savoir dérouler en trois minutes</h2>', 1)
    ip.write_text(t); print('index ok')
