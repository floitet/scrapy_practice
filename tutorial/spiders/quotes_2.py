# -*- coding: utf-8 -*-
import scrapy


class Quotes2Spider(scrapy.Spider):
    name = 'quotes_2'
    custom_settings = {
        'ITEM_PIPELINES': {
            'tutorial.pipelines.TutorialPipeline': 300,
        }
    }
    start_urls = ['http://quotes.toscrape.com/random', 'http://quotes.toscrape.com/random']

    def parse(self, response):
        new_dict = {'author': (response.css('.author::text').get(),), 'quote': (response.css('.text::text').get(),),
                    'tags': response.css('.tag::text').getall()}
        return new_dict
