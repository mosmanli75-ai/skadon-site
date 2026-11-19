#!/usr/bin/env bash
# Первичная настройка сервера skadon-web (Джино, 81.177.6.198) и заливка сайта.
# Запускать на маке:  bash "~/Desktop/Alliance Inc/1 Сайт/prototype/site/server/setup-jino.sh"
# Нужен SSH-ключ ~/.ssh/id_ed25519 (добавлен на сервер при создании).
# Повторный запуск безопасен: просто заново зальёт файлы сайта.
set -euo pipefail

HOST=root@81.177.6.198
SITE="$(cd "$(dirname "$0")/.." && pwd)"   # папка prototype/site

echo "== 1/3 Ставлю Caddy и настраиваю сервер =="
ssh -o StrictHostKeyChecking=accept-new "$HOST" 'bash -s' <<'REMOTE'
set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
if ! apt-get install -y -q caddy rsync; then
  # запасной вариант — официальный репозиторий Caddy
  apt-get install -y -q debian-keyring debian-archive-keyring apt-transport-https curl gnupg rsync
  curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/gpg.key | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt > /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -q && apt-get install -y -q caddy
fi
mkdir -p /var/www/skadon

cat > /etc/caddy/Caddyfile <<'CADDY'
skadon.ru {
	root * /var/www/skadon
	encode gzip zstd

	# без этого корень домена отдаёт 404 — проверено на практике
	rewrite / /index.html

	# приёмщик заявок (lead_service.py), подключается отдельно — см. deploy.md
	handle /api/* {
		reverse_proxy 127.0.0.1:8787
	}

	handle {
		try_files {path} {path}.html {path}/index.html
		file_server
	}
}

www.skadon.ru {
	redir https://skadon.ru{uri} permanent
}
CADDY

# файрвол: только SSH, HTTP, HTTPS
if command -v ufw >/dev/null; then
  ufw allow OpenSSH >/dev/null; ufw allow 80/tcp >/dev/null; ufw allow 443/tcp >/dev/null
  ufw --force enable >/dev/null
fi
REMOTE

echo "== 2/3 Заливаю сайт =="
rsync -az --delete --exclude 'server/' --exclude 'tools/' --exclude '.DS_Store' \
  "$SITE"/ "$HOST":/var/www/skadon/

echo "== 3/3 Запускаю Caddy =="
ssh "$HOST" 'chown -R caddy:caddy /var/www/skadon && caddy validate --config /etc/caddy/Caddyfile && systemctl enable caddy >/dev/null 2>&1; systemctl reload caddy || systemctl restart caddy; systemctl is-active caddy'

echo
echo "Готово. Проверка по IP (до смены DNS):"
curl -s -o /dev/null -w "  http://81.177.6.198/ -> %{http_code}\n" -H 'Host: skadon.ru' http://81.177.6.198/ || true
echo "После того как DNS skadon.ru смотрит на 81.177.6.198, Caddy сам выпустит сертификат."
