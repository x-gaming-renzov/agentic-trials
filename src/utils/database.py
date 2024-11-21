#connect to mongodb
from pymongo import MongoClient

def connect_to_db(session_id):
    client = MongoClient('mongodb+srv://paras:yqjLfxelzB1eUuWx@cluster0.ki0kt.mongodb.net/')
    #create a database called session_id
    db = client[session_id]
    
