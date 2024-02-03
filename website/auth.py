#The url_for library allows you to write url_for('name of the function')
#e.g. if I have a route called @qpp.route def xxx(): and I want to go to that route
#type  url_for('xxx') REMEMBER if using Blueprints nameoffile.function e.g. 
#url_for('views.xxx') You can use in templates too with jinja e.g. {{ url_for('views.xxx)}}
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from . import db
from .models import User
#wraps is required but the reasons why are complex (search if required)
from functools import wraps
#Great video to explain flask_login library: https://www.youtube.com/watch?v=2dEM-s3mRLE
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

#A Blueprint simply allows you to create seperate files from the standard app.py
#file to hold routes (without blueprint all routes would be in one file)
#see this video for explanation: https://www.youtube.com/watch?v=pjVhrIJFUEs
#To use a Blueprint you have to import Blueprint from flask (see above)
#You then assign that blueprint to a variable and then use that 
#as the @route in this code (see line 15)
auth = Blueprint("auth", __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Email = request.form.get("Email")
        Password = request.form.get("Password")

        user = User.query.filter_by(Email=Email).first()
        if user:
            if check_password_hash(user.Password, Password):
                flash("Logged in!", category='success')
                # Logs in the User whos Email and hashed Password match
                #(see variable above User =   on line 26)
                login_user(user, remember=True)
                # Store the user's role in the session
                session['role'] = user.Role
                #redirect to views.home where the User is passed as an object
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user = current_user)


@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    Email = ""
    Username = ""
    Forename = ""
    Surname = ""
    Role = None

    if request.method == 'POST':
        Email = request.form.get("Email")
        Username = request.form.get("Username")
        Password1 = request.form.get("Password1")
        Password2 = request.form.get("Password2")
        Forename = request.form.get("Forename")
        Surname = request.form.get("Surname")
        #are these requests getting the id, name or value from the signup form?
        Role = request.form.get("Role")

        Email_exists = User.query.filter_by(Email=Email).first()
        Username_exists = User.query.filter_by(Username=Username).first()

        if Email_exists:
            flash('Email is already in use.', category='error')
        elif Username_exists:
            flash('Username is already in use.', category='error')
        elif Password1 != Password2:
            flash('Password don\'t match!', category='error')
        elif len(Username) < 2:
            flash('Username is too short.', category='error')
        elif len(Password1) < 6:
            flash('Password is too short.', category='error')
        elif len(Email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_User = User(Email=Email, Username=Username, Password=generate_password_hash(
                Password1, method='scrypt'), Forename=Forename, Surname=Surname, Role=Role)
            db.session.add(new_User)
            db.session.commit()
            login_user(new_User, remember=True)
            flash('User created!')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user, 
                           email=Email, username=Username, 
                           forename=Forename, surname=Surname, role=Role)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))


#This is me building my own decorator so that above each route for a
#Player or a Coach you can use @role_required('Player') or @role_required('Coach')
#and only those routes will be accessible to someone in that role
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.Role != role:
                flash('You do not have the necessary permissions to access this page.', 'error')
                return redirect(url_for('views.home'))  # Redirect to a different page
            return f(*args, **kwargs)
        return decorated_function
    return decorator
