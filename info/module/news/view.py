from info.constants import CLICK_RANK_MAX_NEWS
from . import news_rule
from flask import render_template, session, g
from info.models import User, News
from info.utils.common import login_user_data

@news_rule.route('/<int:news_id>')
@login_user_data
def news_detail(news_id):
    user = g.user
    news_list_click = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)
    news = News.query.get(news_id)

    # 判断是否收藏该新闻，默认值为 false
    is_collection = False

    # 判断用户是否收藏过该新闻
    if g.user:
        if news in user.collection_news:
            is_collection = True


    return render_template('news/extend.html',
                           news_list_click = news_list_click,
                           news = news,
                           user =user,
                           is_collection = is_collection)

# 前端根据传入值判断显示哪一个a标签，并使用标签记录当前新闻id，以供后续逻辑使用