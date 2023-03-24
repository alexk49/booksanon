import sqlite3
from flask import Flask, g, redirect, render_template, request, session

# Configure app 
app = Flask(__name__)

# ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

""" sql 
test_table - 
title, author, year of publication, review, timestamp

functions taken pretty much exactly from flask docs

"""

DATABASE = 'books.db'

""" establish connection to database, as per flask docs """
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # row factory allows querying via dictionary calls 
        db.row_factory = sqlite3.Row
    return db


""" close connection on exit of app as per flask docs """ 
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


""" provides easy way to query database as per flask docs """
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


""" Web pages """

@app.route("/")
def index():
    """ 
    homepage, used for recommendations 
    and for listing latest 
    """
    
    # query database for top 10 most recent book recs 
    books = query_db('SELECT title, author, pub_year, review from "test_books" ORDER BY Timestamp DESC LIMIT 10')

    return render_template("index.html", books=books)

@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    """ 
    page for submitting recommendations
    """
    if request.method == "POST":
        # get data from form 
        rows = [(request.form.get("title"), request.form.get("author"), request.form.get("pub_year"), request.form.get("review"))]

        # validate data 
        """ 
        to do:
            use api to validate real book
            parse api return to get values you want to store
        """

        # establish cursor for processing 
        cursor = get_db().cursor()
        
        cursor.executemany('''INSERT into "test_books" (title, author, pub_year, review) VALUES (?, ?, ?, ?)''', rows)
        
        # commit changes to database 
        db = get_db()
        db.commit()

        # redirect to homepage
        return redirect("/")

    else: 
        return render_template("recommend.html")


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
