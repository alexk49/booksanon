#!/bin/bash


deploy_db_container_local () {
        if [[ "$(docker ps -a | grep booksanon-db)" ]]; then 
                echo "removing existing container"
                docker stop "booksanon-db";
                docker rm "booksanon-db"
        fi;

        echo "deploying container locally"
        docker run --name booksanon-db \
                -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
                -e POSTGRES_DB=booksanon \
                -p 5432:5432 -v "$POSTGRES_VOLUME_PATH":/var/lib/postgresql/data \
                -d postgres
}

deploy_app_local () {
    echo "running app locally"
    source .venv/bin/activate
    uvicorn src.server.app:app --reload
}


deploy_huey_local () {
    echo "running huey"
    source .venv/bin/activate
    huey_consumer.py src.server.tasks.huey --workers=1 
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
            -h | --help)
                help
                exit
                ;;
        esac
        shift
done
