import scrapy
import re
import json
import pandas as pd
from datetime import datetime
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver


class NBASpider(scrapy.Spider):
    name = "nba"
    allowed_domains = ['nba.com']

    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')

    def start_requests(self):
        urls = [
            # f'https://www.nba.com/games?date={self.today}',
            # 'https://www.nba.com/games?date=2021-06-01',
            'https://www.nba.com/game/lal-vs-phx-0042000155'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_game)

    def parse(self, response):
        # find game boxes
        games = response.css(
            "div.w-full.flex.flex-col.flex-1.md\:w-7\/12.lg\:w-5\/12")
        if games is not None:
            for game in games:
                game_id = game.css('a::attr(href)').extract_first()
                url = response.urljoin(game_id)
                yield SeleniumRequest(
                    url=url,
                    callback=self.parse_game,
                    wait = 5,
                    wait_until = EC.presence_of_element_located((By.CSS_SELECTOR,'[table^="GameLinescore_table-"]' ))
                )

    def parse_game(self, response):
        summary_table = response.css('[table^="GameLinescore_table-"]')
        self.log(f'table exists?? {summary_table}')


    def save_as_html(self, response):
        page = response.url.split("/")
        filename = f'quotes-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
