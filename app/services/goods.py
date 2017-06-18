#!/usr/bin/env python
#coding=utf-8

import json, urllib2, time
from decimal import Decimal

from flask import current_app, request, session

from codingabc.database import db
from codingabc.ext.aliyun import AliyunOSS, UploadNotAllowed
from codingabc.helpers import log_debug, log_info, log_error, toint

from app.helpers.date_time import current_timestamp
from app.models.goods import Goods, GoodsAttr, GoodsCategory, GoodsGallery, GoodsSku, Attr, AttrGroup


class SaveGoodsService(object):
    """ 保存商品service """
    __slots__ = ('errmsg', 'form', 'goods_id', 'current_time', 'is_new', 'goods', 'goods_img', 'goods_gallery_list', 'goods_attr_list', 'goods_sku_list')
    def __init__(self, form, goods_id=0):
        self.errmsg             = {}
        self.form               = form
        self.goods_id           = goods_id
        self.current_time       = current_timestamp()
        self.is_new             = False
        self.goods              = None
        self.goods_img          = ''
        self.goods_gallery_list = []
        self.goods_attr_list    = []
        self.goods_sku_list     = []

    def check(self):
        """ 检查 """

        # 商品主图
        _goods_img = request.files.get('goods_img', None)

        # 商品相册
        _gallery_list = request.files.getlist('gallery')

        # 筛选属性
        _attr_id_list = request.form.getlist('attr_id')
        _attr_id_list = list(set(_attr_id_list))

        # SKU
        _sku_list          = request.form.getlist('sku')
        _sku_name_list     = request.form.getlist('sku_name')
        _sku_price_list    = request.form.getlist('sku_price')
        _sku_quantity_list = request.form.getlist('sku_quantity')

        # 是否创建商品
        self.is_new = True if self.goods_id == 0 else False

        # 检查 - 必填项
        required_arr = ['goods_name', 'is_sale', 'is_hot', 'is_pre', 'is_new', 'goods_price', 'is_free_shipping', 'is_return']
        for key in required_arr:
            value = self.form.get(key, '').strip()
            if not value:
                self.errmsg[key] = u'必填项'

        # 检查 - 新建商品是否上传商品主图
        if self.is_new and not _goods_img:
            self.errmsg['goods_img'] = u'必填项'

        gc_id = toint(self.form.get('gc_id', '0'))
        if gc_id <= 0:
            self.errmsg['gc_id'] = u'必填项'

        # 检查 - 商品是否存在
        if not self.is_new:
            self.goods = Goods.get(self.goods_id)
            if not self.goods:
                self.errmsg['submit'] = u'商品不存在'

        # 检查 - 商品主图是否合法
        if _goods_img:
            oss = AliyunOSS('goods', current_app.config['SAVE_TARGET_PATH'])
            try:
                oss.save(_goods_img)
                self.goods_img = oss.put_to_oss()
            except UploadNotAllowed, e:
                self.errmsg['goods_img'] = u'商品图片只允许是图片文件'
            except Exception, e:
                self.errmsg['goods_img'] = u'商品图片上传失败'

        # 检查 - 商品相册是否合法
        for gallery in _gallery_list:
            oss = AliyunOSS('goods', current_app.config['SAVE_TARGET_PATH'])
            try:
                oss.save(gallery)
                goods_gallery = oss.put_to_oss()
                self.goods_gallery_list.append(goods_gallery)
            except UploadNotAllowed, e:
                self.errmsg['gallery'] = u'商品相册图片只允许是图片文件'
            except Exception, e:
                self.errmsg['gallery'] = u'商品相册图片上传失败'

        # 检查 - 筛选属性是否合法
        for attr_id in _attr_id_list:
            if not self.is_new:
                goods_attr = GoodsAttr.query.filter(GoodsAttr.goods_id == self.goods_id).\
                                filter(GoodsAttr.attr_id == attr_id).first()
                if goods_attr:
                    continue

            attr = db.session.query(Attr.attr_id, Attr.attr_name, AttrGroup.ag_id, AttrGroup.ag_name).\
                            filter(Attr.ag_id == AttrGroup.ag_id).\
                            filter(Attr.attr_id == attr_id).first()
            self.goods_attr_list.append(attr)

        # 检查 - SKU是否合法
        for k in range(0, len(_sku_list)):
            sku          = _sku_list[k]
            sku_name     = _sku_name_list[k]
            sku_price    = _sku_price_list[k]
            sku_quantity = _sku_quantity_list[k]

            if not sku:
                self.errmsg['submit'] = u'SKU不能为空'

            if not sku_name:
                self.errmsg['submit'] = u'SKU名称不能为空'

            if not sku_price:
                self.errmsg['submit'] = u'SKU价格不能为空'

            if not sku_quantity:
                self.errmsg['submit'] = u'SKU库存不能为空'

            if not self.is_new:
                gs = GoodsSku.query.filter(GoodsSku.goods_id == self.goods_id).\
                        filter(GoodsSku.sku == sku).first()
                if gs:
                    continue

            goods_sku = {'sku':sku, 'sku_name':sku_name, 'sku_price':sku_price, 'sku_quantity':sku_quantity}
            self.goods_sku_list.append(goods_sku)

        if len(self.errmsg) > 0:
            return False

        return True

    def save(self):
        """ 保存 """

        gc_id            = toint(self.form.get('gc_id', 0))
        goods_name       = self.form.get('goods_name', '').strip()
        goods_desc       = self.form.get('goods_desc', '').strip()
        goods_detail     = self.form.get('goods_detail', '').strip()
        is_sale          = toint(self.form.get('is_sale', 0))
        kind             = toint(self.form.get('kind', 0))
        goods_price      = Decimal(self.form.get('goods_price', '0.00').strip())
        market_price     = Decimal(self.form.get('market_price', '0.00').strip())
        quantity         = toint(self.form.get('quantity', 0))
        sort_order       = toint(self.form.get('sort_order', 0))
        unit             = self.form.get('unit', '').strip()
        uf_id            = toint(self.form.get('uf_id', 0))
        uid              = session.get('uid', 0)
        is_hot           = toint(self.form.get('is_hot', '0'))
        is_pre           = toint(self.form.get('is_pre', '0'))
        is_new           = toint(self.form.get('is_new', '0'))
        sale_count       = toint(self.form.get('sale_count', 0))
        is_free_shipping = toint(self.form.get('is_free_shipping', 0))
        is_return        = toint(self.form.get('is_return', 0))
        goods_attr       = self.form.get('goods_attr', '').strip()

        if self.is_new:
            self.goods = Goods.create(add_time=self.current_time, commit=True)

        # 商品主图
        if self.goods_img:
            self.goods.update(goods_img=self.goods_img)

        # 相册
        for img in self.goods_gallery_list:
            GoodsGallery.create(goods_id=self.goods.goods_id, img=img, add_time=self.current_time)

        # 筛选属性
        for attr in self.goods_attr_list:
            GoodsAttr.create(goods_id=self.goods.goods_id, attr_id=attr.attr_id, attr_name=attr.attr_name,
                            ag_id=attr.ag_id, ag_name=attr.ag_name)

        # SKU
        for sku in self.goods_sku_list:
            GoodsSku.create(goods_id=self.goods.goods_id, sku=sku['sku'], sku_name=sku['sku_name'],
                        sku_price=sku['sku_price'], sku_quantity=sku['sku_quantity'])

        self.goods.update(gc_id=gc_id,
                        goods_name=goods_name,
                        is_hot=is_hot,
                        is_pre=is_pre,
                        is_new=is_new,
                        goods_attr=goods_attr,
                        goods_desc=goods_desc,
                        goods_detail=goods_detail,
                        sale_count=sale_count,
                        is_sale=is_sale,
                        market_price=market_price,
                        goods_price=goods_price,
                        kind=kind,
                        quantity=quantity,
                        sort_order=sort_order,
                        uid=uid,
                        unit=unit,
                        uf_id=uf_id,
                        is_return=is_return,
                        is_free_shipping=is_free_shipping,
                        commit=True)

        return True




