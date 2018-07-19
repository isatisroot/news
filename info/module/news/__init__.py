from flask import Blueprint

#创建一个蓝图对象
news_rule = Blueprint('news', __name__, url_prefix='/news')

from info.module.news.view import *