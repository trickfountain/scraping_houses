import sys
sys.path.append('/home/eric/scraping_houses/flaskApp/')
sys.path.append('/home/eric/scraping_houses/flaskApp/app')
import config
from app import app, db
from app.models import Listing
import json
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np

import re

with open('/home/eric/scraping_houses/data/plex_sample.json') as f:
  items = json.load(f)

feats = json.loads(items[1]['features'])

residential_units = None
commercial_units = None

if feats.get('Nombre d’unité'):
  for s in feats['Nombre d’unités'].split(","):
    # Matching for residentiel 
    search = re.search('r?sid.*\s\(([0-9])\)', s, re.IGNORECASE)
    if search:
      residential_units = search.group(1)
    # Matching for commercial
    search = re.search('mmer.*\(([0-9])\)', s, re.IGNORECASE)
    if search:
      commercial_units = search.group(1)
