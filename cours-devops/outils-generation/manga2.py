import re, pathlib, html as H, math

p = pathlib.Path('/mnt/user-data/outputs/devops-00-fondations.html')
S = p.read_text()
assert 'class="fig manga"' not in S, 'déjà des planches : restaurer d\'abord'

INK = '#111'

# ================================================================ moteur
class Strip:
    def __init__(self, ident, title, chapter, panels=(260, 260, 260), ph=290):
        self.id = ident; self.title = title; self.chapter = chapter
        self.pw = list(panels); self.ph = ph; self.gap = 8; self.top = 30
        self.w = sum(self.pw) + (len(panels)+1)*self.gap; self.h = self.top + ph + self.gap; self.b = ''
    def origin(self, i): return self.gap + sum(self.pw[:i]) + i*self.gap, self.top
    def begin(self, i):
        x, y = self.origin(i); w = self.pw[i]
        self.b += f'<clipPath id="{self.id}_c{i}"><rect x="{x}" y="{y}" width="{w}" height="{self.ph}"/></clipPath>'
        self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{self.ph}" fill="#fff"/><g clip-path="url(#{self.id}_c{i})">'
        return x, y, w
    def end(self, i):
        x, y = self.origin(i)
        self.b += f'</g><rect x="{x}" y="{y}" width="{self.pw[i]}" height="{self.ph}" fill="none" stroke="{INK}" stroke-width="3.5"/>'
    def raw(self, s): self.b += s
    # ---- fonds et effets
    def tone(self, x, y, w, h, kind='dots'): self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{self.id}_{kind})"/>'
    def night(self, x, y, w, h):
        self.tone(x, y, w, h, 'dark')
        self.b += f'<circle cx="{x+w-46}" cy="{y+40}" r="17" fill="#fff"/><circle cx="{x+w-54}" cy="{y+34}" r="14" fill="url(#{self.id}_dark)"/>'
        for k, (sx, sy) in enumerate([(30,26),(70,18),(120,40),(160,22),(50,60),(200,66)]):
            self.b += f'<path d="M{x+sx},{y+sy-4} L{x+sx+1.5},{y+sy-1} L{x+sx+4},{y+sy} L{x+sx+1.5},{y+sy+1} L{x+sx},{y+sy+4} L{x+sx-1.5},{y+sy+1} L{x+sx-4},{y+sy} L{x+sx-1.5},{y+sy-1} Z" fill="#fff"/>'
    def focus(self, cx, cy, r1, r2, n=40, sw=1.3):
        s = ''
        for k in range(n):
            a = 2*math.pi*k/n + (0.13 if k%2 else 0); rr = r2 + (14 if k%3==0 else 0)
            s += f'<line x1="{cx+r1*math.cos(a):.1f}" y1="{cy+r1*math.sin(a):.1f}" x2="{cx+rr*math.cos(a):.1f}" y2="{cy+rr*math.sin(a):.1f}" stroke="{INK}" stroke-width="{sw}"/>'
        self.b += s
    def speed(self, x, y, w, h, n=14):
        s = ''
        for k in range(n):
            yy = y + h*k/n; s += f'<line x1="{x}" y1="{yy:.1f}" x2="{x+w}" y2="{yy-10:.1f}" stroke="{INK}" stroke-width="{1+ (k%3)*0.4:.1f}" opacity=".7"/>'
        self.b += s
    def floor(self, x, y, w): self.b += f'<line x1="{x}" y1="{y}" x2="{x+w}" y2="{y}" stroke="{INK}" stroke-width="2"/>'
    # ---- décors
    def wall(self, x, y, w, h):
        self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{self.id}_brick)" stroke="{INK}" stroke-width="2.5"/>'
    def desk(self, x, y, w, laptop=True, screen_lines=(), monitor=False):
        self.b += f'<rect x="{x}" y="{y}" width="{w}" height="8" fill="#fff" stroke="{INK}" stroke-width="2.5"/><line x1="{x+10}" y1="{y+8}" x2="{x+10}" y2="{y+60}" stroke="{INK}" stroke-width="2.5"/><line x1="{x+w-10}" y1="{y+8}" x2="{x+w-10}" y2="{y+60}" stroke="{INK}" stroke-width="2.5"/>'
        if laptop:
            lx = x + w/2 - 34
            self.b += f'<path d="M{lx},{y} L{lx+68},{y} L{lx+62},{y-4} L{lx+6},{y-4} Z" fill="#fff" stroke="{INK}" stroke-width="2"/>'
            self.b += f'<rect x="{lx+6}" y="{y-50}" width="56" height="46" rx="3" fill="{INK}" stroke="{INK}" stroke-width="2"/>'
            for k, t in enumerate(screen_lines[:3]):
                self.b += f'<text x="{lx+10}" y="{y-38+k*12}" font-size="8" font-family="JetBrains Mono, monospace" style="fill:#fff">{H.escape(t)}</text>'
        if monitor:
            mx = x + w/2 - 46
            self.b += f'<rect x="{mx}" y="{y-74}" width="92" height="62" rx="4" fill="{INK}"/><rect x="{mx+40}" y="{y-12}" width="12" height="12" fill="{INK}"/>'
            for k, t in enumerate(screen_lines[:4]):
                self.b += f'<text x="{mx+6}" y="{y-60+k*13}" font-size="8.5" font-family="JetBrains Mono, monospace" style="fill:#fff">{H.escape(t)}</text>'
    def rack(self, x, y, w=60, h=140, alarm=False):
        self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#fff" stroke="{INK}" stroke-width="2.5"/>'
        for k in range(6):
            yy = y + 8 + k*22
            self.b += f'<rect x="{x+6}" y="{yy}" width="{w-12}" height="16" fill="url(#{self.id}_dots)" stroke="{INK}" stroke-width="1.5"/>'
            self.b += f'<circle cx="{x+w-14}" cy="{yy+8}" r="3" fill="{INK if not alarm or k%2 else "#fff"}" stroke="{INK}" stroke-width="1.2"/>'
        if alarm: self.b += f'<path d="M{x+w+6},{y+20} q8,-8 0,-16 M{x+w+12},{y+26} q14,-14 0,-28" fill="none" stroke="{INK}" stroke-width="2"/>'
    def phone(self, x, y, ring=True):
        self.b += f'<rect x="{x}" y="{y}" width="22" height="38" rx="4" fill="#fff" stroke="{INK}" stroke-width="2"/><rect x="{x+4}" y="{y+5}" width="14" height="24" fill="url(#{self.id}_dots)"/>'
        if ring: self.b += f'<path d="M{x-4},{y+6} q-8,12 0,24 M{x+26},{y+6} q8,12 0,24 M{x-10},{y+2} q-12,17 0,32 M{x+32},{y+2} q12,17 0,32" fill="none" stroke="{INK}" stroke-width="2"/>'
    def board(self, x, y, w, h, lines, title=None):
        self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{INK}" stroke="{INK}" stroke-width="3"/><rect x="{x-4}" y="{y-4}" width="{w+8}" height="{h+8}" fill="none" stroke="{INK}" stroke-width="2"/>'
        yy = y + 18
        if title: self.b += f'<text x="{x+w/2}" y="{yy}" text-anchor="middle" font-size="11" font-weight="700" style="fill:#fff">{H.escape(title)}</text>'; yy += 18
        for t in lines:
            self.b += f'<text x="{x+10}" y="{yy}" font-size="10" font-family="JetBrains Mono, monospace" style="fill:#fff">{H.escape(t)}</text>'; yy += 15
    def terminal(self, x, y, w, h, lines, fs=8.5):
        self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{INK}"/><rect x="{x}" y="{y}" width="{w}" height="12" rx="6" fill="#fff" stroke="{INK}" stroke-width="2"/><rect x="{x}" y="{y+8}" width="{w}" height="6" fill="{INK}"/>'
        for k in range(3): self.b += f'<circle cx="{x+9+k*10}" cy="{y+6}" r="2.5" fill="{INK}"/>'
        for k, t in enumerate(lines): self.b += f'<text x="{x+8}" y="{y+26+k*(fs+4)}" font-size="{fs}" font-family="JetBrains Mono, monospace" style="fill:#fff">{H.escape(t)}</text>'
    # ---- robots (processus)
    def robot(self, x, y, kind='sh', expr='neutral', label=None, scale=1.0):
        g = f'<g transform="translate({x},{y}) scale({scale})">'
        if kind == 'sh':
            g += f'<rect x="-22" y="-52" width="44" height="40" rx="6" fill="#fff" stroke="{INK}" stroke-width="2.5"/><line x1="0" y1="-52" x2="0" y2="-64" stroke="{INK}" stroke-width="2.5"/><circle cx="0" cy="-66" r="4" fill="{INK}"/>'
            g += f'<rect x="-16" y="-12" width="32" height="10" rx="3" fill="{INK}"/><line x1="-22" y1="-40" x2="-34" y2="-26" stroke="{INK}" stroke-width="3"/><line x1="22" y1="-40" x2="34" y2="-26" stroke="{INK}" stroke-width="3"/>'
            if expr == 'closed': g += f'<line x1="-14" y1="-38" x2="-6" y2="-38" stroke="{INK}" stroke-width="2.5"/><line x1="6" y1="-38" x2="14" y2="-38" stroke="{INK}" stroke-width="2.5"/><line x1="-8" y1="-24" x2="8" y2="-24" stroke="{INK}" stroke-width="2.5"/>'
            elif expr == 'broken': g += f'<path d="M-14,-42 L-6,-34 M-6,-42 L-14,-34 M6,-42 L14,-34 M14,-42 L6,-34" stroke="{INK}" stroke-width="2.5"/><path d="M-8,-22 q4,-6 8,0 q4,6 8,0" fill="none" stroke="{INK}" stroke-width="2"/>'
            else: g += f'<circle cx="-10" cy="-38" r="4" fill="{INK}"/><circle cx="10" cy="-38" r="4" fill="{INK}"/><line x1="-6" y1="-24" x2="6" y2="-24" stroke="{INK}" stroke-width="2.5"/>'
        else:  # java : tasse
            g += f'<path d="M-20,-52 L20,-52 L16,-12 L-16,-12 Z" fill="#fff" stroke="{INK}" stroke-width="2.5"/><path d="M20,-46 q16,0 14,14 q-2,12 -16,12" fill="none" stroke="{INK}" stroke-width="2.5"/>'
            g += f'<path d="M-8,-58 q4,-8 0,-14 M2,-58 q4,-8 0,-14" fill="none" stroke="{INK}" stroke-width="2" opacity=".8"/>'
            if expr == 'sleep': g += f'<path d="M-12,-36 q4,-4 8,0 M4,-36 q4,-4 8,0" fill="none" stroke="{INK}" stroke-width="2.5"/><text x="26" y="-60" font-size="12" font-weight="900" style="fill:{INK}">zzz</text>'
            elif expr == 'broken': g += f'<path d="M-12,-40 L-4,-32 M-4,-40 L-12,-32 M4,-40 L12,-32 M12,-40 L4,-32" stroke="{INK}" stroke-width="2.5"/><path d="M-6,-20 q6,-6 12,0" fill="none" stroke="{INK}" stroke-width="2"/><path d="M-24,-40 l-8,-14 M24,-44 l10,-12" stroke="{INK}" stroke-width="2"/>'
            else: g += f'<circle cx="-8" cy="-36" r="4" fill="{INK}"/><circle cx="8" cy="-36" r="4" fill="{INK}"/><path d="M-6,-24 q6,6 12,0" fill="none" stroke="{INK}" stroke-width="2.5"/>'
        g += '</g>'
        self.b += g
        if label: self.b += f'<text x="{x}" y="{y+14*scale}" text-anchor="middle" font-size="10" font-weight="700" style="fill:{INK}">{H.escape(label)}</text>'
    # ---- personnages
    def chara(self, x, y, who, expr='smile', pose='stand', scale=1.0, flip=False, upper=False):
        """x, y : position des pieds (ou du bassin si upper)."""
        s = scale; sx = -s if flip else s
        g = f'<g transform="translate({x},{y}) scale({sx},{s})">'
        OUT = {'kai': INK, 'mika': '#fff', 'sensei': '#fff'}[who]
        # jambes et pieds
        if not upper:
            g += f'<path d="M-15,-38 L-15,-6 L-4,-6 L-4,-38 Z M4,-38 L4,-6 L15,-6 L15,-38 Z" fill="{"#fff" if who!="kai" else INK}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            g += f'<path d="M-18,-6 L-3,-6 L-3,0 L-20,0 Z M3,-6 L18,-6 L20,0 L3,0 Z" fill="{INK}"/>'
        # torse
        if who == 'kai':      # sweat à capuche
            g += f'<path d="M-26,-84 Q-30,-84 -30,-76 L-27,-38 L27,-38 L30,-76 Q30,-84 26,-84 Z" fill="{INK}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            g += f'<path d="M-12,-84 Q0,-70 12,-84" fill="none" stroke="#fff" stroke-width="2"/><rect x="-14" y="-52" width="28" height="10" rx="3" fill="none" stroke="#fff" stroke-width="1.5"/><line x1="-4" y1="-70" x2="-4" y2="-58" stroke="#fff" stroke-width="1.5"/><line x1="4" y1="-70" x2="4" y2="-58" stroke="#fff" stroke-width="1.5"/>'
        elif who == 'mika':   # veste zippée, casque
            g += f'<path d="M-26,-84 Q-30,-84 -30,-76 L-27,-38 L27,-38 L30,-76 Q30,-84 26,-84 Z" fill="#fff" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            g += f'<line x1="0" y1="-84" x2="0" y2="-38" stroke="{INK}" stroke-width="2"/><rect x="-22" y="-62" width="12" height="9" rx="2" fill="url(#{self.id}_dots)" stroke="{INK}" stroke-width="1.5"/><path d="M-12,-84 L-6,-72 L0,-84 L6,-72 L12,-84" fill="none" stroke="{INK}" stroke-width="1.5"/>'
        else:                 # sensei : haori sur kimono
            g += f'<path d="M-28,-84 Q-32,-84 -32,-76 L-28,-38 L28,-38 L32,-76 Q32,-84 28,-84 Z" fill="url(#{self.id}_lines)" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            g += f'<path d="M-14,-84 L0,-60 L14,-84" fill="#fff" stroke="{INK}" stroke-width="2"/><path d="M0,-60 L-6,-38 M0,-60 L6,-38" fill="none" stroke="{INK}" stroke-width="1.5"/>'
        # bras (contour noir puis remplissage), mains
        def arm(x1, y1, x2, y2, x3, y3):
            return (f'<path d="M{x1},{y1} L{x2},{y2} L{x3},{y3}" fill="none" stroke="{INK}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>'
                    f'<path d="M{x1},{y1} L{x2},{y2} L{x3},{y3}" fill="none" stroke="{OUT}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
                    f'<circle cx="{x3}" cy="{y3}" r="6" fill="#fff" stroke="{INK}" stroke-width="2"/>')
        poses = {
            'stand': [(-27,-78,-34,-60,-34,-42), (27,-78,34,-60,34,-42)],
            'point': [(-27,-78,-34,-60,-34,-42), (27,-78,44,-72,62,-78)],
            'up':    [(-27,-78,-40,-96,-38,-114), (27,-78,40,-96,38,-114)],
            'head':  [(-27,-78,-46,-104,-34,-134), (27,-78,46,-104,34,-134)],
            'chin':  [(-27,-78,-34,-60,-34,-42), (27,-78,30,-66,10,-92)],
            'cross': [(-27,-78,-10,-62,14,-64), (27,-78,10,-62,-14,-64)],
            'type':  [(-27,-78,-34,-58,-14,-52), (27,-78,34,-58,14,-52)],
            'hips':  [(-27,-78,-40,-60,-26,-46), (27,-78,40,-60,26,-46)],
        }[pose]
        for a in poses: g += arm(*a)
        # cou et tête
        g += f'<rect x="-6" y="-92" width="12" height="10" fill="#fff" stroke="{INK}" stroke-width="2"/>'
        g += f'<path d="M-30,-118 Q-30,-96 -12,-88 Q0,-84 12,-88 Q30,-96 30,-118 Q30,-150 0,-150 Q-30,-150 -30,-118 Z" fill="#fff" stroke="{INK}" stroke-width="2.5"/>'
        g += f'<path d="M-30,-118 q-6,2 -2,10 M30,-118 q6,2 2,10" fill="none" stroke="{INK}" stroke-width="2"/>'   # oreilles
        # cheveux
        if who == 'kai':
            g += f'<path d="M-32,-124 L-36,-150 L-24,-140 L-20,-166 L-8,-146 L0,-172 L8,-146 L20,-166 L24,-140 L36,-150 L32,-124 Q30,-134 22,-134 L18,-124 L12,-136 L4,-124 L-2,-138 L-10,-126 L-18,-136 L-24,-124 Q-30,-136 -32,-124 Z" fill="{INK}"/>'
            g += f'<path d="M-10,-152 L-4,-140 M10,-156 L16,-142" stroke="#fff" stroke-width="2"/>'
        elif who == 'mika':
            g += f'<path d="M-32,-116 L-32,-136 Q-30,-158 0,-158 Q30,-158 32,-136 L32,-116 L26,-118 L24,-134 Q18,-128 6,-136 L2,-126 Q-8,-134 -20,-132 L-26,-118 Z" fill="{INK}"/>'
            g += f'<path d="M-32,-130 L-40,-96 L-30,-100 Z" fill="{INK}"/><path d="M32,-136 L42,-104 Q46,-96 38,-98 L30,-112 Z" fill="{INK}"/>'   # mèches, queue
            g += f'<path d="M-6,-152 L-2,-142 M14,-150 L18,-140" stroke="#fff" stroke-width="2"/>'
            g += f'<path d="M-32,-132 Q0,-166 32,-132" fill="none" stroke="{INK}" stroke-width="4"/><rect x="-38" y="-126" width="10" height="14" rx="3" fill="{INK}"/><rect x="28" y="-126" width="10" height="14" rx="3" fill="{INK}"/><path d="M-36,-112 q-6,10 4,14" fill="none" stroke="{INK}" stroke-width="2"/><circle cx="-31" cy="-98" r="2.5" fill="{INK}"/>'   # casque
        else:
            g += f'<path d="M-30,-130 Q-34,-146 -22,-150 L-24,-120 Z M30,-130 Q34,-146 22,-150 L24,-120 Z" fill="#fff" stroke="{INK}" stroke-width="2"/>'
            g += f'<path d="M-24,-100 Q-16,-64 0,-62 Q16,-64 24,-100 Q10,-92 0,-94 Q-10,-92 -24,-100 Z" fill="#fff" stroke="{INK}" stroke-width="2"/>'   # barbe
            g += f'<path d="M-16,-116 Q-8,-120 -2,-116 M2,-116 Q8,-120 16,-116" stroke="{INK}" stroke-width="3" fill="none"/>'   # sourcils épais
        # yeux
        ey = -118
        if who == 'sensei':
            g += f'<circle cx="-11" cy="{ey}" r="9" fill="#fff" stroke="{INK}" stroke-width="2"/><circle cx="11" cy="{ey}" r="9" fill="#fff" stroke="{INK}" stroke-width="2"/><line x1="-2" y1="{ey}" x2="2" y2="{ey}" stroke="{INK}" stroke-width="2"/><line x1="-20" y1="{ey-2}" x2="-30" y2="{ey-6}" stroke="{INK}" stroke-width="2"/>'
            g += f'<path d="M-15,{ey+1} q4,-4 8,0 M7,{ey+1} q4,-4 8,0" fill="none" stroke="{INK}" stroke-width="2.5"/>'
        elif expr == 'happy':
            g += f'<path d="M-19,{ey} q8,-12 16,0 M3,{ey} q8,-12 16,0" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
        else:
            big = expr in ('shock','panic','cry','scared'); ry = 12 if big else 10; rx = 8 if big else 7
            for cx in (-12, 12):
                g += f'<ellipse cx="{cx}" cy="{ey}" rx="{rx}" ry="{ry}" fill="#fff" stroke="{INK}" stroke-width="2"/>'
                if big:
                    g += f'<circle cx="{cx}" cy="{ey+1}" r="3" fill="{INK}"/>'
                else:
                    g += f'<ellipse cx="{cx}" cy="{ey+1}" rx="5.5" ry="8" fill="url(#{self.id}_iris)" stroke="{INK}" stroke-width="1.5"/><ellipse cx="{cx}" cy="{ey+2}" rx="3" ry="5" fill="{INK}"/><circle cx="{cx-2.5}" cy="{ey-3}" r="2.2" fill="#fff"/><circle cx="{cx+2}" cy="{ey+4}" r="1.2" fill="#fff"/>'
                g += f'<path d="M{cx-rx},{ey-ry+4} q{rx},-{ry+2} {2*rx},0" fill="none" stroke="{INK}" stroke-width="3"/>'   # paupière
            if who == 'mika': g += f'<path d="M-20,{ey-8} l-4,-3 M20,{ey-8} l4,-3" stroke="{INK}" stroke-width="2"/>'
            brow = {'angry': f'<path d="M-22,{ey-20} L-6,{ey-14} M22,{ey-20} L6,{ey-14}" stroke="{INK}" stroke-width="3"/>',
                    'panic': f'<path d="M-20,{ey-14} L-6,{ey-20} M20,{ey-14} L6,{ey-20}" stroke="{INK}" stroke-width="3"/>',
                    'cry':   f'<path d="M-20,{ey-14} L-6,{ey-20} M20,{ey-14} L6,{ey-20}" stroke="{INK}" stroke-width="3"/>',
                    'shock': f'<path d="M-20,{ey-24} q8,-4 16,0 M4,{ey-24} q8,-4 16,0" fill="none" stroke="{INK}" stroke-width="3"/>'}.get(expr, f'<path d="M-20,{ey-20} q8,-3 16,0 M4,{ey-20} q8,-3 16,0" fill="none" stroke="{INK}" stroke-width="3"/>')
            g += brow
        g += f'<path d="M-1,-104 l3,3" stroke="{INK}" stroke-width="1.5"/>'   # nez
        # bouche
        mouth = {'smile': f'<path d="M-9,-96 Q0,-88 9,-96" fill="none" stroke="{INK}" stroke-width="2.5"/>',
                 'happy': f'<path d="M-11,-98 Q0,-84 11,-98 Z" fill="{INK}"/>',
                 'shock': f'<ellipse cx="0" cy="-94" rx="6" ry="8" fill="{INK}"/>',
                 'panic': f'<path d="M-10,-94 q5,6 10,0 q5,-6 10,0 q-5,8 -10,6 q-5,2 -10,-6 Z" fill="{INK}"/>',
                 'angry': f'<path d="M-9,-92 Q0,-100 9,-92" fill="none" stroke="{INK}" stroke-width="2.5"/>',
                 'cry':   f'<path d="M-8,-92 Q0,-98 8,-92" fill="none" stroke="{INK}" stroke-width="2.5"/>',
                 'neutral': f'<line x1="-7" y1="-94" x2="7" y2="-94" stroke="{INK}" stroke-width="2.5"/>',
                 'scared': f'<path d="M-8,-96 q4,4 8,0 q4,-4 8,0" fill="none" stroke="{INK}" stroke-width="2.5"/>'}
        g += mouth.get(expr, mouth['smile'])
        # extras
        if expr in ('panic','scared','shock'): g += f'<path d="M28,-142 q5,10 0,14 q-5,-4 0,-14 Z" fill="#fff" stroke="{INK}" stroke-width="1.5"/><path d="M34,-130 q4,8 0,11 q-4,-3 0,-11 Z" fill="#fff" stroke="{INK}" stroke-width="1.5"/>'
        if expr == 'cry': g += f'<path d="M-20,-110 q-4,20 -2,40 M20,-110 q4,20 2,40" fill="none" stroke="{INK}" stroke-width="2" opacity=".7"/>'
        if expr == 'angry': g += f'<path d="M20,-150 l4,-4 M24,-150 l-4,-4 M22,-156 l0,10 M17,-153 l10,0" stroke="{INK}" stroke-width="1.5"/>'
        if expr in ('happy','smile') and who != 'sensei': g += f'<path d="M-22,-104 l4,2 M-24,-101 l4,2 M18,-104 l4,2 M20,-101 l4,2" stroke="{INK}" stroke-width="1.2"/>'   # rougeurs
        g += '</g>'
        self.b += g
    # ---- lettrage
    def bubble(self, x, y, w, lines, tail=None, fs=11, shout=False, think=False):
        h = 12 + len(lines)*(fs+4)
        if shout:
            cx, cy = x+w/2, y+h/2; m = 22; pts = []
            for k in range(m):
                a = 2*math.pi*k/m; rx = w/2 + (12 if k%2==0 else -2); ry = h/2 + (12 if k%2==0 else -1)
                pts.append(f'{cx+rx*math.cos(a):.1f},{cy+ry*math.sin(a):.1f}')
            self.b += f'<polygon points="{" ".join(pts)}" fill="#fff" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
        else:
            self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{min(16, h/2)}" fill="#fff" stroke="{INK}" stroke-width="2.5"/>'
            if tail and not think:
                tx, ty = tail; bx = min(max(tx, x+18), x+w-18); d = 8 if tx >= bx else -8
                self.b += f'<path d="M{bx-8},{y+h-1} L{tx},{ty} L{bx+8},{y+h-1}" fill="#fff" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/><line x1="{bx-8}" y1="{y+h-1}" x2="{bx+8}" y2="{y+h-1}" stroke="#fff" stroke-width="4"/>'
            if tail and think:
                tx, ty = tail
                for k, r in enumerate((5, 3.5, 2)): self.b += f'<circle cx="{x+w/2+(tx-x-w/2)*(k+1)/4}" cy="{y+h+(ty-y-h)*(k+1)/4}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="2"/>'
        for k, t in enumerate(lines):
            self.b += f'<text x="{x+w/2}" y="{y+9+fs+k*(fs+4)}" text-anchor="middle" font-size="{fs}" font-weight="700" style="fill:{INK}">{H.escape(t)}</text>'
    def caption(self, x, y, w, text, fs=10):
        self.b += f'<rect x="{x}" y="{y}" width="{w}" height="{fs+12}" fill="#fff" stroke="{INK}" stroke-width="2.5"/><text x="{x+w/2}" y="{y+fs+4}" text-anchor="middle" font-size="{fs}" font-style="italic" font-weight="700" style="fill:{INK}">{H.escape(text)}</text>'
    def sfx(self, x, y, text, fs=28, rot=-10, outline=True):
        self.b += f'<text x="{x}" y="{y}" transform="rotate({rot} {x} {y})" text-anchor="middle" font-size="{fs}" font-weight="900" font-style="italic" style="fill:{INK}" stroke="#fff" stroke-width="7" paint-order="stroke" letter-spacing="1.5">{H.escape(text)}</text>'
    def label(self, x, y, text, fs=10, bold=True): self.b += f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{fs}" font-weight="{700 if bold else 400}" style="fill:{INK}">{H.escape(text)}</text>'
    def render(self, caption):
        defs = (f'<pattern id="{self.id}_dots" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.3" fill="{INK}" opacity=".5"/></pattern>'
                f'<pattern id="{self.id}_lines" width="6" height="6" patternUnits="userSpaceOnUse"><line x1="0" y1="6" x2="6" y2="0" stroke="{INK}" stroke-width="1" opacity=".55"/></pattern>'
                f'<pattern id="{self.id}_dark" width="5" height="5" patternUnits="userSpaceOnUse"><rect width="5" height="5" fill="{INK}"/><circle cx="2.5" cy="2.5" r="1.1" fill="#fff" opacity=".28"/></pattern>'
                f'<pattern id="{self.id}_iris" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="3" fill="#fff"/><circle cx="1.5" cy="1.5" r="1" fill="{INK}" opacity=".55"/></pattern>'
                f'<pattern id="{self.id}_brick" width="28" height="16" patternUnits="userSpaceOnUse"><rect width="28" height="16" fill="#fff"/><rect x="1" y="1" width="26" height="6" fill="url(#{self.id}_dots)" stroke="{INK}" stroke-width="1"/><rect x="-13" y="9" width="26" height="6" fill="url(#{self.id}_dots)" stroke="{INK}" stroke-width="1"/><rect x="15" y="9" width="26" height="6" fill="url(#{self.id}_dots)" stroke="{INK}" stroke-width="1"/></pattern>')
        head = (f'<rect x="{self.gap}" y="{self.gap-2}" width="{self.w-2*self.gap}" height="{self.top-self.gap-4}" fill="#fff"/>'
                f'<text x="{self.gap+8}" y="{self.top-9}" font-size="12" font-weight="900" style="fill:{INK}" letter-spacing="1">{H.escape(self.chapter)}</text>'
                f'<text x="{self.w-self.gap-8}" y="{self.top-9}" text-anchor="end" font-size="12" font-weight="700" font-style="italic" style="fill:{INK}">{H.escape(self.title)}</text>')
        return (f'<figure class="fig manga"><svg viewBox="0 0 {self.w} {self.h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{H.escape(self.chapter + " : " + self.title)}">'
                f'<defs>{defs}</defs><rect width="{self.w}" height="{self.h}" fill="{INK}"/>{head}{self.b}</svg><figcaption>{caption}</figcaption></figure>')

STRIPS = []

# ================================================================ Présentation des personnages
s = Strip("mg0", "les personnages", "Fondations, en manga", panels=(260, 260, 260), ph=250)
for i, (who, name, role, lines) in enumerate([
    ('kai', "Kaï", "développeur", ["Java, React, du code qui", "marche sur son poste.", "Apprend que « ça marche", "chez moi » ne suffit pas."]),
    ('mika', "Mika", "opérations", ["Tient la production,", "l'astreinte et les serveurs.", "Rêve d'une nuit", "sans alerte."]),
    ('sensei', "Sensei Ohno", "le maître", ["Trente ans de systèmes.", "Une phrase, une commande,", "et le problème change", "de nature."])]):
    x, y, w = s.begin(i); s.tone(x, y, w, 70, 'dots')
    s.chara(x+62, y+236, who, 'smile' if who!='kai' else 'happy', 'point' if who=='sensei' else ('hips' if who=='mika' else 'stand'), scale=.95)
    s.label(x+182, y+96, name, 16); s.label(x+182, y+114, role, 11, False)
    for k, t in enumerate(lines): s.label(x+182, y+140+k*14, t, 8.5, False)
    s.end(i)
CAST = s.render("Trois personnages originaux traversent le niveau 0 : chaque chapitre s'ouvre sur une planche où l'un d'eux tombe dans le piège que le chapitre apprend à éviter.")

# ================================================================ 1. Le mur
s = Strip("mg1", "le mur entre Dev et Ops", "Chapitre 1")
x, y, w = s.begin(0); s.tone(x, y, w, 90, 'dots'); s.floor(x, y+236, w)
s.wall(x+126, y+50, 16, 186)
s.desk(x+4, y+190, 110, laptop=True, screen_lines=["build OK", "tests OK", "v2.zip"])
s.chara(x+60, y+236, 'kai', 'happy', 'up', scale=.9)
s.raw(f'<rect x="{x+112}" y="{y+70}" width="34" height="22" rx="3" fill="#fff" stroke="{INK}" stroke-width="2"/><text x="{x+129}" y="{y+85}" text-anchor="middle" font-size="9" font-weight="700" style="fill:{INK}">v2.zip</text>')
s.speed(x+76, y+70, 40, 30, 6)
s.rack(x+214, y+96, 42, 140); s.chara(x+176, y+236, 'mika', 'neutral', 'stand', scale=.9, flip=True)
s.bubble(x+6, y+6, 112, ["C'est fini !", "À vous de le faire", "tourner !"], tail=(x+56, y+112), fs=10)
s.sfx(x+204, y+64, "HOP !", 20, -18); s.caption(x+w-118, y+246, 112, "vendredi, 17 h 55")
s.end(0)
x, y, w = s.begin(1); s.night(x, y, w, s.ph); s.floor(x, y+236, w)
s.rack(x+30, y+96, 54, 140, alarm=True); s.rack(x+92, y+96, 54, 140, alarm=True)
s.chara(x+190, y+236, 'mika', 'panic', 'head', scale=.9); s.phone(x+150, y+150)
s.focus(x+190, y+150, 60, 120, 30, 1.2)
s.bubble(x+40, y+10, 180, ["Ça ne démarre pas !", "Quelle version de Java ?!", "Pourquoi le port 8080 ?!"], fs=10.5, shout=True)
s.sfx(x+124, y+120, "BIP BIP", 15, 8); s.caption(x+6, y+246, 160, "samedi, 3 h 12, production")
s.end(1)
x, y, w = s.begin(2); s.floor(x, y+236, w)
s.desk(x+50, y+190, 160, laptop=False, monitor=True, screen_lines=["pipeline   OK", "logs       OK", "astreinte  Kaï + Mika"])
s.chara(x+44, y+236, 'kai', 'happy', 'stand', scale=.88); s.chara(x+216, y+236, 'mika', 'happy', 'stand', scale=.88, flip=True)
s.bubble(x+6, y+6, 248, ["« You build it, you run it. »", "Le même code, la même équipe,", "la même responsabilité."], fs=10.5)
s.sfx(x+130, y+98, "DevOps", 26, 0)
s.end(2)
STRIPS.append(("1.1", s.render("Le développeur lance le code par-dessus le mur, l'ops le reçoit la nuit. DevOps, c'est retirer le mur, pas ajouter un outil.")))

# ================================================================ 2. PID 1
s = Strip("mg2", "PID 1 et le signal ignoré", "Chapitre 2")
x, y, w = s.begin(0)
s.raw(f'<rect x="{x+16}" y="{y+40}" width="{w-32}" height="170" rx="12" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="9 6"/>')
s.label(x+w/2, y+32, "conteneur", 11)
s.robot(x+80, y+190, 'sh', 'neutral', "sh, PID 1"); s.robot(x+180, y+190, 'java', 'smile', "java, PID 7")
s.raw(f'<rect x="{x+28}" y="{y+56}" width="46" height="30" rx="3" fill="#fff" stroke="{INK}" stroke-width="2"/><path d="M{x+28},{y+56} L{x+51},{y+74} L{x+74},{y+56}" fill="none" stroke="{INK}" stroke-width="2"/><text x="{x+51}" y="{y+100}" text-anchor="middle" font-size="9" font-weight="700" style="fill:{INK}">SIGTERM</text>')
s.speed(x+80, y+62, 30, 20, 5)
s.caption(x+16, y+224, w-32, "ENTRYPOINT java -jar app.jar   (forme shell)", 9)
s.bubble(x+120, y+50, 120, ["docker stop", "→ « arrête-toi", "proprement »"], fs=9.5)
s.end(0)
x, y, w = s.begin(1); s.tone(x, y, w, s.ph, 'lines')
s.raw(f'<rect x="{x+16}" y="{y+40}" width="{w-32}" height="170" rx="12" fill="#fff" stroke="{INK}" stroke-width="3" stroke-dasharray="9 6"/>')
s.robot(x+80, y+190, 'sh', 'closed', "sh : reçu…"); s.robot(x+180, y+190, 'java', 'sleep', "java : rien")
s.raw(f'<rect x="{x+58}" y="{y+120}" width="44" height="26" rx="3" fill="#fff" stroke="{INK}" stroke-width="2"/><path d="M{x+58},{y+120} L{x+80},{y+136} L{x+102},{y+120}" fill="none" stroke="{INK}" stroke-width="2"/>')
s.bubble(x+20, y+50, 130, ["…et je ne le", "transmets à personne."], tail=(x+80, y+118), fs=10)
s.caption(x+16, y+224, w-32, "1 s, 5 s, 9 s… Docker attend", 9)
s.end(1)
x, y, w = s.begin(2); s.focus(x+130, y+130, 50, 180, 44, 1.5)
s.robot(x+80, y+172, 'sh', 'broken', "sh"); s.robot(x+180, y+172, 'java', 'broken', "java")
s.raw(f'<path d="M{x+130},{y+52} L{x+130},{y+100}" stroke="{INK}" stroke-width="6"/><rect x="{x+104}" y="{y+40}" width="52" height="22" rx="4" fill="{INK}"/><text x="{x+130}" y="{y+56}" text-anchor="middle" font-size="9" font-weight="900" style="fill:#fff">docker</text>')
s.sfx(x+130, y+98, "SIGKILL !", 28, -8)
s.bubble(x+12, y+204, w-24, ["Tué à 10 s, code 137 : requêtes coupées.", "Forme exec : ENTRYPOINT [\"java\",\"-jar\",\"app.jar\"]"], fs=8)
s.end(2)
STRIPS.append(("2.3", s.render("En forme shell, sh est PID 1 et n'a aucun gestionnaire de signal : java n'est jamais prévenu. En forme exec, java est PID 1 et s'arrête proprement.")))

# ================================================================ 3. DNS
s = Strip("mg3", "diagnostiquer de gauche à droite", "Chapitre 3")
x, y, w = s.begin(0); s.floor(x, y+236, w)
s.desk(x+10, y+190, 140, laptop=False, monitor=True, screen_lines=["$ curl https://api…", "curl: (6)", "Could not", "resolve host"])
s.chara(x+200, y+236, 'kai', 'panic', 'head', scale=.9, flip=True)
s.bubble(x+96, y+8, 158, ["C'est le réseau !", "Non, le pare-feu !", "Non, le certificat !"], fs=10, shout=True)
s.caption(x+6, y+246, 130, "depuis trois heures…")
s.end(0)
x, y, w = s.begin(1); s.floor(x, y+236, w)
s.board(x+94, y+60, 104, 96, ["DNS  resolve", "TCP  refused", "TLS  certif.", "HTTP 4xx/5xx"], "lis le message")
s.chara(x+50, y+236, 'sensei', 'smile', 'point', scale=.85); s.chara(x+226, y+236, 'kai', 'neutral', 'stand', scale=.85, flip=True)
s.bubble(x+6, y+6, 150, ["« resolve », c'est le DNS.", "On va droit à la couche."], tail=(x+56, y+112), fs=10)
s.caption(x+6, y+246, w-12, "$ dig +short api.crisisshield.example", 9)
s.end(1)
x, y, w = s.begin(2); s.focus(x+130, y+120, 70, 170, 36, 1.2); s.floor(x, y+236, w)
s.chara(x+130, y+236, 'kai', 'happy', 'up', scale=.95)
s.sfx(x+130, y+52, "TROUVÉ !", 28, -6)
s.bubble(x+14, y+204, w-28, ["Pas d'enregistrement DNS en staging.", "Cinq minutes, pas trois heures."], fs=9.5)
s.end(2)
STRIPS.append(("3.1", s.render("Chaque étape a son message d'erreur ; on lit le message et on va droit à la couche fautive au lieu de tout soupçonner à la fois.")))

# ================================================================ 4. set -e
s = Strip("mg4", "le script qui continue après l'erreur", "Chapitre 4")
x, y, w = s.begin(0); s.floor(x, y+236, w)
s.terminal(x+14, y+10, 232, 84, ["#!/bin/bash", "cd /var/backups/$APP", "rm -rf ./*", "cp -r /data/$APP ."], 8.5)
s.chara(x+70, y+236, 'kai', 'happy', 'chin', scale=.85)
s.bubble(x+118, y+124, 128, ["Sauvegarde", "automatique.", "Trop simple."], tail=(x+96, y+186), fs=10)
s.end(0)
x, y, w = s.begin(1); s.night(x, y, w, s.ph)
s.terminal(x+14, y+80, 232, 100, ["02:00 cron", "$APP = \"\"  (vide ce soir)", "cd: /var/backups/: échec", "→ le script continue…", "rm -rf ./*"], 9)
s.raw(f'<text x="{x+40}" y="{y+56}" font-size="14" font-weight="900" style="fill:#fff">zzz</text>')
s.caption(x+14, y+200, 232, "cd a échoué : on n'a pas bougé…", 9)
s.caption(x+14, y+228, 232, "…et le répertoire courant est /var/backups", 9)
s.end(1)
x, y, w = s.begin(2); s.focus(x+130, y+150, 46, 160, 40, 1.4); s.floor(x, y+236, w)
s.bubble(x+10, y+8, w-20, ["Toutes les sauvegardes. Toutes.", "set -euo pipefail : arrêt au premier échec.", "En tête de chaque script."], fs=9)
s.chara(x+76, y+236, 'kai', 'cry', 'head', scale=.85); s.chara(x+206, y+236, 'sensei', 'neutral', 'point', scale=.8, flip=True)
s.sfx(x+130, y+84, "rm -rf ./*", 22, -8)
s.end(2)
STRIPS.append(("4.1", s.render("Sans set -e, un cd qui échoue est ignoré et le rm s'exécute ailleurs. Trois options en tête de script évitent la catégorie entière d'accidents.")))

# ================================================================ 5. reflog
s = Strip("mg5", "le reflog te sauve", "Chapitre 5")
x, y, w = s.begin(0); s.tone(x, y, w, s.ph, 'dots'); s.floor(x, y+236, w)
s.terminal(x+14, y+180, 232, 56, ["$ git reset --hard HEAD~3", "HEAD is now at e3f9a1 init"], 9)
s.chara(x+130, y+178, 'kai', 'shock', 'head', scale=.8); s.focus(x+130, y+118, 50, 100, 22, 1)
s.bubble(x+46, y+8, 168, ["Trois commits… envolés ?!", "Une journée de travail !"], fs=10, shout=True)
s.caption(x+6, y+246, 140, "rien n'est poussé")
s.end(0)
x, y, w = s.begin(1); s.floor(x, y+236, w)
s.board(x+94, y+60, 104, 96, ["@{0} reset", "@{1} cache", "@{2} api", "rien perdu"], "git reflog")
s.chara(x+50, y+236, 'sensei', 'smile', 'point', scale=.85); s.chara(x+226, y+236, 'kai', 'cry', 'stand', scale=.85, flip=True)
s.bubble(x+6, y+6, 150, ["Git garde 90 jours tout", "ce que HEAD a pointé."], tail=(x+56, y+112), fs=10)
s.caption(x+6, y+246, w-12, "$ git reset --hard HEAD@{1}", 9)
s.end(1)
x, y, w = s.begin(2); s.focus(x+130, y+130, 60, 170, 34, 1.2); s.floor(x, y+236, w)
s.terminal(x+14, y+12, 232, 44, ["HEAD is now at 7b2c44 feat: cache", "$ git log --oneline | wc -l  → 4"], 9)
s.chara(x+130, y+236, 'kai', 'happy', 'up', scale=.9)
s.sfx(x+130, y+96, "SAUVÉ !", 26, -6)
s.bubble(x+14, y+206, w-28, ["reset --hard déplace la branche,", "il n'efface rien. Le reflog est le filet."], fs=9.5)
s.end(2)
STRIPS.append(("5.3", s.render("Un reset --hard n'efface pas les commits : il déplace la branche. Le reflog garde chaque position de HEAD ; on y revient en une commande.")))

# ================================================================ 6. Seq Scan
s = Strip("mg6", "le Seq Scan qui grossit", "Chapitre 6")
x, y, w = s.begin(0); s.floor(x, y+236, w)
s.raw(f'<rect x="{x+20}" y="{y+150}" width="90" height="70" rx="5" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
for k in range(4): s.raw(f'<line x1="{x+30}" y1="{y+164+k*15}" x2="{x+100}" y2="{y+164+k*15}" stroke="{INK}" stroke-width="2"/>')
s.label(x+65, y+232, "1 000 lignes", 10)
s.chara(x+196, y+236, 'kai', 'happy', 'chin', scale=.9, flip=True)
s.bubble(x+110, y+8, 144, ["SELECT * WHERE zone = ?", "12 ms. Parfait.", "Pas besoin d'index."], tail=(x+190, y+126), fs=9.5)
s.caption(x+6, y+246, 120, "en développement")
s.end(0)
x, y, w = s.begin(1); s.tone(x, y, w, s.ph, 'lines'); s.floor(x, y+236, w)
s.raw(f'<rect x="{x+14}" y="{y+56}" width="120" height="176" rx="5" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
for k in range(11): s.raw(f'<line x1="{x+24}" y1="{y+70+k*15}" x2="{x+124}" y2="{y+70+k*15}" stroke="{INK}" stroke-width="2"/>')
s.label(x+74, y+246, "1 000 000 de lignes", 9.5)
s.chara(x+200, y+236, 'mika', 'panic', 'head', scale=.9, flip=True); s.phone(x+150, y+180)
s.bubble(x+114, y+14, 108, ["12 secondes !", "La prod rame,", "l'astreinte sonne."], fs=9.5, shout=True)
s.caption(x+6, y+8, 110, "six mois plus tard")
s.end(1)
x, y, w = s.begin(2); s.floor(x, y+236, w)
s.board(x+94, y+60, 104, 96, ["Seq Scan", "rows=1e6", "→ index", "log(n)"], "EXPLAIN")
s.chara(x+50, y+236, 'sensei', 'smile', 'point', scale=.85); s.chara(x+226, y+236, 'kai', 'neutral', 'stand', scale=.85, flip=True)
s.bubble(x+6, y+6, 150, ["Le temps suit la table.", "Avec l'index, il suit le log."], tail=(x+56, y+112), fs=10)
s.sfx(x+226, y+92, "12 ms", 18, 8)
s.caption(x+6, y+246, w-12, "CREATE INDEX CONCURRENTLY ON incidents (zone);", 8.5)
s.end(2)
STRIPS.append(("6.1", s.render("Rapide sur mille lignes, catastrophique sur un million : EXPLAIN ANALYZE montre le Seq Scan, l'index le remplace par une recherche en log(n).")))

# ================================================================ insertion
CSS = """
/* ============ Planches manga ============ */
.fig.manga svg{min-width:640px;border-radius:6px}
.fig.manga svg text{font-family:"Atkinson Hyperlegible",system-ui,sans-serif}
.fig.manga figcaption::before{content:"Manga — ";font-weight:700;color:var(--ink)}
:root[data-theme="dark"] .fig.manga svg{opacity:.94}
</style>"""
S = S.replace('</style>', CSS, 1)
# page des personnages : après le résumé du chapitre 1
m = re.search(r'<span class="chapnum">Chapitre 1</span>.*?</div>\n', S, flags=re.S); assert m
b = S.index('<div class="bref">', m.end()); e = S.index('</div>', b) + 6
S = S[:e] + '\n' + CAST + S[e:]
for sec, svg in STRIPS:
    m = re.search(r'<h3>' + re.escape(sec) + r' [^<]*(?:<span class="badge[^<]*</span>)?</h3>', S); assert m, sec
    S = S[:m.end()] + '\n' + svg + S[m.end():]
p.write_text(S); print('planches :', S.count('class="fig manga"'))
