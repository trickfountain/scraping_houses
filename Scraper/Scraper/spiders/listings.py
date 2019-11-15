# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
import json


class ListingsSpider(scrapy.Spider):
    name = 'commercial'
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
        listings = sel.xpath("//div[@class='row templateListItem']")
        
        for i, listing in enumerate(listings):
            list_no= f"{self.position['startPosition'] + i}/{count}"
            centris_id = listing.xpath('.//meta[@itemprop="sku"]/@content').get()
            category = listing.xpath(
                ".//div[@class='description']/h2/span/text()").get()
            sub = listing.xpath(
                ".//div[@class='description']/p[@class='features border']/span/span/text()").get()
            price = listing.xpath(
                ".//div[@class='description']/p[@class='price']/span/text()").get()
            city = listing.xpath(
                ".//div[@class='description']/p[@class='address']/span/text()").get()
            url = listing.xpath(".//a[@class='btn a-more-detail']/@href").get()
            abs_url = f"https://www.centris.ca{url}"
            lat = listing.xpath(
                './/span[@class="ll-match-score noAnimation"]/@data-lat').get()
            lng = listing.xpath(
                './/span[@class="ll-match-score noAnimation"]/@data-lng').get()

            yield SplashRequest(
                url=abs_url,
                endpoint='execute',
                callback=self.parse_summary,
                args={
                    'lua_source': self.script
                },
                meta={
                    'list_no': list_no,
                    'centris_id': centris_id,
                    'cat': category,
                    'sub': sub,
                    'pri': price,
                    'city': city,
                    'url': abs_url,
                    'lat': lat,
                    'lng': lng}
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
        # Fields from main page
        category = response.request.meta['cat']
        sub = response.request.meta['sub']
        price = response.request.meta['pri']
        city = response.request.meta['city']
        url = response.request.meta['url']
        lat = response.request.meta['lat']
        lng = response.request.meta['lng']
        centris_id = response.request.meta['centris_id']
        list_no = response.request.meta['list_no']
        
        # Fields from summary page
        address = response.xpath("//h2[@itemprop='address']/text()").get()
        description = response.xpath(
            "normalize-space(//div[@itemprop='description']/text())").get()
        DetailedSheetURL = response.xpath("//span[@id='DetailedSheetURL']/text()").get()
        tables = response.xpath('//h3[text()="Caractéristiques"]/following-sibling::table')
        features = {}
        for table in tables:
            col1 = table.xpath('.//tr/td/text()').getall()
            col2 = table.xpath('.//tr/td/span/text()').getall()

            features.update(dict(list(zip(col1, col2))))

        yield {
            'list_no': list_no,
            'centris_id': centris_id,
            'category': category,
            'sub': sub,
            'price': price,
            'city': city,
            'url': url,
            'lat': lat,
            'lng': lng,
            'address': address,
            'description': description,
            'features': features
        }
