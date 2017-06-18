#!/usr/bin/env python
#coding=utf-8
import json
import time, random
from hashlib import md5

from flask import request, session

from codingabc.database import db
from codingabc.helpers import toint, log_debug, log_info, log_error, ismobile, randomstr, conver_model, current_app

from app.helpers.date_time import str2timestamp
from app.models.comment import Comment
from app.models.goods import Goods
from app.models.user import User
from codingabc.ext.aliyun import AliyunOSS
from codingabc.ext.uploads import UploadNotAllowed


class GoodsCommentSaveService(object):
    """项目评价service"""
    def __init__(self, goods_id=0):

        self.errmsg           = {}
        self.comment          = None
        self.user             = None
        self.admin            = None


    def _check_param(self, form):
        """检查表单"""
        required_param_list = ['star', 'content']
        for param in required_param_list:
            val = form.get(param, '')
            val = val.strip()
            if not val:
                self.errmsg[param] = u'必填项'

        content = form.get('content', '')
        star  = toint(form.get('star', '0'))

        if content is None:
            self.errmsg['content'] = u'请输入评价内容'

        if star is None:
            self.errmsg['star'] = u'请输入评价分数'

        if self.errmsg:
            log_debug(self.errmsg)
            return

    def save(self, form):
        """保存评价信息"""
        self._check_param(form)

        if self.errmsg:
            return self.errmsg

        goods_id = toint(form.get('goods_id', '0'))
        uid      = toint(session.get('uid'))
        content  = form.get('content', '')
        star     = toint(form.get('star', '1'))
        comment  = Comment.query.filter(Comment.tid == goods_id).\
                        filter(Comment.content == content).\
                        filter(Comment.star == star).\
                        filter(Comment.uid == uid).first()

        if comment is not None:
            self.errmsg['content'] = u'你已经评价过了'
        else:
            self.comment = Comment()
            self.comment.add_time  = int(time.time())
            db.session.add(self.comment)

        if self.errmsg:
            return self.errmsg

        user = User.query.filter(User.uid == uid).first()

        goods = Goods.query.filter(Goods.goods_id == goods_id).first()

        if user or goods is None:
            self.errmsg['content'] = u'你已经评价过了'

        if user and goods is not None:

            self.comment.uid        = user.uid
            self.comment.nickname   = user.nickname
            self.comment.avatar     = user.avatar
            self.comment.content    = content
            self.comment.star       = star
            self.comment.timg       = goods.goods_img
            self.comment.tname      = goods.goods_name
            self.comment.tid        = goods.goods_id

        db.session.commit()
        return {}
