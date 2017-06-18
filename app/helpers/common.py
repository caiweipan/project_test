#!/usr/bin/env python
#coding=utf-8

import urllib, types, time, platform, socket
from flask.ext.sqlalchemy import Pagination
from flask import request
from codingabc.helpers import toint
from decimal import Decimal
from codingabc.helpers import log_debug, log_info, log_error
from codingabc.database import db
from app.models.role import RolePermission
from app.models.permission import Permission

def getip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
     s.connect(('www.baidu.com', 0))
     ip = s.getsockname()[0]
    except:
     ip = "127.0.0.1"
    finally:
     s.close()
    return ip


def model_to_dict(model):
    """ orm model转换成dict """

    ret = {}
    for c in model.__table__.columns:
        ret[c.name] = getattr(model, c.name)

    return ret

def model_to_dict_only(model, only=[]):
    """ orm model转换成dict - only版 """

    __dict = model_to_dict(model)

    _dict = {}
    for key in only:
        _dict[key] = __dict.get(key, None)

    return _dict

def ml_to_dl(model_list):
    """ model list to dict list """

    return [model_to_dict(m) for m in model_list]

def kt_to_dict(kt):
    """ KeyedTuple转换成Dict """

    return kt._asdict()

def ktl_to_dl(kt_list):
    """ KeyedTuple List转换成Dict List """

    return [kt_to_dict(kt) for kt in kt_list]

def urlencode(params):
    """ url转码 """

    if not params:
        return ''

    _params = params.copy()
    for k,v in params.items():
        if isinstance(v, types.StringType) or isinstance(v, types.UnicodeType):
            _params[k] = v.encode('utf8')

    return urllib.urlencode(_params)


def object_name(id, Object, name):
    """获取对象名称"""

    if id <= 0:
        return u''

    object_info = Object.query.get_or_404(id)
    if not object_info:
        return u''

    object_name = object_info.category_name
    return getattr(object_info,name,'')


def list_pagination(query_list, page=1,page_size=20):
    pagination  = Pagination(None, page, page_size, len(query_list), None)
    if page and page_size and len(query_list) > 0:
        a = (page -1)*page_size; b = ((page - 1)*page_size + page_size)if page > 1 else page_size
        query_list = query_list[a:b]

    return [query_list,pagination]


def easy_query_filter(Object,q,query_dict={}):
    """查询"""

    if not Object:
        log_info(u'请传入查询对象。')
        return q

    if not q:
        log_info(u'请传入q。')
        return q

    query_name_list = query_dict.keys()
    for query_name in query_name_list:
        attr = query_dict.get(query_name)
        if isinstance(attr, int) == True:
            if attr >= 0:
                q = q.filter(getattr(Object, query_name) == attr)
                continue
            continue
        if attr:
            if query_name[-4:] == 'time':
                if query_name[:5] == 'begin':
                    begin_time = time.mktime(time.strptime(attr,'%Y-%m-%d'))
                    q = q.filter(getattr(Object, query_name[6:]) >= begin_time)
                    continue

                if query_name[:3] == 'end':
                    end_time = time.mktime(time.strptime(attr,'%Y-%m-%d')) + 24*3600
                    q = q.filter(getattr(Object, query_name[4:]) <= end_time)
                    continue
                q = q.filter(getattr(Object, query_name).like(u'%'+attr+u'%'))
                continue
            q = q.filter(getattr(Object,query_name).like(u'%'+attr+u'%'))
            continue
    return q


def get_params(param_dict):
    """ 获取参数 """

    param_list = {}
    for key, value in param_dict.iteritems():
        request_param = request.form if request.method == 'POST' else request.args
        if value is int:
            param = toint(request_param.get(key, '0'))
            param = param if param > 0 or request_param.get(key, '') == '0'  else -1
            param_list[key] = param
            continue
        if value is str:
            param = request_param.get(key, '').strip()
            if key[-4:] == 'time':
                try:
                    param = int(time.mktime(time.strptime(param,'%Y-%m-%d %H:%M')))
                except Exception, e:
                    pass
            param_list[key] = param
            continue

        if value == Decimal:
            param = Decimal(request_param.get(key,'0.0'))
            param_list[key] = param
            continue

        if value is None:
            param = request.files[key]
            param = param if param else ''
            param_list[key] = param
            continue

    return param_list


def img_list(img_list=[]):
    """图片列表"""

    img_list = img_list.split(',')

    if len(img_list) > 0:
        return img_list

    return ''


def menu(role_id=0):
    """菜单"""
    menu = []

    if role_id > 0:
        # 获取用户权限列表
        rp_list = RolePermission.query.filter(RolePermission.role_id == role_id).all()
        rp_id_list  = [rp.permission_id for rp in rp_list]

        permission_list = Permission.query.filter(Permission.parent_id == 0).\
                            filter(Permission.permission_id.in_(rp_id_list)).\
                            order_by(Permission.sort_order.desc()).all()

        # 如果是超级管理员，就显示所有菜单
        if role_id == 1:
            permission_list = Permission.query.filter(Permission.parent_id == 0).\
                            order_by(Permission.sort_order.desc()).all()

        for permission in permission_list:
            # # 如果找不到端点就continue掉
            # if not permission.endpoint:
            #     continue

            permission_child_list = Permission.get_child_list(permission.permission_id)
            child_list = []
            for child in permission_child_list:
                # 如果找不到端点就continue掉
                if not child.endpoint:
                    continue

                # 如果permission_id没有在获取用户权限id列表就continue掉
                if role_id != 1 and child.permission_id not in rp_id_list:
                    continue

                child_dict = {}
                child_dict['name'] = u'%s'% child.endpoint_name
                child_dict['endpoint'] = child.endpoint
                child_list.append(child_dict)

            base_menu_dict ={
                        'name':u'%s'% permission.endpoint_name,
                        'endpoint':u'%s'% permission.endpoint,
                        'params':{},
                        'icon':u'%s' % permission.endpoint_icon,
                        'child':child_list
                    }
            menu.append(base_menu_dict)
    return menu


def child_menu_list(id=0):
    """子菜单列表"""

    if id <= 0:
        return u'参数出错'

    permission_list = db.session.query(Permission.permission_id, Permission.endpoint_name).\
                    filter(Permission.parent_id > 0).\
                    filter(Permission.parent_id == id).all()

    log_info(permission_list)
    return permission_list
