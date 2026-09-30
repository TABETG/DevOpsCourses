import re, pathlib, html as H

out = pathlib.Path('/mnt/user-data/outputs')
head = re.sub(r'<title>[^<]*</title>', '<title>Correction du TP 2 — Un serveur web sous Ubuntu, à la main</title>', re.search(r'^.*?</head>', (out/'devops-00-fondations.html').read_text(), flags=re.S).group(0))
extra = """
.pagenav{display:flex;flex-wrap:wrap;gap:.6rem;margin-bottom:1rem;font-size:.9rem}
.pagenav a{color:#fff;text-decoration:none;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);padding:.3rem .75rem;border-radius:6px}
.pagenav a:hover{background:rgba(255,255,255,.2);color:#fff}
.footnav{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin-top:2rem;padding-top:1.2rem;border-top:1px solid var(--line)}
.footnav a{text-decoration:none;font-weight:700;background:var(--paper);border:1px solid var(--line);padding:.6rem 1rem;border-radius:var(--radius)}
.out{font-family:"JetBrains Mono",monospace;font-size:.8rem;background:var(--bg);border:1px dashed var(--line-strong);border-radius:8px;padding:.6rem .8rem;white-space:pre-wrap;word-break:break-word;margin:.3rem 0 1rem}
.out::before{content:"résultat attendu";display:block;font-family:"Atkinson Hyperlegible",system-ui,sans-serif;font-size:.72rem;font-weight:700;color:var(--muted);margin-bottom:.3rem;letter-spacing:.04em;text-transform:uppercase}
body{padding-bottom:2rem}
@media print{.pagenav,.footnav{display:none}}
</style>"""
head = head.replace('</style>', extra, 1)

body = r'''<body>
<header class="hero"><div class="in">
<div class="pagenav"><a href="../devops-00-fondations.html#c2">← Retour au chapitre 2</a><a href="../index.html">Accueil du parcours</a></div>
<div class="level">Correction type — Travail pratique 2</div>
<h1>Un serveur web sous Ubuntu, à la main</h1>
<p class="lead">Chaque commande, son résultat attendu, et pourquoi. Le but n'est pas de copier : c'est de comprendre chaque ligne du <code>tp2.md</code> que tu vas écrire, et surtout la dernière phrase sur systemd.</p>
</div></header>
<div class="single">

<article><div class="chaphead"><span class="chapnum">Étape 0</span><span class="badge tag-important">Important</span></div>
<h2>Lancer le conteneur, depuis Git Bash</h2>
<pre><code>winpty docker run -it --rm -p 8080:80 --name tp2 ubuntu:24.04 bash</code></pre>
<div class="out">root@3f1a9c2e7b5d:/#</div>
<ul>
<li><code>winpty</code> : sans lui, Git Bash n'attache pas correctement le terminal interactif (le prompt ne s'affiche pas ou le clavier ne répond pas).</li>
<li><code>-p 8080:80</code> : le port 80 du conteneur est publié sur le 8080 de ton poste ; c'est ce qui permettra le curl depuis Git Bash.</li>
<li><code>--rm</code> : le conteneur disparaît à la sortie ; tout ce que tu fais est perdu, c'est voulu, c'est un labo.</li>
<li>Tu es <code>root</code> dans le conteneur : ce n'est pas root sur ton poste, c'est root dans un espace isolé.</li>
</ul>
<div class="note">Il te faut <strong>deux terminaux</strong> Git Bash : un pour le conteneur, un pour les curl depuis l'extérieur. Dans le second, <code>docker exec -it tp2 bash</code> te redonne un shell dans le même conteneur si besoin.</div>
</article>

<article><div class="chaphead"><span class="chapnum">Étape 1</span><span class="badge tag-coeur">Par cœur</span></div>
<h2>Installer nginx et les outils de diagnostic</h2>
<pre><code>apt update &amp;&amp; apt install -y nginx procps iproute2 curl</code></pre>
<div class="out">Get:1 http://archive.ubuntu.com/ubuntu noble InRelease [256 kB]
…
Setting up nginx (1.24.0-2ubuntu7) …
Processing triggers for libc-bin …</div>
<ul>
<li><code>apt update</code> rafraîchit la liste des paquets : l'image Ubuntu est livrée sans index, <code>apt install</code> échouerait avant.</li>
<li><code>procps</code> (ps, top, free) et <code>iproute2</code> (ss, ip) ne sont pas dans l'image minimale : sans eux, l'étape 6 échoue avec « command not found ». <code>curl</code> non plus.</li>
<li>Aucun <code>sudo</code> : tu es déjà root, et sudo n'est pas installé.</li>
</ul>
</article>

<article><div class="chaphead"><span class="chapnum">Étape 2</span><span class="badge tag-coeur">Par cœur</span></div>
<h2>Créer webadmin sans sudo, propriétaire du site</h2>
<pre><code>useradd -m -s /bin/bash webadmin
id webadmin
chown -R webadmin:webadmin /var/www/html
ls -ld /var/www/html</code></pre>
<div class="out">uid=1000(webadmin) gid=1000(webadmin) groups=1000(webadmin)
drwxr-xr-x 2 webadmin webadmin 4096 Sep 22 10:12 /var/www/html</div>
<ul>
<li><code>-m</code> crée le répertoire personnel, <code>-s /bin/bash</code> donne un vrai shell (sinon <code>su -</code> tomberait sur <code>/bin/sh</code> ou rien).</li>
<li>Pas de <code>-G sudo</code>, et sudo n'existe pas : webadmin ne peut rien faire hors de ses fichiers. Droits minimaux, chapitre 2.2.</li>
<li><code>chown -R</code> transfère la propriété du répertoire et de son contenu ; <code>ls -ld</code> (le <code>-d</code> montre le répertoire lui-même, pas son contenu) le confirme : <code>rwx</code> pour le propriétaire, <code>r-x</code> pour les autres, ce qui permet à nginx (utilisateur <code>www-data</code>) de lire.</li>
</ul>
</article>

<article><div class="chaphead"><span class="chapnum">Étape 3</span><span class="badge tag-important">Important</span></div>
<h2>Remplacer la page, en tant que webadmin</h2>
<pre><code>su - webadmin
echo '&lt;h1&gt;Bonjour DevOps&lt;/h1&gt;' &gt; /var/www/html/index.html
cat /var/www/html/index.html
exit</code></pre>
<div class="out">webadmin@3f1a9c2e7b5d:~$ echo … &gt; /var/www/html/index.html
&lt;h1&gt;Bonjour DevOps&lt;/h1&gt;
webadmin@3f1a9c2e7b5d:~$ exit
root@3f1a9c2e7b5d:/#</div>
<ul>
<li><code>su -</code> (avec le tiret) charge l'environnement de webadmin : répertoire personnel, variables, shell.</li>
<li>Le fichier par défaut s'appelle <code>index.nginx-debian.html</code> ; nginx sert <code>index.html</code> en priorité s'il existe, donc pas besoin de le supprimer. Vérifie avec <code>ls /var/www/html</code>.</li>
<li>Essaie <code>echo test &gt; /etc/nginx/nginx.conf</code> en tant que webadmin : <em>Permission denied</em>. C'est le comportement attendu, et la raison d'être de cet utilisateur.</li>
</ul>
</article>

<article><div class="chaphead"><span class="chapnum">Étape 4</span><span class="badge tag-coeur">Par cœur</span></div>
<h2>Lancer nginx, sans systemd</h2>
<pre><code>systemctl start nginx</code></pre>
<div class="out">System has not been booted with systemd as init system (PID 1). Can't operate.
Failed to connect to bus: Host is down</div>
<pre><code>nginx
ps -ef | grep [n]ginx</code></pre>
<div class="out">root        412      1  0 10:15 ?  00:00:00 nginx: master process nginx
www-data    413    412  0 10:15 ?  00:00:00 nginx: worker process</div>
<p>Puis, <strong>depuis Git Bash</strong> (second terminal) :</p>
<pre><code>curl http://localhost:8080</code></pre>
<div class="out">&lt;h1&gt;Bonjour DevOps&lt;/h1&gt;</div>
<ul>
<li><strong>Pourquoi systemd ne tourne pas</strong> : dans un conteneur, le PID 1 est la commande lancée (ici <code>bash</code>), pas <code>systemd</code>. systemd est un système d'init complet (démons, cgroups, journal) qui suppose être PID 1 d'une machine entière ; un conteneur ne lance qu'un processus et ses enfants. C'est la phrase attendue dans <code>tp2.md</code>.</li>
<li><code>nginx</code> seul se met en arrière-plan (démon) : le processus maître appartient à root, les workers à <code>www-data</code>. <code>service nginx start</code> fonctionne aussi : c'est un script d'init classique, qui ne passe pas par systemd.</li>
<li>Le <code>grep [n]ginx</code> : l'astuce des crochets évite que grep se trouve lui-même dans la liste.</li>
<li>Si le curl échoue depuis Git Bash : vérifier que le conteneur a bien été lancé avec <code>-p 8080:80</code>, et que nginx tourne (<code>ss -tulpn</code> dans le conteneur, étape 6).</li>
</ul>
</article>

<article><div class="chaphead"><span class="chapnum">Étape 5</span><span class="badge tag-coeur">Par cœur</span></div>
<h2>50 requêtes, puis compter les codes HTTP</h2>
<p>Depuis Git Bash :</p>
<pre><code>for i in $(seq 50); do curl -s localhost:8080 &gt; /dev/null; done
curl -s localhost:8080/inexistant &gt; /dev/null     # pour avoir au moins un 404</code></pre>
<p>Dans le conteneur :</p>
<pre><code>tail -2 /var/log/nginx/access.log
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn</code></pre>
<div class="out">172.17.0.1 - - [22/Sep/2026:10:18:41 +0000] "GET / HTTP/1.1" 200 23 "-" "curl/8.7.1"
172.17.0.1 - - [22/Sep/2026:10:18:52 +0000] "GET /inexistant HTTP/1.1" 404 162 "-" "curl/8.7.1"
     51 200
      1 404</div>
<ul>
<li>51 et non 50 : le curl de l'étape 4 compte aussi. Si tu obtiens 50, tu avais oublié l'étape 4 ou nginx a redémarré entre les deux.</li>
<li><code>172.17.0.1</code> : l'adresse de ton poste vue depuis le réseau Docker (la passerelle du réseau par défaut), pas 127.0.0.1.</li>
<li>Le pipeline : la 9e colonne est le code ; <code>sort</code> avant <code>uniq -c</code> parce que uniq ne fusionne que des lignes consécutives ; <code>sort -rn</code> classe par fréquence. C'est le pipeline pas à pas du chapitre 4.2.</li>
<li>Variante en une ligne avec cut : <code>cut -d' ' -f9</code> ; variante qui compte par chemin : <code>awk '{print $7}'</code>.</li>
</ul>
</article>

<article><div class="chaphead"><span class="chapnum">Étape 6</span><span class="badge tag-coeur">Par cœur</span></div>
<h2>Qui écoute sur le port 80, et l'arrêter proprement</h2>
<pre><code>ss -tulpn</code></pre>
<div class="out">Netid State  Recv-Q Send-Q Local Address:Port Peer Address:Port Process
tcp   LISTEN 0      511          0.0.0.0:80        0.0.0.0:*     users:(("nginx",pid=413,fd=6),("nginx",pid=412,fd=6))
tcp   LISTEN 0      511             [::]:80           [::]:*     users:(("nginx",pid=413,fd=7),("nginx",pid=412,fd=7))</div>
<pre><code>kill -15 412          # le maître, pas le worker ; -15 = SIGTERM, la valeur par défaut de kill
sleep 1
ss -tulpn ; ps -ef | grep [n]ginx</code></pre>
<div class="out">Netid State  Recv-Q Send-Q Local Address:Port Peer Address:Port Process
(plus rien sur :80, plus aucun processus nginx)</div>
<ul>
<li><code>ss -tulpn</code> : TCP et UDP, en écoute, avec le processus, sans résolution de noms. <code>0.0.0.0:80</code> = toutes les interfaces ; dans le conteneur c'est normal, c'est Docker qui filtre à l'extérieur.</li>
<li>On tue le <strong>maître</strong> (PID 412, parent) : il arrête ses workers proprement. Tuer un worker seul, le maître en relance un.</li>
<li>SIGTERM (15) laisse nginx finir les requêtes en cours et fermer ses sockets ; SIGKILL (9) ne laisse rien faire et ne s'utilise qu'après un SIGTERM sans effet. <code>nginx -s quit</code> est l'équivalent « propre » côté nginx.</li>
<li>Vérification depuis Git Bash : <code>curl localhost:8080</code> → <em>curl: (56) Recv failure</em> ou <em>Empty reply</em> : le port est publié par Docker mais plus personne ne répond derrière.</li>
</ul>
</article>

<article><div class="chaphead"><span class="chapnum">Livrable</span><span class="badge tag-important">Important</span></div>
<h2>tp2.md, version courte attendue</h2>
<pre><code># TP 2 — Serveur web Ubuntu à la main (conteneur ubuntu:24.04)

| Étape | Commande | Résultat |
|---|---|---|
| Installation | apt update &amp;&amp; apt install -y nginx procps iproute2 curl | nginx 1.24 installé |
| Utilisateur | useradd -m -s /bin/bash webadmin ; chown -R webadmin:webadmin /var/www/html | uid 1000, propriétaire de /var/www/html, sans sudo |
| Page | su - webadmin ; echo '&lt;h1&gt;Bonjour DevOps&lt;/h1&gt;' &gt; /var/www/html/index.html | page remplacée ; /etc/nginx interdit en écriture (Permission denied) |
| Démarrage | nginx (systemctl échoue : pas de systemd) | maître root, workers www-data ; curl localhost:8080 → Bonjour DevOps |
| Requêtes | for i in $(seq 50); do curl -s localhost:8080 &gt;/dev/null; done | access.log : 51 × 200, 1 × 404 |
| Comptage | awk '{print $9}' access.log \| sort \| uniq -c \| sort -rn | 51 200 / 1 404 |
| Port et arrêt | ss -tulpn ; kill -15 412 | nginx écoutait sur 0.0.0.0:80 (pid 412) ; après SIGTERM, plus rien |

Pourquoi systemd ne tourne pas : dans un conteneur, le PID 1 est la commande lancée
(bash), pas systemd. systemd est un système d'init complet qui suppose piloter une machine
entière (démons, cgroups, journal) ; un conteneur n'exécute qu'un processus et ses enfants,
c'est pourquoi on lance nginx directement, ou via un script d'init (service), jamais via systemctl.</code></pre>
</article>

<article><div class="chaphead"><span class="chapnum">Pour aller plus loin</span><span class="badge tag-contexte">Bon à savoir</span></div>
<h2>Trois questions qu'un relecteur poserait</h2>
<ul>
<li><strong>Pourquoi nginx écoute-t-il en 0.0.0.0 et pas seulement en 127.0.0.1 ?</strong> Parce que le trafic vient de l'extérieur du conteneur (ton poste, via Docker) : en 127.0.0.1 il ne répondrait qu'à des curl lancés dans le conteneur. Sur une vraie machine, un service interne (base de données) écoute en 127.0.0.1 ou sur l'adresse privée, jamais en 0.0.0.0 sans pare-feu.</li>
<li><strong>Que se passe-t-il si tu quittes le shell du conteneur ?</strong> bash est PID 1 ; à sa sortie le conteneur s'arrête et, avec <code>--rm</code>, disparaît, nginx compris. Dans une vraie image, c'est nginx qui serait PID 1, en avant-plan (<code>nginx -g 'daemon off;'</code>) : chapitre 8.</li>
<li><strong>Pourquoi webadmin et pas root pour la page ?</strong> Parce que le contenu du site est la seule chose qu'un éditeur de contenu doit pouvoir modifier ; s'il se fait compromettre, la configuration de nginx et le système restent intacts. Moindre privilège, et c'est le même raisonnement que USER dans un Dockerfile.</li>
</ul>
</article>

<div class="footnav"><a href="../devops-00-fondations.html#c2">← Chapitre 2</a><a href="../devops-00-fondations.html#c3">Chapitre 3 →</a></div>
</div>
<script>
(function(){ var root=document.documentElement; try{ var t=localStorage.getItem('devops-theme'); if(t) root.setAttribute('data-theme',t); }catch(e){}
  document.querySelectorAll('table').forEach(function(t){ var rows=t.rows; if(!rows.length) return; var head=rows[0]; if(!head.querySelector('th')) return; head.classList.add('head');
    var labels=Array.prototype.map.call(head.cells,function(c){return c.textContent.trim();});
    for(var i=1;i<rows.length;i++){ var cells=rows[i].cells; for(var j=0;j<cells.length;j++){ if(cells[j].tagName==='TD') cells[j].setAttribute('data-label',labels[j]||''); } } t.classList.add('stack'); });
  document.querySelectorAll('pre').forEach(function(pre){ var b=document.createElement('button'); b.type='button'; b.className='copy'; b.textContent='Copier';
    b.addEventListener('click',function(){ var t=pre.querySelector('code').textContent; navigator.clipboard.writeText(t).then(function(){ b.textContent='Copié !'; setTimeout(function(){ b.textContent='Copier'; },1500); }); }); pre.appendChild(b); });
})();
</script>
</body></html>'''
pathlib.Path('/home/claude/corr').mkdir(exist_ok=True)
pathlib.Path('/home/claude/corr/tp02.html').write_text(head + '\n' + body)
print('correction TP 2 écrite')
