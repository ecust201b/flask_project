#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()
from ..db.mongo import mongo_service
from ...models import Eqp, Thread, Supplier

def eqp_find(FID):
    obj = mongo_service(Eqp, FID + 'eqp')
    return obj.find_object()

def eqp_info_find(FID, EID):
    factory_eqp = mongo_service(Eqp, FID + 'eqp')
    factory_sup = mongo_service(Supplier, FID + 'sup')
    factory_eqp_thread = mongo_service(Thread, FID + EID + 'thread')
    try:
        eqp_info = factory_eqp.find_object(EID=EID)[0]
        sup_info = factory_sup.find_object(SID=eqp_info.SID)[0]
        thread_info = factory_eqp_thread.find_object(timestamp=eqp_info.timestamp)[0]
        return eqp_info, sup_info, thread_info
    except Exception as e:
        print(e)
        raise e
