#!/usr/bin/env python
#coding=utf-8

import time, hashlib, requests, cPickle
from decimal import Decimal

from flask import Blueprint, g, request, redirect, url_for, render_template, make_response, session, current_app
from flask.ext.sqlalchemy import Pagination

from codingabc.database import db
from codingabc.ext.aliyun import AliyunOSS, UploadNotAllowed
from codingabc.helpers import log_debug, log_info, log_error, toint, get_count, randomstr

from app.helpers.user import get_uid, create_salt, create_password
from app.helpers.date_time import current_timestamp
from app.helpers.common import easy_query_filter, get_params, menu
from app.services.user import SaveUserSalonService
from app.services.rongcloud import RcGroupService
from app.models.user import User, UserAccount, UserAccountDetail, UserTroy, UserPassword
from app.models.role import Role
from app.models.question import Question, QuestionAnswer, QuestionGallery
from app.helpers.common import list_pagination
from app.services.get_data import get_role_list, user_role_id_list

user = Blueprint('user', __name__)


@user.route('/')
@user.route('/<int:page>')
@user.route('/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """用户列表"""
    g.page_type = 'search'
    g.title = u'用户列表'

    args     = request.args
    mobile   = args.get('mobile', '').strip()
    nickname = args.get('nickname', '').strip()
    gender   = toint(args.get('gender', '0'))

    q = User.query

    if gender > 0:
        q = q.filter(User.gender == gender)

    if nickname:
        like_nickname = u'%' + nickname + u'%'
        q = q.filter(User.nickname.like(like_nickname))

    if mobile:
        like_mobile = u'%' + mobile + u'%'
        q = q.filter(User.mobile.like(like_mobile))

    user_count = get_count(q)
    user_list  = q.order_by(User.uid.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    pagination = Pagination(None, page, page_size, user_count, None)

    res = make_response(render_template('user/index.html.j2',
                user_list=user_list, pagination=pagination))
    res.set_cookie('goback_url', request.url)
    return res


@user.route('/user_detail/')
@user.route('/user_detail/<int:page>')
@user.route('/user_detail/<int:page>-<int:page_size>')
def user_detail(page=1, page_size=20):
    """用户详情"""
    g.page_type = ''
    g.title = u'用户详情'

    uid    = toint(request.args.get('uid', '0'))
    check_type = request.args.get('check_type', '1')
    user_info = User.query.filter(User.uid == uid).first()

    if user_info is None:
        return u'用户不存在'

    user_acount_info = UserAccount.query.filter(UserAccount.uid == User.uid).\
                        filter(UserAccount.uid == user_info.uid).first()

    user_acount_detail_list = UserAccountDetail.query.filter(UserAccountDetail.uid == User.uid).\
                                filter(User.uid == user_info.uid).all()


    pagination_info = list_pagination(user_acount_detail_list, page,page_size)

    user_acount_detail_list = pagination_info[0]
    pagination = pagination_info[1]

    q = Question.query.filter(Question.uid == User.uid).\
                    filter(Question.uid == uid)
    q_count = get_count(q)
    q_pagination = Pagination(None, page, page_size, q_count, None)

    question_list = q.order_by(Question.add_time.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    return render_template('user/detail.html.j2',
                            user=user_info,
                            ua=user_acount_info,
                            user_acount_detail_list=user_acount_detail_list,
                            pagination=pagination,
                            check_type=check_type,
                            q_pagination = q_pagination,
                            question_list=question_list)


@user.route('/troy/list')
@user.route('/troy/list/<int:page>')
@user.route('/troy/list/<int:page>-<int:page_size>')
def troy_list(page=1, page_size=20):
    """ 马甲用户列表 """
    g.page_type = 'search'
    g.title     = u'马甲用户列表'
    g.add_new = True
    g.button_name = u'添加马甲用户'
    args = request.args
    uid      = toint(args.get('uid', 0))
    nickname = args.get('nickname', '').strip()

    q = db.session.query(UserTroy.add_time, User.uid, User.nickname, User.avatar).\
                filter(UserTroy.uid == User.uid)

    if uid:
        q = q.filter(UserTroy.uid == uid)

    if nickname:
        like_nickname = u'%' + nickname + u'%'
        q = q.filter(User.nickname.like(like_nickname))

    troy_count = get_count(q)
    troy_list  = q.order_by(UserTroy.uid.desc()).\
                        offset((page-1)*page_size).limit(page_size).all()

    pagination = Pagination(None, page, page_size, troy_count, None)

    res = make_response(render_template('user/troy_list.html.j2', troy_list=troy_list, pagination=pagination))
    res.set_cookie('goback_url', request.url)
    return res


@user.route('/troy/add')
def troy_add():
    """ 增加马甲用户 """
    g.page_type = 'form'
    g.title     = u'增加马甲用户'

    return render_template('user/troy_info.html.j2', f={})


@user.route('/troy/edit/<int:uid>')
def troy_edit(uid):
    """ 编辑马甲用户 """
    g.page_type = 'form'
    g.title     = u'编辑马甲用户'

    user = User.get(uid)
    if not user:
        return u'找不到用户'

    troy = UserTroy.get(uid)
    if not troy:
        return u'找不到用户'

    return render_template('user/troy_info.html.j2', f=user)


@user.route('/troy/save', methods=['POST'])
def troy_save():
    """ 保存马甲用户 """
    g.title     = u'保存马甲用户'
    g.page_type = 'form'
    errmsg      = {}

    form = request.form
    uid          = toint(form.get('uid', 0))
    nickname     = form.get('nickname', '').strip()
    current_time = current_timestamp()

    required_param_list = ['nickname']
    form = request.form
    for param in required_param_list:
        val = request.form.get(param, '')
        val = val.strip()
        if not val:
            errmsg[param] = u'必填项'
            g.errmsg = errmsg
            return render_template('goods/goods_category_edit.html.j2', f=form, uid=uid, nickname=nickname)

    is_new = True if uid <= 0 else False

    if is_new:
        avatar    = 'http://img.kapokcloud.com/news/2016-12-13/0739a11b-a0fa-4367-a103-ff5f73b43c6d.png';
        _password = randomstr(8, 0)
        _password = hashlib.sha256(_password).hexdigest()

        # 创建用户
        user = User.create(nickname=nickname, avatar=avatar, commit=True)
        uid  = user.uid

        # 创建马甲用户
        ut = UserTroy.create(uid=uid, password=_password, add_time=current_time, commit=True)

        # 创建密码
        salt     = create_salt()
        password = create_password(_password, salt)
        up       = UserPassword.create(uid=uid, password=password, salt=salt, type=1, commit=True)

        """
        # 登录 - 参数
        uri    = '/user/signin/v2'
        param  = {'uid':uid, 'password':_password, 'method':'POST'}
        method = 'POST'

        # 登录 - 获取API服务实例
        ajs = get_ajs(uri, param, method)

        # 登录 - 调用远程服务
        is_call = ajs.call_service()

        # 登录 - session
        if is_call and ajs.ret == 0:
            cookies     = ajs.get_response_cookie()
            api_session = cookies.get('session', '')
        else:
            user.delete(commit=True)
            up.delete(commit=True)
            ut.delete(commit=True)
            return u'创建马甲用户失败！'
        """
        uri     = '%s/user/signin/v2' % current_app.config['API_DOMAIN']
        data    = {'uid':uid, 'password':_password}
        res     = requests.post(uri, data=data)
        cookies = res.cookies
        cookies = cPickle.dumps(cookies)

        # 创建用户帐户
        UserAccount.create(uid=uid, balance=Decimal('0.00'), add_time=current_time, update_time=current_time)

        # 更新马甲用户
        ut.update(cookies_obj=cookies)
    else:
        user = User.get(uid)

    user.update(nickname=nickname)

    db.session.commit()

    return redirect(url_for('user.troy_list'))


@user.route('/question_detail')
@user.route('/question_detail/<int:page>')
@user.route('/question_detail/<int:page>-<int:page_size>')
def question_detail(page=1, page_size=20):
    """回答详情"""
    g.page_type = ''
    g.title     = u'回答详情'

    args = request.args
    question_id = toint(args.get('question_id', '0'))
    uid         = toint(args.get('uid', '0'))
    check_type  = toint(args.get('check_type', '1'))
    query_type  = toint(args.get('query_type', '1'))

    user = User.get(uid)
    if not user:
        return u'找不到用户'

    question = Question.get(question_id)
    if not question:
        return u'找不到提问的问题'

    qa_query = QuestionAnswer.query.filter(QuestionAnswer.uid == uid).\
                filter(QuestionAnswer.question_id == question_id)

    qa_count = get_count(qa_query)

    qa_list  = qa_query.order_by(QuestionAnswer.add_time.desc()).\
                        offset((page-1)*page_size).limit(page_size).all()

    pagination = Pagination(None, page, page_size, qa_count, None)

    return render_template('user/question_detail.html.j2', f=question, **locals())


@user.route('/change_role')
def change_role():
    """角色切换"""

    role_id = toint(request.args.get('role_id', '0'))
    uid     = session.get('uid')
    if role_id <= 0:
        return u'参数出错'

    role = Role.get(role_id)

    if not role and role_id != 1:
        return u'切换的角色不存在'

    role_id_list = user_role_id_list(uid)
    role_id_list.remove(role_id) #去除角色列表中的已切换的角色
    session['menu'] = menu(role_id)
    session['role_id'] = role_id
    session['role_name'] = u'超级管理员' if role_id == 1 else role.role_name
    session['role_temp_list'] = get_role_list(role_id_list)

    return u'ok'
