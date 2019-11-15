from flask import render_template, redirect, url_for, session, request
from sqlalchemy import text
from app import app, db
from app.tables import ResultsTable
from app.forms import FiltersForm
from app.models import Listing
from collections import OrderedDict


@app.route('/hello')    
def hello():
    return "Hello, World!"

@app.route('/', methods=['GET', 'POST'])
def index():
    
    form = FiltersForm()
    if form.validate_on_submit():
        filters = []
        filters.append(('min_price', form.min_price.data))
        filters.append(('max_price', form.max_price.data))
        filters = OrderedDict(filters)
        session['filters'] = filters

        return redirect(url_for('results'))
    
    print(form.errors)
    
    return render_template('home.html', form=form, sub='Home')



@app.route('/results')
def results():
    
    sql = text(f'''SELECT id, centris_id, category, price, centris_detail_url, broker_detail_url 
                  FROM Listings
                  WHERE price between {session['filters'].get('min_price')} and
                                      {session['filters'].get('max_price')}
                  ''')
    results = db.engine.execute(sql)
    items = [row for row in results]
    table = ResultsTable(items)
      
    return render_template('results.html', table=table, sub='Listings')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html', sub='Page not found :('), 404  


@app.route('/redirect', methods=['GET', 'POST'])
def redirect_page():
    
    link = request.args.get('link', None)
    
    if link:
        return redirect(link)
    else:
        return redirect(url_for('page_not_found', 404))
    
