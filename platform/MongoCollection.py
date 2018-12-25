# -*- coding: utf-8 -*-
from ..app.util.db.mongo import mongo_service
from mongoengine import Document, DateTimeField, IntField, StringField

class MongoFaultCollection(Document):
    FaultTime = DateTimeField()  # 故障时间
    RecoverTime = DateTimeField()  # 恢复时间
    PeriodSecond = IntField()  # 间隔时间(s)
    FaultSensor = StringField()  # 故障传感器
    FaultCode = IntField()  # 故障代码
    EQP_State = IntField()  # 设备状态
