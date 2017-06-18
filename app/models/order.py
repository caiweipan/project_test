#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService

class Order(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'order'

    order_id = db.Column(db.Integer, primary_key=True)
    tran_id = db.Column(db.Integer, default=0)
    uid = db.Column(db.Integer, default=0)
    order_type = db.Column(db.Integer, default=0)
    order_status = db.Column(db.Integer, default=0)
    order_desc = db.Column(db.String(255), default='')
    user_remark = db.Column(db.Text, default=None)
    goods_amount = db.Column(db.Float, default=0.00)
    goods_name_list = db.Column(db.Text, default=None)
    goods_img_list = db.Column(db.Text, default=None)
    goods_price_list = db.Column(db.Text, default=None)
    goods_num_list = db.Column(db.Text, default=None)
    lottery_id_list = db.Column(db.Text, default=None)
    lottery_name_list = db.Column(db.Text, default=None)
    lottery_img_list = db.Column(db.Text, default=None)
    section_number_list = db.Column(db.Text, default=None)
    order_amount = db.Column(db.Float, default=0.00)
    discount_amount = db.Column(db.Float, default=0.00)
    discount_desc = db.Column(db.String(255), default='')
    pay_amount = db.Column(db.Float, default=0.00)
    pay_method = db.Column(db.String(16), default='')
    pay_type = db.Column(db.Integer, default=0)
    pay_status = db.Column(db.Integer, default=0)
    pay_tran_id = db.Column(db.String(32), default='')
    paid_time = db.Column(db.Integer, default=0)
    paid_amount = db.Column(db.Float, default=0.00)
    shipping_id = db.Column(db.Integer, default=0)
    shipping_name = db.Column(db.String(32), default='')
    shipping_code = db.Column(db.String(20), default='')
    shipping_amount = db.Column(db.Float, default=0.00)
    shipping_sn = db.Column(db.String(32), default='')
    shipping_status = db.Column(db.Integer, default=0)
    shipping_time = db.Column(db.Integer, default=0)
    deliver_status = db.Column(db.Integer, default=0)
    deliver_time = db.Column(db.Integer, default=0)
    milestone_status = db.Column(db.Integer, default=0)
    milestone_text = db.Column(db.String(20), default='')
    is_comment = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Order => { \
order_id:%d, tran_id:%d, uid:%d, order_type:%d, order_status:%d,  \
order_desc:'%s', user_remark:'%s', goods_amount:%0.2f, goods_name_list:'%s', goods_img_list:'%s',  \
goods_price_list:'%s', goods_num_list:'%s', lottery_id_list:'%s', lottery_name_list:'%s', lottery_img_list:'%s',  \
section_number_list:'%s', order_amount:%0.2f, discount_amount:%0.2f, discount_desc:'%s', pay_amount:%0.2f,  \
pay_method:'%s', pay_type:%d, pay_status:%d, pay_tran_id:'%s', paid_time:%d,  \
paid_amount:%0.2f, shipping_id:%d, shipping_name:'%s', shipping_code:'%s', shipping_amount:%0.2f,  \
shipping_sn:'%s', shipping_status:%d, shipping_time:%d, deliver_status:%d, deliver_time:%d,  \
milestone_status:%d, milestone_text:'%s', is_comment:%d, add_time:%d, update_time:%d}" % (
self.order_id, self.tran_id, self.uid, self.order_type, self.order_status,
self.order_desc, self.user_remark, self.goods_amount, self.goods_name_list, self.goods_img_list,
self.goods_price_list, self.goods_num_list, self.lottery_id_list, self.lottery_name_list, self.lottery_img_list,
self.section_number_list, self.order_amount, self.discount_amount, self.discount_desc, self.pay_amount,
self.pay_method, self.pay_type, self.pay_status, self.pay_tran_id, self.paid_time,
self.paid_amount, self.shipping_id, self.shipping_name, self.shipping_code, self.shipping_amount,
self.shipping_sn, self.shipping_status, self.shipping_time, self.deliver_status, self.deliver_time,
self.milestone_status, self.milestone_text, self.is_comment, self.add_time, self.update_time)

    __repr__ = __str__


class OrderAddress(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'order_address'

    oa_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, default=0)
    name = db.Column(db.String(32), default='')
    mobile = db.Column(db.String(15), default='')
    province = db.Column(db.String(32), default='')
    city = db.Column(db.String(32), default='')
    district = db.Column(db.String(32), default='')
    address = db.Column(db.String(255), default='')
    zip = db.Column(db.String(8), default='')
    oa_type = db.Column(db.Integer, default=0)

    def __str__(self):
        return "OrderAddress => { \
oa_id:%d, order_id:%d, name:'%s', mobile:'%s', province:'%s',  \
city:'%s', district:'%s', address:'%s', zip:'%s', oa_type:%d}" % (
self.oa_id, self.order_id, self.name, self.mobile, self.province,
self.city, self.district, self.address, self.zip, self.oa_type)

    __repr__ = __str__


class OrderGoods(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'order_goods'

    og_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, default=0)
    goods_id = db.Column(db.Integer, default=0)
    goods_name = db.Column(db.String(255), default='')
    goods_img = db.Column(db.String(255), default='')
    goods_num = db.Column(db.Integer, default=0)
    goods_price = db.Column(db.Float, default=0.00)
    gs_id = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(255), default='')
    sku_name = db.Column(db.String(255), default='')
    lottery_id = db.Column(db.Integer, default=0)
    section_number = db.Column(db.Integer, default=0)
    comment_id = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    after_valid_time = db.Column(db.Integer, default=0)
    after_num = db.Column(db.Integer, default=0)

    def __str__(self):
        return "OrderGoods => { \
og_id:%d, order_id:%d, goods_id:%d, goods_name:'%s', goods_img:'%s',  \
goods_num:%d, goods_price:%0.2f, gs_id:%d, sku:'%s', sku_name:'%s',  \
lottery_id:%d, section_number:%d, comment_id:%d, add_time:%d, after_valid_time:%d,  \
after_num:%d}" % (
self.og_id, self.order_id, self.goods_id, self.goods_name, self.goods_img,
self.goods_num, self.goods_price, self.gs_id, self.sku, self.sku_name,
self.lottery_id, self.section_number, self.comment_id, self.add_time, self.after_valid_time,
self.after_num)

    __repr__ = __str__


class OrderIndex(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'order_index'

    order_id = db.Column(db.Integer, primary_key=True)

    def __str__(self):
        return "OrderIndex => { \
order_id:%d}" % (
self.order_id)

    __repr__ = __str__


class OrderTran(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'order_tran'

    tran_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    pay_amount = db.Column(db.Float, default=0.00)
    pay_status = db.Column(db.Integer, default=0)
    paid_time = db.Column(db.Integer, default=0)
    pay_tran_id = db.Column(db.String(32), default='')
    pay_method = db.Column(db.String(16), default='')
    order_id_list = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "OrderTran => { \
tran_id:%d, uid:%d, pay_amount:%0.2f, pay_status:%d, paid_time:%d,  \
pay_tran_id:'%s', pay_method:'%s', order_id_list:'%s', add_time:%d}" % (
self.tran_id, self.uid, self.pay_amount, self.pay_status, self.paid_time,
self.pay_tran_id, self.pay_method, self.order_id_list, self.add_time)

    __repr__ = __str__


class OrderTranIndex(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'order_tran_index'

    tran_id = db.Column(db.Integer, primary_key=True)

    def __str__(self):
        return "OrderTranIndex => { \
tran_id:%d}" % (
self.tran_id)

    __repr__ = __str__
