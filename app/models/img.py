#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService

class Img(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'img'

    img_id = db.Column(db.Integer, primary_key=True)
    ic_id = db.Column(db.Integer, default=0)
    _img = db.Column(db.String(255), default='')
    ic_name = db.Column(db.String(255), default='')
    img_title = db.Column(db.String(255), default='')
    img_desc = db.Column(db.String(255), default='')
    tid = db.Column(db.Integer, default=0)
    ttype = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)
    is_display = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Img => { \
img_id:%d, ic_id:%d, _img:'%s', ic_name:'%s', img_title:'%s',  \
img_desc:'%s', tid:%d, ttype:%d, sort_order:%d, is_display:%d,  \
add_time:%d}" % (
self.img_id, self.ic_id, self._img, self.ic_name, self.img_title,
self.img_desc, self.tid, self.ttype, self.sort_order, self.is_display,
self.add_time)

    __repr__ = __str__


class ImgCategory(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'img_category'

    ic_id = db.Column(db.Integer, primary_key=True)
    ic_name = db.Column(db.String(32), default='')
    add_time = db.Column(db.Integer, default=None)

    def __str__(self):
        return "ImgCategory => { \
ic_id:%d, ic_name:'%s', add_time:%d}" % (
self.ic_id, self.ic_name, self.add_time)

    __repr__ = __str__
