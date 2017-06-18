#!/usr/bin/env python
#coding=utf-8

import time
from sqlalchemy import and_, or_

from flask import Blueprint, request, session, redirect, current_app, abort, url_for, g, render_template, make_response
from flask.ext.sqlalchemy import Pagination

from codingabc.helpers import log_debug, get_count, toint, log_info
from codingabc.database import db

from app.helpers.date_time import str2timestamp, current_timestamp
from app.helpers.common import get_params, easy_query_filter
from app.models.user import User, UserDevice
from app.models.order import Order, OrderAddress, OrderGoods, OrderIndex, OrderTran, OrderTranIndex
from app.models.coupon import Coupon
from app.models.shipping import Shipping
from app.models.goods import Goods
from app.models.lottery import Lottery, LotteryTemplate, LotteryNumber, LotteryNumberPool
from app.services.kuaidi100 import KuaiDi100StaticMethodsService
from app.services.user import get_user_data

order = Blueprint('order', __name__)

@order.route('/lottery_index/')
@order.route('/lottery_index/<int:page>')
@order.route('/lottery_index/<int:page>-<int:page_size>')
def lottery_index(page=1, page_size=20):
    """一元购订单列表"""
    g.title     = u'一元购订单列表'
    g.page_type = 'search'

    param_dict  = get_params({'order_id':int,'order_status':int,'section_number_list':str,'order_amount':int,'begin_paid_time':str,'end_paid_time':str,'shipping_sn':str,'shipping_status':int,'deliver_status':int,'is_comment':int,'begin_add_time':str,'end_add_time':str,'lt_id':int, 'lottery_id':int, 'is_prize':int, 'tran_id':int, 'pay_status':int})

    query_dict = {'order_id':param_dict['order_id'],'order_status':param_dict['order_status'],'order_amount':param_dict['order_amount'], 'shipping_sn':param_dict['shipping_sn'],'shipping_status':param_dict['shipping_status'],'deliver_status':param_dict['deliver_status'],'is_comment':param_dict['is_comment'], 'begin_add_time':param_dict['begin_add_time'],'end_add_time':param_dict['end_add_time'], 'begin_paid_time':param_dict['begin_paid_time'], 'end_paid_time':param_dict['end_paid_time'], 'pay_status':param_dict['pay_status']}

    section_number = 0
    if param_dict['lottery_id']:
        lottery = Lottery.query.get(param_dict['lottery_id'])
        section_number = lottery.section_number if lottery else 0

    q = db.session.query(Order.order_id, Order.order_status, Order.order_desc, Order.pay_status, Order.section_number_list, Order.order_amount, Order.shipping_sn, Order.shipping_status, Order.deliver_status, Order.is_comment, Order.add_time, Order.paid_time, LotteryNumber.is_prize,LotteryNumber.ln_id).outerjoin(LotteryNumber,and_(Order.order_id == LotteryNumber.order_id)).\
        group_by(Order.order_id.desc())

    # 筛选是否中奖
    is_prize = param_dict['is_prize']
    is_prize_list = [is_prize] if is_prize >= 0 else [0,1]
    if len(is_prize_list) == 1:
        q = db.session.query(LotteryNumber.is_prize,LotteryNumber.ln_id, Order.order_status, Order.order_desc, Order.section_number_list, Order.order_amount, Order.shipping_sn, Order.shipping_status, Order.deliver_status, Order.is_comment, Order.add_time, Order.paid_time, Order.order_id).\
            outerjoin(Order,and_(Order.order_id == LotteryNumber.order_id, LotteryNumber.is_prize.in_(is_prize_list)))

    if section_number > 0:
        q = q.filter(Order.section_number_list == section_number)

    if param_dict['tran_id'] > 0:
        g.title = u'交易订单列表'
        q = q.filter(Order.tran_id == param_dict['tran_id'])
    else:
        q = q.filter(Order.order_type == 3)

    q = easy_query_filter(Order,q,query_dict)

    # 一元购活动模板列表
    lottery_template_list = [{'name':u'请选择活动模板……', 'value':''}]
    lottery_template_list_temp = db.session.query(LotteryTemplate.lt_id, LotteryTemplate.lottery_name).\
                                    filter(LotteryTemplate.lottery_name != '').all()

    for lottery_template in lottery_template_list_temp:
        template = {'name':lottery_template.lottery_name, 'value':lottery_template.lt_id}
        lottery_template_list.append(template)

    # 活动期数列表
    section_number_list = [{'name':u'请选择活动期数……', 'value':''}]
    section_number_list_temp = db.session.query(Lottery.lottery_id, Lottery.section_number).\
                                filter(Lottery.lt_id == param_dict['lt_id']).all()

    for section_number in section_number_list_temp:
        section_number = {'name':section_number.section_number, 'value':section_number.lottery_id}
        section_number_list.append(section_number)

    order_count = get_count(q)
    order_list = q.order_by(Order.add_time.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    pagination  = Pagination(None, page, page_size, order_count, None)

    res = make_response(render_template('order/lottery_index.html.j2',lottery_template_list=lottery_template_list,section_number_list=section_number_list,order_list=order_list, pagination=pagination, is_prize_list=is_prize_list,f={'lt_id':'', 'lottery_id':''}))
    res.set_cookie('goback_url', request.url)
    return res


@order.route('/ordinary_list/')
@order.route('/ordinary_list/<int:page>')
@order.route('/ordinary_list/<int:page>-<int:page_size>')
def ordinary_list(page=1, page_size=20):
    """普通订单列表"""
    g.title     = u'普通订单列表'
    g.page_type = 'search'

    param_dict  = get_params({'order_id':int,'order_status':int,'pay_status':int, 'order_amount':int,'begin_paid_time':str,'end_paid_time':str,'shipping_sn':str,'shipping_status':int,'deliver_status':int,'is_comment':int,'begin_add_time':str,'end_add_time':str})

    query_dict = {'order_id':param_dict['order_id'],'pay_status':param_dict['pay_status'], 'order_status':param_dict['order_status'],'order_amount':param_dict['order_amount'], 'shipping_sn':param_dict['shipping_sn'],'shipping_status':param_dict['shipping_status'],'deliver_status':param_dict['deliver_status'],'is_comment':param_dict['is_comment'], 'begin_add_time':param_dict['begin_add_time'],'end_add_time':param_dict['end_add_time'], 'begin_paid_time':param_dict['begin_paid_time'], 'end_paid_time':param_dict['end_paid_time']}

    q = db.session.query(Order.order_id, Order.uid, Order.order_status, Order.order_desc, Order.order_amount, Order.shipping_sn, Order.shipping_status, Order.deliver_status, Order.is_comment, Order.add_time, Order.paid_time, Order.pay_status).\
        filter(Order.uid == User.uid).\
        filter(Order.order_type == 1)

    q = easy_query_filter(Order,q,query_dict)

    order_count = get_count(q)
    order_list = q.order_by(Order.add_time.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    (USERNAME, MOBILE, NICKNAME, AVATAR, REALNAME, GENDER) = get_user_data()
    pagination  = Pagination(None, page, page_size, order_count, None)

    res = make_response(render_template('order/ordinary_list.html.j2',f={'lt_id':'', 'lottery_id':''}, **locals()))
    res.set_cookie('goback_url', request.url)
    return res


@order.route('/recharge_list')
@order.route('/recharge_list/<int:page>')
@order.route('/recharge_list/<int:page>-<int:page_size>')
def recharge_list(page=1, page_size=20):
    """充值订单列表"""
    g.title     = u'充值订单列表'
    g.page_type = 'search'

    param_dict  = get_params({'order_id':int,'order_status':int,'order_amount':int,'begin_paid_time':str,'end_paid_time':str,'begin_add_time':str,'end_add_time':str})

    query_dict = {'order_id':param_dict['order_id'],'order_status':param_dict['order_status'],'order_amount':param_dict['order_amount'], 'begin_add_time':param_dict['begin_add_time'],'end_add_time':param_dict['end_add_time'], 'begin_paid_time':param_dict['begin_paid_time'], 'end_paid_time':param_dict['end_paid_time']}

    q = db.session.query(Order.order_id, Order.order_status, Order.order_desc, Order.order_amount, Order.shipping_sn, Order.shipping_status, Order.deliver_status, Order.is_comment, Order.add_time, Order.pay_type, Order.paid_time, Order.paid_amount).\
        filter(Order.order_type == 2)

    q = easy_query_filter(Order,q,query_dict)

    order_count = get_count(q)
    order_list = q.order_by(Order.add_time.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    pagination  = Pagination(None, page, page_size, order_count, None)

    res = make_response(render_template('order/recharge_list.html.j2',
            order_list=order_list, pagination=pagination,f={'lt_id':'', 'lottery_id':''}))
    res.set_cookie('goback_url', request.url)
    return res


@order.route('/detail')
def detail():
    """订单详情"""
    g.title = u'订单详情'
    g.page_type = ''

    order_id   = toint(request.args.get('order_id', '0'))
    is_diliver = toint(request.args.get('is_diliver', '0'))

    if order_id <= 0:
        return u'参数出错'

    order_info = Order.query.get_or_404(order_id)
    if not order_info:
        return u'找不到订单信息'

    user = User.query.get(order_info.uid)
    if not user:
        return u'找不到对应的用户'
    user_device = UserDevice.query.filter(UserDevice.uid == user.uid).first()

    order_goods_list = OrderGoods.query.filter(OrderGoods.order_id == order_id).all()
    for order_goods in order_goods_list:
        lottery = Lottery.query.get(order_goods.lottery_id)
        order_goods.lottery_name = lottery.lottery_name if lottery else ''
    address = OrderAddress.query.filter(OrderAddress.order_id == order_id).first()

    coupon_list = Coupon.query.filter(Coupon.order_id == order_info.order_id).all()
    shipping_list    = Shipping.query.order_by(Shipping.shipping_id.desc()).all()

    data, status_text = KuaiDi100StaticMethodsService.search(order_info.shipping_code, order_info.shipping_sn)
    log_info('### data:%s, status_text:%s'%(data, status_text))
    if order_info.order_type not in (0,1,2,3):
        return u'找不到订单类型'

    if order_info.order_type == 2:
        g.title = u'充值订单详情'
        return render_template('order/recharge_detail.html.j2', order=order_info,**locals())

    if order_info.order_type == 3:
        g.title = u'一元购订单详情'
        return render_template('order/lottery_detail.html.j2', order=order_info,**locals())

    g.title = u'普通订单详情'
    return render_template('order/ordinary_detail.html.j2', order=order_info,**locals())


@order.route('/tran_list')
@order.route('/tran_list/<int:page>')
@order.route('/tran_list/<int:page>-<int:page_size>')
def order_tran_list(page=1, page_size=20):
    """订单交易列表"""
    g.title     = u'订单交易列表'
    g.page_type = 'search'

    param_dict  = get_params({'tran_id':int,'pay_status':int,'begin_paid_time':str,'end_paid_time':str, 'begin_add_time':str, 'end_add_time':str, 'order_id':int})

    query_dict = {'tran_id':param_dict['tran_id'], 'pay_status':param_dict['pay_status'],'begin_paid_time':param_dict['begin_paid_time'],'end_paid_time':param_dict['end_paid_time'],'begin_add_time':param_dict['begin_add_time'],'end_add_time':param_dict['end_add_time'],}

    q = OrderTran.query
    q = easy_query_filter(OrderTran,q,query_dict)

    order_id = param_dict['order_id']
    if order_id > 0:
        q = q.filter(or_(OrderTran.order_id_list.like(u'%'+'%d,'%order_id+u'%'), OrderTran.order_id_list.like(u'%'+',%d,'%order_id+u'%'),OrderTran.order_id_list.like(u'%'+',%d'%order_id+u'%'), OrderTran.order_id_list.like(u'%'+'%d'%order_id+u'%')))

    tran_count = get_count(q)
    order_tran_list = q.order_by(OrderTran.add_time.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    for tran in order_tran_list:
        uid = tran.uid
        user_info = User.query.get(uid)
        tran.nickname = user_info.nickname if user_info else ''

    pagination  = Pagination(None, page, page_size, tran_count, None)

    res = make_response(render_template('order/tran_list.html.j2',
            order_tran_list=order_tran_list, pagination=pagination))
    res.set_cookie('goback_url', request.url)
    return res


@order.route('/tran_detail')
def tran_detail():
    """交易订单详情"""

    g.title     = u'交易订单详情'
    g.page_type = 'search'

    tran_id = toint(request.args.get('tran_id'))
    tran_info = OrderTran.query.get(tran_id)

    if not tran_info:
        return u'交易不存在'

    order_id_list = tran_info.order_id_list.split(',')

    return redirect(url_for('order.lottery_index',tran_id=tran_id))


@order.route('/section_number/options', methods=['POST'])
def html_section_number_options():
    """一元购活动期数选择"""

    lt_id = toint(request.form.get('lt_id', '0'))

    if lt_id <= 0:
        return u'参数出错'

    section_number_list = Lottery.query.filter(Lottery.lt_id == lt_id).all()
    return render_template('order/section_number_options.html.j2',section_number_list=section_number_list)


@order.route('/prize_detail')
def prize_detail():
    """中奖订单详情"""

    g.title = u'中奖订单详情'
    g.pay_type = ''

    ln_id = toint(request.args.get('ln_id', '0'))

    if ln_id <= 0:
        return u'参数出错'

    # 抽奖号码信息
    lottery_number = LotteryNumber.query.get_or_404(ln_id)
    user = User.query.get(lottery_number.uid)

    lottery_number.nickname = user.nickname if user else ''
    lottery = Lottery.query.get(lottery_number.lottery_id)
    lottery_number.lottery_name = lottery.lottery_name if lottery else ''

    order = Order.query.get_or_404(lottery_number.order_id)

    user_device = UserDevice.query.filter(UserDevice.uid == user.uid).first()

    #订单商品列表
    order_goods_list = OrderGoods.query.filter(OrderGoods.order_id == order.order_id).all()
    for goods in order_goods_list:
        lottery = Lottery.query.get(goods.lottery_id)
        goods.lottery_name = lottery.lottery_name if lottery else ''

    # 抽奖号码池列表
    lottery_number_pool_list = LotteryNumberPool.query.filter(LotteryNumberPool.lottery_id == lottery_number.lottery_id).all()
    for number in lottery_number_pool_list:
        number_lottery_info = Lottery.query.get(number.lottery_id)
        number.lottery_name = number_lottery_info.lottery_name if number_lottery_info else ''
        number.prize = 'yes' if lottery_number.lottery_number == number.lottery_number else 'no'

    address          = OrderAddress.query.filter(OrderAddress.order_id == order.order_id).filter(OrderAddress.oa_type == 1).first()
    coupon_list      = Coupon.query.filter(Coupon.order_id == order.order_id).all()
    bill_address     = OrderAddress.query.filter(OrderAddress.order_id == order.order_id).filter(OrderAddress.oa_type == 2).first()
    shipping_list    = Shipping.query.order_by(Shipping.shipping_id.desc()).all()

    return render_template('order/prize_detail.html.j2',**locals())


@order.route('/shipping/<int:order_id>', methods=['POST'])
def shipping(order_id):
    """订单发货 """

    shipping_sn = request.form.get('shipping_sn', '').strip()
    # ln_id  = toint(request.args.get('ln_id', '0'))
    order_type = toint(request.args.get('order_type', '0')) # 订单类型 1.一元购订单 2.普通订单
    if not shipping_sn:
        return u'发货单号是必填项'

    shipping_id = toint(request.form.get('shipping_id', 0))
    # log_info('### ln_id:%s, shipping_id:%s, shipping_sn:%s'%(ln_id, shipping_id, shipping_sn))

    shipping    = Shipping.get(shipping_id)
    if not shipping and order_type == 1:
        return u'错误的物流快递ID'

    is_shipping_sn = Order.query.filter(Order.shipping_sn == shipping_sn).first()

    # if is_shipping_sn:
    #     return u'快递单号：%s已经存在'%shipping_sn

    order_info = Order.query.filter(Order.order_id == order_id).first_or_404()
    order_goods_list = OrderGoods.query.filter(OrderGoods.order_id == order_id).all()
    for og in order_goods_list:
        goods = Goods.query.get(og.goods_id)
        if goods and goods.is_return == 1:
            AFTER_FRESH_VALID_DAYS = current_app.config['AFTER_FRESH_VALID_DAYS']
            AFTER_COMMON_VALID_DAYS = current_app.config['AFTER_COMMON_VALID_DAYS']
            VALID_DAYS = AFTER_FRESH_VALID_DAYS if goods.is_fresh == 1 else AFTER_COMMON_VALID_DAYS
            og.update(after_valid_time=int(time.time()) + 60*60*24*VALID_DAYS)

    # if order_info.pay_status != 2:
    #     return u'还未付款，无需发货'

    if order_info.shipping_status == 2:
        return u'此订单已经发过货了，无需再发货'

    if order_type == 1:
        order_info.update(shipping_id=shipping_id,
                        shipping_name=shipping.shipping_name,
                        shipping_code=shipping.shipping_code,
                        shipping_sn=shipping_sn,
                        shipping_amount=0,
                        shipping_status=2,
                        shipping_time=current_timestamp(),
                        deliver_status=1,
                        commit=True)

        # return redirect(url_for('order.prize_detail', order_id=order_id, ln_id=ln_id))
        return redirect(url_for('order.lottery_index', order_id=order_id))
    else:
        order_info.update(shipping_time=current_timestamp(),
                        shipping_sn=shipping_sn,
                        shipping_status=2,
                        deliver_status=1,
                        commit=True)

        return redirect(url_for('order.detail', order_id=order_id))


@order.route('/delivery_list/')
@order.route('/delivery_list/<int:page>')
@order.route('/delivery_list/<int:page>-<int:page_size>')
def delivery_list(page=1, page_size=20):
    """发货订单列表"""
    g.title     = u'发货订单列表'
    g.page_type = 'search'

    param_dict  = get_params({'order_id':int,'order_type':int,'begin_paid_time':str,'end_paid_time':str,'begin_add_time':str,'end_add_time':str})

    query_dict = {'order_id':param_dict['order_id'],'order_type':param_dict['order_type'],'begin_add_time':param_dict['begin_add_time'],'end_add_time':param_dict['end_add_time'], 'begin_paid_time':param_dict['begin_paid_time'], 'end_paid_time':param_dict['end_paid_time']}

    q = db.session.query(Order.order_id, Order.uid, Order.order_status, Order.order_desc, Order.order_amount, Order.shipping_sn, Order.shipping_status, Order.deliver_status, Order.is_comment, Order.add_time, Order.paid_time, Order.pay_status, Order.order_type).\
        filter(Order.uid == User.uid).\
        filter(Order.pay_status == 2).\
        filter(Order.shipping_status == 1).\
        filter(Order.deliver_status == 0).\
        filter(Order.order_type != 2)

    q = easy_query_filter(Order,q,query_dict)

    order_count = get_count(q)
    order_list = q.order_by(Order.add_time.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    (USERNAME, MOBILE, NICKNAME, AVATAR, REALNAME, GENDER) = get_user_data()
    pagination  = Pagination(None, page, page_size, order_count, None)

    res = make_response(render_template('order/delivery_list.html.j2',f={'lt_id':'', 'lottery_id':''}, **locals()))
    res.set_cookie('goback_url', request.url)
    return res
