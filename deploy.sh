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
                -p 5432:5432 -v data:/var/lib/postgresql/data \
                -d postgres
}

help () {

cat << _EOF_

Run deployments.

-h
print help

-dbl | --db-local 
run local postgres container with mounted volume

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
            -h | --help)
                help
                exit
                ;;
        esac
        shift
done
