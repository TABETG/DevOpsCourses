import re, pathlib, html as H, math

p = pathlib.Path('/mnt/user-data/outputs/devops-niveau-0-fondations.html')
S = p.read_text()
assert 'class="fig manga"' not in S, 'déjà fait'

# ---------------------------------------------------------------- moteur de dessin
class Strip:
    def __init__(self, ident, title, panels=3, pw=236, ph=250):
        self.id = ident; self.title = title; self.pw = pw; self.ph = ph; self.n = panels
        self.w = panels*pw + (panels+1)*6; self.h = ph + 12; self.b = ''
    def panel_origin(self, i): return 6 + i*(self.pw+6), 6
    def frame(self, i):
        x, y = self.panel_origin(i)
        self.b += f'<clipPath id="{self.id}_c{i}"><rect x="{x}" y="{y}" width="{self.pw}" height="{self.ph}"/></clipPath>'
        self.b += f'<rect x="{x}" y="{y}" width="{self.pw}" height="{self.ph}" fill="#fff"/>'
        return x, y
    def close(self, i):
        x, y = self.panel_origin(i)
        self.b += f'<rect x="{x}" y="{y}" width="{self.pw}" height="{self.ph}" fill="none" stroke="#111" stroke-width="3"/>'
    def raw(self, s): self.b += s
    def tone(self, x, y, w, h, kind='dots'):  # trame
        self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{self.id}_{kind})"/>'
    def speedlines(self, cx, cy, r1, r2, n=28, sw=1.4):
        s = ''
        for k in range(n):
            a = 2*math.pi*k/n
            s += f'<line x1="{cx+r1*math.cos(a):.1f}" y1="{cy+r1*math.sin(a):.1f}" x2="{cx+r2*math.cos(a):.1f}" y2="{cy+r2*math.sin(a):.1f}" stroke="#111" stroke-width="{sw}"/>'
        self.b += s
    def bubble(self, x, y, w, lines, tail=None, fs=11, shout=False):
        h = 10 + len(lines)*(fs+4)
        if shout:  # bulle en étoile
            pts = []
            cx, cy = x+w/2, y+h/2; m = 18
            for k in range(m):
                a = 2*math.pi*k/m; r = (w/2+10 if k%2==0 else w/2-4); ry = (h/2+10 if k%2==0 else h/2-2)
                pts.append(f'{cx+r*math.cos(a):.1f},{cy+ry*math.sin(a):.1f}')
            self.b += f'<polygon points="{" ".join(pts)}" fill="#fff" stroke="#111" stroke-width="2"/>'
        else:
            self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{min(14, h/2)}" fill="#fff" stroke="#111" stroke-width="2"/>'
            if tail:
                tx, ty = tail; bx = min(max(tx, x+16), x+w-16)
                self.b += f'<polygon points="{bx-7},{y+h-1} {bx+7},{y+h-1} {tx},{ty}" fill="#fff" stroke="#111" stroke-width="2"/>'
                self.b += f'<line x1="{bx-7}" y1="{y+h-1}" x2="{bx+7}" y2="{y+h-1}" stroke="#fff" stroke-width="3"/>'
        for k, t in enumerate(lines):
            self.b += f'<text x="{x+w/2}" y="{y+8+fs+k*(fs+4)}" text-anchor="middle" font-size="{fs}" font-weight="700" fill="#111">{H.escape(t)}</text>'
    def caption(self, x, y, w, text, fs=10):  # cartouche narratif
        self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{fs+12}" fill="#fff" stroke="#111" stroke-width="2"/>'
        self.b += f'<text x="{x+w/2}" y="{y+fs+4}" text-anchor="middle" font-size="{fs}" font-style="italic" fill="#111">{H.escape(text)}</text>'
    def sfx(self, x, y, text, fs=26, rot=-12, color='#111'):
        self.b += f'<text x="{x}" y="{y}" transform="rotate({rot} {x} {y})" text-anchor="middle" font-size="{fs}" font-weight="900" font-style="italic" fill="{color}" stroke="#fff" stroke-width="6" paint-order="stroke" letter-spacing="1">{H.escape(text)}</text>'
    def label(self, x, y, text, fs=10):
        self.b += f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{fs}" font-weight="700" fill="#111">{H.escape(text)}</text>'
    # ---- personnages chibi
    def chara(self, x, y, who, expr='smile', scale=1.0, flip=False, arms='down'):
        """x,y = bas du personnage (pieds), centré"""
        s = scale; g = f'<g transform="translate({x},{y}) scale({-s if flip else s},{s})">'
        col = {'kai':'#111', 'mika':'#fff', 'sensei':'#ddd'}[who]      # couleur de la tenue
        hair = {'kai':'spiky', 'mika':'bob', 'sensei':'bald'}[who]
        # corps
        g += f'<path d="M-16,-44 L16,-44 L20,-6 L-20,-6 Z" fill="{col}" stroke="#111" stroke-width="2"/>'
        g += '<rect x="-14" y="-6" width="11" height="6" fill="#111"/><rect x="3" y="-6" width="11" height="6" fill="#111"/>'   # pieds
        if who == 'mika': g += '<circle cx="0" cy="-32" r="3" fill="#111"/><circle cx="0" cy="-22" r="3" fill="#111"/>'   # boutons
        if who == 'sensei': g += '<path d="M-16,-44 L16,-44 L12,-20 L-12,-20 Z" fill="#fff" stroke="#111" stroke-width="1.5"/>'  # tablier/kimono
        # bras
        if arms == 'down': g += '<line x1="-16" y1="-40" x2="-24" y2="-14" stroke="#111" stroke-width="3" stroke-linecap="round"/><line x1="16" y1="-40" x2="24" y2="-14" stroke="#111" stroke-width="3" stroke-linecap="round"/>'
        elif arms == 'up': g += '<line x1="-16" y1="-40" x2="-30" y2="-66" stroke="#111" stroke-width="3" stroke-linecap="round"/><line x1="16" y1="-40" x2="30" y2="-66" stroke="#111" stroke-width="3" stroke-linecap="round"/>'
        elif arms == 'point': g += '<line x1="-16" y1="-40" x2="-24" y2="-14" stroke="#111" stroke-width="3" stroke-linecap="round"/><line x1="16" y1="-40" x2="40" y2="-48" stroke="#111" stroke-width="3" stroke-linecap="round"/>'
        elif arms == 'head': g += '<line x1="-16" y1="-40" x2="-28" y2="-70" stroke="#111" stroke-width="3" stroke-linecap="round"/><line x1="16" y1="-40" x2="28" y2="-70" stroke="#111" stroke-width="3" stroke-linecap="round"/>'
        elif arms == 'cross': g += '<path d="M-16,-40 L10,-30 M16,-40 L-10,-30" stroke="#111" stroke-width="3" stroke-linecap="round" fill="none"/>'
        # tête
        g += '<circle cx="0" cy="-66" r="24" fill="#fff" stroke="#111" stroke-width="2"/>'
        if hair == 'spiky': g += '<path d="M-24,-70 L-22,-92 L-12,-80 L-6,-98 L2,-82 L10,-100 L14,-82 L24,-92 L24,-70 Q0,-84 -24,-70 Z" fill="#111"/>'
        elif hair == 'bob': g += '<path d="M-25,-62 L-25,-78 Q0,-100 25,-78 L25,-62 L18,-64 Q0,-80 -18,-64 Z" fill="#111"/><path d="M-25,-62 L-27,-40 L-19,-44 Z" fill="#111"/><path d="M25,-62 L27,-40 L19,-44 Z" fill="#111"/>'
        elif hair == 'bald': g += '<path d="M-24,-68 Q-28,-80 -20,-84 L-18,-70 Z" fill="#fff" stroke="#111" stroke-width="1.5"/><path d="M24,-68 Q28,-80 20,-84 L18,-70 Z" fill="#fff" stroke="#111" stroke-width="1.5"/><path d="M-14,-52 Q0,-36 14,-52 L12,-46 Q0,-30 -12,-46 Z" fill="#fff" stroke="#111" stroke-width="1.5"/>'   # cheveux blancs, barbe
        # yeux
        if who == 'sensei':
            g += '<path d="M-14,-66 Q-8,-72 -2,-66 M2,-66 Q8,-72 14,-66" stroke="#111" stroke-width="2.5" fill="none"/><circle cx="-8" cy="-64" r="7" fill="none" stroke="#111" stroke-width="1.5"/><circle cx="8" cy="-64" r="7" fill="none" stroke="#111" stroke-width="1.5"/>'
        else:
            if expr in ('shock','panic','angry','cry'):
                g += '<ellipse cx="-9" cy="-64" rx="6" ry="8" fill="#fff" stroke="#111" stroke-width="1.5"/><ellipse cx="9" cy="-64" rx="6" ry="8" fill="#fff" stroke="#111" stroke-width="1.5"/>'
                g += '<circle cx="-9" cy="-63" r="2.5" fill="#111"/><circle cx="9" cy="-63" r="2.5" fill="#111"/>'
            else:
                g += '<ellipse cx="-9" cy="-64" rx="5.5" ry="7" fill="#111"/><ellipse cx="9" cy="-64" rx="5.5" ry="7" fill="#111"/><circle cx="-7" cy="-67" r="2" fill="#fff"/><circle cx="11" cy="-67" r="2" fill="#fff"/>'
            if expr == 'angry': g += '<path d="M-16,-76 L-4,-72 M16,-76 L4,-72" stroke="#111" stroke-width="2.5"/>'
            if expr == 'happy': g += '<path d="M-15,-64 Q-9,-72 -3,-64 M3,-64 Q9,-72 15,-64" stroke="#111" stroke-width="2.5" fill="none"/>'
        # bouche
        if expr in ('smile','happy'): g += '<path d="M-7,-52 Q0,-46 7,-52" stroke="#111" stroke-width="2" fill="none"/>'
        elif expr == 'shock': g += '<ellipse cx="0" cy="-50" rx="5" ry="7" fill="#111"/>'
        elif expr == 'panic': g += '<path d="M-8,-50 Q0,-44 8,-50 Q0,-56 -8,-50 Z" fill="#111"/>'
        elif expr == 'angry': g += '<path d="M-7,-48 Q0,-54 7,-48" stroke="#111" stroke-width="2" fill="none"/>'
        elif expr == 'cry': g += '<path d="M-6,-48 Q0,-54 6,-48" stroke="#111" stroke-width="2" fill="none"/><path d="M-14,-58 L-16,-44 L-11,-46 Z M14,-58 L16,-44 L11,-46 Z" fill="#111" opacity=".6"/>'
        elif expr == 'neutral': g += '<line x1="-6" y1="-50" x2="6" y2="-50" stroke="#111" stroke-width="2"/>'
        if expr in ('panic','shock'): g += '<path d="M22,-82 Q26,-72 22,-70 Q18,-72 22,-82 Z" fill="#fff" stroke="#111" stroke-width="1.5"/>'   # goutte de sueur
        if who == 'mika': g += '<path d="M-24,-70 Q-30,-56 -20,-52 L-14,-54" stroke="#111" stroke-width="2" fill="none"/>'  # casque
        g += '</g>'
        self.b += g
    def render(self, caption):
        defs = (f'<pattern id="{self.id}_dots" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.2" fill="#111" opacity=".55"/></pattern>'
                f'<pattern id="{self.id}_lines" width="6" height="6" patternUnits="userSpaceOnUse"><line x1="0" y1="6" x2="6" y2="0" stroke="#111" stroke-width="1" opacity=".5"/></pattern>'
                f'<pattern id="{self.id}_dark" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="4" fill="#111"/><circle cx="2" cy="2" r="1" fill="#fff" opacity=".35"/></pattern>')
        return (f'<figure class="fig manga"><svg viewBox="0 0 {self.w} {self.h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{H.escape(self.title)}">'
                f'<defs>{defs}</defs><rect width="{self.w}" height="{self.h}" fill="#111"/>{self.b}</svg><figcaption>{caption}</figcaption></figure>')

STRIPS = []

# ---------------------------------------------------------------- 1. Le mur
s = Strip("mg1", "Manga : le mur entre Dev et Ops")
x, y = s.frame(0); s.raw(f'<g clip-path="url(#{s.id}_c0)">'); s.tone(x, y, s.pw, 90, 'lines')
s.raw(f'<rect x="{x+108}" y="{y+40}" width="20" height="210" fill="url(#{s.id}_dark)" stroke="#111" stroke-width="2"/>')
s.chara(x+60, y+236, 'kai', 'happy', arms='up'); s.raw(f'<rect x="{x+96}" y="{y+54}" width="34" height="24" fill="#fff" stroke="#111" stroke-width="2"/><text x="{x+113}" y="{y+70}" text-anchor="middle" font-size="9" font-weight="700">v2.zip</text>')
s.speedlines(x+113, y+66, 22, 36, 10, 1.2)
s.chara(x+180, y+236, 'mika', 'neutral', flip=True)
s.bubble(x+6, y+8, 96, ["C'est fini !", "À vous de le", "faire tourner !"], tail=(x+60, y+130), fs=10)
s.caption(x+130, y+214, 100, "vendredi, 17 h 55"); s.sfx(x+160, y+70, "HOP !", 22, -20)
s.raw('</g>'); s.close(0)
x, y = s.frame(1); s.raw(f'<g clip-path="url(#{s.id}_c1)">'); s.tone(x, y, s.pw, s.ph, 'dots')
s.raw(f'<circle cx="{x+40}" cy="{y+36}" r="16" fill="#fff" stroke="#111" stroke-width="2"/>')   # lune
s.chara(x+118, y+236, 'mika', 'panic', arms='head'); s.speedlines(x+118, y+150, 60, 90, 24, 1)
s.bubble(x+30, y+22, 176, ["Ça ne démarre pas !", "Quelle version de Java ?!", "Pourquoi le port 8080 ?!"], fs=10, shout=True)
s.caption(x+8, y+214, 150, "samedi, 3 h 12, en production"); s.sfx(x+196, y+120, "BIP BIP", 18, 10)
s.raw('</g>'); s.close(1)
x, y = s.frame(2); s.raw(f'<g clip-path="url(#{s.id}_c2)">')
s.raw(f'<rect x="{x+76}" y="{y+150}" width="84" height="60" fill="#fff" stroke="#111" stroke-width="2"/><text x="{x+118}" y="{y+172}" text-anchor="middle" font-size="9" font-weight="700">pipeline</text><text x="{x+118}" y="{y+186}" text-anchor="middle" font-size="9" font-weight="700">logs</text><text x="{x+118}" y="{y+200}" text-anchor="middle" font-size="9" font-weight="700">astreinte</text>')
s.chara(x+50, y+236, 'kai', 'happy'); s.chara(x+186, y+236, 'mika', 'happy', flip=True)
s.bubble(x+8, y+8, 220, ["« You build it, you run it. »", "Le même code, la même équipe,", "la même responsabilité."], fs=10)
s.sfx(x+118, y+120, "DevOps", 24, 0)
s.raw('</g>'); s.close(2)
STRIPS.append(("1.1", s.render("Le mur : le développeur lance le code par-dessus, l'ops le reçoit la nuit. DevOps, c'est retirer le mur, pas ajouter un outil.")))

# ---------------------------------------------------------------- 2. PID 1
s = Strip("mg2", "Manga : PID 1 et le signal ignoré")
x, y = s.frame(0); s.raw(f'<g clip-path="url(#{s.id}_c0)">')
s.raw(f'<rect x="{x+20}" y="{y+40}" width="196" height="150" rx="10" fill="none" stroke="#111" stroke-width="3" stroke-dasharray="8 5"/><text x="{x+118}" y="{y+32}" text-anchor="middle" font-size="10" font-weight="700">conteneur</text>')
s.chara(x+70, y+186, 'kai', 'neutral', scale=.9); s.label(x+70, y+200, "sh (PID 1)", 10)
s.chara(x+170, y+186, 'mika', 'smile', scale=.9); s.label(x+170, y+200, "java (PID 7)", 10)
s.raw(f'<text x="{x+30}" y="{y+72}" font-size="16" font-weight="900">SIGTERM ↓</text>')
s.bubble(x+30, y+210, 176, ["ENTRYPOINT java -jar app.jar", "(forme shell : sh d'abord)"], fs=9)
s.raw('</g>'); s.close(0)
x, y = s.frame(1); s.raw(f'<g clip-path="url(#{s.id}_c1)">'); s.tone(x, y, s.pw, s.ph, 'lines')
s.chara(x+70, y+186, 'kai', 'neutral', scale=.9, arms='cross'); s.chara(x+170, y+186, 'mika', 'smile', scale=.9)
s.bubble(x+14, y+10, 130, ["Un signal ?", "Pas pour moi.", "Je ne transmets rien."], tail=(x+70, y+118), fs=10)
s.bubble(x+120, y+120, 100, ["…tout va bien,", "non ?"], tail=(x+170, y+160), fs=10)
s.caption(x+8, y+214, 150, "10 secondes plus tard…")
s.raw('</g>'); s.close(1)
x, y = s.frame(2); s.raw(f'<g clip-path="url(#{s.id}_c2)">'); s.speedlines(x+118, y+120, 40, 130, 36, 1.6)
s.chara(x+70, y+200, 'kai', 'shock', scale=.9); s.chara(x+170, y+200, 'mika', 'panic', scale=.9, arms='head')
s.sfx(x+118, y+70, "SIGKILL !", 30, -8)
s.bubble(x+10, y+200, 216, ["Requêtes coupées, transaction perdue.", "Solution : la forme exec", "ENTRYPOINT [\"java\",\"-jar\",\"app.jar\"]"], fs=8.5)
s.raw('</g>'); s.close(2)
STRIPS.append(("2.3", s.render("En forme shell, sh est PID 1 et n'a aucun gestionnaire de signal : java n'est jamais prévenu. En forme exec, java est PID 1 et s'arrête proprement.")))

# ---------------------------------------------------------------- 3. Could not resolve host
s = Strip("mg3", "Manga : diagnostiquer de gauche à droite")
x, y = s.frame(0); s.raw(f'<g clip-path="url(#{s.id}_c0)">')
s.raw(f'<rect x="{x+20}" y="{y+120}" width="130" height="80" rx="6" fill="#fff" stroke="#111" stroke-width="2"/><text x="{x+85}" y="{y+150}" text-anchor="middle" font-size="9" font-family="JetBrains Mono, monospace">$ curl https://api…</text><text x="{x+85}" y="{y+166}" text-anchor="middle" font-size="9" font-family="JetBrains Mono, monospace" font-weight="700">Could not resolve host</text>')
s.chara(x+190, y+236, 'kai', 'panic', flip=True, arms='head')
s.bubble(x+90, y+8, 138, ["C'est le réseau !", "Non, le pare-feu !", "Non, le certificat !"], tail=(x+190, y+130), fs=10, shout=True)
s.raw('</g>'); s.close(0)
x, y = s.frame(1); s.raw(f'<g clip-path="url(#{s.id}_c1)">'); s.tone(x, y, s.pw, 60, 'dots')
s.chara(x+60, y+206, 'sensei', 'smile', arms='point'); s.chara(x+190, y+206, 'kai', 'neutral', flip=True)
s.bubble(x+8, y+8, 220, ["Lis le message. « resolve »,", "c'est le DNS. Le reste vient après :", "DNS → TCP → TLS → HTTP."], tail=(x+60, y+100), fs=10)
s.caption(x+8, y+218, 220, "$ dig +short api.crisisshield.example", 9)
s.raw('</g>'); s.close(1)
x, y = s.frame(2); s.raw(f'<g clip-path="url(#{s.id}_c2)">')
s.chara(x+118, y+200, 'kai', 'happy', arms='up'); s.speedlines(x+118, y+120, 60, 100, 20, 1)
s.sfx(x+118, y+50, "TROUVÉ !", 26, -6)
s.bubble(x+14, y+204, 208, ["L'enregistrement DNS manquait en staging.", "Cinq minutes, pas trois heures."], fs=9)
s.raw('</g>'); s.close(2)
STRIPS.append(("3.1", s.render("Chaque étape a son message d'erreur ; on lit le message et on va droit à la couche fautive au lieu de tout soupçonner à la fois.")))

# ---------------------------------------------------------------- 4. set -euo pipefail
s = Strip("mg4", "Manga : le script qui continue après l'erreur")
x, y = s.frame(0); s.raw(f'<g clip-path="url(#{s.id}_c0)">')
s.raw(f'<rect x="{x+16}" y="{y+16}" width="204" height="86" rx="6" fill="#111"/>')
for k, t in enumerate(["#!/bin/bash", "cd /var/backups/$APP", "rm -rf ./*", "cp -r /data/$APP ."]):
    s.raw(f'<text x="{x+26}" y="{y+36+k*18}" font-size="10" font-family="JetBrains Mono, monospace" style="fill:#fff">{H.escape(t)}</text>')
s.chara(x+118, y+236, 'kai', 'smile'); s.bubble(x+120, y+110, 108, ["Sauvegarde", "automatique,", "trop simple."], tail=(x+130, y+170), fs=10)
s.raw('</g>'); s.close(0)
x, y = s.frame(1); s.raw(f'<g clip-path="url(#{s.id}_c1)">'); s.tone(x, y, s.pw, s.ph, 'lines')
s.raw(f'<rect x="{x+16}" y="{y+16}" width="204" height="52" rx="6" fill="#fff" stroke="#111" stroke-width="2"/>')
s.raw(f'<text x="{x+118}" y="{y+36}" text-anchor="middle" font-size="10" font-family="JetBrains Mono, monospace">$APP est vide ce soir-là</text><text x="{x+118}" y="{y+54}" text-anchor="middle" font-size="10" font-family="JetBrains Mono, monospace" font-weight="700">cd /var/backups/ : échoue…</text>')
s.chara(x+118, y+206, 'kai', 'neutral', scale=.95); s.bubble(x+40, y+82, 156, ["…et le script", "continue quand même."], tail=(x+118, y+130), fs=10)
s.caption(x+8, y+218, 212, "cd a échoué, rm s'exécute quand même")
s.raw('</g>'); s.close(1)
x, y = s.frame(2); s.raw(f'<g clip-path="url(#{s.id}_c2)">'); s.speedlines(x+118, y+110, 50, 140, 40, 1.4)
s.chara(x+118, y+236, 'kai', 'cry', arms='head'); s.sfx(x+118, y+60, "rm -rf ./*", 24, -8)
s.bubble(x+10, y+188, 216, ["Dans /var/backups. Tout.", "set -euo pipefail : le script s'arrête", "au premier échec. Toujours en tête."], fs=9)
s.raw('</g>'); s.close(2)
STRIPS.append(("4.1", s.render("Sans set -e, un cd qui échoue est ignoré et le rm s'exécute ailleurs. Trois options en tête de script évitent la catégorie entière d'accidents.")))

# ---------------------------------------------------------------- 5. git reflog
s = Strip("mg5", "Manga : le reflog te sauve")
x, y = s.frame(0); s.raw(f'<g clip-path="url(#{s.id}_c0)">'); s.tone(x, y, s.pw, s.ph, 'dots')
s.raw(f'<rect x="{x+16}" y="{y+150}" width="204" height="40" rx="6" fill="#fff" stroke="#111" stroke-width="2"/>')
s.raw(f'<text x="{x+118}" y="{y+175}" text-anchor="middle" font-size="11" font-family="JetBrains Mono, monospace" font-weight="700">$ git reset --hard HEAD~3</text>')
s.chara(x+118, y+140, 'kai', 'shock', scale=.9, arms='head'); s.speedlines(x+118, y+80, 40, 70, 20, 1)
s.bubble(x+40, y+18, 156, ["Trois commits… envolés ?!", "Une journée de travail !"], fs=9, shout=True)
s.caption(x+8, y+214, 140, "Rien n'est poussé. Panique.")
s.raw('</g>'); s.close(0)
x, y = s.frame(1); s.raw(f'<g clip-path="url(#{s.id}_c1)">')
s.chara(x+60, y+206, 'sensei', 'smile', arms='point'); s.chara(x+190, y+206, 'kai', 'cry', flip=True)
s.bubble(x+8, y+8, 220, ["Git ne perd rien pendant 90 jours.", "Tout ce que HEAD a pointé", "est dans le reflog."], tail=(x+60, y+100), fs=10)
s.caption(x+8, y+218, 220, "$ git reflog", 9)
s.raw('</g>'); s.close(1)
x, y = s.frame(2); s.raw(f'<g clip-path="url(#{s.id}_c2)">')
s.raw(f'<rect x="{x+16}" y="{y+16}" width="204" height="70" rx="6" fill="#111"/>')
for k, t in enumerate(["e3f9a1 HEAD@{0}: reset: moving to HEAD~3", "7b2c44 HEAD@{1}: commit: feat: cache", "$ git reset --hard HEAD@{1}"]):
    s.raw(f'<text x="{x+22}" y="{y+34+k*18}" font-size="8.5" font-family="JetBrains Mono, monospace" style="fill:#fff">{H.escape(t)}</text>')
s.chara(x+118, y+236, 'kai', 'happy', arms='up'); s.sfx(x+118, y+130, "SAUVÉ !", 24, -6)
s.bubble(x+30, y+196, 176, ["reflog = filet de sécurité.", "reset --hard n'est pas la mort."], fs=9)
s.raw('</g>'); s.close(2)
STRIPS.append(("5.3", s.render("Un reset --hard n'efface pas les commits : il déplace la branche. Le reflog garde chaque position de HEAD ; on y revient en une commande.")))

# ---------------------------------------------------------------- 6. Seq Scan
s = Strip("mg6", "Manga : le Seq Scan qui grossit")
x, y = s.frame(0); s.raw(f'<g clip-path="url(#{s.id}_c0)">')
s.raw(f'<rect x="{x+30}" y="{y+120}" width="90" height="80" rx="6" fill="#fff" stroke="#111" stroke-width="2"/>')
for k in range(4): s.raw(f'<line x1="{x+40}" y1="{y+136+k*16}" x2="{x+110}" y2="{y+136+k*16}" stroke="#111" stroke-width="2"/>')
s.label(x+75, y+212, "1 000 lignes", 10)
s.chara(x+180, y+236, 'kai', 'happy', flip=True)
s.bubble(x+108, y+8, 122, ["SELECT * WHERE zone = ?", "12 ms. Parfait.", "Pas besoin d'index."], tail=(x+180, y+130), fs=9)
s.caption(x+8, y+218, 100, "en développement")
s.raw('</g>'); s.close(0)
x, y = s.frame(1); s.raw(f'<g clip-path="url(#{s.id}_c1)">'); s.tone(x, y, s.pw, s.ph, 'lines')
s.raw(f'<rect x="{x+20}" y="{y+60}" width="120" height="150" rx="6" fill="#fff" stroke="#111" stroke-width="2"/>')
for k in range(9): s.raw(f'<line x1="{x+30}" y1="{y+76+k*15}" x2="{x+130}" y2="{y+76+k*15}" stroke="#111" stroke-width="2"/>')
s.label(x+80, y+226, "1 000 000 lignes", 10)
s.chara(x+190, y+236, 'mika', 'panic', flip=True, arms='head'); s.speedlines(x+190, y+150, 50, 80, 18, 1)
s.bubble(x+130, y+16, 96, ["12 secondes !", "La prod rame,", "l'astreinte sonne."], fs=9.5, shout=True)
s.caption(x+8, y+8, 92, "six mois plus tard")
s.raw('</g>'); s.close(1)
x, y = s.frame(2); s.raw(f'<g clip-path="url(#{s.id}_c2)">')
s.chara(x+60, y+206, 'sensei', 'smile', arms='point'); s.chara(x+190, y+206, 'kai', 'neutral', flip=True)
s.bubble(x+8, y+8, 220, ["EXPLAIN ANALYZE : Seq Scan.", "Le temps suit la table.", "Un index, et il suit le log."], tail=(x+60, y+100), fs=10)
s.caption(x+8, y+218, 220, "CREATE INDEX CONCURRENTLY ON incidents (zone);", 8)
s.sfx(x+196, y+112, "12 ms", 18, 8)
s.raw('</g>'); s.close(2)
STRIPS.append(("6.1", s.render("Rapide sur mille lignes, catastrophique sur un million : EXPLAIN ANALYZE montre le Seq Scan, l'index le remplace par une recherche en log(n).")))

# ---------------------------------------------------------------- insertion
CSS = """
/* ============ Planches manga ============ */
.fig.manga svg{min-width:600px;border-radius:6px}
.fig.manga svg text{font-family:"Atkinson Hyperlegible",system-ui,sans-serif;fill:#111}
.fig.manga figcaption::before{content:"Manga — ";font-weight:700;color:var(--ink)}
:root[data-theme="dark"] .fig.manga svg{opacity:.94}
</style>"""
S = S.replace('</style>', CSS, 1)
for sec, svg in STRIPS:
    m = re.search(r'<h3>' + re.escape(sec) + r' [^<]*(?:<span class="badge[^<]*</span>)?</h3>', S); assert m, sec
    # après le titre, avant tout le reste (schéma statique ou animation compris) : la planche ouvre la section
    S = S[:m.end()] + '\n' + svg + S[m.end():]
p.write_text(S); print('planches :', S.count('class="fig manga"'))

ip = pathlib.Path('/mnt/user-data/outputs/devops-parcours-complet.html'); t = ip.read_text()
if 'Manga' not in t:
    t = t.replace('<li><strong>Animations</strong> (niveau 0)', '<li><strong>Manga</strong> (niveau 0) : six planches de trois cases avec Kaï le développeur, Mika l\'ops et Sensei Ohno, une par chapitre, qui racontent le piège du chapitre (le mur Dev/Ops, PID 1 et SIGKILL, « Could not resolve host », le script sans set -e, le reflog, le Seq Scan).</li>\n<li><strong>Animations</strong> (niveau 0)', 1)
    ip.write_text(t); print('index ok')
