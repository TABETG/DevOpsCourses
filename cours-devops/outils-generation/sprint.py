import re, pathlib, json

LEVEL_HOURS = {0:30,1:25,2:30,3:30,4:40,5:50,6:35,7:45,8:45,9:45}
BUDGET = {"tag-coeur":12, "tag-important":8, "tag-contexte":4}

CSS = """
/* ============ Mode sprint : temps maximum, minuteurs, pression ============ */
.tbox{display:flex;flex-wrap:wrap;align-items:center;gap:.4rem;margin:.35rem 0 .8rem;font-size:.82rem}
.tbox .tb{font-weight:700;color:var(--muted);background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:.15rem .6rem}
.tbox button{font:inherit;font-size:.8rem;font-weight:700;border:1px solid var(--accent);background:var(--paper);color:var(--accent-ink);border-radius:999px;padding:.2rem .7rem;cursor:pointer;min-height:32px}
.tbox button.go{background:var(--accent);color:#fff}
.tbox button.ok{border-color:var(--ok);color:var(--ok)}
.tbox .spent{color:var(--muted)}
.tbox.done .tb{background:var(--tp-soft);border-color:var(--tp-line);color:var(--tp)}
.tbox.done .spent{color:var(--ok);font-weight:700}
.tbox.late .spent{color:#A11B1B;font-weight:700}
.chaptime{font-size:.86rem;color:var(--muted);margin:-.2rem 0 .9rem;padding:.5rem .8rem;border:1px dashed var(--line-strong);border-radius:8px;background:var(--bg)}
.chaptime b{color:var(--ink)}
.sec-active{outline:3px solid var(--accent);outline-offset:6px;border-radius:6px}
.sec-active.exo,.sec-active.tp{outline-offset:2px}
h3.sec-active{padding-left:.75rem}
#sprint{position:fixed;left:0;right:0;bottom:0;z-index:60;background:var(--hero);color:#fff;padding:.5rem .9rem calc(.5rem + env(safe-area-inset-bottom,0px));box-shadow:0 -4px 16px rgba(0,0,0,.25);font-size:.85rem}
#sprint .row{display:flex;align-items:center;gap:.6rem .9rem;flex-wrap:wrap;max-width:1120px;margin:0 auto}
#sprint .clock{font-family:"JetBrains Mono",monospace;font-size:1.5rem;font-weight:700;min-width:5.2rem;letter-spacing:.02em}
#sprint .clock.late{color:#FF6B6B;animation:blink 1s steps(2,start) infinite}
#sprint .cur{flex:1 1 200px;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#sprint .cur b{color:#fff}
#sprint .stat{opacity:.85;white-space:nowrap}
#sprint .pbar{flex:1 1 100%;height:6px;background:rgba(255,255,255,.18);border-radius:3px;overflow:hidden}
#sprint .pbar i{display:block;height:100%;width:0;background:#6CD19B;transition:width .3s}
#sprint button{font:inherit;font-size:.8rem;font-weight:700;border:1px solid rgba(255,255,255,.4);background:rgba(255,255,255,.1);color:#fff;border-radius:6px;padding:.3rem .65rem;cursor:pointer;min-height:34px}
#sprint button.primary{background:#6FA3F5;border-color:#6FA3F5;color:#0B1220}
#sprint button:disabled{opacity:.4;cursor:default}
#sprint .late-msg{color:#FF6B6B;font-weight:700}
body{padding-bottom:6.5rem}
@keyframes blink{50%{opacity:.35}}
@media (max-width:480px){#sprint{font-size:.78rem;padding:.4rem .6rem calc(.4rem + env(safe-area-inset-bottom,0px))} #sprint .clock{font-size:1.25rem;min-width:4.4rem} body{padding-bottom:7.5rem}}
@media print{#sprint,.tbox,.chaptime{display:none !important} body{padding-bottom:0}}
</style>"""

JS = r"""
<script>
(function(){
  var KEY='__KEY__'; var BUDGET=__BUDGET__; var TP=__TP__; var EXO=5; var REV=20;
  function load(){ try{ return JSON.parse(localStorage.getItem(KEY)||'{}'); }catch(e){ return {}; } }
  function save(){ try{ localStorage.setItem(KEY, JSON.stringify(st)); }catch(e){} }
  var st=load(); st.done=st.done||{}; st.spent=st.spent||{}; st.streak=st.streak||0; st.session=st.session||0; st.sessionDay=st.sessionDay||'';
  var today=new Date().toISOString().slice(0,10); if(st.sessionDay!==today){ st.session=0; st.sessionDay=today; }
  function fmt(s){ s=Math.max(0,Math.round(s)); var m=Math.floor(s/60), r=s%60; return (m<10?'0':'')+m+':'+(r<10?'0':'')+r; }
  function fmtMin(m){ if(m>=60){ var h=Math.floor(m/60), r=m%60; return h+' h'+(r?' '+(r<10?'0':'')+r:''); } return m+' min'; }
  function slug(t){ return t.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,''); }

  // 1. Inventaire des sections avec leur budget
  var secs=[];
  document.querySelectorAll('article').forEach(function(art){
    var chId=art.id, chRead=0, chExo=0;
    art.querySelectorAll('h3').forEach(function(h){
      var m=h.textContent.match(/^(\d+\.\d+)/); if(!m) return;
      var b=h.querySelector('.badge[class*="tag-"]'); var cls=b?(b.className.match(/tag-\w+/)||[''])[0]:'tag-important';
      var min=BUDGET[cls]||8; chRead+=min;
      secs.push({el:h, id:'s'+m[1].replace('.','-'), title:m[1]+' '+h.childNodes[0].textContent.trim(), min:min, kind:'lecture', ch:chId});
    });
    art.querySelectorAll('.exo').forEach(function(x){
      var t=x.querySelector('.tag'); var m=t?t.textContent.match(/Exercice\s+(\d+\.\d+)/):null; if(!m) return;
      chExo+=EXO; secs.push({el:x, id:'e'+m[1].replace('.','-'), title:'Exercice '+m[1], min:EXO, kind:'exercice', ch:chId, anchor:t});
    });
    var tp=art.querySelector('.tp'); if(tp){
      var t=tp.querySelector('.tag'); var m=t?t.textContent.match(/pratique\s+(\d+)/):null; var n=m?m[1]:chId.replace('c','');
      var tpm=TP[n]||120; secs.push({el:tp, id:'tp'+n, title:'TP '+n, min:tpm, kind:'tp', ch:chId, anchor:t});
      var head=art.querySelector('.chaphead');
      if(head){ var d=document.createElement('div'); d.className='chaptime';
        d.innerHTML='<b>Objectif de ce chapitre :</b> lecture '+fmtMin(chRead)+' + exercices '+fmtMin(chExo)+' + TP '+fmtMin(tpm)+' = <b>'+fmtMin(chRead+chExo+tpm)+' maximum</b>. Au-delà, tu passes au chapitre suivant et tu notes ce qui manque.';
        var h2=art.querySelector('h2'); h2.parentNode.insertBefore(d, h2.nextSibling); }
    }
  });
  var rev=document.querySelector('section.rev'); if(rev){ var h=rev.querySelector('h2'); secs.push({el:rev, id:'rev', title:'Révision du niveau', min:REV, kind:'révision', anchor:h}); }

  // 2. Boîte minuteur sous chaque titre
  secs.forEach(function(s,i){
    s.el.dataset.sec=s.id;
    var box=document.createElement('div'); box.className='tbox'; box.dataset.for=s.id;
    box.innerHTML='<span class="tb">⏱ max '+fmtMin(s.min)+'</span><button type="button" class="go">Démarrer</button><button type="button" class="ok">Terminé</button><span class="spent"></span>';
    var after=s.anchor||s.el;
    if(s.kind==='lecture') s.el.parentNode.insertBefore(box, s.el.nextSibling);
    else after.parentNode.insertBefore(box, after.nextSibling);
    s.box=box;
    box.querySelector('.go').addEventListener('click',function(){ start(i); });
    box.querySelector('.ok').addEventListener('click',function(){ finish(i); });
    paint(s);
  });
  function paint(s){
    var sp=s.box.querySelector('.spent'); s.box.classList.remove('done','late');
    if(st.done[s.id]){ var t=st.spent[s.id]||0; s.box.classList.add(t<=s.min*60?'done':'late'); sp.textContent=(t<=s.min*60?'✓ tenu en ':'✓ fini en ')+fmt(t); s.box.querySelector('.go').textContent='Refaire'; }
    else { sp.textContent=''; }
  }

  // 3. Barre de sprint
  var bar=document.createElement('div'); bar.id='sprint';
  bar.innerHTML='<div class="row"><span class="clock" id="spClock">--:--</span><span class="cur" id="spCur">Aucune section en cours. <b>Démarre la première.</b></span>'
    +'<button type="button" id="spPause" disabled>Pause</button><button type="button" id="spDone" disabled>Terminé</button><button type="button" id="spNext" class="primary">Suivant ▶</button>'
    +'<span class="stat" id="spProg"></span><span class="stat" id="spStreak"></span><span class="stat" id="spSession"></span><span class="stat" id="spLeft"></span><div class="pbar"><i id="spBar"></i></div></div>';
  document.body.appendChild(bar);
  var clock=document.getElementById('spClock'), cur=document.getElementById('spCur');
  var active=-1, remaining=0, elapsed=0, tick=null, paused=false, warned=false;

  function stats(){
    var done=0, left=0; secs.forEach(function(s){ if(st.done[s.id]) done++; else left+=s.min; });
    document.getElementById('spProg').textContent='Page : '+done+'/'+secs.length+' ('+Math.round(done/secs.length*100)+' %)';
    document.getElementById('spBar').style.width=(done/secs.length*100)+'%';
    document.getElementById('spStreak').textContent='Série dans les temps : '+st.streak;
    document.getElementById('spSession').textContent="Aujourd'hui : "+fmtMin(Math.round(st.session/60));
    document.getElementById('spLeft').textContent='Reste : '+fmtMin(left);
  }
  function beep(n){
    try{ var ac=beep.ctx||(beep.ctx=new (window.AudioContext||window.webkitAudioContext)()); var t=ac.currentTime;
      for(var i=0;i<n;i++){ var o=ac.createOscillator(), g=ac.createGain(); o.frequency.value=i%2?660:880; o.connect(g); g.connect(ac.destination); g.gain.setValueAtTime(.2,t+i*.25); g.gain.exponentialRampToValueAtTime(.001,t+i*.25+.2); o.start(t+i*.25); o.stop(t+i*.25+.22); } }catch(e){}
    if(navigator.vibrate) navigator.vibrate(n>2?[200,100,200,100,400]:[150]);
  }
  function start(i){
    if(active>=0) stop();
    active=i; var s=secs[i]; remaining=s.min*60; elapsed=0; paused=false; warned=false;
    secs.forEach(function(x){ x.el.classList.remove('sec-active'); }); s.el.classList.add('sec-active');
    s.el.scrollIntoView({behavior:'smooth',block:'start'});
    cur.innerHTML='En cours : <b>'+s.title+'</b> — objectif '+fmtMin(s.min);
    document.getElementById('spPause').disabled=false; document.getElementById('spDone').disabled=false; document.getElementById('spPause').textContent='Pause';
    try{ beep.ctx=beep.ctx||new (window.AudioContext||window.webkitAudioContext)(); }catch(e){}
    tick=setInterval(step,1000); render();
  }
  function step(){
    if(paused) return;
    remaining--; elapsed++; st.session++; if(elapsed%15===0) save();
    if(remaining===60 && !warned){ warned=true; beep(1); }
    if(remaining===0){ beep(5); }
    render();
  }
  function render(){
    if(active<0){ clock.textContent='--:--'; clock.classList.remove('late'); return; }
    if(remaining>=0){ clock.textContent=fmt(remaining); clock.classList.remove('late'); }
    else { clock.textContent='+'+fmt(-remaining); clock.classList.add('late'); cur.innerHTML='<span class="late-msg">EN RETARD</span> sur <b>'+secs[active].title+'</b> — termine ou passe à la suite.'; }
    stats();
  }
  function stop(){ if(tick){ clearInterval(tick); tick=null; } if(active>=0){ st.spent[secs[active].id]=(st.spent[secs[active].id]||0)+0; secs[active].el.classList.remove('sec-active'); } active=-1; document.getElementById('spPause').disabled=true; document.getElementById('spDone').disabled=true; save(); }
  function finish(i){
    var s=secs[i]; var t=(i===active)?elapsed:(st.spent[s.id]||0);
    st.spent[s.id]=t; st.done[s.id]=true;
    if(i===active){ if(t<=s.min*60) st.streak++; else st.streak=0; }
    paint(s); if(i===active){ stop(); } save(); stats();
    cur.innerHTML='Section terminée. <b>Enchaîne tout de suite : Suivant.</b>'; clock.textContent='--:--'; clock.classList.remove('late');
  }
  function next(){
    var from=active>=0?active:-1; var j=-1;
    for(var i=from+1;i<secs.length;i++){ if(!st.done[secs[i].id]){ j=i; break; } }
    if(j<0){ for(var i=0;i<secs.length;i++){ if(!st.done[secs[i].id]){ j=i; break; } } }
    if(j<0){ cur.innerHTML='<b>Page terminée.</b> Coche le niveau sur la page d\'accueil et ouvre le suivant.'; beep(3); return; }
    if(active>=0 && !st.done[secs[active].id]) finish(active);
    start(j);
  }
  document.getElementById('spPause').addEventListener('click',function(){ paused=!paused; this.textContent=paused?'Reprendre':'Pause'; });
  document.getElementById('spDone').addEventListener('click',function(){ if(active>=0) finish(active); });
  document.getElementById('spNext').addEventListener('click',next);
  document.addEventListener('keydown',function(e){ if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA') return; if(e.key==='n'||e.key==='N') next(); if(e.key===' '&&active>=0){ e.preventDefault(); document.getElementById('spPause').click(); } if(e.key==='Enter'&&active>=0) finish(active); });
  window.addEventListener('beforeunload', save);
  document.addEventListener('visibilitychange', function(){ if(document.hidden) save(); });
  stats();
})();
</script>
"""

out = pathlib.Path('/mnt/user-data/outputs')
files = [
 ("devops-niveau-0-fondations.html", 0, range(1,7)), ("devops-niveau-1-conteneurs.html", 1, range(7,11)),
 ("devops-niveau-2-ci-cd.html", 2, range(11,16)), ("devops-niveau-3-infrastructure-as-code.html", 3, range(16,20)),
 ("devops-niveau-4-cloud.html", 4, range(20,25)), ("devops-niveau-5-kubernetes.html", 5, range(25,32)),
 ("devops-niveau-6-observabilite.html", 6, range(32,37)), ("devops-niveau-7-securite-devsecops.html", 7, range(37,43)),
 ("devops-niveau-8-sre-architecture.html", 8, range(43,49)), ("devops-niveau-9-expert-leadership.html", 9, range(49,55)),
]
for fn, lvl, chs in files:
    p = out/fn; s = p.read_text()
    if 'id="spClock"' in s:
        print(fn, 'déjà fait'); continue
    # budgets TP par chapitre : budget du chapitre moins lecture et exercices, arrondi à 5 min, minimum 45
    per_ch = LEVEL_HOURS[lvl]*60/len(list(chs))
    tp = {}
    for ch in chs:
        a = s.index(f'<span class="chapnum">Chapitre {ch}</span>')
        b = s.find('<span class="chapnum">Chapitre', a+10); b = len(s) if b<0 else b
        chunk = s[a:b]
        read = sum(BUDGET[t] for t in re.findall(r'<h3>\d+\.\d+ [^<]*<span class="badge (tag-\w+)">', chunk))
        exos = 5*len(re.findall(r'Exercice \d+\.\d+', chunk))
        tp[str(ch)] = max(45, int(round((per_ch - read - exos)/5.0)*5))
    js = JS.replace('__KEY__', f'devops-n{lvl}-sprint').replace('__BUDGET__', json.dumps(BUDGET)).replace('__TP__', json.dumps(tp))
    s = s.replace('</style>', CSS, 1)
    s = s.replace('</body>', js + '</body>', 1)
    p.write_text(s)
    print(fn, 'TP (min) :', tp)

# page d'accueil : explication du mode sprint
ip = out/'devops-parcours-complet.html'; t = ip.read_text()
if 'Mode sprint' not in t:
    t = t.replace('<li><strong>Lecture rapide</strong>',
        '<li><strong>Mode sprint</strong> : chaque titre, exercice et TP affiche son temps maximum (par cœur 12 min, important 8 min, bon à savoir 4 min, exercice 5 min, TP calculé). La barre en bas de page tient le minuteur : « Démarrer » lance le compte à rebours, un bip à une minute de la fin, cinq bips et un chrono rouge en retard, « Suivant » enchaîne. Raccourcis clavier : N suivant, Espace pause, Entrée terminé. Le temps passé, la série de sections tenues dans les temps et la progression se conservent dans le navigateur.</li>\n<li><strong>Lecture rapide</strong>', 1)
    ip.write_text(t)
print('index ok')
