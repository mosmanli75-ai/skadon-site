#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Статичная поза тессеракта (та, на которой останавливается анимация) → SVG + favicon."""
import math, json, os

Q = math.pi / 2
T1, T2, T3 = 2, 3, 5
INK   = (0x0D, 0x17, 0x16)
SLATE = (0x12, 0x31, 0x2F)

# эйлеров обход рёбер гиперкуба — как в app.js
adj = [[v ^ (1 << k) for k in range(4)] for v in range(16)]
used, st, out = set(), [0], []
key = lambda a, b: (min(a, b), max(a, b))
while st:
    v = st[-1]; n = -1
    for w in adj[v]:
        if key(v, w) not in used:
            n = w; break
    if n < 0: out.append(st.pop())
    else: used.add(key(v, n)); st.append(n)
CIRC = out[::-1]

VTX = [[1 if v & 1 else -1, 1 if v & 2 else -1,
        1 if v & 4 else -1, 1 if v & 8 else -1] for v in range(16)]

def project(e, S):
    a1, a2, a3 = Q*T1*e, Q*T2*e, Q*T3*e
    P, K = [], []
    for a in VTX:
        x, y, z, w = a
        c, s = math.cos(a1), math.sin(a1); x, y = x*c - y*s, x*s + y*c
        c, s = math.cos(a2), math.sin(a2); x, w = x*c - w*s, x*s + w*c
        c, s = math.cos(a3), math.sin(a3); z, w = z*c - w*s, z*s + w*c
        k4 = 2.75 / (2.75 - w); X, Y, Z = x*k4, y*k4, z*k4
        k3 = 4.4 / (4.4 - Z)
        P.append((X*k3*S, Y*k3*S)); K.append(k4*k3)
    return P, K

maxR = 0
for i in range(361):
    e = 1 - (1 - i/360) ** 5
    P, _ = project(e, 1)
    maxR = max(maxR, max(math.hypot(x, y) for x, y in P))

def svg(size=112, pad=4, lw=1.0, flat=None, bg=None, rounded=False):
    S = (size/2 - pad) / maxR
    P, K = project(1.0, S)
    kmin, kmax = min(K), max(K)
    span = max(1e-6, kmax - kmin)
    parts = []
    if bg:
        r = f' rx="{size*0.22:.1f}"' if rounded else ''
        parts.append(f'<rect width="{size}" height="{size}"{r} fill="{bg}"/>')
    parts.append(f'<g transform="translate({size/2},{size/2})" stroke-linecap="round">')
    for i in range(len(CIRC) - 1):
        a, b = P[CIRC[i]], P[CIRC[i+1]]
        d = ((K[CIRC[i]] + K[CIRC[i+1]]) / 2 - kmin) / span
        if flat:
            col, op, w = flat, 1, lw * (0.9 + 1.7*d) * (size/100)
        else:
            c = [INK[j] + (SLATE[j] - INK[j]) * (1 - d) for j in range(3)]
            col = '#%02X%02X%02X' % tuple(int(v) for v in c)
            op = round(0.24 + 0.76*d, 3)
            w = lw * (0.9 + 1.7*d) * (size/100)
        parts.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" '
                     f'stroke="{col}" stroke-opacity="{op}" stroke-width="{w:.2f}"/>')
    parts.append('</g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
            f'width="{size}" height="{size}">' + ''.join(parts) + '</svg>')

os.makedirs('assets', exist_ok=True)

# для PDF и печати — на белом
open('assets/logo-static.svg', 'w', encoding='utf-8').write(svg(160, 6, 1.0))
# favicon — контрастнее, линии толще
open('favicon.svg', 'w', encoding='utf-8').write(svg(64, 3, 2.1, flat='#0D1716'))
# для iOS — на светлой плашке
open('apple-touch-icon.svg', 'w', encoding='utf-8').write(
    svg(180, 22, 1.6, flat='#0D1716', bg='#E8EEED', rounded=False))

print('logo-static.svg, favicon.svg, apple-touch-icon.svg готовы; рёбер:', len(CIRC) - 1)
