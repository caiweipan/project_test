#!/usr/bin/env python
#coding=utf-8

from hashlib import sha256

from flask import session, abort

from codingabc.helpers import log_debug, log_info, log_error, toint


def price_be_prom_or_sku_or_goods(goods, sku, current_time):
    """ 商品价格取prom_price还是sku_price还是goods_price """

    if current_time >= goods.prom_begin_time and current_time <= goods.prom_end_time:
        return goods.prom_price

    if sku.sku_price:
        return sku.sku_price

    return goods.goods_price




