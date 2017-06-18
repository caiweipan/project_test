#!/usr/bin/env python
#coding=utf-8

import time, cookielib, requests, cPickle, json
from decimal import Decimal

from flask import Blueprint, g, request, redirect, url_for, render_template, make_response, session
from flask.ext.sqlalchemy import Pagination
from sqlalchemy import func

from codingabc.database import db
from codingabc.response import ResponseJson
from codingabc.ext.aliyun import AliyunOSS, UploadNotAllowed
from codingabc.helpers import log_debug, log_info, log_error, toint, get_count, randomstr, current_app

from app.helpers.user import get_uid
from app.helpers.common import easy_query_filter, get_params
from app.models.lottery import Lottery, LotteryNumberPool, LotteryNumber, LotteryTemplate
from app.models.goods import Goods
from app.models.user import User, UserTroy
from app.models.order import Order
from app.services.rongcloud import RcGroupService
from app.services.lottery import LotteryStaticService

lottery = Blueprint('lottery', __name__)
resjson = ResponseJson()
resjson.module_code = 13

@lottery.route('/')
@lottery.route('/<int:page>')
@lottery.route('/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """一元云购活动列表"""
    g.page_type = 'search'
    g.title = u'一元云购活动列表'

    param_dict  = get_params({'lottery_id':int,'section_number':int,'goods_id':int,'lottery_name':str,'lottery_status':int, 'begin_add_time':str, 'end_add_time':str})

    query_dict = {'lottery_id':param_dict['lottery_id'],'section_number':param_dict['section_number'],'goods_id':param_dict['goods_id'],'lottery_name':param_dict['lottery_name'],'lottery_status':param_dict['lottery_status'],'begin_add_time':param_dict['begin_add_time'],'end_add_time':param_dict['end_add_time'],}

    q = db.session.query(Lottery.lottery_id, Lottery.section_number, Goods.goods_name, Lottery.goods_id, Lottery.lottery_name, Lottery.lottery_img, Lottery.lottery_price, Lottery.lottery_status, Lottery.schedule, Lottery.announced_time, Lottery.add_time).\
        filter(Lottery.goods_id == Goods.goods_id).\
        filter(Goods.kind == 2)

    q = easy_query_filter(Lottery,q,query_dict)

    lottery_count = get_count(q)
    lottery_list  = q.order_by(Lottery.lottery_id.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    # 商品列表
    goods_id_list = [l.goods_id for l in lottery_list]
    goods_list      = [{'name':u'请选择……', 'value':'-1'}]
    goods_list_temp = db.session.query(Goods.goods_name, Goods.goods_id).\
                                filter(Goods.goods_id.in_(goods_id_list)).\
                                group_by(Goods.goods_id).all()

    for goods in goods_list_temp:
        if goods.goods_name:
            gs = {'name':goods.goods_name, 'value':goods.goods_id}
            goods_list.append(gs)

    pagination  = Pagination(None, page, page_size, lottery_count, None)

    res = make_response(render_template('lottery/index.html.j2', **locals()))
    res.set_cookie('goback_url', request.url)
    return res


@lottery.route('/lottery_detail')
@lottery.route('/lottery_detail/<int:page>')
@lottery.route('/lottery_detail/<int:page>-<int:page_size>')
def lottery_detail(page=1, page_size=30):
    """一元云购活动详情"""
    g.page_type = ''
    g.title = u'一元云购活动详情'

    lottery_id   = toint(request.args.get('lottery_id', '0'))

    lottery_info = Lottery.query.filter(Lottery.lottery_id == lottery_id).first()
    goods_list = Goods.query.filter(Goods.kind == 2).\
                    filter(Goods.is_sale == 1).all()

    if lottery_info is None:
        return u'一元云购活动不存在'

    param_dict  = get_params({'lottery_name':str,'lottery_number':str,'nickname':str,'order_id':int,'is_prize':int,'add_time':str})
    query_dict = {'lottery_number':param_dict['lottery_number'],'order_id':param_dict['order_id'], 'is_prize':param_dict['is_prize'],'add_time':param_dict['add_time']}

    q = db.session.query(LotteryNumber.ln_id, LotteryNumber.order_id, LotteryNumber.lottery_number, LotteryNumber.is_prize, LotteryNumber.add_time,Lottery.lottery_name,User.nickname).\
            filter(Lottery.lottery_id == LotteryNumber.lottery_id).\
            filter(LotteryNumber.uid == User.uid).\
            filter(LotteryNumber.lottery_id == lottery_id)

    q = easy_query_filter(LotteryNumber,q,query_dict)

    if param_dict['nickname']:
        q = q.filter(User.nickname.like(u'%'+param_dict['nickname']+u'%'))

    if param_dict['lottery_name']:
        q = q.filter(Lottery.lottery_name.like(u'%'+param_dict['lottery_name']+u'%'))

    lottery_count = get_count(q)
    lottery_number_list  = q.order_by(LotteryNumber.ln_id.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()
    pagination  = Pagination(None, page, page_size, lottery_count, None)

    return render_template('lottery/add.html.j2', f=lottery_info,**locals())


@lottery.route('/save', methods=['POST'])
def save():
    """保存一元云购活动"""
    g.title     = u'保存一元云购活动'
    g.page_type = ''
    errmsg      = {}
    form        = request.form
    lottery_id      = toint(form.get('lottery_id', '0'))
    section_number  = toint(form.get('section_number', '0'))
    goods_id        = toint(form.get('goods_id', '0'))
    lottery_name    = form.get('lottery_name', '').strip()
    lottery_img     = request.files.get('lottery_img', None)
    lottery_price   = Decimal(form.get('lottery_price', '0.0'))
    max_quantity    = toint(form.get('max_quantity', '0'))
    finish_quantity = toint(form.get('finish_quantity', '0'))

    # 每人最多参与次数 不能大于 达到开奖人次数量
    if max_quantity > finish_quantity:
        max_quantity = u'每人最多参与次数 不能大于 达到开奖人次数量'
        g.errmsg = errmsg
        return render_template('lottery/add.html.j2', f=form,**locals())

    # 检查 - 封面原图是否合法
    if lottery_img:
        oss = AliyunOSS('lottery', current_app.config['SAVE_TARGET_PATH'])
        try:
            oss.save(lottery_img)
            lottery_img = oss.put_to_oss()
        except UploadNotAllowed, e:
            errmsg['lottery_img'] = u'图片只允许是图片文件'
        except Exception, e:
            errmsg['lottery_img'] = u'图片上传失败'

    if errmsg:
        g.errmsg = errmsg
        log_debug('errmsg:%s'%g.errmsg)
        return render_template('lottery/add.html.j2', f=form,**locals())

    lottery_info = Lottery.get_or_404(lottery_id)
    if not lottery_info:
        return u'获取一元购信息失败'

    lottery_number_pool_list = LotteryNumberPool.query.filter(LotteryNumberPool.lottery_id == lottery_info.lottery_id).all()
    diff_finish_quantity = finish_quantity - len(lottery_number_pool_list)

    if finish_quantity >= 100:
        # 获取当前一元云购号码池表数据条数
        max_lottery_number = db.session.query(LotteryNumberPool.lottery_number).\
                                order_by(LotteryNumberPool.lnp_id.desc()).first()
        lnp_list = LotteryNumberPool.query.all()

        # 获取最大一元云购号码
        max_lottery_number = toint(max_lottery_number.lottery_number) if max_lottery_number else 0
        lottery_number = max_lottery_number if max_lottery_number > 10000000 else 10000000

        # 如果修改的达到开奖人次数量比之前的大就增加一元云购号码池表数据
        if diff_finish_quantity > 0:
            for diff in range(diff_finish_quantity):
                lottery_number += 1
                LotteryNumberPool.create(lottery_id=lottery_info.lottery_id,lottery_number=lottery_number)

    # 如果修改的达到开奖人次数量比之前的小就删除一元云购号码池表数据
    # if diff_finish_quantity < 0:
    #     for diff in range(abs(diff_finish_quantity)):
    #         max_lottery_number_list=db.session.query(func.max(LotteryNumberPool.lottery_number)).\
    #                                 filter(LotteryNumberPool.lottery_id == lottery_info.lottery_id).all()
    #         max_lottery_number = LotteryNumberPool.query.filter(LotteryNumberPool.lottery_number.in_([toint(lnp) for lnp in max_lottery_number_list])).first()
    #         if max_lottery_number:
    #             db.session.delete(max_lottery_number)
    goods = Goods.get(goods_id)
    lottery_info.update(section_number=section_number,
                        goods_id=goods_id,
                        lottery_img=lottery_img if lottery_img else lottery_info.lottery_img,
                        lottery_price=lottery_price,
                        max_quantity=max_quantity,
                        finish_quantity=finish_quantity,
                        lottery_name=lottery_name if lottery_name else goods.goods_name,
                        commit=True)

    return redirect(url_for('lottery.index'))


@lottery.route('/number')
@lottery.route('/number/<int:page>')
@lottery.route('/number/<int:page>-<int:page_size>')
def number_index(page=1, page_size=20):
    """一元云购号码列表"""
    g.page_type = 'search'
    g.title = u'一元云购号码列表'



    res = make_response(render_template('lottery/number_index.html.j2', **locals()))
    res.set_cookie('goback_url', request.url)
    return res


@lottery.route('/temp_list')
@lottery.route('/temp_list/<int:page>')
@lottery.route('/temp_list/<int:page>-<int:page_size>')
def temp_list(page=1, page_size=20):
    """一元云购模板列表"""
    g.page_type = 'search'
    g.title = u'一元云购模板列表'
    g.add_new = True
    g.button_name = u'新增一元云购模板'

    param_dict  = get_params({'lt_id':int,'section_number':int,'goods_id':int,'lottery_name':str, 'begin_add_time':str, 'end_add_time':str})

    query_dict = {'lt_id':param_dict['lt_id'],'section_number':param_dict['section_number'],'goods_id':param_dict['goods_id'],'lottery_name':param_dict['lottery_name'],'begin_add_time':param_dict['begin_add_time'],'end_add_time':param_dict['end_add_time'],}

    q = db.session.query(LotteryTemplate.lt_id, LotteryTemplate.section_number, Goods.goods_name, LotteryTemplate.goods_id, LotteryTemplate.lottery_name, LotteryTemplate.lottery_img, LotteryTemplate.lottery_price, LotteryTemplate.add_time).\
        filter(LotteryTemplate.goods_id == Goods.goods_id).\
        filter(Goods.kind == 2)

    q = easy_query_filter(LotteryTemplate,q,query_dict)

    # 商品列表
    goods_list      = [{'name':u'请选择……', 'value':'-1'}]
    goods_list_temp = db.session.query(Goods.goods_name, Goods.goods_id).\
                                group_by(Goods.goods_id).all()

    for goods in goods_list_temp:
        gs = {'name':goods.goods_name, 'value':goods.goods_id}
        goods_list.append(gs)

    lottery_temp_count = get_count(q)
    lottery_temp_list  = q.order_by(LotteryTemplate.lt_id.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()
    pagination  = Pagination(None, page, page_size, lottery_temp_count, None)

    res = make_response(render_template('lottery/temp_list.html.j2', **locals()))
    res.set_cookie('goback_url', request.url)
    return res


@lottery.route('/lottery_temp_detail')
@lottery.route('/lottery_temp_detail/<int:page>')
@lottery.route('/lottery_temp_detail/<int:page>-<int:page_size>')
def lottery_temp_detail(page=1,page_size=20):
    """一元云购活动模板详情"""
    g.page_type = ''
    g.title = u'一元云购活动模板详情'

    lt_id   = toint(request.args.get('lt_id', '0'))

    lottery_temp_info = LotteryTemplate.query.filter(LotteryTemplate.lt_id == lt_id).first()
    goods_list = Goods.query.filter(Goods.kind == 2).\
                    filter(Goods.is_sale == 1).all()

    if lottery_temp_info is None:
        return u'一元云购活动模板不存在'

    param_dict  = get_params({'lottery_id':int,'section_number':int,'query_goods_id':int,'lottery_name':str,'lottery_status':int, 'begin_add_time':str, 'end_add_time':str})

    query_dict = {'lottery_id':param_dict['lottery_id'],'section_number':param_dict['section_number'],'goods_id':param_dict['query_goods_id'],'lottery_name':param_dict['lottery_name'],'lottery_status':param_dict['lottery_status'],'begin_add_time':param_dict['begin_add_time'],'end_add_time':param_dict['end_add_time'],}

    q = db.session.query(Lottery.lottery_id, Lottery.section_number, Goods.goods_name, Lottery.goods_id, Lottery.lottery_name, Lottery.lottery_img, Lottery.lottery_price, Lottery.lottery_status, Lottery.schedule, Lottery.announced_time, Lottery.add_time).\
        filter(Lottery.goods_id == Goods.goods_id).\
        filter(Goods.kind == 2).\
        filter(Lottery.lt_id == lt_id)

    q = easy_query_filter(Lottery,q,query_dict)

    # 商品列表
    goods_query_list      = [{'name':u'请选择……', 'value':'-1'}]
    goods_query_list_temp = db.session.query(Goods.goods_name, Goods.goods_id).\
                                group_by(Goods.goods_id).all()

    for goods in goods_query_list_temp:
        gs = {'name':goods.goods_name, 'value':goods.goods_id}
        goods_query_list.append(gs)

    lottery_count = get_count(q)
    lottery_list  = q.order_by(Lottery.lottery_id.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()
    pagination  = Pagination(None, page, page_size, lottery_count, None)

    return render_template('lottery/add_template.html.j2', f=lottery_temp_info,**locals())


@lottery.route('/add_template')
def add_template():
    """新增一元云购活动"""
    g.title = u'新增一元云购活动'
    g.page_type = ''

    goods_list = Goods.query.filter(Goods.kind == 2).\
                    filter(Goods.is_sale == 1).all()
    return render_template('lottery/add_template.html.j2', f={'lt_id':0},**locals())


@lottery.route('/save_temp', methods=['POST'])
def save_temp():
    """保存一元云购活动"""
    g.title     = u'保存一元云购活动'
    g.page_type = ''
    errmsg      = {}
    param_dict  = get_params({'lt_id':int,'section_number':int,'goods_id':int,'lottery_name':str,'lottery_img':None, 'lottery_price':Decimal, 'max_quantity':int, 'finish_quantity':int})
    lt_id = param_dict['lt_id']
    is_new = True if lt_id <= 0 else False
    goods_list = Goods.query.filter(Goods.kind == 2).\
                    filter(Goods.is_sale == 1).all()
    finish_quantity=param_dict['finish_quantity']

    if finish_quantity < 1:
        errmsg['finish_quantity'] = u'达到开奖人次数量不能小于1'

    required_param_list = ['goods_id', 'lottery_price', 'max_quantity','finish_quantity']

    form = request.form
    for param in required_param_list:
        val = request.form.get(param, '')
        val = val.strip()
        if not val:
            errmsg[param] = u'必填项'
            g.errmsg = errmsg
            log_debug('errmsg:%s'%g.errmsg)
            return render_template('lottery/add_template.html.j2', f=form,**locals())

    goods = Goods.query.get_or_404(param_dict['goods_id'])

    # 每人最多参与次数 不能大于 达到开奖人次数量
    if param_dict['max_quantity'] > finish_quantity:
        errmsg['max_quantity'] = u'每人最多参与次数 不能大于 达到开奖人次数量'
        g.errmsg = errmsg
        return render_template('lottery/add_template.html.j2', f=form,**locals())

    # 检查 - 封面原图是否合法
    lottery_img = param_dict['lottery_img']
    if lottery_img:
        oss = AliyunOSS('lottery', current_app.config['SAVE_TARGET_PATH'])
        try:
            oss.save(lottery_img)
            lottery_img = oss.put_to_oss()
        except UploadNotAllowed, e:
            errmsg['lottery_img'] = u'图片只允许是图片文件'
        except Exception, e:
            errmsg['lottery_img'] = u'图片上传失败'

    if errmsg:
        g.errmsg = errmsg
        log_debug('errmsg:%s'%g.errmsg)
        return render_template('lottery/add_template.html.j2', f=form,**locals())

    section_number=param_dict['section_number']

    if is_new:
        section_number = 2  # 模板下期期数
        lt = LotteryTemplate.create(add_time=int(time.time()), commit=True)
        lottery_info = Lottery.create(section_number=1,goods_id=param_dict['goods_id'], lottery_img=lottery_img if lottery_img else '', lottery_name=goods.goods_name, lottery_price=param_dict['lottery_price'], lottery_status=1, max_quantity=param_dict['max_quantity'], remain_quantity=finish_quantity, finish_quantity=finish_quantity,lt_id=lt.lt_id if lt else 0, add_time=int(time.time()))

        lottery_number_pool_list = LotteryNumberPool.query.filter(LotteryNumberPool.lottery_id == lottery_info.lottery_id).all()
        diff_finish_quantity = finish_quantity - len(lottery_number_pool_list)

        max_lottery_number_list = db.session.query(func.max(LotteryNumberPool.lottery_number)).all()
        lnp_list = LotteryNumberPool.query.all()

        # 获取最大一元云购号码
        if len(lnp_list) > 0:
            for lnp in max_lottery_number_list:
                max_lottery_number = lnp
                lottery_number = toint(max_lottery_number) if toint(max_lottery_number) > 10000000 else 10000000
        else:
            lottery_number = 10000000

        # 如果修改的达到开奖人次数量比之前的大就增加一元云购号码池表数据
        if diff_finish_quantity > 0:
            for diff in range(diff_finish_quantity):
                lottery_number += 1
                LotteryNumberPool.create(lottery_id=lottery_info.lottery_id,lottery_number=lottery_number)

        # 如果修改的达到开奖人次数量比之前的小就删除一元云购号码池表数据
        # if diff_finish_quantity < 0:
        #     for diff in range(abs(diff_finish_quantity)):
        #         max_lottery_number_list=db.session.query(func.max(LotteryNumberPool.lottery_number)).\
        #                                 filter(LotteryNumberPool.lottery_id == lt.lottery_id).all()
        #         max_lottery_number = LotteryNumberPool.query.filter(LotteryNumberPool.lottery_number.in_([toint(lnp) for lnp in max_lottery_number_list])).first()
        #         if max_lottery_number:
        #             db.session.delete(max_lottery_number)
    else:
        lt = LotteryTemplate.query.get_or_404(lt_id)


    if lottery_img:
        lt.update(lottery_img=lottery_img)

    lt.update(lottery_name=goods.goods_name, lottery_desc=goods.goods_desc)

    lt.update(section_number=section_number, goods_id=param_dict['goods_id'],lottery_price=param_dict['lottery_price'], finish_quantity=finish_quantity, max_quantity=param_dict['max_quantity'], commit=True)

    return redirect(url_for('lottery.temp_list'))


@lottery.route('/goods_name')
def goods_name():
    """返回商品名称"""

    resjson.action_code = 11

    goods_id = toint(request.args.get('goods_id', '0'))

    if goods_id < -1:
        return resjson.print_json(11, u'参数出错')

    goods = Goods.query.get(goods_id)
    if not goods:
        return resjson.print_json(12, u'找不到商品')

    return resjson.print_json(0, u'%s'% goods.goods_name)


@lottery.route('/join', methods=['POST'])
def join():
    """ ajax 马甲用户参与云购 """
    resjson.action_code = 10

    total, errmsg = 0, u''

    form = request.form
    lottery_id    = toint(form.get('lottery_id', 0))
    join_quantity = toint(form.get('join_quantity', 0))

    if lottery_id <= 0:
        return resjson.print_json(10, u'错误的一元云购活动ID')

    if join_quantity <= 0:
        return resjson.print_json(11, u'参与总人次必须大于或等于0')

    troy_list     = db.session.query(UserTroy.uid).order_by(UserTroy.uid.desc()).all()
    troy_uid_list = [troy.uid for troy in troy_list]

    dict_list = LotteryStaticService.random_join(troy_uid_list, join_quantity, [])
    for d in dict_list:
        uid     = d['uid']
        buy_num = d['buy_num']
        troy    = UserTroy.get(uid)
        cookies = cPickle.loads(str(troy.cookies_obj))

        # 创建订单
        uri     = '%s/order/lottery/create' % current_app.config['API_DOMAIN']
        data    = {'lottery_id':lottery_id, 'buy_num':buy_num}
        res     = requests.post(uri, data=data, cookies=cookies)

        if res.status_code == 200:
            data = res.json()
            if data['ret'] == 0:
                # 支付订单
                tran_id = data['data']['tran']['tran_id']
                uri     = '%s/pay/balance/req?tran_id=%s' % (current_app.config['API_DOMAIN'], tran_id)
                res     = requests.get(uri, cookies=cookies)

                if res.status_code == 200:
                    data = res.json()
                    if data['ret'] == 0:
                        errmsg = u''
                    else:
                        errmsg = data['msg']
                else:
                    errmsg = u'支付订单网络错误'
            else:
                errmsg = data['msg']
        else:
            errmsg = u'创建订单网络错误'

        if errmsg:
            break

        total += buy_num

    return resjson.print_json(0, u'ok', {'total':total, 'errmsg':errmsg})




