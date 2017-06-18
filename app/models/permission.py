#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService

class Permission(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'permission'

    permission_id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, default=0)
    endpoint = db.Column(db.String(255), default='')
    endpoint_name = db.Column(db.String(255), default='')
    endpoint_icon = db.Column(db.String(255), default='')
    endpoint_list = db.Column(db.Text, default=None)
    sort_order = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Permission => { \
permission_id:%d, parent_id:%d, endpoint:'%s', endpoint_name:'%s', endpoint_icon:'%s',  \
endpoint_list:'%s', sort_order:%d}" % (
self.permission_id, self.parent_id, self.endpoint, self.endpoint_name, self.endpoint_icon,
self.endpoint_list, self.sort_order)

    __repr__ = __str__


    @staticmethod
    def get_child_list(id=0):
        """获取子菜单列表"""
        permission_child_list = Permission.query.filter(Permission.parent_id == id).\
                                    order_by(Permission.sort_order.desc()).all()

        return permission_child_list
