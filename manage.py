#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()
import os
from app import creat_app, db
from app.models import Role, User, Factory, Eqp, Supplier, Thread, EqpInfo, FaultList, Operation
from flask_script import Manager, Shell
from app.util.db.mongo import mongo_service

app = creat_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, Role=Role, User=User, Factory=Factory, Eqp=Eqp,
                Supplier=Supplier, mongo_service=mongo_service, Thread=Thread,
                EqpInfo=EqpInfo, FaultList=FaultList, Operation=Operation)


manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()
