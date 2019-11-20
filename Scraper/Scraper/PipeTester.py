import sys
sys.path.append('/home/eric/scraping_houses/flaskApp/')
sys.path.append('/home/eric/scraping_houses/flaskApp/app')
import config
from app import app, db
from app.models import Listing
import json

with open('/home/eric/scraping_houses/data/commercialNov19.json') as f:
  items = json.load(f)
  
print(type(items))

print(items)


listing = Listing(" ".join(item['centris_id'].split()),
                  item['category'],
                  item['price'],
                  item['centris_detail_url'],
                  item['city'],
                  item['lat'],
                  item['lng'])


#db.session.add(listing)
# db.session.commit()

all = db.query.all()
print(all[0])

# Get the listing
i = Listing.query.filter_by(centris_id='11269851').first()
	
from datetime import datetime
# Update last_seen
i.last_seen = datetime.utcnow().strftime("%d-%b-%Y (%H:%M:%S.%f)")

# Then simply commit.