from flask import Flask, render_template, request, session, url_for, redirect
from forms import FiltersForm
from dotenv import load_dotenv
from collections import OrderedDict 
import os
from flask_sqlalchemy import SQLAlchemy
from flask_table import Table, Col
from db_setup import Listing, db
import json

class ListingsTable(Table):
    id = Col('id')
    centris_id = Col('centris_id')
    category = Col('category')
    price = Col('price')
    centris_detail_url = Col('centris_detail_url')
    broker_detail_url = Col('broker_detail_url')
    lat = Col('lat')
    lng = Col('lng')
    
load_dotenv('.env')
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# db config
app.config['SQLALCHEMY_DATABASE_URI'] : 'sqlite:///'+os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



@app.route('/', methods=['GET', 'POST'])
def index():
    
    form = FiltersForm()
    if form.validate_on_submit():
        filters = []
        filters.append(('min_price', form.min_price.data))
        filters.append(('max_price', form.max_price.data))
        filters.append(('min_units', form.min_units.data))
        filters.append(('min_units', form.min_units.data))
        
        session['filters'] = filters

        return redirect(url_for('results'))
    
    print(form.errors)
    
    return render_template('home.html', form=form)

@app.route('/results')
def results():
    items = Listing.query.all()
    table = ListingsTable(items)
      
    return render_template('results.html', table=table)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404  

if __name__ == "__main__":
    app.run(debug=True)