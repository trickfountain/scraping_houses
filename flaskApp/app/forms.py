from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, IntegerField, StringField

class FiltersForm(FlaskForm):
    # min_units = IntegerField('Min Logements')
    # max_units = IntegerField('Max Logements')
    min_price = IntegerField('Prix minimum')
    max_price = IntegerField('Prix maximum')
    # region = SelectField(u"Lieux de recherche", choices=[('all', 'Tous'),
    #                                                      ('greater_mtl', 'Montreal & Banlieues'),
    #                                                      ('eastern_townships', "Cantons de l'est")])
    submit = SubmitField('Cherche les maisons !')
    