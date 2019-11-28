from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, IntegerField, StringField

class FiltersForm(FlaskForm):
    min_price = IntegerField('Prix minimum', default=0)
    max_price = IntegerField('Prix maximum', default=2000000)
    geofence = SelectField(u"Lieux de recherche", choices=[])
    submit = SubmitField('Cherche les maisons !')
    