from flask import Blueprint, render_template, session, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import db, User, UserRatings, RatingCategory, School

from faker import Faker
from werkzeug.security import generate_password_hash
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
        return render_template("coachdash.html", user=current_user)



@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html', user=current_user)


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html', user=current_user)



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
    player_ratings =[
        [2,4,1,5,"2024-03-05"],
        [2,4,2,3,"2024-03-05"],
        [2,4,3,6,"2024-03-05"],
        [2,4,4,2,"2024-03-05"],
        [2,4,5,8,"2024-03-07"],
        [2,4,6,5,"2024-03-07"],
        [2,4,1,7,"2024-03-07"],
        [2,4,2,5,"2024-03-07"],
        [2,4,7,7,"2024-03-08"],
        [2,4,3,3,"2024-03-10"],
        [2,4,4,4,"2024-03-12"]
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
        ["player@player.com","player","player123","player","player","Player"],
        ["coach@coach.com","coach","coach123","coach","coach","Coach"],
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
