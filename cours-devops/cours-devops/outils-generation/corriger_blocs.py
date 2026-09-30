"""Corrige les pages déjà générées : tableaux affichés comme du code, check-lists et listes de questions
mises dans des blocs de code. Usage : python3 corriger_blocs.py <page> [<page> …]"""
import sys, re, html
def questions(txt):
    parts = re.split(r'(?:^|\s)(\d{1,2}) (?=\S)', ' ' + txt.strip())
    items = [parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)]
    nums = [int(parts[i]) for i in range(1, len(parts) - 1, 2)]
    if len(items) < 15 or nums[:3] != [1, 2, 3]: return None
    def li(t):
        k = t.find('?')
        return f'<li><strong>{html.escape(t[:k + 1])}</strong> {html.escape(t[k + 1:].strip())}</li>' if 0 < k < 120 else f'<li>{html.escape(t)}</li>'
    return '<ol class="questions">' + ''.join(li(t) for t in items) + '</ol>'
def controle(txt):
    lignes = [l.rstrip() for l in txt.strip().split('\n') if l.strip()]
    cases = [l for l in lignes if l.lstrip().startswith('[ ]')]
    if len(cases) < 3 or len(cases) < len(lignes) * 0.6: return None
    out = ''
    for l in lignes:
        if l.lstrip().startswith('[ ]'): continue
        if lignes.index(l) < lignes.index(cases[0]): out += f'<p class="liste-titre">{html.escape(l.strip())}</p>'
    out += '<ul class="liste-controle">' + ''.join(f'<li>{html.escape(l.lstrip()[3:].strip())}</li>' for l in cases) + '</ul>'
    fin = [l for l in lignes if not l.lstrip().startswith('[ ]') and lignes.index(l) > lignes.index(cases[-1])]
    out += ''.join(f'<p>{html.escape(l.strip())}</p>' for l in fin)
    return out
for f in sys.argv[1:]:
    s = open(f).read(); n = {'tableaux': 0, 'questions': 0, 'controles': 0}
    def rep(m):
        brut = html.unescape(m.group(1))
        if brut.lstrip().startswith('<div class="tablewrap">'): n['tableaux'] += 1; return brut
        q = questions(brut) if re.match(r'\s*1 \S', brut) and re.search(r'\s(29|30|40) \S', brut) else None
        if q: n['questions'] += 1; return q
        c = controle(brut)
        if c: n['controles'] += 1; return c
        return m.group(0)
    s = re.sub(r'<pre><code>(.*?)</code></pre>', rep, s, flags=re.S)
    s = s.replace('<p></p>', '')
    s = re.sub(r'<p>(<div class="tablewrap">.*?</table></div>)</p>', r'\1', s, flags=re.S)
    open(f, 'w').write(s); print(f, n)
