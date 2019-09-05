import os
import uuid

from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
    send_from_directory,
    current_app)
from werkzeug.datastructures import FileStorage

from config import admin_mail
from models.message import Messages
from models.reply import Reply
from models.topic import Topic
from models.user import User
from routes import current_user
# from routes import current_user, cache

import json

from utils import log

main = Blueprint('index', __name__)

"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /profile
"""

import gevent
import time



@main.route("/")
def index():
    # t = threading.Thread()
    # t.start()
    # gevent.spawn()
    time.sleep(0.5)
    u = current_user()
    return render_template("index_1.html", user=u)


@main.route("/register_view")
def register_view():
    # t = threading.Thread()
    # t.start()
    # gevent.spawn()
    time.sleep(0.5)
    u = current_user()
    return render_template("register.html", user=u)


@main.route("/register", methods=['POST'])
def register():
    form = request.form.to_dict()
    # 用类函数来判断
    u = User.register(form)
    return redirect(url_for('.index'))


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    print(form)
    u = User.validate_login(form)
    if u is None:
        return redirect(url_for('.index'))
    else:
        # session 中写入 user_id
        # session_id = str(uuid.uuid4())
        # key = 'session_id_{}'.format(session_id)
        # log('index login key <{}> user_id <{}>'.format(key, u.id))
        # cache.set(key, u.id)
        #
        # redirect_to_index = redirect(url_for('topic.index'))
        # response = current_app.make_response(redirect_to_index)
        # response.set_cookie('session_id', value=session_id)
        # 转到 topic.index 页面
        # return response
        session['user_id'] = u.id
        return redirect(url_for('topic.index'))


def created_topic(user_id):
    # O(n)
    ts = Topic.all(user_id=user_id)
    return ts
    #
    # k = 'created_topic_{}'.format(user_id)
    # if cache.exists(k):
    #     v = cache.get(k)
    #     ts = json.loads(v)
    #     return ts
    # else:
    #     ts = Topic.all(user_id=user_id)
    #     v = json.dumps([t.json() for t in ts])
    #     cache.set(k, v)
    #     return ts


def replied_topic(user_id):
    # O(k)+O(m*n)
    rs = Reply.all(user_id=user_id)
    ts = []
    for r in rs:
        t = Topic.one(id=r.topic_id)
        ts.append(t)
    return ts
    #
    #     sql = """
    # select * from topic
    # join reply on reply.topic_id=topic.id
    # where reply.user_id=1
    # """
    # k = 'replied_topic_{}'.format(user_id)
    # if cache.exists(k):
    #     v = cache.get(k)
    #     ts = json.loads(v)
    #     return ts
    # else:
    #     rs = Reply.all(user_id=user_id)
    #     ts = []
    #     for r in rs:
    #         t = Topic.one(id=r.topic_id)
    #         ts.append(t)
    #
    #     v = json.dumps([t.json() for t in ts])
    #     cache.set(k, v)
    #
    #     return ts
    # ts = Topic.query\
    #     .join(Reply, Topic.id == Reply.topic_id)\
    #     .filter(Reply.user_id == user_id)\
    #     .all()
    # return ts


@main.route('/profile')
def profile():
    print('running profile route')
    u = current_user()
    if u is None:
        return redirect(url_for('.index'))
    else:
        created = created_topic(u.id)
        replied = replied_topic(u.id)
        return render_template(
            'profile.html',
            user=u,
            created=created,
            replied=replied
        )


@main.route('/user/<int:id>')
def user_detail(id):
    u = User.one(id=id)
    if u is None:
        abort(404)
    else:
        return render_template('profile.html', user=u)


@main.route('/image/add', methods=['POST'])
def avatar_add():
    file: FileStorage = request.files['avatar']
    # file = request.files['avatar']
    # filename = file.filename
    # ../../root/.ssh/authorized_keys
    # images/../../root/.ssh/authorized_keys
    # filename = secure_filename(file.filename)
    suffix = file.filename.split('.')[-1]
    if suffix not in ['gif', 'jpg', 'jpeg']:
        abort(400)
        log('不接受的后缀, {}'.format(suffix))
    else:
        filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
        path = os.path.join('images', filename)
        file.save(path)

        u = current_user()
        User.update(u.id, image='/images/{}'.format(filename))

        return redirect(url_for('.profile'))


@main.route('/images/<filename>')
def image(filename):
    # 不要直接拼接路由，不安全，比如
    # http://localhost:3000/images/..%5Capp.py
    # path = os.path.join('images', filename)
    # print('images path', path)
    # return open(path, 'rb').read()
    # if filename in os.listdir('images'):
    #     return
    return send_from_directory('images', filename)


csrf_tokens = dict()


@main.route('/reset/send', methods=['POST'])
def reset():
    form = request.form
    user = form['username']
    u = User.one(username=user)
    token = int(uuid.uuid4())
    csrf_tokens[token] = u.id
    print(csrf_tokens)
    # key = 'token_{}'.format(token)
    # cache.set(key, u.id)
    Messages.send(
        title='重置密码',
        content='http://localhost:3000/reset/view?token={}'.format(token),
        sender_id=u.id,
        receiver_id=u.id,
    )
    return render_template('index_1.html')

@main.route("/reset_view")
def reset_view():
    # t = threading.Thread()
    # t.start()
    # gevent.spawn()
    time.sleep(0.5)
    u = current_user()
    return render_template("reset_view.html", user=u)


@main.route('/reset/view')
def view():
    query = request.args
    token = int(query['token'])
    for k, v in csrf_tokens.items():
        if token == k:
            return render_template(
                'reset.html',
                token=token,
                id=csrf_tokens[token],
            )
        else:
            abort(400)
    # key = 'token_{}'.format(token)
    # if cache.exists(key):
    #     id = cache.get(key)
    #     id = json.loads(id)
    #     return render_template(
    #         'reset.html',
    #         token=token,
    #         id=id,
    #     )
    # else:
    #     abort(404)


@main.route('/reset/update', methods=['POST'])
def update():
    form = request.form
    token = int(form['token'])
    # key = 'token_{}'.format(token)
    password = form['new_pass']
    for k, v in csrf_tokens.items():
        if token == k:
            id = csrf_tokens[k]
            User.update(id, password=User.salted_password(password))
            return render_template(
                'index.html'
            )
        else:
            abort(400)
    # if cache.exists(key):
    #     id = cache.get(key)
    #     id = json.loads(id)
    #     User.update(id, password=User.salted_password(password))
    #     return render_template(
    #         'index.html'
    #     )
    # else:
    #     abort(404)

