from items import MatchItem, TeamItem
from pipelines import DBPipeline
from itemadapter import ItemAdapter
from datetime import datetime


class EPLTeamPipeline(DBPipeline):
    def __init__(self, host, user, password, db) -> None:
        super().__init__(host, user, password, db)
        self.sport_id = 2
        self.table = 'teams'
        self.cursor = self.connection.cursor()

    def process_item(self, item: TeamItem, spider):
        super().process_item(item, spider)
        name = item['name']
        short_name = item['short_name']
        official_site = item['official_site']
        logo_url = item['logo_url']
        query = f'''INSERT INTO {self.table} 
            (sport_id, name, short_name, official_site, logo_url)
            VALUES (2, '{name}', '{short_name}', '{official_site}', '{logo_url}')
            ON DUPLICATE KEY UPDATE 
            name = '{name}'
            '''
        self.cursor.execute(query)
        return item


class EPLSchedulePipeline(DBPipeline):
    def __init__(self, host, user, password, db) -> None:
        super().__init__(host, user, password, db)
        self.table = 'matches'
    def process_item(self, item, spider):
        super().process_item(item, spider)
        season_id = item['season_id']
        competition_id = item['competition_id']
        game_number = item['game_number']
        url = 'https:' + item['url']
        date = datetime.fromtimestamp(item['scheduled_date']/1000)
        away_team = item['away_team']
        home_team = item['home_team']
        location = item['location']

        timezone = item['tzone']
        scheduled_date = self.to_local(date, timezone)
        scheduled_date_utc = self.to_string(date)
        cursor = self.connection.cursor()
        cursor.execute(
            f'''INSERT INTO {self.table} (
                season_id, 
                competition_id,
                game_number, 
                scheduled_date, 
                timezone, 
                scheduled_date_UTC, 
                away_team,
                home_team,
                location,
                url
            ) VALUES (
                {season_id},
                {competition_id},
                {game_number},
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

    def to_local(self, dt: datetime, tz: str) -> str:
        from pytz import timezone
        if tz == 'BST':
            local_tz = timezone('Etc/GMT+1')
        else:
            local_tz = timezone('Etc/GMT')
        dt = dt.astimezone(local_tz)
        return self.to_string(dt)


class EPLStandingPipeline(DBPipeline):

    def __init__(self, host, user, password, db) -> None:
        super().__init__(host, user, password, db)
        self.season_id = 3
        self.division = 'first team'
        self.table = 'football_standings'
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        super().process_item(item, spider)
        standing = item
        position = int(standing['position'])
        played = int(standing['played'])
        points = int(standing['points'])
        won = int(standing['won'])
        drawn = int(standing['drawn'])
        lost = int(standing['lost'])
        goals_for = int(standing['goals_for'])
        goals_against = int(standing['goals_against'])
        goal_difference = int(standing['goal_difference'])
        team = standing['team']

        query = f'''SELECT id FROM teams WHERE name = '{team}';'''
        self.cursor.execute(query)
        team_id = self.cursor.fetchone()[0]
        self.cursor.execute(f'''
            INSERT INTO {self.table} (
                id,
                season_id,
                team_id,
                division,
                position,
                points,
                played,
                won,
                drawn,
                lost,
                goals_for,
                goals_against,
                goal_difference
            ) VALUES (
                {team_id+self.season_id},
                {self.season_id},
                {team_id},
                '{self.division}',
                {position},
                {points},
                {played},
                {won},
                {drawn},
                {lost},
                {goals_for},
                {goals_against},
                {goal_difference}
            ) ON DUPLICATE KEY UPDATE
                season_id  = {self.season_id},
                position = {position},
                points = {points},
                played = {played},
                won = {won},
                drawn = {drawn},
                lost = {lost},
                goals_for = {goals_for},
                goals_against = {goals_against},
                goal_difference = {goal_difference}    
        ''')

        return item


class LaligaResultPipeline(DBPipeline):

    def __init__(self, host, user, password, db) -> None:
        super().__init__(host, user, password, db)
        self.season_id = 2
        self.division = 'primera'
        self.table = 'football_match_details'
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        super().process_item(item, spider)
        standings = item['data']
        for standing in standings:
            position = standing['position']
            played = standing['played']
            points = standing['points']
            won = standing['won']
            drawn = standing['drawn']
            lost = standing['lost']
            goals_for = standing['goals_for']
            goals_against = standing['goals_against']
            goal_difference = standing['goal_difference']
            team = standing['team']['nickname']

            query = f'''SELECT id FROM teams WHERE name = '{team}';'''
            self.cursor.execute(query)
            team_id = self.cursor.fetchone()[0]
            self.cursor.execute(f'''
                INSERT INTO {self.table} (
                    id,
                    season_id,
                    team_id,
                    division,
                    position,
                    points,
                    played,
                    won,
                    drawn,
                    lost,
                    goals_for,
                    goals_against,
                    goal_difference
                ) VALUES (
                    {team_id+self.season_id},
                    {self.season_id},
                    {team_id},
                    '{self.division}',
                    {position},
                    {points},
                    {played},
                    {won},
                    {drawn},
                    {lost},
                    {goals_for},
                    {goals_against},
                    {goal_difference}
                ) ON DUPLICATE KEY UPDATE 
                    position = {position},
                    points = {points},
                    played = {played},
                    won = {won},
                    drawn = {drawn},
                    lost = {lost},
                    goals_for = {goals_for},
                    goals_against = {goals_against},
                    goal_difference = {goal_difference}    
            ''')

        return item
