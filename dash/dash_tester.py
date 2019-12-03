import dash_table
import json
import sys
sys.path.append('/home/eric/scraping_houses/flaskApp')
import pandas as pd
from dash.dependencies import Input, Output
from sqlalchemy import text
from app import db
from app.models import Listing, Fence
import dash_html_components as html
import dash_core_components as dcc
import dash


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
df = df.astype({'residential_units':float,
           'commercial_units': float})

nulls = df[df.residential_units.between(1,2)].residential_units
t = [i for i in df.residential_units if type(i) == str]

print(nulls)