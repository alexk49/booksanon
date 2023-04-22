# Books Anon

## About 
Books Anon is a web app made in flask, where users can recommend a book to database without entering any of their own personal data. This is a no strings attached book recommendation and exists for people who just want to share something they've read with others. 

The biblographical data is obtained via the [Open Library API](https://openlibrary.org/dev/docs/api/books). Every submitted book recommendation is then stored in an sqlite3 database.

I've tried to use standard libraries where possible. I deliberately did not use any css frameworks for this, as I wanted to actually practise vanilla css - I might revist this particular one in the future. I have used standard python library for sqlite3. The external libraries used are:
* [flask](https://github.com/pallets/flask) - to make the whole application work
* [better-profanity](https://github.com/snguyenthanh/better_profanity) - to ensure user reviews don't contain bad language
* [requests](https://github.com/psf/requests) - to get the biblographical data from the Open Library API

## About Me
This was made as my "final project" for the [CS50](https://cs50.harvard.edu/x/2023/) course. Prior to CS50 I had a bit of experience with html and xml, and had the [Jose Portilla python udemy course](https://www.udemy.com/course/complete-python-bootcamp/), as well as a few of my own [small projects](https://github.com/alex-k-9). Mainly straight forward utility scripts. Basically, I am new to this, and will welcome any comments or suggested improvements to the code. 

## Testing
The app has been hosted on [Render](https://render.com/). Because of the way Render handles persistant storage, you must swap the database file path for local testing. This different options are noted in app.py. 
