from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import InputRequired, DataRequired, NumberRange
from wtforms import SelectField, StringField, SubmitField
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

