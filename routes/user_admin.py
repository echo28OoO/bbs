from datetime import datetime
from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
)

from models import user
from models.reply import Reply
from models.topic import Topic
from models.user import User

from utils import log

main = Blueprint('user_admin', __name__)


def current_user():
    # 从 session 中找到 user_id 字段, 找不到就 -1
    # 然后用 id 找用户
    # 找不到就返回 None
    uid = session.get('user_id', -1)
    u = User.one(id=uid)
    return u


"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /profile
"""


@main.route('/<string:username>')
def index(username):
    u = User.one(username=username)
    image = u.image
    topic = Topic.all(id=u.id)
    reply = Reply.all(id=u.id)
    # 最近回复的话题
    zjcj = []
    for i in reply:
        zjcj.append(Topic.one(id=i.topic_id))
    topic = sorted(
        topic, key=lambda x: x.created_time, reverse=True
    )
    zjcj = sorted(
        zjcj, key=lambda x: x.created_time, reverse=True
    )

    return render_template(
        'user_index.html',
        user=u,
        topic=topic,
        zjcj=zjcj,
        image=image,
    )




