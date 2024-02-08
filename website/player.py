from flask import Blueprint, render_template, session
from flask_login import login_required, current_user
from .auth import role_required

from .models import db, UserRatings, RatingCategory  # Adjust the import as per your project structure


#A Blueprint simply allows you to create seperate files from the standard app.py
#file to hold routes (without blueprint all routes would be in one file)
#see this video for explanation: https://www.youtube.com/watch?v=pjVhrIJFUEs
#To use a Blueprint you have to import Blueprint from flask (see above)
#You then assign that blueprint to a variable and then use that 
#as the @route in this code (see lines 13 and 14)
player = Blueprint("player", __name__)


# @views.route("/")
@player.route("/player")
@login_required
@role_required('Player')
def mates():
    # Check the user's role and pass it to the template
    role = session.get('role', 'Player')  # Default to 'Player' if not set

    #here the user variable stores the current user which if it exists i.e.
    # you are logged in, is an object containing the users record
    # we can then inside home.html use jinja to access the users fields
    #e.g. id, username, email {{ current_user.username }}
    return render_template("player.html", user=current_user)


@player.route('/playerdashboard')
@login_required
@role_required('Player')
def playerdashboard():
    role = session.get('role', 'Player')  # Default to 'Player' if not set
    # Query to fetch the ratings and their categories for the current user
    ratings = db.session.query(UserRatings, RatingCategory).join(RatingCategory).filter(UserRatings.id == current_user.id).all()
    return render_template('playerdash.html', ratings=ratings, user=current_user)