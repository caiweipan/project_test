#!/usr/bin/env python
#coding=utf-8

from hashlib import sha256

from flask import session, abort

from codingabc.helpers import log_debug, log_info, log_error, toint, randomstr

from app.helpers.common import model_to_dict_only


def check_login():
    """ 检查登录 """

    uid = toint(session.get('uid', '0'))
    if uid == 0:
        abort(403)

def set_user_session(u):
    """ 设置用户session值 """
    
    session['uid']      = u.uid
    session['mobile']   = u.mobile
    session['username'] = u.username
    session['nickname'] = u.nickname
    session['avatar']   = u.avatar

def get_uid():
    """ 获取用户uid """

    return toint(session.get('uid', 0))

def get_username():
    """ 获取用户名 """

    return session.get('username', '')

def get_nickname(userinfo=None):
    """ 获取用户昵称 """

    # 从userinfo获取
    if userinfo:
        nickname = userinfo.realname or \
                   userinfo.nickname or \
                   userinfo.username
        if not nickname:
            nickname = '%s****%s' % (userinfo.mobile[:3], userinfo.mobile[-4:])

        return nickname

    # 从session获取 - nickname
    nickname = session.get('nickname', '')
    
    # 从session获取 - username
    if not nickname:
        nickname = session.get('username', '')

    # 从session获取 - mobile
    if not nickname:
        mobile   = session.get('mobile', '')
        nickname = '%s****%s' % (mobile[:3], mobile[-4:])

    return nickname

def get_avatar(userinfo=None):
    """ 获取用户头像 """

    avatar = ''

    if userinfo is not None:
        avatar = userinfo.avatar
    else:
        avatar = session.get('avatar', '')
    
    # 默认头像
    if not avatar:
        avatar = ''

    return avatar

def get_userinfo():
    """ 获取用户信息 """

    u = {}
    u['uid']      = get_uid()
    u['nickname'] = get_nickname()
    u['avatar']   = get_avatar()

    return u

def get_mobile():
    """ 获取用户手机 """

    return session.get("mobile", "0")

def create_salt():
    """ 创建盐 """

    return randomstr(32)

def create_password(password='', salt=''):
    """ 创建密码 """

    return sha256(password+salt).hexdigest()

def user_info_to_api(user_model):
    """ 返回给API的用户信息 """

    only = ['uid', 'mobile', 'mobile_status', 'username', 'nickname', 'realname', 'gender', 'avatar',
            'country', 'province', 'city', 'district', 'desc', 'birthday', 'school', 'industry']

    return model_to_dict_only(user_model, only)




