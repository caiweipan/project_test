#!/usr/bin/env python
#coding=utf-8

import time, json
from hashlib import sha256

from flask import Blueprint, g, request, redirect, url_for, render_template, make_response, session

from codingabc.database import db
from codingabc.helpers import log_debug, log_info, toint, randomstr, get_count

from app.helpers.date_time import current_timestamp
from app.models.user import User, UserPassword, UserCheckCode, UserAdmin
from app.services.yunpian import YunPian
from app.helpers.common import menu
from app.services.get_data import role_name, user_role_id_list, get_role_list

index = Blueprint('index', __name__)

@index.route('/')
def welcome():
    """ 首页 """

    uid = toint(session.get('uid', 0))
    if uid <= 0:
        return redirect(url_for('index.signin'))

    return redirect(url_for('user.index'))


@index.route('/signin', methods=['GET', 'POST'])
def signin():
    """ 登陆 """

    if request.method == 'GET':
        args = request.args
        mobile   = args.get('mobile', '')
        password = args.get('password', '')

        if mobile and password:
            return login_check(mobile,password)

        return render_template('signin.html', f={}, errormsg={})

    form = request.form
    mobile   = form.get('mobile', '')
    password = form.get('password', '')

    if mobile and password:
        return login_check(mobile, password, form)

    return render_template('signin.html', f={}, errormsg={})


@index.route('/signout')
def signout():
    """ 登出 """

    session.clear()

    return redirect('/')


@index.route('/change/password')
def change_password():
    """ 修改密码 """

    args = request.args
    old_password = args.get('old_password', '')
    password1    = args.get('password1', '')
    password2    = args.get('password2', '')
    uid          = session.get('uid')

    if uid <= 0:
        return u'参数出错'

    up = UserPassword.query.filter(UserPassword.uid == uid).first()

    #判断旧密码是否正确
    sha256_old_password = sha256(old_password).hexdigest()
    old_password = sha256(sha256_old_password+up.salt).hexdigest()

    if old_password != up.password:
        return 'error_password'

    salt         = randomstr(32)
    password1    = sha256(password1).hexdigest()
    new_password = sha256(password1+salt).hexdigest()

    up.salt     = salt
    up.password = new_password
    db.session.commit()

    return 'ok'


@index.route('/forget/password')
def forget_password():
    """忘记密码"""

    args     = request.args
    mobile   = args.get('mobile', '')
    code     = args.get('code', '')
    password = args.get('password1', '')

    current_time = current_timestamp()
    ucc = UserCheckCode.query.filter(UserCheckCode.mobile == mobile).\
                filter(UserCheckCode.check_code == code).\
                filter(UserCheckCode.check_type == 2).\
                order_by(UserCheckCode.ucc_id.desc()).first()
    if ucc is None:
        return u'验证码错误'

    if ucc.expire_time < current_time:
        return u'验证码已经过期，请重新获取'

    user = User.query.filter(User.mobile == mobile).first()
    if user is None:
        return u'{mobile}帐号不存在'.format(mobile=mobile)

    up          = UserPassword.query.filter(UserPassword.uid == user.uid).first()
    password    = sha256(password).hexdigest()
    password    = sha256(password+up.salt).hexdigest()
    up.password = password
    db.session.commit()

    return u'ok'


def login_check(mobile='',password='', form={},errmsg=None):
    """ 登陆检查 """

    if not mobile:
        return render_template('signin.html', f=form, errmsg=u'手机号不能为空')

    if not password:
        return render_template('signin.html', f=form, errmsg=u'密码不能为空')

    me = User.query.filter(User.mobile == mobile).first()
    if me is None:
        return render_template('signin.html', f=form, errmsg=u'用户不存在')

    up = UserPassword.query.filter(UserPassword.uid == me.uid).filter(UserPassword.type == 1).first()
    if up is None:
        return render_template('signin.html', f=form, errmsg=u'还没有设置密码')

    sha256_password = sha256(password).hexdigest()
    sha256_password = sha256(sha256_password+up.salt).hexdigest()
    if sha256_password != up.password:
        return render_template('signin.html', f=form, errmsg=u'密码错误')

    ua = UserAdmin.query.filter(UserAdmin.uid == me.uid).first()
    if ua is None:
        return render_template('signin.html', f=form, errmsg=u'您没有权限登录系统，请联系可爱的管理员')

    role_id_list = user_role_id_list(me.uid)
    role_id_list.remove(ua.role_id)
    ROLE_NAME = role_name()

    session['admin_id']     = me.uid
    session['admin_name']   = me.mobile
    session['uid']          = me.uid
    session['mobile']       = mobile
    session['nickname']     = me.nickname
    session['avatar']       = me.avatar
    session['role_id']      = ua.role_id
    session['role_temp_list'] = get_role_list(role_id_list) if len(role_id_list) > 0 else []
    session['role_name']    = ROLE_NAME.get(ua.role_id, '')
    session['menu']         = menu(ua.role_id)

    if not session['menu'] and ua.role_id == 1:
        return redirect(url_for('sys.menu_list'))
    else:
        return redirect(url_for('user.index'))



@index.route('/getcode', methods=['POST'])
def getcode():
    """获取验证码"""
    form = request.form
    mobile = form.get('mobile', '')

    check_type = 2

    # 24小时内不能超过5次获取验证码
    current_time = int(time.time())
    min_time = current_time - 24*60*60
    day_limit_query = UserCheckCode.query.filter(UserCheckCode.mobile == mobile).\
                    filter(UserCheckCode.check_type == check_type).\
                    filter(UserCheckCode.expire_time >= min_time).\
                    filter(UserCheckCode.expire_time < current_time)
    day_sms_count = get_count(day_limit_query)
    if day_sms_count >= 5:
        return u'一天之内只能获取5次验证码，请明天再来获取'

    # 一分钟内不重复发短信
    one_ucc = UserCheckCode.query.filter(UserCheckCode.mobile == mobile).\
            filter(UserCheckCode.check_type == check_type).\
            filter(UserCheckCode.expire_time >= current_time).first()
    if one_ucc is not None:
        return u'请2分钟后再获取'

    code = randomstr(6, 1)
    content = u'【101计划】您的验证码是%s。如非本人操作，请忽略本短信' % (code, )
    log_debug(content)

    sms = YunPian()
    res = sms.send_sms_text(mobile, content)
    result = json.loads(res)
    log_debug(result)
    # if result['code'] != 0:
    #     return u'发送验证码失败，请重新获取。'

    ucc = UserCheckCode()
    ucc.mobile      = mobile
    ucc.check_code  = code
    ucc.expire_time = current_time + 150
    ucc.check_type  = check_type
    db.session.add(ucc)
    db.session.commit()

    return 'ok'


@index.route('/database_clear')
def database_clear():
    import mysql.connector
    args = request.args if request.method == 'GET' else request.form
    table_name_str = args.get('table_name_str', 'user_check_code').strip()
    user = args.get('user', 'root')
    password = args.get('password', '')
    host     = args.get('host', '127.0.0.1')
    database = args.get('database', 'didi_car')
    table_name_list = table_name_str.split(',')
    conn = mysql.connector.connect(user=user, password=password, host=host, database=database)
    cursor = conn.cursor()
    for table_name in table_name_list:
        cursor.execute('truncate table `%s`'% table_name)
        log_info(u'### %s表已经被清空'%table_name)
    # cursor.rowcount
    conn.commit()
    cursor.close()

    return u'ok'
