import pymysql

class DBPipeline:

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('DB_HOST'),
            user=crawler.settings.get('DB_USER'),
            password=crawler.settings.get('DB_PASSWORD'),
            db=crawler.settings.get('DB_NAME'),
        )

    def __init__(self, host, user, password, db) -> None:
        self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db,
        )

    def close_spider(self, spider):
        self.connection.commit()
        self.connection.close()

    def process_item(self, item, spider):
        pass

