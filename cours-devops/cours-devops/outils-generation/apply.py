import re, glob, pathlib
css = pathlib.Path('/home/claude/course.css').read_text()
fonts = '<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">'
extra_js = r'''
<script>
(function(){
  // Barre de lecture
  var bar=document.createElement('div'); bar.className='readbar'; document.body.prepend(bar);
  function upd(){ var h=document.documentElement; var max=h.scrollHeight-h.clientHeight; bar.style.width=(max>0?(h.scrollTop/max*100):0)+'%'; }
  window.addEventListener('scroll',upd,{passive:true}); upd();
  // Bouton copier sur chaque bloc de code
  document.querySelectorAll('pre').forEach(function(pre){
    var b=document.createElement('button'); b.type='button'; b.className='copy'; b.textContent='Copier'; b.setAttribute('aria-label','Copier le code');
    b.addEventListener('click',function(){
      var t=pre.innerText.replace(/^Copier\n?/,'').replace(/Copi\u00e9 !$/,'');
      var done=function(){ b.textContent='Copi\u00e9 !'; b.classList.add('ok'); setTimeout(function(){ b.textContent='Copier'; b.classList.remove('ok'); },1500); };
      if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(t).then(done,done); }
      else { var ta=document.createElement('textarea'); ta.value=t; document.body.appendChild(ta); ta.select(); try{document.execCommand('copy');}catch(e){} document.body.removeChild(ta); done(); }
    });
    pre.appendChild(b);
  });
  // Sommaire qui suit la lecture
  var links=document.querySelectorAll('nav.toc a[href^="#"]');
  if(links.length&&'IntersectionObserver' in window){
    var map={}; links.forEach(function(a){ map[a.getAttribute('href').slice(1)]=a; });
    var io=new IntersectionObserver(function(entries){
      entries.forEach(function(e){ if(e.isIntersecting){ links.forEach(function(a){a.classList.remove('active');}); var a=map[e.target.id]; if(a) a.classList.add('active'); } });
    },{rootMargin:'-10% 0px -75% 0px'});
    Object.keys(map).forEach(function(id){ var el=document.getElementById(id); if(el) io.observe(el); });
  }
  // Impression : ouvrir tous les corrig\u00e9s
  window.addEventListener('beforeprint',function(){ document.querySelectorAll('details').forEach(function(d){ d.open=true; }); });
})();
</script>
'''
for f in sorted(glob.glob('devops-*.html')):
    s = pathlib.Path(f).read_text()
    s = re.sub(r'<link href="https://fonts\.googleapis\.com/css2[^>]*>', fonts, s, count=1)
    s = re.sub(r'<style>.*?</style>', '<style>\n'+css+'</style>', s, count=1, flags=re.S)
    # Retirer un éventuel script additionnel déjà présent, puis l'insérer avant </body>
    s = re.sub(r'\n<script>\n\(function\(\)\{\n  // Barre de lecture.*?</script>\n', '\n', s, count=1, flags=re.S)
    s = s.replace('</body>', extra_js+'</body>', 1)
    pathlib.Path(f).write_text(s)
    print(f, len(s))
