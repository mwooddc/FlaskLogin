from flask import Blueprint, render_template, session, flash, redirect, url_for, request, get_flashed_messages
from flask_login import login_required, current_user
from .forms import UserRatingForm, RatingCategoryForm, AddSchoolForm, TennisEventForm, MatchForm
from .models import db, User, UserRatings, RatingCategory, School, TennisEvent, Match, Notification
from .auth import role_required
from datetime import datetime
from flask import jsonify
import re


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


def determine_number_of_matches(request):
    # Example: Parsing field names to find the highest index
    max_index = 0
    for key in request.keys():
        if key.startswith('player1_name_'):
            index = int(key.split('_')[-1])  # Extract the numeric part of the field name
            max_index = max(max_index, index) + 1
    return max_index



@coach.route('/create-event-and-matches', methods=['GET', 'POST'])
@login_required
@role_required('Coach')
def create_event_and_matches():
    schools = School.query.all()
    #to get the players as a list of tuples:
    # player_choices = [(str(user.id), f'{user.Forename} {user.Surname}') for user in User.query.filter_by(Role='Player').all()]
    #to get the players as a list of dictionaries:
    player_choices = [
    {"user_id": str(user.id), "user_name": f"{user.Forename} {user.Surname}"}
    for user in User.query.filter_by(Role='Player').all()] or []
    print("Player Choices:", player_choices)

    # Convert players list to a dictionary {user_id: user_name}
    players_dict = {player['user_id']: player['user_name'] for player in player_choices}
    print("PlayerDictionary:", players_dict)

    if request.method == 'POST':
        
        raw_data = request.form.to_dict(flat=False)
        print(raw_data)
        event = []
        print("Event",event)

        # Populate player choices

        # Initialize the parsed data with keys that should have their values as integers
        event = {
            'date': raw_data['date'][0],
            'home_venue': int(raw_data['home_venue'][0]),
            'away_venue': int(raw_data['away_venue'][0]),
            'matches': []
        }

        # Define keys within matches that need their values converted to integers
        integer_keys = ['player1_name', 'player2_name', 'sets_played', 'sets_won']

        # Parse the match data
        for key, value in raw_data.items():
            if key.startswith('match'):
                # Extract the match index and attribute name
                parts = key.split('[')
                match_index = int(parts[1].split(']')[0])
                attribute_name = parts[2].split(']')[0]

                # Ensure the matches list is long enough
                while len(event['matches']) <= match_index:
                    event['matches'].append({})

                # Convert to integer if in integer_keys, otherwise assign directly
                if attribute_name in integer_keys:
                    event['matches'][match_index][attribute_name] = int(value[0])
                else:
                    event['matches'][match_index][attribute_name] = value[0]

        print("Event Updated",event)

        errors = []

        # Loop through each match in the "matches" list with updated error message
        for i, match in enumerate(event['matches']):
            if match['sets_won'] > match['sets_played']:
                # Append the customized error message including the match number (i+1 for human-readable numbering)
                errors.append(f"Error in Match {i+1}: Sets won can not exceed sets played")

        print("NEW ERRORS",errors)

        if errors:
            for e in errors:
                flash(e)

            # for key, error_list in errors.items():
            #     error_messages = ', '.join(error_list)  # Join all errors in the list into a single string
            #     flash(f"Match {key + 1} has these errors: {error_messages}")

            return render_template('create_event_and_matches.html', errors=errors, user=current_user, event=event, schools=schools, players=players_dict)
        else:
            # return "All users added successfully", 200
            # Convert the date from string to datetime object
            event_date = datetime.strptime(event['date'], "%Y-%m-%d")

            # Create a TennisEvent instance
            tennis_event = TennisEvent(
                date=event_date,
                home_venue_id=event['home_venue'],
                away_venue_id=event['away_venue']
            )

            # Add to session and commit to database
            db.session.add(tennis_event)
            db.session.commit()

            for match_data in event['matches']:
                match = Match(
                    tennis_event_id=tennis_event.id,
                    player1_id=match_data['player1_name'],  # Assuming player IDs are directly usable
                    player2_id=match_data['player2_name'],
                    singles_or_doubles=match_data['singles_or_doubles'],
                    sets_played=match_data['sets_played'],
                    sets_won=match_data['sets_won'],
                    won_or_lost=match_data['won_or_lost'],
                    comment=match_data['comment']
                )
                db.session.add(match)

                db.session.commit()

                # Create notifications for each player if there's a comment
                if match_data['comment'].strip():  # Check if comment is not just whitespace
                    for player_id in [match.player1_id, match.player2_id]:
                        # Ensure player_id is valid and not None before creating a notification
                        if player_id and player_id != current_user.id:  # Ensure the player is not the sender
                            notification = Notification(
                                receiver_id=player_id,
                                sender_id=current_user.id,  # Current logged-in user as the sender
                                match_id=match.id,
                                comment=match_data['comment'],
                                is_read=False
                            )                        

                            db.session.add(notification)



            # Commit all matches to the database
            db.session.commit()

            flash('matches added successfully!')
            return redirect(url_for('coach.create_event_and_matches'))  # Redirect back to the form
            # return render_template('create_event_and_matches.html', errors=errors, user=current_user, event=event, schools=schools)

    return render_template('create_event_and_matches.html', user=current_user, schools=schools, players=players_dict)
