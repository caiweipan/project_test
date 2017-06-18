#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService

class Lottery(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'lottery'

    lottery_id = db.Column(db.Integer, primary_key=True)
    lt_id = db.Column(db.Integer, default=0)
    section_number = db.Column(db.Integer, default=0)
    goods_id = db.Column(db.Integer, default=0)
    lottery_name = db.Column(db.String(255), default='')
    lottery_desc = db.Column(db.Text, default=None)
    lottery_img = db.Column(db.String(255), default='')
    lottery_price = db.Column(db.Float, default=0.00)
    lottery_status = db.Column(db.Integer, default=0)
    finish_quantity = db.Column(db.Integer, default=0)
    join_quantity = db.Column(db.Integer, default=0)
    remain_quantity = db.Column(db.Integer, default=0)
    max_quantity = db.Column(db.Integer, default=0)
    schedule = db.Column(db.Integer, default=0)
    announced_time = db.Column(db.Integer, default=0)
    prize_number = db.Column(db.Integer, default=0)
    prize_uid = db.Column(db.Integer, default=0)
    prize_nickname = db.Column(db.String(32), default='')
    prize_avatar = db.Column(db.String(128), default='')
    prize_goods_num = db.Column(db.Integer, default=0)
    prize_time = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Lottery => { \
lottery_id:%d, lt_id:%d, section_number:%d, goods_id:%d, lottery_name:'%s',  \
lottery_desc:'%s', lottery_img:'%s', lottery_price:%0.2f, lottery_status:%d, finish_quantity:%d,  \
join_quantity:%d, remain_quantity:%d, max_quantity:%d, schedule:%d, announced_time:%d,  \
prize_number:%d, prize_uid:%d, prize_nickname:'%s', prize_avatar:'%s', prize_goods_num:%d,  \
prize_time:%d, add_time:%d}" % (
self.lottery_id, self.lt_id, self.section_number, self.goods_id, self.lottery_name, 
self.lottery_desc, self.lottery_img, self.lottery_price, self.lottery_status, self.finish_quantity, 
self.join_quantity, self.remain_quantity, self.max_quantity, self.schedule, self.announced_time, 
self.prize_number, self.prize_uid, self.prize_nickname, self.prize_avatar, self.prize_goods_num, 
self.prize_time, self.add_time)

    __repr__ = __str__


class LotteryTemplate(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'lottery_template'

    lt_id = db.Column(db.Integer, primary_key=True)
    section_number = db.Column(db.Integer, default=0)
    goods_id = db.Column(db.Integer, default=0)
    lottery_name = db.Column(db.String(255), default='')
    lottery_desc = db.Column(db.Text, default=None)
    lottery_img = db.Column(db.String(255), default='')
    lottery_price = db.Column(db.Float, default=0.00)
    finish_quantity = db.Column(db.Integer, default=0)
    max_quantity = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "LotteryTemplate => { \
lt_id:%d, section_number:%d, goods_id:%d, lottery_name:'%s', lottery_desc:'%s',  \
lottery_img:'%s', lottery_price:%0.2f, finish_quantity:%d, max_quantity:%d, status:%d,  \
add_time:%d}" % (
self.lt_id, self.section_number, self.goods_id, self.lottery_name, self.lottery_desc, 
self.lottery_img, self.lottery_price, self.finish_quantity, self.max_quantity, self.status, 
self.add_time)

    __repr__ = __str__


class LotteryNumber(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'lottery_number'

    ln_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    lottery_id = db.Column(db.Integer, default=0)
    order_id = db.Column(db.Integer, default=0)
    lottery_number = db.Column(db.Integer, default=0)
    is_prize = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "LotteryNumber => { \
ln_id:%d, uid:%d, lottery_id:%d, order_id:%d, lottery_number:%d,  \
is_prize:%d, add_time:%d}" % (
self.ln_id, self.uid, self.lottery_id, self.order_id, self.lottery_number,
self.is_prize, self.add_time)

    __repr__ = __str__


class LotteryNumberPool(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'lottery_number_pool'

    lnp_id = db.Column(db.Integer, primary_key=True)
    lottery_id = db.Column(db.Integer, default=0)
    lottery_number = db.Column(db.Integer, default=0)

    def __str__(self):
        return "LotteryNumberPool => { \
lnp_id:%d, lottery_id:%d, lottery_number:%d}" % (
self.lnp_id, self.lottery_id, self.lottery_number)

    __repr__ = __str__




