#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from flask import render_template, session, redirect, url_for, flash, abort, request, jsonify
from . import engineer
from .forms import SetForm, OperationForm, HistoryForm, SencerFormNoCsrf
from flask_login import login_required, current_user
from .. import db
from ..decorators import engineer_required
from ..models import Eqp, Supplier, SencerInfo, EqpSup, SencerThreadInfo, Thread, User, FaultList, Operation
from ..util.db.mongo import mongo_service
from ..util.db.mongo_util import delete_collection


@engineer.route('/create_eqp', methods=['POST', 'GET'])
@login_required
@engineer_required
def create_eqp():
    form = SetForm()
    inner_form = SencerFormNoCsrf()
    inner_form.sencer_name = ""
    inner_form.no_load = ""
    inner_form.standard_load = ""
    inner_form.zero_point = ""
    inner_form.empty_load = ""
    inner_form.exec_v = ""
    inner_form.sensitivity = ""
    inner_form.resistance = ""
    form.sencer_info.append_entry(inner_form)
    if form.validate_on_submit():
        factory_eqp = mongo_service(Eqp, current_user.factory.FID + 'eqp')
        EID = form.eqp_name.data
        if len(factory_eqp.find_object(EID=EID)) == 0:
            try:
                sencers = []
                sencer_threads = []
                time_now = datetime.utcnow()
                for sencer in form.sencer_info.data:
                    sencers.append(SencerInfo(sencer_name=sencer["sencer_name"],
                                            no_load_set=sencer["no_load"],
                                            empty_load_set=sencer["empty_load"],
                                            exec_v=sencer["exec_v"],
                                            sensitivity=sencer["sensitivity"],
                                            resistance=sencer["resistance"]))
                    sencer_threads.append(SencerThreadInfo(standard_point=sencer["standard_load"],
                                                        zero_point=sencer["zero_point"]))
                factory_eqp.create_obj(EID=EID, place=form.eqp_location.data,
                                        supplier=EqpSup(SID=form.supplier.data,
                                                        contact=form.supplier_con.data),
                                        timestamp=time_now,
                                        sencer_num=form.num.data,
                                        sencer_info=sencers,
                                        temperature=form.temperature.data,
                                        wet=form.wet.data)
                factory_eqp_thread = mongo_service(Thread, current_user.factory.FID + EID + 'thread')
                factory_eqp_thread.create_obj(timestamp=time_now,
                                            sencer_thread_info=sencer_threads)
                factory_sup = mongo_service(Supplier, current_user.factory.FID + 'sup')
                if len(factory_sup.find_object(SID=form.supplier.data)) == 0:
                    factory_sup.create_obj(SID=form.supplier.data,
                                        contact=form.supplier_con.data,
                                        info=form.supplier_info.data)
                flash('创建设备成功')
                current_user.eqp_list.append(EID)
                User.objects(UID=current_user.UID).update(eqp_list=current_user.eqp_list)
                return redirect(url_for('main.index'))
            except Exception as e:
                flash(e)
                return render_template('500.html'), 500
        else:
            flash('设备已存在，请不要重复添加')
    if form.errors:
        flash(form.errors)
    return render_template('/engineer/SetPoint.html', form=form)


@engineer.route('/edit_eqp/<string:eqp_name>', methods=['POST', 'GET'])
@login_required
@engineer_required
def edit_eqp(eqp_name):
    form = SetForm()
    factory_eqp = mongo_service(Eqp, current_user.factory.FID + 'eqp')
    factory_sup = mongo_service(Supplier, current_user.factory.FID + 'sup')
    factory_eqp_thread = mongo_service(Thread, current_user.factory.FID + eqp_name + 'thread')
    try:
        eqp_info = factory_eqp.find_object(EID=eqp_name)[0]
        sup_info = factory_sup.find_object(SID=eqp_info.supplier.SID)[0]
        thread_info = factory_eqp_thread.find_object(timestamp=eqp_info.timestamp)[0]
    except Exception as e:
        print(e)
        flash('设备信息查询失败，联系管理员')
        return render_template('500.html'), 500
    if form.validate_on_submit():
        try:
            EID = form.eqp_name.data
            sencers = []
            sencer_threads = []
            time_now = datetime.utcnow()
            for sencer in form.sencer_info.data:
                sencers.append(SencerInfo(sencer_name=sencer["sencer_name"],
                                        no_load_set=sencer["no_load"],
                                        empty_load_set=sencer["empty_load"],
                                        exec_v=sencer["exec_v"],
                                        sensitivity=sencer["sensitivity"],
                                        resistance=sencer["resistance"]))
                sencer_threads.append(SencerThreadInfo(standard_point=sencer["standard_load"],
                                                    zero_point=sencer["zero_point"]))
            factory_eqp.update_obj(q_dic={'EID': eqp_name},
                                u_dic={'EID': EID, 'place': form.eqp_location.data,
                                        'supplier': EqpSup(SID=form.supplier.data,
                                                        contact=form.supplier_con.data),
                                        'timestamp': time_now,
                                        'sencer_num': form.num.data,
                                        'sencer_info': sencers,
                                        'temperature': form.temperature.data,
                                        'wet': form.wet.data})
            factory_eqp_thread.update_obj(q_dic={'timestamp': eqp_info.timestamp},
                                        u_dic={'timestamp': time_now,
                                                'sencer_thread_info': sencer_threads})
            factory_sup.update_obj(q_dic={'SID': sup_info.SID},
                                u_dic={'SID': form.supplier.data,
                                        'contact': form.supplier_con.data,
                                        'info': form.supplier_info.data})
            flash('更新设备信息成功')
            return redirect(url_for('main.index'))
        except Exception as e:
            print(e)
            flash(e)
            return render_template('500.html'), 500
    form.eqp_name.data = eqp_info.EID
    form.eqp_location.data = eqp_info.place
    form.num.data = str(eqp_info.sencer_num)
    form.supplier.data = sup_info.SID
    form.supplier_con.data = sup_info.contact
    form.supplier_info.data = sup_info.info
    form.temperature.data = str(eqp_info.temperature)
    form.wet.data = str(eqp_info.wet)
    for sencer_info, thread_info in zip(eqp_info.sencer_info, thread_info.sencer_thread_info):
        inner_form = SencerFormNoCsrf()
        inner_form.sencer_name = sencer_info.sencer_name
        inner_form.no_load = str(sencer_info.no_load_set)
        inner_form.standard_load = str(thread_info.standard_point)
        inner_form.zero_point = str(thread_info.zero_point)
        inner_form.empty_load = str(sencer_info.empty_load_set)
        inner_form.exec_v = str(sencer_info.exec_v)
        inner_form.sensitivity = str(sencer_info.sensitivity)
        inner_form.resistance = str(sencer_info.resistance)
        form.sencer_info.append_entry(inner_form)
    return render_template('/engineer/SetPoint.html', form=form)


@engineer.route('/delete_eqp/<string:eqp_name>', methods=['POST', 'GET'])
@login_required
@engineer_required
def delete_eqp(eqp_name):
    try:
        User.objects(eqp_list=eqp_name).update(pull__eqp_list=eqp_name)
        factory_eqp = mongo_service(Eqp, current_user.factory.FID + 'eqp')
        factory_eqp.delete_obj(EID=eqp_name)
        delete_collection(current_user.factory.FID + eqp_name)
    except Exception as e:
        print(e)
        return redirect(url_for('main.index'))
    flash('删除设备成功')
    return redirect(url_for('main.index'))


# def code_to_mes(code):
#     if code == 1:
#         return '信号丢失故障'
#     elif code == 3:
#         return '瞬时过流故障'
#     elif code == 2:
#         return '瞬时受力报警'
#     elif code == 4:
#         return '超出量程故障'
#     elif code == 5:
#         return '偏载报警'


# def queryFault(start, end, eqp, dic):
#     facID = current_user.factoryID
#     FaultList.__table__.name = facID + eqp + 'faultlist'
#     result = db.session.query(FaultList).filter(FaultList.FaultTime > start, FaultList.FaultTime < end).all()
#     for item in result:
#         dic['id'].append(item.id)
#         dic['fault_time'].append(item.FaultTime.strftime('%Y-%m-%d %H:%M:%S'))
#         if item.RecoverTime:
#             dic['recover_time'].append(item.RecoverTime.strftime('%Y-%m-%d %H:%M:%S'))
#             delt = (item.RecoverTime - item.FaultTime).seconds
#             days = delt // (24 * 3600)
#             hours = (delt - (24 * 3600) * days) // 3600
#             minutes = (delt - (24 * 3600) * days - 3600 * hours) // 60
#             dic['period_second'].append(str(days) + "天" + str(hours) + "小时" + str(minutes) + "分钟")
#         else:
#             dic['recover_time'].append('——')
#             dic['period_second'].append('——')
#         if item.FaultSencer:
#             dic['fault_reason'].append(item.FaultSencer + code_to_mes(item.FaultCode))
#         # else:
#         #     dic['fault_reason'].append()
#         dic['fault_state'].append('已修复' if item.FaultState == 0 else '未修复')
#         dic['fault_level'].append(2 if item.FaultCode in [1, 3, 4] else 1)
#     return dic

# @engineer.route('/faultreport', methods=['POST', 'GET'])
# @login_required
# @engineer_required
# def faultreport():
#     form = HistoryForm(current_user)
#     dic = {}
#     dic['id'] = []
#     dic['fault_time'] = []
#     dic['recover_time'] = []
#     dic['period_second'] = []
#     dic['fault_reason'] = []
#     dic['fault_state'] = []
#     dic['fault_level'] = []
#     Num = 0
#     if current_user.role_id > 1:
#         if form.validate_on_submit():
#             start = datetime.strptime(form.startdate.data, "%Y-%m-%d %H:%M:%S")
#             end = datetime.strptime(form.enddate.data, "%Y-%m-%d %H:%M:%S")
#             eqp = form.eqp.data
#             if (start > end):
#                 flash("请正确输入时间！")
#             else:
#                 dic = queryFault(start, end, eqp, dic)
#                 Num = len(dic['id'])
#                 flash('查询完成')
#         return render_template('/engineer/FaultReport.html', dic=dic, Num=Num, form=form)
#     return render_template('/engineer/FaultReport.html', dic=dic, Num=Num)


# @engineer.route('/operaterecord', methods=['POST', 'GET'])
# @login_required
# def operaterecord():
#     form = OperationForm(current_user)
#     if form.validate_on_submit():
#         facID = current_user.factoryID
#         eqpID = form.eqp.data
#         Operation.__table__.name = facID + eqpID + 'operation'
#         work = form.operator.data + form.operate.data
#         context = Operation(Timestamp=form.date.data,
#                             record=work)
#         db.session.add(context)
#         db.session.commit()
#         Thread.__table__.name = facID + eqpID + 'thread'
#         newThread = Thread(Timestamp=form.date.data,
#                            standard=form.standard.data,
#                            zeropoint=form.zero.data)
#         db.session.add(newThread)
#         db.session.commit()
#         flash('操作记录成功！')
#         return redirect(url_for('main.index'))
#     return render_template('/engineer/OperationRecord.html', form=form)


# @engineer.route('/history', methods=['POST', 'GET'])
# @login_required
# @engineer_required
# def history():
#     form = HistoryForm(current_user)
#     return render_template('/engineer/History.html', form=form)


# @engineer.route('/historyQuery', methods=['POST', 'GET'])
# def historyQuery():
#     dic = {}
#     dic['axisData'] = []
#     dic['Tag1'] = []
#     dic['Tag2'] = []
#     dic['Tag3'] = []
#     dic['Tag4'] = []
#     startTime = request.form.get("startTime", "")
#     endTime = request.form.get("endTime", "")
#     eqp = request.form.get("eqp", "")
#     startTime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S") - timedelta(hours=1)
#     if endTime == 'noEnd':
#         endTime = datetime.datetime.now() + timedelta(hours=1)
#     else:
#         endTime = datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)
#     # result = NewData.query.filter(NewData.Timestamp > startTime, NewData.Timestamp < endTime).all()
#     NewVal.__table__.name = current_user.factoryID + eqp + "newval" + startTime.strftime('%Y-%m-%d %H:%M:%S')[:10]
#     result = db.session.query(NewVal).filter(NewVal.Timestamp >= startTime).all()
#     while startTime.date() < endTime.date():
#         print(startTime.date() < endTime.date())
#         startTime += timedelta(days=1)
#         NewVal.__table__.name = current_user.factoryID + eqp + "newval" + startTime.strftime('%Y-%m-%d %H:%M:%S')[:10]
#         result.extend(db.session.query(NewVal).all())
#     NewVal.__table__.name = current_user.factoryID + eqp + "newval" + startTime.strftime('%Y-%m-%d %H:%M:%S')[:10]
#     result.extend(db.session.query(NewVal).filter(NewVal.Timestamp <= endTime).all())
#     for item in result:
#         dic['axisData'].append(getattr(item, 'Timestamp').strftime('%Y-%m-%d %H:%M:%S'))
#         dic['Tag1'].append(getattr(item, 'WeightTag1'))
#         dic['Tag2'].append(getattr(item, 'WeightTag2'))
#         dic['Tag3'].append(getattr(item, 'WeightTag3'))
#         dic['Tag4'].append(getattr(item, 'WeightTag4'))
#     return jsonify(dic)


# @engineer.route('/operationQuery', methods=['POST', 'GET'])
# def operationQuery():
#     dic = {}
#     dic['Timestamp'] = []
#     # dic['record'] = []
#     dic['standard'] = []
#     dic['zeropoint'] = []
#     startTime = request.form.get("startTime", "")
#     endTime = request.form.get("endTime", "")
#     eqp = request.form.get("eqp", "")
#     startTime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S") - timedelta(hours=1)
#     Operation.__table__.name = current_user.factoryID + eqp + "operation"
#     Thread.__table__.name = current_user.factoryID + eqp + "thread"
#     if endTime == 'noEnd':
#         # result1 = Operation.query.filter(Operation.Timestamp > startTime).all()
#         result2 = Thread.query.filter(Thread.Timestamp > startTime).all()
#     else:
#         endTime = datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)
#         # result1 = Operation.query.filter(Operation.Timestamp > startTime, Operation.Timestamp < endTime).all()
#         result2 = Thread.query.filter(Thread.Timestamp > startTime, Thread.Timestamp < endTime).all()
#     for item in result2:
#         for key in dic.keys():
#             if key == 'Timestamp':
#                 dic[key].append(getattr(item, key).strftime('%Y-%m-%d %H:%M:%S'))
#             else:
#                 dic[key].append(getattr(item, key))
#     return jsonify(dic)
