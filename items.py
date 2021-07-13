import scrapy


class TeamItem(scrapy.Item):
    name = scrapy.Field()
    short_name = scrapy.Field()
    official_site = scrapy.Field()
    logo_url = scrapy.Field()
    division = scrapy.Field() #nullable


class MatchItem(scrapy.Item):
    url = scrapy.Field()
    scheduled_date = scrapy.Field()
    away_team = scrapy.Field()
    home_team = scrapy.Field()
    location = scrapy.Field()
