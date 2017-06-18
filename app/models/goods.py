#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService


class Attr(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'attr'

    attr_id = db.Column(db.Integer, primary_key=True)
    attr_name = db.Column(db.String(255), default='')
    ag_id = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Attr => { \
attr_id:%d, attr_name:'%s', ag_id:%d}" % (
self.attr_id, self.attr_name, self.ag_id)

    __repr__ = __str__


class AttrGroup(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'attr_group'

    ag_id = db.Column(db.Integer, primary_key=True)
    ag_name = db.Column(db.String(255), default='')
    alias_name = db.Column(db.String(255), default='')
    ag_type = db.Column(db.Integer, default=0)

    def __str__(self):
        return "AttrGroup => { \
ag_id:%d, ag_name:'%s', alias_name:'%s', ag_type:%d}" % (
self.ag_id, self.ag_name, self.alias_name, self.ag_type)

    __repr__ = __str__


class Goods(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'goods'

    goods_id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.Integer, default=0)
    gc_id = db.Column(db.Integer, default=0)
    uid = db.Column(db.Integer, default=0)
    goods_name = db.Column(db.String(255), default='')
    goods_desc = db.Column(db.Text, default=None)
    goods_detail = db.Column(db.Text, default=None)
    goods_img = db.Column(db.String(255), default='')
    is_sale = db.Column(db.Integer, default=0)
    market_price = db.Column(db.Float, default=0.00)
    goods_price = db.Column(db.Float, default=0.00)
    prom_price = db.Column(db.Float, default=0.00)
    prom_begin_time = db.Column(db.Integer, default=0)
    prom_end_time = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)
    is_fresh = db.Column(db.Integer, default=0)
    is_free_shipping = db.Column(db.Integer, default=0)
    is_return = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)
    sale_count = db.Column(db.Integer, default=0)
    is_hot = db.Column(db.Integer, default=0)
    is_pre = db.Column(db.Integer, default=0)
    is_new = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    goods_attr = db.Column(db.Text, default=None)

    def __str__(self):
        return "Goods => { \
goods_id:%d, kind:%d, gc_id:%d, uid:%d, goods_name:'%s',  \
goods_desc:'%s', goods_detail:'%s', goods_img:'%s', is_sale:%d, market_price:%0.2f,  \
goods_price:%0.2f, prom_price:%0.2f, prom_begin_time:%d, prom_end_time:%d, quantity:%d,  \
is_fresh:%d, is_free_shipping:%d, is_return:%d, sort_order:%d, sale_count:%d,  \
is_hot:%d, is_pre:%d, is_new:%d, add_time:%d, goods_attr:'%s'}" % (
self.goods_id, self.kind, self.gc_id, self.uid, self.goods_name,
self.goods_desc, self.goods_detail, self.goods_img, self.is_sale, self.market_price,
self.goods_price, self.prom_price, self.prom_begin_time, self.prom_end_time, self.quantity,
self.is_fresh, self.is_free_shipping, self.is_return, self.sort_order, self.sale_count,
self.is_hot, self.is_pre, self.is_new, self.add_time, self.goods_attr)

    __repr__ = __str__

    @staticmethod
    def get_info_by_id(goods_id):
        goods = db.session.query(Goods.goods_id, Goods.goods_name, Goods.goods_desc,
                            Goods.is_sale, Goods.market_price, Goods.goods_price,
                            Goods.prom_price, Goods.prom_begin_time, Goods.prom_end_time,
                            Goods.quantity, Goods.unit, Goods.uf_id, Goods.florist_img).\
                        filter(Goods.goods_id == goods_id).first()
        return goods


class GoodsAttr(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'goods_attr'

    ga_id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer, default=0)
    attr_id = db.Column(db.Integer, default=0)
    attr_name = db.Column(db.String(255), default='')
    ag_id = db.Column(db.Integer, default=0)
    ag_name = db.Column(db.String(255), default='')

    def __str__(self):
        return "GoodsAttr => { \
ga_id:%d, goods_id:%d, attr_id:%d, attr_name:'%s', ag_id:%d,  \
ag_name:'%s'}" % (
self.ga_id, self.goods_id, self.attr_id, self.attr_name, self.ag_id,
self.ag_name)

    __repr__ = __str__


class GoodsCategory(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'goods_category'

    gc_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255), default='')
    parent_id = db.Column(db.Integer, default=0)
    node_chain = db.Column(db.String(255), default='')
    category_img = db.Column(db.String(255), default='')
    brief = db.Column(db.Text, default=None)
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "GoodsCategory => { \
gc_id:%d, category_name:'%s', parent_id:%d, node_chain:'%s', category_img:'%s',  \
brief:'%s', sort_order:%d, status:%d, add_time:%d}" % (
self.gc_id, self.category_name, self.parent_id, self.node_chain, self.category_img,
self.brief, self.sort_order, self.status, self.add_time)

    __repr__ = __str__

    @staticmethod
    def get_goods_cat_list(gc_id=0):
        """获取子分类列表"""
        return GoodsCategory.query.filter(GoodsCategory.parent_id == gc_id).all()


class GoodsGallery(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'goods_gallery'

    gg_id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer, default=0)
    img = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "GoodsGallery => { \
gg_id:%d, goods_id:%d, img:'%s', add_time:%d}" % (
self.gg_id, self.goods_id, self.img, self.add_time)

    __repr__ = __str__

    @staticmethod
    def list_by_goods_id(goods_id):
        """ 根据商品ID获取相册列表 """
        gallery_list = db.session.query(GoodsGallery.img).\
                                filter(GoodsGallery.goods_id == goods_id).all()
        return gallery_list


class GoodsSku(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'goods_sku'

    gs_id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(255), default='')
    sku_name = db.Column(db.String(255), default='')
    sku_price = db.Column(db.Float, default=0.00)
    sku_quantity = db.Column(db.Integer, default=0)

    def __str__(self):
        return "GoodsSku => { \
gs_id:%d, goods_id:%d, sku:'%s', sku_name:'%s', sku_price:%0.2f,  \
sku_quantity:%d}" % (
self.gs_id, self.goods_id, self.sku, self.sku_name, self.sku_price,
self.sku_quantity)

    __repr__ = __str__


class GoodsInColumn(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'goods_in_column'

    gic_id = db.Column(db.Integer, primary_key=True)
    first_gc_id = db.Column(db.Integer, default=0)
    second_gc_id = db.Column(db.Integer, default=0)
    goods_id = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "GoodsInColumn => { \
gic_id:%d, first_gc_id:%d, second_gc_id:%d, goods_id:%d, sort_order:%d,  \
add_time:%d}" % (
self.gic_id, self.first_gc_id, self.second_gc_id, self.goods_id, self.sort_order,
self.add_time)

    __repr__ = __str__


class GoodsColumn(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'goods_column'

    gc_id = db.Column(db.Integer, primary_key=True)
    column_name = db.Column(db.String(255), default='')
    parent_id = db.Column(db.Integer, default=0)
    node_chain = db.Column(db.String(255), default='')
    column_img = db.Column(db.String(255), default='')
    brief = db.Column(db.Text, default=None)
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "GoodsColumn => { \
gc_id:%d, column_name:'%s', parent_id:%d, node_chain:'%s', column_img:'%s',  \
brief:'%s', sort_order:%d, status:%d, add_time:%d}" % (
self.gc_id, self.column_name, self.parent_id, self.node_chain, self.column_img,
self.brief, self.sort_order, self.status, self.add_time)

    __repr__ = __str__


class AttrGroupInCategory(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'attr_group_in_category'

    agic_id = db.Column(db.Integer, primary_key=True)
    gc_id = db.Column(db.Integer, default=0)
    ag_id = db.Column(db.Integer, default=0)
    ag_type = db.Column(db.Integer, default=0)

    def __str__(self):
        return "AttrGroupInCategory => { \
agic_id:%d, gc_id:%d, ag_id:%d, ag_type:%d}" % (
self.agic_id, self.gc_id, self.ag_id, self.ag_type)

    __repr__ = __str__


class GoodsSpec(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'goods_spec'

    gs_id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer, default=0)
    spec_key = db.Column(db.String(255), default='')
    spec_value = db.Column(db.String(255), default='')
    sort_order = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "GoodsSpec => { \
gs_id:%d, goods_id:%d, spec_key:'%s', spec_value:'%s', sort_order:%d,  \
add_time:%d}" % (
self.gs_id, self.goods_id, self.spec_key, self.spec_value, self.sort_order,
self.add_time)

    __repr__ = __str__


class Spec(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'spec'

    spec_id = db.Column(db.Integer, primary_key=True)
    st_id = db.Column(db.Integer, default=0)
    spec_key = db.Column(db.String(255), default='')
    spec_value = db.Column(db.String(255), default='')
    sort_order = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Spec => { \
spec_id:%d, st_id:%d, spec_key:'%s', spec_value:'%s', sort_order:%d,  \
add_time:%d}" % (
self.spec_id, self.st_id, self.spec_key, self.spec_value, self.sort_order,
self.add_time)

    __repr__ = __str__


class SpecTemplate(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'spec_template'

    st_id = db.Column(db.Integer, primary_key=True)
    st_name = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "SpecTemplate => { \
st_id:%d, st_name:'%s', add_time:%d}" % (
self.st_id, self.st_name, self.add_time)

    __repr__ = __str__
