# -*- coding: utf-8 -*-
'''
    Scraper 2.0 April 2020.
    Largely taken from old plex, refactored with websites changes
    
    Starts with a get request to centris.ca/en which probably sets 
    a cookie for language = en.
'''

import scrapy
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
import json
import re
from re import sub
from decimal import Decimal
from datetime import datetime


class ListingsSpider(scrapy.Spider):
    name = 'centris'
    allowed_domains = ['www.centris.ca']

    position = {
        "startPosition": 0
    }
    # Set to False for full scrape
    MAX_LISTINGS = False

    script = '''
        function main(splash, args)
        splash:on_request(function(request)
            if request.url:find('css') then
                request.abort()
            end
        end)
        splash.images_enabled = false
        splash.js_enabled = false
        assert(splash:go(args.url))
        assert(splash:wait(0.5))
        return splash:html()
end
    '''
       
    query = {
            "query": {
                "FieldsValues": [
                    {
                        "fieldConditionId": "",
                        "fieldId": "SellingType",
                        "value": "Sale",
                        "valueConditionId": ""
                    },
                    ],
                "UseGeographyShapes": 0,
                "Filters": []
            },
            "isHomePage": True
        }
    
    def start_requests(self):
        ''' 
        Get on centris.ca/en to set en cookie.
        Not doing anything with response.
        '''

        yield scrapy.Request(
            url="https://www.centris.ca/en",
            method="GET",
            headers={
                'Content-Type': 'application/json',
            },
            callback=self.update_query
        )
    
    def update_query(self, response):
               
        yield scrapy.Request(
            url="https://www.centris.ca/property/UpdateQuery",
            method="POST",
            body=json.dumps(self.query),
            headers={
                'Content-Type': 'application/json',
            },
            callback=self.get_inscriptions
        )
    
    def get_inscriptions(self, response):
        yield scrapy.Request(
            url="https://www.centris.ca/Property/GetInscriptions",
            method="POST",
            body=json.dumps(self.position),
            headers={
                'Content-Type': 'application/json',
            },
            callback=self.parse_main
        )
        
    def parse_main(self, response):
        '''
        Parse a few fields from main page
        Send splash request for each listing
        Loop through pages using start_position incrementer
        '''
        
        resp_dict = json.loads(response.body)
        count = self.MAX_LISTINGS if self.MAX_LISTINGS else resp_dict.get('d').get('Result').get('count')
        html = resp_dict.get('d').get('Result').get('html')
        sel = Selector(text=html)
        listings = sel.xpath("//div[@class='shell']")
        increment_number = resp_dict.get('d').get(
            'Result').get('inscNumberPerPage')
        # incremet & pos just for debugging.
        meta = {
            # 'incrementNumber': increment_number,
            # 'startPosition': self.position['startPosition']
            }
        
        for listing in listings:
            meta['centris_id'] = listing.xpath('.//meta[@itemprop="sku"]/@content').get()
            meta['category'] = listing.xpath(".//span[@itemprop='category']/div/text()").get().strip().split('\xa0')[0]
            detail_url = listing.xpath(".//a[@class='a-more-detail']/@href").get()
            meta['centris_detail_url'] = f"https://www.centris.ca{detail_url}"
            meta['lat'] = listing.xpath('.//span[@class="ll-match-score noAnimation"]/@data-lat').get()
            meta['lng'] = listing.xpath('.//span[@class="ll-match-score noAnimation"]/@data-lng').get()
            
            yield SplashRequest(
                url=meta['centris_detail_url'],
                endpoint='execute',
                callback=self.parse_detailed,
                args={
                    'lua_source': self.script
                },
                meta=meta.copy(),
                dont_filter=True
            )

        if self.position['startPosition'] <= count:
            self.position['startPosition'] += increment_number

            yield scrapy.Request(
                url="https://www.centris.ca/Mvc/Property/GetInscriptions",
                method="POST",
                body=json.dumps(self.position),
                headers={
                    'Content-Type': 'application/json'
                },
                callback=self.parse_main
            )
            
    def parse_detailed(self, response):
        "Parse individual listing (result of splash request)"
        
        # meta has a lot of unwanted fields, specify what we want to keep
        meta_fields = ['centris_id', 'category', 'centris_detail_url', 'lat', 'lng',
                       #'startPosition', 'incrementNumber'
                       ]
        fields = {}
        for k in meta_fields:
            fields[k] = response.request.meta[k]

        # Get fields of interest in detailed page with xpath
        fields['price'] = response.xpath("//span[@itemprop='price']/@content").get()
        fields['address'] = response.xpath("//h2[@itemprop='address']/text()").get()
        fields['description'] = response.xpath("normalize-space(//div[@itemprop='description']/text())").get()
        fields['broker_details_url'] = response.xpath("//span[@id='DetailedSheetURL']/text()").get()
        pieces = response.xpath('//div[contains(@class, "piece")]/text()').get()
        fields['pieces'] = pieces.strip() if pieces else None
        sdb = response.xpath('//div[contains(@class, "sdb")]/text()').get()
        fields['sdb'] = sdb.strip() if sdb else None
        chambres = response.xpath('//div[contains(@class, "cac")]/text()').get()
        fields['chambres'] = chambres.strip() if chambres else None

        features = {}
        # Extract feature from table
        for sel in response.xpath('//div[@class="grid_3"]//div[@class="row"]/div'):
            key = sel.xpath('./div[@class="carac-title"]/text()').get('')
            key = key.strip() if key else None
            val = sel.xpath('./div[@class="carac-value"]/span/text()').get()
            val = val.strip() if key else None
            # Avoid adding None Keys
            if key:
                features[key] = val

        # Unpack features directly in main level
        fields.update(features)
        
        yield fields
