#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService

class Like(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'like'

    like_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    nickname = db.Column(db.String(32), default='')
    avatar = db.Column(db.String(128), default='')
    desc = db.Column(db.String(255), default='')
    ttype = db.Column(db.Integer, default=0)
    tid = db.Column(db.Integer, default=0)
    tname = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Like => { \
like_id:%d, uid:%d, nickname:'%s', avatar:'%s', desc:'%s',  \
ttype:%d, tid:%d, tname:'%s', add_time:%d}" % (
self.like_id, self.uid, self.nickname, self.avatar, self.desc,
self.ttype, self.tid, self.tname, self.add_time)

    __repr__ = __str__
