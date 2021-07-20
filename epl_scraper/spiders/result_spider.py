from epl_scraper.items import StandingList
import scrapy


class EPLResultSpider(scrapy.Spider):
    name = "epl_result"
    allowed_domains = ['premierleague.com']
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


class EPLStandingSpider(scrapy.Spider):
    name = "epl_standing"
    allowed_domains = ['premierleague.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'epl_scraper.pipelines.EPLStandingPipeline': 300,
        }
    }

    def start_requests(self):
        self.url = 'https://www.premierleague.com/tables'
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        table = response.xpath("(//table)[1]")
        rows = table.xpath(".//tr")
        for row in rows:
            value = row.css('::attr(data-filtered-table-row-name)')
            if value is not None and len(value) != 0:

                data = row.xpath(".//td//text()[normalize-space()]").extract()
                data = [data.replace('\n', ' ').strip() for data in data]
                # form
                # ['1', 'Arsenal', 'ARS', '0', '0', '0', '0', '0', '0', '0', '0', 'Brentford', 'Friday 13 August 2021', 'BRE', '20:00', 'ARS']
                yield StandingList(
                    position=data[0],
                    played=data[3],
                    points=data[10],
                    won=data[4],
                    drawn=data[5],
                    lost=data[6],
                    goals_for=data[7],
                    goals_against=data[8],
                    goal_difference=data[9],
                    team=data[1],
                )
