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

    return render_template('news/extend.html',
                           news_list_click = news_list_click,
                           news = news,
                           user =user)