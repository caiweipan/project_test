#!/usr/bin/env python
#coding=utf-8

import time
from decimal import Decimal
from flask import Blueprint, request, session, redirect, current_app, abort, url_for, g, render_template, make_response
from flask.ext.sqlalchemy import Pagination

from codingabc.helpers import log_debug, toint, get_count, log_info
from codingabc.database import db
from codingabc.ext.aliyun import AliyunOSS
from codingabc.ext.uploads import UploadNotAllowed
from app.services.qiniu_upload import QiNiuOSS

from app.helpers.common import easy_query_filter, get_params, menu
from app.models.sys import SysRegion, Adv, SysSetting
from app.services.sys import SaveSysSettingService
from app.models.recharge_card import RechargeCard
from app.models.permission import Permission

sys = Blueprint('sys', __name__)


@sys.route('/ad_list')
@sys.route('/ad_list/<int:page>')
@sys.route('/ad_list/<int:page>-<int:page_size>')
def ad_list(page=1, page_size=20):
    """广告列表"""
    g.page_type = 'search'
    g.title = u'广告列表'
    g.add_new = True
    g.button_name = u'增加广告'

    param_dict  = get_params({'adv_id':int,'is_show':int,'begin_add_time':str, 'end_add_time':str})

    query_dict = {'adv_id':param_dict['adv_id'],'is_show':param_dict['is_show'],'begin_add_time':param_dict['begin_add_time'],'end_add_time':param_dict['end_add_time'],}

    q = Adv.query
    q = easy_query_filter(Adv,q,query_dict)

    ad_count = get_count(q)
    ad_list  = q.order_by(Adv.add_time.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    pagination  = Pagination(None, page, page_size, ad_count, None)

    res = make_response(render_template('sys/ad_list.html.j2', ad_list=ad_list, pagination=pagination))
    res.set_cookie('goback_url', request.url)
    return res


@sys.route('/ad/add', methods=['GET', 'POST'])
def ad_add():
    """广告增加"""
    g.title = u'广告增加'
    g.page_type = ''

    return render_template('sys/ad_edit.html.j2', f={})


@sys.route('/ad/edit')
def ad_edit():
    """广告编辑"""
    g.title = u'广告编辑'
    g.page_type = ''

    adv_id = toint(request.args.get('adv_id', '0'))
    ad = Adv.query.get_or_404(adv_id)

    return render_template('sys/ad_edit.html.j2', f=ad)


@sys.route('/ad/save', methods=['POST'])
def ad_save():
    """保存广告"""
    g.title = u'保存广告'
    g.page_type = ''

    form = request.form
    adv_id       = toint(form.get('adv_id', '0'))
    ttype        = toint(form.get('ttype', '0'))
    tid          = toint(form.get('tid', '0'))
    is_show      = toint(form.get('is_show', '0'))
    sort_order   = toint(form.get('sort_order', '0'))
    ac_id        = toint(form.get('ac_id', '0'))
    adv_category = form.get('adv_category', '')
    adv_title    = form.get('adv_title', '')
    adv_title2   = form.get('adv_title2', '')
    adv_desc     = form.get('adv_desc', '')
    adv_img      = request.files.get('adv_img', None)

    errmsg = {}
    form = request.form
    required_param_list = ['is_show', 'ac_id', 'ttype', 'tid']
    for param in required_param_list:
        val = form.get(param, '')
        val = val.strip()
        if not val:
            errmsg[param] = u'必填项'

    if errmsg:
        g.errmsg = errmsg
        log_debug('errmsg:%s'%g.errmsg)
        return render_template('sys/ad_edit.html.j2', f=form)

    # 检查 - 封面原图是否合法
    if adv_img:
        oss = AliyunOSS('ad', current_app.config['SAVE_TARGET_PATH'])
        try:
            oss.save(adv_img)
            adv_img = oss.put_to_oss()
        except UploadNotAllowed, e:
            errmsg['adv_img'] = u'图片只允许是图片文件'
        except Exception, e:
            errmsg['adv_img'] = u'图片上传失败'

    if adv_id <= 0:
        ad_info = Adv.create(add_time=int(time.time()))
    else:
        ad_info = Adv.get(adv_id)

    if adv_img:
        ad_info.update(adv_img=adv_img)

    ad_info.update(is_show=is_show, ttype=ttype, tid=tid, sort_order=sort_order, ac_id=ac_id,
                    adv_category=adv_category, adv_title=adv_title, adv_title2=adv_title2, adv_desc=adv_desc, commit=True)
    return redirect(url_for('sys.ad_list'))


@sys.route('/ad/delete')
def ad_delete():
    """移除广告"""

    adv_id = toint(request.args.get('adv_id', '0'))
    if adv_id <= 0:
        return u'参数出错'

    ad = Adv.query.get_or_404(adv_id)

    if ad:
        db.session.delete(ad)
        db.session.commit()

    return 'ok'


@sys.route('/ad_sort/modify')
def sort_modify():
    """修改排序"""

    adv_id = toint(request.args.get('adv_id', '0'))
    new_sort = toint(request.args.get('new_sort', '0'))
    new_sort = new_sort if new_sort > 0 else -1

    if new_sort < 0:
        return u'只能输入大于0的数字'

    if new_sort > 10000000:
        return u'数字不能过大'

    if adv_id <= 0:
        return u'参数出错'

    ad = Adv.get(adv_id)

    if ad:
        ad.sort_order = new_sort
        db.session.commit()

    return u'ok'


@sys.route('/region/options')
def region():
    """返回地区html"""
    args = request.args
    region_name = args.get('region_name', '')
    region_id   = toint(args.get('region_id', '0'))
    db_value    = args.get('db_value', '')

    if region_name:
        r = SysRegion.query.filter(SysRegion.region_name == region_name).first()
        region_id = r.region_id if r else 0

    if region_id <= 0:
        region_id = 1

    log_debug('region_id:%d' % region_id)
    region_list = SysRegion.get_children_region_list(region_id)

    options_html = u'<option>请选择……</option>'
    for r in region_list:
        selected = 'selected' if r.region_name == db_value else ''
        options_html += u'<option value="%s" %s>%s</option>' % (r.region_name, selected, r.region_name )

    return options_html


@sys.route('/file/upload', methods=['POST'])
def file_upload():
    """文件上传"""
    form = request.form
    cat = form.get('cat', 'sys')
    one_file = request.files.get('file')
    file_type = toint(form.get('file_type', '1')) # 1.图片 2.视频
    file_url = 'error'
    if one_file:
        if file_type == 2:
            # push_type 1.图片 2.视频 3.音频 4.文档
            push_type = 2
            oss = QiNiuOSS('video', push_type, current_app.config['SAVE_TARGET_PATH'])
            try:
                oss.save(one_file)
                file_url = oss.put_to_oss()
            except IOError, e:
                log_info(u'### 只允许是视频文件:%s'% e)
                pass
            except Exception, e:
                log_info(u'### 视频上传失败:%s'% e)
                pass
        else:
            oss = AliyunOSS(cat, current_app.config['SAVE_TARGET_PATH'])
            try:
                oss.save(one_file)
                file_url = oss.put_to_oss()
            except UploadNotAllowed, e:
                pass
            except Exception, e:
                pass

    log_debug(file_url)

    return file_url


@sys.route('/setting', methods=['GET', 'POST'])
def setting():
    """系统设置"""
    g.page_type = 'form'
    g.title = u'系统设置'

    cb_id = db.session.query(SysSetting.value).filter(SysSetting.key == 'cb_id').first()
    cb_id = cb_id.value if cb_id else ''

    is_invite_new_friends_to_register_as_a_gift_coupon = db.session.query(SysSetting.value).filter(SysSetting.key == 'is_invite_new_friends_to_register_as_a_gift_coupon').first()
    is_invite_new_friends_to_register_as_a_gift_coupon = is_invite_new_friends_to_register_as_a_gift_coupon.value if is_invite_new_friends_to_register_as_a_gift_coupon else ''

    is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons   = db.session.query(SysSetting.value).filter(SysSetting.key == 'is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons').first()
    is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons = is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons.value if is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons else ''

    return render_template('sys/setting.html.j2', f={'cb_id':cb_id,'is_invite_new_friends_to_register_as_a_gift_coupon':is_invite_new_friends_to_register_as_a_gift_coupon, 'is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons':is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons})


@sys.route('/save_setting', methods=['POST'])
def save_setting():
    """ 保存系统设置 """
    g.page_type = 'form'
    g.title = u'保存系统设置'

    form = request.form
    ss_id = toint(form.get('ss_id', 0))

    snss = SaveSysSettingService(form, ss_id)
    if not snss.check():
        g.errmsg = snss.errmsg

        return render_template('sys/setting.html.j2', f=form)

    snss.save()

    return redirect(url_for('sys.setting'))


@sys.route('/recharge_card_list')
@sys.route('/recharge_card_list/<int:page>')
@sys.route('/recharge_card_list/<int:page>-<int:page_size>')
def recharge_card_list(page=1, page_size=20):
    """充值卡列表"""
    g.page_type = 'search'
    g.title = u'充值卡列表'
    g.add_new = True
    g.button_name = u'新增充值卡'
    param_dict  = get_params({'rc_id':int,'amount':str,'gift':str})

    query_dict = {'rc_id':param_dict['rc_id'],'amount':param_dict['amount'],'gift':param_dict['gift']}

    q = RechargeCard.query
    q = easy_query_filter(RechargeCard,q,query_dict)
    recharge_card_count = get_count(q)
    recharge_card_list  = q.order_by(RechargeCard.rc_id.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    pagination  = Pagination(None, page, page_size, recharge_card_count, None)

    res = make_response(render_template('sys/recharge_card_list.html.j2', **locals()))
    res.set_cookie('goback_url', request.url)
    return res


@sys.route('/recharge_card/detail')
def recharge_card_detail():
    """充值卡详情"""
    g.page_type = ''
    g.title = u'充值卡详情'

    rc_id = toint(request.args.get('rc_id', '0'))

    recharge_card_info = RechargeCard.query.get_or_404(rc_id)

    return render_template('sys/card_detail.html.j2', f=recharge_card_info,**locals())


@sys.route('/recharge_card/add')
def recharge_card_add():
    """新增充值卡"""
    g.page_type = ''
    g.title = u'新增充值卡'

    return render_template('sys/card_detail.html.j2', f={},**locals())


@sys.route('/save_card', methods=['POST'])
def save_card():
    """保存抽奖活动"""
    g.title     = u'保存抽奖活动'
    g.page_type = ''
    errmsg      = {}
    param_dict  = get_params({'rc_id':int,'amount':Decimal,'gift':Decimal,'sort_order':str})
    required_param_list = ['amount','gift']
    form = request.form
    for param in required_param_list:
        val = request.form.get(param, '')
        val = val.strip()
        if not val:
            errmsg[param] = u'必填项'
            g.errmsg = errmsg
            log_debug('errmsg:%s'%g.errmsg)
            return render_template('sys/card_detail.html.j2', f=form,**locals())

    if param_dict['amount'] < 0:
        errmsg['amount'] = u'金额不能小于0'
        g.errmsg = errmsg
        return render_template('sys/card_detail.html.j2', f=form,**locals())

    if param_dict['gift'] < 0:
        errmsg['gift'] = u'赠送金额不能小于0'
        g.errmsg = errmsg
        return render_template('sys/card_detail.html.j2', f=form,**locals())

    rc_id = param_dict['rc_id']
    if rc_id > 0:
        recharge_card = RechargeCard.query.get_or_404(rc_id)
    else:
        recharge_card = RechargeCard.create(add_time=int(time.time()), update_time=int(time.time()))

    recharge_card.update(amount=param_dict['amount'] ,gift=param_dict['gift'], sort_order=param_dict['sort_order'],commit=True)

    return redirect(url_for('sys.recharge_card_list'))


@sys.route('/card_sort/modify')
def card_sort_modify():
    """修改排序"""

    rc_id = toint(request.args.get('rc_id', '0'))
    new_sort = toint(request.args.get('new_sort', '0'))
    new_sort = new_sort if new_sort > 0 else -1

    if new_sort < 0:
        return u'只能输入大于0的数字'

    if new_sort > 10000000:
        return u'数字不能过大'

    if rc_id <= 0:
        return u'参数出错'

    rc = RechargeCard.get(rc_id)

    if rc:
        rc.sort_order = new_sort
        db.session.commit()

    return u'ok'


@sys.route('/recharge_card/delete')
def recharge_card_delete():
    """移除充值卡"""

    rc_id = toint(request.args.get('rc_id', '0'))
    if rc_id <= 0:
        return u'参数出错'

    rc = RechargeCard.query.get_or_404(rc_id)

    if rc:
        db.session.delete(rc)
        db.session.commit()

    return 'ok'


@sys.route('/menu_list')
@sys.route('/menu_list/<int:page>')
@sys.route('/menu_list/<int:page>-<int:page_size>')
def menu_list(page=1, page_size=20):
    """菜单列表"""
    g.page_type = 'search'
    g.title = u'菜单列表'
    g.add_new = True
    g.button_name = u'新增菜单'

    args = request.args
    endpoint = args.get('endpoint', '')
    endpoint_name = args.get('endpoint_name', '')
    menu_type = toint(args.get('menu_type', '-1'))

    q = Permission.query
    if endpoint:
        q = q.filter(Permission.endpoint.like(u'%'+endpoint+u'%'))

    if endpoint_name:
        q = q.filter(Permission.endpoint_name.like(u'%'+endpoint_name+u'%'))

    if menu_type == 0:
        q = q.filter(Permission.parent_id == 0)

    if menu_type > 0:
        q = q.filter(Permission.parent_id > 0)

    menu_count = get_count(q)
    menu_list  = q.order_by(Permission.permission_id.desc()).\
                offset((page-1)*page_size).limit(page_size).all()

    pagination  = Pagination(None, page, page_size, menu_count, None)
    session['menu'] = menu(session.get('role_id'))
    res = make_response(render_template('sys/menu_list.html.j2', menu_list=menu_list, pagination=pagination))
    res.set_cookie('goback_url', request.url)
    return res


@sys.route('/menu_add', methods=['GET', 'POST'])
def menu_add():
    """新增菜单"""
    g.title = u'新增菜单'
    g.page_type = ''

    return render_template('sys/menu_add.html.j2', f={})


@sys.route('/menu_edit')
def menu_edit():
    """菜单编辑"""
    g.title = u'菜单编辑'
    g.page_type = ''

    permission_id = toint(request.args.get('permission_id', '0'))
    if permission_id <= 0:
        return u'参数出错'

    p = Permission.query.get_or_404(permission_id)
    menu_type = 0 if p.parent_id == 0 else 1
    setattr(p,'menu_type',menu_type)
    return render_template('sys/menu_add.html.j2', f=p)


@sys.route('/menu_save', methods=['POST'])
def menu_save():
    """保存菜单"""
    g.title = u'保存菜单'
    g.page_type = ''

    errmsg = {}
    form = request.form
    permission_id     = toint(form.get('permission_id', '0'))
    endpoint          = form.get('endpoint', '').strip()
    endpoint_name     = form.get('endpoint_name', '').strip()
    endpoint_icon     = form.get('endpoint_icon', '').strip()
    menu_type         = toint(form.get('menu_type', '0'))
    sort_order        = toint(form.get('sort_order', '0'))
    new_endpoint_list = form.get('endpoint_list', '').strip()     #新端点列表

    # 必填项检查
    if menu_type == 0:
        required_param_list = ['endpoint', 'endpoint_name', 'endpoint_icon', 'menu_type', 'sort_order']
    else:
        required_param_list = ['endpoint', 'endpoint_name', 'menu_type', 'sort_order','endpoint_list']

    for param in required_param_list:
        val = form.get(param, '')
        val = val.strip()
        if not val:
            errmsg[param] = u'必填项'

    if errmsg:
        g.errmsg = errmsg
        log_debug('errmsg:%s'%g.errmsg)
        return render_template('sys/menu_add.html.j2', f=form)

    if permission_id <= 0:
        permission_info = Permission.create(endpoint_list=endpoint)
        # 判断新增端点是否已经存在
        if menu_type == 0:
            e_q = Permission.query.filter(Permission.endpoint == endpoint).filter(Permission.parent_id == 0)
        else:
            e_q = Permission.query.filter(Permission.endpoint == endpoint).filter(Permission.parent_id > 0)
        e = e_q.first()
        if e:
            errmsg['endpoint'] = u'新增端点:%s已经存在'% endpoint

        # 判断新增端点名称是否存在
        en = e_q.filter(Permission.endpoint_name == endpoint_name).first()
        if en:
            errmsg['endpoint_name'] = u'新增端点名称:%s已经存在'% endpoint_name

        if errmsg:
            g.errmsg = errmsg
            log_debug('errmsg:%s'%g.errmsg)
            return render_template('sys/menu_add.html.j2', f=form)
    else:
        permission_info = Permission.get(permission_id)

    if menu_type == 1:
        endpoint_list = db.session.query(Permission.endpoint).filter(Permission.parent_id == 0).all()
        endpoint_key_list = map(lambda e:e.endpoint.split('.')[0], endpoint_list)
        new_endpoint      = endpoint.split('.')
        new_endpoint_key  = new_endpoint[0]
        if new_endpoint_key not in endpoint_key_list:
            errmsg['endpoint'] = u'子菜单端点%s与主菜单不符合'% endpoint

        if errmsg:
            g.errmsg = errmsg
            log_debug('errmsg:%s'%g.errmsg)
            return render_template('sys/menu_add.html.j2', f=form)

        # 允许访问的端点列表处理
        ne_list = new_endpoint_list.split(',')  # 分割逗号后允许访问的端点列表
        if endpoint not in ne_list:
            new_endpoint_list = endpoint+ ',' + new_endpoint_list
        permission_info.update(endpoint_list=new_endpoint_list)

        for key in endpoint_key_list:
            if key != new_endpoint_key:
                continue

            p = Permission.query.filter(Permission.endpoint.like(u'%'+new_endpoint_key)).first()
            if not p:
                p = Permission.query.filter(Permission.endpoint.like(u'%'+new_endpoint_key+ u'%')).first()

            if not p:
                errmsg['endpoint'] = u'找不到对应的主菜单'

            if errmsg:
                g.errmsg = errmsg
                log_debug('errmsg:%s'%g.errmsg)
                return render_template('sys/menu_add.html.j2', f=form)

            parent_id = p.permission_id

    parent_id = parent_id if menu_type == 1 else 0
    permission_info.update(parent_id=parent_id, endpoint=endpoint, endpoint_name=endpoint_name,endpoint_icon=endpoint_icon, sort_order=sort_order, commit=True)

    return redirect(url_for('sys.menu_list'))


@sys.route('/delete_menu')
def delete_menu():
    """移除菜单"""

    permission_id = toint(request.args.get('permission_id', '0'))

    if permission_id <= 0:
        return u'参数出错'

    p = Permission.query.get(permission_id)

    if not p:
        return u'此菜单已经移除'

    is_pparent = None
    if p.parent_id == 0:
        is_pparent = Permission.query.filter(Permission.parent_id == p.permission_id).first()

    if is_pparent:
        return u'此菜单存在子菜单,不能移除'

    p.delete(commit=True)

    return u'ok'

