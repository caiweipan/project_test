#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService

class Role(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'role'

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(255), default='')
    desc = db.Column(db.String(255), default='')

    def __str__(self):
        return "Role => { \
role_id:%d, role_name:'%s', desc:'%s'}" % (
self.role_id, self.role_name, self.desc)

    __repr__ = __str__


class RolePermission(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'role_permission'

    rp_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, default=0)
    permission_id = db.Column(db.Integer, default=0)
    menu_type = db.Column(db.Integer, default=0)
    endpoint_list = db.Column(db.Text, default=None)

    def __str__(self):
        return "RolePermission => { \
rp_id:%d, role_id:%d, permission_id:%d, menu_type:%d, endpoint_list:'%s'}" % (
self.rp_id, self.role_id, self.permission_id, self.menu_type, self.endpoint_list)

    __repr__ = __str__
