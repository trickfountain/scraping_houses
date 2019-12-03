# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/eric/scraping_houses/flaskApp')

import pandas as pd
import dash_table
import json
from dash.dependencies import Input, Output
from sqlalchemy import text
from app import db
from app.models import Listing, Fence
import dash
import dash_core_components as dcc
import dash_html_components as html



# Getting data from SQLite
sql = text(f'''SELECT id,
                      centris_id,
                      category,
                      price,
                      geofence,
                      potential_revenue,
                      residential_units,
                      commercial_units,
                      unites_residentielles,
                      unite_principale,
                      centris_detail_url,
                      broker_detail_url
                  FROM Listings
                  ''')

df = pd.read_sql(sql, db.engine)
df['pt_revenue'] = df.potential_revenue/df.price
df = df.astype({'residential_units': float,
                'commercial_units': float})

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


region_choices = []

for row in db.session.query(Fence.area_name).distinct():
    if row.area_name != None:
        region_choices.append({'label': row.area_name, 'value': row.area_name})
region_choices.append({'label': 'All', 'value': 'All'})

app.layout = html.Div(children=[
    html.H1('WoW belle table Wow',
            id='header',),
    html.Div([
        html.Div([html.H6('Region'
                             ),
                  dcc.Dropdown(id='Region',
                               options=region_choices,
                               value='All'
                               )],
                 id='div_region',),
        html.Div([html.H6('Price', className='filter-sub'),
                  html.Div([html.Label('Min Price'),
                            dcc.Input(id='min_price',
                                      value=300000, type='number'),
                            html.Label('max Price'),
                            dcc.Input(id='max_price',
                                      value=5000000, type='number'),
                            ], className='sub-select2')],
                 id='price-sel',),
        html.Div([html.H6('Residential units', className='filter-sub'),
                  html.Div([html.Label('Min units'),
                            dcc.Input(id='min_units', value=2, type='number'),
                            html.Label('max units'),
                            dcc.Input(id='max_units', value=10, type='number'),
                            ], id='res-units-sel',
                           className='sub-select2')],
                 ),
    ], id='filters',
        className="dropdown"),
    html.Div(id='Results'),
]
)

@app.callback(
    Output('Results', 'children'),
    [Input('Region', 'value'),
     Input('min_price', 'value'),
     Input('max_price', 'value'),
     Input('min_units', 'value'),
     Input('max_units', 'value')
     ]

)
def update_results(Region, min_price, max_price, min_units, max_units):
    if Region == 'All':
        filt_df = df
    else:
        filt_df = df[df.geofence == Region]

    filt_df = filt_df[filt_df.price.between(min_price, max_price)]
    filt_df = filt_df[filt_df.residential_units.between(min_units, max_units)]

    return dash_table.DataTable(
        id='listings',
        columns=[{"name": i, "id": i, "deletable": False, "selectable": True}
                 for i in filt_df.columns],
        data=filt_df.to_dict('records'),
        sort_action='native',
        page_size=20,
    )


# Don't use the same ones than for the website
PORT = 8080

if __name__ == '__main__':
    app.run_server(port=PORT,
                   debug=True)
