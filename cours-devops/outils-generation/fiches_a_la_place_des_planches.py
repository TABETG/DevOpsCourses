"""Remplace, dans des chapitres donnés, la planche manga par la fiche visuelle du chapitre (déplacée en tête de chapitre).
Idempotent. Usage : python3 fiches_a_la_place_des_planches.py <page> <premier chapitre> <dernier chapitre> <préfixe des fiches>
Exemple : python3 fiches_a_la_place_des_planches.py cours-75-latex.html 1 9 cours-75-"""
import sys, re
page, c1, c2, prefixe = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
s = open(page).read(); n = 0
for c in range(c1, c2 + 1):
    a = s.index(f'<article id="c{c}"'); b = s.index('</article>', a); art = s[a:b]
    fiche = re.search(r'<figure class="fig zoomable" id="' + re.escape(prefixe) + r'[^"]*">.*?</figure>', art, flags=re.S)
    planche = re.search(r'<figure class="fig manga">.*?</figure>', art, flags=re.S)
    if not fiche or not planche: continue
    f = fiche.group(0)
    art = art.replace(f, '', 1)                                   # retirer la fiche de sa place (fin de chapitre)
    art = re.sub(r'<figure class="fig manga">.*?</figure>', lambda m: f, art, count=1, flags=re.S)   # et la mettre à la place de la planche
    s = s[:a] + art + s[b:]; n += 1
open(page, 'w').write(s); print(page, ':', n, 'planches remplacées par leur fiche')
