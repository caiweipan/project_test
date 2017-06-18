#!/usr/bin/env python
#coding=utf-8

import json
import time
from hashlib import md5
from decimal import Decimal

from flask import request, session, current_app

from codingabc.database import db
from codingabc.helpers import toint, log_debug, log_info, log_error

from app.models.coupon import CouponBatch, Coupon
from app.models.goods import Goods

class CouponSaveService(object):
    """保存优惠券service"""
    def __init__(self):
        self.current_time = int(time.time())
        self.errmsg       = {}
        self.coupon_batch = None
        self.cb_id        = 0


    def _check_param(self, form):
        """检查表单"""
        required_param_list = ['cb_name', 'coupon_name', 'coupon_amount', 'limit_amount',
            'publish_num', 'begin_time', 'end_time', 'is_valid', 'coupon_from', 'valid_days']
        for param in required_param_list:
            val = form.get(param, '')
            val = val.strip()
            if not val:
                self.errmsg[param] = u'必填项'

        # goods_id_list = form.getlist('goods_id')
        # if not goods_id_list:
        #     self.errmsg['submit'] = u'玩儿蛋啊，连一个项目都没有优惠，还设置毛毛啊'

        self.cb_id = toint(form.get('cb_id', '0'))
        if self.cb_id > 0:
            self.coupon_batch = CouponBatch.query.get(self.cb_id)
            if self.coupon_batch is None:
                self.errmsg['submit'] = u'找不到优惠券批次'

        else:
            self.coupon_batch = CouponBatch()
            self.coupon_batch.add_time = self.current_time
            db.session.add(self.coupon_batch)


    def save(self, form):
        """保存优惠券信息"""
        self._check_param(form)
        if self.errmsg:
            return self.errmsg

        cb_name       = form.get('cb_name', '')
        coupon_name   = form.get('coupon_name', '')
        coupon_amount = Decimal(form.get('coupon_amount', '0'))
        limit_amount  = Decimal(form.get('limit_amount', '0'))
        publish_num   = toint(form.get('publish_num', '0'))
        begin_time    = form.get('begin_time', '')
        end_time      = form.get('end_time', '')
        is_valid      = toint(form.get('is_valid', '0'))
        goods_id_list = form.getlist('goods_id')
        goods_id_all  = form.get('goods_id_all', '')
        coupon_from   = form.get('coupon_from', '')
        valid_days    = toint(form.get('valid_days', '0'))

        for k,v in form.items():
            log_info('[SaveCouponBatch] %s:%s' % (k,v))

        begin_time = int(time.mktime(time.strptime(begin_time, '%Y-%m-%d')))
        end_time   = int(time.mktime(time.strptime(end_time, '%Y-%m-%d')))

        limit_goods = 'all'
        limit_goods_name = u'全场通用'
        # if goods_id_all != 'all':
        #     goods_list = Goods.query.all()
        #     if len(goods_id_list) != len(goods_list):
        #         limit_goods = ','.join(goods_id_list)
        #         limit_goods_name = u''

        #         goods_dict = {}
        #         for goods in goods_list:
        #             goods_dict[goods.goods_id] = goods.goods_name

        #         limit_goods_name_list = []
        #         for goods_id in goods_id_list:
        #             goods_id = toint(goods_id)
        #             limit_goods_name_list.append(goods_dict.get(goods_id, ''))

        #         limit_goods_name = ','.join(limit_goods_name_list)

        self.coupon_batch.cb_name          = cb_name
        self.coupon_batch.coupon_name      = coupon_name
        self.coupon_batch.coupon_amount    = coupon_amount
        self.coupon_batch.limit_amount     = limit_amount
        self.coupon_batch.publish_num      = publish_num
        self.coupon_batch.begin_time       = begin_time
        self.coupon_batch.end_time         = end_time
        self.coupon_batch.is_valid         = is_valid
        self.coupon_batch.limit_goods      = limit_goods
        self.coupon_batch.limit_goods_name = limit_goods_name
        self.coupon_batch.coupon_from      = coupon_from
        self.coupon_batch.valid_days       = valid_days
        self.coupon_batch.update_time      = int(time.time())

        update_dict = {'limit_amount':limit_amount,
                         'coupon_name':coupon_name,
                         'coupon_amount':coupon_amount,
                         'begin_time':begin_time,
                         'end_time':end_time,
                         'limit_goods':limit_goods,
                         'limit_goods_name':limit_goods_name,
                         'coupon_from':coupon_from}

        if is_valid == 0:
            update_dict['is_valid'] = 0
        Coupon.query.filter(Coupon.cb_id == self.coupon_batch.cb_id).update(update_dict)
        db.session.commit()
        return {}
