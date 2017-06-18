#!/usr/bin/env python
#coding=utf-8

import time
from decimal import Decimal
from flask import Blueprint, request, session, redirect, current_app, abort, url_for, g, render_template, make_response
from flask.ext.sqlalchemy import Pagination

from codingabc.helpers import log_debug, toint, get_count
from codingabc.database import db
from codingabc.ext.aliyun import AliyunOSS
from codingabc.ext.uploads import UploadNotAllowed

from app.helpers.common import easy_query_filter, get_params
from app.models.question import Question, QuestionAnswer, QuestionGallery
# from app.services.question import SaveSysSettingService

question = Blueprint('question', __name__)


@question.route('/')
@question.route('/<int:page>')
@question.route('/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """提问列表"""
    g.page_type = 'search'
    g.title = u'提问列表'

    args = request.args
    nickname = args.get('nickname', '').strip()
    title    = args.get('title', '').strip()
    begin_add_time = args.get('begin_add_time', '').strip()
    end_add_time = args.get('end_add_time', '').strip()

    q = Question.query

    if nickname:
        q = q.filter(Question.nickname.like(u'%'+ nickname +u'%'))

    if title:
        q = q.filter(Question.title.like(u'%'+ title +u'%'))

    if begin_add_time:
        begin_time = time.mktime(time.strptime(begin_add_time,'%Y-%m-%d'))
        q = q.filter(Question.add_time >= begin_time)

    if end_add_time:
        end_add_time = time.mktime(time.strptime(end_add_time,'%Y-%m-%d')) + 24*3600
        q = q.filter(Question.add_time < end_add_time)

    q_count = get_count(q)
    question_list  = q.order_by(Question.add_time.desc()).offset((page-1)*page_size).\
                    limit(page_size).all()

    pagination  = Pagination(None, page, page_size, q_count, None)

    res = make_response(render_template('question/index.html.j2', question_list=question_list, pagination=pagination))
    res.set_cookie('goback_url', request.url)
    return res


