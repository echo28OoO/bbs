import os
import uuid
from datetime import datetime
from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
    send_from_directory)
from werkzeug.datastructures import FileStorage

from models import user
from models.reply import Reply
from models.topic import Topic
from models.user import User

from utils import log

main = Blueprint('setting', __name__)


def current_user():
    # 从 session 中找到 user_id 字段, 找不到就 -1
    # 然后用 id 找用户
    # 找不到就返回 None
    uid = session.get('user_id',  -1)
    u = User.one(id=uid)
    return u


"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /setting
"""


@main.route('/')
def index():
    u = current_user()
    username = u.username
    id = u.id
    image = u.image
    signature = u.signature
    return render_template(
        'setting.html',
        user=u,
        image=image,
        username=username,
        id=id,
        signature=signature,
    )


@main.route('/update_username', methods=['POST'])
def update_username():
    form = request.form.to_dict()
    id = form['id']
    username = form['name']
    User.update(id, username=username)
    return redirect(url_for('.index'))


@main.route('/update_signature', methods=['POST'])
def update_signature():
    form = request.form.to_dict()
    id = form['id']
    signature = form['signature']
    User.update(id, signature=signature)
    return redirect(url_for('.index'))


@main.route('/update_password', methods=['POST'])
def update_password():
    form = request.form.to_dict()
    id = form['id']
    u =User.one(id=id)
    old_pass = form['old_pass']
    old_pass = User.salted_password(old_pass)
    if u.password == old_pass:
        new_pass = form['new_pass']
        User.update(id, password=User.salted_password(new_pass))
        return redirect(url_for('.index'))
    else:
        abort(400)


def created_topic(user_id):
    ts = Topic.all(user_id=user_id)
    return ts


def replied_topic(user_id):
    rs = Reply.all(user_id=user_id)
    ts = []
    for r in rs:
        t = Topic.one(id=r.topic_id)
        ts.append(t)
    return ts


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

        return redirect(url_for('.index'))


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


