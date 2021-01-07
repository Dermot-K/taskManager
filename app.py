import os
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


# create an instance of Flask (stored in variable named "app")
app = Flask(__name__)

# app configurations
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

# instantiate PyMongo using constructor - app passed to this
mongo = PyMongo(app)


@app.route("/")
@app.route("/get_tasks")
def get_tasks():
    # declare var to hold data from our mongo.db tasks collection
    mongo_tasks = mongo.db.tasks.find()
    return render_template("tasks.html", tasks=mongo_tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            # get username from the form field name="username"
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            # redirect to the registration page
            return redirect(url_for("register"))

        # else if no existing user
        # create dictionary variable which will be insterted into the db
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")

    # render register.html
    return render_template("register.html")


# tell application how and where to run
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
