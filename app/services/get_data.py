#!/usr/bin/env python
#coding=utf-8

import json
import time
from hashlib import md5
from decimal import Decimal

from flask import request, session, current_app

from codingabc.database import db
from codingabc.helpers import toint, log_debug, log_info, log_error
from app.models.role import Role
from app.models.user import User, UserAdmin

def role_name():
    """获取角色名称"""

    role_list = db.session.query(Role.role_id, Role.role_name).\
                    order_by(Role.role_id.asc()).all()

    ROLE_NAME = {}
    for role in role_list:
        ROLE_NAME[role.role_id] = role.role_name

    return ROLE_NAME


def get_role_list(role_id_list=[]):
    """角色列表"""
    role_list = []

    if len(role_id_list) > 0:
        role_list_temp = db.session.query(Role.role_id, Role.role_name).\
                            filter(Role.role_id.in_(role_id_list)).\
                            order_by(Role.role_id.asc()).all()
    else:
        role_list_temp = db.session.query(Role.role_id, Role.role_name).\
                            order_by(Role.role_id.asc()).all()

    # 如果role_id=1,append超级管理员到role_list
    if 1 in role_id_list:
        role = {'name':u'超级管理员', 'value':1}
        role_list.append(role)

    for role in role_list_temp:
        role = {'name':role.role_name, 'value':role.role_id}
        role_list.append(role)

    return role_list


def user_role_id_list(uid=0):
    """获取用户角色id列表"""

    q = db.session.query(UserAdmin.role_id)

    if uid > 0:
        q = q.filter(UserAdmin.uid == uid)
    ua_list = q.all()
    role_id_list = map(lambda role:role.role_id, ua_list)

    return role_id_list
