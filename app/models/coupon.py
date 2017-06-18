#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService

class Coupon(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'coupon'

    coupon_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    cb_id = db.Column(db.Integer, default=0)
    coupon_name = db.Column(db.String(255), default='')
    coupon_amount = db.Column(db.Float, default=0.00)
    begin_time = db.Column(db.Integer, default=0)
    end_time = db.Column(db.Integer, default=0)
    limit_amount = db.Column(db.Float, default=99999.00)
    use_time = db.Column(db.Integer, default=0)
    order_id = db.Column(db.Integer, default=0)
    is_valid = db.Column(db.Integer, default=0)
    limit_goods = db.Column(db.String(255), default='')
    limit_goods_name = db.Column(db.String(255), default='')
    coupon_from = db.Column(db.String(16), default='')
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Coupon => { \
coupon_id:%d, uid:%d, cb_id:%d, coupon_name:'%s', coupon_amount:%0.2f,  \
begin_time:%d, end_time:%d, limit_amount:%0.2f, use_time:%d, order_id:%d,  \
is_valid:%d, limit_goods:'%s', limit_goods_name:'%s', coupon_from:'%s', add_time:%d}" % (
self.coupon_id, self.uid, self.cb_id, self.coupon_name, self.coupon_amount,
self.begin_time, self.end_time, self.limit_amount, self.use_time, self.order_id,
self.is_valid, self.limit_goods, self.limit_goods_name, self.coupon_from, self.add_time)

    __repr__ = __str__


class CouponBatch(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'coupon_batch'

    cb_id = db.Column(db.Integer, primary_key=True)
    cb_name = db.Column(db.String(255), default='')
    coupon_name = db.Column(db.String(100), default=None)
    begin_time = db.Column(db.Integer, default=0)
    end_time = db.Column(db.Integer, default=0)
    is_valid = db.Column(db.Integer, default=0)
    publish_num = db.Column(db.Integer, default=0)
    give_num = db.Column(db.Integer, default=0)
    use_num = db.Column(db.Integer, default=0)
    limit_amount = db.Column(db.Float, default=9999.00)
    coupon_amount = db.Column(db.Float, default=0.00)
    limit_goods = db.Column(db.String(255), default='')
    limit_goods_name = db.Column(db.String(255), default='')
    date_num = db.Column(db.Integer, default=0)
    coupon_from = db.Column(db.String(16), default='')
    valid_days = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "CouponBatch => { \
cb_id:%d, cb_name:'%s', coupon_name:'%s', begin_time:%d, end_time:%d,  \
is_valid:%d, publish_num:%d, give_num:%d, use_num:%d, limit_amount:%0.2f,  \
coupon_amount:%0.2f, limit_goods:'%s', limit_goods_name:'%s', date_num:%d, coupon_from:'%s',  \
valid_days:%d, add_time:%d, update_time:%d}" % (
self.cb_id, self.cb_name, self.coupon_name, self.begin_time, self.end_time,
self.is_valid, self.publish_num, self.give_num, self.use_num, self.limit_amount,
self.coupon_amount, self.limit_goods, self.limit_goods_name, self.date_num, self.coupon_from,
self.valid_days, self.add_time, self.update_time)

    __repr__ = __str__
