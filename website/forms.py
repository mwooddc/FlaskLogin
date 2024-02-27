from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, DataRequired, NumberRange, ValidationError
from wtforms import SelectField, StringField, SubmitField, IntegerField
from .models import User, RatingCategory

class UserRatingForm(FlaskForm):
    ratee_id = SelectField('Ratee', coerce=int)
    rating_category = SelectField('Rating Category', coerce=int)
    value = IntegerField('Value:', validators=[InputRequired(), NumberRange(min=0, max=10, message="Value must be between 0 and 10")])

    def __init__(self, *args, **kwargs):
        super(UserRatingForm, self).__init__(*args, **kwargs)
        # Populate the ratee dropdown list with user names
        self.ratee_id.choices = [(user.id, f"{user.Forename} {user.Surname}") for user in User.query.all()]
        # Populate the rating category dropdown list with category names
        self.rating_category.choices = [(category.CategoryCode, category.CategoryDescription) for category in RatingCategory.query.all()]

class RatingCategoryForm(FlaskForm):
    category_description = StringField('Category Description', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddSchoolForm(FlaskForm):
    school_name = StringField('School Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


# class TennisEventForm(FlaskForm):
#     date = StringField('Date', validators=[InputRequired()])
#     home_venue = SelectField('Home Venue', coerce=int, validators=[InputRequired()])
#     away_venue = SelectField('Away Venue', coerce=int, validators=[InputRequired()])

# class MatchForm(FlaskForm):
#     player1_name = SelectField('Player 1')
#     player2_name = SelectField('Player 2')
#     singles_or_doubles = SelectField('Singles or Doubles')
#     sets_played = IntegerField('Sets Played', validators=[InputRequired()])
#     sets_won = IntegerField('Sets Won', validators=[InputRequired()])
#     outcome = SelectField('Outcome')
#     comment = StringField('Comment')

class TennisEventForm(FlaskForm):
    date = StringField('Date', validators=[InputRequired()])
    home_venue = StringField('Home Venue', validators=[InputRequired()])
    away_venue = StringField('Away Venue', validators=[InputRequired()])

class MatchForm(FlaskForm):
    player1_name = SelectField('Player 1')
    # player2_name = SelectField('Player 2')
    player2_name = SelectField('Player 2', choices=[('', 'None')])  # Assuming you've populated the rest of the choices elsewhere
    singles_or_doubles = SelectField(
        'Singles or Doubles',
        choices=[('Singles', 'Singles'), ('Doubles', 'Doubles')],
        validators=[DataRequired()]
    )
    sets_played = IntegerField('Sets Played', validators=[InputRequired()])
    sets_won = IntegerField('Sets Won', validators=[InputRequired()])
    won_or_lost = StringField('won_or_lost')
    comment = StringField('Comment')


    def validate_player2_name(form, field):
        print("Test",form.singles_or_doubles.data)
        if form.singles_or_doubles.data == 'Singles' and field.data != 'None':
            raise ValidationError("For Singles, 'None' must be selected for Player 2.")
