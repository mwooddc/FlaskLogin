from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from flask_login import login_required, current_user
from .forms import UserRatingForm, RatingCategoryForm, AddSchoolForm, TennisEventForm, MatchForm
from .models import db, User, UserRatings, RatingCategory, School, TennisEvent, Match
from .auth import role_required
from datetime import datetime


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
        # Clear the form data to prepare for the next input
        # form.ratee_id.data = None
        # form.rating_category.data = None
        # form.value.data = None
        flash('Rating submitted successfully!', 'success')
        # After clearing the form data, redirect to the same page
        return redirect(url_for('coach.submit_rating'))

    # Render the template with the form and user data
    return render_template('submit_rating.html', form=form, user=current_user)



@coach.route('/add-rating-category', methods=['GET', 'POST'])
@login_required
@role_required('Coach')
def add_rating_category():
    form = RatingCategoryForm()
    if form.validate_on_submit():
        category_description = form.category_description.data
        new_category = RatingCategory(CategoryDescription=category_description)
        db.session.add(new_category)
        db.session.commit()
        flash('Rating category added successfully!', 'success')
        return redirect(url_for('coach.add_rating_category'))
    return render_template('add_rating_category.html', form=form, user=current_user)



@coach.route('/add-school', methods=['GET', 'POST'])
@login_required
@role_required('Coach')
def add_school():
    form = AddSchoolForm()
    if form.validate_on_submit():
        school_name = form.school_name.data
        new_school = School(name=school_name)
        db.session.add(new_school)
        db.session.commit()
        flash('School added successfully!', 'success')
        return redirect(url_for('coach.add_school'))
    return render_template('add_school.html', form=form, user=current_user)






@coach.route('/create-event-and-matches', methods=['GET', 'POST'])
@login_required
@role_required('Coach')
def create_event_and_matches():
    event_form = TennisEventForm()
    match_form = MatchForm()

    if request.method == 'POST':
        print("Form Data:", request.form)
        # print("Won or Lost Value:", form_data.get('won_or_lost'))

    # Fetch schools data from the database
    schools = School.query.all()

    # Populate player choices
    player_choices = [(str(user.id), f'{user.Forename} {user.Surname}') for user in User.query.filter_by(Role='Player').all()]
    print("Player Choices:", player_choices)

    match_form.player1_name.choices = [('None', 'None')] + player_choices
    match_form.player2_name.choices = [('None', 'None')] + player_choices


    if request.method == 'POST' and match_form.validate():
        # Process form data for TennisEvent
        event_date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        new_event = TennisEvent(date=event_date,
                                home_venue_id=request.form['home_venue'],
                                away_venue_id=request.form['away_venue'])
        db.session.add(new_event)
        db.session.commit()

        form_data = dict(request.form)
        # print("DICTIONARY of form_data",  form_data)


        # Initialize a variable to keep track of player index
        player_index = 0


        while True:
            if player_index == 0:
                player1_name = form_data["player1_name"]
                player2_name = form_data["player2_name"]
                singles_or_doubles = form_data["singles_or_doubles"]
                sets_played = form_data["sets_played"]
                sets_won = form_data["sets_won"]
                won_or_lost = form_data["won_or_lost"]
                comment = form_data["comment"]
            else:
                player_key = f"player1_name_{player_index}"
                
                if player_key in form_data:
                    # Assign values to separate variables
                    player1_name = form_data.get(f'player1_name_{player_index}', "")
                    player2_name = form_data.get(f'player2_name_{player_index}', "")
                    singles_or_doubles = form_data.get(f"singles_or_doubles_{player_index}", "")
                    sets_played = form_data.get(f"sets_played_{player_index}", "")
                    sets_won = form_data.get(f"sets_won_{player_index}", "")
                    won_or_lost = form_data.get(f"won_or_lost_{player_index}", "")
                    comment = form_data.get(f"comment_{player_index}", "")

                else:
                    break
            new_match = Match(tennis_event_id=new_event.id,
                                        player1_id=player1_name,
                                        player2_id=player2_name,
                                        singles_or_doubles=singles_or_doubles,
                                        sets_played=sets_played,
                                        sets_won=sets_won,
                                        won_or_lost=won_or_lost,
                                        comment=comment)
            player_index += 1
            db.session.add(new_match)
        db.session.commit()
                    
            

        return redirect(url_for('coach.create_event_and_matches'))
    
    elif request.method == 'POST':
        # Form validation failed
        flash('There were errors in your form, please review them.', 'danger')

    return render_template('create_event_and_matches.html', event_form=event_form, match_form=match_form, user=current_user, schools=schools)
