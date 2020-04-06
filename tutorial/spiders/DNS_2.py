class QuotesSpider(scrapy.Spider):
    name = "dns"
    start_urls = ['https://www.dns-shop.ru/catalog/17a8a01d16404e77/smartfony/']

    def parse(self, response):