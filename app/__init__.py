#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mongoengine import MongoEngine
from config import config
from flask_login import LoginManager

bootstrap = Bootstrap()
db = MongoEngine()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'


def creat_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    from .main import main as main_blueprint
    from .user import user as user_blueprint
    from .enginer import engineer as engineer_blueprint
    # from .report import report as report_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(user_blueprint, url_prefix='/user')
    app.register_blueprint(engineer_blueprint, url_prefix='/engineer')
    # app.register_blueprint(report_blueprint, url_prefix='/report')
    return app
