import sys
sys.path.append('/home/eric/scraping_houses/flaskApp')
sys.path.append('/home/eric/scraping_houses')

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
from helpers.taxes import TaxBrackets, tax_calculator

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

df['welcome_tax'] = tax_calculator(df,
                        TaxBrackets.welcome_tax.get('Montreal'),
                        ).loc[:,'total']


df['school_tax'] = tax_calculator(df,
                        TaxBrackets.school_tax.get('Montreal'),
                        ).loc[:,'total']

df['property_tax'] = tax_calculator(df,
                        TaxBrackets.property_tax.get('Montreal'),
                        ).loc[:,'total']

print(df.head())