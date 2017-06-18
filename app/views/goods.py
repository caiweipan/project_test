#!/usr/bin/env python
#coding=utf-8

import time
from sqlalchemy import func, or_, not_
from flask import Blueprint, g, request, redirect, url_for, render_template, make_response, session
from flask.ext.sqlalchemy import Pagination

from codingabc.database import db
from codingabc.response import ResponseJson
from codingabc.helpers import log_debug, log_info, log_error, toint, get_count, current_app
from codingabc.ext.aliyun import AliyunOSS, UploadNotAllowed

from app.helpers.common import ktl_to_dl, easy_query_filter, get_params
from app.services.goods import SaveGoodsService
from app.models.goods import Attr, AttrGroup, Goods, GoodsAttr, GoodsGallery, GoodsSku, GoodsCategory, AttrGroupInCategory, GoodsColumn, GoodsInColumn, GoodsSpec, Spec, SpecTemplate

goods = Blueprint('goods', __name__)

resjson = ResponseJson()
resjson.module_code = 10

@goods.route('/list')
@goods.route('/list/<int:page>')
@goods.route('/list/<int:page>-<int:page_size>')
def goods_list(page=1, page_size=20):
    """ 商品列表 """
    g.page_type = 'search'
    g.title     = u'商品列表'
    g.add_new = True
    g.button_name = u'添加商品'
    args = request.args
    goods_id    = toint(args.get('goods_id', 0))
    goods_name  = args.get('goods_name', '').strip()
    gc_id       = toint(args.get('gc_id', 0))
    is_sale     = toint(args.get('is_sale', -1))
    kind        = toint(args.get('kind', '-1'))

    q = db.session.query(Goods.gc_id, Goods.goods_name, GoodsCategory.category_name, Goods.goods_img, Goods.goods_name, Goods.sort_order, Goods.goods_price, Goods.sale_count, Goods.kind, Goods.is_sale, Goods.goods_id, Goods.add_time).\
        filter(GoodsCategory.gc_id == Goods.gc_id)

    if goods_id:
        q = q.filter(Goods.goods_id == goods_id)

    if goods_name:
        like_goods_name = u'%' + goods_name + u'%'
        q = q.filter(Goods.goods_name.like(like_goods_name))

    if gc_id > 0:
        q = q.filter(Goods.gc_id == gc_id)

    if is_sale in (0, 1):
        q = q.filter(Goods.is_sale == is_sale)

    if kind >= 0:
        q = q.filter(Goods.kind == kind)

    # 商品分类列表
    goods_cat_list      = [{'name':u'请选择……', 'value':'-1'}]
    goods_cat_list_temp = db.session.query(GoodsCategory.category_name, GoodsCategory.gc_id).\
                                filter(GoodsCategory.gc_id == Goods.gc_id).\
                                group_by(GoodsCategory.gc_id).all()

    for goods_cat in goods_cat_list_temp:
        gc = {'name':goods_cat.category_name, 'value':goods_cat.gc_id}
        goods_cat_list.append(gc)

    goods_count = get_count(q)
    goods_list  = q.order_by(Goods.goods_id.desc()).all()

    pagination  = Pagination(None, page, page_size, goods_count, None)

    res = make_response(render_template('goods/goods_list.html.j2',**locals()))
    res.set_cookie('goback_url', request.url)
    return res


@goods.route('/add', methods=['GET', 'POST'])
def goods_add():
    """ 增加商品 """
    g.page_type = 'form'
    g.title     = u'增加商品'

    attr_group_list = AttrGroup.query.filter(AttrGroup.ag_type == 1).\
                            order_by(AttrGroup.ag_id.desc()).all()
    sku_group_list  = AttrGroup.query.filter(AttrGroup.ag_type == 2).\
                            order_by(AttrGroup.ag_id.desc()).all()

    category_list = GoodsCategory.query.all()
    return render_template('goods/goods_info.html.j2', f={}, category_list=category_list,
                attr_group_list=attr_group_list, sku_group_list=sku_group_list)


@goods.route('/edit/<int:goods_id>')
def goods_edit(goods_id):
    """ 编辑商品 """
    g.page_type = 'form'
    g.title     = u'编辑商品'

    check_type = request.args.get('check_type', '0') # 0. 基本信息 1.商品规格 2.相册
    goods = Goods.query.filter(Goods.goods_id == goods_id).first()
    # tags_value = None
    if goods is None:
        return u'找不到商品'

    attr_group_list = AttrGroup.query.filter(AttrGroup.ag_type == 1).\
                            order_by(AttrGroup.ag_id.desc()).all()
    sku_group_list  = AttrGroup.query.filter(AttrGroup.ag_type == 2).\
                            order_by(AttrGroup.ag_id.desc()).all()
    gallery_list    = GoodsGallery.query.filter(GoodsGallery.goods_id == goods_id).\
                            order_by(GoodsGallery.gg_id.desc()).all()
    attr_list       = GoodsAttr.query.filter(GoodsAttr.goods_id == goods_id).\
                            order_by(GoodsAttr.ga_id.desc()).all()
    sku_list        = GoodsSku.query.filter(GoodsSku.goods_id == goods_id).\
                            order_by(GoodsSku.gs_id.desc()).all()

    gs_list = GoodsSpec.query.filter(GoodsSpec.goods_id == goods_id).\
                            order_by(GoodsSpec.gs_id.desc()).all()

    st_list = SpecTemplate.query.order_by(SpecTemplate.st_id.desc()).all()

    category_list     = GoodsCategory.query.all()
    goods_cat_info    = GoodsCategory.query.get(goods.gc_id)
    # parent_gc_id_list = map(lambda parent_gc_id:parent_gc_id,goods_cat_info.node_chain.split(','))

    # for parent_gc_id in parent_gc_id_list:
    #     parent_goods_cat_info = GoodsCategory.query.get(parent_gc_id)
    #     if parent_goods_cat_info is None:
    #         return u'分类节点链出错'
    #     tags_value = parent_goods_cat_info.category_name + '/' if tags_value is None else tags_value + parent_goods_cat_info.category_name + '/'

    # tags_value = tags_value[:-1] if tags_value is not None else None
    gc_id      = goods_cat_info.gc_id if goods_cat_info else 0

    return render_template('goods/goods_info.html.j2', f=goods, **locals())


@goods.route('/save', methods=['POST'])
def goods_save():
    """ 保存商品 """
    g.page_type = 'form'
    g.title     = u'编辑商品'

    form = request.form
    goods_id = toint(form.get('goods_id', 0))

    sgs = SaveGoodsService(form, goods_id)
    if not sgs.check():
        g.errmsg = sgs.errmsg

        attr_group_list = AttrGroup.query.filter(AttrGroup.ag_type == 1).\
                                order_by(AttrGroup.ag_id.desc()).all()
        sku_group_list  = AttrGroup.query.filter(AttrGroup.ag_type == 2).\
                            order_by(AttrGroup.ag_id.desc()).all()
        gallery_list    = GoodsGallery.query.filter(GoodsGallery.goods_id == goods_id).\
                                order_by(GoodsGallery.gg_id.desc()).all()
        attr_list       = GoodsAttr.query.filter(GoodsAttr.goods_id == goods_id).\
                                order_by(GoodsAttr.ga_id.desc()).all()
        sku_list        = GoodsSku.query.filter(GoodsSku.goods_id == goods_id).\
                            order_by(GoodsSku.gs_id.desc()).all()
        category_list = GoodsCategory.query.all()
        return render_template('goods/goods_info.html.j2', f=form,category_list=category_list,
                    attr_group_list=attr_group_list, sku_group_list=sku_group_list,
                    gallery_list=gallery_list, attr_list=attr_list, sku_list=sku_list)

    sgs.save()

    return redirect(url_for('goods.goods_list'))


@goods.route('/attr_group/list')
@goods.route('/attr_group/list/<int:page>')
@goods.route('/attr_group/list/<int:page>-<int:page_size>')
def attr_group_list(page=1, page_size=20):
    """ 属性组列表 """
    g.page_type = 'search'
    g.title     = u'属性组列表'

    args = request.args
    ag_name = args.get('ag_name', '').strip()
    ag_type = toint(args.get('ag_type', -1))

    q = AttrGroup.query

    if ag_name:
        like_ag_name = u'%' + ag_name + u'%'
        q = q.filter(AttrGroup.ag_name.like(like_ag_name))

    if ag_type >= 0:
        ag_type = ag_type if ag_type in (1,2) else 0
        q = q.filter(AttrGroup.ag_type == ag_type)

    group_count = get_count(q)
    group_list  = q.order_by(AttrGroup.ag_id.desc()).all()
    pagination  = Pagination(None, page, page_size, group_count, None)

    res = make_response(render_template('goods/attr_group_list.html.j2',
                group_list=group_list, pagination=pagination))
    res.set_cookie('goback_url', request.url)
    return res


@goods.route('/attr_group/add', methods=['GET', 'POST'])
def attr_group_add():
    """ 增加属性组 """
    g.page_type = ''
    g.title     = u'增加属性组'

    return render_template('goods/attr_group_info.html.j2', f={})


@goods.route('/attr_group/edit/<int:ag_id>')
def attr_group_edit(ag_id):
    """ 编辑属性组 """
    g.page_type = ''
    g.title     = u'编辑属性组'
    g.attr_add  = True

    group = AttrGroup.query.filter(AttrGroup.ag_id == ag_id).first()

    if group is None:
        return u'找不到属性组'

    attr_list = db.session.query(Attr.attr_id, Attr.attr_name, Attr.ag_id, AttrGroup.ag_name, AttrGroup.ag_type).\
                filter(Attr.ag_id == AttrGroup.ag_id).\
                filter(Attr.ag_id == ag_id).\
                group_by(Attr.attr_id.asc()).\
                order_by(Attr.attr_id.desc()).all()

    return render_template('goods/attr_group_info.html.j2', f=group, attr_list=attr_list)


@goods.route('/attr/edit/<int:attr_id>')
def attr_edit(attr_id):
    """ 编辑属性 """
    g.page_type = 'form'
    g.title     = u'编辑属性'

    attr = Attr.query.filter(Attr.attr_id == attr_id).first()

    if attr is None:
        return u'找不到属性'

    attr_group_list = AttrGroup.query.order_by(AttrGroup.ag_id.desc()).all()

    return render_template('goods/attr_info.html.j2', f=attr, attr_group_list=attr_group_list)


@goods.route('/attr_group/save', methods=['POST'])
def attr_group_save():
    """ 保存属性组 """
    g.page_type = ''
    g.title     = u'编辑属性组'

    form = request.form
    ag_id   = toint(form.get('ag_id', 0))
    ag_name = form.get('ag_name', '').strip()
    ag_type = toint(form.get('ag_type', 0))

    errmsg, ag_type_list = {}, [1,2]

    # 检查
    if ag_id < 0:
        errmsg['ag_id'] = u'错误的属性组ID'
        g.errmsg = errmsg
        return render_template('goods/attr_group_info.html.j2', f=form)

    # 检查
    if not ag_name:
        errmsg['ag_name'] = u'请填写属性组名称'
        g.errmsg = errmsg
        return render_template('goods/attr_group_info.html.j2', f=form)

    # 检查
    if ag_type not in ag_type_list:
        errmsg['ag_type'] = u'请选择属性组类别'
        g.errmsg = errmsg
        return render_template('goods/attr_group_info.html.j2', f=form)

    # 检查
    attr_group = AttrGroup.query.filter(AttrGroup.ag_name == ag_name).\
                    filter(AttrGroup.ag_type == ag_type).first()
    if attr_group:
        errmsg['ag_type'] = u'属性组类别已经存在'
        g.errmsg = errmsg
        return render_template('goods/attr_group_info.html.j2', f=form)

    # 编辑
    if ag_id:
        # 检查
        attr_group = AttrGroup.get(ag_id)
        if not attr_group:
            errmsg['ag_type'] = u'属性组不存在'
            g.errmsg = errmsg
            return render_template('goods/attr_group_info.html.j2', f=form)
    # 创建
    else:
        attr_group = AttrGroup.create()

    attr_group.update(ag_name=ag_name, ag_type=ag_type, commit=True)

    return redirect(url_for('goods.attr_group_list'))


@goods.route('/attr/save', methods=['POST'])
def attr_save():
    """ 保存属性 """
    g.page_type = ''
    g.title     = u'编辑属性'

    form = request.form
    attr_id   = toint(form.get('attr_id', 0))
    attr_name = form.get('attr_name', '').strip()
    ag_id     = toint(form.get('ag_id', 0))

    errmsg = {}
    attr_group_list = AttrGroup.query.order_by(AttrGroup.ag_id.desc()).all()
    ag_id_list      = [ag.ag_id for ag in attr_group_list]

    # 检查
    if attr_id < 0:
        errmsg['submit'] = u'错误的属性ID'
        g.errmsg = errmsg
        return render_template('goods/attr_info.html.j2', f=form, attr_group_list=attr_group_list)

    # 检查
    if not attr_name:
        errmsg['submit'] = u'请填写属性名称'
        g.errmsg = errmsg
        return render_template('goods/attr_info.html.j2', f=form, attr_group_list=attr_group_list)

    # 检查
    if not ag_id:
        errmsg['submit'] = u'请选择属性组'
        g.errmsg = errmsg
        return render_template('goods/attr_info.html.j2', f=form, attr_group_list=attr_group_list)

    # 检查
    if ag_id not in ag_id_list:
        errmsg['submit'] = u'请选择正确的属性组'
        g.errmsg = errmsg
        return render_template('goods/attr_info.html.j2', f=form, attr_group_list=attr_group_list)

    # 检查
    attr = Attr.query.filter(Attr.attr_name == attr_name).\
                    filter(Attr.ag_id == ag_id).first()

    if attr:
        errmsg['submit'] = u'属性已经存在，无需再创建。'
        g.errmsg = errmsg
        return render_template('goods/attr_info.html.j2', f=form, attr_group_list=attr_group_list)

    # 编辑
    if attr_id:
        # 检查
        attr = Attr.get(attr_id)
        if not attr:
            errmsg['submit'] = u'属性不存在'
            g.errmsg = errmsg

            return render_template('goods/attr_info.html.j2', f=form, attr_group_list=attr_group_list)
    # 创建
    else:
        attr = Attr.create()

    attr.update(attr_name=attr_name, ag_id=ag_id, commit=True)

    return redirect(url_for('goods.attr_list'))


@goods.route('/save/attr', methods=['POST'])
def save_attr():
    """保存属性"""
    form = request.form

    attr_name = form.get('attr_name_modal', '')
    ag_id     = toint(form.get('ag_id', '0'))

    if ag_id <= 0:
        return u'参数出错'

    attr = Attr()
    attr.attr_name = attr_name
    attr.ag_id     = ag_id

    #判断是否重复
    is_exist_attr = Attr.query.filter(Attr.ag_id == ag_id).\
                    filter(Attr.attr_name == attr_name).all()

    if is_exist_attr:
        return u'属性已经存在，无需再创建。'

    db.session.add(attr)
    db.session.commit()

    return redirect(url_for('goods.attr_group_edit',ag_id=ag_id))


@goods.route('/gallery/delete/<int:gg_id>')
def gallery_delete(gg_id):
    """ ajax 删除相册图片 """

    resjson.action_code = 10

    gallery = GoodsGallery.query.get(gg_id)
    if gallery is None:
        return u'找不到相册'

    gallery.delete(commit=True)

    return resjson.print_json(0, u'ok')


@goods.route('/attr/delete/<int:ga_id>')
def attr_delete(ga_id):
    """ ajax 删除筛选属性 """

    resjson.action_code = 11

    ga = GoodsAttr.query.get(ga_id)
    if ga is None:
        return u'找不到筛选属性'

    ga.delete(commit=True)

    return resjson.print_json(0, u'ok')


@goods.route('/attr_group/delete')
def delete_attr_group():
    """删除属性组属性"""
    attr_id = toint(request.args.get('attr_id', '0'))
    if attr_id <= 0:
        return u'参数出错'

    attr = Attr.query.get_or_404(attr_id)
    if attr:
        db.session.delete(attr)
        db.session.commit()

    return u'ok'


@goods.route('/attr_name/modify')
def attr_name_modify():
    """修改属性组的属性名称"""

    new_attr_name = request.args.get('new_attr_name', '')
    attr_id       = toint(request.args.get('attr_id', '0'))

    if attr_id <= 0:
        return u'参数出错'

    attr = Attr.query.get_or_404(attr_id)
    if attr is None:
        return u'找不到属性'

    attr.attr_name = new_attr_name
    db.session.commit()

    return u'ok'


@goods.route('/attr_group/attr/list/', methods=['POST'])
def attr_group_attr_list():
    """ ajax 根据属性组获取属性列表 """

    resjson.action_code = 12

    ag_id = toint(request.form.get('ag_id'), 0)

    attr_list = Attr.query.filter(Attr.ag_id == ag_id).order_by(Attr.ag_id.desc()).all()

    return resjson.print_json(0, u'ok', {'attr_list':attr_list})


@goods.route('/sku/table', methods=['POST'])
def sku_table():
    """ ajax 根据SKU属性组列表生成SKU属性组合页面 """

    resjson.action_code = 13

    _sku_id_group_list, sku_id_group_list, sku_name_group_list = [], [], []
    sku_list, sku_name_list = [], []

    # 处理SKU属性组ID列表
    ag_id_list = request.form.getlist('ag_id_list[]')
    ag_id_list = list(set(ag_id_list))

    # 检查是否为空
    if len(ag_id_list) <= 0:
        return resjson.print_json(10, u'SKU属性组不能为空')
    # 生成SKU属性ID矩阵
    elif len(ag_id_list) == 1:
        ag_id_0   = ag_id_list[0]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_0).order_by(Attr.ag_id.asc()).all()
        list_0    = [attr.attr_id for attr in attr_list]

        _sku_id_group_list = [[k0] for k0 in list_0]
    # 生成SKU属性ID矩阵
    elif len(ag_id_list) == 2:
        ag_id_0   = ag_id_list[0]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_0).order_by(Attr.ag_id.asc()).all()
        list_0    = [attr.attr_id for attr in attr_list]

        ag_id_1   = ag_id_list[1]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_1).order_by(Attr.ag_id.asc()).all()
        list_1    = [attr.attr_id for attr in attr_list]

        _sku_id_group_list = [[k0, k1] for k0 in list_0 for k1 in list_1]
    # 生成SKU属性ID矩阵
    elif len(ag_id_list) == 3:
        ag_id_0   = ag_id_list[0]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_0).order_by(Attr.ag_id.asc()).all()
        list_0    = [attr.attr_id for attr in attr_list]

        ag_id_1   = ag_id_list[1]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_1).order_by(Attr.ag_id.asc()).all()
        list_1    = [attr.attr_id for attr in attr_list]

        ag_id_2   = ag_id_list[2]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_2).order_by(Attr.ag_id.asc()).all()
        list_2    = [attr.attr_id for attr in attr_list]

        _sku_id_group_list = [[k0, k1, k2] for k0 in list_0 for k1 in list_1 for k2 in list_2]
    # 生成SKU属性ID矩阵
    elif len(ag_id_list) == 4:
        ag_id_0   = ag_id_list[0]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_0).order_by(Attr.ag_id.asc()).all()
        list_0    = [attr.attr_id for attr in attr_list]

        ag_id_1   = ag_id_list[1]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_1).order_by(Attr.ag_id.asc()).all()
        list_1    = [attr.attr_id for attr in attr_list]

        ag_id_2   = ag_id_list[2]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_2).order_by(Attr.ag_id.asc()).all()
        list_2    = [attr.attr_id for attr in attr_list]

        ag_id_3   = ag_id_list[3]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_3).order_by(Attr.ag_id.asc()).all()
        list_3    = [attr.attr_id for attr in attr_list]

        _sku_id_group_list = [[k0, k1, k2, k3] for k0 in list_0 for k1 in list_1 for k2 in list_2 for k3 in list_3]
    # 生成SKU属性ID矩阵
    elif len(ag_id_list) == 5:
        ag_id_0   = ag_id_list[0]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_0).order_by(Attr.ag_id.asc()).all()
        list_0    = [attr.attr_id for attr in attr_list]

        ag_id_1   = ag_id_list[1]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_1).order_by(Attr.ag_id.asc()).all()
        list_1    = [attr.attr_id for attr in attr_list]

        ag_id_2   = ag_id_list[2]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_2).order_by(Attr.ag_id.asc()).all()
        list_2    = [attr.attr_id for attr in attr_list]

        ag_id_3   = ag_id_list[3]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_3).order_by(Attr.ag_id.asc()).all()
        list_3    = [attr.attr_id for attr in attr_list]

        ag_id_4   = ag_id_list[4]
        attr_list = db.session.query(Attr.attr_id).filter(Attr.ag_id == ag_id_4).order_by(Attr.ag_id.asc()).all()
        list_4    = [attr.attr_id for attr in attr_list]

        _sku_id_group_list = [[k0, k1, k2, k3, k4] for k0 in list_0 for k1 in list_1 for k2 in list_2 for k3 in list_3 for k4 in list_4]
    # 检查最大长度
    else:
        return resjson.print_json(11, u'SKU属性组不能超过5个')

    # SKU属性ID按照从小到大排列
    for sku_group in _sku_id_group_list:
        sku_group.sort()
        sku_id_group_list.append(sku_group)

    # 生成SKU属性名称矩阵
    id_name = {}
    for id_list in sku_id_group_list:
        name_list = []
        for sku_id in id_list:
            sku_name = id_name.get(sku_id, '')
            if not sku_name:
                sku      = db.session.query(Attr.attr_name).filter(Attr.attr_id == sku_id).first()
                sku_name = sku.attr_name if sku else ''
                id_name[sku_id] = sku_name
            name_list.append(sku_name)
        sku_name_group_list.append(name_list)

    # 转换成SKU列表
    for id_list in sku_id_group_list:
        id_list = [_id.__str__() for _id in id_list]
        sku     = ','.join(id_list)
        sku_list.append(sku)

    # 转换成SKU名称列表
    for name_list in sku_name_group_list:
        sku_name = ','.join(name_list)
        sku_name_list.append(sku_name)

    html_text = render_template('goods/sku_table.html.j2', sku_list=sku_list, sku_name_list=sku_name_list)

    return resjson.print_json(0, u'ok', {'html_text':html_text})


@goods.route('/sku/delete/<int:gs_id>')
def sku_delete(gs_id):
    """ ajax 删除SKU """

    resjson.action_code = 14

    gs = GoodsSku.query.get(gs_id)
    if gs is None:
        return u'找不到筛选属性'

    gs.delete(commit=True)

    return resjson.print_json(0, u'ok')


@goods.route('/sort/modify')
def sort_modify():
    """修改排序"""

    goods_id = toint(request.args.get('goods_id', '0'))
    new_sort = toint(request.args.get('new_sort', '0'))
    new_sort = new_sort if new_sort > 0 else -1

    if new_sort < 0:
        return u'只能输入大于0的数字'

    if new_sort > 10000000:
        return u'数字不能过大'

    if goods_id <= 0:
        return u'参数出错'

    goods_info = Goods.get(goods_id)

    if goods_info:
        goods_info.sort_order = new_sort
        db.session.commit()

    return u'ok'


@goods.route('/column_sort/modify')
def column_sort_modify():
    """修改商品栏目排序"""

    gc_id = toint(request.args.get('gc_id', '0'))
    new_sort = toint(request.args.get('new_sort', '0'))
    new_sort = new_sort if new_sort > 0 else -1

    if new_sort < 0:
        return u'只能输入大于0的数字'

    if new_sort > 10000000:
        return u'数字不能过大'

    if gc_id <= 0:
        return u'参数出错'

    gc = GoodsColumn.get(gc_id)

    if gc:
        gc.sort_order = new_sort
        db.session.commit()

    return u'ok'


@goods.route('/in_column_sort/modify')
def in_column_sort_modify():
    """修改栏目商品排序"""

    gic_id = toint(request.args.get('gic_id', '0'))
    new_sort = toint(request.args.get('new_sort', '0'))
    new_sort = new_sort if new_sort > 0 else -1

    if new_sort < 0:
        return u'只能输入大于0的数字'

    if new_sort > 10000000:
        return u'数字不能过大'

    if gic_id <= 0:
        return u'参数出错'

    gic = GoodsInColumn.get(gic_id)

    if gic:
        gic.sort_order = new_sort
        db.session.commit()

    return u'ok'


@goods.route('/category/list')
@goods.route('/category/list/<int:page>')
@goods.route('/category/list/<int:page>-<int:page_size>')
def category_list(page=1, page_size=20):
    """ 分类列表 """
    g.page_type = 'search'
    g.title     = u'分类列表'
    g.add_new = True
    g.button_name = u'创建分类'
    args           = request.args
    gc_id          = toint(args.get('gc_id', 0))
    category_name  = args.get('category_name', '').strip()
    begin_add_time = args.get('begin_add_time', '')
    end_add_time   = args.get('end_add_time', '')

    q = GoodsCategory.query

    if category_name:
        q = q.filter(GoodsCategory.category_name.like(u'%'+category_name+u'%'))

    if gc_id > 0:
        q = q.filter(GoodsCategory.gc_id == gc_id)

    if begin_add_time:
        begin_add_time = time.mktime(time.strptime(begin_add_time,'%Y-%m-%d'))
        q = q.filter(GoodsCategory.add_time >= begin_add_time)

    if end_add_time:
        end_add_time = time.mktime(time.strptime(end_add_time,'%Y-%m-%d'))
        q = q.filter(GoodsCategory.add_time <= end_add_time)

    category_count = get_count(q)

    category_list  = q.order_by(GoodsCategory.gc_id.desc()).all()
    pagination = Pagination(None, page, page_size, category_count, None)

    res = make_response(render_template('goods/category_list.html.j2',
                category_list=category_list, pagination=pagination))
    res.set_cookie('goback_url', request.url)
    return res


@goods.route('/category/save', methods=['POST'])
def category_save():
    """ 保存分类 """
    g.page_type = ''
    g.title     = u'保存分类'

    form = request.form
    edit_gc_id        = toint(form.get('edit_gc_id', '0'))
    category_name     = form.get('category_name', '').strip()
    brief             = form.get('brief', '')
    sort_order        = toint(form.get('sort_order', '0'))
    status            = toint(form.get('status', '-1'))
    category_img      = request.files['category_img']
    errmsg            = {}

    # GoodsCategory表是否为空
    goods_category_list = GoodsCategory.query.all()
    if edit_gc_id <= 0:
        gs = GoodsCategory()
        db.session.add(gs)
    else:
        gs = GoodsCategory.query.get_or_404(edit_gc_id)

    #判段新增商品分类是否重复
    is_exit_category = GoodsCategory.query.filter(GoodsCategory.gc_id != edit_gc_id).\
                        filter(GoodsCategory.category_name == category_name).first()
    if is_exit_category:
        errmsg['category_name'] = u'新增商品分类已经存在'
        g.errmsg = errmsg
        return render_template('goods/category_add.html.j2', f=form,**locals())

    if category_img:
        oss = AliyunOSS('user', current_app.config['SAVE_TARGET_PATH'])
        try:
            oss.save(category_img)
            gs.category_img = oss.put_to_oss()
        except UploadNotAllowed, e:
            errmsg['category_img'] = u'只允许是图片文件'
            return render_template('goods/category_add.html.j2', f=form,**locals())
        except Exception, e:
            errmsg['category_img'] = u'原图上传失败'
            return render_template('goods/category_add.html.j2', f=form,**locals())

    gs.node_chain    = gs.gc_id
    gs.category_name = category_name
    gs.brief         = brief
    gs.sort_order    = sort_order
    gs.status        = status
    gs.add_time      = int(time.time())
    db.session.commit()
    return redirect(url_for('goods.category_list'))


@goods.route('/category_add')
def category_add():
    """新增商品分类"""

    g.page_type = ''
    g.title     = u'新增商品分类'

    goods_cat_list = GoodsCategory.query.filter(GoodsCategory.parent_id == 0).all()
    for goods_cat in goods_cat_list:
        setattr(goods_cat, 'goods_cat_name',goods_cat.category_name)
    return render_template('goods/category_add.html.j2', f={},goods_cat_list=goods_cat_list)


@goods.route('/category/edit')
def category_edit():
    """ 编辑商品分类 """
    g.page_type = ''
    g.title = u'编辑商品分类'

    gc_id = toint(request.args.get('gc_id', '0'))
    if gc_id <= 0:
        return u'参数出错'
    edit_gc_id     = gc_id
    goods_cat_info = GoodsCategory.query.get_or_404(gc_id)
    parent_gc_id   = goods_cat_info.parent_id if goods_cat_info.parent_id else None
    node_chain_arr = goods_cat_info.node_chain
    cat_name_chain = None
    chain_gc_id_list = map(lambda gc_id:gc_id, node_chain_arr.split(','))
    parent_gc_id_list = chain_gc_id_list[:-1]
    goods_cat_list = []
    for gc_id in parent_gc_id_list:
        gc = GoodsCategory()
        if not gc_id:
            continue
        gc_id = toint(gc_id)
        if gc_id <= 0:
            return u'节点链数据不正确'
        parent_cat_info = GoodsCategory.query.get_or_404(gc_id)

        parent_cat_name = parent_cat_info.category_name
        setattr(gc,'goods_cat_name', parent_cat_name)
        setattr(gc,'gc_id', gc_id)
        goods_cat_list.append(gc)

    attr_group_cat_list = db.session.query(AttrGroupInCategory.agic_id, AttrGroupInCategory.gc_id, AttrGroup.ag_name,AttrGroup.ag_id, AttrGroup.alias_name, AttrGroup.ag_type).\
                            filter(AttrGroupInCategory.ag_id == AttrGroup.ag_id).\
                            filter(AttrGroupInCategory.gc_id == edit_gc_id).\
                            group_by(AttrGroupInCategory.agic_id.desc()).all()

    agic_ag_id_list = db.session.query(AttrGroupInCategory.ag_id).filter(AttrGroupInCategory.gc_id == edit_gc_id).all()

    agic_ag_id_list = map(lambda ag_id:ag_id,[agic_ag_id.ag_id for agic_ag_id in agic_ag_id_list])
    attr_group_list = db.session.query(AttrGroup.ag_id, AttrGroup.ag_name).\
                        filter(not_(AttrGroup.ag_id.in_(agic_ag_id_list))).\
                        group_by(AttrGroup.ag_id.asc()).\
                        order_by(AttrGroup.ag_id.desc()).all()

    return render_template('goods/category_add.html.j2', f=goods_cat_info,**locals())


@goods.route('/category/add_attr_group')
def add_attr_group():
    """添加分类属性"""

    args = request.args
    gc_id = toint(args.get('edit_gc_id', '0'))
    ag_id = toint(args.get('ag_id', '0'))
    errmsg = {}

    if ag_id <= 0 or gc_id <= 0:
        return u'参数出错'

    ag_info = AttrGroup.query.get_or_404(ag_id)
    goods_cat_info = GoodsCategory.query.get_or_404(gc_id)

    if not ag_info:
        return u'找不到属性组'

    if not goods_cat_info:
        return u'找不到对应的商品分类'

    # 判断是否重复
    agic = AttrGroupInCategory.query.filter(AttrGroupInCategory.gc_id == gc_id).\
            filter(AttrGroupInCategory.ag_id == ag_id).first()

    if agic:
        return u'新增属性组已经存在'

    agic = AttrGroupInCategory()
    agic.gc_id = gc_id
    agic.ag_id = ag_id
    agic.ag_type = ag_info.ag_type
    db.session.add(agic)
    db.session.commit()

    return u'ok'


@goods.route('/column/list')
@goods.route('/column/list/<int:page>')
@goods.route('/column/list/<int:page>-<int:page_size>')
def column_list(page=1, page_size=20):
    """ 商品栏目列表 """

    g.page_type = 'search'
    g.title     = u'商品栏目列表'

    args           = request.args
    gc_id          = toint(args.get('gc_id', '0'))
    column_name    = args.get('column_name', '').strip()
    status         = toint(args.get('status', '-1'))
    begin_add_time = args.get('begin_add_time', '')
    end_add_time   = args.get('end_add_time', '')

    gc_id = gc_id if gc_id > 0 or args.get('gc_id', '') == '0'  else -1

    query_dict = {'gc_id':gc_id,'column_name':column_name,'status':status,'begin_add_time':begin_add_time,'end_add_time':end_add_time,}

    q = GoodsColumn.query
    q = easy_query_filter(GoodsColumn,q,query_dict)

    column_count = get_count(q)
    column_list  = q.order_by(GoodsColumn.gc_id.desc()).all()

    pagination = Pagination(None, page, page_size, column_count, None)

    res = make_response(render_template('goods/column.html.j2',
                column_list=column_list, pagination=pagination))
    res.set_cookie('goback_url', request.url)
    return res


@goods.route('/column/edit')
def column_edit():
    """商品栏目编辑"""

    g.page_type = ''
    g.title     = u'商品栏目编辑'
    args  = request.args
    gc_id = toint(args.get('gc_id', '0'))
    goods_column_info = GoodsColumn.query.get_or_404(gc_id)
    goods_in_column_list = GoodsInColumn.query.filter(GoodsInColumn.first_gc_id == gc_id).all()
    first_gc_id_list = map(lambda goods_in_column:goods_in_column.first_gc_id, [goods_in_column for goods_in_column in goods_in_column_list])
    column_goods_list = []
    for goods_in_column in goods_in_column_list:
        # 获取一级栏目商品信息
        first_gc_info = GoodsColumn.query.get(goods_in_column.first_gc_id)
        first_column_name = first_gc_info.column_name if first_gc_info else u''
        first_gc_id = goods_in_column.first_gc_id if goods_in_column else 0

        # 获取二级栏目商品信息
        second_gc_info = GoodsColumn.query.get(goods_in_column.second_gc_id)
        second_column_name = second_gc_info.column_name if second_gc_info else u''
        second_gc_id = second_gc_info.column_name if second_gc_info else 0

        # # 获取商品信息
        goods = Goods.query.get(goods_in_column.goods_id)
        goods_id = goods.goods_id if goods else 0
        goods_name = goods.goods_name if goods else u''

        goods_in_column_dict = {'gic_id':goods_in_column.gic_id,'first_column_name':first_column_name,'first_gc_id':first_gc_id,'second_column_name':second_column_name, 'second_gc_id':second_gc_id,'goods_name':goods_name, 'goods_id':goods_id,'sort_order':goods_in_column.sort_order, 'add_time':goods_in_column.add_time}
        column_goods_list.append(goods_in_column_dict)

    goods_column_list = GoodsColumn.query.filter(not_(GoodsColumn.gc_id.in_(first_gc_id_list))).all()

    goods_list = db.session.query(Goods.goods_id, Goods.goods_name).all()

    return render_template('goods/column_detail.html.j2',f=goods_column_info, **locals())


@goods.route('/column/delete')
def delete_column():
    """移除商品栏目"""

    gc_id = toint(request.args.get('gc_id', '0'))
    if gc_id <= 0:
        return u'参数出错'

    gc = GoodsColumn.query.get_or_404(gc_id)

    if gc:
        db.session.delete(gc)
        db.session.commit()
    else:
        return u'找不到商品栏目'

    return u'ok'

@goods.route('/column_goods/delete')
def delete_column_goods():
    """移除栏目商品"""

    gic_id = toint(request.args.get('gic_id', '0'))
    if gic_id <= 0:
        return u'参数出错'

    gic = GoodsInColumn.query.get_or_404(gic_id)

    if gic:
        db.session.delete(gic)
        db.session.commit()
    else:
        return u'找不到栏目商品'

    return u'ok'


@goods.route('/goods_column/save')
def goods_column_save():
    """保存栏目商品"""

    args = request.args
    gc_id = toint(args.get('gc_id', '0'))
    goods_id = toint(args.get('goods_id', '0'))
    sort_order = toint(args.get('sort_order', '0'))

    if gc_id <= 0:
        return u'请先新增商品栏目'

    if goods_id <= 0:
        return '请选择商品'

    gc = GoodsColumn.query.get(gc_id)

    if not gc:
        return u'找不到商品栏目'

    # 一级栏目商品id
    first_gc_id = gc.gc_id

    # 二级栏目商品id
    if gc.parent_id > 0:
        second_gc = GoodsColumn.query.get(gc.parent_id)
        second_gc_id = second_gc.second_gc_id
    else:
        second_gc_id = 0

    GoodsInColumn.create(first_gc_id=first_gc_id, second_gc_id=second_gc_id, goods_id=goods_id,sort_order=sort_order ,add_time=int(time.time()), commit=True)

    return u'ok'


@goods.route('/column/save', methods=['POST'])
def column_save():
    """保存商品栏目"""

    param_dict  = get_params({'gc_id':int,'column_name':str,'column_img':None,'status':int,'sort_order':int, 'brief':str})
    required_param_list = ['column_name','status']
    form = request.form
    for param in required_param_list:
        val = request.form.get(param, '')
        val = val.strip()
        if not val:
            errmsg[param] = u'必填项'
            g.errmsg = errmsg
            log_debug('errmsg:%s'%g.errmsg)
            return render_template('goods/column_detail.html.j2', f=form,**locals())

    # 检查 - 封面原图是否合法
    column_img = param_dict['column_img']
    if column_img:
        oss = AliyunOSS('goods', current_app.config['SAVE_TARGET_PATH'])
        try:
            oss.save(column_img)
            column_img = oss.put_to_oss()
        except UploadNotAllowed, e:
            errmsg['column_img'] = u'图片只允许是图片文件'
        except Exception, e:
            errmsg['column_img'] = u'图片上传失败'

    gc_id = param_dict['gc_id']
    is_new = True if gc_id <= 0 else False

    if is_new:
        goods_column_info = GoodsColumn.create(add_time=int(time.time()), commit=True)
    else:
        goods_column_info = GoodsColumn.query.get_or_404(gc_id)

    if column_img:
        goods_column_info.update(column_img=column_img)

    goods_column_info.update(column_name=param_dict['column_name'], status=param_dict['status'], sort_order=param_dict['sort_order'], brief=param_dict['brief'], commit=True)

    gc_id = goods_column_info.gc_id
    return redirect(url_for('goods.column_edit', gc_id=gc_id))


@goods.route('/column/add')
def column_add():
    """新增商品栏目"""
    gc_id = 0
    goods_column_list = GoodsColumn.query.all()
    goods_list = db.session.query(Goods.goods_id, Goods.goods_name).all()
    return render_template('goods/column_detail.html.j2',f={}, **locals())


# @goods.route('/category_name')
# def category_name():
#     """ 返回上级分类 """
#     resjson.action_code = 15
#     edit_gc_id = toint(request.args.get('edit_gc_id', '0'))
#     tags_value = request.args.get('tags_value', '')
#     goods_id   = toint(request.args.get('goods_id', '0'))

#     category_name_list = db.session.query(GoodsCategory.gc_id, GoodsCategory.category_name, GoodsCategory.parent_id).\
#                             filter(GoodsCategory.category_name.like(u'%'+tags_value+u'%')).all()
#     if edit_gc_id > 0:
#         edit_goods_cat = GoodsCategory.query.get_or_404(edit_gc_id)
#         node_chain_arr = edit_goods_cat.node_chain
#         chain_gc_id_list = map(lambda gc_id:gc_id, node_chain_arr.split(','))
#         category_name_list = db.session.query(GoodsCategory.gc_id, GoodsCategory.category_name, GoodsCategory.parent_id).\
#                                 filter(GoodsCategory.gc_id.in_(chain_gc_id_list)).\
#                                 filter(GoodsCategory.category_name.like(u'%'+tags_value+u'%')).\
#                                 filter(GoodsCategory.gc_id != edit_gc_id).all()

#     if goods_id > 0:
#         goods_info = Goods.query.get_or_404(goods_id)
#         goods_cat_info =  GoodsCategory.query.get_or_404(goods_info.gc_id)
#         node_chain_arr = goods_cat_info.node_chain
#         chain_gc_id_list = map(lambda gc_id:gc_id, node_chain_arr.split(','))
#         category_name_list = db.session.query(GoodsCategory.gc_id, GoodsCategory.category_name, GoodsCategory.parent_id).\
#                                 filter(GoodsCategory.gc_id.in_(chain_gc_id_list)).\
#                                 filter(GoodsCategory.category_name.like(u'%'+tags_value+u'%')).all()

#     category_name_list = ktl_to_dl(category_name_list)

#     for key in range(0, len(category_name_list)):
#         cat = category_name_list[key]
#         goods_parent_info = GoodsCategory.query.filter(GoodsCategory.gc_id == cat['parent_id']).first()
#         goods_parent_name = goods_parent_info.category_name if goods_parent_info else ''
#         category_name_list[key]['category_name'] = '%s/%s' % (goods_parent_name, cat['category_name']) if goods_parent_name else '%s'%cat['category_name']

#     return resjson.print_json(0, u'ok', {'category_name_list':category_name_list})


@goods.route('/spec')
@goods.route('/spec/<int:page>')
@goods.route('/spec/<int:page>-<int:page_size>')
def spec(page=1, page_size=20):
    """ 规格模板列表 """
    g.page_type = 'search'
    g.title     = u'规格模板列表'
    g.add_new = True
    g.button_name = u'新增规格模板'

    args = request.args
    st_name  = args.get('st_name', '').strip()

    q = SpecTemplate.query

    if st_name:
        q = q.filter(SpecTemplate.st_name.like(u'%' + st_name + u'%'))

    spec_count = get_count(q)
    st_list  = q.order_by(SpecTemplate.add_time.desc()).all()

    pagination  = Pagination(None, page, page_size, spec_count, None)

    res = make_response(render_template('goods/spec_template.html.j2',**locals()))
    res.set_cookie('goback_url', request.url)
    return res


@goods.route('/st_save')
def st_save():
    """保存规格模板"""

    args = request.args
    st_name  = args.get('st_name', '').strip()
    st_id = toint(args.get('st_id', '0'))
    log_info('### st_name:%s, st_id:%s'%(st_name, st_id))
    if st_id > 0:
        st = SpecTemplate.query.get(st_id)
        if not st:
            return u'获取模板失败'
    else:
        st = SpecTemplate.create(add_time=int(time.time()))

    st.update(st_name=st_name, commit=True)

    return u'ok'


@goods.route('/st_detail')
def st_detail():
    """规格模板详情"""

    st_id = toint(request.args.get('st_id', '0'))

    if st_id <= 0:
        return u'参数出错'

    st = SpecTemplate.query.get(st_id)

    if not st:
        return u'获取规格模板失败'
    spec_list = Spec.query.filter(Spec.st_id == st.st_id).\
                    order_by(Spec.add_time.desc()).all()
    return render_template('goods/st_detail.html.j2', f=st, **locals())


@goods.route('/spec_add')
def spec_add():
    """新增规格"""

    args       = request.args
    spec_id    = toint(args.get('spec_id', '0'))
    st_id      = toint(args.get('st_id', '0'))
    sort_order = toint(args.get('sort_order', '0'))
    spec_key   = args.get('spec_key', '')
    spec_value = args.get('spec_value', '')

    if spec_id > 0:
        s = Spec.query.get(spec_id)
        if not s:
            return u'获取规格信息失败'
    else:
        s = Spec.create(add_time=int(time.time()))

    s.update(st_id=st_id, spec_key=spec_key, spec_value=spec_value, sort_order=sort_order, commit=True)

    return u'ok'


@goods.route('/st_add')
def st_add():
    """添加商品模板"""

    args = request.args
    goods_id = toint(args.get('goods_id', '0'))
    st_id    = toint(args.get('st_id', '0'))

    if st_id <= 0 or goods_id <= 0:
        return u'参数出错'

    st = SpecTemplate.query.get(st_id)

    s_list = Spec.query.filter(Spec.st_id == st.st_id).all()

    goods = Goods.query.get(goods_id)

    if not goods:
        return u'获取商品信息失败'

    gs = None
    for s in s_list:
        is_gs_exit = GoodsSpec.query.filter(GoodsSpec.goods_id == goods_id).\
                        filter(GoodsSpec.spec_key == s.spec_key).\
                        filter(GoodsSpec.spec_value == s.spec_value).first()

        if is_gs_exit:
            log_info('### is_gs_exit:%s'% is_gs_exit)
            continue
        gs = GoodsSpec.create(goods_id=goods_id,
                             spec_key=s.spec_key,
                             spec_value=s.spec_value,
                             sort_order=s.sort_order,
                             add_time=int(time.time()))

    if not gs:
        return u'新增模板已经存在'

    gs.update(commit=True)
    return u'ok'


@goods.route('/gs_edit')
def gs_edit():
    """编辑商品规格"""

    args = request.args
    spec_key  = args.get('spec_key', '').strip()
    spec_value  = args.get('spec_value', '').strip()
    sort_order  = args.get('sort_order', '').strip()
    gs_id = toint(args.get('gs_id', '0'))

    if gs_id <= 0:
        return u'参数出错'

    gs = GoodsSpec.query.get(gs_id)

    if not gs:
        return u'获取规格信息失败'

    gs.update(spec_key=spec_key, spec_value=spec_value, sort_order=sort_order, commit=True)

    return u'ok'


@goods.route('/st_delete')
def st_delete():
    """移除规格模板"""

    st_id = toint(request.args.get('st_id', '0'))

    st = SpecTemplate.query.get(st_id)

    if not st:
        return u'该模板已经被移除'

    st.delete(commit=True)

    return u'ok'


@goods.route('/gs_delete')
def gs_delete():
    """移除商品规格"""

    gs_id = toint(request.args.get('gs_id', '0'))

    gs = GoodsSpec.query.get(gs_id)

    if not gs:
        return u'该规格已经被移除'

    gs.delete(commit=True)

    return u'ok'


@goods.route('/s_delete')
def s_delete():
    """移除规格"""

    spec_id = toint(request.args.get('spec_id', '0'))

    s = Spec.query.get(spec_id)

    if not s:
        return u'该规格已经被移除'

    s.delete(commit=True)

    return u'ok'
