#!/bin/sh

set -e
FILE=/app/bctf/media/start.ok

echo "Waiting for database"
while ! mysqladmin ping -h db --silent; do
  >&2 echo -n "."
  sleep 1
done
echo "Database ready for connections."


if [ -f "$FILE" ]; then
    echo "$FILE exist"
else 
    touch $FILE	
    echo "Migrating Database"
    python manage.py migrate
    python manage.py flush --noinput
fi

echo "Starting bCTF."
exec gunicorn --chdir /app/ \
    bctf.wsgi \
    --workers=4 \
    --bind 0.0.0.0:8000