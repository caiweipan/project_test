#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService


class After(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'after'

    after_id = db.Column(db.Integer, primary_key=True)
    og_id = db.Column(db.Integer, default=0)
    order_id = db.Column(db.Integer, default=0)
    goods_id = db.Column(db.Integer, default=0)
    uid = db.Column(db.Integer, default=0)
    after_type = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)
    content = db.Column(db.String(255), default='')
    img_list = db.Column(db.Text, default=None)
    review_content = db.Column(db.String(255), default='')
    status = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "After => { \
after_id:%d, og_id:%d, order_id:%d, goods_id:%d, uid:%d,  \
after_type:%d, quantity:%d, content:'%s', img_list:'%s', review_content:'%s',  \
status:%d, add_time:%d, update_time:%d}" % (
self.after_id, self.og_id, self.order_id, self.goods_id, self.uid,
self.after_type, self.quantity, self.content, self.img_list, self.review_content,
self.status, self.add_time, self.update_time)

    __repr__ = __str__


class AfterStep(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'after_step'

    as_id = db.Column(db.Integer, primary_key=True)
    after_id = db.Column(db.Integer, default=0)
    step_status = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "AfterStep => { \
as_id:%d, after_id:%d, step_status:%d, add_time:%d}" % (
self.as_id, self.after_id, self.step_status, self.add_time)

    __repr__ = __str__
