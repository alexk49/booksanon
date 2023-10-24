""" web app to allow users to anonymously recommend books """

import json
import sqlite3
import logging
import logging.config
from os.path import exists, join

from better_profanity import profanity
from flask import (
    Flask,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
)

from config_dict import config_dict
from key_file import key
from open_lib_api_calls import open_lib_search


# Configure app
app = Flask(__name__)

# config logs
logging.config.dictConfig(config_dict)
# secret key is needed for session variable
app.secret_key = key
# ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


""" sql 
test_table - 
work_key, cover_id, title, author, pub_date, num_of_pages, search_term, review, timestamp

book table 
work_key, cover_id, title, author, pub_date, num_of_pages, search_term, review, timestamp
"""

"""
The render persistant storage requires a render disk.
This can't be stored in the root project directory.

Consequently, the local path that should be used for testing is:

DATABASE = "data/books.db"

The live database is hosted on the render server.

This uses the path:

DATABASE = "/opt/var/booksanon/data/books.db"

"""

# DATABASE = "data/books.db"
PRODUCTION_DATABASE = join("opt", "var", "booksanon", "data", "books.db")

if exists(PRODUCTION_DATABASE):
    DATABASE = PRODUCTION_DATABASE
else:
    # test db path
    TEST_DATABASE = join("data", "books.db")
    DATABASE = TEST_DATABASE


OPEN_LIB_URL = "https://openlibrary.org"


def get_db():
    """establish connection to database, as per flask docs"""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # row factory allows querying via dictionary calls
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    """close connection on exit of app as per flask docs"""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """provides easy way to query database as per flask docs"""
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
    books = query_db(
        'SELECT work_key, cover_id, title, author, pub_year, num_of_pages, review from "books" ORDER BY Timestamp DESC LIMIT 10'
    )

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

        # eventually provide way to search different ways
        search_method = "open_library"

        search_term = request.form["search-term"]
        logging.info("A user has made a search for: %s", search_term)

        # search for query
        if search_method == "open_library":
            results = open_lib_search(search_term)
            session["results"] = results
            logging.info("successful search")

        # if no results
        if not results:
            logging.info("Failed search")
            error = "That search query returned no results, please try again."
            return render_template("recommend.html", error=error)

        # send user to submit page with results of query passed on
        return render_template("submit.html", results=results)

    else:
        # if get request just teturn template
        return render_template("recommend.html")


@app.route("/submit", methods=["POST"])
def submit():
    """validate recommendation and submit to database"""
    if request.method == "POST":
        # get passed over book info
        results = session.get("results")

        try:
            # get form option turn to integer and adapt for index value
            option = int(request.form["select"])
            option = option - 1
            # get selected index
            result = results[option]
        except KeyError:
            error = "You must select a book to submit!"
            return render_template("submit.html", results=results, error=error)

        # get review value
        if request.form["review-button"] == "no":
            review = "No review"
            logging.info("No review given")
        else:
            review = request.form.get("review-box")

        # check review not blank
        if not review:
            logging.info("Submitted with empty review")
            error = "Your review is empty. Either write a review, or select no review."
            flash("Review selected as yes, but no review given.")
            return render_template("submit.html", results=results, error=error)
        # check review is not too longer
        if len(review) > 500:
            logging.info("Review rejected for exceeding character limit")
            error = "Your review is too long, try and be more concise."
            return render_template("submit.html", results=results, error=error)
        # check review does not contain profanity
        if profanity.contains_profanity(review):
            logging.info("Review rejected for containing profanity")
            error = (
                "Your review contained profanity. Please be less rude and try again."
            )
            return render_template("submit.html", results=results, error=error)

        # submit to datbase

        # establish cursor for processing
        cursor = get_db().cursor()

        cursor.execute(
            """INSERT into "books" (work_key, title, author, pub_year, num_of_pages, cover_id, search_term, review) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                result["work_key"],
                result["title"],
                result["author"],
                result["pub_date"],
                result["num_of_pages"],
                result["cover_id"],
                result["search_term"],
                review,
            ),
        )

        # commit changes to database
        db = get_db()
        db.commit()
        logging.info("Book submitted to database")
        logging.info(result)
        logging.info(review)
        flash("Your recommendation has been received, thank you!")
        return redirect("/")
    else:
        return render_template("recommend.html")


@app.route("/history", methods=["GET", "POST"])
def history():
    """page for viewing recommendation history"""
    # default view is top 10
    top_ten = query_db(
        'SELECT work_key, cover_id, title, author, pub_year, count(title) FROM "books" GROUP BY title ORDER by count(title) DESC LIMIT 10'
    )

    # need to provide means for this to be filtered depending on user selection
    filters = ["All Books", "Recommendations Ordered by Count", "Top Ten"]

    if request.method == "POST":
        selected_filter = request.form.get("filter")

        # check for valid filter
        if selected_filter not in filters:
            flash("Please select a valid filter")
            books = top_ten
            current_selection = "Top Ten"
            return render_template(
                "history.html",
                books=books,
                filters=filters,
                current_selection=current_selection,
            )

        # return selected filters
        if selected_filter == "All Books":
            current_selection = selected_filter
            all_books = query_db(
                'SELECT work_key, cover_id, title, author, pub_year, review from "books" ORDER BY Timestamp DESC'
            )
            books = all_books

        # all top recommendations
        if selected_filter == "Recommendations Ordered by Count":
            current_selection = selected_filter
            top_recs = query_db(
                'SELECT work_key, cover_id, title, author, pub_year, count(title) FROM "books" GROUP BY title ORDER by count(title) DESC'
            )
            books = top_recs
        # top ten
        if selected_filter == "Top Ten":
            current_selection = selected_filter
            books = top_ten

        return render_template(
            "history.html",
            books=books,
            filters=filters,
            current_selection=current_selection,
        )
    # if get request return default view
    else:
        current_selection = "Top Ten"
        books = top_ten
        return render_template(
            "history.html",
            books=books,
            filters=filters,
            current_selection=current_selection,
        )


@app.route("/search_history")
def search_history():
    return render_template("search_history.html")


@app.route("/search")
def search():
    """search query for history page"""
    q = request.args.get("q")
    if q:
        query = "%" + q + "%"
        books = query_db(
            'SELECT * FROM "books" WHERE (title LIKE (?)) OR (author LIKE (?)) OR (review LIKE (?)) LIMIT 50',
            (query, query, query),
        )
    else:
        books = []

    data = []

    for book in books:
        json_string = json.dumps(dict(book))
        data.append(json_string)
    return jsonify(data)


@app.route("/about")
def about():
    """page for reading about how site was made"""
    return render_template("about.html")


""" error handling """


@app.errorhandler(400)
def bad_request(e):
    logging.info(e)
    return render_template("400.html", error_message=e), 400


@app.errorhandler(404)
def page_not_found(e):
    logging.info(e)
    return render_template("404.html", error_message=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    logging.info(e)
    return render_template("500.html", error_message=e), 500


if __name__ == "__main__":
    app.run()
