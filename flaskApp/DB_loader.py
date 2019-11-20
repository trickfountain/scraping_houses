# Rudimentary loader to go from json into db.
# Should look at CLI options (sqlite3 is installed on your laptop) for bigger files

from app.models import Listing
from app import db
import json

with open('/home/eric/scraping_houses/data/commercialNov19.json') as f:
    items = json.load(f)

# Create
for item in items[0:3]:
    scraped_at = item.pop('scraped_at')
    item['first_seen'] = scraped_at
    item['last_seen'] = scraped_at
    listing = Listing(**item)
    
    db.session.add(listing)
    print(listing)

# db.session.commit()

# # READ
# all_listings = Listing.query.all()

# # Clean database.
# for l in all_listings:
#     db.session.delete(l)
    
