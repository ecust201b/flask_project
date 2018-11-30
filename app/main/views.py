#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from flask_login import login_required, current_user
from flask import render_template, session, redirect, url_for, flash, abort, request, jsonify
from . import main
from .. import db
# from ..models import Equipment, FaultMsg, NewVal, FaultList
from ..models import Eqp
from ..util.db.mongo import mongo_service

def code_to_state(state):
    if state == 1:
        return '预警状态'
    elif state == 2:
        return '设备故障'
    else:
        return '正常运行'


@main.route('/', methods=['POST', 'GET'])
def index():
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')[:10]
    if current_user.is_authenticated:
        Eqp_new = mongo_service(Eqp, current_user.factory.FID + 'eqp')
        if current_user.role.RID == 0:
            try:
                eqpList = Eqp_new.find_object()
            except Exception as e:
                flash(e)
                return render_template('500.html')
            # for eqp in eqpList:
                # FaultMsg.__table__.name = current_user.factory + eqp.id + 'faultmsg' + date
                # state = db.session.query(FaultMsg).order_by(FaultMsg.id.desc()).first()
                # setattr(eqp, 'state', code_to_state(state.eqpState))
            return render_template('main/MainPage.html', eqpList=eqpList)
        elif current_user.role.RID >= 1:
            eqpList = []
            eqpName = current_user.eqp_list
            if eqpName:
                try:
                    for item in eqpName:
                        eqpList.append(Eqp_new.find_object(EID=item)[0])
                except Exception as e:
                    flash(e)
                    return render_template('500.html')
                # for eqp in eqpList:
                #     FaultMsg.__table__.name = current_user.factory + eqp.id + 'faultmsg' + date
                #     state = db.session.query(FaultMsg).order_by(FaultMsg.id.desc()).first()
                #     setattr(eqp, 'state', code_to_state(state.eqpState))
            else:
                flash("请联系管理员为您添加设备！")
            return render_template('main/MainPage.html', eqpList=eqpList)
        else:
            pass
    return render_template('/main/MainPage.html')


@main.route('/Running/<string:eqp_name>', methods=['POST', 'GET'])
@login_required
def Running(eqp_name):
    return render_template('/main/RunningUI.html')

