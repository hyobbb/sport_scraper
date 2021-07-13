import scrapy
import json


class LaligaResultSpider(scrapy.Spider):
    name = "laliga_result"
    allowed_domains = ['laliga.com']

    def __init__(self, url='https://www.laliga.com/en-ES/match/temporada-2020-2021-laliga-santander-sevilla-fc-elche-c-f-2'):
        self.url = url
  
    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        selectors = response.xpath("//div[starts-with(@class, 'styled__TabContent-')]//text()")
        if selectors is not None:
            for s in selectors:
                content = s.extract()
                print(content)
        else :
            print('nothing')

    def save_as_html(self, response):
        page = response.url.split("/")
        filename = f'quotes-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)