# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
import json
import re
from re import sub
from decimal import Decimal
from datetime import datetime


def clean(s):
    s = s.replace('\n', ' ')
    s = " ".join(s.split())
    return s

def clean_money(s_money):
    s = s_money.replace('$', '').replace(' ', '').replace(',', '')
    return s

class ListingsSpider(scrapy.Spider):
    name = 'plex'
    allowed_domains = ['www.centris.ca']

    custom_settings = {
        # 'ITEM_PIPELINES': {'Scraper.pipelines.PlexPipeline': 300,}
    }

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
        count = resp_dict.get('d').get('Result').get('count')
        html = resp_dict.get('d').get('Result').get('html')
        sel = Selector(text=html)
        listings = sel.xpath("//div[@class='shell']")
        
        for i, listing in enumerate(listings):
            listing_number = f"{self.position['startPosition'] + i}/{count}"
            centris_id = listing.xpath(
                './/meta[@itemprop="sku"]/@content').get()
            category = listing.xpath(
                ".//span[@itemprop='category']").get()
            title = listing.xpath(
                ".//div[@class='description']/p[@class='features border']/span/span/text()").get()
            city = listing.xpath(
                ".//div[@class='description']/p[@class='address']/span/text()").get()
            detail_url = listing.xpath(
                ".//a[@class='a-more-detail']/@href").get()
            centris_detail_url = f"https://www.centris.ca{detail_url}"
            lat = listing.xpath(
                './/span[@class="ll-match-score noAnimation"]/@data-lat').get()
            lng = listing.xpath(
                './/span[@class="ll-match-score noAnimation"]/@data-lng').get()

            #print(f'Expecting SplashRequest for:\n   --> {centris_detail_url}')
            
            meta =  {
                'listing_number': listing_number,
                'centris_id': centris_id,
                'cat': category,
                'title': title,
                'city': city,
                'centris_detail_url': centris_detail_url,
                'lat': lat,
                'lng': lng
                }
            
            #yield meta
            
            
            yield SplashRequest(
                url=centris_detail_url,
                endpoint='execute',
                callback=self.parse_summary,
                args={
                    'lua_source': self.script
                },
                meta=meta
            )

        increment_number = resp_dict.get('d').get(
            'Result').get('inscNumberPerPage')

        if self.position['startPosition'] <= count:
            self.position['startPosition'] += increment_number

            yield scrapy.Request(
                url="https://www.centris.ca/Mvc/Property/GetInscriptions",
                method="POST",
                body=json.dumps(self.position),
                headers={
                    'Content-Type': 'application/json'
                },
                callback=self.parse
            )

    def parse_summary(self, response):
        print('**SPLASH** : Parsing Summary page from Splash Request')
        # Fields from main page
        category = response.request.meta['cat']
        title = response.request.meta['title']
        city = response.request.meta['city']
        centris_detail_url = response.request.meta['centris_detail_url']
        lat = response.request.meta['lat']
        lng = response.request.meta['lng']
        centris_id = response.request.meta['centris_id']
        listing_number = response.request.meta['listing_number']

        # Fields from summary page
        price = response.xpath("//span[@itemprop='price']/@content").get()
        address = response.xpath("//h2[@itemprop='address']/text()").get()
        postal_code = re.search(
            r"[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d", address).group()
        description = response.xpath(
            "normalize-space(//div[@itemprop='description']/text())").get()
        broker_details_url = response.xpath(
            "//span[@id='DetailedSheetURL']/text()").get()
        tables = response.xpath(
            '//h3[text()="Caractéristiques"]/following-sibling::table')
        features = {}

        potential_revenue = None

        for table in tables:
            col1 = table.xpath('.//tr/td/text()').getall()
            col2 = table.xpath('.//tr/td/span/text()').getall()

            for feat, val in (zip(col1, col2)):
                if any(rev in feat for rev in ['revenue', 'Revenus']):
                    val = clean_money(val)
                    try:
                        potential_revenue = val
                    except:
                        feat, val = clean(feat), clean(val)
                        features.update({feat: val})
                else:
                    feat, val = clean(feat), clean(val)
                    features.update({feat: val})

        scraped_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        residential_units = None
        commercial_units = None
        if features.get('Nombre d’unités'):
            for s in features.get('Nombre d’unités').split(","):
                # Matching for residentiel 
                search = re.search(r'r?sid.*\s\(([0-9])\)', s, re.IGNORECASE)
                if search:
                    residential_units = search.group(1)
                # Matching for commercial
                search = re.search(r'mmer.*\(([0-9])\)', s, re.IGNORECASE)
                if search:
                    commercial_units = search.group(1)
                    
        unites_residentielles = features.get('Unités résidentielles')
        unite_principale = features.get('Unité principale')

        yield {
            'listing_number': listing_number,
            'centris_id': centris_id,
            'category': category,
            'title': clean(title),
            'price': price,
            'city': city,
            'centris_detail_url': centris_detail_url,
            'broker_detail_url': broker_details_url,
            'lat': lat,
            'lng': lng,
            'address': clean(address),
            'postal_code': postal_code,
            'description': clean(description),
            'potential_revenue': potential_revenue,
            'residential_units': residential_units,
            'commercial_units': commercial_units,
            'unites_residentielles': unites_residentielles,
            'unite_principale': unite_principale,
            'features': json.dumps(features),
            'scraped_at': scraped_at
        }
