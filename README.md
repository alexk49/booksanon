# BooksAnon

## About
BooksAnon is a web app made in flask, where users can recommend a book to a database without entering any of their own personal data. This is a no strings attached book recommendation and exists for people who just want to share something they've read with others.

The biblographical data is obtained via the [Open Library API](https://openlibrary.org/dev/docs/api/books). Every submitted book recommendation is then stored in an sqlite3 database.

I've tried to use standard libraries where possible. I deliberately did not use any css frameworks for this, as I wanted to actually practise vanilla css - I might revisit this particular one in the future. I have used the standard python library for sqlite3. The external libraries used are:

* [flask](https://github.com/pallets/flask) - to make the whole application actually work
* [better-profanity](https://github.com/snguyenthanh/better_profanity) - to ensure user reviews don't contain bad language
* [requests](https://github.com/psf/requests) - to get the biblographical data from the Open Library API

## Testing
The app has been hosted on [Render](https://render.com/). Because of the way Render handles persistant storage, app.py is configured to use the local test database found in the /data folder when not on the production environment.

All tests have so far been written using the standard python library unittest module. These can be run using the supplied makefile or run with:

```
python -m unittest discover -v
```
