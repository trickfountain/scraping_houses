# -*- coding: utf-8 -*-
import sys
sys.path.append('/home/eric/scraping_houses/flaskApp')
sys.path.append('/home/eric/scraping_houses')

from helpers.dash_helpers import generate_table
from helpers.taxes import TaxBrackets, tax_calculator
from helpers.utils import monthly_payments
import dash_html_components as html
import dash_core_components as dcc
import dash
from app.models import Listing, Fence
from app import db
from sqlalchemy import text
from dash.dependencies import Input, Output
import json
import dash_table
import pandas as pd


# Getting data from SQLite
sql = text(f'''SELECT id,
                      centris_id,
                      category,
                      city,
                      price,
                      geofence,
                      potential_revenue,
                      coalesce(residential_units, 0) as residential_units,
                      coalesce(commercial_units, 0) as commercial_units,
                      address,
                      unites_residentielles,
                      unite_principale,
                      centris_detail_url,
                      broker_detail_url,
                      first_seen,
                      last_seen
                FROM Listings
                  ''')

df = pd.read_sql(sql, db.engine)
df['% Revenue'] = df.apply(lambda x: '{:.1%}'.format(
    x.potential_revenue/x.price), axis=1)
df['Potential Revenue'] = round(df.potential_revenue/12, 0)
df = df.astype({'residential_units': float,
                'commercial_units': float})

df['welcome_tax'] = tax_calculator(df,
                                   TaxBrackets.welcome_tax.get('Montreal'),
                                   ).loc[:, 'total']

df['school_tax'] = tax_calculator(df,
                                  TaxBrackets.school_tax.get('Montreal'),
                                  ).loc[:, 'total']

df['property_tax'] = tax_calculator(df,
                                    TaxBrackets.property_tax.get('Montreal'),
                                    ).loc[:, 'total']

# Convert to date & format
df.last_seen = pd.to_datetime(df.last_seen, infer_datetime_format=True)
df.first_seen = pd.to_datetime(df.first_seen, infer_datetime_format=True)

# Create days on market col
df['Days on market'] = df.last_seen - df.first_seen
df['Days on market'] = df['Days on market'].dt.days

# Format for humans
df.last_seen = df.last_seen.dt.strftime("%d %b %Y")
df.first_seen = df.first_seen.dt.strftime("%d %b %Y")

# Show the following columns in the datatable
show_cols = ['centris_id', 'city', 'price', 'Potential Revenue', '% Revenue',
             'category', #'residential_units', 'commercial_units',
             'first_seen', 'last_seen', 'Days on market'
             ]

external_stylesheets = ['/assets/dash_listings1.css','https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets[0:])

region_choices = []

for row in db.session.query(Fence.area_name).distinct():
    if row.area_name != None:
        region_choices.append({'label': row.area_name, 'value': row.area_name})
region_choices.append({'label': 'All', 'value': 'All'})


### Page header ###
# main_header = html.H1('WoW belle table Wow redux', id='header')

### Filter section ###
filter_header = html.H3("Listings filters")
filter_region = html.Div([
    html.Label('Region'),
    dcc.Dropdown(id='Region', options=region_choices, value='All',),
    ],className='filter')

filter_price = html.Div([
    html.Label('Price'),
    html.Div([
        html.Div([
            html.Span('Min Price ( k $ )'),
            dcc.Input(id='min_price',
                    value=300, type='number'),
        ], className='sub-multi'),
        html.Div([
            html.Span('Max Price ( k$ )'),
            dcc.Input(id='max_price', value=2000, type='number',)
        ], className='sub-multi'),
    ], className='multi-select-container'),
], className='filter')

filter_res_units = html.Div([
    html.Label('Residential units'),
    html.Div([
        html.Div([
            html.Span('Min units'),
            dcc.Input(id='min_units', value=2, type='number'),
        ], className='sub-multi'),
        html.Div([
            html.Span('Max units'),
            dcc.Input(id='max_units', value=10, type='number'),
        ], className='sub-multi')
    ], className='multi-select-container'),
], className='filter')

filter_com_units = html.Div([
    html.Label('Commercial units'),
    html.Div([
        html.Div([
            html.Span('Min units'),
            dcc.Input(id='min_comm_units', value=0, type='number'),
        ], className='sub-multi'),
        html.Div([
            html.Span('Max units'),
            dcc.Input(id='max_comm_units', value=2, type='number'),
        ], className='sub-multi')
    ], className='multi-select-container'),
], className='filter')

filter_section = html.Div(
    [filter_header,
        html.Div(
            [filter_region,
            filter_price,
            filter_res_units,
            filter_com_units
        ], id='filters-box'),
    ], id='filters-section')

### User input section (UI) ####
ui_header = html.H3('Additional inputs')

ui_interest_rate = html.Div([
                    html.Label('interest rate', className='input-label'),
                    dcc.Input(id='interest_rate',
                              value=2.8,
                              type='number',
                              ),
                    ])

ui_amortization = html.Div([
                    html.Label('amortization'),
                    dcc.Input(id='amortization',
                              value=25,
                              type='number')
                ],)

ui_maintenance_rate = html.Div([
                    html.Label('maintenance rate', className='input-label'),
                    dcc.Input(id='maintenance_rate',
                              value=1,
                              type='number'),
                    ])

ui_cashdown = html.Div([
            html.Label('cashdown'),
            dcc.Input(id='cashdown',
                      value=0,
                      type='number')
                    ])

ui_RAP = html.Div([
            html.Label('RAP'),
            dcc.Input(id='RAP',
                        value=0,
                        type='number')
                    ])

ui_monthly_revenue = html.Div([
            html.Label('Monthly revenue'),
            dcc.Input(id='ui_monthly_revenue',
                        value=0,
                        type='number')]
)

ui_renos =  html.Div([
    html.Label('Renos'),
    dcc.Input(id='renos',
              value=0,
              type='number')
                ]
)

ui_section = html.Div([
    ui_header,
    html.Div([
        ui_interest_rate,
        ui_amortization,
        ui_cashdown,
        ui_RAP,
        ui_monthly_revenue,
        ui_renos,
        ui_maintenance_rate
    ], id='user-input' )
], id='ui-section')

### more info section ###
info_header = html.H3( id='title_more_info')
centris_id = html.Div([
    html.Label("Centris ID"),
    dcc.Markdown(id='sel_centris_id')
    ], className='info')

detail_url = html.Div([
    html.Label('centris detail page'),
    dcc.Markdown(id='sel_centris_detail_url'),
    ], className='info')

broker_url = html.Div([
    html.Label('broker page'),
    dcc.Markdown(id='sel_broker_detail_url'),
    ], className='info')

first_year_expense = html.Div([
    html.Label('First year expenses'),
    html.Div(id='first_year_expenses'),
    ], className='info')

cashflow = html.Div([
    html.Label('cashflow'),
    html.Div(id='cashflow'),
    ], className='info')

address = html.Div([
    html.Label('address'),
    html.Div(id='address'),
    ], className='info')

unite_principale = html.Div([
    html.Label('unité principale'),
    html.Div(id='unite_principale'),
    ], className='info')

unites_residentielles = html.Div([
    html.Label('unités residentielles'),
    html.Div(id='unites_residentielles'),
    ], className='info')

info_section = html.Div([
    info_header,
    # box for info
    html.Div([
        centris_id,
        cashflow,
        first_year_expense,
        unite_principale,
        unites_residentielles,
        address,
        detail_url,
        broker_url,
    ] )
], id='more-info-section')

### listings table ###
listings_table = dash_table.DataTable(
    id='listings',
    # See show_cols at the top of the script
    columns=[{"name": i, "id": i} for i in show_cols],
    style_cell={
        'minWidth': '0px', 'maxWidth': '180px',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
    },
    sort_action='native',
    page_size=25,
    row_selectable="single",
    selected_rows=[],
    filter_action="native",
)

### Layout ###
app.layout = html.Div([
    # main_header,
    html.Div([
        info_section,
        html.Div([
            filter_section,
            ui_section,
            listings_table
        ], className='result-block'),
    ], id='page-box'),
], )


# listings table
@app.callback(
    Output('listings', 'data'),
    [Input('Region', 'value'),
     Input('min_price', 'value'),
     Input('max_price', 'value'),
     Input('min_units', 'value'),
     Input('max_units', 'value'),
     Input('min_comm_units', 'value'),
     Input('max_comm_units', 'value'),
     ])

def update_results(Region,
                   min_price,
                   max_price,
                   min_units,
                   max_units,
                   min_comm_units,
                   max_comm_units
                ):

    min_price *= 1000
    max_price *= 1000
    
    if Region == 'All':
        filt_df = df
    else:
        filt_df = df[df.geofence == Region]

    filt_df = filt_df[filt_df.price.between(min_price, max_price)]
    filt_df = filt_df[filt_df.residential_units.between(min_units, max_units)]
    filt_df = filt_df[filt_df.commercial_units.between(
        min_comm_units, max_comm_units)]

    return filt_df.to_dict('records')

# more info section 
@app.callback(
    [
     Output('title_more_info', 'children'),
     Output('sel_centris_id', 'children'),
     Output('sel_centris_detail_url', 'children'),
     Output('sel_broker_detail_url', 'children'),
     Output('first_year_expenses', 'children'),
     Output('cashflow', 'children'),
     Output('address', 'children'),
     Output('unite_principale', 'children'),
     Output('unites_residentielles', 'children')
    ],
    [
     Input('listings', "derived_virtual_data"),
     Input('listings', "derived_virtual_selected_rows"),
     Input('interest_rate', "value"),
     Input('amortization', "value"),
     Input('maintenance_rate', "value"),
     Input('renos', "value"),
     Input('cashdown', "value"),
     Input('RAP', "value"),
     Input('ui_monthly_revenue', "value"),
     ]
)

def update_more_info(rows,
                     selected_rows,
                     rate,
                     amortization,
                     maintenance_rate,
                     renos,
                     cashdown,
                     RAP,
                     m_revenue
                    ):

    if not selected_rows:
        return ('Make a selection to get more details on a listing',
                None, None , None , None, None, None, None, None
                )

    else:
        df = pd.DataFrame(rows)
        sel_row = df.loc[selected_rows[0], :]
        centris_id = sel_row.centris_id
        centris_detail_url = sel_row.centris_detail_url
        broker_detail_url = sel_row.broker_detail_url
        
        if m_revenue not in [0, None]:
            potential_revenue = m_revenue*12
        else:
            potential_revenue = sel_row.potential_revenue / 12
        
        # Cashflow calculations
        mortgage = monthly_payments((sel_row.price - cashdown - RAP),
                                    interest_rate=rate, amortization=amortization)
        
        building_maintenance = maintenance_rate/100 * sel_row.price
        annual_fees = sel_row.school_tax + sel_row.property_tax + building_maintenance
        cashflow = potential_revenue - mortgage - (annual_fees/12)
        first_year_expense = renos + sel_row.welcome_tax
        
        # Property details
        address = sel_row.address
        unite_principale = sel_row.unite_principale
        unites_residentielles = sel_row.unites_residentielles


        return ("More info",
                f"{centris_id}",
                f"[link]({centris_detail_url})",
                f"[link]({broker_detail_url})",
                "$ {:10,.0f}".format(first_year_expense),
                "$ {:10,.0f}".format(cashflow),
                address,
                unite_principale,
                unites_residentielles
                )


# Don't use the same ones than for the website
PORT = 8080

if __name__ == '__main__':
    app.run_server(port=PORT,
                   debug=True)
