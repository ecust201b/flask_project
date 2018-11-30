#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient

def delete_collection(key_word):
    mongo_client = MongoClient(host='localhost', port=27017, username='siemens', password='siemens')
    db = mongo_client['weighting']
    collection_names = db.collection_names()
    for collection in collection_names:
        if key_word in collection:
            db.drop_collection(collection)
    mongo_client.close()
