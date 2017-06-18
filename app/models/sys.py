#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService


class SysRegion(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'sys_region'

    region_id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, default=0)
    region_name = db.Column(db.String(120), default='')
    region_type = db.Column(db.Integer, default=2)
    agency_id = db.Column(db.Integer, default=0)

    def __str__(self):
        return "SysRegion => { \
region_id:%d, parent_id:%d, region_name:'%s', region_type:%d, agency_id:%d}" % (
self.region_id, self.parent_id, self.region_name, self.region_type, self.agency_id)

    __repr__ = __str__

    @staticmethod
    def get_children_region_list(region_id=0):
        """获取子地区列表"""
        return SysRegion.query.filter(SysRegion.parent_id == region_id).all()


class Adv(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'adv'

    adv_id = db.Column(db.Integer, primary_key=True)
    ac_id = db.Column(db.Integer, default=0)
    adv_img = db.Column(db.String(255), default='')
    adv_category = db.Column(db.String(255), default='')
    adv_title = db.Column(db.String(255), default='')
    adv_title2 = db.Column(db.String(255), default='')
    adv_desc = db.Column(db.String(255), default='')
    ttype = db.Column(db.Integer, default=0)
    tid = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)
    is_show = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Adv => { \
adv_id:%d, ac_id:%d, adv_img:'%s', adv_category:'%s', adv_title:'%s',  \
adv_title2:'%s', adv_desc:'%s', ttype:%d, tid:%d, sort_order:%d,  \
is_show:%d, add_time:%d}" % (
self.adv_id, self.ac_id, self.adv_img, self.adv_category, self.adv_title, 
self.adv_title2, self.adv_desc, self.ttype, self.tid, self.sort_order, 
self.is_show, self.add_time)

    __repr__ = __str__


class SysSetting(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'sys_setting'

    ss_id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(225), default='')
    value = db.Column(db.String(225), default='')
    desc = db.Column(db.String(225), default='')

    def __str__(self):
        return "SysSetting => { \
ss_id:%d, key:'%s', value:'%s', desc:'%s'}" % (
self.ss_id, self.key, self.value, self.desc)

    __repr__ = __str__

