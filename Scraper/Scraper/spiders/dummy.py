# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
import json
import re
from re import sub
from decimal import Decimal
from datetime import datetime

'''
    Sandbox generator: Fake spider to create output that can be used in Jupyter Notebook
    to confirm xpath selection.
    
    For the centris project I am crawling some pages with Scrapy (main pages) some with Splash
    (detailed listing) so this crawler generates one page of each type.
'''

class ListingsSpider(scrapy.Spider):
    name = 'dummy'
    allowed_domains = ['www.centris.ca']

    position = {
        "startPosition": 0
    }

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

    def start_requests(self):
        print('STARTING DUMMY SPIDER: EXPECTING TWO PAGES')
        query = {
            "queryView": {
                "Filters": [],
                "FieldsValues": [
                    {
                        "fieldId": "PropertyType",
                        "value": "MultiFamily"
                    },
                    {
                        "fieldId": "Category",
                        "value": "Commercial"
                    },
                    {
                        "fieldId": "SellingType",
                        "value": "Sale"
                    },
                    {
                        "fieldId": "NumberUnits",
                        "value": "2"
                    },
                    {
                        "fieldId": "NumberUnits",
                        "value": "8"
                    },
                    {
                        "fieldId": "SalePrice",
                        "value": 0
                    },
                    {
                        "fieldId": "SalePrice",
                        "value": 50000000
                    }
                ]
            },
            "isHomePage": True
        }

        yield scrapy.Request(
            url="https://www.centris.ca/mvc/property/UpdateQuery",
            method="POST",
            body=json.dumps(query),
            headers={
                'Content-Type': 'application/json'
            },
            callback=self.update_query
        )

    def update_query(self, response):
        yield scrapy.Request(
            url="https://www.centris.ca/Mvc/Property/GetInscriptions",
            method="POST",
            body=json.dumps(self.position),
            headers={
                'Content-Type': 'application/json'
            },
            callback=self.parse
        )

    def parse(self, response):
        resp_dict = json.loads(response.body)
        
        yield resp_dict
        count = resp_dict.get('d').get('Result').get('count')
        html = resp_dict.get('d').get('Result').get('html')
        sel = Selector(text=html)
        listings = sel.xpath("//div[@class='shell']")

        # Get detail from 1st listing, we just want one page.
        detail_url = listings[0].xpath(".//a[@class='a-more-detail']/@href").get()
        centris_detail_url = f"https://www.centris.ca{detail_url}"
        
        print('-------> Sending request for ', centris_detail_url)
        
        meta = {'centris_detail_url': centris_detail_url}
            
        yield SplashRequest(
            url=centris_detail_url,
            endpoint='execute',
            callback=self.parse_summary,
            args={
                'lua_source': self.script
            },
            meta=meta
        )


    def parse_summary(self, response):
        yield {'html': response.text,
               'link used for request (centris_detail_url)' : response.request.meta['centris_detail_url']}