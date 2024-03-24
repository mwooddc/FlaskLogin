from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from .models import User
from .auth import role_required
from collections import defaultdict
# from collections import defaultdict
# from sqlalchemy.sql import func
from sqlalchemy import or_
from datetime import datetime
from .forms import generate_survey_form
from .models import db, UserRatings, RatingCategory, Notification, TennisEvent, Match, School  # Adjust the import as per your project structure


#A Blueprint simply allows you to create seperate files from the standard app.py
#file to hold routes (without blueprint all routes would be in one file)
#see this video for explanation: https://www.youtube.com/watch?v=pjVhrIJFUEs
#To use a Blueprint you have to import Blueprint from flask (see above)
#You then assign that blueprint to a variable and then use that 
#as the @route in this code (see lines 13 and 14)
player = Blueprint("player", __name__)


############# HANDLING NOTIFICATIONS ##############################################################

def get_user_notifications(user_id):
    notifications = Notification.query.filter_by(receiver_id=user_id, is_read=False).order_by(Notification.timestamp.desc()).limit(5).all()
    # # Option 1: Return a list of comments/messages
    # comments = [notification.comment for notification in notifications]
    # return comments

    # Option 2: Return a list of dictionaries with more details
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



############# HANDLING NOTIFICATIONS FINISHED #####################################################
###################################################################################################



############# HANDLING INITIAL SURVEY #####################################################
###################################################################################################

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
        # If the form doesn't validate, you may want to flash an error and redirect back to the survey
        # or render the form again with error messages.
        flash('There was an error with your submission. Please ensure all fields are filled out correctly.', 'error')
        return redirect(url_for('player.submit_survey'))  # Assuming 'player.survey' is the route where your survey form is located


############# HANDLING INITIAL SURVEY FINISHED #####################################################
###################################################################################################


######################## GETTING the USERS UPCOMING FIXTURES ###################################
    #################################################################################


def get_opponent_name(home_away, home_venue_id, away_venue_id):
    opponent_id = away_venue_id if home_away == 'Home' else home_venue_id
    opponent = School.query.filter_by(id=opponent_id).first()
    return opponent.name if opponent else None

def add_opponent_name_to_fixtures(fixtures):
    for fixture in fixtures:
        fixture['opponent_name'] = get_opponent_name(
            fixture['home_or_away'],
            fixture['home_venue_id'],
            fixture['away_venue_id']
        )
    return fixtures


def get_user_upcoming_fixtures():
    # Assuming current_user is the logged-in user, provided by Flask-Login
    user_id = current_user.id

    fixtures_query = db.session.query(
        TennisEvent.date.label('date'),
        TennisEvent.home_venue_id,
        TennisEvent.away_venue_id,
        db.func.count(Match.id).label('number_of_matches'),
        db.case(
            (TennisEvent.home_venue_id == 1, 'Home'),
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


######################## GETTING the USERS UPCOMING FIXTURES ###################################
    ############################# FINISHED #######################################






def player_and_coach_ratings():
    # Get the current player's ID
    player_id = current_user.id
    coach_id = 1
    
    # Retrieve self-assessed ratings for the player
    self_assessed_ratings = {}
    self_assessed_query = UserRatings.query.filter(
        UserRatings.Rateeid == player_id,
        UserRatings.Raterid != coach_id  # Exclude coach ratings
    )
    for rating in self_assessed_query:
        category_description = RatingCategory.query.get(rating.RatingCategory).CategoryDescription
        self_assessed_ratings[category_description] = rating.Value
    
    # Retrieve coach ratings for the player (latest rating for each category)
    coach_ratings = {}
    for rating in RatingCategory.query.all():
        latest_coach_rating = UserRatings.query.filter(
            UserRatings.Rateeid == player_id,
            UserRatings.Raterid == coach_id,
            UserRatings.RatingCategory == rating.CategoryCode
        ).order_by(UserRatings.date_created.desc()).first()
        
        if latest_coach_rating:
            category_description = rating.CategoryDescription
            coach_ratings[category_description] = latest_coach_rating.Value

    print("SELLLLLF", self_assessed_ratings)
    print("CCCOOOACCCH", coach_ratings)

    return self_assessed_ratings, coach_ratings




















@player.route('/playerdashboard')
@login_required
@role_required('Player')
def playerdashboard():
    CoachID = 1 #This is the coachesID
    role = session.get('role', 'Player')  # Default to 'Player' if not set

    user_upcoming_fixtures = get_user_upcoming_fixtures()

    user = User.query.get(current_user.id)
    survey_completed = user.survey_completed

    # Conditional form generation based on survey completion
    form = generate_survey_form()() if not survey_completed else None


    user_notifications = get_user_notifications(current_user.id)

    # Query to fetch the ratings, their categories, and dates for the current user
    ratings_query = db.session.query(UserRatings.Value, UserRatings.date_created, RatingCategory.CategoryDescription)\
        .join(RatingCategory)\
        .filter(UserRatings.Rateeid == current_user.id)\
        .filter(UserRatings.Raterid == CoachID)\
        .order_by(UserRatings.date_created.asc()).all()
    
    #Iterate over the ratings query and remove any repeating categories, keep only the latest
    #This is so we can plot in a table the LATEST ratings for a player
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
            # Add more customization for each line here (e.g., backgroundColor, borderColor)
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
    print("PPPPPPPPPPPPPPPPPPPPPPPP", player_ratings)
    print("CCCCCCCCCCCCCCCCCCCCC", coach_ratings)




    return render_template('playerdash.html', player_ratings=player_ratings, coach_ratings=coach_ratings, survey_completed=survey_completed, user_upcoming_fixtures=user_upcoming_fixtures, form=form, ratings_query=ratings_query, filtered_data=filtered_data, datasets=datasets, players_rating_data=players_rating_data, categories=categories, user_notifications=user_notifications, user=current_user)
