#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField, TextAreaField, FormField, FieldList
from wtforms.validators import Required, Regexp, ValidationError
from ..models import Eqp
from .. import db
from ..util.form.form_util import eqp_find


class SencerForm(Form):
    sencer_name = StringField('传感器位号：', validators=[Required()])
    no_load = StringField('传感器无负载读数：', validators=[Required()])
    standard_load = StringField('传感器标定读数：', validators=[Required()])
    zero_point = StringField('传感器零点：', validators=[Required()])
    empty_load = StringField('传感器空载读数：', validators=[Required()])    
    exec_v = StringField('激励电压(mV)：', validators=[Required()])
    sensitivity = StringField('传感器灵敏度(mV)：', validators=[Required()])
    resistance = StringField('传感器阻抗(Ω)：', validators=[Required()])


class SencerFormNoCsrf(SencerForm):
    def __init__(self, *args, **kwargs):
        super(SencerFormNoCsrf, self).__init__(meta={'csrf':False}, *args, **kwargs)


class SetForm(Form):
    eqp_name = StringField('设备号：', validators=[Required()])
    eqp_location = StringField('设备所处工段：', validators=[Required()])
    supplier = StringField('供应商：', validators=[Required()])
    supplier_info = StringField('供应商信息：', validators=[Required()])
    supplier_con = StringField('供应商联系方式：', validators=[Required()])
    num = StringField('传感器数量：', validators=[Required()])
    temperature = StringField('记录时环境温度(℃)：', validators=[Required()])
    wet = StringField('记录时环境湿度(%)：', validators=[Required()])
    sencer_info = FieldList(FormField(SencerFormNoCsrf), min_entries=1)
    submit = SubmitField('提交信息')

    def __init__(self, *args, **kwargs):
        super(SetForm, self).__init__(*args, **kwargs)


class OperationForm(Form):
    date = StringField('操作时间：', validators=[Required()], render_kw={"placeholder": "year-month-day hour:month"})
    operator= StringField('操作人：', validators=[Required()], render_kw={"placeholder": ""})
    eqp = SelectField('设备号', coerce=str)
    operate = TextAreaField('操作记录：', validators=[Required()], render_kw={"placeholder": "请填写操作记录"})
    standard = StringField('操作时标定值：', validators=[Required()], render_kw={"placeholder": ""})
    zero = StringField('操作时零点值：', validators=[Required()], render_kw={"placeholder": ""})
    submit = SubmitField('提交信息')

    def __init__(self, current_user, *args, **kwargs):
        super(OperationForm, self).__init__(*args, **kwargs)
        self.eqp.choices = [(e.EID, e.EID) for e in eqp_find(current_user)]


class HistoryForm(Form):
    startdate = StringField('起始时间：', validators=[Required()], render_kw={"placeholder": "year-month-day hour:month"})
    enddate = StringField('结束时间：', validators=[Required()], render_kw={"placeholder": "year-month-day hour:month"})
    eqp = SelectField('设备号', coerce=str)
    submit = SubmitField('查询')

    def __init__(self, current_user, *args, **kwargs):
        super(HistoryForm, self).__init__(*args, **kwargs)
        self.eqp.choices = [(e.EID, e.EID) for e in eqp_find(current_user)]
