""" web app to allow users to anonymously recommend books """

import sqlite3
import requests
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
        # rows = [(request.form.get("title"), request.form.get("author"), request.form.get("pub_year"), request.form.get("review"))]

        # validate data 
        """ to do:
            use api to validate real book
            parse api return to get values you want to store
            
            example string https://openlibrary.org/api/books?bibkeys=ISBN:9781785039065&format=json
        """
        search_method = request.form['search-method']

        if search_method == "open-library":
            print(search_method)
            isbn = request.form.get("isbn")
            # test isbn = 978-0747579885 
            valid = validate_isbn(isbn)
            if valid:
                
                # get biblographic data via open lib api 
                title, author, pub_date  = open_lib_isbn(isbn)                 
                review = request.form['review-button']
                
                if review == 'no':
                    review = ""

                rows = [(title, author, pub_date, review)]
                
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


def validate_isbn(isbn):
    """ test for valid isbn """
    isbn = isbn.replace("-", "")
    check = isbn.isdigit()
    if check:
        length = len(isbn)
        if length == 10 or length == 13:
            return True
    else:
        return False


def open_lib_isbn(isbn):
    """ get data back from open library api via isbn """
    # add isbn into url
    url = f"https://openlibrary.org/isbn/{isbn}.json"
    
    # get response as json
    response = requests.get(url)
    response_dict = response.json()

    # get title and edition pub date
    title = response_dict['title']
    pub_date = response_dict['publish_date']
    
    # authors goes via different page
    authors = response_dict['authors']

    if len(authors) == 1:
        author_key = authors[0]['key']
        author_url = "https://openlibrary.org" + author_key + ".json"
        
        response = requests.get(author_url)
        response_dict = response.json()
        author = response_dict['name']
    else:
        authors = ""

        for count, author in enumerate(authors):
            author_key = authors[count]['authors']

            author_url = "https://openlibrary.org" + author_key + ".json"
            
            response = requests.get(author_url)
            response_dict = response.json()
            author = respons_dict['name']

            authors = authors + ", " + author
        # reset numerous authors as one author value         
        author = authors
    
    return(title, author, pub_date)
