from info.constants import CLICK_RANK_MAX_NEWS, HOME_PAGE_MAX_NEWS
from info.module.index import index_rule
from flask import render_template, session, current_app, request, jsonify
import logging

from info.response_code import RET


@index_rule.route('/')
def index():
    from info.models import News, Category
    categorys = Category.query.all()
    # 查询点击排行榜前十列信息
    news_list_click =News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)



    user_id = session.get('user.id')
    # print(user_id)
    user = None
    if user_id:
        try:
            from info.models import User
            user = User.query.get(user_id)
            # print(user)
        except Exception as e:
            print(e)

    return render_template('news/index.html', user = user, news_list_click = news_list_click, categorys = categorys)

# 给当前的主页返回一个图标
@index_rule.route('/favicon.ico')
def get_favicon():
    # 将本地资源图片返还给浏览器
    # current_app 等价于 app =Flask（__name__）
    # send_static_file 将静态资源图片返回给浏览器
    return current_app.send_static_file('news/favicon.ico')

@index_rule.route('/newslist')
def get_news_list():
    """
       获取指定分类的新闻列表
       1. 获取参数
       2. 校验参数
       3. 查询数据
       4. 返回数据
       :return:
       """
    req_dict = request.args
    cid = req_dict.get('cid', 1)
    page = req_dict.get('page', 1)
    per_page = req_dict.get('per_page', HOME_PAGE_MAX_NEWS)

    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        print(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数格式错误')
    from info.models import News, Category
    news_list = None
    if cid == 1:
        news_list = News.query.order_by(News.create_time.desc()).paginate(page, per_page, False)
    else:
        news_list = News.query.filter(News.category_id == cid)\
                              .order_by(News.create_time.desc())\
                              .paginate(page, per_page, False)

    news_li = []
    for news in news_list.items:
        news_li.append(news.to_basic_dict())

    currentPage = news_list.page
    totalPage = news_list.pages

    return jsonify(errno=RET.OK,
                   errmsg='发送成功',
                   cid = cid,
                   currentPage = currentPage,
                   totalPage = totalPage,
                   newsList = news_li)

