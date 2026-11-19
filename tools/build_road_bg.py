# Рисует фоновые эскизы для страницы «Асфальт» в стиле чертежей сайта (assets/bg2).
import math, os
L = '#BACDC9'   # основная линия
T = '#96A6A3'   # тонкая/размерная
FONT = "font-family:'Helvetica Neue',Arial,sans-serif;fill:%s" % T

class S:
    def __init__(s, w, h): s.w, s.h, s.o = w, h, []
    def ln(s, x1, y1, x2, y2, w=2.2, c=L, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        s.o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}"{d} stroke-linecap="round"/>')
    def pl(s, pts, w=2.2, c=L, close=False, dash=None):
        p = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        tag = 'polygon' if close else 'polyline'
        d = f' stroke-dasharray="{dash}"' if dash else ''
        s.o.append(f'<{tag} points="{p}" fill="none" stroke="{c}" stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>')
    def rect(s, x, y, w_, h_, w=2.2, c=L, r=0):
        s.o.append(f'<rect x="{x}" y="{y}" width="{w_}" height="{h_}" rx="{r}" fill="none" stroke="{c}" stroke-width="{w}"/>')
    def circ(s, x, y, r, w=2.2, c=L, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        s.o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{c}" stroke-width="{w}"{d}/>')
    def path(s, d, w=2.2, c=L):
        s.o.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>')
    def txt(s, x, y, t, size=15, anchor='start', rot=0):
        tr = f' transform="rotate({rot} {x} {y})"' if rot else ''
        s.o.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" style="{FONT}"{tr}>{t}</text>')
    def arrow(s, x, y, ang):  # засечка размера (наклонная, как в СПДС)
        a = math.radians(ang + 45)
        s.ln(x - 7*math.cos(a), y - 7*math.sin(a), x + 7*math.cos(a), y + 7*math.sin(a), 1.6, T)
    def dimh(s, x1, x2, y, label, ext_from=None):
        s.ln(x1 - 12, y, x2 + 12, y, 1.2, T)
        s.arrow(x1, y, 0); s.arrow(x2, y, 0)
        if ext_from is not None:
            s.ln(x1, ext_from, x1, y + 8, 1.0, T); s.ln(x2, ext_from, x2, y + 8, 1.0, T)
        s.txt((x1 + x2) / 2, y - 7, label, 15, 'middle')
    def dimv(s, x, y1, y2, label, ext_from=None):
        s.ln(x, y1 - 12, x, y2 + 12, 1.2, T)
        s.arrow(x, y1, 90); s.arrow(x, y2, 90)
        if ext_from is not None:
            s.ln(ext_from, y1, x + 8, y1, 1.0, T); s.ln(ext_from, y2, x + 8, y2, 1.0, T)
        s.txt(x - 8, (y1 + y2) / 2, label, 15, 'middle', -90)
    def axis(s, x1, y1, x2, y2):
        s.ln(x1, y1, x2, y2, 1.1, T, '28 6 4 6')
    def leader(s, x, y, x2, y2, label, right=True):
        s.ln(x, y, x2, y2, 1.1, T); s.circ(x, y, 2.5, 1.2, T)
        tw = len(label) * 7.6
        s.ln(x2, y2, x2 + (tw if right else -tw), y2, 1.1, T)
        s.txt(x2 + (4 if right else -tw), y2 - 6, label, 14)
    def svg(s):
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{s.w}" height="{s.h}" viewBox="0 0 {s.w} {s.h}">' + ''.join(s.o) + '</svg>'

def wheel(s, x, y, r, rim=0.62):
    s.circ(x, y, r); s.circ(x, y, r*rim, 1.6); s.circ(x, y, r*0.16, 1.4)
    for k in range(6):
        a = k*math.pi/3
        s.ln(x + r*0.2*math.cos(a), y + r*0.2*math.sin(a), x + r*0.55*math.cos(a), y + r*0.55*math.sin(a), 1.0, T)
    s.ln(x - r - 10, y, x + r + 10, y, 1.0, T, '14 4 3 4'); s.ln(x, y - r - 10, x, y + r + 10, 1.0, T, '14 4 3 4')

# 1. Дорога в перспективе с разметкой
def road():
    s = S(1200, 780); H = 170; cx = 600; K = 560
    def Y(d): return H + K / d
    def X(off, d): return cx + off * K / d
    s.axis(20, H, 1180, H); s.txt(30, H - 10, 'линия горизонта', 13)
    for off, w in [(-1.25, 2.4), (1.25, 2.4), (-1.55, 1.4), (1.55, 1.4)]:
        s.ln(X(off, 0.78), Y(0.78), X(off, 60), Y(60), w, L if w > 2 else T)
    for off in (-1.12, 1.12):
        s.ln(X(off, 0.78), Y(0.78), X(off, 60), Y(60), 1.6)
    d = 1.05
    while d < 45:
        d2 = d + 0.32*d**0.55
        s.pl([(X(-0.012, d), Y(d)), (X(0.012, d), Y(d)), (X(0.012, d2), Y(d2)), (X(-0.012, d2), Y(d2))], 1.4, L, True)
        d = d2 + 0.75*d**0.6
    for dd in (1.3, 2.2, 4, 8):
        s.ln(X(-1.55, dd), Y(dd), X(1.55, dd), Y(dd), 1.0, T, '6 6')
        s.txt(X(1.6, dd) + 10, Y(dd) + 4, 'ПК %d+00' % {1.3: 12, 2.2: 13, 4: 14, 8: 15}[dd], 13)
    for off in (-2.3, 2.3):  # опоры освещения
        for dd in (1.6, 3.2, 6.4, 12.8):
            x, y = X(off, dd), Y(dd); h = 300 / dd
            s.ln(x, y, x, y - h, 2.0 if dd < 3 else 1.4)
            dx = -0.22*h if off > 0 else 0.22*h
            s.path(f'M{x:.1f},{y-h:.1f} q0,{-0.08*h:.1f} {dx:.1f},{-0.08*h:.1f}', 1.4)
            s.ln(x + dx - 0.06*h*(1 if dx > 0 else -1), y - h - 0.08*h, x + dx + 0.04*h*(1 if dx > 0 else -1), y - h - 0.08*h, 2.0)
    s.dimh(X(-1.12, 0.8), X(1.12, 0.8), 740, '7 000')
    return s

# 2. Поперечный профиль: конструкция дорожной одежды
def section():
    s = S(1200, 520)
    top = 150; cx = 600; half = 380
    layers = [(0, 'Асфальтобетон ЩМА-20, h = 50'), (16, 'Асфальтобетон пористый, h = 80'),
              (42, 'Щебень фр. 40–80, h = 300'), (120, 'Песок средний, h = 400'), (220, 'Грунт земляного полотна')]
    def edge(depth, side):
        return cx + side*(half + depth*1.6)
    for i, (dep, _) in enumerate(layers):
        y = top + dep + (0 if dep == 0 else 0)
        yc = y - 8 if dep < 120 else y
        s.pl([(edge(dep, -1), y), (cx, yc), (edge(dep, 1), y)], 2.2 if dep < 200 else 1.6)
    s.pl([(edge(0, -1), top), (edge(220, -1) - 120, top + 260)], 1.6)
    s.pl([(edge(0, 1), top), (edge(220, 1) + 120, top + 260)], 1.6)
    for x in range(int(edge(42, -1)) + 10, int(edge(42, 1)) - 10, 22):  # штриховка щебня
        s.circ(x + (7 if (x//22) % 2 else 0), top + 80, 3.2, 1.0, T)
    for x in range(int(edge(120, -1)) + 30, int(edge(120, 1)) - 30, 16):
        s.circ(x, top + 172 + (x % 3)*6, 1.2, 0.9, T)
    s.axis(cx, 40, cx, 470); s.txt(cx + 8, 52, 'ось дороги', 13)
    s.dimh(cx - half, cx, 100, '3 500', top - 10); s.dimh(cx, cx + half, 100, '3 500')
    s.txt(cx - 200, top - 18, 'i = 20‰', 14, 'middle'); s.txt(cx + 200, top - 18, 'i = 20‰', 14, 'middle')
    s.txt(edge(60, 1) + 120, top + 130, '1:4', 14)
    for k, (dep, lab) in enumerate(layers):
        yy = top + dep + (6 if dep < 120 else 30)
        px = 880 - k*45; ly = 300 + k*36
        s.circ(px, yy, 2.5, 1.2, T); s.ln(px, yy, px, ly, 1.1, T); s.ln(px, ly, 960 + len(lab)*7.6, ly, 1.1, T)
        s.txt(964, ly - 6, lab, 14)
    return s

# 3. Каток тандемный, вид сбоку
def roller():
    s = S(1200, 700); y0 = 600; r = 105
    xf, xr = 300, 870
    for x in (xf, xr):
        s.circ(x, y0 - r, r); s.circ(x, y0 - r, r - 12, 1.4)
        s.ln(x - r - 12, y0 - r, x + r + 12, y0 - r, 1.0, T, '14 4 3 4'); s.ln(x, y0 - 2*r - 12, x, y0 + 12, 1.0, T, '14 4 3 4')
        s.path(f'M{x - r - 18},{y0 - r} L{x - r - 18},{y0 - 2*r - 24} L{x + r + 18},{y0 - 2*r - 24} L{x + r + 18},{y0 - r}', 2.0)
        s.ln(x - r - 6, y0 - 30, x - r - 18, y0 - 60, 1.4)
    s.ln(40, y0, 1160, y0, 1.2, T)
    top = y0 - 2*r - 24
    s.pl([(xf + r + 18, top + 30), (xr - r - 18, top + 30), (xr - r - 18, top + 110), (xf + r + 18, top + 110)], 2.2, L, True)
    s.pl([(xr - r - 18, top), (xr - r - 30, top - 120), (xr + r + 10, top - 128), (xr + r + 40, top - 90), (xr + r + 18, top)], 2.2)
    for x in range(xr - 100, xr + 120, 22): s.ln(x, top - 100, x, top - 20, 1.2, T)
    s.ln(xr + 60, top - 128, xr + 64, top - 175, 2.0)
    cx1, cx2 = 470, 700
    s.pl([(cx1, top + 30), (cx1 + 12, top - 250), (cx2 - 12, top - 250), (cx2, top + 30)], 2.2)
    s.ln(cx1 - 20, top - 262, cx2 + 20, top - 262, 2.6); s.ln(cx1 - 10, top - 276, cx2 + 10, top - 276, 1.6)
    s.pl([(cx1 + 30, top - 225), (cx2 - 30, top - 225), (cx2 - 24, top - 90), (cx1 + 24, top - 90)], 1.4, T, True)
    s.pl([(540, top + 30), (545, top - 30), (600, top - 34), (606, top + 5)], 1.8)
    s.ln(625, top - 20, 650, top - 70, 1.8); s.circ(653, top - 75, 16, 1.6)
    s.dimh(xf, xr, 650, '3 400', y0 - r)
    s.dimh(xf - r - 18, xr + r + 40, 690, '4 650')
    s.dimv(1140, top - 276, y0, '3 050', xr + r + 40)
    s.txt(600, 40, 'Каток тандемный 10 т · вид сбоку', 16, 'middle')
    return s

# 4. Асфальтоукладчик, вид сбоку
def paver():
    s = S(1200, 740); y0 = 640
    s.ln(30, y0, 1170, y0, 1.2, T)
    s.rect(330, 560, 560, 80, 2.2, L, 40)
    for x in (372, 848): s.circ(x, 600, 34, 2.0); s.circ(x, 600, 10, 1.2)
    for x in range(430, 800, 62): s.circ(x, 618, 16, 1.4)
    for x in range(350, 880, 18): s.ln(x, 640, x + 6, 646, 1.0, T)
    s.pl([(300, 560), (300, 400), (880, 400), (900, 560)], 2.2)
    for x in range(340, 640, 24): s.ln(x, 420, x, 480, 1.2, T)
    s.pl([(880, 470), (1090, 350), (1110, 360), (1100, 520), (900, 560)], 2.2)
    s.ln(900, 470, 1100, 520, 1.2, T)
    s.pl([(80, 560), (300, 560), (300, 625), (60, 625), (60, 585)], 2.2, L, True)
    s.ln(70, 600, 290, 600, 1.2, T); s.ln(40, 560, 80, 560, 1.4)
    s.circ(250, 590, 22, 1.4)
    for k in range(5): s.path(f'M{240 + k*9},{576} l6,28', 1.0, T)
    s.ln(430, 400, 440, 140, 2.2); s.ln(760, 400, 750, 140, 2.2)
    s.ln(840, 400, 850, 300, 2.0); s.ln(838, 300, 862, 300, 2.0)
    s.pl([(690, 400), (700, 330), (740, 326), (745, 360)], 1.6, T)
    s.ln(390, 132, 800, 132, 2.6); s.ln(400, 118, 790, 118, 1.6)
    s.pl([(520, 400), (528, 330), (600, 325), (605, 370)], 1.8); s.ln(640, 330, 670, 290, 1.8); s.ln(652, 286, 690, 294, 2.0)
    s.dimh(60, 1110, 700, '6 170', y0)
    s.dimv(1160, 118, y0, '3 900', 1110)
    s.dimh(60, 300, 520, 'плита 2 500', 560)
    s.txt(600, 60, 'Асфальтоукладчик гусеничный · вид сбоку', 16, 'middle')
    return s

# 5. Самосвальный полуприцеп с тягачом
def tipper():
    s = S(1200, 640); y0 = 560; r = 46
    s.ln(20, y0, 1180, y0, 1.2, T)
    s.pl([(60, 180), (780, 180), (790, 430), (70, 430)], 2.4, L, True)
    for x in range(110, 760, 54): s.ln(x, 180, x + 2, 430, 1.4, T)
    s.ln(60, 210, 780, 210, 1.4); s.ln(70, 400, 790, 400, 1.4)
    s.ln(60, 180, 46, 430, 2.0); s.ln(46, 430, 70, 430, 2.0)
    s.pl([(90, 430), (90, 470), (860, 470), (860, 450)], 2.2)
    for x in (420, 520, 620): wheel(s, x, y0 - r, r)
    s.ln(330, 470, 330, 520, 1.6); s.ln(310, 520, 350, 520, 1.6)
    s.pl([(860, 470), (870, 230), (980, 210), (1080, 260), (1110, 330), (1120, 470)], 2.4, L, True)
    s.pl([(980, 225), (1068, 268), (1090, 330), (985, 330)], 1.6, T, True)
    s.ln(880, 330, 1120, 330, 1.2, T); s.rect(900, 360, 70, 12, 1.4, T, 6)
    s.ln(800, 480, 1150, 480, 2.2); s.pl([(1120, 470), (1150, 470), (1150, 520), (1120, 520)], 1.8)
    for x in (840, 940, 1090): wheel(s, x, y0 - r, r)
    s.ln(800, 450, 860, 450, 2.0)
    s.dimh(46, 1150, 610, '16 500')
    s.dimv(24, 180, y0, '3 800', 46)
    s.txt(420, 150, 'кузов 32 м³', 15, 'middle')
    s.txt(600, 60, 'Самосвальный полуприцеп с седельным тягачом · вид сбоку', 16, 'middle')
    return s

os.makedirs('/home/claude/draw/svg', exist_ok=True)
for name, f in [('doroga-perspektiva', road), ('dorozhnaya-odezhda', section), ('katok', roller), ('asfaltoukladchik', paver), ('samosval', tipper)]:
    open(f'/home/claude/draw/svg/{name}.svg', 'w').write(f().svg())
print('ok')
