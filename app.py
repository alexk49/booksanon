from flask import Flask, redirect, render_template, request, session

# Configure app 
app = Flask(__name__)

# ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def index():
    """ homepage, used for recommendations 
        and for listing latest """

    return render_template("index.html")
