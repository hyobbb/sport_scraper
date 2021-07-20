from items import MatchItem, TeamItem
import scrapy
import time
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class EPLTeamLinkSpider(scrapy.Spider):
    name = "epl_team_links"
    allowed_domains = ['premierleague.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'epl_scraper.pipelines.EPLTeamPipeline': 300,
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
        url = 'https://www.premierleague.com/clubs'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.driver.get(response.url)
        try:
            index = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@class=\"indexAllTime\"]//tbody[@class='allTimeDataContainer']"))
            )
            teams = index.find_elements(By.CLASS_NAME, "team")
            links = []
            for team in teams:
                link = team.find_element(
                    By.TAG_NAME, 'a').get_attribute('href')
                links.append(link)
            self.save_links(links)

        except TimeoutException:
            self.driver.close()
        finally:
            self.driver.close()

    def save_links(self, links):
        filename = f'./data_examples/epl_teams.txt'
        with open(filename, 'w') as f:
            for link in links:
                f.write(link + '\n')


class EPLTeamSpider(scrapy.Spider):
    name = "epl_teams"
    allowed_domains = ['premierleague.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'epl_scraper.pipelines.EPLTeamPipeline': 300,
        }
    }

    def start_requests(self):
        urls = []
        filename = './data_examples/epl_teams.txt'
        with open(filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                urls.append(line)
        f.close()

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        info = response.xpath("//div[@class='clubDetailsContainer']")
        team_name = info.xpath('//h1/text()').get()
        official_site = info.xpath('//div[@class="website"]/a/text()').get()
        if official_site is not None:
            if 'http' not in official_site:
                official_site = 'https://' + official_site
        else:
            official_site = response.url

        logo_url = info.xpath('.//img/@src').get()
        logo_url = 'https:' + logo_url

        short_name = response.xpath(
            f"//abbr[@title='{team_name}']/text()").get()
        if short_name is not None:
            short_name = short_name.strip()

        yield TeamItem(
            name=team_name,
            short_name=short_name,
            official_site=official_site,
            logo_url=logo_url
        )


class EPLScheduleSpider(scrapy.Spider):
    name = "epl_schedule"
    allowed_domains = ['premierleague.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'epl_scraper.pipelines.EPLSchedulePipeline': 300,
        }
    }

    def __init__(self, date=None):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')

        #disable images 
        #https://tarunlalwani.com/post/selenium-disable-image-loading-different-browsers/
        chrome_prefs = {}
        options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
        
        self.driver = webdriver.Remote(
            command_executor='http://chrome:4444/wd/hub',
            options=options
        )

    def start_requests(self):
        url = 'https://www.premierleague.com/fixtures'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.driver.get(response.url)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "matchList"))
            )
            
            ml = self.driver.find_elements(By.CLASS_NAME, "matchList")
            while True:
                # Scroll down to bottom
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                # Wait to load page
                time.sleep(3)
                
                ml_new = self.driver.find_elements(By.CLASS_NAME, "matchList")
                if len(ml) == len(ml_new) and ml_new != 0 : 
                    break
            
            for matchList in ml:
                matches = matchList.find_elements(By.XPATH, ".//span[contains(@class, 'quickView')]")
                for match in matches:
                    data = match.get_attribute('data-ui-args')
                    if data is not None:
                        item = json.loads(data)
                        scheduled = item['kickoff']
                        tzone = scheduled['label'].split(' ')[-1]
                        yield MatchItem(
                            season_id=3,
                            competition_id=3,
                            game_number=item['gameweek']['gameweek'],
                            url=item['url'],
                            scheduled_date=item['kickoff']['millis'],
                            tzone = tzone,
                            away_team=item['teams'][1]['team']['name'],
                            home_team=item['teams'][0]['team']['name'],
                            location=item['ground']['name']
                        )
        except TimeoutException:
            self.driver.close()
        finally:
            self.driver.close()

    def get_all_data(self):
        #https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down to bottom
            self.driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            #self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')

            # Wait to load page
            time.sleep(3)
            print('current height is {}'.format(last_height))

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print('arrived to end!!')
                break
            
            last_height = new_height
            