import pymongo
a=pymongo.MongoClient()
a["BotLogger"]["random"].insert_one({"mutes":{}})
