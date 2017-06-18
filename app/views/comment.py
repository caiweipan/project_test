#!/usr/bin/env python
#coding=utf-8
import json, time
from hashlib import md5

from flask import Blueprint, session, request, render_template, make_response, g, url_for, redirect
from flask.ext.sqlalchemy import Pagination

from codingabc.database import db
from codingabc.ext.aliyun import AliyunOSS, UploadNotAllowed
from app.helpers.date_time import str2timestamp
from app.helpers.common import easy_query_filter, get_params
from codingabc.helpers import toint, get_count, log_info, randomstr, log_debug, ismobile, randomstr, current_app

from app.models.comment import Comment
from app.models.user import User
from app.models.sys import SysRegion
from app.models.goods import Goods
from app.models.order import Order, OrderAddress, OrderGoods, OrderIndex, OrderTran, OrderTranIndex
from app.services.comment import GoodsCommentSaveService
from app.services.push import XingePushService


comment = Blueprint('comment', __name__)

@comment.route('/goods')
@comment.route('/goods/<int:page>')
@comment.route('/goods/<int:page>-<int:page_size>')
def goods_index(page=1, page_size=20):
    """商品评价列表"""
    g.title     = u'商品评价列表'
    g.page_type = 'search'

    args = request.args
    goods_id       = toint(args.get('goods_id', '0'))
    goods_name = args.get('goods_name', '')

    q = Goods.query

    if goods_id > 0:
        q = q.filter(Goods.goods_id == goods_id)

    if goods_name:
        q = q.filter(Goods.goods_name.like(u'%'+goods_name+u'%'))

    goods_count = get_count(q)
    goods_list = q.order_by(Goods.goods_id.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    pagination  = Pagination(None, page, page_size, goods_count, None)
    res = make_response(render_template('comment/goods_index.html',
            goods_list=goods_list, pagination=pagination))
    res.set_cookie('goback_url', request.url)
    return res


@comment.route('/goods_detail/<int:goods_id>')
def goods_detail(goods_id):
    """商品评价详情"""
    g.title = u'商品评价详情'
    g.page_type = ''

    goods_comment_list = Comment.query.filter(Comment.tid == Goods.goods_id).\
                            filter(Comment.tid == goods_id).\
                            order_by(Comment.comment_id.desc()).all()

    goods_info = Goods.query.get(goods_id)
    if not goods_info:
        return u'找不到对应的商品'
    return render_template('comment/goods_detail.html', **locals())


@comment.route('/goods_add/<int:goods_id>', methods=['GET', 'POST'])
def goods_add(goods_id):
    """新增评价"""
    g.title = u'新增评价'
    g.page_type = ''
    goods_id = goods_id

    return render_template('comment/goods_add.html', f={}, goods_id=goods_id)


@comment.route('/goods/edit')
def goods_edit():
    """编辑商品评价"""
    g.title = u'编辑商品评价'
    g.page_type = ''
    comment_id = toint(request.args.get('comment_id', '0'))
    goods_id   = toint(request.args.get('goods_id', '0'))
    if comment_id <= 0 or goods_id <= 0:
        return u'参数出错'
    c_info = Comment.query.get(comment_id)

    if not c_info:
        return u'找不到评价'

    return render_template('comment/goods_edit.html.j2', f=c_info,**locals())


@comment.route('/goods/edit/save', methods=['POST', 'GET'])
def goods_edit_save():
    """保存编辑商品评价"""
    g.title     = u'保存编辑商品评价'
    g.page_type = ''
    errmsg      = {}

    param_dict  = get_params({'comment_id':int,'goods_id':int,'tname':str,'timg':None,'star':int,'content':str, 'add_time':str})

    required_param_list = ['comment_id', 'tname','star', 'content','add_time']

    for param in required_param_list:
        val = request.form.get(param, '')
        val = val.strip()
        if not val:
            errmsg[param] = u'必填项'
            g.errmsg = errmsg
            log_debug('errmsg:%s'%g.errmsg)
            return render_template('comment/goods_edit.html.j2', f=form,**locals())

    # 检查 - 封面原图是否合法
    timg = param_dict['timg']
    if timg:
        oss = AliyunOSS('comment', current_app.config['SAVE_TARGET_PATH'])
        try:
            oss.save(timg)
            timg = oss.put_to_oss()
        except UploadNotAllowed, e:
            errmsg['timg'] = u'图片只允许是图片文件'
        except Exception, e:
            errmsg['timg'] = u'图片上传失败'

    if errmsg:
        g.errmsg = errmsg
        log_debug('errmsg:%s'%g.errmsg)
        return render_template('comment/goods_edit.html.j2', f=form,**locals())

    comment_id = param_dict['comment_id']
    is_new = True if comment_id <= 0 else False

    if is_new:
        comment_info = Comment.create(add_time=int(time.time()))
    else:
        comment_info = Comment.get(comment_id)

    if timg:
        comment_info.update(timg=timg)

    comment_info.update(tname=param_dict['tname'], star=param_dict['star'], content=param_dict['content'], add_time=param_dict['add_time'],commit=True)

    return redirect(url_for('comment.goods_detail',goods_id=param_dict['goods_id']))



@comment.route('/goods_save', methods=['POST'])
def goods_save():
    """保存商品信息"""
    g.title = u'新增评价'
    g.page_type = ''

    form     = request.form
    goods_id = toint(form.get('goods_id', '0'))
    gcss     = GoodsCommentSaveService()
    errmsg   = gcss.save(form)

    if errmsg:
        g.errmsg = errmsg
        log_debug(errmsg)

        return render_template('comment/goods_add.html', f=form,goods_id=goods_id)

    return redirect(url_for('comment.goods_detail',goods_id=goods_id))


@comment.route('/goods/delete')
def goods_delete():
    """删除商品评价"""

    comment_id = toint(request.args.get('comment_id', '0'))

    if comment_id <= 0:
        return u'参数出错'

    c_info = Comment.query.get(comment_id)
    if not c_info:
        return u'找不到评价'

    db.session.delete(c_info)
    db.session.commit()

    return redirect(url_for('comment.goods_detail', goods_id=c_info.tid))


@comment.route('/order/')
@comment.route('/order/<int:page>')
@comment.route('/order/<int:page>-<int:page_size>')
def order_index(page=1, page_size=20):
    """订单评价列表"""
    g.title     = u''
    g.page_type = 'search'

    param_dict  = get_params({'mobile':str,'nickname':str,'user_device':str,'order_type':int,'order_status':int,'order_id':str,'order_amount':int,'discount_amount':int,'discount_desc':str,'pay_amount':int,'pay_method':str,'pay_type':int,'pay_status':int,'pay_tran_id':int,'begin_paid_time':str,'end_paid_time':str,'paid_amount':int,'shipping_id':int,'shipping_name':str,'shipping_amount':int,'shipping_sn':str,'shipping_status':int,'shipping_time':str,'deliver_status':int,'deliver_time':str,'milestone_status':int,'milestone_text':str,'is_comment':int,'begin_add_time':str,'end_add_time':str,'update_time':str})

    query_dict = {'order_id':param_dict['order_id'], 'order_type':param_dict['order_type'],'order_status':param_dict['order_status'], 'shipping_sn':param_dict['shipping_sn'],'shipping_status':param_dict['shipping_status'],'deliver_status':param_dict['deliver_status'],'is_comment':param_dict['is_comment'], 'begin_add_time':param_dict['begin_add_time'],'end_add_time':param_dict['end_add_time'],'pay_type':param_dict['pay_type'], 'begin_paid_time':param_dict['begin_paid_time'], 'end_paid_time':param_dict['end_paid_time']}

    q = db.session.query(Order.order_id, User.nickname, Order.order_type, Order.order_status, Order.order_desc, Order.order_amount, Order.shipping_sn, Order.shipping_status, Order.deliver_status, Order.is_comment, Order.add_time, Order.pay_type, Order.paid_time).\
        filter(Order.uid == User.uid)

    q = easy_query_filter(Order,q,query_dict)

    order_count = get_count(q)
    order_list = q.order_by(Order.order_id.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()
    pagination  = Pagination(None, page, page_size, order_count, None)

    res = make_response(render_template('comment/order_index.html',
            order_list=order_list, pagination=pagination))
    res.set_cookie('goback_url', request.url)
    return res


@comment.route('/order_add/<int:order_id>', methods=['GET', 'POST'])
def order_add(order_id):
    """新增订单评价"""
    g.title = u'新增订单评价'
    g.page_type = ''

    return render_template('comment/order_add.html', f={'order_id':order_id})


@comment.route('/order_save', methods=['POST'])
def order_save():
    """保存订单评价"""
    g.title = u'保存订单评价'
    g.page_type = ''

    form = request.form
    ocss   = OrderCommentSaveService()
    errmsg = ocss.save(form)

    if errmsg:
        g.errmsg = errmsg
        log_debug(errmsg)

        return render_template('comment/order_add.html', f=form)
    return redirect(url_for('comment.order_index'))

