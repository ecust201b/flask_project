#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()
from mongoengine.queryset import QuerySet
from mongoengine.errors import DoesNotExist, MultipleObjectsReturned

class mongo_service(object):
    
    qs = None
    qs_name = ""
    old_collection = None

    def __init__(self, collection, new_name):
        if new_name is None:
            self.qs = collection.objects
        else:
            self.qs = self._switch_table_and_return_query_set(collection, new_name)
            self.qs_name = new_name
        self.old_collection = collection
    
    def _switch_table_and_return_query_set(self, collection, new_name):
        new_collection = collection.switch_collection(collection(), new_name)
        new_objects = QuerySet(collection,new_collection._get_collection())
        return new_objects
    
    def find_object(self, **q):
        try:
            obj = self.qs.filter(**q).all()
            return obj
        except DoesNotExist as e:
            print(e)
            raise e
    
    def delete_obj(self, **q):
        try:
            obj = self.find_object(**q)
            num = len(obj)
            for item in obj:
                item.switch_collection(self.qs_name)
                item.delete()
            return num
        except DoesNotExist as e:
            raise e
    
    def create_obj(self, **q):
        try:
            obj = self.old_collection(**q)
            obj.switch_collection(self.qs_name)
            obj.save()
        except Exception as e:
            print(e)
            raise e
    
    def update_obj(self, q_dic, u_dic):
        try:
            obj = self.find_object(**q_dic)
            num = len(obj)
            for item in obj:
                item.switch_collection(self.qs_name)
                item.update(**u_dic)
            return num
        except Exception as e:
            print(e)
            raise e
