from flask import Blueprint, render_template, session, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import db, User, UserRatings, RatingCategory, School, Notification
from sqlalchemy import func
from .forms import LoginForm
from faker import Faker
from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import datetime, timedelta

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
    # role = session.get('role', 'Player')  # Default to 'Player' if not set

    #here the user variable stores the current user which if it exists i.e.
    # you are logged in, is an object containing the users record
    # we can then inside home.html use jinja to access the users fields
    #e.g. id, username, email {{ current_user.username }}
    if current_user.is_authenticated and current_user.Role == 'Player':
        return redirect(url_for("player.playerdashboard"))
        # return redirect(url_for('playerdashboard'))
        # return render_template("playerdash.html", user=current_user)
    elif current_user.is_authenticated and current_user.Role == 'Coach':
        return redirect(url_for("coach.coachdashboard", user=current_user))



@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html', user=current_user)


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html', user=current_user)



def count_unread_notifications(user_id):
    count = Notification.query.filter_by(receiver_id=user_id, is_read=False).count()
    return count



#######################################################
###### ROUTES TO POPULATE THE DATABASE WITH DATA ######
#######################################################



@views.route("/")
@views.route("/populate_categories")
# Predefined category descriptions
def populate_categories():
    category_descriptions = [
        "Forehand", "Backhand", "Serve", "Net-Play", "Lob", "Volley", "Spin",
        "Timing", "Slice", "Footwork", "Strategy", "Speed", "Coordination",
        "Endurance", "Flexibility", "Agility", "Reflexes", "Finesse"
    ]

    for code, description in enumerate(category_descriptions, start=1):
        category = RatingCategory(CategoryCode=code, CategoryDescription=description)
        db.session.add(category)
    db.session.commit()

    flash('Database populated successfully!', 'success')
    return redirect(url_for('views.home'))  # Redirect to another route (e.g., index)




@views.route("/")
@views.route("/populate_schools")
# Predefined category descriptions
def populate_schools():
    schools = [
        "Charter House", "Epsom", "Sevenoaks", "Harrow", "Tonbridge", "Eton", "Wellington","Cranleigh"
    ]

    for code, school in enumerate(schools, start=1):
        new_school = School(id=code, name=school)
        db.session.add(new_school)
    db.session.commit()

    flash('Database populated successfully!', 'success')
    return redirect(url_for('views.home'))  # Redirect to another route (e.g., index)






@views.route("/")
@views.route("/populate_player_ratings")
# Predefined category descriptions
def populate_player_ratings():
    CoachID = 1
    player_ratings =[
        [CoachID,4,1,5,"2024-03-05"],
        [CoachID,4,2,3,"2024-03-05"],
        [CoachID,4,3,6,"2024-03-05"],
        [CoachID,4,4,2,"2024-03-05"],
        [CoachID,4,5,8,"2024-03-07"],
        [CoachID,4,6,5,"2024-03-07"],
        [CoachID,4,1,7,"2024-03-07"],
        [CoachID,4,2,5,"2024-03-07"],
        [CoachID,4,7,7,"2024-03-08"],
        [CoachID,4,3,3,"2024-03-10"],
        [CoachID,4,4,4,"2024-03-12"]
    ]
    for i in range(len(player_ratings)):
        Raterid = player_ratings[i][0]
        Rateeid = player_ratings[i][1]
        RatingCategory = player_ratings[i][2]
        Value = player_ratings[i][3]
        date_created_string = player_ratings[i][4]
        # convert a string date into an SQLite recognised data type
        date_created = datetime.strptime(date_created_string, "%Y-%m-%d")

        rating = UserRatings(Raterid=Raterid, Rateeid=Rateeid, RatingCategory=RatingCategory,
                    Value=Value, date_created=date_created)
        db.session.add(rating)

    db.session.commit()

    flash('Database populated successfully with new player ratings!', 'success')
    return redirect(url_for('views.home'))  # Redirect to another route (e.g., index)




@views.route("/")
@views.route("/populate_users")
# Predefined category descriptions
def populate_users():
    fake = Faker()
    start_date = datetime(2000, 1, 1)  # Start date for random date generation
    end_date = datetime.now()  # End date for random date generation (current date)

    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    created_date = start_date + timedelta(days=random_days)
    passwords = []

    ####################################################################################
    ########################## Generate bulk users - change range ######################
    ####################################################################################

    # for _ in range(5):
    #     email = fake.email()
    #     username = fake.user_name()
    #     password = fake.password()
    #     hashed_password = generate_password_hash(password)
    #     forename = fake.first_name()
    #     surname = fake.last_name()
    #     role = random.choice(['Player', 'Coach'])
    #     date_created = created_date
        
    #     user = User(Email=email, Username=username, Password=hashed_password,
    #                 Forename=forename, Surname=surname, Role=role,
    #                 date_created=date_created)
    #     db.session.add(user)
        
        
    #     # Print out the generated user information including the password
    #     passwords.append(f"Username: {username}, Password: {password}")

    ####################################################################################

    ####################################################################################
    ########################## FOR 2 USERS - add to list if needed #######################
    ####################################################################################

    set_users =[
        ["coach@coach.com","coach","coach123","coach","coach","Coach"],
        ["player@player.com","player","player123","player","player","Player"],
        ["player2@player2.com","player2","player2123","player2","player2","Player"],
        ["sam@sam.com","sam","sam123","sam","smith","Player"]
    ]
    for i in range(len(set_users)):
        email = set_users[i][0]
        username = set_users[i][1]
        password = set_users[i][2]
        hashed_password = generate_password_hash(set_users[i][2])
        forename = set_users[i][3]
        surname = set_users[i][4]
        role = set_users[i][5]
        date_created = created_date
        
        user = User(Email=email, Username=username, Password=hashed_password,
                    Forename=forename, Surname=surname, Role=role,
                    date_created=date_created)
        db.session.add(user)
        
        
        # Print out the generated user information including the password
        passwords.append(f"Username: {username}, Password: {password}")

    ####################################################################################
    
        
    db.session.commit()
    flash('Users populated successfully!', 'success')
    return render_template("passwords.html", passwords=passwords, user=current_user)




#### routes required for Notifications Page ####
#################################################


@views.route('/all_notifications')
@login_required
def all_notifications():
    # user_notifications = Notification.query.filter_by(receiver_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    
    notifications = Notification.query.filter_by(receiver_id=current_user.id).order_by(Notification.timestamp.desc()).all()
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
    
    return render_template('notifications.html', notifications=detailed_notifications, user=current_user)



@views.route('/all_mark_notification_as_read/<int:notification_id>', methods=['POST'])
@login_required
def all_mark_notification_as_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, receiver_id=current_user.id).first()
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': 'Notification marked as read'}), 200
    return jsonify({'error': 'Notification not found'}), 404







@views.route('/all_reply_to_notification', methods=['POST'])
@login_required
def all_reply_to_notification():
    data = request.get_json()

    original_notification_id = data.get('original_notification_id')
    reply_message = data.get('reply_message')

    # Fetch the original notification to derive receiver_id and to mark it as read
    original_notification = Notification.query.get(original_notification_id)
    if not original_notification:
        return jsonify({'error': 'Original notification not found'}), 404
    
    # Assuming you want to reply to the sender of the original notification
    receiver_id = original_notification.sender_id

    original_notification.is_read = True  # Mark the original notification as read

    # Create the reply notification
    reply_notification = Notification(
        receiver_id=receiver_id,
        sender_id=current_user.id,  # The ID of the currently logged-in user
        comment=reply_message,
        is_read=False  # New notifications are unread by default
    )
    
    db.session.add(reply_notification)
    db.session.commit()

    return jsonify({'success': 'Reply submitted successfully'}), 200

#### routes required for Notifications Page ####
################## FINSIHED #########################
