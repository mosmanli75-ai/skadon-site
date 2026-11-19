#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Запускать из папки сайта:  python3 tools/build_icons.py

Генерирует assets/calc-icons.js — изометрические схемы конструкций и типов объектов.
Грани непрозрачные, порядок отрисовки — от дальних к ближним."""
import math, json

COS = math.cos(math.radians(30))

def iso(p):
    x, y, z = p
    return ((x - y) * COS, (x + y) * 0.5 - z)

def flat(p):
    x, y, z = p
    return (x, -z)

# ── палитра (переопределяется CSS-переменными на выбранной карточке) ────────
A  = 'var(--ic-a,#E8EEED)'   # верх
B  = 'var(--ic-b,#D2DEDB)'   # левая грань
C  = 'var(--ic-c,#B4C6C3)'   # правая грань
D  = 'var(--ic-d,#F0F4F3)'   # контекст
E  = 'var(--ic-e,#9FB2AF)'   # тень, вырезы
S1 = 'var(--ic-s,#2E3B39)'   # контур основной
S2 = 'var(--ic-t,#8B9C99)'   # контур контекста

ST = {
 'top': f'fill="{A}" stroke="{S1}" stroke-width="1.15" stroke-linejoin="round"',
 'lft': f'fill="{B}" stroke="{S1}" stroke-width="1.15" stroke-linejoin="round"',
 'rgt': f'fill="{C}" stroke="{S1}" stroke-width="1.15" stroke-linejoin="round"',
 'ctx': f'fill="{D}" stroke="{S2}" stroke-width=".95" stroke-linejoin="round"',
 'cut': f'fill="{E}" stroke="{S1}" stroke-width="1.05" stroke-linejoin="round"',
 'fil': f'fill="{C}" stroke="{S1}" stroke-width="1.15" stroke-linejoin="round"',
 'gnd': f'fill="none" stroke="{S2}" stroke-width=".95" stroke-linejoin="round"',
 'ln':  f'fill="none" stroke="{S2}" stroke-width=".95" stroke-linecap="round"',
 'lnm': f'fill="none" stroke="{S1}" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"',
 'dsh': f'fill="none" stroke="{S2}" stroke-width=".95" stroke-dasharray="3 3"',
 'hat': f'fill="none" stroke="{S2}" stroke-width=".85"',
}

# ── примитивы: каждая функция возвращает список ГРУПП ───────────────────────
def _depth(pts):
    return sum(x + y + z for x, y, z in pts) / len(pts)

def grp(els, d=None):
    pts = [p for e in els for p in e['p']]
    return [{'d': _depth(pts) if d is None else d, 'els': els}]

def poly(pts, s):  return {'t': 'poly', 'p': pts, 's': s}
def pline(pts, s): return {'t': 'line', 'p': pts, 's': s}

def line(pts, s='ln', d=None):  return grp([pline(pts, s)], d)
def face(pts, s, d=None):       return grp([poly(pts, s)], d)

def box(x, y, z, dx, dy, dz, kind='m', d=None):
    X, Y, Z = x + dx, y + dy, z + dz
    top = [(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]
    rgt = [(X,y,z),(X,Y,z),(X,Y,Z),(X,y,Z)]
    lft = [(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)]
    if kind == 'c':
        els = [poly(lft,'ctx'), poly(rgt,'ctx'), poly(top,'ctx')]
    else:
        els = [poly(lft,'lft'), poly(rgt,'rgt'), poly(top,'top')]
    return grp(els, d if d is not None else (x+X)/2 + (y+Y)/2 + (z+Z)/2)

def ground(x=-4, y=-4, dx=50, dy=50):
    return face([(x,y,0),(x+dx,y,0),(x+dx,y+dy,0),(x,y+dy,0)], 'gnd', d=-9999)

SC, OB, PROJ, INSET = {}, {}, {}, {}

# ═══ КОНСТРУКЦИИ ════════════════════════════════════════════════════════════

# 1 · бетонная подготовка — разрез, слои
SC['prep'] = (
    face([(0,0,-11),(62,0,-11),(62,0,-4),(0,0,-4)], 'ctx') +
    sum([line([(2+i*7,0,-11),(7+i*7,0,-4)], 'hat') for i in range(9)], []) +
    face([(0,0,-4),(62,0,-4),(62,0,0),(0,0,0)], 'ctx') +
    sum([line([(3+i*5,0,-2),(4.6+i*5,0,-2)], 'ln') for i in range(12)], []) +
    face([(0,0,0),(62,0,0),(62,0,3.6),(0,0,3.6)], 'fil') +
    line([(66,0,0),(66,0,3.6)], 'lnm') + line([(63,0,0),(69,0,0)], 'ln') +
    line([(63,0,3.6),(69,0,3.6)], 'ln')
)
PROJ['prep'] = 'flat'

# 2 · фундаментная плита
SC['plate'] = ground() + box(0,0,-3, 42,42,3,'c') + box(2,2,0, 38,38,7)

# 3 · ленточный фундамент — замкнутый контур в траншее
def sc_strip():
    L, W, H = 44, 8, 12
    o = ground(-7,-7,58,58)
    o += face([(-4,-4,0),(L+4,-4,0),(L+4,L+4,0),(-4,L+4,0)], 'gnd')
    o += box(0,0,-H, L,W,H)          # дальняя
    o += box(0,0,-H, W,L,H)          # левая
    o += box(L-W,0,-H, W,L,H)        # правая
    o += box(0,L-W,-H, L,W,H)        # ближняя
    for i in range(4):               # штриховка грунта снаружи
        o += line([(-4,-4+i*13,0),(-8,-8+i*13,0)], 'hat')
        o += line([(-4+i*13,L+4,0),(-8+i*13,L+8,0)], 'hat')
    return o
SC['strip'] = sc_strip()

# 4 · ростверк — балка поверх свай
def sc_grill():
    o = ground(-6,0,58,24)
    for px in (1, 17, 33):
        o += box(px,6,-18, 8,8,18,'c')
        o += line([(px,6,-18),(px,6,-24)], 'dsh')
    o += line([(-6,10,0),(52,10,0)], 'ln')
    o += box(-2,3,0, 48,13,9, d=9999)
    return o
SC['grill'] = sc_grill()

# 5 · сваи буронабивные — разрез, стволы в грунте
SC['pile'] = (
    face([(0,0,-52),(72,0,-52),(72,0,0),(0,0,0)], 'ctx') +
    sum([line([(3+i*8,0,-50),(11+i*8,0,-42)], 'hat') for i in range(9)], []) +
    sum([line([(3+i*8,0,-28),(11+i*8,0,-20)], 'hat') for i in range(9)], []) +
    line([(0,0,0),(72,0,0)], 'lnm') +
    face([(12,0,-46),(26,0,-46),(26,0,6),(12,0,6)], 'fil') +
    face([(44,0,-38),(58,0,-38),(58,0,6),(44,0,6)], 'fil') +
    sum([line([(14,0,-40+i*9),(24,0,-40+i*9)], 'ln') for i in range(5)], []) +
    sum([line([(46,0,-32+i*9),(56,0,-32+i*9)], 'ln') for i in range(4)], []) +
    line([(19,0,6),(19,0,14)], 'lnm') + line([(51,0,6),(51,0,14)], 'lnm')
)
PROJ['pile'] = 'flat'

# 6 · стакан под колонну — с раструбом
def sc_cup():
    o = ground(-6,-6,48,48)
    o += box(0,0,0, 34,34,6)
    o += box(8,8,6, 18,18,15)
    # вырез стакана: тёмное дно + внутренние стенки
    o += face([(11,11,14),(23,11,14),(23,23,14),(11,23,14)], 'cut', d=9999)
    o += face([(11,11,14),(11,11,21),(11,23,21),(11,23,14)], 'cut', d=9999)
    o += face([(11,11,14),(11,11,21),(23,11,21),(23,11,14)], 'cut', d=9999)
    o += line([(11,11,21),(23,11,21),(23,23,21),(11,23,21),(11,11,21)], 'lnm', d=10000)
    return o
SC['cup'] = sc_cup()

# 7 · фундамент под оборудование — анкеры и рама
def sc_equip():
    o = ground(-6,-6,52,46)
    o += box(0,0,0, 40,30,12)
    o += line([(5,5,20),(35,5,20),(35,25,20),(5,25,20),(5,5,20)], 'dsh', d=9998)
    for ax in (5, 20, 35):
        for ay in (5, 25):
            o += line([(ax,ay,12),(ax,ay,20)], 'lnm', d=9999)
            o += face([(ax-1.6,ay-1.6,12),(ax+1.6,ay-1.6,12),(ax+1.6,ay+1.6,12),(ax-1.6,ay+1.6,12)], 'cut', d=9999)
    return o
SC['equip'] = sc_equip()

# 8 · подпорная стена — разрез, перепад грунта
SC['retain'] = (
    face([(0,0,4),(27,0,4),(27,0,34),(0,0,34)], 'ctx') +
    sum([line([(2+i*6,0,7),(8+i*6,0,13)], 'hat') for i in range(4)], []) +
    sum([line([(2+i*6,0,20),(8+i*6,0,26)], 'hat') for i in range(4)], []) +
    face([(35,0,0),(70,0,0),(70,0,7),(35,0,7)], 'ctx') +
    sum([line([(37+i*6,0,0),(43+i*6,0,6)], 'hat') for i in range(5)], []) +
    face([(20,0,0),(48,0,0),(48,0,7),(35,0,7),(35,0,40),(27,0,40),(27,0,7),(20,0,7)], 'fil') +
    line([(12,0,28),(23,0,28)], 'lnm') + line([(19,0,25),(23,0,28),(19,0,31)], 'lnm')
)
PROJ['retain'] = 'flat'

# 9 · монолитные стены — угол с проёмом
def sc_wall():
    o = ground(-6,-6,54,50)
    o += box(0,0,0, 6,38,4,'c')
    o += box(0,0,0, 34,6,4,'c')
    o += box(0,0,4, 34,6,30)              # дальняя стена
    o += box(0,0,4, 6,38,30)              # левая стена
    # дверной проём в правой (видимой) грани левой стены
    o += face([(6,14,4),(6,26,4),(6,26,24),(6,14,24)], 'cut', d=9999)
    # оконный проём в дальней стене
    o += face([(14,6,16),(26,6,16),(26,6,27),(14,6,27)], 'cut', d=9999)
    return o
SC['wall'] = sc_wall()

# 10 · колонны — квадратные
def sc_column():
    o = ground(-6,-6,52,48)
    o += box(0,0,0, 40,36,4,'c')
    o += box(4,22,4, 9,9,32)
    o += box(25,6,4, 9,9,32)
    return o
SC['column'] = sc_column()
INSET['column'] = 'sq'

# 11 · пилоны — вытянутые в плане
def sc_pylon():
    o = ground(-6,-6,52,48)
    o += box(0,0,0, 40,36,4,'c')
    o += box(2,4,4, 6,28,32)
    o += box(23,4,4, 6,28,32)
    return o
SC['pylon'] = sc_pylon()
INSET['pylon'] = 'rect'

# 12 · безбалочное перекрытие
def sc_slab():
    o = []
    for cx, cy in ((2,2),(2,27),(27,2),(27,27)):
        o += box(cx,cy,0, 8,8,26,'c')
    o += box(-3,-3,26, 44,44,6)
    return o
SC['slab'] = sc_slab()
INSET['slab'] = 'plate'

# 13 · перекрытие с ригелями
def sc_slabbeam():
    o = []
    for cx, cy in ((2,2),(2,27),(27,2),(27,27)):
        o += box(cx,cy,0, 8,8,22,'c')
    o += box(2,2,22, 33,6,8)
    o += box(2,2,22, 6,33,8)
    o += box(2,29,22, 33,6,8)
    o += box(29,2,22, 6,33,8)
    o += box(-3,-3,30, 44,44,5)
    return o
SC['slabbeam'] = sc_slabbeam()
INSET['slabbeam'] = 'tee'

# 14 · лестничный марш и площадка
def sc_stairs():
    """марш как призма со ступенчатым профилем + площадка"""
    o = ground(-6,-6,64,44)
    y0, y1 = 6, 30
    prof = [(0,0)]
    for i in range(6):
        prof.append((i*8, 6 + i*6))
        prof.append((i*8 + 8, 6 + i*6))
    prof.append((48, 0))
    near = [(x, y1, z) for x, z in prof]
    # верхние площадки ступеней и подступенки
    for i in range(6):
        x, z = i*8, 6 + i*6
        o += face([(x,y0,z),(x+8,y0,z),(x+8,y1,z),(x,y1,z)], 'top', d=100+i*10+1)
        o += face([(x,y0,z-6),(x,y1,z-6),(x,y1,z),(x,y0,z)], 'rgt', d=100+i*10)
    o += face(near, 'lft', d=900)
    o += face([(48,y0,36),(48,y1,36),(48,y1,0),(48,y0,0)], 'rgt', d=901)
    o += box(48, 4, 30, 18, 28, 6, d=9999)
    return o
SC['stairs'] = sc_stairs()

# 15 · лифтовая шахта с приямком
def sc_shaft():
    o = ground(-8,-8,56,56)
    o += face([(2,2,-10),(32,2,-10),(32,32,-10),(2,32,-10)], 'cut')
    o += box(2,2,-10, 32,6,10,'c')
    o += box(2,2,-10, 6,32,10,'c')
    o += box(2,2,0, 32,6,36)
    o += box(2,2,0, 6,32,36)
    o += box(28,2,0, 6,32,36)
    o += line([(8,8,0),(28,8,0),(28,28,0),(8,28,0)], 'dsh', d=9999)
    return o
SC['shaft'] = sc_shaft()

# 16 · монолитный пояс по верху кладки
def sc_belt():
    o = ground(-6,-6,56,44)
    for r in range(3):
        off = 0 if r % 2 == 0 else 6.5
        x = off
        while x < 44:
            w = min(12, 44 - x)
            if w > 3:
                o += box(x, 6, r*6, w-1, 22, 5.4, 'c')
            x += 12
    o += box(-1, 5, 18, 46, 24, 8, d=9999)
    return o
SC['belt'] = sc_belt()

# 17 · промышленные полы — деформационные швы
def sc_floor():
    o = ground(-7,-7,58,58)
    o += box(0,0,0, 44,44,5)
    for i in (11, 22, 33):
        o += line([(i,0,5),(i,44,5)], 'ln', d=9999)
        o += line([(0,i,5),(44,i,5)], 'ln', d=9999)
    return o
SC['floor'] = sc_floor()

# 18 · отмостка — разрез, уклон от стены
SC['apron'] = (
    face([(0,0,-10),(70,0,-10),(70,0,0),(0,0,0)], 'ctx') +
    sum([line([(3+i*7,0,-10),(9+i*7,0,-3)], 'hat') for i in range(10)], []) +
    face([(0,0,0),(16,0,0),(16,0,44),(0,0,44)], 'ctx') +
    line([(0,0,12),(16,0,12)], 'ln') + line([(0,0,26),(16,0,26)], 'ln') +
    face([(16,0,12),(62,0,1),(62,0,-4),(16,0,7)], 'fil') +
    line([(22,0,20),(54,0,13)], 'lnm') + line([(50,0,10.5),(54,0,13),(49,0,16)], 'lnm')
)
PROJ['apron'] = 'flat'

# 19 · демонтаж — отбитый верх, торчащая арматура
def sc_demo():
    o = ground(-6,-6,56,44)
    o += box(0,0,0, 38,26,5,'c')
    o += box(0,0,5, 20,26,18)
    # рваный скол по верху
    o += line([(20,0,23),(24,5,19),(21,11,24),(26,18,18),(22,26,23)], 'lnm', d=9999)
    for i, yy in enumerate((4, 12, 21)):
        o += line([(20+i*1.5,yy,23),(26+i*1.5,yy,28),(23+i*1.5,yy,31),(29+i*1.5,yy,34)], 'lnm', d=9999)
    for bx, by, bz in ((28,4,5),(33,14,5),(26,20,5)):
        o += box(bx,by,bz, 5,5,4)
    return o
SC['demo'] = sc_demo()

# 20 · усиление ЖБК — обойма вокруг колонны
def sc_reinf():
    o = ground(-8,-8,54,54)
    o += box(7,7,0, 12,12,34,'c')
    o += box(2,2,0, 22,22,5)
    for zz in (11, 21, 31):
        o += line([(2,2,zz),(24,2,zz),(24,24,zz),(2,24,zz),(2,2,zz)], 'lnm', d=9000+zz)
    for cx, cy in ((2,2),(24,2),(24,24),(2,24)):
        o += line([(cx,cy,5),(cx,cy,34)], 'lnm', d=9500)
    return o
SC['reinf'] = sc_reinf()

# ═══ ТИПЫ ОБЪЕКТОВ ══════════════════════════════════════════════════════════

def sc_house():
    o = ground(-8,-8,58,54)
    o += box(4,4,0, 32,28,17)
    o += face([(4,4,17),(36,4,17),(36,18,27),(4,18,27)], 'rgt')
    o += face([(4,32,17),(36,32,17),(36,18,27),(4,18,27)], 'top')
    o += face([(4,4,17),(4,32,17),(4,18,27)], 'lft')
    o += face([(36,4,17),(36,32,17),(36,18,27)], 'lft')
    o += face([(36,13,0),(36,21,0),(36,21,11),(36,13,11)], 'cut', d=9999)
    o += face([(36,4,10),(36,10,10),(36,10,15),(36,4,15)], 'cut', d=9999)
    o += box(24,22,23, 4,4,8, d=9999)
    return o
OB['house'] = sc_house()

def sc_shop():
    o = ground(-8,-8,64,54)
    o += box(2,4,0, 42,26,20)
    for i in range(3):
        o += face([(44,7+i*8,2),(44,13+i*8,2),(44,13+i*8,11),(44,7+i*8,11)], 'cut', d=9999)
    o += box(44,2,12, 8,30,2, d=10000)
    o += line([(44,2,20),(44,32,20)], 'ln', d=10001)
    return o
OB['shop'] = sc_shop()

def sc_hotel():
    o = ground(-8,-8,54,50)
    o += box(4,4,0, 28,24,46)
    for r in range(5):
        for c in range(4):
            o += face([(32,6+c*5,9+r*7),(32,9.4+c*5,9+r*7),(32,9.4+c*5,13+r*7),(32,6+c*5,13+r*7)], 'cut', d=9000+r)
    o += face([(32,14,0),(32,21,0),(32,21,7),(32,14,7)], 'cut', d=9999)
    o += face([(32,2,10),(32,30,10),(41,30,9),(41,2,9)], 'top', d=10000)
    return o
OB['hotel'] = sc_hotel()

def sc_plant():
    o = ground(-8,-8,62,56)
    o += box(2,4,0, 42,30,19)
    o += face([(2,4,19),(44,4,19),(44,19,27),(2,19,27)], 'rgt')
    o += face([(2,34,19),(44,34,19),(44,19,27),(2,19,27)], 'top')
    o += face([(44,4,19),(44,34,19),(44,19,27)], 'lft')
    o += face([(44,11,0),(44,27,0),(44,27,14),(44,11,14)], 'cut', d=9999)
    for i in range(3):
        o += line([(44,14+i*4,0),(44,14+i*4,14)], 'ln', d=10000)
    o += line([(10,4,19),(10,19,27),(10,34,19)], 'ln', d=10000)
    o += line([(26,4,19),(26,19,27),(26,34,19)], 'ln', d=10000)
    return o
OB['plant'] = sc_plant()

def sc_tower():
    o = ground(-10,-10,60,56)
    o += box(20,4,0, 22,22,32)
    for r in range(4):
        for c in range(3):
            o += face([(42,6+c*6,6+r*7),(42,10+c*6,6+r*7),(42,10+c*6,10+r*7),(42,6+c*6,10+r*7)], 'cut', d=9000+r)
    o += box(2,6,0, 18,22,54)
    for r in range(6):
        z = 10 + r*7
        o += box(20,9,z, 5,16,2, d=9500+r*10)
        o += line([(25,9,z+2),(25,9,z+5),(25,25,z+5),(25,25,z+2)], 'ln', d=9500+r*10+5)
    return o
OB['tower'] = sc_tower()

def sc_big():
    o = ground(-10,-10,72,64)
    o += box(2,28,0, 24,22,18)
    o += box(30,26,0, 22,24,29)
    o += box(4,2,0, 26,20,38)
    for r in range(4):
        o += line([(30,2,8+r*7),(30,22,8+r*7)], 'ln', d=9400+r)
    o += line([(44,8,0),(44,8,58)], 'lnm', d=9990)
    o += line([(41,8,0),(47,8,0)], 'lnm', d=9990)
    o += line([(24,8,54),(62,8,54)], 'lnm', d=9991)
    o += line([(44,8,58),(62,8,54)], 'ln', d=9991)
    o += line([(44,8,58),(26,8,54)], 'ln', d=9991)
    o += line([(56,8,54),(56,8,43)], 'ln', d=9992)
    o += line([(53.5,8,43),(58.5,8,43),(58.5,8,38),(53.5,8,38),(53.5,8,43)], 'lnm', d=9992)
    return o
OB['big'] = sc_big()

# ── врезки-сечения ─────────────────────────────────────────────────────────
def inset_svg(kind, vw=120, vh=94):
    w, h = 30, 24
    x, y = vw - w - 3, vh - h - 3
    bg = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{D}" stroke="{S2}" stroke-width=".9"/>'
    cx, cy = x + w/2, y + h/2
    st = f'fill="{C}" stroke="{S1}" stroke-width="1.15" stroke-linejoin="round"'
    if kind == 'sq':
        s = f'<rect x="{cx-6}" y="{cy-6}" width="12" height="12" {st}/>'
    elif kind == 'rect':
        s = f'<rect x="{cx-11}" y="{cy-3.5}" width="22" height="7" {st}/>'
    elif kind == 'plate':
        s = f'<rect x="{cx-11}" y="{cy-3}" width="22" height="6" {st}/>'
    else:  # tee
        s = (f'<rect x="{cx-11}" y="{cy-7}" width="22" height="5.5" {st}/>'
             f'<rect x="{cx-4}" y="{cy-2}" width="8" height="9" {st}/>')
    return bg + s

# ── сборка ──────────────────────────────────────────────────────────────────
def render(groups, proj='iso', inset=None, vw=120, vh=94, pad=5):
    f = flat if proj == 'flat' else iso
    pts = [f(p) for g in groups for e in g['els'] for p in e['p']]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    w, h = (maxx - minx) or 1, (maxy - miny) or 1
    bw = vw - 2*pad - (26 if inset else 0)
    s = min(bw / w, (vh - 2*pad) / h)
    ox = (vw - (26 if inset else 0) - w*s) / 2 - minx*s
    oy = (vh - h*s) / 2 - miny*s
    T = lambda p: (lambda P: f'{P[0]*s+ox:.1f},{P[1]*s+oy:.1f}')(f(p))
    out = []
    order = groups if proj == 'flat' else sorted(groups, key=lambda g: g['d'])
    for g in order:
        for e in g['els']:
            tag = 'polygon' if e['t'] == 'poly' else 'polyline'
            out.append(f'<{tag} points="{" ".join(T(p) for p in e["p"])}" {ST[e["s"]]}/>')
    if inset:
        out.append(inset_svg(inset, vw, vh))
    return ''.join(out)

icons  = {k: render(v, PROJ.get(k, 'iso'), INSET.get(k)) for k, v in SC.items()}
otypes = {k: render(v) for k, v in OB.items()}

with open('assets/calc-icons.js', 'w', encoding='utf-8') as f:
    f.write('/* Сгенерировано build_icons.py — руками не править. */\n')
    f.write('window.CALCICONS = ' + json.dumps(icons, ensure_ascii=False) + ';\n')
    f.write('window.CALCOBJICONS = ' + json.dumps(otypes, ensure_ascii=False) + ';\n')

tot = sum(len(v) for v in icons.values()) + sum(len(v) for v in otypes.values())
print(f'{len(icons)} схем конструкций, {len(otypes)} схем объектов, {tot/1024:.1f} КБ')
