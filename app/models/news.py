#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService

class News(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'news'

    news_id = db.Column(db.Integer, primary_key=True)
    nc_id = db.Column(db.Integer, default=0)
    title = db.Column(db.String(100), default='')
    author_name = db.Column(db.String(50), default='')
    desc = db.Column(db.Text, default=None)
    detail = db.Column(db.Text, default=None)
    news_img = db.Column(db.String(255), default='')
    news_video = db.Column(db.String(255), default='')
    video_html = db.Column(db.String(255), default='')
    img_list = db.Column(db.Text, default=None)
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    longitude = db.Column(db.Float, default=None)
    latitude = db.Column(db.Float, default=None)
    like_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    is_top = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "News => { \
news_id:%d, nc_id:%d, title:'%s', author_name:'%s', desc:'%s',  \
detail:'%s', news_img:'%s', news_video:'%s', video_html:'%s', img_list:'%s',  \
sort_order:%d, status:%d, longitude:%0.2f, latitude:%0.2f, like_count:%d,  \
view_count:%d, is_top:%d, add_time:%d}" % (
self.news_id, self.nc_id, self.title, self.author_name, self.desc,
self.detail, self.news_img, self.news_video, self.video_html, self.img_list,
self.sort_order, self.status, self.longitude, self.latitude, self.like_count,
self.view_count, self.is_top, self.add_time)

    __repr__ = __str__


class NewsGoods(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'news_goods'

    ng_id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, default=0)
    goods_id = db.Column(db.Integer, default=0)
    extend = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "NewsGoods => { \
ng_id:%d, news_id:%d, goods_id:%d, extend:'%s', add_time:%d}" % (
self.ng_id, self.news_id, self.goods_id, self.extend, self.add_time)

    __repr__ = __str__




