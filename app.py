import os
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

# bson.object ObjectId - render MongoDB docs by unique id

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
    tasks = list(mongo.db.tasks.find())
    return render_template("tasks.html", tasks=tasks)


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

        # put the new user into 'session variable' (cookie)
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    # render register.html
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match - redirect user back to login page
                flash("Incorrect Username and/or password")
                return redirect(url_for("login"))

        else:
            # username does not exist
            flash("Incorrect Username and/or password")
            return redirect(url_for("login"))
        # redirect user to login page to try again

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("you have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# START of CRUD FUNCTIONALITY

@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        # insert our form into the mongo db
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        task = {
            "category": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"),
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }
        mongo.db.tasks.insert_one(task)
        flash("Task succesfully added")
        return redirect(url_for("get_tasks"))

    # connect data from Mongo DB categories collection
    # to dynamically generate options
    categories = mongo.db.categories.find().sort(
        "category_name", 1)
    return render_template("add_task.html", categories=categories)


# edit tasks
@app.route("/edit_task/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if request.method == "POST":
        # insert our form into the mongo db
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        submit = {
            "category": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"),
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }
        mongo.db.tasks.update({"_id": ObjectId(task_id)}, submit)
        flash("Task succesfully updated")

    # ObjectID function returns db record of task_id which gets passed to it
    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})

    # grab data from Mongo DB categories collection to generate options
    categories = mongo.db.categories.find().sort(
        "category_name", 1)
    return render_template("edit_task.html", task=task, categories=categories)


# delete tasks
@app.route("/delete_task/<task_id>")
def delete_task(task_id):
    mongo.db.tasks.remove({"_id": ObjectId(task_id)})
    flash("Task Successfully Deleted")
    return redirect(url_for("get_tasks"))


# get categories
@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


# add category
@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


# edit category
@app.route("/edit_catgeory/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name")
        }
        # param 1 = id of category to be looked up and edited
        # param 2 = updated category input by the user
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category successfully updated")
        return redirect(url_for("get_categories"))
    # return Mongo db BSON object for category_id passed from Jinja
    # store it in category variable
    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


# tell application how and where to run
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
