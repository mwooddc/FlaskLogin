from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from .models import User
from .auth import role_required
from collections import defaultdict
from sqlalchemy import or_
from datetime import datetime
from .forms import generate_survey_form
from sqlalchemy.exc import SQLAlchemyError
from .models import db, UserRatings, RatingCategory, Notification, TennisEvent, Match, School


#A Blueprint simply allows you to create seperate files from the standard app.py
#file to hold routes (without blueprint all routes would be in one file)
#see this video for explanation: https://www.youtube.com/watch?v=pjVhrIJFUEs
#To use a Blueprint you have to import Blueprint from flask (see above)
#You then assign that blueprint to a variable and then use that 
#as the @route in this code (see lines 13 and 14)
player = Blueprint("player", __name__)

# CONSTANTS
CoachID = 1
HomeVenueID = 1

############# HANDLING NOTIFICATIONS FOR PLAYERS DASHBOARD ###################

# Function: Get a users notifications
def get_user_notifications(user_id):
    notifications = Notification.query.filter_by(receiver_id=user_id, is_read=False).order_by(Notification.timestamp.desc()).limit(5).all()

    # Return a list of dictionaries with more details
    detailed_notifications = [{
        'id': notification.id,
        'comment': notification.comment,
        'match_id': notification.match_id,
        'sender_id': notification.sender_id,  # Include sender_id if you want to show who sent the notification
        'sender_name': f"{notification.sender.Forename} {notification.sender.Surname}",  # Access sender's name via relationship
        'is_read': notification.is_read,
        'timestamp': notification.timestamp
    } for notification in notifications]
    return detailed_notifications

# Route: Mark the Notifications as read
@player.route('/mark-notification-read/<int:notification_id>', methods=['POST'])
@login_required
@role_required('Player')
def mark_notification_read(notification_id):
    notification = Notification.query.get(notification_id)
    if notification and notification.receiver_id == current_user.id:  # Check that the notification exists and belongs to the current user
        notification.is_read = True
        db.session.commit()
        return jsonify({"success": True}), 200
    return jsonify({"error": "Notification not found or access denied"}), 404

# Route: Reply to a Notification
# This route can not be the same name as the route in the coach.py
@player.route('/reply_to_notification', methods=['POST'])
@login_required
@role_required('Player')
def reply_to_notification():
    original_notification_id = request.form.get('original_notification_id')
    receiver_id = request.form.get('receiver_id')
    reply_message = request.form.get('reply_message')

    # Mark the original notification as read
    original_notification = Notification.query.get(original_notification_id)
    if original_notification:
        original_notification.is_read = True

    # Create the reply notification
    reply_notification = Notification(
        receiver_id=receiver_id,
        sender_id=current_user.id,  # Assuming you have access to the currently logged-in user's ID
        comment=reply_message,
        is_read=False
    )
    db.session.add(reply_notification)
    db.session.commit()

    return redirect(url_for('player.playerdashboard'))  # Redirect to the notifications page or wherever appropriate

############# HANDLING NOTIFICATIONS #########################################
############# FINISHED #######################################################



############# HANDLING INITIAL SURVEY ########################################

# Route: When submitting the intiail survey
@player.route('/submit_survey', methods=['POST'])
@login_required
@role_required('Player')
def submit_survey():
    form = generate_survey_form()()
    if form.validate_on_submit():
        user_id = current_user.id
        # Check if the survey is already completed to avoid duplicate entries
        survey_already_completed = User.query.get(user_id).survey_completed
        if not survey_already_completed:
            for category in RatingCategory.query.all():
                field_name = f'rating_{category.CategoryCode}'
                rating_value = getattr(form, field_name).data
                new_rating = UserRatings(Raterid=user_id, Rateeid=user_id, RatingCategory=category.CategoryCode, Value=rating_value)
                db.session.add(new_rating)
            # Mark the survey as completed for the user
            current_user.survey_completed = True
            db.session.commit()
            flash('Thank you for completing the survey!', 'success')
        else:
            flash('You have already completed the survey.', 'info')
        return redirect(url_for('player.playerdashboard'))
    else:
        flash('There was an error with your submission. Please ensure all fields are filled out correctly.', 'error')
        return redirect(url_for('player.submit_survey'))


############# HANDLING INITIAL SURVEY FINISHED ###############################
##############################################################################


################## USERS UPCOMING FIXTURES ###################################

# Function: Get THIS PLAYERS (logged in user) upcoming fixtures
def get_user_upcoming_fixtures():
    user_id = current_user.id

    fixtures_query = db.session.query(
        TennisEvent.date.label('date'),
        TennisEvent.id,
        TennisEvent.home_venue_id,
        TennisEvent.away_venue_id,
        db.func.count(Match.id).label('number_of_matches'),
        db.case(
            (TennisEvent.home_venue_id == HomeVenueID, 'Home'),
            else_='Away'
        ).label('home_or_away')
    ).join(
        Match, Match.tennis_event_id == TennisEvent.id
    ).filter(
        TennisEvent.date >= datetime.now(),
        or_(Match.player1_id == user_id, Match.player2_id == user_id)
    ).group_by(
        TennisEvent.id
    ).all()

    fixtures = [
        {
            'id': fixture.id,
            'date': fixture.date,
            'number_of_matches': fixture.number_of_matches,
            'home_or_away': fixture.home_or_away,
            'opponent_name': '',  # Placeholder, to be filled in later
            'home_venue_id': fixture.home_venue_id,
            'away_venue_id': fixture.away_venue_id
        }
        for fixture in fixtures_query
    ]

    return add_opponent_name_to_fixtures(fixtures)

# Function: Get the name of a school opponent
def get_opponent_name(home_away, home_venue_id, away_venue_id):
    opponent_id = away_venue_id if home_away == 'Home' else home_venue_id
    opponent = School.query.filter_by(id=opponent_id).first()
    return opponent.name if opponent else None

# Function: Use the function above to then present the name of the opponent
def add_opponent_name_to_fixtures(fixtures):
    for fixture in fixtures:
        fixture['opponent_name'] = get_opponent_name(
            fixture['home_or_away'],
            fixture['home_venue_id'],
            fixture['away_venue_id']
        )
    return fixtures

################## USERS UPCOMING FIXTURES ###################################
############# FINISHED #######################################################



############## GRAPH FOR PLAYER AND COACH RATINGS COMPARISON #################

# Function: to create data structure with data for graph of both
# Coach (Latest Rating) and Player (Initial Rating)
def player_and_coach_ratings():
    # Get the current player's ID
    player_id = current_user.id
    
    # Retrieve self-assessed ratings for the player
    self_assessed_ratings = {}
    self_assessed_query = UserRatings.query.filter(
        UserRatings.Rateeid == player_id,
        UserRatings.Raterid != CoachID  # Exclude coach ratings
    )
    for rating in self_assessed_query:
        category_description = RatingCategory.query.get(rating.RatingCategory).CategoryDescription
        self_assessed_ratings[category_description] = rating.Value
    
    # Retrieve coach ratings for the player (latest rating for each category)
    coach_ratings = {}
    for rating in RatingCategory.query.all():
        latest_coach_rating = UserRatings.query.filter(
            UserRatings.Rateeid == player_id,
            UserRatings.Raterid == CoachID,
            UserRatings.RatingCategory == rating.CategoryCode
        ).order_by(UserRatings.date_created.desc()).first()
        
        if latest_coach_rating:
            category_description = rating.CategoryDescription
            coach_ratings[category_description] = latest_coach_rating.Value

    return self_assessed_ratings, coach_ratings

############## GRAPH FOR PLAYER AND COACH RATINGS COMPARISON #################
############# FINISHED #######################################################



#######################  ROUTE FOR THE PLAYER DASHBOARD  #####################

# Route: This is the main route for the Player dashboard
@player.route('/playerdashboard')
@login_required
@role_required('Player')
def playerdashboard():

    user_upcoming_fixtures = get_user_upcoming_fixtures()

    user = User.query.get(current_user.id)
    survey_completed = user.survey_completed

    # Show the form if not completed
    form = generate_survey_form()() if not survey_completed else None

    user_notifications = get_user_notifications(current_user.id)

    # Query to fetch the ratings, their categories, and dates for the current user
    ratings_query = db.session.query(UserRatings.Value, UserRatings.date_created, RatingCategory.CategoryDescription)\
        .join(RatingCategory)\
        .filter(UserRatings.Rateeid == current_user.id)\
        .filter(UserRatings.Raterid == CoachID)\
        .order_by(UserRatings.date_created.asc()).all()
    
    # Iterate over the ratings query and remove any repeating categories, keep only the latest
    # This is so we can plot in a table the LATEST ratings for a player
    # Create a dictionary to store the latest datetime for each unique value
    latest_datetime = {}

    # Iterate over the data and update the latest datetime for each unique value
    for value, dt, category in ratings_query:
        latest_datetime[category] = max(latest_datetime.get(category, datetime.min), dt)

    # Filter the data to keep only the tuples with the latest datetime for each unique value
    filtered_data = [(value, dt, category) for value, dt, category in ratings_query if latest_datetime[category] == dt]

    # Organize data for plotting
    data_for_plot = defaultdict(lambda: defaultdict(list))
    for value, date_created, category_description in ratings_query:
        data_for_plot[category_description]['dates'].append(date_created.strftime('%Y-%m-%d'))  # Format date as string
        data_for_plot[category_description]['values'].append(value)

    # Prepare data for Chart.js
    categories = list(data_for_plot.keys())
    datasets = []
    for category, details in data_for_plot.items():
        datasets.append({
            'Category': category,
            'Value': details['values'],
            'Date': details['dates'],  # use this to ensure all datasets have the same x-axis labels
        })

    # Determine all unique dates
    unique_dates = sorted(set(date for entry in datasets for date in entry['Date']))

    # Adjust values for each category
    players_rating_data = []
    for entry in datasets:
        category = entry['Category']
        values = entry['Value']
        dates = entry['Date']

        # Create a dictionary to store values by date
        date_values = {date: value for date, value in zip(dates, values)}

        # Update values for each unique date
        adjusted_values = []
        last_value = None
        for date in unique_dates:
            if date in date_values:
                last_value = date_values[date]
                adjusted_values.append(last_value)
            else:
                adjusted_values.append(last_value or 0)  # Repeat last value if available, otherwise use 0

        # Append to the final data structure
        players_rating_data.append({'Category': category, 'Value': adjusted_values, 'Date': unique_dates})

    player_ratings, coach_ratings = player_and_coach_ratings()

    return render_template('playerdash.html', player_ratings=player_ratings, coach_ratings=coach_ratings, survey_completed=survey_completed, user_upcoming_fixtures=user_upcoming_fixtures, form=form, ratings_query=ratings_query, filtered_data=filtered_data, datasets=datasets, players_rating_data=players_rating_data, categories=categories, user_notifications=user_notifications, user=current_user)

#######################  ROUTE FOR THE PLAYER DASHBOARD  #####################
############# FINISHED #######################################################



######################  VIEWING UPCOMING FIXTURES  ###########################

@player.route('/player_edit_fixture/<int:fixture_id>', methods=['GET', 'POST'])
@login_required
@role_required('Player')
def edit_fixture(fixture_id):
    # Fetch the fixture and its related matches
    fixture = TennisEvent.query.get_or_404(fixture_id)
    matches = Match.query.filter_by(tennis_event_id=fixture_id).all()

    # Fetch the schools participating in the fixture
    home_school = School.query.get_or_404(fixture.home_venue_id)
    away_school = School.query.get_or_404(fixture.away_venue_id)

    if request.method == 'POST':
        try:
            # Iterate over each match to update its details
            for match in matches:
                player1_id = request.form.get(f'match_{match.id}_player1_id')
                player2_id = request.form.get(f'match_{match.id}_player2_id')
                singles_or_doubles = request.form.get(f'match_{match.id}_type')
                sets_played = request.form.get(f'match_{match.id}_sets_played')
                sets_won = request.form.get(f'match_{match.id}_sets_won')
                won_or_lost = request.form.get(f'match_{match.id}_won_lost')
                comment = request.form.get(f'match_{match.id}_comment')

                # Update match details
                match.player1_id = int(player1_id) if player1_id else match.player1_id
                match.player2_id = int(player2_id) if player2_id else match.player2_id
                match.singles_or_doubles = singles_or_doubles if singles_or_doubles else match.singles_or_doubles
                match.sets_played = int(sets_played) if sets_played else match.sets_played
                match.sets_won = int(sets_won) if sets_won else match.sets_won
                match.won_or_lost = won_or_lost if won_or_lost else match.won_or_lost
                match.comment = comment if comment else match.comment

            db.session.commit()
            flash('Fixture updated successfully!', 'success')
            return redirect(url_for('edit_fixture', fixture_id=fixture_id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred while updating the fixture.', 'error')

    return render_template('view_fixture.html', fixture=fixture, matches=matches, home_school=home_school, away_school=away_school, user=current_user)

######################  VIEWING UPCOMING FIXTURES  ###########################
############# FINISHED #######################################################


