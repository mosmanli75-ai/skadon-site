#!/bin/bash
# Забирает свежую версию сайта с GitHub и выкладывает в /var/www/skadon.
# Запускается таймером systemd раз в минуту.
set -euo pipefail
REPO=https://github.com/mosmanli75-ai/skadon-site
SRC=/opt/skadon-site
WEB=/var/www/skadon
STATE=/var/lib/skadon-deploy
mkdir -p "$STATE"
if [ ! -d "$SRC/.git" ]; then git clone -q --depth 1 "$REPO" "$SRC"; fi
cd "$SRC"
git fetch -q --depth 1 origin main
NEW=$(git rev-parse origin/main)
OLD=$(cat "$STATE/deployed" 2>/dev/null || true)
[ "$NEW" = "$OLD" ] && exit 0
git reset -q --hard origin/main
rsync -a --delete --exclude '.git/' --exclude 'server/' --exclude 'tools/' --exclude 'deploy/' --exclude 'README.md' "$SRC"/ "$WEB"/
chown -R caddy:caddy "$WEB"
echo "$NEW" > "$STATE/deployed"
echo "$(date '+%F %T') выложено $NEW" >> "$STATE/log"
