from app import app, db
from flask import redirect, render_template, request, session, url_for
from app.models import user, storage, history
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from datetime import datetime
import pytz

from app.helpers import login_required

# Defining Brazil timezone for later functions
brazil_hour = pytz.timezone('Brazil/East') 

# Routes:
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login_page():
    """User Login"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Getting Username, password and confirmation. And validate:
        error = False # When error found, error == True
        success = False
        username = request.form.get("username")
        password = request.form.get("password")

        # Blank Input / No values received
        if not username or not password:
            error = True
            error_message = "You can\'t leave blank inputs!"
            return render_template("login.html", error=error, error_message=error_message)
        # Validating user
        else:
            # User exist?
            if user.query.filter_by(username=username).first()  == None:
                error = True
                error_message = "Username doesn't exist"
                return render_template("login.html", error=error, error_message=error_message)
            else:
                # User's id
                user_id = user.query.filter_by(username=username).first().id
                # Checking password
                if not check_password_hash(user.query.all()[user_id - 1].password_hash, password):
                    error = True
                    error_message = "Wrong Password"
                    return render_template("login.html", error=error, error_message=error_message)
                else:
                    # User is valid -> Login the user
                    # Remember which user has logged in
                    session["user_id"] = user_id
                    return redirect("storage")
    else:
        return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register_page():
    """"Register"""

    if request.method == "POST":
        # Getting Username, password and confirmation. And validate:
        error = False # When error found, error == True
        success = False
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Blank Input / No values received
        if not username or not password  or not confirmation :
            error = True
            error_message = "You can\'t leave blank inputs!"
            return render_template("register.html", error=error, error_message=error_message)

        # If passwords are not the same
        if password != confirmation:
            error = True
            error_message = "Passwords are not equal"
            return render_template("register.html", error=error, error_message=error_message)
        else:
            # Checking if the username already exists in the database
            if user.query.filter_by(username=username).first()  != None:
                error = True
                error_message = "Username already exists"
                return render_template("register.html", error=error, error_message=error_message)
            else:
                # Updating database with new user
                hash = generate_password_hash(password)
                new_user = user(username=username, password_hash=hash)
                db.session.add(new_user)   
                db.session.commit()
                success_message = 'Your account was created successfully'
                success = True
                return render_template("login.html", success_message=success_message, success=success)
    else:
        return render_template('register.html')

@app.route('/storage', methods=["GET", "POST"])
@login_required
def storage_page():
    """""Storage interface"""
    
    # When user add/remove items
    if request.method == "POST":
        # The user did ADD or REMOVE
        if request.form["modal_button"] == 'add':
            print("add!")
        elif request.form["modal_button"] == 'remove':
            print("remove!")
        return redirect('storage')

    # Getting Username
    user_id = user.query.filter_by(id=session.get("user_id")).first().id
    username = user.query.all()[user_id - 1].username
    # Showing user's owned items
    user_storage = storage.query.filter_by(owner=session.get("user_id")).all()
    # Checking if the user have any items at all:
    if not user_storage:
        empty = True
        return render_template('storage.html', empty=empty, username=username)
    else:
        empty = False
        return render_template('storage.html', user_storage=user_storage, username=username, empty=empty)

@app.route('/newitem', methods=["GET", "POST"])
@login_required
def newitem_page():
    """Adding a new item"""
    if request.method == 'POST':
        # Getting user's id
        user_id = user.query.filter_by(id=session.get("user_id")).first().id
        # Gettting live hours
        time = datetime.now(brazil_hour)
        formated_time = time.strftime("%d/%m/%y - %H:%M")
        # Adding item to 'item' table and 'history' table
        new_item = storage(owner=user_id, item=request.form.get('new_item'), quantity=request.form.get('modalnew_quantity'))
        new_item_history = history(owner=user_id, item=request.form.get('new_item'), type='add', quantity=request.form.get('modalnew_quantity'),
                                                    price=request.form.get('modalnew_price'), time=formated_time)
        db.session.add(new_item)   
        db.session.add(new_item_history)   
        db.session.commit()
        return redirect(url_for('storage_page'))
    else:
        return redirect(url_for('storage_page'))

@app.route('/history')
@login_required
def history_page():
    """Last updates of user"""

    # Getting Username
    user_id = user.query.filter_by(id=session.get("user_id")).first().id
    username = user.query.all()[user_id - 1].username
    # Getting User's history
    user_history = history.query.filter_by(owner=session.get("user_id")).all()
    # Checking if the user has any items
    if not user_history:
        empty = True
        return render_template('storage.html', empty=empty, username=username)
    else:
        empty = False
        return render_template("history.html", user_history=user_history, empty=empty, username=username)

@app.route('/logout')
def logout_page():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")