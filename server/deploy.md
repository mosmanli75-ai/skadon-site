# Приём заявок и расчётов — установка на сервер

Один сервис на все формы сайта: расчёт с калькулятора, заявка с главной, анкета с вакансий.
Заявка сохраняется в файл **и** уходит письмом. Если почта отвалится — заявка не потеряется.

Все команды выполняешь ты сам на сервере, под root.

---

## 1. Положить файлы

С Mac:

```bash
scp ~/Desktop/"Alliance Inc"/"1 Сайт"/prototype/site/server/lead_service.py root@81.177.6.198:/tmp/
scp ~/Desktop/"Alliance Inc"/"1 Сайт"/prototype/site/server/skadon-lead.service root@81.177.6.198:/tmp/
```

На сервере:

```bash
useradd --system --no-create-home --shell /usr/sbin/nologin skadon 2>/dev/null || true
mkdir -p /opt/skadon /var/lib/skadon/leads
mv /tmp/lead_service.py /opt/skadon/
mv /tmp/skadon-lead.service /etc/systemd/system/
chown -R skadon:skadon /var/lib/skadon
chmod 755 /opt/skadon/lead_service.py
```

## 2. Настроить почту

Нужны данные SMTP того ящика, с которого будут уходить письма. Их даёт хостер почты
(если почта на Jino — в панели Jino, раздел «Почта»).

```bash
nano /etc/skadon-lead.env
```

Вставить и заполнить:

```
SMTP_HOST=smtp.jino.ru
SMTP_PORT=465
SMTP_USER=mustafa@osmanli.ru
SMTP_PASS=пароль_от_ящика
MAIL_FROM=mustafa@osmanli.ru
MAIL_TO=mustafa@osmanli.ru
```

Закрыть файл от чужих глаз:

```bash
chmod 600 /etc/skadon-lead.env
chown root:root /etc/skadon-lead.env
```

> Пароль от ящика живёт только в этом файле на сервере. В репозиторий, в чат и в код он не попадает.
> Если ящик поддерживает пароли приложений — заведи отдельный пароль для сайта, а не основной.

## 3. Запустить

```bash
systemctl daemon-reload
systemctl enable --now skadon-lead
systemctl status skadon-lead --no-pager
curl -s localhost:8787/api/health
```

Должно ответить `{"ok": true, "smtp": true}`. Если `"smtp": false` — не подхватился env-файл.

## 4. Добавить в Caddy

В `/etc/caddy/Caddyfile`, **внутри** блока `skadon.ru { ... }`, перед `file_server`:

```
	handle /api/* {
		reverse_proxy 127.0.0.1:8787
	}
```

Целиком блок должен выглядеть так:

```
skadon.ru {
	root * /var/www/skadon
	encode gzip zstd

	handle /api/* {
		reverse_proxy 127.0.0.1:8787
	}

	handle {
		try_files {path} {path}.html {path}/index.html {path}/
		file_server
	}
}
```

Применить:

```bash
caddy validate --config /etc/caddy/Caddyfile
systemctl reload caddy
```

## 5. Проверить целиком

```bash
curl -s -X POST https://skadon.ru/api/lead \
  -H 'Content-Type: application/json' \
  -d '{"kind":"calc","obj":"Проверка","region":"Ростов","lo":100000,"hi":110000}'
```

Ответ `{"ok": true}`, на почту приходит письмо «Расчёт с сайта · Проверка».
Файл появляется в `/var/lib/skadon/leads/`.

---

## Что смотреть потом

```bash
journalctl -u skadon-lead -n 50 --no-pager   # лог
ls -lt /var/lib/skadon/leads | head          # последние заявки
```

## Ограничения, которые уже стоят

- не больше 12 заявок с одного IP за 10 минут
- тело запроса не больше 64 КБ
- скрытое поле-ловушка для ботов
- сервис слушает только localhost, наружу торчит только через Caddy
- systemd режет ему доступ к файловой системе: писать может только в `/var/lib/skadon`

## Чего ещё нет

Формы на сайте (главная, вакансии) пока никуда не отправляют — к ним обработчик
подключим отдельно, вместе со страницей политики обработки персональных данных
и галочкой согласия. **До этого момента формы, собирающие имя и телефон,
включать нельзя** — это персональные данные, нужно уведомление в Роскомнадзор.

Расчёт с калькулятора персональных данных не содержит: уходят только параметры расчёта,
без имени, телефона и почты.
