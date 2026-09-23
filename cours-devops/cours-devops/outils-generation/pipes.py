import re, pathlib, json, html as H

p = pathlib.Path('/mnt/user-data/outputs/devops-niveau-0-fondations.html')
S = p.read_text()
assert 'class="pipe"' not in S, 'déjà fait'

# ---- retirer l'ancienne animation SVG du 2.4 (remplacée par le composant)
i = S.index('<figure class="anim" id="anim-pipe">'); j = S.index('</figure>', i); k = S.index('</script>', j) + len('</script>\n')
S = S[:i] + S[k:]
assert 'anim-pipe' not in S

CSS = """
/* ============ Pipelines pas à pas ============ */
.pipe{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);padding:.8rem;margin:1rem 0}
.pipe .ctl{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin-bottom:.6rem}
.pipe .ctl button{font:inherit;font-size:.82rem;font-weight:700;border:1px solid var(--accent);background:var(--paper);color:var(--accent-ink);border-radius:999px;padding:.25rem .75rem;cursor:pointer;min-height:32px}
.pipe .ctl button.primary{background:var(--accent);color:#fff}
.pipe .ctl .st{font-size:.82rem;color:var(--muted);margin-left:auto}
.pipe .q{font-size:.9rem;margin:0 0 .5rem;font-weight:700}
.pipe .cmd{font-family:"JetBrains Mono",monospace;font-size:.8rem;background:var(--code-bg);color:var(--code-ink);border-radius:8px;padding:.55rem .8rem;white-space:pre-wrap;word-break:break-word;line-height:1.5}
.pipe .cmd b{font-weight:400;background:rgba(111,163,245,.35);border-radius:3px;padding:0 .15em}
.pipe .cols{display:flex;gap:6px;margin-top:.6rem;overflow-x:auto;padding-bottom:.3rem;-webkit-overflow-scrolling:touch}
.pipe .col{flex:1 1 0;min-width:150px;border:1.5px solid var(--line-strong);border-radius:8px;background:var(--paper);padding:.4rem .45rem;opacity:.35;transition:opacity .3s,background .3s,border-color .3s;position:relative}
.pipe .col.on{opacity:1}
.pipe .col.cur{opacity:1;background:var(--accent-soft);border-color:var(--accent)}
.pipe .col h5{margin:.2rem 0 .35rem;font-size:.76rem;text-align:center;font-family:"JetBrains Mono",monospace;font-weight:700;word-break:break-word;line-height:1.25}
.pipe .col .n{position:absolute;top:-.55rem;left:.45rem;font-size:.66rem;font-weight:700;background:var(--ink);color:var(--paper);border-radius:999px;padding:0 .45rem;line-height:1.2rem}
.pipe .col ol{list-style:none;margin:0;padding:0;font-family:"JetBrains Mono",monospace;font-size:.72rem;line-height:1.55}
.pipe .col li{white-space:normal;word-break:break-word;border-top:1px dashed var(--line);padding:.12rem 0;line-height:1.4}
.pipe .col li:first-child{border-top:0}
.pipe .col li.hl{background:var(--tp-soft)}
.pipe .col .empty{color:var(--muted);text-align:center;font-family:inherit;font-size:.78rem;padding:.6rem 0}
.pipe .col .cnt{font-family:inherit;font-size:.7rem;color:var(--muted);text-align:right;margin-top:.3rem}
.pipe .col:not(:last-child)::after{content:"›";position:absolute;right:-7px;top:45%;font-size:1rem;color:var(--muted);background:var(--paper);line-height:1}
.pipe .expl{font-size:.82rem;color:var(--muted);min-height:2.4em;margin:.5rem 0 0}
.pipe figcaption{font-size:.85rem;color:var(--muted);margin-top:.5rem;text-align:center}
@media print{.pipe .ctl{display:none} .pipe .col{opacity:1}}
</style>"""

JS = r"""
<script>
(function(){
  function esc(t){ return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;'); }
  document.querySelectorAll('figure.pipe').forEach(function(fig){
    var data=JSON.parse(fig.querySelector('script[type="application/json"]').textContent);
    var cols=fig.querySelector('.cols'), st=fig.querySelector('.st'), cmd=fig.querySelector('.cmd'), expl=fig.querySelector('.expl');
    var shown=1, timer=null, N=data.stages.length;
    function draw(){
      cols.innerHTML=data.stages.map(function(s,k){
        var vis=k<shown, cur=k===shown-1;
        var body='';
        if(vis){ body = s.lines.length ? '<ol>'+s.lines.slice(0,10).map(function(l){ var hl=(s.hl||[]).indexOf(l)>=0; return '<li'+(hl?' class="hl"':'')+' title="'+esc(l)+'">'+esc(l)+'</li>'; }).join('')+(s.lines.length>10?'<li>… ('+(s.lines.length-10)+' de plus)</li>':'')+'</ol><div class="cnt">'+s.lines.length+' ligne'+(s.lines.length>1?'s':'')+'</div>' : '<div class="empty">(vide)</div>'; }
        else body='<div class="empty">…</div>';
        return '<div class="col'+(vis?' on':'')+(cur?' cur':'')+'"><span class="n">'+k+'</span><h5 title="'+esc(s.title)+'">'+esc(s.title)+'</h5>'+body+'</div>';
      }).join('');
      var parts=data.cmd; cmd.innerHTML=parts.map(function(pt,k){ return (k===shown-1&&k>0)?'<b>'+esc(pt)+'</b>':esc(pt); }).join(data.sep||' | ');
      st.textContent = shown>=N ? ('terminé : '+data.done) : (shown===1?'entrée':'étape '+(shown-1)+' / '+(N-1));
      expl.textContent = data.stages[shown-1].why||'';
    }
    fig.querySelector('[data-play]').addEventListener('click',function(){ clearInterval(timer); shown=1; draw(); timer=setInterval(function(){ shown++; draw(); if(shown>=N) clearInterval(timer); }, 1100); });
    fig.querySelector('[data-next]').addEventListener('click',function(){ clearInterval(timer); if(shown<N){ shown++; draw(); } });
    fig.querySelector('[data-reset]').addEventListener('click',function(){ clearInterval(timer); shown=1; draw(); });
    draw();
  });
})();
</script>
"""

def pipe(ident, question, cmd_parts, stages, done, caption, sep=' | '):
    data = {"cmd": cmd_parts, "sep": sep, "stages": stages, "done": done}
    return (f'<figure class="pipe" id="{ident}">'
            f'<div class="ctl"><button type="button" class="primary" data-play>Exécuter pas à pas</button><button type="button" data-next>Étape suivante</button><button type="button" data-reset>Réinitialiser</button><span class="st"></span></div>'
            f'<p class="q">{H.escape(question)}</p><div class="cmd"></div><div class="cols"></div><p class="expl"></p>'
            f'<script type="application/json">{json.dumps(data, ensure_ascii=False)}</script>'
            f'<figcaption>{caption}</figcaption></figure>')

P = []

# ---------- 2.3 : le processus qui mange la mémoire
ps = ["  PID COMMAND        %MEM", " 1042 java           41.2", " 2310 postgres       12.5", "  871 node            6.1", " 1930 nginx           0.8", " 2400 python3         3.4", "  512 sshd            0.2", " 2555 redis-server    1.9"]
srt = [" 1042 java           41.2", " 2310 postgres       12.5", "  871 node            6.1", " 2400 python3         3.4", " 2555 redis-server    1.9", " 1930 nginx           0.8", "  512 sshd            0.2"]
P.append(("2.3", pipe("pipe-ps", "Quel processus mange la mémoire ?",
    ["ps -eo pid,comm,%mem", "sort -k3 -rn", "head -3"],
    [{"title":"ps -eo …","lines":ps,"why":"ps liste tous les processus avec les colonnes demandées : PID, commande, part de mémoire."},
     {"title":"sort -k3 -rn","lines":srt,"why":"sort trie sur la 3e colonne (-k3), en numérique (-n) et décroissant (-r). L'en-tête, non numérique, passe en bas."},
     {"title":"head -3","lines":srt[:3],"hl":[srt[0]],"why":"head garde les trois premières lignes : le suspect est en tête. On regarde ensuite ses logs avant de le tuer."}],
    "java, PID 1042, 41 % de la mémoire",
    "Trois commandes, une question : qui consomme ? ps produit, sort ordonne, head coupe. Ensuite seulement on décide (logs, kill -15, jamais kill -9 d'abord).")))

# ---------- 3.4 : quels ports écoutent
ssl = ["Netid State  Local Address:Port  Process", "tcp   LISTEN 0.0.0.0:22          sshd", "tcp   LISTEN 127.0.0.1:5432      postgres", "tcp   LISTEN 0.0.0.0:8080        java", "tcp   LISTEN 0.0.0.0:443         nginx", "udp   UNCONN 0.0.0.0:68          dhclient", "tcp   ESTAB  10.0.1.5:22         sshd", "tcp   LISTEN 127.0.0.1:6379      redis"]
lst = [l for l in ssl if "LISTEN" in l]
addrs = ["0.0.0.0:22", "127.0.0.1:5432", "0.0.0.0:8080", "0.0.0.0:443", "127.0.0.1:6379"]
P.append(("3.4", pipe("pipe-ss", "Qu'est-ce qui écoute sur cette machine, et sur quelle adresse ?",
    ["ss -tulpn", "grep LISTEN", "awk '{print $4}'", "sort"],
    [{"title":"ss -tulpn","lines":ssl,"why":"ss montre les sockets : TCP et UDP (-tu), en écoute (-l), avec le processus (-p) et sans résolution de noms (-n)."},
     {"title":"grep LISTEN","lines":lst,"why":"grep ne garde que les lignes qui contiennent LISTEN : les connexions établies et l'UDP disparaissent."},
     {"title":"awk '{print $4}'","lines":addrs,"why":"awk découpe chaque ligne en colonnes séparées par des blancs et n'imprime que la 4e : adresse:port."},
     {"title":"sort","lines":sorted(addrs),"hl":["0.0.0.0:8080"],"why":"Trié, on lit d'un coup : 0.0.0.0 = ouvert à tout le monde, 127.0.0.1 = local seulement. 8080 exposé sur toutes les interfaces mérite une question."}],
    "5 ports en écoute, dont 8080 ouvert sur toutes les interfaces",
    "Le port 5432 écoute en 127.0.0.1 : inaccessible de l'extérieur, c'est voulu. Le 8080 en 0.0.0.0 devrait être derrière le reverse proxy. Cette chaîne est le premier réflexe d'un audit.")))

# ---------- 4.2 : codes HTTP d'un access.log
acc = ['10.0.1.7 - - [22/Sep/2026:10:01:02] "GET /api/incidents HTTP/1.1" 200 512', '10.0.1.9 - - [22/Sep/2026:10:01:05] "POST /api/login HTTP/1.1" 401 88', '10.0.1.7 - - [22/Sep/2026:10:01:08] "GET /api/incidents/42 HTTP/1.1" 200 1204', '10.0.2.3 - - [22/Sep/2026:10:01:11] "GET /api/zones HTTP/1.1" 500 62', '10.0.1.9 - - [22/Sep/2026:10:01:14] "POST /api/login HTTP/1.1" 401 88', '10.0.1.7 - - [22/Sep/2026:10:01:20] "GET /health HTTP/1.1" 200 15', '10.0.2.3 - - [22/Sep/2026:10:01:22] "GET /api/zones HTTP/1.1" 500 62', '10.0.3.1 - - [22/Sep/2026:10:01:30] "GET /admin HTTP/1.1" 404 120', '10.0.1.9 - - [22/Sep/2026:10:01:33] "POST /api/login HTTP/1.1" 401 88']
codes = [l.split('" ')[1].split(' ')[0] for l in acc]
from collections import Counter
cnt = Counter(codes)
uniqc = [f"{v:7d} {k}" for k, v in sorted(cnt.items())]
uniqr = [f"{v:7d} {k}" for k, v in sorted(cnt.items(), key=lambda kv: -kv[1])]
P.append(("4.2", pipe("pipe-http", "Quels codes HTTP renvoie l'API, et combien de fois ?",
    ["awk '{print $9}' access.log", "sort", "uniq -c", "sort -rn"],
    [{"title":"awk '{print $9}'","lines":codes,"why":"Dans un access.log nginx, le code de statut est la 9e colonne : awk l'extrait ligne par ligne."},
     {"title":"sort","lines":sorted(codes),"why":"uniq ne compte que des lignes consécutives identiques : il faut trier avant, sinon 401 et 401 séparés seraient comptés deux fois."},
     {"title":"uniq -c","lines":uniqc,"why":"uniq -c fusionne les doublons et met le compte devant."},
     {"title":"sort -rn","lines":uniqr,"hl":[uniqr[0]],"why":"Tri numérique décroissant sur le compte : le code le plus fréquent en tête. Trois 401 sur /login et deux 500 sur /zones : deux enquêtes à ouvrir."}],
    "200 ×3, 401 ×3, 500 ×2, 404 ×1",
    "sort | uniq -c | sort -rn est le motif universel « compter et classer ». Il vaut pour les codes HTTP, les adresses IP, les commandes Git, les erreurs de logs.")))

# ---------- 4.4 (Python / jq) : incidents P1 par zone
inc = ['{"id":1,"zone":"nord","priority":"P1","status":"open"}', '{"id":2,"zone":"sud","priority":"P3","status":"closed"}', '{"id":3,"zone":"nord","priority":"P1","status":"open"}', '{"id":4,"zone":"est","priority":"P2","status":"open"}', '{"id":5,"zone":"est","priority":"P1","status":"closed"}', '{"id":6,"zone":"nord","priority":"P2","status":"open"}', '{"id":7,"zone":"sud","priority":"P1","status":"open"}']
p1 = [l for l in inc if '"P1"' in l]
zones = ["nord", "nord", "est", "sud"]
P.append(("4.4", pipe("pipe-jq", "Combien d'incidents prioritaires par zone, depuis l'API ?",
    ["curl -s http://api:8080/api/incidents", "jq -c '.[]'", "jq -c 'select(.priority==\"P1\")'", "jq -r '.zone'", "sort | uniq -c"],
    [{"title":"curl -s","lines":['[', ' {"id":1,"zone":"nord",…},', ' {"id":2,"zone":"sud",…},', ' …', ']'],"why":"curl récupère le JSON ; -s tait la barre de progression pour ne laisser que les données dans le pipe."},
     {"title":"jq '.[]'","lines":inc,"why":"jq déplie le tableau : un objet par ligne (-c compact), la matière première des étapes suivantes."},
     {"title":"select(P1)","lines":p1,"why":"select garde les objets dont la priorité est P1 : un filtre, comme grep, mais qui comprend le JSON."},
     {"title":"jq -r '.zone'","lines":zones,"why":"On ne garde que le champ zone, en texte brut (-r) : à partir d'ici on est revenu dans le monde des lignes."},
     {"title":"sort | uniq -c","lines":["      1 est", "      2 nord", "      1 sud"],"hl":["      2 nord"],"why":"Le motif compter-et-classer, encore lui. La zone nord concentre les incidents prioritaires."}],
    "nord : 2 incidents P1",
    "jq est le awk du JSON : on filtre, on extrait, puis on revient aux outils texte. Au-delà de trois étapes ou d'une logique métier, on passe à Python (requests + collections.Counter).")))

# ---------- 5.2 : qui commite le plus
authors = ["Kaï", "Mika", "Kaï", "Kaï", "Sam", "Mika", "Kaï", "Mika"]
ac = Counter(authors)
P.append(("5.2", pipe("pipe-git", "Qui commite le plus sur ce dépôt depuis un mois ?",
    ["git log --since='1 month' --format=%an", "sort", "uniq -c", "sort -rn"],
    [{"title":"git log --format=%an","lines":authors,"why":"--format=%an n'imprime que le nom de l'auteur, un par commit, dans l'ordre chronologique inverse."},
     {"title":"sort","lines":sorted(authors),"why":"Trié pour que uniq puisse fusionner les doublons consécutifs."},
     {"title":"uniq -c","lines":[f"{v:7d} {k}" for k, v in sorted(ac.items())],"why":"Un compte par auteur."},
     {"title":"sort -rn","lines":[f"{v:7d} {k}" for k, v in sorted(ac.items(), key=lambda kv: -kv[1])],"hl":[f"{ac['Kaï']:7d} Kaï"],"why":"Classement. git shortlog -sn fait la même chose en une commande : connaître le pipeline permet de comprendre le raccourci."}],
    "Kaï : 4 commits, Mika : 3, Sam : 1",
    "Un dépôt Git est une base de données : git log avec --format produit des lignes, et les outils texte font le reste. Même motif pour les fichiers les plus modifiés (--name-only) ou les commits par jour (--format=%ad).")))

# ---------- 6.2 : l'ordre logique d'une requête SQL
rows = ["1  nord  open    P1", "2  sud   closed  P3", "3  nord  open    P1", "4  est   open    P2", "5  est   closed  P1", "6  nord  open    P2", "7  sud   open    P1", "8  est   open    P3"]
where = [r for r in rows if " open " in r]
grp = ["nord  3", "est   2", "sud   1"]
having = ["nord  3", "est   2"]
P.append(("6.2", pipe("pipe-sql", "Dans quelles zones y a-t-il plus d'un incident ouvert ?",
    ["FROM incidents", "WHERE status = 'open'", "GROUP BY zone → COUNT(*)", "HAVING COUNT(*) > 1", "ORDER BY n DESC", "LIMIT 1"],
    [{"title":"FROM incidents","lines":rows,"why":"Le moteur part de la table entière (ou de l'index, s'il y en a un sur status). C'est l'ordre logique d'évaluation, pas l'ordre d'écriture."},
     {"title":"WHERE status='open'","lines":where,"why":"WHERE filtre les lignes avant tout regroupement : c'est ici qu'un index sur status évite le Seq Scan."},
     {"title":"GROUP BY zone","lines":grp,"why":"Les lignes sont regroupées par zone et chaque groupe est compté : COUNT(*) devient une colonne n."},
     {"title":"HAVING n > 1","lines":having,"why":"HAVING filtre les groupes, après l'agrégation ; WHERE ne peut pas, il ne connaît pas encore les comptes."},
     {"title":"ORDER BY n DESC","lines":having,"why":"Le tri vient après : sur trois lignes, il ne coûte rien ; sur un million, il justifie un index."},
     {"title":"LIMIT 1","lines":[having[0]],"hl":[having[0]],"why":"LIMIT est appliqué en dernier. Résultat : la zone nord, trois incidents ouverts."}],
    "nord, 3 incidents ouverts",
    "SELECT s'écrit en premier mais s'exécute presque en dernier : FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT. Comprendre cet ordre explique pourquoi on ne peut pas mettre un alias de SELECT dans WHERE, et où un index agit.",
    sep='  →  ')))

# ---------- 2.4 : l'original, reconstruit avec le composant
lines = ["10:01 INFO api demarrage", "10:02 ERROR db connexion refusee", "10:02 ERROR api timeout amont", "10:03 WARN api lenteur", "10:03 ERROR db connexion refusee", "10:04 ERROR api timeout amont", "10:04 INFO web ok", "10:05 ERROR db connexion refusee"]
err = [l for l in lines if "ERROR" in l]; svc = [l.split(' ')[2] for l in err]; sc = Counter(svc)
P.append(("2.4", pipe("pipe-log", "Quel service produit le plus d'erreurs ?",
    ["grep ERROR app.log", "cut -d' ' -f3", "sort", "uniq -c", "sort -rn"],
    [{"title":"app.log","lines":lines,"why":"Le fichier brut : tout niveau, tout service."},
     {"title":"grep ERROR","lines":err,"why":"grep ne garde que les lignes contenant ERROR."},
     {"title":"cut -d' ' -f3","lines":svc,"why":"cut découpe sur l'espace et garde le 3e champ : le nom du service."},
     {"title":"sort","lines":sorted(svc),"why":"Trié pour uniq."},
     {"title":"uniq -c","lines":[f"{v:7d} {k}" for k, v in sorted(sc.items())],"why":"Compte par service."},
     {"title":"sort -rn","lines":[f"{v:7d} {k}" for k, v in sorted(sc.items(), key=lambda kv: -kv[1])],"hl":[f"{sc['db']:7d} db"],"why":"Classement décroissant : db en tête."}],
    "db produit le plus d'erreurs",
    "Chaque commande lit ce que la précédente écrit et ne fait qu'une chose : filtrer, découper, trier, compter. Le résultat est une réponse à une question, pas un fichier à lire.")))

# ---------- insertion : après le titre de section et ce qui le suit immédiatement (planche, schéma, animation)
S = S.replace('</style>', CSS, 1)
for sec, block in P:
    m = re.search(r'<h3>' + re.escape(sec) + r' [^<]*(?:<span class="badge[^<]*</span>)?</h3>', S); assert m, sec
    j = m.end()
    while True:
        m2 = re.match(r'\n(<figure class="fig(?: manga)?">.*?</figure>|<figure class="anim"[^>]*>.*?</figure>\n<script>.*?</script>)', S[j:], flags=re.S)
        if not m2: break
        j += m2.end()
    S = S[:j] + '\n' + block + S[j:]
S = S.replace('</body>', JS + '</body>', 1)
p.write_text(S); print('pipelines :', S.count('class="pipe"'))

ip = pathlib.Path('/mnt/user-data/outputs/devops-parcours-complet.html'); t = ip.read_text()
old = [l for l in t.split('\n') if '<strong>Animations</strong>' in l]
if old and 'Pipelines pas à pas' not in t:
    t = t.replace(old[0], old[0] + '\n<li><strong>Pipelines pas à pas</strong> (niveau 0, un par chapitre) : une chaîne de commandes se déroule colonne par colonne, avec les données transformées à chaque étape et une phrase qui explique pourquoi : processus gourmand (ps | sort | head), ports en écoute (ss | grep | awk), codes HTTP d\'un access.log, jq sur une API, qui commite le plus, l\'ordre logique d\'une requête SQL, les erreurs par service.</li>')
    ip.write_text(t); print('index ok')
