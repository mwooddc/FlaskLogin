from flask import Blueprint, render_template, session, flash, redirect, url_for, request, get_flashed_messages
from flask_login import login_required, current_user
from .forms import UserRatingForm, RatingCategoryForm, AddSchoolForm, TennisEventForm, MatchForm
from .models import db, User, UserRatings, RatingCategory, School, TennisEvent, Match
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


# @coach.route('/create-event-and-matches', methods=['GET', 'POST'])
# @login_required
# @role_required('Coach')
# def create_event_and_matches():
#     try:
#         event_form = TennisEventForm()
#         match_form = MatchForm()
#         errors = {}  # Initialize errors
#         form_data = dict(request.form)



#         # if request.method == 'POST':
#         #     print("Form Data:", request.form)
#             # print("Won or Lost Value:", form_data.get('won_or_lost'))
        
#         print("DICTIONARY of form_data",  form_data)

#         # Fetch schools data from the database
#         schools = School.query.all()

#         # Populate player choices
#         player_choices = [(str(user.id), f'{user.Forename} {user.Surname}') for user in User.query.filter_by(Role='Player').all()]
#         print("Player Choices:", player_choices)

#         match_form.player1_name_0.choices = [('None', 'None')] + player_choices
#         match_form.player2_name_0.choices = [('None', 'None')] + player_choices


#         if request.method == 'POST' and match_form.validate():
#             return jsonify({'status': 'success'})
#             all_fields_valid = True

#             # Iterate over dynamically added fields
#             for key, value in request.form.items():
#                 if key.startswith('player2_name'):
#                     # Extract the corresponding 'singles_or_doubles' value
#                     # Assuming the naming convention holds for dynamically added fields
#                     singles_or_doubles_key = 'singles_or_doubles' + key[len('player2_name'):]
#                     singles_or_doubles_value = request.form.get(singles_or_doubles_key, '')
                    
#                     # Apply your custom validation logic
#                     if singles_or_doubles_value == 'Singles' and value != 'None':
#                         flash(f"Validation error for {key}: For Singles, 'None' must be selected for Player 2.", 'danger')
#                         all_fields_valid = False
#                         break  # Optionally break if one validation fails, or continue to check all fields

#             if all_fields_valid:
#                 # Proceed with processing the form and saving data
#                 # pass  # Your logic here


#                 # Process form data for TennisEvent
#                 event_date = datetime.strptime(request.form['date'], '%Y-%m-%d')
#                 new_event = TennisEvent(date=event_date,
#                                         home_venue_id=request.form['home_venue'],
#                                         away_venue_id=request.form['away_venue'])
#                 db.session.add(new_event)
#                 db.session.commit()

#                 # form_data = dict(request.form)
#                 print("DICTIONARY of form_data",  form_data)

#                 max_index = determine_number_of_matches(form_data)
#                 print("MAX INDEX",max_index)


#                 # Initialize a variable to keep track of player index
#                 player_index = 0


#                 while True:
#                     # if player_index == 0:
#                     #     player1_name = form_data["player1_name"]
#                     #     player2_name = form_data["player2_name"]
#                     #     singles_or_doubles = form_data["singles_or_doubles"]
#                     #     sets_played = form_data["sets_played"]
#                     #     sets_won = form_data["sets_won"]
#                     #     won_or_lost = form_data["won_or_lost"]
#                     #     comment = form_data["comment"]
#                     # else:
#                     player_key = f"player1_name_{player_index}"
                    
#                     if player_key in form_data:
#                         # Assign values to separate variables
#                         player1_name = form_data.get(f'player1_name_{player_index}', "")
#                         player2_name = form_data.get(f'player2_name_{player_index}', "")
#                         singles_or_doubles = form_data.get(f"singles_or_doubles_{player_index}", "")
#                         sets_played = form_data.get(f"sets_played_{player_index}", "")
#                         sets_won = form_data.get(f"sets_won_{player_index}", "")
#                         won_or_lost = form_data.get(f"won_or_lost_{player_index}", "")
#                         comment = form_data.get(f"comment_{player_index}", "")

#                     else:
#                         break
#                     new_match = Match(tennis_event_id=new_event.id,
#                                             player1_id=player1_name,
#                                             player2_id=player2_name,
#                                             singles_or_doubles=singles_or_doubles,
#                                             sets_played=sets_played,
#                                             sets_won=sets_won,
#                                             won_or_lost=won_or_lost,
#                                             comment=comment)
#                     player_index += 1
#                     db.session.add(new_match)
#                 db.session.commit()
                            
                    

#                 return redirect(url_for('coach.create_event_and_matches'))
            
#         elif request.method == 'POST':
#             errors = {field_name: error_messages for field_name, error_messages in match_form.errors.items()}
#             return jsonify({'status': 'failure', 'errors': errors}), 400
        
#             if not match_form.validate():
#                 print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
#                 max_index = determine_number_of_matches(form_data)
#                 # flash('There were errors in your form, please review them.', 'danger')
#                 # Assuming you have a way to track dynamic fields
#                 errors = {f'player2_name_{i}': match_form.errors.get(f'player2_name_{i}', [])
#                         for i in range(max_index)}  # number_of_matches is dynamic
#                 # errors={"Hey":"Mark"}
#                 print("ERRRORS",errors)
#                 return render_template('create_event_and_matches.html', event_form=event_form, match_form=match_form, user=current_user, schools=schools, errors=errors)
#                 # Form validation failed
                

#         return render_template('create_event_and_matches.html', event_form=event_form, match_form=match_form, user=current_user, schools=schools)

#     except Exception as e:
#         print("ERRRRRRRRRRRRRRRRRRRRRROR")
#         return jsonify({'status': 'error', 'message': str(e)}), 500





@coach.route('/submit', methods=['GET', 'POST'])
@login_required
@role_required('Coach')
def submit_users():
    schools = School.query.all()
    #to ge the players as a list of tuples:
    # player_choices = [(str(user.id), f'{user.Forename} {user.Surname}') for user in User.query.filter_by(Role='Player').all()]
    #to get the players as a list of dictionaries:
    player_choices = [
    {"user_id": str(user.id), "user_name": f"{user.Forename} {user.Surname}"}
    for user in User.query.filter_by(Role='Player').all()]
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


        # errors = {}
        # valid_data = []

        # # Validate each user's data
        # for i, user in enumerate(matches):
        #     user_id = user.get('id', '')
        #     name = user.get('name', '')
        #     age = user.get('age', '')
        #     user_errors = []

        #     # Validation checks
        #     if not user_id or not user_id.isdigit():
        #         user_errors.append("ID must be a number and cannot be blank")
        #     if not name:
        #         user_errors.append("Name must not be blank")
        #     if not age or not age.isdigit() or not 1 <= int(age) <= 100:
        #         user_errors.append("Age must be a number between 1 and 100")

        #     if user_errors:
        #         errors[i] = user_errors

        # print("ERRORS",errors)

        if errors:
            for e in errors:
                flash(e)


            # for key, error_list in errors.items():
            #     error_messages = ', '.join(error_list)  # Join all errors in the list into a single string
            #     flash(f"Match {key + 1} has these errors: {error_messages}")

            return render_template('test.html', errors=errors, user=current_user, event=event, schools=schools, players=players_dict)
        else:
            # return "All users added successfully", 200
            flash('matches added successfully!')
            return redirect(url_for('coach.submit_users'))  # Redirect back to the form
            # return render_template('test.html', errors=errors, user=current_user, event=event, schools=schools)

        # Proceed to JSON generation and database insertion if data is valid
        # Assume valid_data is the data to be inserted
        # Generate JSON file and insert into database here
    # For GET request, just render the template
    return render_template('test.html', user=current_user, schools=schools, players=players_dict)







@coach.route('/create-event-and-matches', methods=['GET', 'POST'])
@login_required
@role_required('Coach')
def create_event_and_matches():
        #Fetch schools data from the database
    schools = School.query.all()
    if request.method == 'POST':
        # event_form = TennisEventForm()
        match_raw_data = request.form.to_dict(flat=False)
        print(match_raw_data)
        return render_template('create_event_and_matches.html', user=current_user, schools=schools)
    else:
        return render_template('create_event_and_matches.html', user=current_user, schools=schools)








    # try:
    #     event_form = TennisEventForm()
    #     match_form = MatchForm()
    #     errors = {}  # Initialize errors
    #     form_data = dict(request.form)



    #     # if request.method == 'POST':
    #     #     print("Form Data:", request.form)
    #         # print("Won or Lost Value:", form_data.get('won_or_lost'))
        
    #     print("DICTIONARY of form_data",  form_data)

    #     # Fetch schools data from the database
    #     schools = School.query.all()

    #     # Populate player choices
    #     player_choices = [(str(user.id), f'{user.Forename} {user.Surname}') for user in User.query.filter_by(Role='Player').all()]
    #     print("Player Choices:", player_choices)

    #     match_form.player1_name_0.choices = [('None', 'None')] + player_choices
    #     match_form.player2_name_0.choices = [('None', 'None')] + player_choices


    #     if request.method == 'POST' and match_form.validate():
    #         return jsonify({'status': 'success'})
    #         all_fields_valid = True

    #         # Iterate over dynamically added fields
    #         for key, value in request.form.items():
    #             if key.startswith('player2_name'):
    #                 # Extract the corresponding 'singles_or_doubles' value
    #                 # Assuming the naming convention holds for dynamically added fields
    #                 singles_or_doubles_key = 'singles_or_doubles' + key[len('player2_name'):]
    #                 singles_or_doubles_value = request.form.get(singles_or_doubles_key, '')
                    
    #                 # Apply your custom validation logic
    #                 if singles_or_doubles_value == 'Singles' and value != 'None':
    #                     flash(f"Validation error for {key}: For Singles, 'None' must be selected for Player 2.", 'danger')
    #                     all_fields_valid = False
    #                     break  # Optionally break if one validation fails, or continue to check all fields

    #         if all_fields_valid:
    #             # Proceed with processing the form and saving data
    #             # pass  # Your logic here


    #             # Process form data for TennisEvent
    #             event_date = datetime.strptime(request.form['date'], '%Y-%m-%d')
    #             new_event = TennisEvent(date=event_date,
    #                                     home_venue_id=request.form['home_venue'],
    #                                     away_venue_id=request.form['away_venue'])
    #             db.session.add(new_event)
    #             db.session.commit()

    #             # form_data = dict(request.form)
    #             print("DICTIONARY of form_data",  form_data)

    #             max_index = determine_number_of_matches(form_data)
    #             print("MAX INDEX",max_index)


    #             # Initialize a variable to keep track of player index
    #             player_index = 0


    #             while True:
    #                 # if player_index == 0:
    #                 #     player1_name = form_data["player1_name"]
    #                 #     player2_name = form_data["player2_name"]
    #                 #     singles_or_doubles = form_data["singles_or_doubles"]
    #                 #     sets_played = form_data["sets_played"]
    #                 #     sets_won = form_data["sets_won"]
    #                 #     won_or_lost = form_data["won_or_lost"]
    #                 #     comment = form_data["comment"]
    #                 # else:
    #                 player_key = f"player1_name_{player_index}"
                    
    #                 if player_key in form_data:
    #                     # Assign values to separate variables
    #                     player1_name = form_data.get(f'player1_name_{player_index}', "")
    #                     player2_name = form_data.get(f'player2_name_{player_index}', "")
    #                     singles_or_doubles = form_data.get(f"singles_or_doubles_{player_index}", "")
    #                     sets_played = form_data.get(f"sets_played_{player_index}", "")
    #                     sets_won = form_data.get(f"sets_won_{player_index}", "")
    #                     won_or_lost = form_data.get(f"won_or_lost_{player_index}", "")
    #                     comment = form_data.get(f"comment_{player_index}", "")

    #                 else:
    #                     break
    #                 new_match = Match(tennis_event_id=new_event.id,
    #                                         player1_id=player1_name,
    #                                         player2_id=player2_name,
    #                                         singles_or_doubles=singles_or_doubles,
    #                                         sets_played=sets_played,
    #                                         sets_won=sets_won,
    #                                         won_or_lost=won_or_lost,
    #                                         comment=comment)
    #                 player_index += 1
    #                 db.session.add(new_match)
    #             db.session.commit()
                            
                    

    #             return redirect(url_for('coach.create_event_and_matches'))
            
    #     elif request.method == 'POST':
    #         errors = {field_name: error_messages for field_name, error_messages in match_form.errors.items()}
    #         return jsonify({'status': 'failure', 'errors': errors}), 400
        
    #         if not match_form.validate():
    #             print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
    #             max_index = determine_number_of_matches(form_data)
    #             # flash('There were errors in your form, please review them.', 'danger')
    #             # Assuming you have a way to track dynamic fields
    #             errors = {f'player2_name_{i}': match_form.errors.get(f'player2_name_{i}', [])
    #                     for i in range(max_index)}  # number_of_matches is dynamic
    #             # errors={"Hey":"Mark"}
    #             print("ERRRORS",errors)
    #             return render_template('create_event_and_matches.html', event_form=event_form, match_form=match_form, user=current_user, schools=schools, errors=errors)
    #             # Form validation failed
                

    #     return render_template('create_event_and_matches.html', event_form=event_form, match_form=match_form, user=current_user, schools=schools)

    # except Exception as e:
    #     print("ERRRRRRRRRRRRRRRRRRRRRROR")
    #     return jsonify({'status': 'error', 'message': str(e)}), 500