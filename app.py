import sqlite3
from flask import Flask, redirect, render_template, request, session

# Configure app 
app = Flask(__name__)

# ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

""" sql 
test_table - 
title, author, year of publication, review, timestamp

"""

DATABASE = 'books.db'

""" Web pages """

@app.route("/")
def index():
    """ 
    homepage, used for recommendations 
    and for listing latest 
    """

    return render_template("index.html")

@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    """ 
    page for submitting recommendations
    """
    if request.method == "POST":
        # get data from form 
       
        rows = [(request.form.get("title"), request.form.get("author"), request.form.get("pub_year"), request.form.get("review"))]

        # validate data 

        # add data to database 
        con = sqlite3.connect(DATABASE)
        # establish cursor for processing 
        cursor = con.cursor()
        
        cursor.executemany('''INSERT into "test_books" (title, author, pub_year, review) VALUES (?, ?, ?, ?)''', rows)
        
        # commit changes to database and close 
        con.commit()
        con.close() 

        # redirect to homepage
        return redirect("/")

    else: 
        return render_template("recommend.html")


@app.route("/history")
def history():
    """ page for viewing recommendation history """

    return render_template("history.html")


@app.route("/about")
def about():
    """ page for reading about how site was made """

    return render_template("about.html")


