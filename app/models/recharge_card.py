#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService

class RechargeCard(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'recharge_card'

    rc_id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, default=0.00)
    gift = db.Column(db.Float, default=0.00)
    sort_order = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "RechargeCard => { \
rc_id:%d, amount:%0.2f, gift:%0.2f, sort_order:%d, add_time:%d,  \
update_time:%d}" % (
self.rc_id, self.amount, self.gift, self.sort_order, self.add_time,
self.update_time)

    __repr__ = __str__
