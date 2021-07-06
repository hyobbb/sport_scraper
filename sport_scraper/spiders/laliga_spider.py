import scrapy
import json


class LaligaScheduleSpider(scrapy.Spider):
    name = "laliga"
    allowed_domains = ['laliga.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'sport_scraper.pipelines.SportScraperPipeline': 300,
        }
    }

    def __init__(self, start_week=1, end_week=2):
        self.start_week = start_week
        self.end_week = end_week

    def start_requests(self):
        urls = [
            f'https://www.laliga.com/en-ES/laliga-santander/results/2020-21/gameweek-{week}'
            for week in range(self.start_week, self.end_week)
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        data = response.xpath(
            "//script[@type=\"application/ld+json\"]//text()").extract()

        for item in data:
            item = json.loads(item)
            if item['@type'] == 'SportsEvent':
                yield item


class LaligaResultSpider(scrapy.Spider):
    name = "laligaResult"
    allowed_domains = ['laliga.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'sport_scraper.pipelines.SportScraperPipeline': 300,
        }
    }

    def __init__(self, url):
        self.url = url
  
    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        pass