# Как обновить расценки на сайте

1. Правишь `~/Site/calc/rascenki.xlsx` (цены, коэффициенты, дату в листе «Настройки»).
2. **Закрываешь Excel** — иначе файл читается недописанным.
3. В терминале:

```bash
cd ~/Desktop/"Alliance Inc"/"1 Сайт"/prototype/site
python3 tools/build_calc_data.py ../../calc/rascenki.xlsx assets/calc-data.js
```

4. Заливаешь сайт:

```bash
scp -r ./* root@81.177.6.198:/var/www/skadon/
ssh root@81.177.6.198 'chown -R caddy:caddy /var/www/skadon && chmod -R u=rwX,go=rX /var/www/skadon'
```

## Остальные генераторы

`tools/build_icons.py` — схемы конструкций и типов объекта (`assets/calc-icons.js`).
Запускать, только если меняли сами рисунки.

`tools/build_logo.py` — статичный логотип для PDF и иконки вкладки
(`assets/logo-static.svg`, `favicon.svg`, `apple-touch-icon.svg`).
PNG-версии иконок пересобираются отдельно, из SVG.

Нужен `openpyxl`: `pip3 install openpyxl`
