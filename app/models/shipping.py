#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService


class Shipping(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'shipping'

    shipping_id = db.Column(db.Integer, primary_key=True)
    shipping_name = db.Column(db.String(32), default='')
    shipping_amount = db.Column(db.Float, default=0.00)
    shipping_desc = db.Column(db.String(255), default='')
    free_limit_amount = db.Column(db.Float, default=0.00)
    tracking_url = db.Column(db.String(255), default='')
    shipping_code = db.Column(db.String(20), default='')
    is_default = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Shipping => { \
shipping_id:%d, shipping_name:'%s', shipping_amount:%0.2f, shipping_desc:'%s', free_limit_amount:%0.2f,  \
tracking_url:'%s', shipping_code:'%s', is_default:%d}" % (
self.shipping_id, self.shipping_name, self.shipping_amount, self.shipping_desc, self.free_limit_amount,
self.tracking_url, self.shipping_code, self.is_default)

    __repr__ = __str__
