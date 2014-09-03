import pymongo


from db import settings


ASC = pymongo.ASCENDING
DSC = pymongo.DESCENDING


db = pymongo.MongoClient(settings.MONGO_DB_ENDPOINT_URL, settings.MONGO_DB_ENDPOINT_PORT)[settings.MONGODB_DB_NAME]