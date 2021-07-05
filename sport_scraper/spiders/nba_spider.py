from copy import deepcopy
import scrapy
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from ..items import NBAResult


class NBASpider(scrapy.Spider):
    name = "nba"
    allowed_domains = ['nba.com']

    def __init__(self, date=None):
        self.date = datetime.now().strftime('%Y-%m-%d') if date is None else date
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Remote(
            command_executor='http://chrome:4444/wd/hub',
            options=options
        )

    def start_requests(self):
        urls = [
            f'https://www.nba.com/games?date={self.date}',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # find game boxes
        games = response.css(
            "div.w-full.flex.flex-col.flex-1.md\:w-7\/12.lg\:w-5\/12")
        if games is not None:
            for game in games:
                ref = game.css('a::attr(href)').extract_first()
                url = response.urljoin(ref)
                game_id = ref.split('/')[-1]
                yield scrapy.Request(url=url, callback=self.parse_game, meta={'item': {'game_id': game_id}})

    def parse_game(self, response):
        self.driver.get(response.url)
        item = response.meta['item']
        try:
            table = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//table[starts-with(@class, 'GameLinescore_')]"))
            )
            rows = table.find_elements(By.TAG_NAME, 'tr')
            data = []
            for row in rows:
                values = row.text.split(' ')
                values = list(filter(None, values))
                data.append(values)

            item_new = deepcopy(item)
            item_new['score_board'] = data
            yield response.follow(response.url+'/box-score',
                                  callback=self.parse_box_score,
                                  meta={'item': item_new},
                                  )
        except TimeoutException:
            self.driver.close()

    def parse_box_score(self, response):
        self.log(f'parsing url is {response.url}')
        self.driver.get(response.url)
        item = response.meta['item']
        try:
            tables = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//table[starts-with(@class, 'StatsTable_')]"))
            )
            tables = self.driver.find_elements(
                By.XPATH, "//table[starts-with(@class, 'StatsTable_')]")

            box_score = []
            for table in tables:
                head = table.find_element(By.TAG_NAME, 'thead').text.split(' ')
                body = table.find_element(By.TAG_NAME, 'tbody')
                data = [head]
                for row in body.find_elements(By.TAG_NAME, 'tr'):
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    row_data = [cell.text.replace('\n', ' ') for cell in cells]
                    data.append(row_data)
                box_score.append(data)

            item_new = deepcopy(item)
            item_new['box_score'] = box_score
            yield NBAResult(
                game_id=item_new['game_id'],
                date=self.date,
                score_board=item_new['score_board'],
                box_score=item_new['box_score']
            )
        except TimeoutException:
            print(f'Time out')
            self.driver.close()

    def save_as_html(self, response):
        page = response.url.split("/")
        filename = f'quotes-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
