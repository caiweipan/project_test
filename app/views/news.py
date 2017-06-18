#!/usr/bin/env python
#coding=utf-8

import time
from sqlalchemy import func, or_, not_
from flask import Blueprint, g, request, redirect, url_for, render_template, make_response, session
from flask.ext.sqlalchemy import Pagination

from codingabc.database import db
from codingabc.response import ResponseJson
from codingabc.ext.aliyun import AliyunOSS, UploadNotAllowed
from codingabc.helpers import log_debug, log_info, log_error, toint, get_count

from app.services.news import SaveNewsService
from app.helpers.common import easy_query_filter, list_pagination
from app.helpers.date_time import current_timestamp
from app.models.news import News, NewsGoods
from app.models.goods import Goods


news = Blueprint('news', __name__)

resjson = ResponseJson()
resjson.module_code = 12

@news.route('/list')
@news.route('/list/<int:page>')
@news.route('/list/<int:page>-<int:page_size>')
def news_list(page=1, page_size=20):
    """ 资讯列表 """
    g.page_type = 'search'
    g.title = u'资讯列表'
    g.add_new = True
    g.button_name = u'添加资讯'

    args = request.args
    title = args.get('title', '').strip()
    begin_add_time = args.get('begin_add_time', '').strip()
    end_add_time = args.get('end_add_time', '').strip()
    nc_id = toint(args.get('nc_id', '-1'))
    status = toint(args.get('status', '-1'))

    q = News.query
    query_dict = {'title':title, 'nc_id':nc_id, 'status':status,'begin_add_time':begin_add_time,'end_add_time':end_add_time,}

    q = News.query
    q = easy_query_filter(News,q,query_dict)

    news_count = get_count(q)
    news_list  = q.order_by(News.news_id.desc()).\
                        offset((page-1)*page_size).limit(page_size).all()

    pagination = Pagination(None, page, page_size, news_count, None)

    res = make_response(render_template('news/news_list.html.j2',
                news_list=news_list, pagination=pagination, Object=News, ))
    res.set_cookie('goback_url', request.url)
    return res


@news.route('/add', methods=['GET', 'POST'])
def news_add():
    """ 增加资讯 """
    g.page_type = ''
    g.title = u'增加资讯'

    # news_goods_list = db.session.query(NewsGoods.ng_id, NewsGoods.news_id, NewsGoods.goods_id,Goods.goods_name).\
    #                     filter(NewsGoods.goods_id == Goods.goods_id).\
    #                     filter(NewsGoods.news_id == News.news_id).all()

    return render_template('news/news_info.html.j2', f={'news_id':0}, **locals())


@news.route('/edit')
@news.route('/edit/<int:page>')
@news.route('/edit/<int:page>-<int:page_size>')
def news_edit(page=1, page_size=20):
    """ 编辑资讯 """
    g.page_type = ''
    g.title = u'编辑资讯'
    news_id = toint(request.args.get('news_id', '0'))
    goods_name = request.args.get('goods_name', '')
    redirect_url = request.args.get('redirect_url', '')
    news = News.query.filter(News.news_id == news_id).first()

    if news is None:
        return u'找不到资讯'

    news_goods_list = db.session.query(NewsGoods.ng_id, NewsGoods.news_id, NewsGoods.goods_id,
                                        NewsGoods.extend, NewsGoods.add_time, Goods.goods_name).\
                        filter(NewsGoods.goods_id == Goods.goods_id).\
                        filter(NewsGoods.news_id == News.news_id).\
                        filter(NewsGoods.news_id == news_id).\
                        order_by(NewsGoods.add_time.desc()).all()

    goods_id_list = map(lambda goods_id:goods_id,[news_goods.goods_id for news_goods in news_goods_list])

    goods_query = db.session.query(Goods.goods_id, Goods.goods_name).\
                    filter(not_(Goods.goods_id.in_(goods_id_list))).\
                    group_by(Goods.goods_id.asc())

    if goods_name:
        goods_query = goods_query.filter(Goods.goods_name.like(u'%'+goods_name+u'%'))

    goods_list = goods_query.order_by(Goods.add_time.desc()).all()

    pagination_info = list_pagination(goods_list, page,page_size)
    goods_list = pagination_info[0]
    pagination = pagination_info[1]
    news.jingdu_weidu = ''
    if news.longitude and news.latitude:
        news.jingdu_weidu = '%.6f,%.6f' % (news.longitude, news.latitude)

    return render_template('news/news_info.html.j2', f=news, **locals())


@news.route('/add/news_goods', methods=['GET', 'POST'])
def add_news_goods():
    """新增资讯商品"""

    """
    goods_id     = toint(request.args.get('goods_id', '0'))
    news_id      = toint(request.args.get('news_id', '0'))
    redirect_url = request.args.get('redirect_url', None)
    if goods_id <= 0 or news_id <=0:
        return u'参数出错'

    goods = Goods.query.get_or_404(goods_id)
    news  = News.query.get_or_404(news_id)
    if not goods:
        return u'新增资讯商品不存在'

    if not news:
        return u'找不到资讯'

    ng_info = NewsGoods.query.filter(NewsGoods.news_id == news_id).\
                filter(NewsGoods.goods_id == goods_id).first()

    if ng_info:
        return u'资讯商品已经存在，无需增加。'

    ng = NewsGoods()
    ng.goods_id = goods_id
    ng.news_id  = news_id
    ng.add_time = int(time.time())
    db.session.add(ng)
    db.session.commit()

    if redirect_url:
        return redirect(url_for('news.news_edit',news_id=news_id, redirect_url=redirect_url))
    return u'ok'
    """
    resjson.action_code = 10

    goods_id = toint(request.form.get('goods_id', 0))
    news_id  = toint(request.form.get('news_id', 0))
    extend   = request.form.get('extend', '')

    if goods_id <= 0 or news_id <= 0:
        return resjson.print_json(10, u'参数错误')

    goods = Goods.get(goods_id)
    if not goods:
        return resjson.print_json(11, u'找不到商品')

    news = News.get(news_id)
    if not news:
        return resjson.print_json(12, u'找不到资讯')

    news_goods = NewsGoods.query.filter(NewsGoods.news_id == news_id).filter(NewsGoods.goods_id == goods_id).first()
    if news_goods:
        return resjson.print_json(13, u'资讯的商品已经存在')

    NewsGoods.create(news_id=news_id, goods_id=goods_id, extend=extend, add_time=current_timestamp(), commit=True)

    return resjson.print_json(0, u'ok')


@news.route('/delete/news_goods')
def delete_news_goods():
    """删除资讯商品"""

    ng_id = toint(request.args.get('ng_id', '0'))
    if ng_id <= 0:
        return u'参数出错'

    ng = NewsGoods.query.get_or_404(ng_id)

    if ng:
        db.session.delete(ng)
        db.session.commit()

    return u'ok'


@news.route('/save', methods=['POST'])
def news_save():
    """ 保存资讯 """
    g.page_type = ''
    g.title = u'保存资讯'

    form = request.form
    news_id = toint(form.get('news_id', 0))

    sns = SaveNewsService(form, news_id)
    if not sns.check():
        g.errmsg = sns.errmsg
        log_info(u'### g.errmsg:%s'% g.errmsg)
        return render_template('news/news_info.html.j2', f=form)

    sns.save()

    return redirect(url_for('news.news_list'))



@news.route('/delete')
def delete():
    """ 删除资讯 """

    news_id = toint(request.args.get('news_id', '0'))

    if news_id <= 0:
        return u'参数出错'

    n = News.query.get_or_404(news_id)

    if n:
        db.session.delete(n)
        db.session.commit()

    return u'ok'


@news.route('/sort/modify')
def sort_modify():
    """修改排序"""

    news_id = toint(request.args.get('news_id', '0'))
    new_sort = toint(request.args.get('new_sort', '0'))
    new_sort = new_sort if new_sort > 0 else -1

    if new_sort < 0:
        return u'只能输入大于0的数字'

    if new_sort > 10000000:
        return u'数字不能过大'

    if news_id <= 0:
        return u'参数出错'

    news_info = News.get(news_id)

    if news_info:
        news_info.sort_order = new_sort
        db.session.commit()

    return u'ok'
