from flask import Blueprint, render_template, session, flash, redirect, url_for, request, get_flashed_messages
from flask_login import login_required, current_user
from .forms import UserRatingForm, RatingCategoryForm, AddSchoolForm, TennisEventForm, MatchForm
from .models import db, User, UserRatings, RatingCategory, School, TennisEvent, Match, Notification
from .auth import role_required
from datetime import datetime
from flask import jsonify
import re
from sqlalchemy import func, case, or_, desc


#A Blueprint simply allows you to create seperate files from the standard app.py
#file to hold routes (without blueprint all routes would be in one file)
#see this video for explanation: https://www.youtube.com/watch?v=pjVhrIJFUEs
#To use a Blueprint you have to import Blueprint from flask (see above)
#You then assign that blueprint to a variable and then use that 
#as the @route in this code (see lines 13 and 14)
coach = Blueprint("coach", __name__)


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




@coach.route('/mark-notifications-read/<int:notification_id>', methods=['POST'])
@login_required
@role_required('Coach')
def mark_notifications_read(notification_id):
    notification = Notification.query.get(notification_id)
    if notification and notification.receiver_id == current_user.id:  # Check that the notification exists and belongs to the current user
        notification.is_read = True
        db.session.commit()
        return jsonify({"success": True}), 200
    return jsonify({"error": "Notification not found or access denied"}), 404



#This route can not be the same name as the route in the player.py
@coach.route('/reply_to_notifications', methods=['POST'])
@login_required
@role_required('Coach')
def reply_to_notifications():
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

    return redirect(url_for('coach.coachdashboard'))  # Redirect to the notifications page or wherever appropriate



############# HANDLING NOTIFICATIONS FINISHED #####################################################
###################################################################################################




############# Upcoming Fixtures #####################################################
#####################################################################################



# Assuming `db` is your SQLAlchemy instance and session
def get_upcoming_fixtures():
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
        or_(TennisEvent.home_venue_id == 1, TennisEvent.away_venue_id == 1)
    ).group_by(TennisEvent.id).all()

    return [
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


# `fixtures` will be a list of tuples with the structure (date, home_or_away, opponent, number_of_matches)


############# Upcoming Fixtures FINSIHED #####################################################
##############################################################################################


############# Recent Results  #####################################################
##############################################################################################



def get_recent_results():
    recent_events = TennisEvent.query.filter(
        or_(TennisEvent.home_venue_id == 1, TennisEvent.away_venue_id == 1),
        TennisEvent.date < datetime.utcnow()  # Adjust timezone as necessary
    ).order_by(desc(TennisEvent.date)).limit(5).all()

    results = []
    for event in recent_events:
        home_or_away = 'Home' if event.home_venue_id == 1 else 'Away'
        opponent_id = event.away_venue_id if home_or_away == 'Home' else event.home_venue_id
        opponent = School.query.get(opponent_id)

        # Directly count the number of matches for this event
        number_of_matches = len(event.matches)

        # Assume wins and losses calculation is corrected here
        wins = sum(1 for match in event.matches if match.won_or_lost == 'Won')
        losses = sum(1 for match in event.matches if match.won_or_lost == 'Lost')

        results.append({
            'date': event.date.strftime('%Y-%m-%d'),
            'opponent_name': opponent.name if opponent else 'Unknown',
            'home_or_away': home_or_away,
            'wins': wins,
            'losses': losses,
            'number_of_matches': number_of_matches,
        })

    return results


############# Recent Results FINISHED #####################################################
##############################################################################################




################## Prepare data for Player Combined Category Scores Graph  ########################################
#####################################################################################################################


def every_player_ratings_chart():
    # Step 1: SQL Query Adjustment
    CoachID = 1
    
    # Adjusted query
    latest_user_category_ratings = db.session.query(
        UserRatings.Rateeid,
        UserRatings.RatingCategory,
        func.max(UserRatings.date_created).label('latest_date')
    ).join(
        User, UserRatings.Rateeid == User.id  # Explicit join condition
    ).filter(
        User.Role == 'Player',
        UserRatings.Raterid == CoachID # So only the coach ratings
    ).group_by(
        UserRatings.Rateeid,
        UserRatings.RatingCategory
    ).subquery('latest_ratings')

    # Assuming the ambiguous join was in the main query fetching the latest ratings' values
    latest_ratings_query = db.session.query(
        User.id,
        User.Username,
        RatingCategory.CategoryDescription,
        UserRatings.Value,
        latest_user_category_ratings.c.latest_date
    ).select_from(UserRatings).join(
        User, UserRatings.Rateeid == User.id  # Starting from UserRatings, joining to User
    ).join(
        latest_user_category_ratings, 
        (UserRatings.Rateeid == latest_user_category_ratings.c.Rateeid) &
        (UserRatings.date_created == latest_user_category_ratings.c.latest_date) &
        (UserRatings.RatingCategory == latest_user_category_ratings.c.RatingCategory)
    ).join(
        RatingCategory, UserRatings.RatingCategory == RatingCategory.CategoryCode
    ).order_by(User.Username).all()
    
    # Step 2: Data Structuring for Chart.js
    
    user_data = {}
    for user_id, username, category_description, value, latest_date in latest_ratings_query:
        if username not in user_data:
            user_data[username] = {'total': 0, 'categories': {}}
        
        user_data[username]['categories'][category_description] = value
        user_data[username]['total'] += value

    labels = list(user_data.keys())
    datasets = []
    category_list = [cat.CategoryDescription for cat in RatingCategory.query.all()]
    for category in category_list:
        dataset = {
            'label': category,
            'data': [],
            'backgroundColor': "assign_a_unique_color",  # Placeholder for color assignment
        }
        
        for user, details in user_data.items():
            dataset['data'].append(details['categories'].get(category, 0))
        
        datasets.append(dataset)

    # Passing the structured data to the template
    return labels, datasets


##################  FINISHED ########################################
#######################################################################################


################## Prepare data for Upcoming Training Sessions Graph  ########################################
#####################################################################################################################


def total_score_player_ratings_chart():
    CoachID = 1
    # Adjusted query with Forename
    latest_user_category_ratings = db.session.query(
        UserRatings.Rateeid,
        UserRatings.RatingCategory,
        func.max(UserRatings.date_created).label('latest_date')
    ).join(
        User, UserRatings.Rateeid == User.id
    ).filter(
        User.Role == 'Player',
        UserRatings.Raterid == CoachID # So only the coach ratings
    ).group_by(
        UserRatings.Rateeid,
        UserRatings.RatingCategory
    ).subquery('latest_ratings')

    latest_ratings_query = db.session.query(
        User.Forename,  # Assuming Forename is the desired label
        func.sum(UserRatings.Value).label('total_value')
    ).select_from(UserRatings).join(
        User, UserRatings.Rateeid == User.id
    ).join(
        latest_user_category_ratings,
        (UserRatings.Rateeid == latest_user_category_ratings.c.Rateeid) &
        (UserRatings.date_created == latest_user_category_ratings.c.latest_date) &
        (UserRatings.RatingCategory == latest_user_category_ratings.c.RatingCategory)
    ).join(
        RatingCategory, UserRatings.RatingCategory == RatingCategory.CategoryCode
    ).group_by(User.Forename).order_by(User.Forename).all()
    
    # Prepare data for Chart.js
    labels = [result.Forename for result in latest_ratings_query]
    totals = [result.total_value for result in latest_ratings_query]

    datasets = [{
        'label': 'Total Ratings',
        'data': totals,
        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
        'borderColor': 'rgba(255, 99, 132, 1)',
        'borderWidth': 1
    }]

    return labels, datasets


##################  FINISHED ########################################
#######################################################################################





def player_ratings_graph():
    players = User.query.filter_by(Role='Player').all()
    categories = RatingCategory.query.all()
    categories=[c.CategoryDescription for c in categories]
    return players, categories



###### Latest Individual Player Ratings Graph #########

@coach.route('/get_player_ratings/<int:player_id>')
@login_required
@role_required('Coach')
def get_player_ratings(player_id):
    CoachID = 1
    ratings = UserRatings.query.filter(
        UserRatings.Rateeid==player_id,
        UserRatings.Raterid == CoachID
        ).all()
    ratings_data = {}
    for rating in ratings:
        category_desc = RatingCategory.query.get(rating.RatingCategory).CategoryDescription
        ratings_data[category_desc] = rating.Value
    return jsonify(ratings_data)


###### Latest Individual Player Ratings Graph FINISHED #########





@coach.route('/coachdashboard', methods=['GET', 'POST'])
@login_required
@role_required('Coach')
def coachdashboard():
    print("MADE IT")
    user_notifications = get_user_notifications(current_user.id)
    fixtures = get_upcoming_fixtures()
    enriched_fixtures = add_opponent_name_to_fixtures(fixtures)
    total_recent_player_ratings_labels, total_recent_player_ratings_datasets = total_score_player_ratings_chart()
    player_ratings_labels, player_ratings_datasets = every_player_ratings_chart()
    recent_results = get_recent_results()
    players, categories = player_ratings_graph()
    # Inside your coachdashboard function, before returning the render_template call
    base_get_player_ratings_url = url_for('coach.get_player_ratings', player_id=0)[:-1]
    # Note: We append a '0' that we'll remove in the template to ensure Flask processes this route correctly.


    return render_template('coachdash.html', user_notifications=user_notifications, base_get_player_ratings_url=base_get_player_ratings_url, players=players, categories=categories, recent_results=recent_results, upcoming_fixtures=enriched_fixtures, player_ratings_labels=player_ratings_labels, player_ratings_datasets=player_ratings_datasets, total_recent_player_ratings_labels=total_recent_player_ratings_labels, total_recent_player_ratings_datasets=total_recent_player_ratings_datasets, user=current_user)








def count_unread_notifications(user_id):
    count = Notification.query.filter_by(receiver_id=user_id, is_read=False).count()
    return count







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










