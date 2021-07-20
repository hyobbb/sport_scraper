from laliga_scraper.items import StandingList
import scrapy
import json


class LaligaResultSpider(scrapy.Spider):
    name = "laliga_result"
    allowed_domains = ['laliga.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'laliga_scraper.pipelines.LaligaStandingPipeline': 300,
        }
    }

    def __init__(self, url='https://www.laliga.com/partido/temporada-2020-2021-laliga-santander-atletico-de-madrid-sevilla-fc-1'):
        self.url = url

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        selectors = response.xpath(
            "//div[starts-with(@class, 'styled__TabContent-')]//text()")
        if selectors is not None:
            for s in selectors:
                content = s.extract()
                print(content)
        else:
            print('nothing')


class LaligaStandingSpider(scrapy.Spider):
    name = "laliga_standing"
    allowed_domains = ['laliga.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'laliga_scraper.pipelines.LaligaStandingPipeline': 300,
        }
    }

    def start_requests(self):
        self.url = 'https://www.laliga.com/laliga-santander/clasificacion'
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        data = response.xpath(
            "//script[@type=\"application/json\"]//text()").extract()

        for item in data:
            item = json.loads(item)
            try:
                standings = item['props']['pageProps']['standings']
                yield StandingList(data=standings)
            except:
                pass
