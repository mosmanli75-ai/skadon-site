#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает assets/calc-data.js из calc/rascenki.xlsx.

Запускать из папки сайта:  python3 tools/build_calc_data.py
"""
import json, sys, datetime
import openpyxl

SRC = sys.argv[1] if len(sys.argv) > 1 else '../../calc/rascenki.xlsx'
DST = sys.argv[2] if len(sys.argv) > 2 else 'assets/calc-data.js'

PRICE_SHEETS = ['Бетон','Металл','Каменные','Отделка','Мокрые фасады','Вентфасады','Кровля','Услуги']

# ── ключ схемы по названию работы ──────────────────────────────────────────
ICON_RULES = [
    ('подготовк',        'prep'),
    ('фундаментной плит','plate'),
    ('ленточн',          'strip'),
    ('ростверк',         'grill'),
    ('сва',              'pile'),
    ('стакан',           'cup'),
    ('под оборудование', 'equip'),
    ('подпорн',          'retain'),
    ('монолитных стен',  'wall'),
    ('колонн',           'column'),
    ('пилон',            'pylon'),
    ('перекрытий с ригел','slabbeam'),
    ('перекрыт',         'slab'),
    ('лестни',           'stairs'),
    ('шахт',             'shaft'),
    ('пояс',             'belt'),
    ('пол',              'floor'),
    ('отмостк',          'apron'),
    ('демонтаж',         'demo'),
    ('усилен',           'reinf'),
]

def icon_for(name):
    n = name.lower()
    for key, ic in ICON_RULES:
        if key in n:
            return ic
    return 'plate'

def num(v):
    if isinstance(v, (int, float)):
        return float(v)
    return None

def main():
    wb = openpyxl.load_workbook(SRC, data_only=True)
    works, addon_names = [], {}

    for sheet in PRICE_SHEETS:
        if sheet not in wb.sheetnames:
            continue
        ws = wb[sheet]
        head = [c.value for c in ws[3]]
        try:
            i_unit = head.index('Ед. изм.')
            i_work = head.index('Работа')
        except ValueError:
            continue
        i_spread = head.index('Разброс, %') if 'Разброс, %' in head else None
        addon_cols = [(i, h) for i, h in enumerate(head)
                      if isinstance(h, str) and h.startswith('+')]

        for row in ws.iter_rows(min_row=4, values_only=True):
            name = row[0]
            if not isinstance(name, str) or not name.strip():
                continue
            if name.startswith('ПРИМЕР') or name.startswith('Пустая'):
                continue
            base = num(row[i_work]) if i_work < len(row) else None
            if not base:
                continue                       # цена не заполнена — на сайт не идёт
            a = {}
            for i, h in addon_cols:
                v = num(row[i]) if i < len(row) else None
                if v:
                    a[h] = v
                    addon_names[h] = h.lstrip('+ ').replace(' (без НДС)', '')
            works.append({
                'g': sheet,
                'n': name.strip(),
                'u': (row[i_unit] or '').strip() if isinstance(row[i_unit], str) else '',
                'b': base,
                'a': a,
                's': num(row[i_spread]) if i_spread is not None and i_spread < len(row) else None,
                'i': icon_for(name),
            })

    def pairs(sheet, r0=4):
        out = []
        if sheet not in wb.sheetnames:
            return out
        for row in wb[sheet].iter_rows(min_row=r0, values_only=True):
            if isinstance(row[0], str) and isinstance(num(row[1]), float):
                out.append([row[0].strip(), num(row[1])])
        return out

    objects = pairs('Коэффициенты')
    regions = pairs('Регионы')

    cfg = {}
    for row in wb['Настройки'].iter_rows(min_row=3, values_only=True):
        if isinstance(row[0], str):
            cfg[row[0].strip()] = row[1]

    updated = cfg.get('Дата обновления расценок')
    if isinstance(updated, datetime.datetime):
        updated = updated.date().isoformat()
    elif updated is not None:
        updated = str(updated)

    data = {
        'works':   works,
        'addons':  addon_names,
        'objects': objects,
        'regions': regions,
        'nds':     num(cfg.get('Коэффициент НДС')) or 1.27,
        'spread':  num(cfg.get('Разброс по умолчанию, %')) or 5,
        'note':    cfg.get('Текст оговорки на сайте') or '',
        'updated': updated or '',
    }
    for w in data['works']:
        if w['s'] is None:
            w['s'] = data['spread']

    with open(DST, 'w', encoding='utf-8') as f:
        f.write('/* Сгенерировано из calc/rascenki.xlsx — руками не править. */\n')
        f.write('window.CALC = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')

    print(f'{DST}: {len(works)} работ, {len(objects)} типов объекта, '
          f'{len(regions)} регионов, разброс {data["spread"]}%, обновлено {data["updated"]}')

main()
