""" web app to allow users to anonymously recommend books """

import sqlite3
import requests
from flask import Flask, g, redirect, render_template, request, session, url_for

from key_file import key

# Configure app
app = Flask(__name__)
app.secret_key = key
# ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

""" sql 
test_table - 
title, author, year of publication, review, timestamp

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
        search_via = request.form['search-via']
        search_term = request.form['search-term']

        print(search_method)
        print(search_via)
        print(search_term)

        if search_method == "open-library":
            if search_via == "isbn":
                valid = validate_isbn(search_term)
                if not valid:
                    return render_template("recommend.html")

            results = open_lib_search(search_via, search_term)
            # get biblographic data via open lib api
            # title, author, pub_date  = open_lib_isbn(isbn)                 
            
            # results = [{'title': title, 'author': author, 'pub_date': pub_date}]
            # results = [(title, author, pub_date, review)]
            session['results'] = results
            print(results)
            # return render_template("submit.html", results=results)
        # render submit with results
        return render_template("submit.html", results=results)
    else:
        return render_template("recommend.html")


@app.route("/submit", methods=["GET", "POST"])
def submit():
    """ validate recommendation and submit to database """
    if request.method == "POST":
        # get form option turn to integer and adapt for index value
        option = int(request.form["select"])
        option = (option - 1)
        # get passed over book info
        results = session.get("results")
        # get selected index
        result = (results[option])
        
        # get review value
        if request.form["review-button"] == "no":
            review = ""
        else:
            review = request.form.get("review-box")
        # submit to datbase
        # establish cursor for processing
        cursor = get_db().cursor() 
        cursor.execute('''INSERT into "test_books" (title, author, pub_year, review) VALUES (?, ?, ?, ?)''', (result['title'], result['author'], result['pub_date'], review))

        # commit changes to database
        db = get_db()
        db.commit()

        return redirect("/")
        # print(results)
        if request.method == "GET":
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
            author = respone_dict['name']

            authors = authors + ", " + author
        # reset numerous authors as one author value
        author = authors
    return(title, author, pub_date)


def open_lib_search(search_via, term):
    """ get data using general open library search api """
    url = "https://openlibrary.org/search.json"
    
    search_via_options = ['title', 'isbn']
    if search_via not in search_via_options: 
        search_via = "" 
    # create url query 
    search_url = url + "?" + search_via + "=" + term

    response = requests.get(search_url)
    response_dict = response.json()
    
    unique_works = []
    results = []

    # get top five unique results
    for num in range(len(response_dict['docs'])):
    
        if response_dict['docs'][num]['ebook_access'] == 'no_ebook':
            pass
        else:
            # add work key to unique works if not already there
            work_key = response_dict['docs'][num]['key']
            
            if work_key not in unique_works:
                unique_works.append(work_key)
                
                # get basic biblographic data
                title = response_dict['docs'][num]['title'] 
                num_of_pages = response_dict['docs'][num]['number_of_pages_median']
                
                                
                author = response_dict['docs'][num]['author_name']
                
                # handle multiple authors
                if len(author) == 1:
                    author = author[0]
                else:
                    author = ', '.join(author)
                
                # handle values that caused key errors on rarer books in testing 
                
                # librarything id can be added to url like:
                # https://www.librarything.com/work/1060
                try:
                    librarything_id = response_dict['docs'][num]['id_librarything']
                except KeyError:
                    librarything_id = "n/a"
                
                try:
                    first_publish_date = response_dict['docs'][num]['first_publish_year'] 
                except KeyError:
                    first_publish_date = "n/a"
 
                # cover id can be added to url like: 
                # https://covers.openlibrary.org/b/id/525391-S.jpg - change S to L or M for different sizes
                cover_id = response_dict['docs'][0]['cover_i']
                
                results.append({'work_key': work_key, 'title': title, 
                                'pub_date': first_publish_date, 'num_of_pages': num_of_pages,
                                'author': author, 'librarything_id': librarything_id, 
                                'cover_id': cover_id, 'searched_via': search_via,
                                'search_term': term}) 
                
                # enforce limit on number of results 
                if len(results) == 10:
                    break
    return results


if __name__ == "__main__":
    app.run(debug=True)
