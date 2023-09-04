import pymongo
from pymongo.collection import Collection
from pymongo import MongoClient


from typing import Any

def connect_collection_mongodb(database:str, collection:str, uri:str="mongodb://localhost:27017/") -> Collection:
    """
    Connect to a MongoDB collection given a database and collection name.

    Args:
        database (str): MongoDB database name.
        collection (str): MongoDB collection name.
        uri (str): MongoDB URI. Defaults to "mongodb://localhost:27017/".

    Returns:
    """
    
    # Connect to MongoDB
    client: MongoClient = MongoClient(uri)

    # Select database and collection
    db = client[database]
    col = db[collection]

    return col
