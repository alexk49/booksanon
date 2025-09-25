# BooksAnon

## About

BooksAnon is a web application for recommending books and looking for book recommendations.

Users can recommend a book without entering any personal data. This is a no strings attached book recommendation service and exists for people who just want to share something they've read with others.

The biblographical data is obtained via the [Open Library API](https://openlibrary.org/dev/docs/api/books).

## Set up

An .env file is required with the following values:

```
DEBUG=True
EMAIL_ADDRESS=  # email is required for requests to openlib
POSTGRES_USERNAME=
POSTGRES_PASSWORD=
POSTGRES_URL={localhost-or-url}:{port}/{username}
POSTGRES_VOLUME_PATH=/var/lib/postgres/data/{volume-name}
SECRET_KEY=
```

Docker must be installed:

https://docs.docker.com/engine/install/ubuntu/

Add user to docker usergroup (optional):

https://docs.docker.com/engine/install/linux-postinstall/

Set up virtual environment and install requirements:

```
python3 -m venv .venv
source .venv/bin/activate
pip install .  # project dependencies
pip install -e .[test,lint]  # install linters and pytest etc.
npm install  # only includes linters and jest
```

Once pip is installed the project cli will be available, run the help command for more info:

```
books --help
```

This allows you to test calls to the API, read/write from the database or start an interactive session as well as linting and testing.
