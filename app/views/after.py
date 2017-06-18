#!/usr/bin/env python
#coding=utf-8

import time
from decimal import Decimal
from flask import Blueprint, request, session, redirect, current_app, abort, url_for, g, render_template, make_response
from flask.ext.sqlalchemy import Pagination

from codingabc.helpers import log_debug, toint, get_count, log_info
from codingabc.database import db
from app.models.after import After, AfterStep
from app.models.user import User

after = Blueprint('after', __name__)

@after.route('/')
@after.route('/<int:page>')
@after.route('/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """售后列表"""
    g.page_type = 'search'
    g.title = u'售后列表'


    args = request.args
    order_id       = args.get('order_id', '0').strip()
    goods_id       = args.get('goods_id', '0').strip()
    after_type     = args.get('after_type', '-1').strip()
    status         = args.get('status', '-1').strip()
    begin_add_time = args.get('begin_add_time', '').strip()
    end_add_time   = args.get('end_add_time', '').strip()

    q = After.query

    if toint(order_id) > 0:
        q = q.filter(After.order_id == order_id)

    if toint(goods_id) > 0:
        q = q.filter(After.goods_id == goods_id)

    if toint(after_type) > -1:
        q = q.filter(After.after_type == after_type)

    if toint(status) > -1:
        q = q.filter(After.status == status)

    if begin_add_time:
        begin_add_time = time.mktime(time.strptime(begin_add_time,'%Y-%m-%d'))
        q = q.filter(After.add_time >= begin_add_time)

    if end_add_time:
        end_add_time = time.mktime(time.strptime(end_add_time,'%Y-%m-%d')) + 24*3600
        q = q.filter(After.add_time < end_add_time)

    a_count = get_count(q)
    a_list  = q.order_by(After.add_time.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    pagination  = Pagination(None, page, page_size, a_count, None)

    USER_NAME = user_name_dict()
    res = make_response(render_template('after/index.html.j2', a_list=a_list, pagination=pagination, USER_NAME=USER_NAME))
    res.set_cookie('goback_url', request.url)
    return res


def user_name_dict():
    """获取用户名"""
    user_list = User.query.all()
    USER_NAME = {}
    for user in user_list:
        USER_NAME[user.uid] = user.username
    return USER_NAME


@after.route('/detail')
def detail():
    """售后详情"""

    after_id = toint(request.args.get('after_id', '0'))

    if after_id <= 0:
        return u'参数出错'

    a = After.query.get(after_id)

    if not a:
        return u'获取售后详情失败'

    USER_NAME = user_name_dict()

    return render_template('after/detail.html.j2',f=a, **locals())


@after.route('/audit')
def audit():
    """售后审核"""

    args = request.args
    audit_status = toint(args.get('audit_status', '0'))
    after_id     = toint(args.get('after_id', '0'))
    reason       = args.get('reason', '')

    if after_id <= 0:
        return u'参数出错'

    if audit_status not in (0,1):
        return u'审核结果只能是通过或者不通过.'

    if audit_status == 0 and not reason:
        return u'原因不能为空'

    a = After.query.get(after_id)

    if not a:
        return u'获取售后信息失败'

    status = 3 if audit_status == 1 else 2
    a.update(status=status, review_content=reason, update_time=int(time.time()), commit=True)

    return u'ok' if audit_status == 1 else u'not_good'


