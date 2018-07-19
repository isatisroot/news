import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, make_response, abort
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from redis import StrictRedis

from config import config
from info.module.index import index_rule


db = SQLAlchemy()

def create_log():
    logging.basicConfig(level=logging.DEBUG)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

redis_store = None

def create_app(config_name):
    # create_log()
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    global redis_store
    redis_store = StrictRedis(host=config[config_name].redis_host, port=config[config_name].redis_port, decode_responses=True)
    # print(redis_store)

    CSRFProtect(app)
    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        # response = make_response()   加了这句之后页面显示就为空，为什么？
        response.set_cookie("csrf_token", csrf_token)

        return response

    Session(app)
    app.register_blueprint(index_rule)

    from info.module.passport import passport_blu
    app.register_blueprint(passport_blu)

    from info.module.news import news_rule
    app.register_blueprint(news_rule)

    return app