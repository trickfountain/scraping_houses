from flask_table import Table, Col, LinkCol
# All listings


class ListingsTable(Table):
    id = Col('id')
    centris_id = Col('centris_id')
    category = Col('category')
    price = Col('price')
    centris_detail_url = Col('centris_detail_url')
    broker_detail_url = Col('broker_detail_url')
    lat = Col('lat')
    lng = Col('lng')

# Only fields I want to see in the results page


class ResultsTable(Table):
    id = Col('Id', show=False)
    centris_id = Col('Centris ID', )
    category = Col('Category')
    price = Col('Price')
    centris_detail_url = LinkCol('Centris details', 'redirect_page',
                                 url_kwargs=dict(link='centris_detail_url')
                                 )
    broker_detail_url = LinkCol('Broker details', 'redirect_page',
                                url_kwargs=dict(link='broker_detail_url')
                                )
    geofence = Col('Region')
    potential_revenue = Col('Potential Revenue')
    pt_revenue = Col('% Revenue')