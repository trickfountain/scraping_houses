# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# Add flaskApp to path to import flask related modules
import sys
sys.path.append('/home/eric/scraping_houses/flaskApp')

from app.models import Listing
from app import app, db
from config import Config
import logging
import os




class ScraperPipeline(object):
    def open_spider(self, spider):
        logging.warning('Spider opened from Pipeline')

    def process_item(self, item, spider):
        scraped_at = item.pop('scraped_at')

        if not Listing.query.filter_by(centris_id=item['centris_id']).first():
            print(f'Centris # {item["centris_id"]} is a new listing')
            item['first_seen'] = scraped_at
            item['last_seen'] = scraped_at
            listing = Listing(**item)
            db.session.add(listing)

        else:
            print(f'Centris # {item["centris_id"]} already exists: updating last_seen')
            listing = Listing.query.filter_by(
                centris_id=item['centris_id']).first()
            listing.last_seen = scraped_at
            print(listing.last_seen, listing)
            db.session.commit()
            
        db.session.commit()


def close_spider(self, spider):
        db.session.commit()
        logging.warning('Spider closed by Pipeline')
