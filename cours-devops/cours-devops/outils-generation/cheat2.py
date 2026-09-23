import re, pathlib, html as H

out = pathlib.Path('/mnt/user-data/outputs')
src = pathlib.Path('/home/claude/cheat.py').read_text().split('# ---------- rendu ----------')[0]
ns = {'re': re, 'pathlib': pathlib, 'html': H}; exec(src, ns); S = ns['S']

# sections ajoutées après coup (Proxmox/Nutanix, OpenShift)
S.insert(5, ("virt", "Proxmox et Nutanix", "Niveau 1, chapitre 7", [
 ("pvecm status ; pvecm nodes ; qm list ; pct list", "cluster Proxmox ; VM ; conteneurs LXC"), ("qm start|shutdown|migrate 100 node2 --online", "cycle de vie et migration à chaud"),
 ("qm clone 9000 101 --full ; qm set 101 --ipconfig0 ip=…", "VM depuis un template cloud-init"), ("vzdump 101 --storage pbs --mode snapshot", "sauvegarde vers Proxmox Backup Server"),
 ("ha-manager add vm:101 --state started ; ha-manager status", "haute disponibilité"), ("pveum user token add ci@pve terraform", "token d'API pour l'IaC"),
 ("acli vm.list ; acli vm.create … ; acli vm.on web1", "Nutanix AHV"), ("acli vm.snapshot_create web1 snapshot_name=x", "snapshot"), ("ncli cluster info ; cluster status ; ncc health_checks run_all", "état et santé Nutanix"),
 ("terraform : providers bpg/proxmox et nutanix/nutanix", "VM en code"), ("ansible : community.general.proxmox_* et nutanix.ncp", "configuration et inventaire dynamique")],
 ["Jamais de clic dans Prism ni Proxmox : templates Packer/cloud-init, Terraform, Ansible avec inventaire dynamique ; comptes et tokens d'API à droits minimaux.",
  "Proxmox : trois nœuds ou QDevice pour le quorum, réseaux dédiés corosync et Ceph, Proxmox Backup Server séparé, MFA, mises à jour Debian.",
  "Nutanix : tout passe par les catégories (Flow, protection, placement), LCM pour les mises à jour, NCC avant toute opération, Move pour migrer depuis VMware.",
  "Traiter la plateforme comme un service : SLO, sauvegardes testées, monitoring par exporters, PRA par réplication entre sites.",
  "Sortie de VMware = projet de migration (chapitre 50) : inventaire, dépendances, vagues, retour arrière, décommissionnement effectif."]))
S.insert(7, ("openshift", "OpenShift", "Niveau 5, chapitre 25", [
 ("oc login URL --token=… ; oc whoami ; oc project proj", "connexion, identité, projet courant"), ("oc new-project proj ; oc new-app image --name=api", "projet ; déploiement en une commande"),
 ("oc expose svc api ; oc create route edge|passthrough|reencrypt …", "Routes"), ("oc get routes ; oc get is ; oc get bc ; oc start-build api --follow", "routes, imagestreams, builds"),
 ("oc rsh deploy/api ; oc debug deploy/api ; oc debug node/N", "shell ; copie de debug ; nœud"), ("oc get scc ; oc adm policy who-can use scc restricted-v2", "contraintes de sécurité"),
 ("oc policy add-role-to-user edit alice -n proj", "rôle par projet"), ("oc get clusterversion ; oc get co ; oc get mcp", "santé : version, opérateurs, pools"),
 ("oc adm upgrade --to-latest ; oc adm must-gather", "mise à jour ; diagnostic pour le support"), ("RUN chgrp -R 0 /app && chmod -R g=u /app ; USER 1001", "Dockerfile compatible UID arbitraire"),
 ("docker run --user 1000680000:0 --read-only img", "tester la contrainte OpenShift en local")],
 ["Kubernetes d'abord : tout ce que tu sais s'applique ; oc ajoute, ne remplace pas.",
  "Images sans root, UID arbitraire, groupe 0, ports > 1024, écriture dans des volumes ; jamais anyuid ni privileged pour contourner une SCC.",
  "Tout est opérateur : installer par abonnement, suivre les versions supportées, vérifier oc get co avant et après une mise à jour.",
  "Routes pour l'exposition (edge par défaut, passthrough pour mTLS), projets avec quotas et rôles admin/edit/view, monitoring intégré à activer pour les charges utilisateur.",
  "Pas de SSH sur RHCOS : MachineConfig par pool ; mises à jour par canaux, une mineure à la fois, EUS pour la stabilité."]))

# ---------------- niveaux : M = minimum (à connaître par cœur), C = confirmé, E = expert ----------------
# règles par section : liste de fragments pour M et pour E ; le reste est C
RULES = {
 'linux': (["ls -la","find /","du -sh","chmod 750","ps -ef","kill -15","cmd > out","grep -rn","tail -f","apt update","systemctl status","journalctl -u","uptime ;","ss -tulpn"], []),
 'bash': (["set -euo","${var:-","[[ -f","for s in","shellcheck","python:3.12"], ["bats/bats"]),
 'git': (["git status","git add -p","git log --oneline","git switch -c","git merge --no-ff","git reflog","git revert","git stash","git tag"], ["git bisect","gpg.format","git ls-tree"]),
 'docker': (["docker run -d","winpty docker run","docker exec","docker stop","docker build -t","docker network create","docker volume create","docker system df"], ["buildx build --platform","netshoot","wagoodman/dive"]),
 'compose': (["compose up -d","compose ps","compose run --rm"], ["--profile","--scale"]),
 'virt': (["pvecm status","qm start|shutdown","vzdump","acli vm.list","ncli cluster info"], []),
 'kubectl': (["get pods -A","describe pod","logs -f deploy","get events","apply -f","rollout status","scale deploy","exec -it deploy","port-forward","top pods","kind create cluster"], ["custom-columns","debug node/","--grace-period=0","etcdctl snapshot"]),
 'openshift': (["oc login","new-project","oc expose","oc rsh","clusterversion","chgrp -R 0","--user 1000680000"], ["oc adm upgrade"]),
 'helm': (["helm repo add","helm show values","upgrade --install","helm list","kubectl kustomize"], ["helm push"]),
 'terraform': (["terraform init","plan -out","apply tfplan","hashicorp/terraform:1.9"], ["-refresh-only","-detailed-exitcode","terraform test","providers lock","TF_LOG","terraform-docs"]),
 'ansible': (["-m ping","--check --diff","--limit web1","ansible-vault","ansible-galaxy","-vvv","willhallonline"], []),
 'aws': (["sso login","get-caller-identity","aws s3 ls","aws logs tail"], ["simulate-principal-policy","get-cost-and-usage"]),
 'vault': (["vault status","vault kv put","vault policy write","gitleaks"], ["rotate-root","raft snapshot"]),
 'supply': (["trivy image","trivy config"], ["cosign attest","cosign attach"]),
 'tls': (["s_client","x509 -in c.crt -noout -text","openssl req -x509","curl -v https","dig +short","nc -zv"], ["tcpdump"]),
 'pg': (["psql -U","\\dt ;","EXPLAIN ANALYZE","pg_dump","pg_isready"], ["lock_timeout","n_dead_tup","cnpg"]),
 'ci': (["stages / image","rules: - if","./mvnw -q verify","npm ci"], ["semantic-release","infracost"]),
 'obs': (["rate(http_server","100 * sum","histogram_quantile","{namespace="], ["topk(10"]),
}
def level(sec, cmd):
    m, e = RULES.get(sec, ([], []))
    if any(f in cmd for f in m): return 'M'
    if any(f in cmd for f in e): return 'E'
    return 'C'
BADGE = {'M': ('min', '★ Minimum'), 'C': ('conf', 'Confirmé'), 'E': ('exp', 'Expert')}
# bonnes pratiques : les deux premières = minimum, la dernière = expert, le reste confirmé

head = re.sub(r'<title>[^<]*</title>', '<title>Aide-mémoire — commandes et bonnes pratiques</title>', re.search(r'^.*?</head>', (out/'devops-niveau-0-fondations.html').read_text(), flags=re.S).group(0))
extra = """
.pagenav{display:flex;flex-wrap:wrap;gap:.6rem;margin-bottom:1rem;font-size:.9rem}
.pagenav a{color:#fff;text-decoration:none;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);padding:.3rem .75rem;border-radius:6px}
.pagenav a:hover{background:rgba(255,255,255,.2);color:#fff}
.cmd td:first-child{font-family:"JetBrains Mono",monospace;font-size:.82em;white-space:pre-wrap;word-break:break-word;width:48%}
.cmd td:nth-child(3),.cmd th:nth-child(3){width:7.5rem;white-space:nowrap}
.lv{display:inline-block;font-size:.72rem;font-weight:700;border-radius:999px;padding:.1rem .55rem;border:1px solid;font-family:"Atkinson Hyperlegible",system-ui,sans-serif;white-space:nowrap}
.lv.min{background:#FDECEC;border-color:#A11B1B;color:#A11B1B}
.lv.conf{background:var(--exo-soft);border-color:var(--exo);color:#7A4E00}
.lv.exp{background:var(--accent-soft);border-color:var(--accent);color:var(--accent-ink)}
:root[data-theme="dark"] .lv.min{background:#3A1616;color:#F29A9A;border-color:#F29A9A}
:root[data-theme="dark"] .lv.conf{color:#F3C77A}
.bp{background:var(--tp-soft);border-left:4px solid var(--tp);border-radius:0 var(--radius) var(--radius) 0;padding:.8rem 1rem;margin:1rem 0}
.bp strong.t{color:var(--tp);display:block;margin-bottom:.3rem}
.bp ol{margin:0;padding-left:1.3rem}
.bp li .lv{margin-left:.4rem;vertical-align:middle}
.jump{display:flex;flex-wrap:wrap;gap:.4rem;margin:1rem 0}
.jump a{text-decoration:none;font-size:.85rem;background:var(--paper);border:1px solid var(--line);border-radius:999px;padding:.25rem .7rem}
.jump a:hover{background:var(--accent-soft)}
.filter{width:100%;font:inherit;padding:.6rem .8rem;border:1px solid var(--line-strong);border-radius:8px;background:var(--paper);color:var(--ink);margin:.5rem 0 .6rem}
.lvbar{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin:0 0 .8rem;font-size:.85rem}
.lvbar button{font:inherit;font-size:.82rem;font-weight:700;border:1px solid var(--line-strong);background:var(--paper);color:var(--ink);border-radius:999px;padding:.25rem .75rem;cursor:pointer;min-height:32px}
.lvbar button.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.legend{font-size:.85rem;color:var(--muted);margin:.4rem 0 1rem}
.legend .lv{margin-right:.3rem}
.stat{font-size:.85rem;color:var(--muted);margin:.4rem 0 1rem}
body{padding-bottom:2rem}
@media (max-width:760px){.cmd td:nth-child(3){width:auto} .cmd td:first-child{width:auto}}
@media print{.pagenav,.jump,.filter,.lvbar{display:none}}
</style>"""
head = head.replace('</style>', extra, 1)

nM = nC = nE = 0
body = '''<body>
<header class="hero"><div class="in">
<div class="pagenav"><a href="index.html">← Accueil du parcours</a><a href="devops-fiches-entretien.html">Fiches entretien</a></div>
<div class="level">Aide-mémoire</div>
<h1>Toutes les commandes à connaître, et les bonnes pratiques par technologie</h1>
<p class="lead">Dix-huit technologies, les commandes du quotidien avec ce qu'elles font, cinq bonnes pratiques par outil, et sur chaque ligne un badge qui dit à quel niveau tu dois la connaître : <strong>★ Minimum</strong> = par cœur, sans réfléchir, dès le premier jour ; <strong>Confirmé</strong> = attendu d'un profil expérimenté ; <strong>Expert</strong> = ce qui fait la différence en mission.</p>
</div></header>
<div class="single">
<div class="legend"><span class="lv min">★ Minimum</span> à savoir taper de tête · <span class="lv conf">Confirmé</span> à savoir retrouver en une minute · <span class="lv exp">Expert</span> à connaître de nom, savoir quand l'utiliser</div>
<input class="filter" id="filter" type="search" placeholder="Filtrer : tape un mot (rebase, jsonpath, lock, serial…)" aria-label="Filtrer l'aide-mémoire">
<div class="lvbar"><span>Afficher :</span><button type="button" data-lv="all" class="on">Tout</button><button type="button" data-lv="min">★ Minimum seulement</button><button type="button" data-lv="minconf">Minimum + Confirmé</button><button type="button" data-lv="exp">Expert seulement</button><span class="stat" id="stat"></span></div>
<div class="jump">''' + ''.join(f'<a href="#{i}">{H.escape(t)}</a>' for i,t,_,_,_ in S) + '</div>\n'
for i,t,ref,cmds,bps in S:
    body += f'<article id="{i}"><div class="chaphead"><span class="chapnum">{H.escape(ref)}</span></div><h2>{H.escape(t)}</h2>'
    body += '<div class="tablewrap"><table class="cmd"><tr><th>Commande</th><th>Ce qu\'elle fait</th><th>À connaître</th></tr>'
    for c,d in cmds:
        lv = level(i, c); cls, lab = BADGE[lv]
        if lv=='M': nM+=1
        elif lv=='C': nC+=1
        else: nE+=1
        body += f'<tr data-lv="{lv}"><td>{H.escape(c)}</td><td>{H.escape(d)}</td><td><span class="lv {cls}">{lab}</span></td></tr>'
    body += '</table></div>'
    body += '<div class="bp"><strong class="t">Bonnes pratiques</strong><ol>'
    for k, b in enumerate(bps):
        lv = 'M' if k < 2 else ('E' if k == len(bps)-1 else 'C'); cls, lab = BADGE[lv]
        body += f'<li data-lv="{lv}">{H.escape(b)}<span class="lv {cls}">{lab}</span></li>'
    body += '</ol></div></article>\n'
body += '''</div>
<script>
(function(){
  var root=document.documentElement; try{ var t=localStorage.getItem('devops-theme'); if(t) root.setAttribute('data-theme',t); }catch(e){}
  document.querySelectorAll('table').forEach(function(t){ var rows=t.rows; if(!rows.length) return; var head=rows[0]; if(!head.querySelector('th')) return; head.classList.add('head');
    var labels=Array.prototype.map.call(head.cells,function(c){return c.textContent.trim();});
    for(var i=1;i<rows.length;i++){ var cells=rows[i].cells; for(var j=0;j<cells.length;j++){ if(cells[j].tagName==='TD') cells[j].setAttribute('data-label',labels[j]||''); } } t.classList.add('stack'); });
  var f=document.getElementById('filter'), lv='all', stat=document.getElementById('stat');
  function keep(el){ var l=el.getAttribute('data-lv'); if(lv==='all') return true; if(lv==='min') return l==='M'; if(lv==='minconf') return l!=='E'; if(lv==='exp') return l==='E'; return true; }
  function apply(){ var q=f.value.trim().toLowerCase(), n=0;
    document.querySelectorAll('article').forEach(function(a){ var any=false;
      a.querySelectorAll('table.cmd tr:not(.head)').forEach(function(r){ var ok=keep(r)&&(!q||r.textContent.toLowerCase().indexOf(q)>=0); r.style.display=ok?'':'none'; if(ok){any=true;n++;} });
      a.querySelectorAll('.bp li').forEach(function(l){ var ok=keep(l)&&(!q||l.textContent.toLowerCase().indexOf(q)>=0); l.style.display=ok?'':'none'; if(ok) any=true; });
      a.style.display=any?'':'none'; });
    stat.textContent=n+' commande'+(n>1?'s':'')+' affichée'+(n>1?'s':''); }
  f.addEventListener('input',apply);
  document.querySelectorAll('.lvbar button').forEach(function(b){ b.addEventListener('click',function(){ document.querySelectorAll('.lvbar button').forEach(function(x){x.classList.remove('on');}); b.classList.add('on'); lv=b.getAttribute('data-lv'); apply(); }); });
  try{ var saved=localStorage.getItem('devops-aide-lv'); if(saved){ var btn=document.querySelector('.lvbar button[data-lv="'+saved+'"]'); if(btn) btn.click(); } }catch(e){}
  document.querySelectorAll('.lvbar button').forEach(function(b){ b.addEventListener('click',function(){ try{ localStorage.setItem('devops-aide-lv', b.getAttribute('data-lv')); }catch(e){} }); });
  apply();
})();
</script>
</body></html>'''
(out/'devops-aide-memoire.html').write_text(head + '\n' + body)
print('sections', len(S), '| minimum', nM, 'confirmé', nC, 'expert', nE, '| total', nM+nC+nE)
