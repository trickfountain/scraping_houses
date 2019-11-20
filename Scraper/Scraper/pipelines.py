# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import logging
import os 
import sys
sys.path.append('~/scraping_houses')
from flaskApp.config import Config
from flaskApp.app import app, db
from flaskApp.app.models import Listing


class ScraperPipeline(object):
    def open_spider(self, spider):
        logging.warning('Spider opened from Pipeline')
    
    def process_item(self, item, spider):
        listing = Listing(item['centris_id'],
                    item['category'],
                    item['price'],
                    item['centris_detail_url'],
                    item['broker_detail_url'],
                    item['lat'],
                    item['lng'])

        db.session.add(listing)
        
    def close_spider(self, spider):
        db.session.commit()
        logging.warning('Spider closed by Pipeline')
