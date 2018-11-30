#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import db
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from flask import current_app


# 记载用户的回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()

class Permission:
    Operator = 2
    Engineer = 1
    ADMINSTER = 0

class Role(db.Document):
    RID = db.IntField()
    name = db.StringField(max_length=64, unique=True)

    def __repr__(self):
        return '<Role %r>' % self.name


class Factory(db.Document):
    FID = db.StringField(max_length=20, unique=True)
    address = db.StringField(max_length=40)
    responsor = db.StringField(max_length=20)
    meta = {'indexes': ['FID']}


# 每个工厂一张，命名：FID + sup
class Supplier(db.Document):
    contact = db.StringField(max_length=20)
    SID = db.StringField(max_length=20, unique_with="contact")
    info = db.StringField(max_length=100)
    meta = {'indexes': [('SID', 'contact')]}


class EqpSup(db.EmbeddedDocument):
    SID = db.StringField(max_length=20)
    contact = db.StringField(max_length=20)


# 每个工厂一张，命名：FID + eqp
class Eqp(db.Document):
    EID = db.StringField(max_length=20, unique=True)
    place = db.StringField(max_length=20)
    supplier = db.EmbeddedDocumentField(EqpSup)
    meta = {'indexes': ['EID']}


class User(UserMixin, db.Document):
    UID = db.StringField(max_length=64, unique=True)
    role = db.ReferenceField(Role)
    password_hash = db.StringField(max_length=128)
    factory = db.ReferenceField(Factory, reverse_delete_rule=db.CASCADE)
    eqp_list = db.ListField(db.StringField(max_length=20))
    meta = {'indexes': ['UID']}

    # 新增密码散列化
    @property
    def password(self):
        raise AttributeError('password is not a readable attr')

    def set_pass(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


# 每个设备一张，命名：FID + EID + eqpinfo

class SencerInfo(db.EmbeddedDocument):
    sencer_name = db.StringField(max_length=20)
    no_load_set = db.FloatField()
    empty_load_set = db.FloatField()
    exec_v = db.FloatField()
    sensitivity = db.FloatField()
    resistance = db.FloatField()


class EqpInfo(db.Document):
    timestamp = db.DateTimeField(default=datetime.datetime.utcnow, required=True)
    sencer_num = db.IntField()
    sencer_info = db.ListField(db.EmbeddedDocumentField(SencerInfo))
    temperature = db.FloatField()
    wet = db.FloatField()
    meta = {'indexes': ['timestamp']}


# 每个设备一张，命名：FID + EID + thread
class SencerThreadInfo(db.EmbeddedDocument):
    standard_point = db.FloatField()
    zero_point = db.FloatField()

class Thread(db.Document):
    timestamp = db.DateTimeField(default=datetime.datetime.utcnow, required=True)
    sencer_thread_info = db.ListField(db.EmbeddedDocumentField(SencerThreadInfo))
    meta = {'indexes': ['timestamp']}


# 每个设备一张，命名：FID + EID + faultlist.
class FaultList(db.Document):
    fault_time = db.DateTimeField(default=datetime.datetime.utcnow, required=True)
    recover_time = db.DateTimeField()
    period_second = db.IntField()
    fault_sencer = db.StringField(max_length=20)
    fault_code = db.IntField()
    fault_state = db.BooleanField()
    meta = {'indexes': ['fault_time', 'fault_sencer', 'fault_code']}


# 每个设备一张，命名：FID + EID + operation
class Operation(db.Document):
    timestamp = db.DateTimeField(default=datetime.datetime.utcnow, required=True)
    record = db.StringField(max_length=250)
    meta = {'indexes': ['timestamp']}