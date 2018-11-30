#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()
from ..db.mongo import mongo_service
from ...models import Eqp

def eqp_find(current_user):
    obj = mongo_service(Eqp, current_user.factory.FID + 'eqp')
    return obj.find_object()
