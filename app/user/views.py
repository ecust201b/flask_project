from flask import render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_user, current_user
from flask_login import logout_user, login_required
from . import user
from ..models import User, Factory, Eqp, Role
from .forms import LoginForm, RegisterForm, UserEdit
from .. import db
from ..decorators import admin_required, engineer_required
import logging
import json


@user.route('/login', methods=['GET', 'POST'])
def login():
    # 新增路由函数
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(UID=form.username.data).first()
        if user is None:
            flash('用户名不存在')
        else:
            if user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
            flash('用户名或密码错误')
    return render_template('/user/login.html', form=form)


@user.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已登出')
    return redirect(url_for('main.index'))


@user.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.objects(UID=form.username.data).first():
            flash('工号已被注册')
            pass
        else:
            user = User(UID=form.username.data)
            user.role = Role.objects(RID=form.role.data).get()
            user.factory = Factory.objects(FID=form.factory.data).get()
            user.set_pass(form.password.data)
            user.save()
            flash('注册成功')
            return redirect(url_for('.login'))
    return render_template('/user/register.html', form=form)


@user.route('/manage', methods=['GET', 'POST'])
@login_required
@engineer_required
def manage():
    UserList = User.objects(factory=current_user.factory, role__gt=current_user.role).order_by("+role__RID")
    return render_template('/user/manage.html', UserList=UserList)


@user.route('/editUser/<string:username>', methods=['GET', 'POST'])
@login_required
@engineer_required
def editUser(username):
    user = User.objects(UID=username).get()
    form = UserEdit(current_user)
    if form.validate_on_submit():
        user.UID = form.username.data
        user.role = Role.objects(RID=form.role.data).get()
        user.eqp_list = form.eqp_list.data
        user.save()
        flash("用户资料更新成功")
        return redirect(url_for('user.manage'))
    form.username.data = user.UID
    form.role.data = user.role.RID
    form.eqp_list.data = user.eqp_list
    return render_template('/user/UserEdit.html', form=form)
