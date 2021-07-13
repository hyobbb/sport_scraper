# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from items import TeamItem
import pandas as pd
import json
import pymysql
from pipelines import DBPipeline
from itemadapter import ItemAdapter


class NBAPipeline:

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


class NBATeamPipeline(DBPipeline):
    def __init__(self, host, user, password, db) -> None:
        super().__init__(host, user, password, db)
        self.table = 'teams'

    def process_item(self, item:TeamItem, spider):
        cursor = self.connection.cursor()
        official_site = item['official_site'].replace('//', 'https://')
        division = item['division'].lower()
        if division == 'atlantic' or division == 'central' or division == 'southeast':
            conference = 'east'
        else :
            conference = 'west'
        cursor.execute(
            f'''INSERT INTO {self.table} (
                sport_id, 
                league_id, 
                conference,
                division,
                name, 
                short_name, 
                official_site, 
                logo_url
            ) VALUES (
                1, 
                2,
                '{conference}',
                '{division}',
                '{item['name']}', 
                '{item['short_name']}', 
                '{official_site}', 
                '{item['logo_url']}'
            )
            ON DUPLICATE KEY UPDATE 
            short_name = '{item['short_name']}', 
            official_site = '{official_site}',
            logo_url = '{item['logo_url']}'
            '''
        )
        return item


class NBASchedulePipeline(DBPipeline):
    def __init__(self, host, user, password, db) -> None:
        super().__init__(host, user, password, db)
        self.table = 'matches'