#!/usr/bin/env python
#coding=utf-8

import time
import random
from sqlalchemy import and_

from flask import Blueprint, request, session, redirect, current_app, abort, url_for, g, make_response, render_template
from flask.ext.sqlalchemy import Pagination

from codingabc.helpers import toint, log_debug, log_info, ismobile, randomstr, get_count, get_today_unixtime
from codingabc.database import db

from app.helpers.common import easy_query_filter
from app.services.coupon import CouponSaveService
from app.services.push import XingePushService
from app.models.goods import Goods
from app.models.user import User
from app.models.coupon import CouponBatch, Coupon

coupon = Blueprint('coupon', __name__)

@coupon.route('/')
@coupon.route('/<int:page>')
@coupon.route('/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """优惠券列表"""
    g.title     = u'优惠券列表'
    g.page_type = 'search'
    g.add_new = True
    g.button_name = u'发放优惠券'

    args = request.args

    cb_name        = args.get('cb_name', '').strip()
    coupon_name    = args.get('coupon_name', '').strip()
    is_valid       = toint(args.get('is_valid', -1))
    begin_add_time = args.get('begin_add_time', '')
    end_add_time   = args.get('end_add_time', '')

    query_dict = {'cb_name':cb_name,'coupon_name':coupon_name,'is_valid':is_valid,'begin_add_time':begin_add_time,'end_add_time':end_add_time,}
    q = CouponBatch.query
    q = easy_query_filter(CouponBatch,q,query_dict)

    coupon_count = get_count(q)
    coupon_list  = q.order_by(CouponBatch.add_time.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()
    pagination  = Pagination(None, page, page_size, coupon_count, None)

    res = make_response(render_template('coupon/index.html', **locals()))
    res.set_cookie('goback_url', request.url)
    return res


@coupon.route('/add', methods=['GET', 'POST'])
def add():
    """发放优惠券"""
    g.title = u'发放优惠券'
    g.page_type = 'form'

    goods_list = Goods.query.order_by(Goods.goods_id.asc()).order_by(Goods.goods_id.asc()).all()

    return render_template('coupon/detail.html', f={'cb_id':0}, goods_list=goods_list)


@coupon.route('/save', methods=['POST'])
def save():
    """保存优惠券"""

    form = request.form
    log_debug(form)
    css = CouponSaveService()
    errmsg = css.save(form)
    if errmsg:
        g.errmsg = errmsg
        goods_list = Goods.query.order_by(Goods.add_time.asc()).order_by(Goods.goods_id.asc()).all()
        return render_template('coupon/detail.html', f=form, goods_list=goods_list)

    return redirect(url_for('coupon.index'))


@coupon.route('/detail/<cb_id>')
def detail(cb_id):
    """编辑优惠券"""
    g.title = u'编辑优惠券'
    g.page_type = 'form'

    cb = CouponBatch.query.get_or_404(cb_id)
    goods_list = Goods.query.order_by(Goods.add_time.desc()).order_by(Goods.goods_id.asc()).all()
    return render_template('coupon/detail.html', f=cb, goods_list=goods_list)


@coupon.route('/give')
def give():
    """赠送优惠券"""

    form = request.form
    cb_id = toint(form.get('cb_id', '0'))
    coupon_id = toint(form.get('coupon_id', '0'))

    g.title     = u'赠送优惠券'
    g.page_type = 'search'

    coupon_batch_list = CouponBatch.query.all()

    return render_template('coupon/give.html', coupon_batch_list=coupon_batch_list, f=form)

@coupon.route('/acquire', methods=['POST'])
def coupon_acquire():
    """获取优惠券"""
    g.page_type = 'form'

    form      = request.form
    mobile    = form.get('mobile', '').strip()
    cb_id     = toint(form.get('cb_id', '0'))
    coupon_id = toint(form.get('coupon_id', '0'))

    if cb_id <= 0:
        return u'参数出错'

    coupon_batch = CouponBatch.query.get(cb_id)
    if coupon_batch is None:
        return u'优惠券批次不存在'

    mobile = mobile.replace('\r', '')
    mobile_list = mobile.split('\n')
    index, mobile_count = 0, len(mobile_list)
    for m in mobile_list:
        if not ismobile(m):
            log_info('[GiveCoupon] mobile is not correct. mobile:%s' % m)

        user = User.query.filter(User.mobile == m).first()
        if user is None:
            log_info('[GiveCoupon] user not found. mobile:%s' % m)
            continue

        # once = User.query.filter(User.uid == Coupon.uid).\
        #         filter(User.mobile == m).\
        #         filter(Coupon.cb_id == cb_id).first()

        # if once is not None:
        #     log_info('[GiveCoupon] user can only get coupon_banch for once. mobile:%s' % m)
        #     continue

        index += 1
        log_info('[GiveCoupon] %d/%d cb_id:%d, mobile:%s' % (index, mobile_count, cb_id, m))

        coupon_batch.give_num += 1
        coupon_batch.update_time = int(time.time())

        begin_time, end_time = coupon_batch.begin_time, coupon_batch.end_time
        if coupon_batch.valid_days > 0:
            begin_time = get_today_unixtime()
            end_time = begin_time + coupon_batch.valid_days*24*60*60

        coupon = Coupon()
        coupon.is_valid         = 1
        coupon.add_time         = int(time.time())
        coupon.uid              = user.uid
        coupon.begin_time       = begin_time
        coupon.end_time         = end_time
        coupon.cb_id            = coupon_batch.cb_id
        coupon.coupon_name      = coupon_batch.coupon_name
        coupon.coupon_amount    = coupon_batch.coupon_amount
        coupon.limit_amount     = coupon_batch.limit_amount
        coupon.limit_goods      = coupon_batch.limit_goods
        coupon.limit_goods_name = coupon_batch.limit_goods_name
        coupon.coupon_from      = coupon_batch.coupon_from
        db.session.add(coupon)
        if index%50 == 0:
            db.session.commit()

        # 发送推送
        xps = XingePushService()
        xps.push_user(user.uid, u'101计划', u'系统赠送您一张'+coupon_batch.coupon_name,
            {'trans_id':0, 'trans_type':'me'}, client_flag='USER')

    if index%50 != 0:
        db.session.commit()

    return redirect(url_for('coupon.user_coupon'))


@coupon.route('/user_coupon/')
@coupon.route('/user_coupon/<int:page>')
@coupon.route('/user_coupon/<int:page>-<int:page_size>')
def user_coupon(page=1, page_size=20):
    """ 用户优惠券 """
    g.title     = u'用户优惠券'
    g.page_type = 'search'

    args = request.args
    uid    = toint(args.get('uid', 0))
    mobile = args.get('mobile', '')
    cb_id  = toint(args.get('cb_id', 0))
    coupon_id = toint(args.get('coupon_id', 0))

    q = Coupon.query

    if uid > 0:
        q = q.filter(Coupon.uid == uid)

    if cb_id:
        q = q.filter(Coupon.cb_id == cb_id)

    if coupon_id:
        q = q.filter(Coupon.coupon_id == coupon_id)

    if mobile:
        q = q.filter(Coupon.uid == User.uid).\
                filter(User.mobile == mobile)

    user_coupon_count = get_count(q)
    user_coupon_list  = q.order_by(Coupon.add_time.desc()).\
                            offset((page-1)*page_size).limit(page_size).all()

    pagination = Pagination(None, page, page_size, user_coupon_count, None)

    res = make_response(render_template('coupon/user_coupon.html.j2',
            user_coupon_list=user_coupon_list, pagination=pagination))
    res.set_cookie('goback_url', request.url)
    return res

