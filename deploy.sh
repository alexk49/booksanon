#!/bin/bash

set -e

DB_CONTAINER_NAME="booksanon-db"
APP_CONTAINER_NAME="booksanon-app"

remove_existing_container_by_name() {
    container_name="$1"

    echo "searching for existing $container_name"

    if docker ps -a --format '{{.Names}}' | grep -Eq "^${container_name}\$"; then
        echo "Removing existing container: $container_name"
        docker rm -f "$container_name"
    fi
}

deploy_db_container_local () {
    remove_existing_container_by_name "$DB_CONTAINER_NAME"
    echo "deploying container locally"
    docker run --name "$DB_CONTAINER_NAME" \
            --env POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
            --env POSTGRES_DB=booksanon-db \
            --publish 5432:5432 --volume "$POSTGRES_VOLUME_PATH":/var/lib/postgresql/data \
            --detach postgres
}

deploy_app_local () {
    echo "running app locally"
    source .venv/bin/activate
    uvicorn src.server.app:app --reload --log-level info --access-log
}


deploy_huey_local () {
    echo "running huey"
    source .venv/bin/activate
    huey_consumer.py src.server.tasks.huey --workers=1 
}

deploy_app () {
    # docker compose up --build -d app --remove-orphans --force-recreate
    remove_existing_container_by_name "$DB_CONTAINER_NAME"
   
    echo "starting up $DB_CONTAINER_NAME"
    docker run --name "$DB_CONTAINER_NAME" \
            --env-file .env \
            --publish "$DB_PORT":5432 \
            --volume "$POSTGRES_VOLUME_PATH":/var/lib/postgresql/data \
            --detach postgres

    echo "waiting for db to init"
    sleep 2

    remove_existing_container_by_name "$APP_CONTAINER_NAME"

    echo "starting up $APP_CONTAINER_NAME"

    docker run --name "$APP_CONTAINER_NAME" \
            --env-file .env \
            --publish "$PORT:8000" \
            --link "$DB_CONTAINER_NAME":db \
            --volume ./data:/data  \
            --volume ./logs:/logs  \
            --detach booksanon
}


help () {

cat << _EOF_

Run deployments.

-h
print help

-dbl | --db-local 
run local postgres container with mounted volume

-l | --local
run web app locally

-hl | --huey-local)
run huey task runner locally

-p | --production)

deploy production app

_EOF_
}


if [ "$#" -ne 1 ]; then
    echo "no args passed, usage:"
    help
    exit
fi


if [[ -f ".env" ]]; then
        echo "sourcing .env file"
        export $(grep -v '^#' .env | xargs)
else
        echo "no .env file found, exiting"
        exit
fi


while [[ -n "$1" ]]; do
        case "$1" in
            -dbl | --db-local)
                deploy_db_container_local
                exit
                ;;
            -hl | --huey-local)
                deploy_huey_local
                exit
                ;;
            -l | --local)
                deploy_app_local
                exit
                ;;
            -p | --production)
                deploy_app
                exit
                ;;
            -h | --help)
                help
                exit
                ;;
        esac
        shift
done
