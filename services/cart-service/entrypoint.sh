#!/bin/sh
set -e

python - <<'PY'
import os
import time
import pymysql

for attempt in range(30):
    try:
        connection = pymysql.connect(
            host=os.environ["DB_HOST"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            port=int(os.environ["DB_PORT"]),
        )
        connection.close()
        print("MySQL is ready.")
        break
    except pymysql.MySQLError:
        print(f"Waiting for MySQL... ({attempt + 1}/30)")
        time.sleep(2)
else:
    raise SystemExit("MySQL did not become ready in time.")
PY

python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
