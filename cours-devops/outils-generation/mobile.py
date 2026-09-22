import re, glob, pathlib

MOBILE_CSS = """
/* ============ Lisibilité mobile ============ */
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{overflow-x:hidden}
a,code,.tag,h1,h2,h3,h4,p,li,td,th{overflow-wrap:anywhere}
pre{overflow-wrap:normal}
/* Repli pour les navigateurs sans color-mix */
tr:nth-child(even) td{background:var(--bg)}
.note{background:var(--bg)}
@supports (color: color-mix(in srgb, red, blue)){
  tr:nth-child(even) td{background:color-mix(in srgb,var(--paper) 93%,var(--ink))}
  .note{background:color-mix(in srgb,var(--paper) 94%,var(--ink))}
}
/* Blocs de code : replié sur mobile, sauf les schémas */
@media (max-width:760px){
  pre{white-space:pre-wrap;word-break:break-word;overflow-wrap:anywhere;font-size:.82em;line-height:1.55;padding:2.4rem .9rem .9rem}
  pre.diagram{white-space:pre;word-break:normal;overflow-wrap:normal;overflow-x:auto;font-size:.72em}
  pre .copy{top:.45rem;right:.45rem;opacity:.85;padding:.3rem .7rem;font-size:.8rem}
}
/* Tableaux empilés en fiches sur petit écran */
@media (max-width:640px){
  .tablewrap{border:none;overflow:visible;margin:1rem 0}
  table.stack{display:block;width:100%}
  table.stack tbody,table.stack thead{display:block;width:100%}
  table.stack tr{display:block;border:1px solid var(--line);border-radius:10px;background:var(--paper);padding:.55rem .8rem;margin:0 0 .7rem}
  table.stack tr.head{display:none}
  table.stack th,table.stack td{display:block;width:100%;border:none;padding:.3rem 0;background:none !important}
  table.stack td::before{content:attr(data-label);display:block;font-size:.76rem;font-weight:700;color:var(--accent-ink);margin-bottom:.1rem}
  table.stack td:empty,table.stack td[data-label=""]:empty{display:none}
  table.stack th{font-weight:700;color:var(--accent-ink);padding-bottom:.35rem;border-bottom:1px solid var(--line);margin-bottom:.25rem}
}
/* Tailles et marges sur téléphone */
@media (max-width:480px){
  body{font-size:16px;line-height:1.6}
  .hero{padding:2rem 1rem 1.6rem}
  .hero .level{font-size:.8rem}
  h1{font-size:1.75rem;line-height:1.15}
  .hero p.lead{font-size:1rem}
  .hero .meta{gap:.4rem;font-size:.85rem}
  .hero .meta span{padding:.25rem .55rem}
  .wrap,.single{padding:1rem .8rem 4rem}
  article,.rev{padding:1rem .85rem 1.2rem;border-radius:10px}
  article h2{font-size:1.45rem}
  h2{font-size:1.4rem;margin-top:2.2rem}
  h3{font-size:1.08rem;margin-top:1.6rem;padding-left:.6rem}
  h4{font-size:1rem}
  .objectifs,.exo,.tp,.entretien,.niche,.note{padding:.75rem .85rem;margin:1rem 0;border-radius:8px}
  .tp .tag{font-size:1rem}
  .badge{font-size:.7rem;padding:.12rem .5rem;margin-left:.3rem}
  .chaphead{gap:.3rem}
  ul,ol{padding-left:1.2rem}
  .tp ol,.tp ul{padding-left:1.1rem}
  summary{padding:.4rem .8rem;font-size:.9rem}
  .check{padding:.7rem .8rem;margin-top:1.3rem}
  .quiz li{padding-left:2.3rem}
  .quiz li::before{width:1.7rem;height:1.7rem;font-size:.75rem}
  nav.toc{padding:.8rem .8rem}
  nav.toc a{padding:.35rem .65rem;font-size:.85rem}
  .legend{font-size:.82rem}
  .lvl{padding:.9rem .9rem}
  .lvl .n{font-size:1.4rem;min-width:1.8rem}
  .lvl h3{font-size:1.05rem}
  .lvl a.btn{padding:.5rem .9rem}
  .footnav a{padding:.55rem .8rem;font-size:.92rem;flex:1 1 100%;text-align:center}
  .pagenav a{font-size:.85rem}
  button.theme{margin-top:1rem}
}
/* Cibles tactiles */
@media (pointer:coarse){
  summary,.check,nav.toc a,.lvl a.btn,.footnav a,pre .copy,button.theme{min-height:40px;display:inline-flex;align-items:center}
  .check{display:flex}
  nav.toc a{display:flex}
}
</style>"""

MOBILE_JS = """
<script>
(function(){
  // Tableaux : libell\u00e9 de colonne sur chaque cellule pour l'affichage empil\u00e9
  document.querySelectorAll('table').forEach(function(t){
    var rows=t.rows; if(!rows.length) return;
    var head=rows[0]; var ths=head.querySelectorAll('th');
    if(!ths.length) return;
    head.classList.add('head');
    var labels=Array.prototype.map.call(head.cells,function(c){return c.textContent.trim();});
    for(var i=1;i<rows.length;i++){
      var cells=rows[i].cells;
      for(var j=0;j<cells.length;j++){ if(cells[j].tagName==='TD') cells[j].setAttribute('data-label',labels[j]||''); }
    }
    t.classList.add('stack');
  });
  // Sch\u00e9mas ASCII : garder l'alignement (d\u00e9filement horizontal) au lieu du repli
  document.querySelectorAll('pre').forEach(function(p){
    if(/[\\u2500-\\u257F\\u25B6\\u25C0\\u25BA\\u25C4\\u2192\\u2190\\u2191\\u2193]/.test(p.textContent)) p.classList.add('diagram');
  });
})();
</script>
"""

out = pathlib.Path('/mnt/user-data/outputs')
for f in sorted(out.glob('devops-*.html')):
    s = f.read_text()
    if 'Lisibilité mobile' in s:
        print(f.name, 'déjà fait'); continue
    s = s.replace('</style>', MOBILE_CSS, 1)
    s = s.replace('</body>', MOBILE_JS + '</body>', 1)
    # viewport : autoriser le zoom, largeur de l'appareil
    s = s.replace('<meta name="viewport" content="width=device-width, initial-scale=1">',
                  '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">', 1)
    f.write_text(s)
    print(f.name, 'ok')
