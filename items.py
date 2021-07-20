import scrapy


class TeamItem(scrapy.Item):
    name = scrapy.Field()
    short_name = scrapy.Field()
    official_site = scrapy.Field()
    logo_url = scrapy.Field()
    

class MatchItem(scrapy.Item):
    season_id = scrapy.Field()
    competition_id = scrapy.Field()
    game_number = scrapy.Field()
    url = scrapy.Field()
    scheduled_date = scrapy.Field()
    tzone = scrapy.Field()
    away_team = scrapy.Field()
    home_team = scrapy.Field()
    location = scrapy.Field()


class StandingList(scrapy.Item):
    data = scrapy.Field()