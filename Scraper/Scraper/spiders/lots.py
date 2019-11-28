# -*- coding: utf-8 -*-
import scrapy


class LotsSpider(scrapy.Spider):
    name = 'lots'
    allowed_domains = ['basic']
    start_urls = ['http://basic/']

    def parse(self, response):
        pass
