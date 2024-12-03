from xxlimited_35 import error

from flask import Flask, render_template, url_for, session, flash,g
from markupsafe import escape
from flask import request
from werkzeug.utils import redirect


import sqlite3

app = Flask(__name__)

mail = None

app.secret_key = os.environ['KEY']
## --------- DATABASE ------


DATABASE = 'my_database.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def get_connection():
    return sqlite3.connect('my_database.db')

def validate(mail, password):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT password FROM users WHERE mail = ?', (mail,))
        passwordr = cursor.fetchone()
        # print(passwordr)
        if passwordr is None:
            flash("User Dont exist","error")
            return False
        return passwordr[0] == password
    except sqlite3.Error as e:
        print(f"An error occurred during validation: {e}")
        return False

def register(mail, password, name, age):
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT mail FROM users WHERE mail = ?', (mail,))
        if cursor.fetchone():
            flash("EMAIL ALREADY REGISTERED", "error")
            return False

        cursor.execute('''
            INSERT INTO users (mail, name, age, password) VALUES (?, ?, ?, ?)
        ''', (mail, name, age, password))
        db.commit()
        return True
    except sqlite3.Error as e:
        print(f"An error occurred during registration: {e}")
        return False
################### ____----------------------------------


def do_login():
    global mail
    mail = request.form["mail"]
    password = request.form["password"]
    #validation
    if validate(mail,password):
        session[mail] = mail
        return redirect(url_for('contents'))

    flash("Invalid username or password. Please try again.", "error")
    return redirect(url_for('login'))

def show_login():
    return render_template("login.html")


@app.route('/login',methods = ["POST","GET"])
def login():

    if request.method == 'POST':
        return do_login()
    else:
        return show_login()


def do_register():
    name = request.form["name"]
    mail = request.form["mail"]
    age = request.form["age"]
    phn = request.form["phn"]
    gender = request.form["gender"]
    password = request.form["password"]
    msg = register(mail, password, name, age)
    if not msg:
        # flash("Mail already registered","error")
        return redirect(url_for("signup"))
    return render_template("signup_sucess.html")


def show_register():
    return render_template("signup.html")


@app.route('/register',methods = ["POST","GET"])
def signup():
    if request.method == 'POST':
        return do_register()
    else:
        return show_register()

@app.route("/content")
def contents():
    if mail in session:
        return render_template("content.html")
    else:
        return redirect(url_for('login'))

@app.route("/logout")
def logout():
    global mail
    session.pop(mail, None)
    mail = None
    return redirect(url_for('login'))
@app.route('/')
def index():
    return redirect(url_for('login'))
if __name__ == "__main__":
    app.run()



