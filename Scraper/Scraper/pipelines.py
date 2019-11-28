# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# Add flaskApp to path to import flask related modules
import sys
sys.path.append('/home/eric/scraping_houses/flaskApp')
from app.models import Listing, Fence
from app import app, db
from config import Config
import logging, os, json
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np


class PlexPipeline(object):
    
    fences = []
    for fence in Fence.query.all():
        name = fence.area_name
        coords = json.loads(fence.coords)
        lats, lons = coords['lat'], coords['lng']
        Pol = Polygon(list(zip(lats, lons)))
        fences.append((name, Pol))

    def open_spider(self, spider):
        logging.warning('Spider opened from Pipeline')
        print(f'Starting pipeline, detected {len(self.fences)} geofences')  

    def process_item(self, item, spider):
        scraped_at = item.pop('scraped_at')

        if not Listing.query.filter_by(centris_id=item['centris_id']).first():
            print(f'Centris # {item["centris_id"]} is a new listing')
            item['first_seen'] = scraped_at
            item['last_seen'] = scraped_at
            
            listing_point = Point(float(item['lat']), float(item['lng']))
            for fence_name, Pol in self.fences:
                fence_check = fence_name if listing_point.within(Pol) else None
            
            item['geofence'] = fence_check
            listing = Listing(**item)
            db.session.add(listing)
            db.session.commit()
            
        else:
            print(f'Centris # {item["centris_id"]} already exists: updating last_seen')
            listing = Listing.query.filter_by(
                centris_id=item['centris_id']).first()
            listing.last_seen = scraped_at
            db.session.commit()
            
        db.session.commit()

    def close_spider(self, spider):
            db.session.commit()
            logging.warning('Spider closed by Pipeline')


# class LotsPipeline(object):
#     def open_spider(self, spider):
#         logging.warning('------>>>> DONT USE THIS SPIDER ITS JUST A TEST <<<<------')



#     def close_spider(self, spider):
#         db.session.commit()
#         logging.warning('Spider closed by Pipeline')
