from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import login_required, current_user
from .forms import UserRatingForm
from .models import db, User, UserRatings
from .auth import role_required


#A Blueprint simply allows you to create seperate files from the standard app.py
#file to hold routes (without blueprint all routes would be in one file)
#see this video for explanation: https://www.youtube.com/watch?v=pjVhrIJFUEs
#To use a Blueprint you have to import Blueprint from flask (see above)
#You then assign that blueprint to a variable and then use that 
#as the @route in this code (see lines 13 and 14)
coach = Blueprint("coach", __name__)


# @views.route("/")
@coach.route("/coach")
@login_required
@role_required('Coach')
def mates():
    # Check the user's role and pass it to the template
    role = session.get('role', 'Coach')  # Default to 'Player' if not set

    #here the user variable stores the current user which if it exists i.e.
    # you are logged in, is an object containing the users record
    # we can then inside home.html use jinja to access the users fields
    #e.g. id, username, email {{ current_user.username }}
    return render_template("coach.html", user=current_user)


@coach.route('/submit-rating', methods=['GET', 'POST'])
@login_required
@role_required('Coach')
def submit_rating():
    form = UserRatingForm()

    rater_id = current_user.id

    if form.validate_on_submit():
        # Create a new UserRatings object and assign form data to its attributes
        new_rating = UserRatings(
            Raterid=rater_id,
            Rateeid=form.ratee_id.data,
            RatingCategory=form.rating_category.data,
            Value=form.value.data
        )
        db.session.add(new_rating)
        db.session.commit()
        return redirect(url_for('coach.success'))

    return render_template('coach.html', form=form, user=current_user)


@coach.route('/success')
@login_required
@role_required('Coach')
def success():
    return "Rating submitted successfully!"
