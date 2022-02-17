from email import message
from app import app, db
from flask import redirect, render_template, request
from app.models import user, storage
from werkzeug.security import check_password_hash, generate_password_hash


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login_page():
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
                user_id = user.query.filter_by(username=username).first().id - 1
                # Checking password
                if not check_password_hash(user.query.all()[user_id].password_hash, password):
                    error = True
                    error_message = "Wrong Password"
                    return render_template("login.html", error=error, error_message=error_message)
                else:
                    # User is valid -> Login the user
                    login_user(user.query.get(username).first())
                    return render_template("storage.html")
    else:
        return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register_page():
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

@app.route('/storage')
def storage_page():
    return render_template('storage.html')

@app.route('/logout')
def logout_page():
    logout_user()
    return redirect('/home')