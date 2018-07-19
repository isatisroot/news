
from flask import session, g
from info.models import User

def do_index_filter(index):
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ''

#在新闻详情页中用于获取用户的登录状态和信息
def login_user_data(func):
    def wrapper(*args, **kwargs):
        user_id = session.get('user.id')
        user = None
        if user_id:
            try:
                from info.models import User
                user = User.query.filter(User.id == user_id).first()
                print(user)
            except Exception as e:
                print(e)
        g.user = user

        return func(*args, **kwargs)

    return wrapper