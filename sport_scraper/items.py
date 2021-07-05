# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NBAResult(scrapy.Item):
    game_id = scrapy.Field()
    date = scrapy.Field()
    score_board = scrapy.Field()
    box_score = scrapy.Field()