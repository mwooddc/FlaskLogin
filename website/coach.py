from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from flask_login import login_required, current_user
from .forms import UserRatingForm, RatingCategoryForm, AddSchoolForm, ScheduleTrainingSessionForm
from .models import db, User, UserRatings, RatingCategory, School, TennisEvent, Match, Notification, PracticeSessions, SessionAttendance
from .auth import role_required
from datetime import datetime
from flask import jsonify
import re
from sqlalchemy import func, case, or_, desc
from sqlalchemy.exc import SQLAlchemyError


#A Blueprint simply allows you to create seperate files from the standard app.py
#file to hold routes (without blueprint all routes would be in one file)
#see this video for explanation: https://www.youtube.com/watch?v=pjVhrIJFUEs
#To use a Blueprint you have to import Blueprint from flask (see above)
#You then assign that blueprint to a variable and then use that 
#as the @route in this code
coach = Blueprint("coach", __name__)

# CONSTANTS
CoachID = 1
HomeVenueID = 1

############# HANDLING NOTIFICATIONS FOR COACHES DASHBOARD ###################

# Function: Get a users notifications
def get_user_notifications(user_id):
    notifications = Notification.query.filter_by(receiver_id=user_id, is_read=False).order_by(Notification.timestamp.desc()).limit(5).all()

    # Return a list of dictionaries with more details
    detailed_notifications = [{
        'id': notification.id,
        'comment': notification.comment,
        'match_id': notification.match_id,
        'sender_id': notification.sender_id,
        'sender_name': f"{notification.sender.Forename} {notification.sender.Surname}",
        'is_read': notification.is_read,
        'timestamp': notification.timestamp
    } for notification in notifications]
    return detailed_notifications

# Route: Mark the Notifications as read
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

# Route: Reply to a Notification
# This route can not be the same name as the route in the player.py
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
        sender_id=current_user.id,
        comment=reply_message,
        is_read=False
    )
    db.session.add(reply_notification)
    db.session.commit()

    return redirect(url_for('coach.coachdashboard'))


############# HANDLING NOTIFICATIONS #########################################
############# FINISHED #######################################################




################## UPCOMING FIXTURES #########################################

# Function: Get ALL the upcoming fixtures
def get_upcoming_fixtures():
    fixtures_query = db.session.query(
        TennisEvent.id,
        TennisEvent.date.label('date'),
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
        or_(TennisEvent.home_venue_id == HomeVenueID, TennisEvent.away_venue_id == HomeVenueID)
    ).group_by(TennisEvent.id).all()

    return [
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
# `fixtures` will be a list of tuples with the structure (date, home_or_away, opponent, number_of_matches)


################## UPCOMING FIXTURES #########################################
############# FINISHED #######################################################


##################### RECENT RESULTS #########################################

# Function: Get all of the recent results
def get_recent_results():
    recent_events = TennisEvent.query.filter(
        or_(TennisEvent.home_venue_id == HomeVenueID, TennisEvent.away_venue_id == HomeVenueID),
        TennisEvent.date < datetime.utcnow()  # Adjust timezone as necessary
    ).order_by(desc(TennisEvent.date)).limit(5).all()

    results = []
    for event in recent_events:
        home_or_away = 'Home' if event.home_venue_id == HomeVenueID else 'Away'
        opponent_id = event.away_venue_id if home_or_away == 'Home' else event.home_venue_id
        opponent = School.query.get(opponent_id)

        # Directly count the number of matches for this event
        number_of_matches = len(event.matches)

        # Assume wins and losses calculation is corrected here
        wins = sum(1 for match in event.matches if match.won_or_lost == 'Won')
        losses = sum(1 for match in event.matches if match.won_or_lost == 'Lost')

        results.append({
            'date': event.date.strftime('%d/%m/%y'),
            'opponent_name': opponent.name if opponent else 'Unknown',
            'home_or_away': home_or_away,
            'wins': wins,
            'losses': losses,
            'number_of_matches': number_of_matches,
        })

    return results

##################### RECENT RESULTS #########################################
############# FINISHED #######################################################




##########  PREPARE DATA FOR PLAYER COMBINED CATEGORY SCORES GRAPH  ##########

# Function: Retrieve players ratings for every category
def every_player_ratings_chart():

    # STRUGGLED TO CONSTRUCT THIS QUERY AND NEEDED A LOT OF HELP INCLUDING CHATGPT
    # SQL QUERY
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
    
    # Constructing an appropriate data structure which can then be used with chart.js
    # To plot the graph    
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

    # returns the labels and data for the graph when passed to the template
    return labels, datasets

##########  PREPARE DATA FOR PLAYER COMBINED CATEGORY SCORES GRAPH  ##########
############# FINISHED #######################################################





###################################################################################################################
## Might REMOVE the function below as the graph above is better and similar ##
##############################################################################
# Function: 
def total_score_player_ratings_chart():
    
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
        User.Forename,  
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

###################################################################################################################
## Might REMOVE the function below as the graph above is better and similar ##
############# FINISHED #######################################################








####### PREPARE THE DATA FOR THE PLAYER RATINGS GRAPH (IN PANEL SIX) #########

# Function: Get the players and the categories
def player_ratings_graph():
    players = User.query.filter_by(Role='Player').all()
    categories = RatingCategory.query.all()
    categories=[c.CategoryDescription for c in categories]
    return players, categories

# Route: This is used in conjunction with base_get_player_ratings_url
# for the AJAX request when selecting the player you want to see in the
# graph which shows that players latest ratings for each category
@coach.route('/get_player_ratings/<int:player_id>')
@login_required
@role_required('Coach')
def get_player_ratings(player_id):
    # CoachID = 1
    ratings = UserRatings.query.filter(
        UserRatings.Rateeid==player_id,
        UserRatings.Raterid == CoachID
        ).all()
    ratings_data = {}
    for rating in ratings:
        category_desc = RatingCategory.query.get(rating.RatingCategory).CategoryDescription
        ratings_data[category_desc] = rating.Value
    return jsonify(ratings_data)


######## PREPARE THE DATA FOR THE PLAYER RATINGS GRAPH (IN PANEL SIX) #######
############# FINISHED #######################################################



#######################  ROUTE FOR THE COACH DASHBOARD  ######################

# Route: This is the main route for the coaches dashboard
@coach.route('/coachdashboard', methods=['GET', 'POST'])
@login_required
@role_required('Coach')
def coachdashboard():

    user_notifications = get_user_notifications(current_user.id)
    fixtures = get_upcoming_fixtures()
    enriched_fixtures = add_opponent_name_to_fixtures(fixtures)
    total_recent_player_ratings_labels, total_recent_player_ratings_datasets = total_score_player_ratings_chart()
    player_ratings_labels, player_ratings_datasets = every_player_ratings_chart()
    recent_results = get_recent_results()
    players, categories = player_ratings_graph()
    # This is for the AJAX request
    base_get_player_ratings_url = url_for('coach.get_player_ratings', player_id=0)[:-1]
    # Have appended a '0' which I remove in the template to ensure Flask processes the route correctly


    return render_template('coachdash.html', user_notifications=user_notifications, \
                           base_get_player_ratings_url=base_get_player_ratings_url, \
                           players=players, categories=categories, recent_results=recent_results, \
                           upcoming_fixtures=enriched_fixtures, player_ratings_labels=player_ratings_labels, \
                           player_ratings_datasets=player_ratings_datasets, total_recent_player_ratings_labels=total_recent_player_ratings_labels, \
                           total_recent_player_ratings_datasets=total_recent_player_ratings_datasets, user=current_user)

#########################  ROUTE FOR THE DASHBOARD  ##########################
############# FINISHED #######################################################



######################  ROUTE FOR THE RATING A PLAYER  #######################

# Route: 
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

######################  ROUTE FOR THE RATING A PLAYER  #######################
############# FINISHED #######################################################


######################  ROUTE FOR ADDING A NEW CATEGORY  #####################

# Route: 
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

######################  ROUTE FOR ADDING A NEW CATEGORY  #####################
############# FINISHED #######################################################



#######################  ROUTE FOR ADDING A NEW SCHOOL  ######################

# Route: 
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

#######################  ROUTE FOR ADDING A NEW SCHOOL  ######################
############# FINISHED #######################################################




# Function: 
def determine_number_of_matches(request):
    # Example: Parsing field names to find the highest index
    max_index = 0
    for key in request.keys():
        if key.startswith('player1_name_'):
            index = int(key.split('_')[-1])  # Extract the numeric part of the field name
            max_index = max(max_index, index) + 1
    return max_index


###############  ROUTE FOR CREATING AN EVENT AND MATCHES  ####################

# Route: 
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
        event = {
            'date': raw_data['date'][0],
            'home_venue': int(raw_data['home_venue'][0]),
            'away_venue': int(raw_data['away_venue'][0]),
            'matches': []
        }

        # Define keys within matches that need their values converted to integers
        integer_keys = ['player1_name', 'player2_name', 'sets_played', 'sets_won']

        # prepare the match data
        for key, value in raw_data.items():
            if key.startswith('match'):
                parts = key.split('[')
                match_index = int(parts[1].split(']')[0])
                attribute_name = parts[2].split(']')[0]

                while len(event['matches']) <= match_index:
                    event['matches'].append({})

                if attribute_name in integer_keys:
                    event['matches'][match_index][attribute_name] = int(value[0])
                else:
                    event['matches'][match_index][attribute_name] = value[0]

        print("Event Updated",event)

        errors = []

        # Loop through each match in the "matches" list with updated error message
        for i, match in enumerate(event['matches']):
            if match['sets_won'] > match['sets_played']:
                errors.append(f"Error in Match {i+1}: Sets won can not exceed sets played")

        print("NEW ERRORS",errors)

        if errors:
            for e in errors:
                flash(e)

            return render_template('create_event_and_matches.html', errors=errors, user=current_user, event=event, schools=schools, players=players_dict)
        else:
            event_date = datetime.strptime(event['date'], "%Y-%m-%d")

            tennis_event = TennisEvent(
                date=event_date,
                home_venue_id=event['home_venue'],
                away_venue_id=event['away_venue']
            )

            db.session.add(tennis_event)
            db.session.commit()

            for match_data in event['matches']:
                match = Match(
                    tennis_event_id=tennis_event.id,
                    player1_id=match_data['player1_name'],
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
                        if player_id and player_id != current_user.id:
                            notification = Notification(
                                receiver_id=player_id,
                                sender_id=current_user.id,
                                match_id=match.id,
                                comment=match_data['comment'],
                                is_read=False
                            )                        

                            db.session.add(notification)

            # Commit all matches to the database
            db.session.commit()

            flash('matches added successfully!')
            return redirect(url_for('coach.create_event_and_matches'))  # Redirect back to the form

    return render_template('create_event_and_matches.html', user=current_user, schools=schools, players=players_dict)

###############  ROUTE FOR CREATING AN EVENT AND MATCHES  ####################
############# FINISHED #######################################################



######################  EDITING UPCOMING FIXTURES  ###########################

# Route: 
@coach.route('/coach_edit_fixture/<int:fixture_id>', methods=['GET', 'POST'])
@login_required
@role_required('Coach')
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


                singles_or_doubles = request.form.get(f'match_{match.id}_singles_or_doubles')


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
            return redirect(url_for('coach.edit_fixture', fixture_id=fixture_id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred while updating the fixture.', 'error')

    # If GET, render the form with current match details
    return render_template('edit_fixture.html', fixture=fixture, matches=matches, \
                            home_school=home_school, away_school=away_school, \
                            user=current_user)

######################  EDITING UPCOMING FIXTURES  ###########################
############# FINISHED #######################################################


######################  SCHEDULING TRAINING SESSIONS #########################

# Route: for scheduling a training session
@coach.route('/schedule_training_session', methods=['GET', 'POST'])
@login_required
@role_required('Coach')
def schedule_training_session():
    form = ScheduleTrainingSessionForm()
    if form.validate_on_submit():
        # Extract data from the form
        date = form.date.data
        time = form.time.data
        comments = form.comments.data

        # Combine date and time into a single datetime object
        session_time = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')

        # Create a new PracticeSessions instance
        new_session = PracticeSessions(SessionTime=session_time, Comments=comments)

        # Add the new session to the database
        db.session.add(new_session)
        db.session.commit()

        flash('Training session scheduled successfully!', 'success')
        return redirect(url_for('coach.training_session_register', session_id=new_session.SessionID))

    return render_template('schedule_training_session.html', form=form, user=current_user)

######################  SCHEDULING TRAINING SESSIONS #########################
############# FINISHED #######################################################




##################  VIEW A TRAINING SESSION and REGISTER #####################

# Route for viewing session details and recording attendance
@coach.route('/session/<int:session_id>', methods=['GET', 'POST'])
@coach.route('/session/<int:session_id>', methods=['GET', 'POST'])
@login_required
@role_required('Coach')
def training_session_register(session_id):
    session = PracticeSessions.query.get(session_id)
    players = User.query.filter_by(Role='Player').all()
    existing_attendance = SessionAttendance.query.filter_by(SessionID=session_id).all()

    if request.method == 'POST':
        for player in players:
            attendance = request.form.get(f'player_{player.id}_attendance')
            # Update existing attendance records or create new ones
            session_attendance = SessionAttendance.query.filter_by(SessionID=session_id, id=player.id).first()
            if session_attendance:
                session_attendance.Attended = attendance
            else:
                session_attendance = SessionAttendance(SessionID=session_id, id=player.id, Attended=attendance)
                db.session.add(session_attendance)
        db.session.commit()
        
        if existing_attendance:
            flash('Attendance has been updated successfully!', 'success')
        else:
            flash('Attendance has been saved successfully!', 'success')
        
        return redirect(url_for('coach.training_session_register', session_id=session_id))
    
    # Prepopulate form fields with existing attendance data
    attendance_data = {}
    for player in players:
        attendance = next((a.Attended for a in existing_attendance if a.id == player.id), None)
        if attendance:
            attendance_data[player.id] = attendance
    
    return render_template('training_session_register.html', session=session, players=players, attendance_data=attendance_data, user=current_user)

##################  VIEW A TRAINING SESSION and REGISTER #####################
############# FINISHED #######################################################