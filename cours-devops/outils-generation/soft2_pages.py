"""Cours savoir-être de zéro à expert : version digeste (paliers courts, échelle visuelle, gestes clés, auto-évaluation). Usage : python3 soft2_pages.py <dossier>"""
import sys, runpy, pathlib
g = runpy.run_path(pathlib.Path(__file__).with_name('front_gen.py'), run_name='front'); ch, page = g['ch'], g['page']

CSS = """<style id="se-design">
.se-why{display:grid;grid-template-columns:auto 1fr;gap:.6rem 1rem;align-items:start;background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:.9rem 1.1rem;margin:.6rem 0 1rem}
.se-why b{color:var(--accent-ink);white-space:nowrap}
.ladder{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.6rem;margin:1rem 0}
.ladder .step{border:1px solid var(--line);border-radius:10px;padding:.7rem .8rem;background:var(--paper);font-size:.9rem;line-height:1.45}
.ladder .step b{display:block;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;margin-bottom:.35rem}
.ladder .step:nth-child(1){border-top:4px solid #16A34A}.ladder .step:nth-child(2){border-top:4px solid #2563EB}.ladder .step:nth-child(3){border-top:4px solid #D97706}.ladder .step:nth-child(4){border-top:4px solid #DB2777}
.ladder .step small{display:block;margin-top:.45rem;color:var(--muted);font-size:.82rem}
@media(max-width:760px){.ladder{grid-template-columns:1fr 1fr}}@media(max-width:480px){.ladder{grid-template-columns:1fr}}
.se-geste{border-left:4px solid var(--accent);background:var(--accent-soft);border-radius:8px;padding:.8rem 1rem;margin:1rem 0;font-size:1.02rem}
.se-geste b{color:var(--accent-ink)}
.avap{display:grid;grid-template-columns:1fr 1fr;gap:.7rem;margin:.8rem 0}
.avap div{border-radius:10px;padding:.8rem 1rem;font-size:.92rem;line-height:1.5}
.avap .av{background:#FEF2F2;border:1px solid #FECACA}.avap .ap{background:#F0FDF4;border:1px solid #BBF7D0}
[data-theme="dark"] .avap .av{background:#3B1111;border-color:#7F1D1D}[data-theme="dark"] .avap .ap{background:#0F2E1A;border-color:#166534}
.avap b{display:block;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;margin-bottom:.3rem}
@media(max-width:600px){.avap{grid-template-columns:1fr}}
.se-check{list-style:none;padding:0;margin:.6rem 0}.se-check li{margin:.3rem 0}.se-check label{display:flex;gap:.6rem;align-items:flex-start;cursor:pointer}.se-check input{margin-top:.35rem}
.se-week{display:grid;grid-template-columns:auto 1fr;gap:.5rem 1rem;background:var(--paper);border:1px dashed var(--line-strong);border-radius:10px;padding:.8rem 1rem;margin:1rem 0;font-size:.95rem}
.se-week b{color:var(--muted);font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;padding-top:.15rem}
.se-recap{background:var(--hero);color:#fff;border-radius:10px;padding:.9rem 1.1rem;margin:1rem 0}.se-recap b{color:#93C5FD}
.se-eval{display:grid;grid-template-columns:1fr auto;gap:.4rem 1rem;align-items:center;margin:.35rem 0}
.se-eval .opts{display:flex;gap:.3rem;flex-wrap:wrap}.se-eval .opts label{border:1px solid var(--line);border-radius:6px;padding:.15rem .5rem;font-size:.8rem;cursor:pointer}
.se-eval .opts input{display:none}.se-eval .opts label:has(input:checked){background:var(--accent);color:#fff;border-color:var(--accent)}
#se-score{font-weight:700;margin-top:.8rem}
.roadmap{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.6rem;margin:.8rem 0}
.roadmap div{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:.7rem .8rem;font-size:.88rem}
.roadmap div b{display:block;color:var(--accent-ink);margin-bottom:.25rem}
@media(max-width:760px){.roadmap{grid-template-columns:1fr 1fr}}
</style>"""
JS = """<script id="se-script">(function(){var K='se-checks';var st={};try{st=JSON.parse(localStorage.getItem(K)||'{}')}catch(e){}
var inputs=document.querySelectorAll('.se-check input,.se-eval input');
inputs.forEach(function(i){var key=i.type==='radio'?i.name+'|'+i.value:i.name;if(st[key])i.checked=true;
 i.addEventListener('change',function(){if(i.type==='radio'){Object.keys(st).forEach(function(k){if(k.indexOf(i.name+'|')===0)delete st[k]});st[i.name+'|'+i.value]=true}else st[i.name]=i.checked;try{localStorage.setItem(K,JSON.stringify(st))}catch(e){}score()});});
function score(){var s=document.getElementById('se-score');if(!s)return;var t=0,n=0,low=[];document.querySelectorAll('.se-eval').forEach(function(r){var c=r.querySelector('input:checked');if(c){var v=parseInt(c.value,10);t+=v;n++;if(v<=2)low.push(r.querySelector('span').textContent)}});
 s.textContent=n?('Score : '+t+' / '+(n*4)+' — moyenne '+(t/n).toFixed(1)+' sur 4'+(low.length?' · à travailler en priorité : '+low.slice(0,2).join(', '):' · bravo, choisis les deux notes les plus basses')):'Coche un niveau par compétence pour obtenir ton score (sauvegardé dans ce navigateur).'}
score();})();</script>"""

def why(items): return '<div class="se-why">' + ''.join(f'<b>{k}</b><span>{v}</span>' for k, v in items) + '</div>'
def ladder(d, c, s, e): return '<div class="ladder">' + ''.join(f'<div class="step"><b>{n}</b>{t}<small>{p}</small></div>' for n, (t, p) in zip(("Débutant", "Confirmé", "Senior", "Expert"), (d, c, s, e))) + '</div>'
def geste(t): return f'<div class="se-geste"><b>Le geste clé :</b> {t}</div>'
def avap(a, b): return f'<div class="avap"><div class="av"><b>Réflexe à éviter</b>{a}</div><div class="ap"><b>Attitude qui marche</b>{b}</div></div>'
def check(n, items): return '<ul class="se-check">' + ''.join(f'<li><label><input type="checkbox" name="{n}-{i}"> {t}</label></li>' for i, t in enumerate(items)) + '</ul>'
def week(items): return '<div class="se-week">' + ''.join(f'<b>{k}</b><span>{v}</span>' for k, v in items) + '</div>'
def recap(t): return f'<div class="se-recap"><b>En une phrase :</b> {t}</div>'

def palier(num, titre, lvl, bref, obj, pourquoi, echelle, gest, situation, pratiques, semaine, phrase, exos, tp):
    sec = [("Pourquoi ça compte", why(pourquoi), None), ("L'échelle", ladder(*echelle) + geste(gest), None), ("Une situation, deux réactions", avap(*situation), None), ("Trois pratiques, pas plus", check(f"p{num}", pratiques) + week(semaine) + recap(phrase), None)]
    return ch(f"Palier {num} — {titre}", lvl, bref, obj, sec, exos, tp)

SE = [
ch("Mode d'emploi : douze semaines pour monter d'un palier", 'j',
 ["Le savoir-être se travaille comme un sport : peu de théorie, des répétitions observées, une mesure.", "Huit paliers, chacun en dix minutes : pourquoi, échelle en quatre niveaux, geste clé, situation avant/après, trois pratiques à cocher, habitude de la semaine.", "Le bilan final donne ta note par compétence (sauvegardée dans ton navigateur) et ton plan des douze semaines suivantes."],
 ["Lire un palier en dix minutes", "Choisir deux compétences et un observateur", "Tenir une pratique par semaine"],
 [("Comment lire ce cours", why([("10 min", "un palier se lit en dix minutes ; les cases à cocher gardent ta progression"), ("1 geste", "chaque palier tient dans un geste clé : si tu ne retiens qu'une chose, c'est lui"), ("1 semaine", "l'encadré « cette semaine » est la seule chose à faire entre deux lectures"), ("1 observateur", "un pair, un mentor ou ton manager dit ce qu'il a vu : sans regard extérieur, on ne progresse pas")]), None),
  ("La feuille de route", '<div class="roadmap"><div><b>Semaines 1–3</b>Paliers 0 et 1 : journal des émotions, e-mails courts, reformulation.</div><div><b>Semaines 4–6</b>Paliers 2 et 3 : engagements visibles, messages types, un feedback par semaine.</div><div><b>Semaines 7–9</b>Paliers 4 et 5 : une proposition avec essai borné, une délégation de résultat.</div><div><b>Semaines 10–12</b>Paliers 6 et 7 : carte des parties prenantes, protocole de crise, bilan et histoires STAR.</div></div>', None),
  ("Les deux cours savoir-être", "Ce cours dit <em>comment progresser</em> ; le cours « situations et attitudes » dit <em>quoi dire</em> dans 80 situations, par rôle. Chaque palier renvoie aux chapitres où trouver les mots.", None)],
 [("Combien de paliers en même temps ?", "Deux au maximum par trimestre. Plus, c'est de la lecture ; un savoir-être change en dix répétitions observées."),
  ("Question d'entretien : comment progresses-tu sur les compétences humaines ?", "Une compétence à la fois, une situation réelle par semaine, un observateur, un journal ; et un exemple récent de ce que ça a changé.")],
 ("Mise en place", ["Choisir tes deux premiers paliers (souvent 0 et 1) et un observateur ; le lui dire.", "Bloquer dix minutes le dimanche soir.", "Faire le bilan initial (dernier chapitre) pour avoir ta note de départ."],
  "Attendu : deux paliers, un observateur qui a accepté, un créneau dans l'agenda, une note de départ enregistrée.")),

palier(0, "Se connaître", 'j',
 ["Nommer ce qu'on ressent, savoir ce qui le déclenche, connaître ses valeurs et son énergie.", "On ne supprime pas un déclencheur : on le voit venir et on prépare sa réponse.", "Mesure : deux minutes de journal par soir pendant deux semaines."],
 ["Tenir un journal d'émotions exploitable", "Nommer tes trois déclencheurs et une parade chacun", "Organiser ta semaine selon ton énergie"],
 [("Le problème", "réagir à chaud, puis regretter ; expliquer ses réactions par les autres"), ("Ce que ça change", "voir venir sa réaction et choisir ; comprendre ses conflits (une valeur bafouée)"), ("La mesure", "journal de deux semaines : situation, émotion en un mot, intensité 1–5, déclencheur")],
 (("Réagit sans le savoir", "journal quotidien de deux minutes"), ("Nomme l'émotion après coup, voit deux ou trois déclencheurs", "relire le journal le dimanche, chercher les motifs"), ("Remarque pendant, et choisit sa réponse", "la phrase intérieure : « je suis agacé, je prends une minute »"), ("Anticipe, adapte son contexte, aide les autres", "revoir ses valeurs chaque trimestre ; organiser la journée selon son énergie")),
 "quand ça monte, nommer l'émotion dans sa tête et prendre une minute avant de répondre.",
 ("Un collègue te contredit devant l'équipe. La chaleur monte, tu réponds sec, tu te justifies, la réunion se crispe.", "Tu te dis « je suis agacé », tu respires, tu poses une question : « qu'est-ce qui te gêne exactement ? » Tu réponds sur ce point, ou tu proposes d'en parler après."),
 ["Journal du soir : trois situations, émotion, intensité, déclencheur (deux minutes).", "Relecture du dimanche : entourer les déclencheurs qui reviennent, écrire une parade pour chacun.", "Carte d'énergie : mes heures fortes, ce qui me vide, ce qui me recharge ; une plage protégée dans l'agenda."],
 [("Cette semaine", "le journal chaque soir ; en fin de semaine, tes trois déclencheurs sur une ligne."), ("Observateur", "« quand est-ce que tu me vois réagir à chaud ? »"), ("Aller plus loin", "situations et attitudes, chapitre 1 : faits, opinions, émotions.")],
 "je ne contrôle pas ce que je ressens, je choisis ce que j'en fais, et ça se prépare.",
 [("Ton journal montre « agacé » cinq fois, toujours en réunion d'estimation. Que fais-tu ?", "Le déclencheur est la négociation des chiffres (valeur honnêteté). Parade : la phrase préparée « l'estimation ne se négocie pas, le périmètre oui », dite calmement à la prochaine réunion ; puis noter si l'agacement baisse."),
  ("Question d'entretien : ta valeur principale et comment elle se voit ?", "Une valeur, un exemple récent où elle t'a coûté quelque chose, et ce que ça a produit.")],
 ("Deux semaines de journal", ["Journal quotidien de deux minutes pendant quatorze jours.", "Bilan : trois déclencheurs avec parade ; cinq valeurs avec un exemple vécu.", "Une plage de concentration protégée dans l'agenda, tenue deux semaines."],
  "Attendu : au moins vingt entrées ; trois déclencheurs avec parade ; cinq valeurs avec exemple ; la plage tenue quatre fois sur cinq.")),

palier(1, "Communiquer", 'j',
 ["Écouter avant de répondre, dire une chose claire et courte, choisir le bon canal.", "L'écrit a une forme (demande, faits, prochaine étape) ; l'oral aussi (conclusion, raisons, détails sur demande).", "Mesure : la longueur de tes e-mails et la vitesse des réponses obtenues."],
 ["Reformuler avant de répondre", "Écrire un message en cinq lignes, demande en tête", "Adapter le même contenu à trois audiences"],
 [("Le problème", "on parle pour se justifier, on écrit long, on répond à côté"), ("Ce que ça change", "moins de malentendus, des réponses plus rapides, une réputation de clarté"), ("La mesure", "e-mails de cinq lignes ; délai des réponses obtenues")],
 (("Interrompt, écrit long et émotionnel, jargon", "reformuler avant de répondre ; relire à froid"), ("Écoute jusqu'au bout, écrit court avec la demande en tête", "demande / faits / prochaine étape"), ("Adapte à l'audience, gère un désaccord calmement, sait se taire", "une question avant d'argumenter"), ("Fait décider, désamorce par une question, raccourcit les réunions", "faciliter plutôt que convaincre")),
 "avant de répondre, reformuler : « si je comprends bien, tu dis que… ».",
 ("E-mail de dix lignes qui rappelle l'historique, reproche le retard de l'autre équipe, en copie à tout le monde.", "« Objet : API paiement — date. Bonjour Marc, notre démo du 15 dépend de l'API prévue le 10. Peux-tu me confirmer une date aujourd'hui ? Merci. » Une demande, deux faits, zéro copie inutile."),
 ["Toute demande floue : trois questions (quel problème, pour quand et avec quoi, à quoi on verra que c'est réussi).", "Tout e-mail : la demande en première ligne, cinq lignes, relu à froid ; sensible = une nuit ou un appel.", "Tout oral : la conclusion d'abord, deux raisons, les détails si on te les demande."],
 [("Cette semaine", "trois e-mails réécrits en cinq lignes ; reformuler dans trois conversations."), ("Observateur", "« est-ce que je t'interromps ? mes messages sont-ils clairs ? »"), ("Aller plus loin", "situations et attitudes, chapitre 10 : écrire, parler, présenter.")],
 "comprendre d'abord, dire court ensuite, faire décider enfin.",
 [("Comment expliquer un problème technique à un non-technicien ?", "Par l'impact et une analogie : ce que ça empêche, combien de temps, ce qu'il faut décider ; le mécanisme seulement s'il le demande. Test : un mot de jargon par phrase maximum."),
  ("Question d'entretien : un malentendu qui a coûté cher ?", "Le malentendu, ce qui n'avait pas été reformulé, le coût, la règle adoptée (trois questions, compte rendu en cinq lignes).")],
 ("Atelier écriture et écoute", ["Cinq e-mails réels réécrits en cinq lignes ; comparer le délai des réponses.", "Trois conversations avec reformulation ; noter une fois où tu avais mal compris.", "Le même sujet en deux minutes pour la direction, pour tes pairs, pour un junior ; s'enregistrer."],
  "Attendu : réponses plus rapides sur au moins deux e-mails ; un malentendu évité par la reformulation ; trois versions qui commencent différemment.")),

palier(2, "Être fiable", 'c',
 ["Dire ce qu'on va faire, le faire ou prévenir tôt ; ne pas surpromettre ; assumer une erreur en une minute.", "La fiabilité repose sur peu de sujets en cours et sur le non avec alternative.", "Mesure : engagements tenus ou renégociés à temps ; zéro manqué en silence."],
 ["Prévenir dès que tu sais, avec une nouvelle date", "Limiter le travail en cours et dire non avec alternative", "Assumer une erreur en une minute"],
 [("Le problème", "on accepte tout, on découvre le retard la veille, on cache les erreurs"), ("Ce que ça change", "on te confie plus, on te croit, on te laisse tranquille"), ("La mesure", "tableau du mois : tenu / renégocié à temps / manqué ; objectif zéro manqué")],
 (("Accepte tout, découvre le retard la veille, s'excuse dix fois", "une liste de priorités unique"), ("Prévient tôt avec une date, deux sujets en cours, assume avec faits", "messages types retard et erreur"), ("Chiffre avant de s'engager, propose des options, dit non avec alternative", "fourchette + hypothèses ; « oui si… »"), ("Rend l'équipe prévisible, retire le superflu, arbitre pour les autres", "engagements visibles, revue hebdomadaire")),
 "dès qu'un délai glisse, le dire avec une nouvelle date et une option.",
 ("Mardi tu vois que vendredi ne tiendra pas ; tu te tais, tu fais des nuits, tu annonces jeudi soir que ce sera lundi.", "Mardi : « le livrable de vendredi glisse à mardi : X a révélé Y. Je peux livrer A et B vendredi sans C si vous préférez. » Faits, date, option."),
 ["Une liste de priorités unique, deux sujets en cours maximum, revue le lundi.", "Messages types prêts : retard (faits, date, option), erreur (impact, correction, prochaine nouvelle, prévention), non (reformuler, coût, alternative).", "Avant de s'engager : une fourchette avec les hypothèses écrites."],
 [("Cette semaine", "un engagement renégocié au premier signe de glissement ; un non avec alternative."), ("Observateur", "« est-ce que je te surprends ? est-ce que je préviens assez tôt ? »"), ("Aller plus loin", "situations et attitudes, chapitre 2 : deadline impossible, tâche ingrate.")],
 "on ne juge pas la fiabilité sur les promesses, mais sur les surprises évitées.",
 [("Tu as accepté trois sujets, tous en retard. Que fais-tu ?", "Les rendre visibles et demander l'arbitrage : « trois priorités en parallèle, toutes en retard ; laquelle je mets en pause, ou qui en reprend une ? » C'est un service rendu au décideur, pas un aveu."),
  ("Question d'entretien : une promesse non tenue ?", "Une vraie, ce que tu as fait dès que tu l'as su, le coût, la règle adoptée depuis.")],
 ("Kit de fiabilité", ["Liste unique de priorités avec la règle des deux sujets ; revue hebdomadaire pendant un mois.", "Trois messages types écrits et utilisés au moins une fois chacun.", "Tableau des engagements du mois : zéro manqué sans renégociation."],
  "Attendu : zéro engagement manqué en silence sur un mois ; trois messages types de cinq lignes qui ont servi ; travail en cours visible et limité.")),

palier(3, "Collaborer", 'c',
 ["Donner et recevoir du feedback, relire sans blesser, régler un désaccord tôt et en direct.", "Le feedback se donne en SBI (situation, comportement, impact) et se reçoit en remerciant et en demandant un exemple.", "Mesure : un feedback donné par semaine ; un désaccord réglé sous 48 heures."],
 ["Donner un feedback SBI en trois phrases", "Relire du code ou un document utilement", "Aller voir la personne sous 48 heures"],
 [("Le problème", "on évite, on accumule, on explose ; ou on critique en public"), ("Ce que ça change", "les problèmes se règlent petits ; les gens te parlent avant que ça casse"), ("La mesure", "un feedback SBI par semaine ; délai entre le désaccord et la conversation")],
 (("Prend la critique pour soi, évite ou fait les conflits en public", "règle du délai ; SBI écrit avant de parler"), ("Feedback factuel en privé, accepte la critique avec un exemple, va voir la personne", "un feedback positif factuel par semaine"), ("Désamorce tôt, arbitre entre pairs, protège les juniors en revue", "règle d'équipe de revue ; médiation en trois temps"), ("Installe la culture : exigeant et bienveillant, sans blâme", "demander du feedback sur soi, en public")),
 "un désaccord se règle en direct, en privé, sous 48 heures, sur un fait, avec une demande.",
 ("Un collègue s'attribue ton correctif en réunion ; tu ne dis rien, tu rumines, tu en parles à deux autres, la relation pourrit.", "Le jour même, en privé : « ce matin tu as présenté le correctif comme le tien ; j'aimerais qu'on cite qui a fait quoi. Ok pour la prochaine fois ? »"),
 ["Feedback SBI : situation, comportement, impact, attente ; trois phrases ; en privé ; tôt.", "Revue : commencer par ce qui est bien, trier bloquant / mineur / opinion, écrire des questions.", "Recevoir : « merci, tu as un exemple ? », choisir une chose à changer, le dire."],
 [("Cette semaine", "un feedback positif factuel et un feedback difficile, en SBI."), ("Observateur", "« comment tu trouves mes revues ? mon ton quand je ne suis pas d'accord ? »"), ("Aller plus loin", "situations et attitudes, chapitres 2 et 4 : revue dure, senior qui résiste.")],
 "on parle du comportement et de son impact, jamais de la personne ; et vite.",
 [("Un senior rejette tes MR avec des commentaires secs. Réaction ?", "En privé : « tes revues m'aident sur le fond ; la forme me fait perdre du temps à deviner. Tu peux dire ce qui bloque ? » Puis une règle d'équipe si ça continue."),
  ("Question d'entretien : un conflit avec un collègue ?", "STAR avec la conversation directe (quand, où, quels mots), l'accord, le résultat durable ; jamais une version où l'autre a tout faux.")],
 ("Atelier feedback et conflit", ["Trois feedbacks SBI réels (dont un difficile) ; noter la réaction.", "Trois relectures avec tri et questions ; demander à l'auteur ce qu'il en a pensé.", "Une conversation de désaccord jouée, puis une médiation à trois."],
  "Attendu : feedbacks en trois phrases plus une attente ; auteurs qui trouvent la revue utile ; accord de fonctionnement en deux lignes.")),

palier(4, "Influencer sans autorité", 's',
 ["Faire adopter une idée sans pouvoir hiérarchique : faits, démonstration, essai réversible, patience.", "Négocier sur les intérêts, pas sur les positions ; tenir des réunions qui décident.", "Mesure : propositions qui obtiennent un essai ; décisions par réunion."],
 ["Convaincre avec un fait et un essai borné", "Négocier avec intérêts, options, critères, alternative", "Faciliter une réunion de 25 minutes qui décide"],
 [("Le problème", "on argumente en volume, on se vexe du refus, on croit que la bonne idée suffit"), ("Ce que ça change", "tes idées passent sans conflit ; on te consulte avant de décider"), ("La mesure", "propositions qui obtiennent un essai ; décisions par réunion")],
 (("Argumente longuement, se vexe du refus", "un fait par argument, deux arguments maximum"), ("Prototype, chiffre, pilote ; accepte de ne pas convaincre", "« qu'est-ce qui te ferait dire oui ? »"), ("Comprend les intérêts, construit des options, tient les réunions", "intérêts / options / critères / alternative"), ("Fait émerger la décision, construit des coalitions, influence les critères avant la réunion", "les entretiens avant la réunion")),
 "commencer par le problème de l'autre, montrer un fait, proposer un essai borné, laisser décider.",
 ("Tu présentes ton standard avec dix arguments ; l'équipe se braque, tu insistes, rien ne change.", "« Je sais que ça vous ajoute une étape. Voilà ce que ça a évité ailleurs. Un essai sur un projet, un mois, avec ce critère ; puis on décide ensemble. »"),
 ["Convaincre : question (leur problème) → fait ou démonstration → essai réversible → décision à eux.", "Négocier : intérêts des deux côtés, trois options, un critère objectif, ton alternative.", "Réunion : ordre du jour = décisions attendues, documents avant, 25 ou 50 minutes, compte rendu en cinq lignes avec propriétaires."],
 [("Cette semaine", "une proposition avec un fait et un essai borné ; une réunion facilitée avec décisions."), ("Observateur", "« est-ce que je convaincs ou est-ce que j'insiste ? »"), ("Aller plus loin", "situations et attitudes, chapitre 10 : négociation, présentation hostile.")],
 "on n'impose pas une idée, on la rend facile à essayer.",
 [("Ton équipe refuse ton standard. Séquence ?", "Écouter ce qui gêne, reconnaître le coût, montrer une mesure d'ailleurs, proposer un essai d'un mois avec critère convenu, décider ensemble."),
  ("Question d'entretien : faire adopter une décision impopulaire ?", "Expliquer les critères, reconnaître ce que ça coûte, écouter les objections nouvelles, fixer une réévaluation datée, demander l'engagement plutôt que l'adhésion.")],
 ("Atelier influence", ["Une proposition menée jusqu'à un essai borné ; résultat noté.", "Une négociation préparée (intérêts, options, critères, alternative) et jouée avec un pair dur.", "Deux réunions facilitées : durée et décisions mesurées."],
  "Attendu : un essai obtenu ; une option non prévue au départ ; réunions plus courtes avec décisions attribuées.")),

palier(5, "Diriger", 's',
 ["Donner un cap, trancher avec des critères, confier des résultats, faire grandir, porter les conséquences.", "Déléguer un résultat, pas une méthode ; accepter une solution différente de la sienne.", "Mesure : décisions écrites et datées ; personnes qui ont pris plus de responsabilités."],
 ["Décider avec critères, date et réévaluation", "Déléguer un résultat sans reprendre derrière", "Fixer un objectif observable par personne et par trimestre"],
 [("Le problème", "on refait derrière, on décide tard ou par affinité, on garde les sujets intéressants"), ("Ce que ça change", "l'équipe avance sans toi ; tu as du temps pour ce que toi seul peux faire"), ("La mesure", "combien de personnes ont pris plus de responsabilités en un an")],
 (("Fait à la place, décide tard, garde les sujets intéressants", "un ADR par décision ; déléguer un sujet complet"), ("Tranche avec critères et date, délègue des tâches claires", "points de contrôle convenus"), ("Délègue des résultats, développe par objectifs observables, met les autres en avant", "l'équipe prend les succès, je prends les échecs"), ("L'équipe décide sans lui dans son cadre, forme d'autres leaders", "cadre écrit ; successeur préparé")),
 "déléguer un résultat avec ses critères et ses points de contrôle, puis ne pas reprendre.",
 ("Tu délègues ; le résultat n'est pas comme tu l'aurais fait ; tu le refais la nuit ; la personne ne prendra plus d'initiative.", "« Ce n'est pas comme je l'aurais fait, et ça tient les critères : bravo. » Tu ne corriges que ce qui viole un critère, et c'est la personne qui présente."),
 ["Décision : critères, deux options chiffrées, date, propriétaire, réévaluation ; écrite et expliquée.", "Délégation : résultat attendu, pourquoi, limites, points de contrôle, droit à l'erreur récupérable.", "Développement : un objectif observable par personne et par trimestre, des occasions (présenter, mener, décider), du feedback continu."],
 [("Cette semaine", "une décision en ADR ; un sujet délégué en entier et présenté par la personne."), ("Observateur", "« est-ce que je reprends derrière ? est-ce que je décide assez vite ? »"), ("Aller plus loin", "situations et attitudes, chapitres 4 à 6.")],
 "un chef qui fait à la place n'a pas d'équipe, il a des assistants.",
 [("La délégation ne donne pas ton résultat mais respecte les critères. Réaction ?", "Accepter et le dire ; reprendre tue la délégation. On ne corrige que ce qui viole un critère."),
  ("Question d'entretien : comment développes-tu les gens ?", "Objectifs observables, occasions réelles, feedback continu, droit à l'erreur, mise en avant ; et je compte ceux qui ont pris plus de responsabilités.")],
 ("Atelier direction", ["Trois décisions en ADR relues par les personnes concernées.", "Une délégation de résultat complet ; journal de ce que tu as eu envie de reprendre sans le faire.", "Plan trimestriel pour deux personnes avec objectifs vérifiables par un tiers."],
  "Attendu : ADR d'une page ; délégation menée au bout sans reprise ; objectifs observables.")),

palier(6, "Naviguer l'organisation", 's',
 ["Comprendre qui décide, qui influence, qui bloque ; gérer son manager ; se rendre visible par les résultats ; tenir une ligne éthique.", "Ce n'est pas de la politique au sens négatif : c'est de la lucidité et le respect des règles.", "Mesure : zéro surprise pour ton manager ; un allié activé ; un refus éthique écrit si nécessaire."],
 ["Cartographier les parties prenantes", "Rendre compte en cinq lignes chaque semaine", "Refuser par écrit ce qui franchit la ligne"],
 [("Le problème", "on ignore qui décide, on se plaint de « la politique », on surprend son manager"), ("Ce que ça change", "tes sujets aboutissent ; ton manager te défend ; tu dors tranquille"), ("La mesure", "surprises subies par ton manager ce mois-ci : zéro")],
 (("Ignore qui décide, surprend son manager", "carte des parties prenantes ; règle « pas de surprise »"), ("Rend compte (fait, risque, décision), connaît les alliés, montre ses résultats", "point hebdomadaire de cinq lignes"), ("Prépare les décisions avant les réunions, construit des coalitions, désaccords en privé", "entretiens bilatéraux avant les comités"), ("Influence les règles et la culture, protège les personnes, sait partir", "refus éthiques écrits")),
 "ton manager ne doit jamais apprendre une mauvaise nouvelle par quelqu'un d'autre.",
 ("Ton manager annonce une décision que tu trouves mauvaise ; tu le dis en réunion, puis tu freines en silence.", "En privé, une fois : « je pense que c'est une erreur pour ces raisons ». S'il maintient : « je l'applique et je la porterai ». Sauf question éthique : refus écrit avec la voie conforme."),
 ["Carte : décideurs, influenceurs, alliés, opposants ; l'intérêt de chacun ; ce qu'il attend de toi.", "Point hebdomadaire à ton manager : fait, risque, décision à prendre ; cinq lignes ; risques d'abord.", "Ligne éthique (mensonge, risque caché, sécurité ou loi contournée, personne lésée) : refus factuel, écrit, avec la solution conforme, en copie à qui de droit."],
 [("Cette semaine", "la carte d'un projet réel ; un point de cinq lignes à ton manager."), ("Observateur", "ton manager : « est-ce que je t'informe au bon moment ? »"), ("Aller plus loin", "situations et attitudes, chapitres 5, 8 et 11.")],
 "la visibilité vient du travail vu, pas du discours ; une carrière se construit aussi sur ses refus.",
 [("Comment te rends-tu visible sans te vanter ?", "Résultats montrés au bon rythme (point hebdomadaire, démonstration), en citant les autres ; documents et outils que les autres réutilisent."),
  ("Question d'entretien : un désaccord avec ta hiérarchie ?", "Dit une fois en privé avec des faits, décision appliquée loyalement ; ou, si c'était éthique, le refus écrit et ce qui en a découlé.")],
 ("Atelier organisation", ["Carte des parties prenantes d'un projet réel avec intérêts et attentes.", "Quatre points hebdomadaires de cinq lignes ; ce que ton manager en dit.", "Un refus éthique type en huit lignes sur une situation réelle ou plausible."],
  "Attendu : un allié à activer et un opposant à écouter ; un manager qui se dit mieux informé ; un refus sans émotion avec la solution conforme.")),

palier(7, "Tenir dans la durée", 'e',
 ["Rester calme en crise, se relever d'un échec, garder son équilibre, transmettre : ce qui distingue l'expert.", "Le stress se gère par la préparation, les rituels et les limites ; la crise par les rôles et le rythme ; l'échec par l'action suivante.", "Mesure : un protocole de crise suivi ; un post-mortem personnel ; un mentoré qui progresse."],
 ["Reconnaître le stress chez soi et les autres", "Tenir un protocole de crise", "Mentorer une personne"],
 [("Le problème", "on sur-réagit, on compense par les heures, on cache la fatigue, on prend l'échec pour une identité"), ("Ce que ça change", "tu durs ; ton calme devient celui de l'équipe ; tu formes la relève"), ("La mesure", "un protocole suivi en crise ; un mentoré avec un objectif atteint")],
 (("Sur-réagit, travaille tard, cache la fatigue", "limites horaires ; parler tôt à quelqu'un"), ("Rituels, sait dire la surcharge, sépare échec et valeur", "post-mortem personnel après un échec"), ("Calme et factuel en crise, tient les rôles, protège l'équipe, récupère", "protocole de crise ; débriefing"), ("Rend les autres calmes, anticipe, transmet, sait s'arrêter", "un mentoré par an ; règles d'équilibre non négociables")),
 "en crise : phrases courtes, rôles, un canal, un rythme ; on rétablit d'abord, on comprend après.",
 ("Incident majeur : tout le monde parle, tu plonges dans le code, tu réponds à chaque message, tu t'épuises, personne ne coordonne.", "« Léa les logs, Sam le rollback, moi la communication. Point à 14 h 15. On rétablit d'abord. » Après : repos, puis post-mortem sans blâme."),
 ["Protocole de crise personnel : rôles, canal, rythme, phrases, après ; une page.", "Signes de stress (irritabilité, erreurs, présence permanente, sommeil) : chez soi, en parler tôt ; chez un collègue, le dire en privé et alléger.", "Après un échec : chronologie, ta part, changement, action suivante datée ; ni héros ni victime."],
 [("Cette semaine", "ton protocole de crise et tes trois règles d'équilibre non négociables."), ("Observateur", "« m'as-tu vu calme ou fébrile pendant le dernier incident ? »"), ("Aller plus loin", "situations et attitudes, chapitres 7 et 9.")],
 "on mesure un professionnel dans la durée, pas dans une bonne semaine.",
 [("Un collègue s'épuise (présent à 7 h et 21 h, erreurs, irritable). Que fais-tu ?", "Lui en parler en privé sans diagnostiquer, alléger concrètement, l'orienter (manager, médecin du travail), suivre. Ne pas attendre que ça passe."),
  ("Question d'entretien : ton plus gros échec ?", "Un vrai, ta part, le changement durable, une situation récente où il t'a servi ; sans dramatiser.")],
 ("Atelier durée", ["Protocole de crise d'une page et règles d'équilibre ; suivis au moins une fois.", "Post-mortem personnel d'un échec réel.", "Un mentorat démarré : trois rendez-vous, objectif observable atteint."],
  "Attendu : protocole suivi sur un incident même petit ; post-mortem qui nomme ta part sans te flageller ; mentoré qui a atteint son objectif.")),

ch("Bilan : ta note, ton plan de douze semaines, tes histoires", 'e',
 ["Huit compétences, quatre niveaux : coche ton niveau, ta note est sauvegardée dans ce navigateur.", "Choisis les deux compétences les plus basses, trois situations réelles chacune, un observateur : c'est ton plan des douze prochaines semaines.", "Une histoire STAR par compétence, 90 secondes chacune : l'entretien comportemental est préparé."],
 ["Obtenir ta note par compétence", "Choisir deux compétences et six situations", "Préparer huit histoires STAR"],
 [("Auto-évaluation", ''.join(f'<div class="se-eval"><span>{n}</span><span class="opts">' + ''.join(f'<label><input type="radio" name="{k}" value="{v}"><span>{l}</span></label>' for v, l in ((1, "Débutant"), (2, "Confirmé"), (3, "Senior"), (4, "Expert"))) + '</span></div>' for k, n in [("se-connaitre", "Se connaître"), ("communiquer", "Communiquer"), ("fiable", "Être fiable"), ("collaborer", "Collaborer"), ("influencer", "Influencer"), ("diriger", "Diriger"), ("naviguer", "Naviguer l'organisation"), ("tenir", "Tenir dans la durée")]) + '<p id="se-score"></p><p class="legend">Fais aussi remplir cette grille par deux personnes de confiance : l\'écart entre ta note et la leur est l\'information la plus utile.</p>', None),
  ("Le plan des douze semaines", week([("Compétences", "les deux notes les plus basses (ou les deux écarts les plus grands avec tes observateurs)."), ("Situations", "trois par compétence, réelles, datées, avec la phrase ou le geste préparé."), ("Observateur", "une personne nommée, qui sait ce qu'elle doit regarder."), ("Mesure", "journal, retour de l'observateur, résultat ; grille refaite en fin de trimestre.")]), None),
  ("Huit histoires STAR", "Une par compétence : situation (deux phrases), tâche, actions avec les mots employés, résultat chiffré, leçon ; 90 secondes ; s'enregistrer. Le recruteur cherche des faits, ta part, des mots réels, un résultat, une leçon ; il rejette le héros, la victime et le vague.", None)],
 [("Ta note et celle de ton manager diffèrent de deux points sur « Collaborer ». Que fais-tu ?", "C'est le meilleur signal de l'exercice : demander deux exemples sans te défendre, choisir cette compétence pour le trimestre, convenir de ce qu'il observera."),
  ("Question d'entretien : sur quoi travailles-tu en ce moment ?", "Une compétence de la grille, le palier visé, la pratique en cours, un progrès récent : la réponse la plus crédible à « ton défaut ».")],
 ("Plan de progression", ["Grille remplie par toi et deux personnes ; écarts identifiés.", "Deux compétences, six situations datées, un observateur nommé, une mesure.", "Huit histoires STAR écrites, enregistrées, retravaillées une fois ; grille refaite dans douze semaines."],
  "Attendu : un écart d'au moins deux points choisi ; six situations dans l'agenda ; huit histoires de 90 secondes enregistrées.")),
]

d = sys.argv[1]
page('cours-09-savoir-etre-de-zero-a-expert.html', 'Savoir-être de zéro à expert : la progression par paliers', "Un mode d'emploi, huit paliers et un bilan. Chaque palier tient en dix minutes : pourquoi ça compte, l'échelle Débutant → Confirmé → Senior → Expert, le geste clé, une situation avant/après, trois pratiques à cocher et l'habitude de la semaine. Le bilan donne ta note (sauvegardée dans ton navigateur) et ton plan de douze semaines. À lire avec le cours « situations et attitudes », qui donne les mots à dire par rôle.", "≈ 12 semaines à raison de dix minutes de lecture et une pratique par semaine · aucun prérequis.", SE, [('cours-10-savoir-etre-situations-et-attitudes.html', 'Situations et attitudes'), ('devops-11-fiches-entretien.html', 'Fiches entretien')])
p = pathlib.Path(d) / 'cours-09-savoir-etre-de-zero-a-expert.html'; s = p.read_text()
if 'se-design' not in s: s = s.replace('</head>', CSS + '\n</head>', 1).replace('</body>', JS + '\n</body>', 1); p.write_text(s)
