from datetime import datetime

from flask import current_app, jsonify, request, render_template, make_response, session
from info.constants import IMAGE_CODE_REDIS_EXPIRES, SMS_CODE_REDIS_EXPIRES
from info.libs.yuntongxun.sms import CCP
from info.response_code import RET
from info.utils.captcha.captcha import captcha
from . import passport_blu
from info import db
import re
import random
from info.models import User
from info import create_log


@passport_blu.route('/images_code')
def passport():
    code_id = request.args.get('code_id')
    name, text, image = captcha.generate_captcha()

    try:
        from info import redis_store
        redis_store.set('code_id' + code_id, text, IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        print(e)
        return make_response(jsonify(errno=RET.DATAERR , erromsg="保存图形验证码失败"))

    res = make_response(image)
    res.headers['Content-Type'] = "image/jpg"

    return res

@passport_blu.route('/sms_code', methods=['POST'])
def mobile_passport():
    """
       1. 接收参数并判断是否有值
       2. 校验手机号是正确
       3. 通过传入的图片编码去redis中查询真实的图片验证码内容
       4. 进行验证码内容的比对
       5. 生成发送短信的内容并发送短信
       6. redis中保存短信验证码内容
       7. 返回发送成功的响应
       :return:
       """
    req_dict = request.json
    mobile = req_dict['mobile']
    image_code = req_dict['image_code']
    code_id = req_dict['code_id']

    if not all(['mobile', 'image_code', 'code_id']):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    if not re.match(r"^1[3-9][0-9]{9}$", mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机号码不正确')

    from info import redis_store
    redis_code_id = redis_store.get('code_id' + code_id)

    if not redis_code_id:
        return jsonify(errno=RET.NODATA, errmsg='图形验证码过期')

    if redis_code_id.upper() != image_code.upper():
        return jsonify(errno=RET.NODATA, errmsg='图形验证码输入错误')

    smscode = "%04d" % random.randint(0, 9999)
    print(smscode)
    # result = CCP().send_template_sms(mobile, [smscode, SMS_CODE_REDIS_EXPIRES / 60], 1)
    #
    # if result == -1:
    #     return jsonify(errno=RET.THIRDERR, errmsg='短信发送失败')

    # print('短信发送成功')

    redis_store.set(mobile,smscode,SMS_CODE_REDIS_EXPIRES)
    return jsonify(errno=RET.OK, errmsg='短信发送成功')

@passport_blu.route('/register', methods=['POST'])
def register():
    """
      1. 获取参数和判断是否有值
      2. 从redis中获取指定手机号对应的短信验证码的
      3. 校验验证码
      4. 初始化 user 模型，并设置数据并添加到数据库
      5. 保存当前用户的状态
      6. 返回注册的结果
      :return:
      """
    req_dict = request.json
    mobile = req_dict['mobile']  # mobile    手机号
    smscode = req_dict['smscode']  # smscode    短信验证码
    password = req_dict['password']  # password    密码

    if not all(['moblie', 'smscode', 'password']):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    from info import redis_store
    redis_smscode = redis_store.get(mobile)

    if not redis_smscode:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码过期')

    if redis_smscode.upper() != smscode.upper():
        return jsonify(errno=RET.NODATA, errmsg='图形验证码输入错误')

    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = password   # TODO user.password 在表里没有，而是user.pssword_hash

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify(errno=RET.PARAMERR, errmsg='注册失败')

    session['user.id'] = user.id
    session['user.nick_name'] = mobile
    session['user.mobile'] = mobile

    # 记录最后一次登录时间
    user.last_login = datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        print(e)

    return jsonify(errno=RET.OK, errmsg='注册成功')

@passport_blu.route('/login', methods=['POST'])
def login():
    """
      1. 获取参数和判断是否有值
      2. 从数据库查询出指定的用户
      3. 校验密码
      4. 保存用户登录状态
      5. 返回结果
      :return:
      """
    req_dict = request.json
    mobile = req_dict['mobile']  # mobile    手机号
    password = req_dict['password']

    if not all(['mobile', 'password']):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不足')

    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        print(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据错误')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在或未激活')

    if not user.check_password(password):
        return jsonify(errno=RET.PWDERR, errmsg='密码错误')

    session['user.id'] = user.id
    # print('set')
    session['user.nick_name'] = user.nick_name
    session['mobile'] = mobile

    return jsonify(errno=RET.OK, errmsg='登录成功')

@passport_blu.route('/logout', methods=['POST'])
def logout():

    session.pop('user.nick_name',None)
    session.pop('user.mobile', None)
    session.pop('user.id',None)

    return jsonify(errno=RET.OK, errmsg='OK')