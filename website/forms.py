from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import InputRequired, NumberRange
from wtforms import SelectField
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

# class UserRatingForm(FlaskForm):
#     rater_id = IntegerField('Rater ID', validators=[InputRequired()])
#     ratee_id = IntegerField('Ratee ID', validators=[InputRequired()])
#     rating_category = IntegerField('Rating Category', validators=[InputRequired()])
#     value = IntegerField('Value', validators=[InputRequired()])
