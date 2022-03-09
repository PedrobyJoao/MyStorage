from app import app, db
from flask import redirect, render_template, request, session, url_for
from app.models import user, storage, history
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from sqlalchemy import asc, desc
from datetime import datetime
import pytz
import json

from app.helpers import login_required, is_integer, usd

# Defining Brazil timezone for later functions
brazil_hour = pytz.timezone('Brazil/East') 

# Custom USD interface
app.jinja_env.filters["usd"] = usd

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
        # Initiating error booleans
        error = False # When error found, error == True
        success = False
        # Getting Username and passwordAnd validate:
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
                error_message = "Username doesn't exist!"
                return render_template("login.html", error=error, error_message=error_message)
            else:
                # User's id
                user_id = user.query.filter_by(username=username).first().id
                # Checking password
                if not check_password_hash(user.query.all()[user_id - 1].password_hash, password):
                    error = True
                    error_message = "Wrong Password!"
                    return render_template("login.html", error=error, error_message=error_message)
                else:
                    # Checking captcha
                    if not request.form.get("captcha"):
                        error = True
                        error_message = "Robots are not allowed here for now!"
                        return render_template("login.html", error=error, error_message=error_message)
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
        # Initiating error booleans
        error = False # When error found, error == True
        success = False
        # Getting Username, password and confirmation. And validate:
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
            error_message = "Passwords are not equal!"
            return render_template("register.html", error=error, error_message=error_message)
        else:
            # Checking if the username already exists in the database
            if user.query.filter_by(username=username).first()  != None:
                error = True
                error_message = "Username already exists!"
                return render_template("register.html", error=error, error_message=error_message)
            else:
                # Checking captcha
                if not request.form.get("captcha_register"):
                    error = True
                    error_message = "Robots are not allowed here (for now)!"
                    return render_template("register.html", error=error, error_message=error_message)
                # Checking if the password has more than 6 chars
                if len(password) < 6:
                    error = True
                    error_message = "Your password must be longer than 6 characters!"
                    return render_template("register.html", error=error, error_message=error_message)
                # Updating database with new user
                hash = generate_password_hash(password)
                new_user = user(username=username, password_hash=hash)
                db.session.add(new_user)   
                db.session.commit()
                success = True
                return render_template("login.html", success=success)
    else:
        return render_template('register.html')

@app.route('/storage', methods=["GET", "POST"])
@login_required
def storage_page():
    """""Storage interface"""
    
    # Getting user's ID
    user_id = session.get("user_id")

    # When user add/remove items
    if request.method == "POST":
        # Getting item and quantity input
        item = request.form.get("modal_item")
        quantity = int(request.form.get("modal_quantity"))
        price = request.form.get("modal_price")
        # If the user let price blank, price will be 0
        if price == '':
            price = 0;
        # Checking if quantity is integer
        if is_integer(quantity) == False:
            message = "Quantity must be integer!"
            return render_template("error.html", message=message)
        # Getting how many items the user has before the update
        old_quantity = storage.query.filter_by(owner=user_id, item=item).first().quantity

        # The user added/removed?
        if request.form["modal_button"] == 'add':
            new_quantity = quantity + old_quantity
        elif request.form["modal_button"] == 'remove':
            new_quantity = old_quantity - quantity
            # Checking if the user has sufficient quantity to remove
            if (quantity > old_quantity):
                message = "You don't have sufficient quantity to remove!"
                return render_template("error.html", message=message)

        # Gettting live hours
        time = datetime.now(brazil_hour)
        formated_date = time.strftime("%d/%m/%y")
        formated_time = time.strftime("%H:%M")

        # Creating an object to add data to storage table
        add_itemstorage = storage.query.filter_by(owner=user_id, item=item).first()
        # If the new quantity is equal 0, so we must take out the item row from storage page
        if new_quantity == 0:
            storage.query.filter_by(owner=user_id, item=item).delete()
        else:
            add_itemstorage.quantity = new_quantity
        # Adding data to history table (no need to create a object, we are not updating a row, instead we are adding it)
        add_itemhistory = history(item=item, type=request.form["modal_button"], quantity=quantity,
                                                    price=price, date=formated_date, time=formated_time, owner=user_id) 
        db.session.add(add_itemhistory)   
        db.session.commit()

    """Showing Storage"""

    # Getting Username
    username = user.query.all()[user_id - 1].username
    # Showing user's owned items
    user_storage = storage.query.filter_by(owner=user_id).all()

    # Dictionary to store item averages
    item_avgs = {}
    storage_items = []
    # Calculating item's average price
    for item in user_storage:
        item_tobeavg = history.query.filter_by(owner=user_id, item=item.item).all()
        denominator = 0
        numerator = 0
        for item_his in item_tobeavg:
            # Getting numerator and denominator for weighted average
            numerator += (item_his.price * item_his.quantity)
            denominator += item_his.quantity
        # Getting the average for the specific item
        average = numerator / denominator
        average = float("{:.2f}".format(average))
        item_avgs[item.item.lower()] = average
        storage_items.append(item.item)
    
    # Getting just the items
      
    # Checking if the user have any items at all:
    if not user_storage:
        empty = True
        return render_template('storage.html', empty=empty, username=username)
    else:
        empty = False
        return render_template('storage.html', user_storage=user_storage, username=username, empty=empty, 
                                                item_avgs=item_avgs, storage_items=json.dumps(storage_items))

@app.route('/newitem', methods=["GET", "POST"])
@login_required
def newitem_page():
    """Adding a new item"""
    if request.method == 'POST':
        # Getting user's id, item, quantity
        user_id = session.get("user_id")
        item = request.form.get("new_item")
        quantity = request.form.get('modalnew_quantity')
        # Gettting live date and hours
        time = datetime.now(brazil_hour)
        formated_date = time.strftime("%d/%m/%y")
        formated_time = time.strftime("%H:%M")
        # Adding item to 'item' table and 'history' table
        new_item = storage(owner=user_id, item=item, quantity=quantity)
        new_item_history = history(owner=user_id, item=item, type='add', quantity=quantity,
                                                    price=request.form.get('modalnew_price'), date=formated_date, time=formated_time)
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
    user_id = session.get("user_id")
    username = user.query.all()[user_id - 1].username
    # Getting User's history
    user_history = history.query.filter_by(owner=user_id).order_by(desc(history.date), desc(history.time)).all()
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