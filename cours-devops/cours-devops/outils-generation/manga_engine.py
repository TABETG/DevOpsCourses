"""Moteur de planches manga (personnages Kaï, Mika, Sensei Ohno ; robots, racks, bulles). Extrait de manga2.py."""
import re, pathlib, html as H, math


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

