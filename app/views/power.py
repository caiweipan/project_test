#!/usr/bin/env python
#coding=utf-8
import json, time
from hashlib import md5, sha256

from flask import Blueprint, session, request, render_template, make_response, g, url_for, redirect
from flask.ext.sqlalchemy import Pagination

from codingabc.database import db
from codingabc.ext.aliyun import AliyunOSS, UploadNotAllowed
from app.helpers.date_time import str2timestamp
from app.helpers.common import easy_query_filter, get_params
from codingabc.helpers import toint, get_count, log_info, randomstr, log_debug, ismobile, randomstr, current_app

from app.models.role import Role, RolePermission
from app.models.permission import Permission
from app.models.user import User, UserAdmin, UserPassword
from app.models.sys import SysRegion
from app.services.get_data import role_name, get_role_list, user_role_id_list

power = Blueprint('power', __name__)

@power.route('/')
@power.route('/<int:page>')
@power.route('/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """权限列表"""
    g.page_type = 'search'
    g.title = u'权限列表'
    g.add_new = True
    g.button_name = u'角色管理'

    args = request.args
    endpoint_name = args.get('endpoint_name', '')
    role_id       = toint(args.get('role_id', '0'))

    q = db.session.query(RolePermission.role_id,
                    RolePermission.endpoint_list,
                    RolePermission.rp_id,
                    Permission.permission_id,
                    Permission.sort_order,
                    Permission.endpoint_name).\
        filter(RolePermission.permission_id == Permission.permission_id)

    if endpoint_name:
        q = q.filter(Permission.endpoint_name.like(u'%'+endpoint_name+u'%'))

    if role_id > 0:
        q = q.filter(RolePermission.role_id == role_id)

    # 角色列表
    role_list = get_role_list()

    permission_id_list = db.session.query(Permission.permission_id).all()
    permission_id_list = map(lambda permission:permission.permission_id, permission_id_list)

    power_count = get_count(q)
    power_list  = q.order_by(RolePermission.role_id.asc()).\
                        order_by(Permission.permission_id.desc()).\
                        offset((page-1)*page_size).limit(page_size).all()

    pagination  = Pagination(None, page, page_size, power_count, None)

    # html页面显示角色名称
    role_dict = role_name()
    res = make_response(render_template('power/index.html.j2',**locals()))
    res.set_cookie('goback_url', request.url)
    return res


@power.route('/edit')
def edit():
    """权限编辑"""

    args = request.args
    permission_id = toint(args.get('permission_id', '0'))
    rp_id = toint(args.get('rp_id', '0'))
    endpoint_list = args.get('endpoint_list', '').strip()
    sort_order = toint(args.get('sort_order', '0'))

    if permission_id <= 0 or rp_id <= 0:
        return u'参数出错'

    p = Permission.query.get(permission_id)
    if not p:
        return u'获取权限信息失败'

    rp =RolePermission.query.get(rp_id)
    if not rp:
        return u'获取角色权限失败'

    p.update(sort_order=sort_order)
    rp.update(endpoint_list=endpoint_list, commit=True)

    return u'ok'


@power.route('/permission_sort/modify')
def permission_sort_modify():
    """权限列表排序"""

    permission_id = toint(request.args.get('permission_id', '0'))
    new_sort = toint(request.args.get('new_sort', '0'))
    new_sort = new_sort if new_sort > 0 else -1

    if new_sort < 0:
        return u'只能输入大于0的数字'

    if new_sort > 10000000:
        return u'数字不能过大'

    if permission_id <= 0:
        return u'参数出错'

    p = Permission.get(permission_id)

    if p:
        p.update(sort_order=new_sort, commit=True)

    return u'ok'


@power.route('/admin_add', methods=['GET', 'POST'])
@power.route('/admin_add/<int:page>', methods=['GET', 'POST'])
@power.route('/admin_add/<int:page>-<int:page_size>', methods=['GET', 'POST'])
def admin_add(page=1, page_size=20):
    """用户角色添加"""
    g.title = u'用户角色添加'
    g.page_type = ''

    args = request.args
    errmsg = args.get('errmsg', '')
    mobile = args.get('mobile', '')
    role_id = toint(args.get('role_id', '0'))

    if errmsg:
        g.errmsg = eval(errmsg)
        log_debug('errmsg:%s'%g.errmsg)

    q = db.session.query(User.uid, User.avatar, User.mobile, User.nickname, UserAdmin.id, UserAdmin.role_id).\
            filter(User.uid == UserAdmin.uid).\
            filter(UserAdmin.role_id > 1)

    admin_count = get_count(q)
    admin_list  = q.order_by(UserAdmin.id.desc()).offset((page-1)*page_size).limit(page_size).all()

    role_list   = db.session.query(Role.role_id, Role.role_name).\
                    order_by(Role.role_id.asc()).all()

    # html页面显示角色名称
    role_dict = role_name()

    pagination  = Pagination(None, page, page_size, admin_count, None)

    return render_template('power/admin_add.html.j2', f={'mobile':mobile},**locals())


@power.route('/admin_save', methods=['POST'])
def admin_save():
    """保存管理员"""
    g.title = u'保存管理员'
    g.page_type = ''

    form = request.form
    mobile  = form.get('mobile', '')
    role_id = toint(form.get('role_id', '0'))

    errmsg = {}
    form = request.form

    if not ismobile(mobile):
        errmsg['mobile'] = u'手机号码不正确'

    if role_id <= 0:
        errmsg['role_id'] = u'请选择角色'

    if errmsg:
        return redirect(url_for('power.admin_add', errmsg=errmsg,**locals()))

    user = User.query.filter(User.mobile == mobile).first()

    # 生成密码
    salt = randomstr(32)
    sha256_password = sha256('888888').hexdigest()
    password = sha256(sha256_password+salt).hexdigest()

    if not user:
        nickname = u'%s*****%s'% (mobile[:3] ,mobile[-3:])
        avatar = current_app.config['DEFAULT_AVATAR']
        user = User.create(mobile=mobile,nickname=nickname, avatar=avatar, commit=True)

    up = UserPassword.query.filter(UserPassword.uid == user.uid).first()
    if not up:
       up = UserPassword.create(uid=user.uid, password=password,salt=salt)

    ua = UserAdmin.query.filter(UserAdmin.uid == user.uid).\
            filter(UserAdmin.role_id == role_id).first()

    if ua:
        ROLE_NAME = role_name()
        errmsg['mobile'] = u'%s的%s角色已经存在'% (user.nickname, ROLE_NAME.get(ua.role_id, ''))
        return redirect(url_for('power.admin_add',mobile=mobile, role_id=role_id,errmsg=errmsg))

    user_admin = UserAdmin.query.filter(UserAdmin.uid == user.uid).\
                    filter(UserAdmin.role_id == 0).first()

    if not user_admin:
        user_admin = UserAdmin.create()

    user_admin.update(role_id=role_id, uid=user.uid,add_time=int(time.time()), commit=True)

    # 更新用户角色名称显示
    session_uid = session.get('uid')
    session_role_id = session.get('role_id')
    role_id_list = user_role_id_list(session_uid)
    role_id_list.remove(session_role_id)
    session['role_temp_list'] = get_role_list(role_id_list)
    return redirect(url_for('power.admin_add'))


@power.route('/admin_delete')
def admin_delete():
    """移除管理员"""

    id = toint(request.args.get('id', '0'))
    role_id = toint(request.args.get('role_id', '0'))

    if id <= 0 or role_id <= 0:
        return u'参数出错'

    ua = UserAdmin.query.get(id)
    if not ua:
        return '该管理员已经被删除'

    if ua.role_id == 1:
        return u'超级管理员不能被移除'
    ua.update(role_id=0, commit=True)

    return u'ok'


@power.route('/role_admin/', methods=['GET', 'POST'])
@power.route('/role_admin/<int:page>', methods=['GET', 'POST'])
@power.route('/role_admin/<int:page>-<int:page_size>', methods=['GET', 'POST'])
def role_admin(page=1, page_size=20):
    """角色管理"""

    g.page_type = ''

    args = request.args
    role_id = toint(args.get('role_id', '0'))
    g.title = u'角色管理' if role_id <= 0 else u'角色详情'
    q = Role.query

    role_count = get_count(q)

    role_query_list = q.order_by(Role.role_id.asc()).offset((page-1)*page_size).limit(page_size).all()

    role = Role.query.get(role_id)

    # 获取角色权限permission_id字符串列表
    permission_id_list = db.session.query(RolePermission.permission_id).\
                        filter(RolePermission.role_id == role_id).all()
    permission_id_list = map(lambda permission:str(permission.permission_id), permission_id_list)
    permission_id_str  = ','.join(permission_id_list)

    # 获取权限列表
    # permission_list = db.session.query(Permission.permission_id, Permission.endpoint_name).\
    #                         order_by(Permission.parent_id.asc()).\
    #                         order_by(Permission.permission_id.asc()).all()

    # 获取一级菜单列表
    menu_list = db.session.query(Permission.permission_id, Permission.endpoint_name).\
                    filter(Permission.parent_id == 0).\
                    order_by(Permission.permission_id.asc()).all()

    pagination = Pagination(None, page, page_size, role_count, None)

    res = make_response(render_template('power/role_admin.html.j2',f=role if role else {},**locals()))

    res.set_cookie('goback_url', request.url)
    return res


@power.route('/role_delete')
def role_delete():
    """移除角色"""

    role_id = toint(request.args.get('role_id'))

    if role_id <= 0:
        return u'参数出错'

    UserAdmin.query.filter(UserAdmin.role_id == role_id).update({'role_id':0})

    role_permission_list = RolePermission.query.filter(RolePermission.role_id == role_id).all()
    for role_permission in role_permission_list:
        rp = RolePermission.query.filter(RolePermission.role_id == role_permission.role_id).first()
        if rp:
            rp.delete()

    r = Role.query.get(role_id)
    if not r:
        return '该角色已经被删除'

    r.delete(commit=True)

    return u'ok'


@power.route('/role_save', methods=['POST'])
def role_save():
    """保存角色"""
    g.title = u'保存角色'
    g.page_type = ''
    form = request.form

    desc               = form.get('desc', '')
    role_name          = form.get('role_name', '')
    role_id            = toint(form.get('role_id', '0'))
    permission_id_list = form.getlist('permission_id')
    permission_id_list = map(lambda permission_id:toint(permission_id), permission_id_list) # 现在获取的权限id列表
    errmsg = {}

    required_param_list = ['desc', 'role_name']
    for param in required_param_list:
        val = form.get(param, '')
        val = val.strip()
        if not val:
            errmsg[param] = u'必填项'

    if errmsg:
        g.errmsg = errmsg
        log_debug('errmsg:%s'%g.errmsg)
        return render_template('power/role_admin.html.j2', f=form,role_id=role_id)

    # 之前的权限id列表
    role_permission_id_list = []
    if role_id > 0:
        role = Role.query.get(role_id)
        role_permission_id_list = db.session.query(RolePermission.permission_id).\
                            filter(RolePermission.menu_type == 0).\
                            filter(RolePermission.role_id == role.role_id).all()
        # 角色权限id列表
        role_permission_id_list = map(lambda role_permission_id:toint(role_permission_id.permission_id), role_permission_id_list)
    else:
        role = Role.create(commit=True)

    if role.role_name == role_name and role.role_id != role_id:
        errmsg['role_name'] = u'角色名称不能重复'
        g.errmsg = errmsg
        log_debug('errmsg:%s'%g.errmsg)
        return render_template('power/role_admin.html.j2', f=form,role_id=role_id)

    # permission_id_list现在获取的权限id列表
    parent_p = None
    for permission_id in permission_id_list:
        p = Permission.query.get(permission_id)
        if not p:
            continue
        if p.parent_id > 0:
            parent_p = Permission.query.filter(Permission.permission_id == p.parent_id).first()

        q = RolePermission.query.filter(RolePermission.role_id == role.role_id)
        # 处理一级菜单的权限
        if parent_p:
            p_rp = q.filter(RolePermission.permission_id == parent_p.permission_id).first()

        if not p_rp:
            # 获取权限表permission_id为0的数据
            parent_rp_0 = RolePermission.query.filter(RolePermission.permission_id == 0).first()
            if parent_rp_0:
                p_rp = parent_rp_0.update(permission_id=parent_p.permission_id, role_id=role.role_id, menu_type=1)
            else:
                p_rp = RolePermission.create(permission_id=parent_p.permission_id, role_id=role.role_id, menu_type=1, endpoint_list='')

        # 处理二级菜单的权限
        rp = q.filter(RolePermission.permission_id == permission_id).first()
        if rp:
            continue

        # 获取权限表permission_id为0的数据
        rp_0 = RolePermission.query.filter(RolePermission.permission_id == 0).first()

        if not rp_0:
            rp_0 = RolePermission.create(endpoint_list='')
        rp_0.update(permission_id=permission_id, role_id=role.role_id)

    # 取消的权限id列表
    cancel_permission_id_list = [permission_id for permission_id in role_permission_id_list if permission_id not in permission_id_list]
    for permission_id in cancel_permission_id_list:
        p = Permission.query.get(permission_id)
        if not p:
            continue

        # 如果没有权限则去掉主菜单
        if p.parent_id > 0:
            parent_p = Permission.query.filter(Permission.permission_id == p.parent_id).first()
            parent_p_list = Permission.query.filter(Permission.parent_id == parent_p.permission_id).all()
            parent_p_id_list = [ parent_p.permission_id for parent_p in parent_p_list ]
            rp_list = RolePermission.query.filter(RolePermission.permission_id.in_(parent_p_id_list)).all()
            if len(rp_list) <= 1:
                parent_rp = RolePermission.query.filter(RolePermission.permission_id == p.parent_id).first()
                if parent_rp:
                    parent_rp.update(permission_id=0, role_id=0)

        rp = RolePermission.query.filter(RolePermission.role_id == role.role_id).\
                        filter(RolePermission.permission_id == permission_id).first()

        if rp:
            # 如果角色权限id列表没有在from表单获取的permission_id列表里,就把permission_id更新为0
            rp.update(permission_id=0, role_id=0)

    role = role.update(desc=desc, role_name=role_name, commit=True)

    return redirect(url_for('power.role_admin'))
