from flask_wtf import FlaskForm
from flask import flash
from wtforms.validators import InputRequired, DataRequired, NumberRange, ValidationError, Email, EqualTo, Length
from wtforms import SelectField, StringField, SubmitField, IntegerField, TextAreaField, PasswordField, RadioField
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
    category_description = StringField('Category Description', validators=[
        DataRequired()])
    #     Length(min=3, message='The field must contain at least 3 characters.')
    # ])
    submit = SubmitField('Submit')
    def validate_category_description(form, field):
        if len(field.data) < 3:
            flash('The category description must contain at least 3 characters.', 'error')
            raise ValidationError('The category description must contain at least 3 characters.')


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
    player1_name_0 = SelectField('Player 1')
    # player2_name = SelectField('Player 2')
    player2_name_0 = SelectField('Player 2', choices=[('', 'None')])  # Assuming you've populated the rest of the choices elsewhere
    singles_or_doubles_0 = SelectField(
        'Singles or Doubles',
        choices=[('Singles', 'Singles'), ('Doubles', 'Doubles')],
        validators=[DataRequired()]
    )
    sets_played_0 = IntegerField('Sets Played', validators=[InputRequired()])
    sets_won_0 = IntegerField('Sets Won', validators=[InputRequired()])
    won_or_lost_0 = SelectField(
        'Won or Lost',
        choices=[('Won', 'Won'), ('Lost', 'Lost')],
        validators=[DataRequired()]
    )
    comment_0 = TextAreaField('Comment', render_kw={'rows': 4, 'cols': 50})

    def validate_player1_name_0(form, field):
        if field.data == 'None':
            raise ValidationError("Player 1 can not be set to None.")

    def validate_player2_name_0(form, field):
        print("Test",form.singles_or_doubles_0.data)
        if form.singles_or_doubles_0.data == 'Singles' and field.data != 'None':
            raise ValidationError("For Singles, 'None' must be selected for Player 2.")
        elif form.singles_or_doubles_0.data == 'Doubles' and field.data == 'None':
            raise ValidationError("For Doubles, 'None' can NOT be selected for Player 2.")


class LoginForm(FlaskForm):
    Email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email", "class": "form-control"})
    Password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password", "class": "form-control"})
    submit = SubmitField('Login', render_kw={"class": "btn btn-primary"})

class SignUpForm(FlaskForm):
    Forename = StringField('Forename', validators=[DataRequired()], render_kw={"placeholder": "Forename"})
    Surname = StringField('Surname', validators=[DataRequired()], render_kw={"placeholder": "Surname"})
    Username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    Email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    Password1 = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    Password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('Password1', message='Passwords must match')], render_kw={"placeholder": "Re-Enter Password"})
    Role = RadioField('Role', choices=[('Coach','Coach'), ('Player','Player')], default='Player')
    submit = SubmitField('Sign Up')

def generate_survey_form():
    class DynamicSurveyForm(FlaskForm):
        pass

    for category in RatingCategory.query.all():
        field_name = f'rating_{category.CategoryCode}'
        setattr(DynamicSurveyForm, field_name, IntegerField(f'{category.CategoryDescription}', validators=[DataRequired(), NumberRange(min=0, max=10)]))

    return DynamicSurveyForm