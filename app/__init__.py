#!/usr/bin/env python
#coding=utf-8

from flask import session, request, redirect, url_for, render_template, make_response
from codingabc.helpers import get_count, toint
from codingabc.database import db
from app.models.role import RolePermission
from app.models.permission import Permission
from app.helpers.common import menu

from app import views

# 项目app名称
DEFAULT_APP_NAME = 'app'

# modules
DEFAULT_MODULES = (
    (views.index,           ''),
    (views.user,            '/user'),
    (views.goods,           '/goods'),
    (views.order,           '/order'),
    (views.sys,             '/sys'),
    (views.coupon,          '/coupon'),
    (views.comment,         '/comment'),
    (views.lottery,         '/lottery'),
    (views.news,            '/news'),
    (views.question,        '/question'),
    (views.shipping,        '/shipping'),
    (views.after,           '/after'),
    (views.img,             '/img'),
    (views.power,           '/power')
)

def configure_before_handlers(app):

    @app.before_request
    def authenticate():

        # 排除校验的endpoint和static
        endpoint = request.endpoint
        if (endpoint in ('index.welcome', 'index.signin', 'index.signout', 'index.getcode','index.forget_password')
                    or request.path.find('/static') == 0):
            return

        if endpoint and endpoint != 'user.change_role':
            role_id = session.get('role_id')
            if role_id > 1:
                # 获取角色权限
                role_permission = db.session.query(Permission.permission_id).\
                                    filter(RolePermission.permission_id == Permission.permission_id).\
                                    filter(RolePermission.role_id == role_id).\
                                    filter(RolePermission.endpoint_list.like(u'%'+endpoint+u'%')).first()

                if not role_permission:
                    return u'您没有访问权限，如需访问请联系管理员。'

        admin_id = toint(session.get('admin_id', '0'))
        if admin_id <= 0:
            return redirect(url_for('index.signin'))


def configure_errorhandlers(app):
    """ Configures the error handlers """
    @app.errorhandler(403)
    def forbidden_page(error):
        return make_response(render_template("errors/error_img.html", error=error, error_type=403))

    @app.errorhandler(404)
    def page_not_found(error):
        return make_response(render_template("errors/error_img.html", error=error,error_type=404))

    @app.errorhandler(500)
    def server_error_page(error):
        return make_response(render_template("errors/error_img.html", error=error, error_type=500))
