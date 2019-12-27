# Collection of helpers aka "Reusable components"

import dash
import dash_html_components as html
import pandas as pd

def generate_table(dataframe, max_rows=26):
    '''Formats a dataframe into html.Table components.
    Taken from: https://stackoverflow.com/questions/52213738/html-dash-table
    '''
    
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns]) ] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )