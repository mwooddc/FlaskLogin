from flask import Blueprint, render_template, session
from flask_login import login_required, current_user
from .auth import role_required
# from collections import defaultdict
# from sqlalchemy.sql import func

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
    ratings_query = db.session.query(UserRatings, RatingCategory).join(RatingCategory).filter(UserRatings.Rateeid == current_user.id).all()
    # Process the query results
    categories = [category.CategoryDescription for _, category in ratings_query]
    ratings = [rating.Value for rating, _ in ratings_query]
    return render_template('playerdash.html', ratings_query=ratings_query, ratings=ratings, categories=categories,user=current_user)




# @player.route('/playerdashboard')
# @login_required
# @role_required('Player')
# def playerdashboard():
#     role = session.get('role', 'Player')  # Default to 'Player' if not set

#     # Query to fetch the ratings, their categories, and dates for the current user
#     ratings_query = db.session.query(UserRatings.Value, UserRatings.date_created, RatingCategory.CategoryDescription)\
#         .join(RatingCategory)\
#         .filter(UserRatings.Rateeid == current_user.id)\
#         .order_by(UserRatings.date_created.asc()).all()

#     # Organize data for plotting
#     data_for_plot = defaultdict(lambda: defaultdict(list))
#     for value, date_created, category_description in ratings_query:
#         data_for_plot[category_description]['dates'].append(date_created.strftime('%Y-%m-%d'))  # Format date as string
#         data_for_plot[category_description]['values'].append(value)

#     # Prepare data for Chart.js
#     categories = list(data_for_plot.keys())
#     datasets = []
#     for category, details in data_for_plot.items():
#         datasets.append({
#             'label': category,
#             'data': details['values'],
#             'dates': details['dates'],  # You'll use this to ensure all datasets have the same x-axis labels
#             # Add more customization for each line here (e.g., backgroundColor, borderColor)
#         })

#     return render_template('playerdash.html', datasets=datasets, categories=categories, user=current_user)
