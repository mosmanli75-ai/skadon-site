#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Приём заявок и расчётов с сайта skadon.ru.
Слушает 127.0.0.1:8787, за ним Caddy. Без внешних зависимостей.

  POST /api/lead   — JSON, до 64 КБ
  GET  /api/health — проверка

Каждая заявка кладётся в файл и уходит письмом.
Настройки — в /etc/skadon-lead.env (см. deploy.md).
"""
import json, os, re, smtplib, ssl, sys, time, uuid
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timezone, timedelta

HOST      = os.environ.get('LEAD_HOST', '127.0.0.1')
PORT      = int(os.environ.get('LEAD_PORT', '8787'))
STORE     = os.environ.get('LEAD_STORE', '/var/lib/skadon/leads')
MAX_BODY  = 64 * 1024
RATE_N    = 12            # заявок с одного IP
RATE_WIN  = 600           # за 10 минут

SMTP_HOST = os.environ.get('SMTP_HOST', '')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '465'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
MAIL_TO   = os.environ.get('MAIL_TO', '')
MAIL_FROM = os.environ.get('MAIL_FROM', SMTP_USER)

MSK  = timezone(timedelta(hours=3))
hits = {}

def now():
    return datetime.now(MSK)

def allowed(ip):
    t = time.time()
    q = [x for x in hits.get(ip, []) if t - x < RATE_WIN]
    q.append(t)
    hits[ip] = q
    if len(hits) > 4000:
        for k in [k for k, v in hits.items() if not v or t - v[-1] > RATE_WIN]:
            hits.pop(k, None)
    return len(q) <= RATE_N

def clean(v, n=400):
    if v is None:
        return ''
    s = str(v).replace('\r', ' ').replace('\x00', '')
    s = re.sub(r'[‪-‮⁦-⁩]', '', s)
    return s[:n].strip()

def rub(n):
    try:
        return '{:,.0f}'.format(float(n)).replace(',', ' ') + ' ₽'
    except Exception:
        return '—'

def as_text(d):
    """человекочитаемое письмо"""
    kind = clean(d.get('kind'), 40) or 'lead'
    L = []
    if kind == 'calc':
        L.append('РАСЧЁТ С САЙТА')
        L.append('')
        L.append('Объект:  ' + clean(d.get('obj'), 80))
        L.append('Регион:  ' + clean(d.get('region'), 80))
        L.append('Расчёт:  ' + ('с НДС' if d.get('nds') else 'без НДС'))
        rows = d.get('rows') or []
        if isinstance(rows, list) and rows:
            L.append('')
            L.append('Работы:')
            for r in rows[:40]:
                if not isinstance(r, dict):
                    continue
                vol = r.get('vol')
                L.append('  · {n} — {v} {u} × {p} = {s}'.format(
                    n=clean(r.get('n'), 90),
                    v=(clean(vol, 20) if vol else '—'),
                    u=clean(r.get('u'), 8),
                    p=rub(r.get('price')),
                    s=(rub(r.get('sum')) if r.get('sum') else '—')))
        inc = d.get('inc')
        if isinstance(inc, list) and inc:
            L.append('')
            L.append('Входит: ' + ', '.join(clean(x, 40) for x in inc[:20]))
        if d.get('lo'):
            L.append('')
            L.append('Итого:   ' + rub(d.get('lo')) + ' – ' + rub(d.get('hi')))
        if d.get('how'):
            L.append('')
            L.append('Клиент сохранил как: ' + clean(d.get('how'), 10))
    else:
        L.append('ЗАЯВКА С САЙТА')
        L.append('')
        for k in ('name', 'phone', 'email', 'prof', 'exp', 'where', 'crew', 'msg', 'text', 'about'):
            if d.get(k):
                L.append('{:8s} {}'.format(k + ':', clean(d.get(k), 900)))
    L.append('')
    L.append('—')
    L.append('Страница: ' + clean(d.get('page'), 120))
    L.append('Время:    ' + now().strftime('%d.%m.%Y %H:%M МСК'))
    return '\n'.join(L)

def subject(d):
    if clean(d.get('kind'), 40) == 'calc':
        obj = clean(d.get('obj'), 40) or 'объект'
        if d.get('lo'):
            return 'Расчёт с сайта · {} · {} – {}'.format(obj, rub(d.get('lo')), rub(d.get('hi')))
        return 'Расчёт с сайта · ' + obj
    who = clean(d.get('name'), 40) or clean(d.get('phone'), 40) or 'без имени'
    return 'Заявка с сайта · ' + who

def store(d, ip):
    try:
        os.makedirs(STORE, exist_ok=True)
        name = now().strftime('%Y-%m-%d_%H%M%S') + '_' + uuid.uuid4().hex[:6] + '.json'
        rec = {'at': now().isoformat(), 'ip': ip, 'data': d}
        with open(os.path.join(STORE, name), 'w', encoding='utf-8') as f:
            json.dump(rec, f, ensure_ascii=False, indent=1)
        return name
    except Exception as e:
        print('store failed:', e, file=sys.stderr, flush=True)
        return None

def mail(d):
    if not (SMTP_HOST and MAIL_TO and MAIL_FROM):
        print('smtp not configured — письмо не отправлено', file=sys.stderr, flush=True)
        return False
    m = EmailMessage()
    m['Subject'] = subject(d)
    m['From'] = MAIL_FROM
    m['To'] = MAIL_TO
    if d.get('email'):
        m['Reply-To'] = clean(d.get('email'), 120)
    m.set_content(as_text(d))
    try:
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=20,
                                  context=ssl.create_default_context()) as s:
                if SMTP_USER:
                    s.login(SMTP_USER, SMTP_PASS)
                s.send_message(m)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as s:
                s.ehlo()
                try:
                    s.starttls(context=ssl.create_default_context())
                    s.ehlo()
                except Exception:
                    pass
                if SMTP_USER:
                    s.login(SMTP_USER, SMTP_PASS)
                s.send_message(m)
        return True
    except Exception as e:
        print('mail failed:', e, file=sys.stderr, flush=True)
        return False


class H(BaseHTTPRequestHandler):
    server_version = 'skadon-lead'
    protocol_version = 'HTTP/1.1'

    def log_message(self, fmt, *a):
        print('%s %s' % (now().strftime('%H:%M:%S'), fmt % a), flush=True)

    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _ip(self):
        return (self.headers.get('X-Forwarded-For', '').split(',')[0].strip()
                or self.client_address[0])

    def do_GET(self):
        if self.path.rstrip('/') == '/api/health':
            self._send(200, {'ok': True, 'smtp': bool(SMTP_HOST and MAIL_TO)})
        else:
            self._send(404, {'ok': False})

    def do_POST(self):
        if self.path.rstrip('/') != '/api/lead':
            return self._send(404, {'ok': False})
        ip = self._ip()
        if not allowed(ip):
            return self._send(429, {'ok': False, 'error': 'too many'})
        try:
            n = int(self.headers.get('Content-Length') or 0)
        except ValueError:
            n = 0
        if n <= 0 or n > MAX_BODY:
            return self._send(413, {'ok': False, 'error': 'bad size'})
        try:
            d = json.loads(self.rfile.read(n).decode('utf-8'))
            if not isinstance(d, dict):
                raise ValueError
        except Exception:
            return self._send(400, {'ok': False, 'error': 'bad json'})
        if d.get('hp'):                       # honeypot
            return self._send(200, {'ok': True})
        name = store(d, ip)
        sent = mail(d)
        print('lead {} kind={} mail={}'.format(name, clean(d.get('kind'), 20), sent), flush=True)
        self._send(200, {'ok': True})


if __name__ == '__main__':
    print('skadon-lead на {}:{} · хранилище {} · почта {}'.format(
        HOST, PORT, STORE, MAIL_TO or 'не настроена'), flush=True)
    ThreadingHTTPServer((HOST, PORT), H).serve_forever()
