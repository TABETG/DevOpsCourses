import re, pathlib

p = pathlib.Path('/mnt/user-data/outputs/devops-00-fondations.html')
s = p.read_text()
assert 'class="anim"' not in s, 'déjà fait'

CSS = """
/* ============ Animations pédagogiques ============ */
.anim{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);padding:.8rem;margin:1rem 0}
.anim .ctl{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin-bottom:.6rem}
.anim .ctl button{font:inherit;font-size:.82rem;font-weight:700;border:1px solid var(--accent);background:var(--paper);color:var(--accent-ink);border-radius:999px;padding:.25rem .75rem;cursor:pointer;min-height:32px}
.anim .ctl button.primary{background:var(--accent);color:#fff}
.anim .ctl button:disabled{opacity:.4;cursor:default}
.anim .ctl .st{font-size:.82rem;color:var(--muted);margin-left:auto}
.anim svg{width:100%;height:auto;display:block;overflow:visible;font-family:inherit}
.anim svg text{fill:var(--ink)}
.anim .lbl{fill:var(--muted);font-size:11px}
.anim .box{fill:var(--paper);stroke:var(--line-strong);stroke-width:1.5}
.anim .soft{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.5}
.anim .green{fill:var(--tp-soft);stroke:var(--tp);stroke-width:1.5}
.anim .amber{fill:var(--exo-soft);stroke:var(--exo);stroke-width:1.5}
.anim .red{fill:#FDECEC;stroke:#A11B1B;stroke-width:1.5}
.anim .redfill{fill:#C0392B}
.anim .greenfill{fill:#1B7A4E}
.anim .amberfill{fill:#B7791F}
.anim .dim{opacity:.35}
.anim .on{filter:drop-shadow(0 0 4px rgba(37,99,235,.5))}
.anim .mono{font-family:"JetBrains Mono",monospace;font-size:11px}
.anim .log{font-family:"JetBrains Mono",monospace;font-size:.78rem;background:var(--code-bg);color:var(--code-ink);border-radius:8px;padding:.6rem .8rem;min-height:3.6em;white-space:pre-wrap;margin-top:.6rem;line-height:1.45}
.anim .log .ok{color:#8FD3A7}.anim .log .ko{color:#F29A9A}.anim .log .cmd{color:#9CC4FF}
.anim figcaption{font-size:.85rem;color:var(--muted);margin-top:.6rem;text-align:center}
:root[data-theme="dark"] .anim .red{fill:#3A1616;stroke:#F29A9A}
@media (prefers-reduced-motion: reduce){.anim .auto{display:none}}
@media print{.anim .ctl{display:none}}
</style>"""

# ---------- A. Chapitre 1 : où passe le temps ----------
A = r'''<figure class="anim" id="anim-flux">
<div class="ctl"><button type="button" class="primary" data-play>Lancer</button><button type="button" data-mode>Mode : manuel</button><span class="st" data-st>jour 0</span></div>
<svg viewBox="0 0 480 152" role="img" aria-label="Animation : où passe le temps entre une idée et la production">
<g data-stages></g>
<circle data-token r="7" cx="24" cy="60" class="redfill"/>
<text x="240" y="146" text-anchor="middle" class="lbl" data-msg>Une idée avance de gauche à droite ; le rouge, c'est l'attente.</text>
</svg>
<figcaption>Le travail actif (vert) tient en quelques heures ; l'attente (rouge) fait les semaines. Le pipeline ne rend pas les gens plus rapides : il supprime l'attente. Compare les deux modes.</figcaption>
</figure>
<script>
(function(){
  var fig=document.getElementById('anim-flux'); if(!fig) return;
  var svg=fig.querySelector('svg'), g=fig.querySelector('[data-stages]'), tok=fig.querySelector('[data-token]'), st=fig.querySelector('[data-st]'), msg=fig.querySelector('[data-msg]');
  var modes={manuel:[["idée",0.2,7],["dev",4,0],["tests à la main",0.5,0],["push",0.1,2],["build à la main",0.3,1],["déploiement manuel",0.4,5],["prod",0,0]],
             pipeline:[["idée",0.2,1],["dev",4,0],["tests en CI",0.2,0],["push",0.1,0],["build en CI",0.1,0],["déploiement auto",0.1,0],["prod",0,0]]};
  var mode='manuel', playing=false, raf=null;
  function draw(){
    var m=modes[mode], tot=0; m.forEach(function(x){tot+=x[1]/24+x[2];});
    var x=24, W=420, html='';
    m.forEach(function(x_,i){
      var w=Math.max(6,(x_[1]/24)*W/tot), wait=(x_[2])*W/tot;
      html+='<rect x="'+x+'" y="48" width="'+w+'" height="24" rx="4" class="green"/>'+
            '<text x="'+(x+w/2)+'" y="40" text-anchor="middle" class="lbl" font-size="10">'+(i+1)+'</text>';
      x+=w;
      if(wait>0){ html+='<rect x="'+x+'" y="54" width="'+wait+'" height="12" rx="3" class="red"/>'; x+=wait; }
    });
    html+='<text x="24" y="96" class="lbl">total : '+tot.toFixed(1)+' jours, dont '+m.reduce(function(a,b){return a+b[1];},0).toFixed(1)+' h de travail actif</text>';
    html+='<text x="24" y="112" class="lbl" font-size="10">'+m.slice(0,4).map(function(x_,i){return (i+1)+' '+x_[0];}).join(' · ')+'</text>';
    html+='<text x="24" y="126" class="lbl" font-size="10">'+m.slice(4).map(function(x_,i){return (i+5)+' '+x_[0];}).join(' · ')+'</text>';
    g.innerHTML=html; tok.setAttribute('cx',24); st.textContent='jour 0';
    fig.querySelector('[data-mode]').textContent='Mode : '+mode;
  }
  function play(){
    if(playing){ playing=false; cancelAnimationFrame(raf); fig.querySelector('[data-play]').textContent='Lancer'; return; }
    playing=true; fig.querySelector('[data-play]').textContent='Pause';
    var m=modes[mode], tot=0; m.forEach(function(x){tot+=x[1]/24+x[2];});
    var dur=Math.min(9000, 1500+tot*450), t0=performance.now(), x0=24, x1=450;
    function step(t){
      if(!playing) return;
      var p=Math.min(1,(t-t0)/dur); tok.setAttribute('cx', x0+(x1-x0)*p); st.textContent='jour '+(tot*p).toFixed(1);
      msg.textContent = p<1 ? (tokOnRed(x0+(x1-x0)*p)?'… en attente de quelqu\u2019un ou de quelque chose':'travail en cours') : 'en production après '+tot.toFixed(1)+' jours';
      if(p<1) raf=requestAnimationFrame(step); else { playing=false; fig.querySelector('[data-play]').textContent='Relancer'; }
    }
    raf=requestAnimationFrame(step);
  }
  function tokOnRed(cx){ var ok=false; g.querySelectorAll('rect.red').forEach(function(r){ var a=+r.getAttribute('x'), w=+r.getAttribute('width'); if(cx>=a&&cx<=a+w) ok=true; }); return ok; }
  fig.querySelector('[data-play]').addEventListener('click',play);
  fig.querySelector('[data-mode]').addEventListener('click',function(){ playing=false; cancelAnimationFrame(raf); mode = mode==='manuel'?'pipeline':'manuel'; draw(); fig.querySelector('[data-play]').textContent='Lancer'; msg.textContent = mode==='pipeline'?'Même travail, presque plus d\u2019attente.':'Une idée avance de gauche à droite ; le rouge, c\u2019est l\u2019attente.'; });
  draw();
})();
</script>
'''

# ---------- B. Chapitre 2 : SIGTERM, 10 s, SIGKILL ----------
B = r'''<figure class="anim" id="anim-sig">
<div class="ctl"><button type="button" class="primary" data-stop>docker stop</button><button type="button" data-form>ENTRYPOINT : forme exec</button><button type="button" data-reset>Réinitialiser</button><span class="st" data-st>conteneur en cours</span></div>
<svg viewBox="0 0 480 150" role="img" aria-label="Animation : ce que fait docker stop selon la forme de l'ENTRYPOINT">
<rect x="20" y="20" width="200" height="70" rx="8" class="soft"/>
<text x="120" y="45" text-anchor="middle" font-size="12" font-weight="700" data-pid1>PID 1 : java -jar app.jar</text>
<text x="120" y="66" text-anchor="middle" class="lbl" data-pid1sub>reçoit les signaux</text>
<rect x="260" y="20" width="200" height="70" rx="8" class="box"/>
<text x="360" y="45" text-anchor="middle" font-size="12" font-weight="700">Docker</text>
<text x="360" y="66" text-anchor="middle" class="lbl" data-docker>attend</text>
<rect x="20" y="112" width="440" height="14" rx="4" class="box"/>
<rect x="20" y="112" width="0" height="14" rx="4" class="amberfill" data-bar/>
<text x="20" y="142" class="lbl">0 s</text><text x="460" y="142" text-anchor="end" class="lbl">10 s (délai de grâce)</text>
<text x="240" y="142" text-anchor="middle" class="lbl" data-msg></text>
</svg>
<div class="log" data-log>$ docker run -d --name api img   # le conteneur tourne</div>
<figcaption>docker stop envoie SIGTERM au PID 1 et attend 10 secondes. En forme exec, l'application est PID 1 : elle finit ses requêtes et sort en une seconde. En forme shell, PID 1 est un sh qui ignore le signal : l'application n'est jamais prévenue, et Docker la tue.</figcaption>
</figure>
<script>
(function(){
  var fig=document.getElementById('anim-sig'); if(!fig) return;
  var exec=true, timer=null, bar=fig.querySelector('[data-bar]'), st=fig.querySelector('[data-st]'), log=fig.querySelector('[data-log]'), msg=fig.querySelector('[data-msg]'), dk=fig.querySelector('[data-docker]');
  function form(){ exec=!exec; fig.querySelector('[data-form]').textContent='ENTRYPOINT : forme '+(exec?'exec':'shell');
    fig.querySelector('[data-pid1]').textContent = exec?'PID 1 : java -jar app.jar':'PID 1 : /bin/sh -c "java -jar app.jar"';
    fig.querySelector('[data-pid1sub]').textContent = exec?'reçoit les signaux':'sh ne transmet pas SIGTERM à java'; reset(); }
  function reset(){ clearInterval(timer); bar.setAttribute('width',0); bar.setAttribute('class','amberfill'); st.textContent='conteneur en cours'; dk.textContent='attend'; msg.textContent=''; log.innerHTML='$ docker run -d --name api img   # le conteneur tourne'; fig.querySelector('[data-stop]').disabled=false; }
  function stop(){
    fig.querySelector('[data-stop]').disabled=true; var t0=performance.now(), speed=3; // 10 s simulées en ~3,3 s
    log.innerHTML='<span class="cmd">$ docker stop api</span>\nDocker → SIGTERM au PID 1'; dk.textContent='SIGTERM envoyé, compte à rebours';
    timer=setInterval(function(){
      var sec=(performance.now()-t0)/1000*speed; bar.setAttribute('width', Math.min(440, sec/10*440)); msg.textContent=sec.toFixed(1)+' s';
      if(exec && sec>=1.2){ clearInterval(timer); bar.setAttribute('class','greenfill'); st.textContent='sorti proprement, code 143'; dk.textContent='conteneur arrêté en 1,2 s';
        log.innerHTML+='\n<span class="ok">java : handler SIGTERM → fin des requêtes en cours, fermeture des connexions, exit(143)</span>\n<span class="ok">Docker : conteneur arrêté proprement</span>'; }
      if(!exec && sec>=10){ clearInterval(timer); bar.setAttribute('class','redfill'); st.textContent='tué, code 137'; dk.textContent='SIGKILL après 10 s';
        log.innerHTML+='\n<span class="ko">sh : SIGTERM ignoré, java jamais prévenu</span>\n<span class="ko">Docker : 10 s écoulées → SIGKILL, code 137, requêtes perdues, transactions coupées</span>'; }
    }, 50);
  }
  fig.querySelector('[data-stop]').addEventListener('click',stop); fig.querySelector('[data-form]').addEventListener('click',form); fig.querySelector('[data-reset]').addEventListener('click',reset);
})();
</script>
'''

# ---------- C. Chapitre 3 : une requête HTTPS, étape par étape ----------
C = r'''<figure class="anim" id="anim-http">
<div class="ctl"><button type="button" class="primary" data-next>Étape suivante</button><button type="button" data-fail>Simuler une panne à l'étape…</button><button type="button" data-reset>Réinitialiser</button><span class="st" data-st>étape 0 / 4</span></div>
<svg viewBox="0 0 480 122" role="img" aria-label="Animation : les quatre étapes d'une requête HTTPS et leurs erreurs">
<g data-steps></g>
<circle data-pkt r="6" cx="20" cy="82" class="greenfill"/>
</svg>
<div class="log" data-log>$ curl -v https://api.crisisshield.example/health</div>
<figcaption>Quatre étapes, quatre messages d'erreur différents : on lit le message, on sait où chercher. Un 502 arrive après les quatre : c'est le reverse proxy qui parle, pas l'application.</figcaption>
</figure>
<script>
(function(){
  var fig=document.getElementById('anim-http'); if(!fig) return;
  var steps=[["DNS","api.crisisshield.example → 203.0.113.10","Could not resolve host","dig, /etc/resolv.conf, le nom existe-t-il ?"],
             ["TCP","SYN, SYN-ACK, ACK sur le port 443","Connection refused / timed out","ss -tulpn : le service écoute ? pare-feu, security group"],
             ["TLS","certificat vérifié, clés de session","certificate verify failed","openssl s_client : chaîne, SAN, dates, horloge"],
             ["HTTP","GET /health → 200 OK","404, 401, 500, 502","logs de l'application ou du proxy ; 502 = proxy sans backend"]];
  var i=0, failAt=-1, g=fig.querySelector('[data-steps]'), pkt=fig.querySelector('[data-pkt]'), log=fig.querySelector('[data-log]'), st=fig.querySelector('[data-st]');
  function draw(){
    var h='';
    steps.forEach(function(s_,k){ var x=40+k*110, cls= k<i ? (failAt===k?'red':'green') : (k===i?'soft on':'box dim');
      h+='<rect x="'+x+'" y="30" width="90" height="40" rx="7" class="'+cls+'"/><text x="'+(x+45)+'" y="55" text-anchor="middle" font-size="13" font-weight="700">'+s_[0]+'</text>';
      if(k<3) h+='<path d="M'+(x+90)+',50 L'+(x+110)+',50" class="arrow" stroke="currentColor" fill="none" stroke-width="1.5"/>';
    });
    h+='<text x="240" y="112" text-anchor="middle" class="lbl" data-hint>'+(i<4? 'prochaine étape : '+steps[i][0]:'réponse reçue')+'</text>';
    g.innerHTML=h; st.textContent='étape '+i+' / 4';
  }
  function next(){
    if(i>=4) return;
    var s_=steps[i]; var x=85+i*110; pkt.setAttribute('cx',x);
    if(failAt===i){ pkt.setAttribute('class','redfill'); log.innerHTML+='\n<span class="ko">'+s_[0]+' : '+s_[2]+'</span>\n   → '+s_[3]; i++; draw(); fig.querySelector('[data-next]').disabled=true; st.textContent='échec à l\u2019étape '+i; return; }
    log.innerHTML+='\n<span class="ok">'+s_[0]+' : '+s_[1]+'</span>'; i++; draw();
    if(i===4){ log.innerHTML+='\n<span class="ok">HTTP/1.1 200 OK</span>'; fig.querySelector('[data-next]').disabled=true; }
  }
  function reset(){ i=0; failAt=-1; pkt.setAttribute('cx',20); pkt.setAttribute('class','greenfill'); log.innerHTML='$ curl -v https://api.crisisshield.example/health'; fig.querySelector('[data-next]').disabled=false; fig.querySelector('[data-fail]').textContent='Simuler une panne à l\u2019étape…'; draw(); }
  fig.querySelector('[data-next]').addEventListener('click',next); fig.querySelector('[data-reset]').addEventListener('click',reset);
  fig.querySelector('[data-fail]').addEventListener('click',function(){ failAt=(failAt+1)%4; this.textContent='Panne simulée : '+steps[failAt][0]; if(i>failAt) reset(); failAt=failAt; });
  draw();
})();
</script>
'''

# ---------- D. Chapitre 2.4 / 4 : un pipeline shell en action ----------
D = r'''<figure class="anim" id="anim-pipe">
<div class="ctl"><button type="button" class="primary" data-play>Exécuter le pipeline</button><button type="button" data-reset>Réinitialiser</button><span class="st" data-st>prêt</span></div>
<div class="log" data-cmd><span class="cmd">$ grep ERROR app.log | cut -d' ' -f3 | sort | uniq -c | sort -rn</span></div>
<svg viewBox="0 0 480 190" role="img" aria-label="Animation : les lignes d'un log traversent grep, cut, sort et uniq">
<g data-cols></g>
</svg>
<figcaption>Chaque commande lit ce que la précédente écrit et ne fait qu'une chose : filtrer, découper, trier, compter. Le résultat est une réponse à une question (« quel service produit le plus d'erreurs ? »), pas un fichier à lire.</figcaption>
</figure>
<script>
(function(){
  var fig=document.getElementById('anim-pipe'); if(!fig) return;
  var lines=["10:01 INFO api demarrage","10:02 ERROR db connexion refusee","10:02 ERROR api timeout amont","10:03 WARN api lenteur","10:03 ERROR db connexion refusee","10:04 ERROR api timeout amont","10:04 INFO web ok","10:05 ERROR db connexion refusee"];
  var stages=[["app.log",lines],["grep ERROR",lines.filter(function(l){return l.indexOf('ERROR')>=0;})],["cut -f3",null],["sort | uniq -c",null],["sort -rn",null]];
  stages[2][1]=stages[1][1].map(function(l){return l.split(' ')[2];});
  var counts={}; stages[2][1].forEach(function(v){counts[v]=(counts[v]||0)+1;});
  stages[3][1]=Object.keys(counts).sort().map(function(k){return counts[k]+' '+k;});
  stages[4][1]=stages[3][1].slice().sort(function(a,b){return parseInt(b)-parseInt(a);});
  var g=fig.querySelector('[data-cols]'), st=fig.querySelector('[data-st]'), shown=1, timer=null;
  function draw(){
    var h='';
    stages.forEach(function(s_,k){ var x=6+k*96, vis=k<shown;
      h+='<rect x="'+x+'" y="6" width="90" height="176" rx="7" class="'+(vis?(k===shown-1?'soft':'box'):'box dim')+'"/><text x="'+(x+45)+'" y="22" text-anchor="middle" font-size="11" font-weight="700">'+s_[0]+'</text>';
      if(vis) s_[1].slice(0,8).forEach(function(l,j){ var t=l.length>14?l.slice(0,13)+'…':l; h+='<text x="'+(x+5)+'" y="'+(40+j*17)+'" class="mono" font-size="8.5">'+t.replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</text>'; });
      else h+='<text x="'+(x+45)+'" y="100" text-anchor="middle" class="lbl">…</text>';
      if(k<4) h+='<text x="'+(x+93)+'" y="100" text-anchor="middle" font-size="14">›</text>';
    });
    g.innerHTML=h; st.textContent = shown>=5?'terminé : db produit le plus d\u2019erreurs':('étape '+(shown-1)+' / 4');
  }
  fig.querySelector('[data-play]').addEventListener('click',function(){ clearInterval(timer); shown=1; draw(); timer=setInterval(function(){ shown++; draw(); if(shown>=5) clearInterval(timer); }, 900); });
  fig.querySelector('[data-reset]').addEventListener('click',function(){ clearInterval(timer); shown=1; draw(); });
  draw();
})();
</script>
'''

# ---------- E. Chapitre 5 : les trois zones de Git, pas à pas ----------
E = r'''<figure class="anim" id="anim-git">
<div class="ctl"><button type="button" class="primary" data-next>Commande suivante</button><button type="button" data-reset>Réinitialiser</button><span class="st" data-st>0 / 6</span></div>
<svg viewBox="0 0 480 212" role="img" aria-label="Animation : un fichier traverse les trois zones de Git, puis une branche est créée et fusionnée">
<rect x="10" y="10" width="140" height="90" rx="8" class="box"/><text x="80" y="30" text-anchor="middle" font-size="12" font-weight="700">répertoire de travail</text>
<rect x="170" y="10" width="140" height="90" rx="8" class="box"/><text x="240" y="30" text-anchor="middle" font-size="12" font-weight="700">index (staging)</text>
<rect x="330" y="10" width="140" height="90" rx="8" class="box"/><text x="400" y="30" text-anchor="middle" font-size="12" font-weight="700">dépôt (commits)</text>
<g data-file><rect x="40" y="50" width="80" height="34" rx="6" class="amber"/><text x="80" y="72" text-anchor="middle" class="mono">api.java *</text></g>
<g data-graph></g>
</svg>
<div class="log" data-log>$ git status   # rien à valider, arbre de travail propre</div>
<figcaption>Un fichier modifié n'est nulle part tant qu'il n'est pas indexé ; un commit est un instantané de l'index ; une branche n'est qu'un pointeur qui avance. Le merge crée un commit à deux parents.</figcaption>
</figure>
<script>
(function(){
  var fig=document.getElementById('anim-git'); if(!fig) return;
  var file=fig.querySelector('[data-file]'), graph=fig.querySelector('[data-graph]'), log=fig.querySelector('[data-log]'), st=fig.querySelector('[data-st]'), i=0;
  var commits=[], branches={main:null}, cur='main';
  function drawGraph(){
    var h='', xs={}, y={main:138, feature:178};
    commits.forEach(function(c,k){ var x=40+k*70; xs[c.id]=x; var yy=y[c.br]||150;
      c.parents.forEach(function(pid){ if(xs[pid]!==undefined) h+='<line x1="'+xs[pid]+'" y1="'+(y[commits.filter(function(z){return z.id===pid;})[0].br]||150)+'" x2="'+x+'" y2="'+yy+'" stroke="currentColor" stroke-width="1.5" opacity=".5"/>'; });
      h+='<circle cx="'+x+'" cy="'+yy+'" r="8" class="'+(c.br==='feature'?'amber':'soft')+'"/><text x="'+x+'" y="'+(c.br==='feature'?yy+22:yy-14)+'" text-anchor="middle" class="mono" font-size="9">'+c.id+'</text>'; });
    Object.keys(branches).forEach(function(b){ var c=branches[b]; if(!c) return; var x=xs[c]; var yy=(b==='feature'?178:138);
      h+='<text x="'+(x+14)+'" y="'+(yy+4)+'" class="lbl" font-weight="700">'+b+(cur===b?' ← HEAD':'')+'</text>'; });
    graph.innerHTML=h;
  }
  function move(zone){ var x={work:40, index:200, repo:360}[zone]; file.setAttribute('transform','translate('+(x-40)+',0)'); }
  var steps=[
    function(){ log.innerHTML='<span class="cmd">$ git add api.java</span>\nle fichier entre dans l\u2019index : c\u2019est ce qui sera validé'; move('index'); file.querySelector('rect').setAttribute('class','soft'); },
    function(){ log.innerHTML='<span class="cmd">$ git commit -m "feat(api): endpoint /health"</span>\n[main a1b2c3] instantané de l\u2019index enregistré'; move('repo'); file.querySelector('rect').setAttribute('class','green'); file.querySelector('text').textContent='api.java'; commits.push({id:'a1b2c3',parents:[],br:'main'}); branches.main='a1b2c3'; drawGraph(); },
    function(){ log.innerHTML='<span class="cmd">$ git switch -c feature/x</span>\nnouvelle branche : un pointeur sur le même commit, rien d\u2019autre'; branches.feature='a1b2c3'; cur='feature'; drawGraph(); },
    function(){ log.innerHTML='<span class="cmd">$ git commit -am "feat: cache"</span>\n[feature/x d4e5f6] la branche feature avance, main ne bouge pas'; commits.push({id:'d4e5f6',parents:['a1b2c3'],br:'feature'}); branches.feature='d4e5f6'; drawGraph(); },
    function(){ log.innerHTML='<span class="cmd">$ git switch main && git commit -am "fix: log"</span>\n[main 789abc] les deux branches ont divergé'; cur='main'; commits.push({id:'789abc',parents:['a1b2c3'],br:'main'}); branches.main='789abc'; drawGraph(); },
    function(){ log.innerHTML='<span class="cmd">$ git merge --no-ff feature/x</span>\n[main m0e1r2] commit de fusion à deux parents ; main pointe dessus'; commits.push({id:'m0e1r2',parents:['789abc','d4e5f6'],br:'main'}); branches.main='m0e1r2'; drawGraph(); }
  ];
  function next(){ if(i>=steps.length) return; steps[i](); i++; st.textContent=i+' / 6'; if(i>=steps.length) fig.querySelector('[data-next]').disabled=true; }
  function reset(){ i=0; commits=[]; branches={main:null}; cur='main'; graph.innerHTML=''; move('work'); file.querySelector('rect').setAttribute('class','amber'); file.querySelector('text').textContent='api.java *'; log.innerHTML='$ git status   # rien à valider, arbre de travail propre'; st.textContent='0 / 6'; fig.querySelector('[data-next]').disabled=false; }
  fig.querySelector('[data-next]').addEventListener('click',next); fig.querySelector('[data-reset]').addEventListener('click',reset);
})();
</script>
'''

# ---------- F. Chapitre 6 : transaction, commit ou rollback ----------
F = r'''<figure class="anim" id="anim-tx">
<div class="ctl"><button type="button" class="primary" data-ok>Virement, tout se passe bien</button><button type="button" data-ko>Virement, panne au milieu</button><button type="button" data-reset>Réinitialiser</button><span class="st" data-st>comptes à l'équilibre</span></div>
<svg viewBox="0 0 480 120" role="img" aria-label="Animation : une transaction bancaire validée ou annulée">
<rect x="30" y="20" width="160" height="70" rx="8" class="box"/><text x="110" y="45" text-anchor="middle" font-size="12" font-weight="700">compte A</text><text x="110" y="72" text-anchor="middle" class="mono" data-a>100 €</text>
<rect x="290" y="20" width="160" height="70" rx="8" class="box"/><text x="370" y="45" text-anchor="middle" font-size="12" font-weight="700">compte B</text><text x="370" y="72" text-anchor="middle" class="mono" data-b>100 €</text>
<circle data-coin r="9" cx="110" cy="55" class="amberfill" opacity="0"/>
<text x="240" y="110" text-anchor="middle" class="lbl" data-msg>total : 200 €</text>
</svg>
<div class="log" data-log>BEGIN;</div>
<figcaption>Deux écritures, une seule transaction : soit les deux, soit aucune. Sans transaction, une panne entre les deux fait disparaître 50 € ; avec, le rollback remet tout en place. Le total ne bouge jamais : c'est l'atomicité.</figcaption>
</figure>
<script>
(function(){
  var fig=document.getElementById('anim-tx'); if(!fig) return;
  var A=fig.querySelector('[data-a]'), B=fig.querySelector('[data-b]'), coin=fig.querySelector('[data-coin]'), msg=fig.querySelector('[data-msg]'), log=fig.querySelector('[data-log]'), st=fig.querySelector('[data-st]'), busy=false;
  function setA(v){A.textContent=v+' €';} function setB(v){B.textContent=v+' €';}
  function run(fail){
    if(busy) return; busy=true; setA(100); setB(100); coin.setAttribute('opacity',1); coin.setAttribute('cx',110); log.innerHTML='BEGIN;'; msg.textContent='total : 200 €';
    setTimeout(function(){ log.innerHTML+='\nUPDATE comptes SET solde = solde - 50 WHERE id = \'A\';'; setA(50); st.textContent='A débité, pas encore validé'; msg.textContent='total provisoire : 150 € (invisible aux autres)'; }, 500);
    var t0=performance.now(); (function anim(t){ var p=Math.min(1,(t-t0)/1800); coin.setAttribute('cx',110+260*p); if(p<1) requestAnimationFrame(anim); })(t0);
    setTimeout(function(){
      if(fail){ log.innerHTML+='\n<span class="ko">-- panne : connexion perdue avant le crédit de B</span>\n<span class="ok">ROLLBACK (automatique) : A revient à 100 €</span>'; setA(100); coin.setAttribute('opacity',0); st.textContent='transaction annulée'; msg.textContent='total : 200 €, rien n\u2019a été perdu'; }
      else { log.innerHTML+='\nUPDATE comptes SET solde = solde + 50 WHERE id = \'B\';\n<span class="ok">COMMIT; -- les deux écritures deviennent visibles en même temps</span>'; setB(150); coin.setAttribute('opacity',0); st.textContent='transaction validée'; msg.textContent='total : 200 €'; }
      busy=false;
    }, 2000);
  }
  fig.querySelector('[data-ok]').addEventListener('click',function(){run(false);}); fig.querySelector('[data-ko]').addEventListener('click',function(){run(true);});
  fig.querySelector('[data-reset]').addEventListener('click',function(){ if(busy) return; setA(100); setB(100); coin.setAttribute('opacity',0); log.innerHTML='BEGIN;'; st.textContent='comptes à l\u2019équilibre'; msg.textContent='total : 200 €'; });
})();
</script>
'''

def after_h3(s, sec, block):
    m = re.search(r'<h3>' + re.escape(sec) + r' [^<]*(?:<span class="badge[^<]*</span>)?</h3>', s); assert m, sec
    # après la figure statique éventuelle qui suit immédiatement le titre
    j = m.end(); m2 = re.match(r'\n<figure class="fig">.*?</figure>', s[j:], flags=re.S)
    if m2: j += m2.end()
    return s[:j] + '\n' + block + s[j:]

s = s.replace('</style>', CSS, 1)
s = after_h3(s, '1.1', A)
s = after_h3(s, '2.3', B)
s = after_h3(s, '2.4', D)
s = after_h3(s, '3.5', C)
s = after_h3(s, '5.1', E)
s = after_h3(s, '6.1', F)
p.write_text(s); print('animations :', s.count('class="anim"'))

ip = pathlib.Path('/mnt/user-data/outputs/devops-parcours-complet.html'); t = ip.read_text()
if 'Animations' not in t:
    t = t.replace('<li><strong>Expliquer les commandes</strong>', '<li><strong>Animations</strong> (niveau 0) : six schémas animés à piloter (où passe le temps d\'une idée à la production, docker stop et les signaux, un pipeline shell, une requête HTTPS et ses pannes, les trois zones de Git, une transaction). Chaque animation a des boutons ; rien ne bouge sans toi.</li>\n<li><strong>Expliquer les commandes</strong>', 1)
    ip.write_text(t); print('index ok')
