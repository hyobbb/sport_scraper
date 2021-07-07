# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas as pd
import json
import pymysql
from itemadapter import ItemAdapter


class LaligaSchedulePipeline:
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host = crawler.settings.get('DB_HOST'),
            user = crawler.settings.get('DB_USER'),
            password = crawler.settings.get('DB_PASSWORD'),
            db = crawler.settings.get('DB_NAME'),
        )

    def __init__(self, host, user, password, db) -> None:
        self.connection = pymysql.connect(
            host = host,
            user = user,
            password = password,
            database = db,
        )

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        url = item['url']
        date = item['startDate']
        away_team = item['awayTeam']['name']
        home_team = item['homeTeam']['name']
        location = item['location']['name']
        return {
            'url' : url,
            'date' : date,
            'away_team' : away_team,
            'home_team' : home_team,
            'location' : location,
        }


class SportScraperPipeline:

    def open_spider(self, spider):
        #self.connection = pymysql.connect()
        pass

    def close_spider(self, spider):
        # self.connection.close()
        pass

    def process_item(self, item, spider):
        score_board = item['score_board']
        for idx, row in enumerate(score_board):
            if idx == 0:
                index = row
            elif idx == 1:
                away_team = row[0]
            else:
                home_team = row[0]

        sb_df = pd.DataFrame(
            data={away_team: score_board[1][1:],
                  home_team: score_board[2][1:]},
            index=index,
        )

        item['score_board'] = sb_df.to_json(orient='split')
        box_score = item['box_score']

        for idx, bs in enumerate(box_score):
            index = bs[0][1:]
            data = dict()
            for row in bs[1:]:
                data.update({row[0]: row[1:]})

            if idx == 0:
                away_bs_df = pd.DataFrame(data=data, index=index)
            else:
                home_bs_df = pd.DataFrame(data=data, index=index)

        item['box_score'] = {
            away_team: away_bs_df.to_json(orient='split'),
            home_team: home_bs_df.to_json(orient='split')
        }

        line = json.dumps(ItemAdapter(item).asdict()) + '\n'
        with open('{}.js'.format(item['date']), 'a') as f:
            f.write(line)
        return item
