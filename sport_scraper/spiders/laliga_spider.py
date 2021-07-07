import scrapy
import json


class LaligaScheduleSpider(scrapy.Spider):
    name = "laliga"
    allowed_domains = ['laliga.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'sport_scraper.pipelines.LaligaSchedulePipeline': 300,
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

    def __init__(self, url='https://www.laliga.com/en-ES/match/temporada-2020-2021-laliga-santander-sevilla-fc-elche-c-f-2'):
        self.url = url
  
    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        selectors = response.xpath("//div[starts-with(@class, 'styled__TabContent-')]//text()")
        if selectors is not None:
            for s in selectors:
                content = s.extract()
                print(content)
        else :
            print('nothing')

    def save_as_html(self, response):
        page = response.url.split("/")
        filename = f'quotes-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)