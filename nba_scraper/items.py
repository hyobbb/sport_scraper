# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from items import TeamItem
import scrapy


class NBAResultItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NBATeamItem(TeamItem):
    division = scrapy.Field()