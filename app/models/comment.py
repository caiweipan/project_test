#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService

class Comment(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'comment'

    comment_id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, default=0)
    uid = db.Column(db.Integer, default=0)
    nickname = db.Column(db.String(32), default='')
    avatar = db.Column(db.String(128), default='')
    ttype = db.Column(db.Integer, default=0)
    tid = db.Column(db.Integer, default=0)
    tname = db.Column(db.String(255), default='')
    timg = db.Column(db.String(255), default='')
    star = db.Column(db.Integer, default=5)
    content = db.Column(db.Text, default=None)
    img_list = db.Column(db.Text, default=None)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Comment => { \
comment_id:%d, parent_id:%d, uid:%d, nickname:'%s', avatar:'%s',  \
ttype:%d, tid:%d, tname:'%s', timg:'%s', star:%d,  \
content:'%s', img_list:'%s', add_time:%d}" % (
self.comment_id, self.parent_id, self.uid, self.nickname, self.avatar,
self.ttype, self.tid, self.tname, self.timg, self.star,
self.content, self.img_list, self.add_time)

    __repr__ = __str__
