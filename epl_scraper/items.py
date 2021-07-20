# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class StandingList(scrapy.Item):
    position = scrapy.Field()
    played = scrapy.Field()
    points = scrapy.Field()
    won = scrapy.Field()
    drawn = scrapy.Field()
    lost = scrapy.Field()
    goals_for = scrapy.Field()
    goals_against = scrapy.Field()
    goal_difference = scrapy.Field()
    team = scrapy.Field()
