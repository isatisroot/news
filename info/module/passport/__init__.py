from flask import Blueprint

#创建一个蓝图对象
passport_blu = Blueprint('passport', __name__, url_prefix='/passport')

from info.module.passport.view import *