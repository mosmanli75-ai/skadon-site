#!/bin/bash
# Однократная установка автовыкладки на сервер. Запуск (с мака):
#   ssh root@81.177.6.198 'curl -fsSL https://raw.githubusercontent.com/mosmanli75-ai/skadon-site/main/deploy/install.sh | bash'
set -euo pipefail
command -v git >/dev/null && command -v rsync >/dev/null && command -v curl >/dev/null || { apt-get update -q && apt-get install -y -q git rsync curl; }
curl -fsSL https://raw.githubusercontent.com/mosmanli75-ai/skadon-site/main/deploy/skadon-pull.sh -o /usr/local/bin/skadon-pull
chmod 755 /usr/local/bin/skadon-pull
cat > /etc/systemd/system/skadon-pull.service <<'U'
[Unit]
Description=skadon.ru: выкладка сайта с GitHub
After=network-online.target
[Service]
Type=oneshot
ExecStart=/usr/local/bin/skadon-pull
U
cat > /etc/systemd/system/skadon-pull.timer <<'U'
[Unit]
Description=skadon.ru: проверка обновлений сайта раз в минуту
[Timer]
OnBootSec=30
OnUnitActiveSec=60
[Install]
WantedBy=timers.target
U
systemctl daemon-reload
systemctl enable --now skadon-pull.timer
/usr/local/bin/skadon-pull && echo "АВТОВЫКЛАДКА РАБОТАЕТ: $(cat /var/lib/skadon-deploy/deployed)"
