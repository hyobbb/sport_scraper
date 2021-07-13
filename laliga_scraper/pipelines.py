# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from items import MatchItem, TeamItem
from pipelines import DBPipeline
from itemadapter import ItemAdapter
from datetime import datetime
import pymysql



class LaligaTeamPipeline(DBPipeline):
    def __init__(self, host, user, password, db) -> None:
        super().__init__(host, user, password, db)
        self.table = 'teams'

    def process_item(self, item: TeamItem, spider):
        super().process_item(item, spider)
        cursor = self.connection.cursor()
        cursor.execute(
            f'''INSERT INTO {self.table} 
            (sport_id, league_id, name, short_name, official_site, logo_url)
            VALUES (2, 1, '{item['name']}', '{item['short_name']}', '{item['official_site']}', '{item['logo_url']}')
            ON DUPLICATE KEY UPDATE 
            league_id = 1, 
            short_name = '{item['short_name']}', 
            official_site = '{item['official_site']}',
            logo_url = '{item['logo_url']}'
            '''
        )
        return item


class LaligaSchedulePipeline(DBPipeline):
    def __init__(self, host, user, password, db) -> None:
        super().__init__(host, user, password, db)
        self.table = 'matches'

    def process_item(self, item: MatchItem, spider):
        super().process_item(item, spider)
        url = item['url']
        date = datetime.fromisoformat(item['scheduled_date'])
        away_team = item['away_team']
        home_team = item['home_team']
        location = item['location']

        scheduled_date = self.to_CET(date)
        timezone = 'CET'
        scheduled_date_utc = self.to_string(date)

        cursor = self.connection.cursor()
        cursor.execute(
            f'''INSERT INTO {self.table} (
                league_id, 
                season_id, 
                scheduled_date, 
                timezone, 
                scheduled_date_UTC, 
                away_team,
                home_team,
                location,
                url
            ) VALUES (
                1,
                1,
                '{scheduled_date}', 
                '{timezone}', 
                '{scheduled_date_utc}', 
                ( SELECT
                    id
                    FROM teams
                    WHERE name = '{away_team}'
                    LIMIT 1
                ),
                ( SELECT
                    id
                    FROM teams
                    WHERE name = '{home_team}'
                    LIMIT 1
                ),
                '{location}',
                '{url}'
            )
            ON DUPLICATE KEY UPDATE 
            scheduled_date = '{scheduled_date}', 
            timezone = '{timezone}',
            scheduled_date_UTC = '{scheduled_date_utc}',
            location = '{location}'
            '''
        )
        return item

    def to_string(self, dt: datetime) -> str:
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def to_CET(self, dt:datetime) -> str:
        from pytz import timezone
        cet = timezone('CET')
        dt = dt.astimezone(cet)
        return self.to_string(dt)
