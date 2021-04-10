set -o errexit
set -o pipefail

cmd=( "$@" )

waitformigration() {
    # check that existing migration in files was apply in DB
    python manage.py checkmigrations
}

migrate() {
    python manage.py migrate --noinput
}

postgres_ready() {
    python << END
import sys
import psycopg2
try:
    psycopg2.connect(
        dbname="${DB_NAME}",
        user="${DB_USERNAME}",
        password="${DB_PASSWORD}",
        host="${DB_HOSTNAME}",
        port="${DB_PORT}")
except psycopg2.OperationalError as e:
    sys.exit(-1)
sys.exit(0)
END
}

if [ -f config/env.sh ]; then
    source config/env.sh
fi

counter=0
until postgres_ready; do
  >&2 echo 'PostgreSQL is unavailable (sleeping)...'
  sleep 1
  counter=$(($counter + 1))
  if [ $counter -gt "300" ]; then
    echo "Can't connect to PostgreSQL. Exiting."
    exit 1
  fi
done

>&2 echo 'PostgreSQL is up - continuing...'

case "$cmd" in
    wait_for_migration)
        # check that existing migration in files was apply in DB
        counter=0
        until waitformigration; do
        >&2 echo 'Django migrations was not applied (sleeping)...'
        sleep 5
        if [ $counter -gt "60" ]; then
            echo "Waiting too long to apply Django migration. Exiting."
            exit 1
        fi
        counter=$(expr $counter + 1)
        done
        >&2 echo 'Django migrations was checked - continuing...'
    ;;
    migrate)
        migrate
    ;;
    *)
        ${cmd[@]}  # usage start.sh
    ;;
esac
