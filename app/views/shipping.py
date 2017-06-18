#!/usr/bin/env python
#coding=utf-8

import time, json
import urllib, urllib2
import requests
from decimal import Decimal
from flask import Blueprint, request, session, redirect, current_app, abort, url_for, g, render_template, make_response
from flask.ext.sqlalchemy import Pagination

from codingabc.helpers import log_debug, toint, get_count, log_info
from codingabc.database import db
from codingabc.ext.aliyun import AliyunOSS
from codingabc.ext.uploads import UploadNotAllowed
from codingabc.response import ResponseJson

from app.helpers.common import easy_query_filter, get_params
from app.models.shipping import Shipping
from app.services.sys import SaveSysSettingService
from app.models.recharge_card import RechargeCard

resjson = ResponseJson()
resjson.module_code = 12
shipping = Blueprint('shipping', __name__)


@shipping.route('/')
@shipping.route('/<int:page>')
@shipping.route('/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """快递列表"""
    g.page_type = 'search'
    g.title = u'快递列表'
    g.add_new = True
    g.button_name = u'新增快递'

    args = request.args
    shipping_name = args.get('shipping_name', '').strip()
    shipping_code = args.get('shipping_code', '').strip()
    is_default = toint(args.get('is_default', '-1'))

    q = Shipping.query

    if shipping_name:
        q = q.filter(Shipping.shipping_name.like(u'%'+ shipping_name + u'%'))

    if shipping_code:
        q = q.filter(Shipping.shipping_code.like(u'%'+ shipping_code + u'%'))

    if is_default >= 0:
        q = q.filter(Shipping.is_default == is_default)

    s_count = get_count(q)
    shipping_list  = q.order_by(Shipping.shipping_id.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    pagination  = Pagination(None, page, page_size, s_count, None)

    res = make_response(render_template('shipping/index.html.j2',**locals()))
    res.set_cookie('goback_url', request.url)
    return res


@shipping.route('/add', methods=['POST'])
def add():
    """新增快递"""
    form = request.form
    shipping_name = form.get('shipping_name', '')
    shipping_amount = Decimal(form.get('shipping_amount', 0.0))
    free_limit_amount = Decimal(form.get('free_limit_amount', 0.0))
    # tracking_url = form.get('tracking_url', '')
    shipping_code = form.get('shipping_code', '')
    is_default = toint(form.get('is_default', '-1'))
    shipping_desc = form.get('shipping_desc', '')

    Shipping.create(shipping_name=shipping_name,
                shipping_amount=shipping_amount,
                free_limit_amount=free_limit_amount,
                shipping_code=shipping_code,
                is_default=is_default,
                shipping_desc=shipping_desc, commit=True)

    return redirect(url_for('shipping.index'))


@shipping.route('/check_shipping_name')
def check_shipping_name():
    """快递名称检查"""

    resjson.action_code = 11

    args = request.args
    shipping_name = args.get('shipping_name', '')

    shipping = Shipping.query.filter(Shipping.shipping_name == shipping_name).first()

    if shipping:
        return resjson.print_json(10, u'shipping')

    return resjson.print_json(0, u'ok')


@shipping.route('/edit')
def edit():
    """快递编辑"""

    args = request.args
    shipping_id = toint(args.get('shipping_id', '0'))

    s = Shipping.query.get_or_404(shipping_id)

    return render_template('shipping/edit.html.j2',f=s, **locals())


@shipping.route('/save', methods=['POST'])
def save():
    """保存快递信息"""

    form = request.form
    shipping_id = toint(form.get('shipping_id', '0'))
    shipping_name = form.get('shipping_name', '')
    shipping_amount = Decimal(form.get('shipping_amount', 0.0))
    free_limit_amount = Decimal(form.get('free_limit_amount', 0.0))
    tracking_url = form.get('tracking_url', '')
    shipping_code = form.get('shipping_code', '')
    is_default = toint(form.get('is_default', '-1'))
    shipping_desc = form.get('shipping_desc', '')

    if shipping_id > 0:
        s = Shipping.query.get_or_404(shipping_id)
    else:
        s = Shipping.create()

    s.update(shipping_name=shipping_name,
                shipping_amount=shipping_amount,
                free_limit_amount=free_limit_amount,
                tracking_url=tracking_url,
                shipping_code=shipping_code,
                is_default=is_default,
                shipping_desc=shipping_desc, commit=True)

    return redirect(url_for('shipping.index'))
