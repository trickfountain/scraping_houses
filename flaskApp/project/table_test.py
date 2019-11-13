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
    
items = Listing.query.all()

table = ListingsTable(items)

print(table.__html__())