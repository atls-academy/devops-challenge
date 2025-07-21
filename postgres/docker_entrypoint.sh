#!/bin/bash
set -e

echo "Custom entrypoint: configuring Postgres..."

# Пример: устанавливаем listen_addresses
echo "listen_addresses = '*'" >> /var/lib/postgresql/data/postgresql.conf

# Запускаем Postgres от имени пользователя postgres
exec su postgres -c "/usr/local/bin/docker-entrypoint.sh postgres"
