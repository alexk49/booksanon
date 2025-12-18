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
    deploy_db_container
}

deploy_db_container () {
    # Make sure to have set in .env:
    # POSTGRES_USER      - defaults to 'postgres'
    # POSTGRES_PASSWORD  - required
    # POSTGRES_DB
    # POSTGRES_VOLUME_NAME - optional but useful for named volume
    docker run --name "$DB_CONTAINER_NAME" \
            --env-file .env \
            --publish "$DB_PORT:$DB_PORT" \
            --volume "$POSTGRES_VOLUME_NAME":/var/lib/postgresql/data \
            --detach postgres
}

deploy_app_local () {
    echo "running app locally"
    source .venv/bin/activate
    uvicorn src.server.app:app --reload --log-level info --access-log
}

deploy_app_container () {
    docker build -t booksanon .

    docker run --name "$APP_CONTAINER_NAME" \
            --env-file .env \
            --publish "$PORT:$PORT" \
            --link "$DB_CONTAINER_NAME":db \
            --volume ./data:/home/app/data  \
            --volume ./logs:/home/app/logs  \
            --detach booksanon
}

deploy_huey_local () {
    echo "running huey"
    source .venv/bin/activate
    huey_consumer.py src.server.tasks.huey --workers=1 
}

deploy_full_app () {
    remove_existing_container_by_name "$DB_CONTAINER_NAME"
   
    echo "starting up $DB_CONTAINER_NAME"
    deploy_db_container

    echo "waiting for db to init"
    sleep 2

    remove_existing_container_by_name "$APP_CONTAINER_NAME"

    echo "starting up $APP_CONTAINER_NAME"
    deploy_app_container
}

restart_app_only () {
    remove_existing_container_by_name "$APP_CONTAINER_NAME"

    echo "starting up $APP_CONTAINER_NAME"
    deploy_app_container
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

-ra | --restart-app
restart web app only

-f | --full)
restart and deploy db and app containers

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
            -f | --full)
                deploy_full_app
                exit
                ;;
            -ra | --restart-app)
                restart_app_only
                exit
                ;;
            -h | --help)
                help
                exit
                ;;
        esac
        shift
done
