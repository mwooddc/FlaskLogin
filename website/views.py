from flask import Blueprint, render_template, session
from flask_login import login_required, current_user

#A Blueprint simply allows you to create seperate files from the standard app.py
#file to hold routes (without blueprint all routes would be in one file)
#see this video for explanation: https://www.youtube.com/watch?v=pjVhrIJFUEs
#To use a Blueprint you have to import Blueprint from flask (see above)
#You then assign that blueprint to a variable and then use that 
#as the @route in this code (see lines 13 and 14)
views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    # Check the user's role and pass it to the template
    role = session.get('role', 'Player')  # Default to 'Player' if not set

    #here the user variable stores the current user which if it exists i.e.
    # you are logged in, is an object containing the users record
    # we can then inside home.html use jinja to access the users fields
    #e.g. id, username, email {{ current_user.username }}
    if current_user.is_authenticated and current_user.Role == 'Player':
        return render_template("playerdash.html", user=current_user)
    elif current_user.is_authenticated and current_user.Role == 'Coach':
        return render_template("coachdash.html", user=current_user)
