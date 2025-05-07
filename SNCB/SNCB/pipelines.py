import pymongo
from itemadapter import ItemAdapter

class MongoDBPipeline:
    collection_name = 'kbo_enterprises'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://localhost:27017/'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'kbo_database')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        enterprise_number = item.get('EnterpriseNumber')
        if enterprise_number:
            self.db[self.collection_name].update_one(
                {'EnterpriseNumber': enterprise_number},
                {'$set': ItemAdapter(item).asdict()},
                upsert=True
            )
            spider.logger.info(f"Enterprise {enterprise_number} upserted to MongoDB")
        else:
            self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
            spider.logger.info("New item inserted to MongoDB (no EnterpriseNumber found)")
        
        return item
