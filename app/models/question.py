#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService


class Question(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'question'

    question_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    nickname = db.Column(db.String(32), default='')
    avatar = db.Column(db.String(128), default='')
    title = db.Column(db.String(255), default='')
    content = db.Column(db.Text, default=None)
    question_img = db.Column(db.String(255), default='')
    qa_id = db.Column(db.Integer, default=0)
    answer_data = db.Column(db.Text, default=None)
    answer_count = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Question => { \
question_id:%d, uid:%d, nickname:'%s', avatar:'%s', title:'%s',  \
content:'%s', question_img:'%s', qa_id:%d, answer_data:'%s', answer_count:%d,  \
add_time:%d}" % (
self.question_id, self.uid, self.nickname, self.avatar, self.title,
self.content, self.question_img, self.qa_id, self.answer_data, self.answer_count,
self.add_time)

    __repr__ = __str__


class QuestionAnswer(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'question_answer'

    qa_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, default=0)
    uid = db.Column(db.Integer, default=0)
    nickname = db.Column(db.String(32), default='')
    avatar = db.Column(db.String(128), default='')
    content = db.Column(db.Text, default=None)
    answer_img = db.Column(db.String(255), default='')
    agree_count = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "QuestionAnswer => { \
qa_id:%d, question_id:%d, uid:%d, nickname:'%s', avatar:'%s',  \
content:'%s', answer_img:'%s', agree_count:%d, add_time:%d}" % (
self.qa_id, self.question_id, self.uid, self.nickname, self.avatar,
self.content, self.answer_img, self.agree_count, self.add_time)

    __repr__ = __str__


class QuestionGallery(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'question_gallery'

    qg_id = db.Column(db.Integer, primary_key=True)
    ttype = db.Column(db.Integer, default=0)
    tid = db.Column(db.Integer, default=0)
    img = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "QuestionGallery => { \
qg_id:%d, ttype:%d, tid:%d, img:'%s', add_time:%d}" % (
self.qg_id, self.ttype, self.tid, self.img, self.add_time)

    __repr__ = __str__

