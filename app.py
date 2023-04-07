""" web app to allow users to anonymously recommend books """

import sqlite3
from better_profanity import profanity
from flask import Flask, flash, g, redirect, render_template, request, session, url_for

from key_file import key
from open_lib_api_calls import open_lib_search

# Configure app
app = Flask(__name__)
app.secret_key = key
# ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

""" sql 
test_table - 
work_key, cover_id, title, author, pub_date, num_of_pages, search_term, review, timestamp

functions for database taken pretty much exactly from flask docs
"""

DATABASE = 'books.db'

OPEN_LIB_URL = "https://openlibrary.org"


def get_db():
    """ establish connection to database, as per flask docs """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # row factory allows querying via dictionary calls 
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    """ close connection on exit of app as per flask docs """ 
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """ provides easy way to query database as per flask docs """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


""" Web pages """

@app.route("/")
def index():
    """ 
    homepage lists latest recommendations 
    """

    # query database for top 10 most recent book recs
    books = query_db('SELECT work_key, cover_id, title, author, pub_year, num_of_pages, review from "test_books" ORDER BY Timestamp DESC LIMIT 10')

    return render_template("index.html", books=books)


@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    """ 
    page for querying books api recommendations
    """
    if request.method == "POST":
        """ 
        use api to validate real book
        parse api return to get values you want to store
        example string https://openlibrary.org/api/books?bibkeys=ISBN:9781785039065&format=json
        """
        search_method = "open-library"
        
        search_term = request.form['search-term']

        if search_method == "open-library":
            results = open_lib_search(search_term)
            session['results'] = results
        # render submit with results
        if not results:
            error = "That search query returned no results, please try again."
            return render_template("recommend.html", error=error)
        else:
            return render_template("submit.html", results=results)
    # if get request
    else:
        return render_template("recommend.html")


@app.route("/submit", methods=["POST"])
def submit():
    """ validate recommendation and submit to database """
    if request.method == "POST":
        # get passed over book info
        results = session.get("results")

        try:
            # get form option turn to integer and adapt for index value
            option = int(request.form["select"])
            option = option - 1
            # get selected index
            result = (results[option])
        except KeyError:
            error = "You must select a book to submit!"
            return render_template("submit.html", results=results, error=error)
                
        # get review value
        if request.form["review-button"] == "no":
            review = "No review"
        else:
            review = request.form.get("review-box")
        
        # check review not blank
        if not review:
            error = "Your review is empty. Either write a review, or select no review."
            flash("Review selected as yes, but no review given.")
            return render_template("submit.html", results=results, error=error)
        # check review is not too longer
        if len(review) > 1000:
            error = "Your review is too long, try and be more concise."
            return render_template("submit.html", results=results, error=error)
        # check review does not contain profanity 
        if profanity.contains_profanity(review):
            error = "Your review contained profanity. Please be less rude and try again."
            return render_template("submit.html", results=results, error=error)
        
        # submit to datbase
        # establish cursor for processing
        cursor = get_db().cursor()

        """
        'work_key': work_key, 'title': title, 
        'pub_date': first_publish_date, 'num_of_pages': num_of_pages,
        'author': author, 'cover_id': cover_id, 
        'search_term': term}) 
        """
        cursor.execute('''INSERT into "test_books" (work_key, title, author, pub_year, num_of_pages, cover_id, search_term, review) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (result['work_key'], result['title'], result['author'], result['pub_date'], result['num_of_pages'], result['cover_id'],  result['search_term'], review))

        # commit changes to database
        db = get_db()
        db.commit()
        flash("Your recommendation has been received, thank you!")
        return redirect("/")
    else:
        return render_template("submit.html")


@app.route("/history")
def history():
    """ page for viewing recommendation history """
    
    # default view is all books 
    books = query_db('SELECT title, author, pub_year, review from "test_books" ORDER BY Timestamp DESC')
    
    # need to provide means for this to be filtered depending on user selection

    return render_template("history.html", books=books)


@app.route("/about")
def about():
    """ page for reading about how site was made """

    return render_template("about.html")


""" error handling """ 

@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html', error_message=e), 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error_message=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', error_message=e), 500


def validate_isbn(isbn):
    """ test for valid isbn """

    # remove white space and dashes
    isbn = isbn.replace("-", "")
    isbn = isbn.replace(" ", "")
    check = isbn.isdigit()
    if check:
        length = len(isbn)
        if length == 10 or length == 13:
            return True
    else:
        return False


if __name__ == "__main__":
    app.run(debug=True)
