import scrapy
import json


class ParserSpider(scrapy.Spider):
    name = 'corona'
    start_urls = ['https://coronavirus.zone/']
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "cookie": "_ga=GA1.2.455129480.1584806707; _gid=GA1.2.2049382574.1584806707; _gat_gtag_UA_156896841_1=1",
        "pragma": "no-cache",
        "referer": "https://coronavirus.zone/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/80.0.3987.149 Safari/537.36"
    }

    def parse(self, response):
        url = 'https://coronavirus.zone/data.json?1584893476207'

        yield scrapy.Request(url,
                             callback=self.parse_stats,
                             headers=self.headers)

    def parse_stats(self, response):
        raw_data = response.body
        data = json.loads(raw_data)
        self.log(type(data))
        for rec in data:
            yield {
                'region': rec['region'],
                'cases': rec['cases'],
                'deaths': rec['death']
            }
