from items import MatchItem, TeamItem
import scrapy
import json


class LaligaTeamSpider(scrapy.Spider):
    name = "laliga_teams"
    allowed_domains = ['laliga.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'laliga_scraper.pipelines.LaligaTeamPipeline': 300,
        }
    }

    def start_requests(self):
        url = 'https://www.laliga.com/laliga-santander/clubes'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        data = response.xpath(
            "//script[@type=\"application/json\"]//text()").extract()

        for item in data:
            item = json.loads(item)
            try:
                teams = item['props']['pageProps']['teams']
                for team in teams:
                    yield TeamItem(
                        name=team['nickname'],
                        short_name=team['shortname'],
                        official_site=team['web'],
                        logo_url=team['shield']['url']
                    )
            except:
                pass


class LaligaScheduleSpider(scrapy.Spider):
    name = "laliga_schedule"
    allowed_domains = ['laliga.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'laliga_scraper.pipelines.LaligaSchedulePipeline': 300,
        }
    }

    def __init__(self, start_week=1, end_week=38):
        self.start_week = start_week
        self.end_week = end_week

    def start_requests(self):
        for week in range(self.start_week, self.end_week+1):
            url = f'https://www.laliga.com/en-ES/laliga-santander/results/2021-22/gameweek-{week}'
            yield scrapy.Request(url=url, callback=self.parse, meta={'week':week})

    def parse(self, response):
        week = response.meta['week']
        data = response.xpath(
            "//script[@type=\"application/ld+json\"]//text()").extract()

        for item in data:
            item = json.loads(item)
            if item['@type'] == 'SportsEvent':
                yield MatchItem(
                    season_id = 2,
                    competition_id = 2,
                    game_number = week,
                    url=item['url'],
                    scheduled_date=item['startDate'],
                    away_team=item['awayTeam']['name'],
                    home_team=item['homeTeam']['name'],
                    location=item['location']['name']
                )
