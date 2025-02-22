import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db, lists, userlogic

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    login_check = userlogic.check_user(username, password)

    if not login_check:
        return render_template("message.html", message="VIRHE: väärä salasana tai tunnus")
    else:
        session["username"] = username
        session["user_id"] = login_check
        return redirect("/")
        

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return render_template("message.html", message="VIRHE: salasanat eivät ole samat")

    new_user = userlogic.create_new_user(username, password1)

    if new_user:
        return render_template("message.html", message="Tunnus luotu")
    else:
        return render_template("message.html", message="VIRHE: tunnus on jo varattu")

@app.route("/main")
def main():
    users_lists = lists.get_users_lists(session["username"], session["user_id"])
    return render_template("main.html", users_lists=users_lists)

@app.route("/newlist")
def newlist():
    return render_template("newlist.html")

@app.route("/createlist", methods=["POST"])
def createlist():
    new_list_name = request.form["listname"]
    lists.create_new_list(new_list_name,session["user_id"])
    return redirect("/main")

@app.route("/list/<int:list_id>", methods=["GET", "POST"])
def handle_lists(list_id):
    if request.method == "GET":
        items = lists.get_items(list_id)
        return render_template("list.html", items=items, list_id=list_id)
    if request.method == "POST":
        new_item = request.form["new_item"]
        lists.add_item_to_list(new_item, list_id, session["user_id"])
        return redirect("/list/"+str(list_id))

@app.route("/remove_item/<int:item_id>", methods=["POST"])
def remove_item(item_id):
    referer_list_id = request.form["list_id"]
    lists.remove_item(item_id)
    return redirect("/list/"+str(referer_list_id))

@app.route("/remove_list/<int:list_id>", methods=["POST"])
def remove_list(list_id):
    lists.remove_list(list_id)
    return redirect("/main")

@app.route("/haku", methods=["GET", "POST"])
def search_lists():
    if request.method == "GET":
        return render_template("search.html")
    if request.method == "POST":
        search_word = request.form["search_word"]
        list_of_lists = lists.search_lists(session["user_id"],search_word)
        return render_template("search.html", results=list_of_lists)