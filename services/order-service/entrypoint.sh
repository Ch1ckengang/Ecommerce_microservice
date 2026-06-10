#!/bin/sh
set -e

python - <<'PY'
import os
import time
import psycopg2

db_config = {
    "dbname": os.environ["DB_NAME"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "host": os.environ["DB_HOST"],
    "port": os.environ["DB_PORT"],
}

for attempt in range(30):
    try:
        connection = psycopg2.connect(**db_config)
        connection.close()
        print("PostgreSQL is ready.")
        break
    except psycopg2.OperationalError:
        print(f"Waiting for PostgreSQL... ({attempt + 1}/30)")
        time.sleep(2)
else:
    raise SystemExit("PostgreSQL did not become ready in time.")
PY

python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
