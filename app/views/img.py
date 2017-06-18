#!/usr/bin/env python
#coding=utf-8

import time, json
from hashlib import sha256

from flask import Blueprint, g, request, redirect, url_for, render_template, make_response, session, current_app
from flask.ext.sqlalchemy import Pagination

from codingabc.database import db
from codingabc.ext.aliyun import AliyunOSS, UploadNotAllowed
from codingabc.helpers import log_debug, log_info, toint, randomstr, get_count

from app.helpers.date_time import current_timestamp
from app.models.img import Img, ImgCategory

img = Blueprint('img', __name__)


@img.route('/')
@img.route('/<int:page>')
@img.route('/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """图片列表"""
    g.page_type = 'search'
    g.title = u'图片列表'
    g.add_new = True
    g.button_name = u'新增图片'

    args       = request.args
    img_title  = args.get('img_title', '').strip()
    ic_id      = toint(args.get('ic_id', '0'))
    img_id     = toint(args.get('img_id', '0'))
    is_display = toint(args.get('is_display', '-1'))
    begin_add_time = args.get('begin_add_time', '').strip()
    end_add_time   = args.get('end_add_time', '').strip()

    q = Img.query

    if ic_id > 0:
        q = q.filter(Img.ic_id == ic_id)

    if img_id > 0:
        q = q.filter(Img.img_id == img_id)

    if is_display > 0:
        q = q.filter(Img.is_display == is_display)

    if img_title:
        like_mobile = u'%' + img_title + u'%'
        q = q.filter(Img.img_title.like(like_mobile))

    if begin_add_time:
        begin_time = time.mktime(time.strptime(begin_add_time,'%Y-%m-%d'))
        q = q.filter(Img.add_time >= begin_time)

    if end_add_time:
        end_add_time = time.mktime(time.strptime(end_add_time,'%Y-%m-%d')) + 24*3600
        q = q.filter(Img.add_time < end_add_time)

    img_count = get_count(q)
    img_list  = q.order_by(Img.img_id.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    ic_temp = db.session.query(ImgCategory.ic_id, ImgCategory.ic_name).\
                order_by(ImgCategory.ic_id.desc()).all()

    ic_dict,ic_list = {}, []
    for ic in ic_temp:
        if ic.ic_name:
            ic_dict = {'value':ic.ic_id, 'name':ic.ic_name}
            ic_list.append(ic_dict)

    pagination = Pagination(None, page, page_size, img_count, None)

    res = make_response(render_template('img/index.html.j2', **locals()))
    res.set_cookie('goback_url', request.url)
    return res


@img.route('/add')
def add():
    """新增图片"""
    g.page_type = ''
    g.title = u'新增图片'

    ic_list = db.session.query(ImgCategory.ic_id, ImgCategory.ic_name).\
                order_by(ImgCategory.add_time.desc()).all()

    return render_template('img/upload.html.j2', **locals())


@img.route('/detail')
def detail():
    """图片详情"""
    g.page_type = ''
    g.title = u'图片详情'

    args   = request.args
    img_id = toint(args.get('img_id', '0'))

    if img_id <= 0:
        return u'参数出错'

    img = Img.query.get(img_id)

    if not img:
        return u'获取图片信息失败'

    ic_list = db.session.query(ImgCategory.ic_id, ImgCategory.ic_name).\
                order_by(ImgCategory.add_time.desc()).all()

    return render_template('img/detail.html.j2', f=img, **locals())


@img.route('/save', methods=['POST'])
def save():
    """保存图片"""

    form = request.form
    img_id     = toint(form.get('img_id', '0'))
    ic_id      = toint(form.get('ic_id', '0'))
    _img       = request.files.get('_img', None)
    img_title  = form.get('img_title', '').strip()
    ttype      = toint(form.get('ttype', '0'))
    tid        = toint(form.get('tid', '0'))
    sort_order = toint(form.get('sort_order', '0'))
    is_display = toint(form.get('is_display', '-1'))
    img_desc   = form.get('img_desc', '').strip()
    errmsg     = {}

    if img_id <= 0:
        img = Img.create(add_time=int(time.time()))
        is_img_title = Img.query.filter(Img.img_title == img_title).first()
    else:
        img = Img.query.get(img_id)
        is_img_title = Img.query.filter(Img.img_title == img_title).\
                        filter(Img.img_id != img_id).first()
        if not img:
            g.errmsg = errmsg['img'] = u'获取图片信息失败'
            log_debug('errmsg:%s'%g.errmsg)
            return render_template('img/detail.html.j2', f=form,**locals())

    if _img:
        oss = AliyunOSS('img', current_app.config['SAVE_TARGET_PATH'])
        try:
            oss.save(_img)
            _img = oss.put_to_oss()
        except UploadNotAllowed, e:
            errmsg['img'] = u'头像必须是图片文件'
        except Exception, e:
            errmsg['img'] = u'发生错误，上传失败'

    if is_img_title:
        errmsg['img_title'] = u'图片标题已经存在'

    if errmsg:
        g.errmsg = errmsg
        log_debug('errmsg:%s'%g.errmsg)
        return render_template('img/detail.html.j2', f=form,**locals())

    ic = ImgCategory.query.get(ic_id)
    ic_name = ic.ic_name if ic else ''

    _img = _img if _img else img._img
    img.update(ic_id=ic_id,
               ic_name=ic_name,
               _img=_img,
               img_title=img_title,
               ttype=ttype,
               tid=tid,
               sort_order=sort_order,
               is_display=is_display,
               img_desc=img_desc,
               commit=True)

    return redirect(url_for('img.index'))


@img.route('/delete')
def delete():
    """移除图片"""

    img_id = toint(request.args.get('img_id', '0'))
    if img_id <= 0:
        return u'参数出错'

    img = Img.query.get(img_id)

    if not img:
        return u'图片已经被移除了'

    img.delete(commit=True)

    return 'ok'


@img.route('/sort_order/modify')
def sort_modify():
    """修改排序"""

    img_id = toint(request.args.get('img_id', '0'))
    new_sort = toint(request.args.get('new_sort', '0'))
    new_sort = new_sort if new_sort > 0 else -1

    if new_sort < 0:
        return u'只能输入大于0的数字'

    if new_sort > 10000000:
        return u'数字不能过大'

    if img_id <= 0:
        return u'参数出错'

    img = Img.get(img_id)

    if img:
        img.sort_order = new_sort
        db.session.commit()

    return u'ok'


@img.route('/ic_list')
@img.route('/ic_list/<int:page>')
@img.route('/ic_list/<int:page>-<int:page_size>')
def ic_list(page=1, page_size=20):
    """图片分类列表"""
    g.page_type = 'search'
    g.title = u'图片分类列表'
    g.add_new = True
    g.button_name = u'新增分类'

    args       = request.args
    ic_name  = args.get('ic_name', '').strip()

    q = ImgCategory.query

    if ic_name:
        like_mobile = u'%' + ic_name + u'%'
        q = q.filter(ImgCategory.ic_name.like(like_mobile))

    ic_count = get_count(q)
    ic_list  = q.order_by(ImgCategory.add_time.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    pagination = Pagination(None, page, page_size, ic_count, None)

    res = make_response(render_template('img/ic_list.html.j2', **locals()))
    res.set_cookie('goback_url', request.url)
    return res


@img.route('/ic_save')
def ic_save():
    """保存图片分类"""

    args = request.args
    ic_id = toint(args.get('ic_id', '0'))
    ic_name = args.get('ic_name', '').strip()

    if ic_id <= 0:
        ic = ImgCategory.create(add_time=int(time.time()))
    else:
        ic = ImgCategory.query.get(ic_id)

        if not ic:
            return u'获取分类信息失败'

    ic.update(ic_name=ic_name, commit=True)

    return u'ok'


@img.route('/ic_delete')
def ic_delete():
    """移除图片分类"""

    ic_id = toint(request.args.get('ic_id', '0'))
    if ic_id <= 0:
        return u'参数出错'

    ic = ImgCategory.query.get(ic_id)

    if not ic:
        return u'图片分类已经被移除了'

    ic.delete(commit=True)

    return 'ok'


@img.route('/upload', methods=['POST'])
def upload():
    """图片导入"""

    form = request.form
    ic_id   = toint(form.get('hidden_ic_id', '0'))
    img_title  = form.get('hidden_img_title', '').strip()
    _img_list = request.files.getlist('image[]')

    i = None
    ic = ImgCategory.query.get(ic_id)
    ic_name = ic.ic_name if ic else ''

    # 处理
    for _img in _img_list:
        img_title = _img.filename[:-4] if not img_title else img_title
        oss = AliyunOSS('img', current_app.config['SAVE_TARGET_PATH'])
        try:
            oss.save(_img)
            _img = oss.put_to_oss()
        except UploadNotAllowed, e:
            return u'头像必须是图片文件'
        except Exception, e:
            return u'发生错误，上传失败'

        i = Img.create(add_time=int(time.time()),
                        _img=_img,
                        ic_id=ic_id,
                        ic_name=ic_name,
                        img_title=img_title,)

    if not i:
        return u'至少上传一张图片'

    i.update(commit=True)

    return redirect(url_for('img.index'))
