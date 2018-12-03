#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient

def delete_collection(key_word):
    client = MongoClient("mongodb://siemens:siemens@127.0.0.1:27017/weighting")
    db = client['weighting']
    collection_names = db.collection_names()
    for collection in collection_names:
        if key_word in collection:
            db.drop_collection(collection)
    client.close()
