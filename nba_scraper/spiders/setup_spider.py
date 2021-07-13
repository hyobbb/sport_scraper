from copy import deepcopy
import scrapy
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from items import TeamItem, MatchItem


class NBATeamSpider(scrapy.Spider):
    name = "nba_teams"
    allowed_domains = ['nba.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'nba_scraper.pipelines.NBATeamPipeline': 300,
        }
    }

    def start_requests(self):
        url = 'https://www.nba.com/teams'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        divisions = response.xpath("//div[contains(@class, 'divisions')]/div")
        if divisions is not None :
            for division in divisions:
                #relative path using .// 
                teams = division.xpath(".//div[contains(@class, 'teams')]/a")
                division_name = division.xpath(".//div/text()").get()
                for team in teams:
                    short_name = team.css('a::attr(data-content)').get()
                    name = team.css('a::attr(data-text)').get()
                    official_site = team.css('a::attr(href)').get()
                    logo_url = team.css('img').attrib['src']
                    yield TeamItem(
                        name = name,
                        short_name = short_name,
                        official_site = official_site,
                        logo_url = logo_url,
                        division = division_name
                    )
                

class NBAScheduleSpider(scrapy.Spider):
    name = "nba_schedule"
    allowed_domains = ['nba.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'nba_scraper.pipelines.NBASchedulePipeline': 300,
        }
    }

    def __init__(self, date=None):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Remote(
            command_executor='http://chrome:4444/wd/hub',
            options=options
        )

    def start_requests(self):
        url = 'https://www.nba.com/schedule?cal=all&pd=false'
        yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        self.driver.get(response.url)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h2[starts-with(@class, 'GameScheduleWeek_')]"))
            )
            weeks = self.driver.find_elements(By.XPATH, "//h2[starts-with(@class, 'GameScheduleWeek_')]")
            for week in weeks:
                print(week)
                print(week.text)
        except TimeoutException:
            self.driver.close()
  