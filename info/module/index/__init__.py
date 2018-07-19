from flask import Blueprint

#创建一个蓝图对象
index_rule = Blueprint('index', __name__)

from info.module.index.view import *