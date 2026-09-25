"""Prépare la version en ligne d'une page locale : liens claude.ai + charte (--online). Usage : prep_online.py <nom> [<nom>…]"""
import pathlib,runpy,sys,re
P=pathlib.Path('/mnt/user-data/outputs/pub'); P.mkdir(exist_ok=True); names=sys.argv[1:]; sys.argv=['x',str(P),'--online']; g=runpy.run_path('/home/claude/restyle.py',run_name='x')
for name in names:
    s=pathlib.Path('/home/claude/work/cours-devops/'+name).read_text()
    for pat in [r'<style id="site-design">.*?</style>\n',r'<header class="topbar".*?</header>\n',r'<footer class="sitefooter">.*?</footer>\n',r'<script id="site-lightbox">.*?</script>\n',r'<script id="site-highlight">.*?</script>\n',r'<script id="site-toc">.*?</script>\n']: s=re.sub(pat,'',s,flags=re.S)
    ON=g['ONLINE']; s=re.sub(r'href="([a-z0-9-]+\.html)(#[^"]*)?"',lambda m:'href="'+ON[m.group(1)]+(m.group(2) or '')+'"' if m.group(1) in ON else m.group(0),s)
    s=re.sub(r'<p><strong>Correction type :</strong> <a href="corrections/[^"]+">[^<]*</a>\.</p>\n?','',s)
    s=re.sub(r'<a href="corrections/[^"]+"[^>]*>([^<]*)</a>',r'\1',s)
    s=re.sub(r'<a href="images/[^"]+"[^>]*>(<img[^>]+>)</a>',r'\1',s)
    import base64
    s=re.sub(r'src="images/([^"]+)"',lambda m:'src="data:image/'+('webp' if m.group(1).endswith('.webp') else 'png')+';base64,'+base64.b64encode(pathlib.Path('/home/claude/work/cours-devops/images/'+m.group(1)).read_bytes()).decode()+'"',s)
    (P/name).write_text(s); g['restyle'](P/name,P,True); print(name, re.findall(r'href="[a-z0-9-]+\.html"',(P/name).read_text())[:2])
