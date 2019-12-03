from flask import render_template, redirect, url_for, session, request
from sqlalchemy import text
from app import app, db
from app.tables import ResultsTable
from app.forms import FiltersForm
from app.models import Listing
from collections import OrderedDict
import pandas as pd


@app.route('/hello')
def hello():
    return "Hello, World!"


@app.route('/', methods=['GET', 'POST'])
def index():

    form = FiltersForm()
    geo_choices = [(r.geofence, r.geofence) for r in db.session.query(
        Listing.geofence).distinct() if r.geofence != None]
    geo_choices.append(('All', 'All'))
    form.geofence.choices = geo_choices

    if form.validate_on_submit():
        filters = []
        filters.append(('min_price', form.min_price.data))
        filters.append(('max_price', form.max_price.data))
        filters.append(('Region', form.geofence.data))
        filters = OrderedDict(filters)
        session['filters'] = filters

        return redirect(url_for('finds'))

    print(form.errors)

    return render_template('home.html', form=form, sub='Home')


@app.route('/plex/finds')
def finds():
    # If you make changes to the ouput, the ResultsTable class has to be modified in app/tables.py

    if session['filters'].get('Region') == 'All':
        geo_filter = 'geofence IS NULL'
    else:
        geo_filter = f"geofence = '{session['filters'].get('Region')}'"

    sql = text(f'''SELECT id,
                          centris_id,
                          category,
                          price,
                          centris_detail_url,
                          broker_detail_url,
                          geofence,
                          potential_revenue
                  FROM Listings
                  WHERE price between {session['filters'].get('min_price')} and
                                      {session['filters'].get('max_price')} and
                        {geo_filter}
                  ''')

    # Flask table way without pandas
    #results = db.engine.execute(sql)
    #items = [row for row in results]
    #table = ResultsTable(items)

    # Flask table with Pandas
    df = pd.read_sql(sql, db.engine)
    df['pt_revenue'] = df.potential_revenue/df.price
    df.sort_values('pt_revenue', inplace=True, ascending=False)
    #items = df.to_dict(orient='records')
    #table = ResultsTable(items)

    # Styling with Pandas
    # Still not sure which way to go with styling. Using Panda for now
    def hover(hover_color="#ffff99"):
        return dict(selector="tr:hover",
                    props=[("background-color", "%s" % hover_color)])
    styles = [
        hover(),
        dict(selector="th", props=[("font-size", "150%"),
                                   ("text-align", "center")]),
        dict(selector="caption", props=[("caption-side", "bottom")])
    ]


    def make_clickable(val):
        # target _blank to open new window
        return '<a target="_blank" href="{}">Link</a>'.format(val)

    table = df.style.set_table_styles(styles)\
                    .format({'pt_revenue': '{:.2%}'.format,
                             'price': '{:20,.0f}'.format,
                             'potential_revenue': '{:20,.0f}'.format,
                             'centris_detail_url': make_clickable,
                             'broker_detail_url': make_clickable
                             })\
                    .hide_index()\
                    .hide_columns('id')\
                    .render()

    return render_template('finds.html', table=table, sub='Listings')


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


@app.route('/dash')
def dash_table():
    return render_template('dash_table.html')