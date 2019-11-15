# Rudimentary loader to go from json into db.
# Should look at CLI options (sqlite3 is installer on your laptop) for bigger files

from db_setup import Listing, db
import json

with open("/home/eric/scraping_houses/data/sample.json") as f:
   data = json.loads(f.read())

# Create
for js in data:
    listing = Listing(js['centris_id'],
                      js['category'],
                      js['price'],
                      js['centris_detail_url'],
                      js['broker_detail_url'],
                      js['lat'],
                      js['lng'])
    
    db.session.add(listing)

db.session.commit()

# READ
all_= Listing.query.all()