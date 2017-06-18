#!/usr/bin/env python
#coding=utf-8

import json, urllib2, random

from flask import current_app, request, session

from codingabc.database import db
from codingabc.ext.aliyun import AliyunOSS, UploadNotAllowed
from codingabc.helpers import log_debug, log_info, log_error, toint

from app.helpers.date_time import current_timestamp
from app.models.news import News


class LotteryStaticService(object):
    """ 一元云购static service """

    @staticmethod
    def random_join(uid_list, join_quantity, random_list):
        """ 随机参与 """

        if join_quantity <= 0:
            return random_list

        # 随机用户
        count   = len(uid_list)
        randint = random.randint(0, (count-1))
        uid     = uid_list[randint]

        # 随机参与人次
        buy_num = random.randint(1, join_quantity)

        # 追加
        join_quantity -= buy_num
        random_dict    = {'uid':uid, 'buy_num':buy_num}
        random_list.append(random_dict)

        random_list = LotteryStaticService.random_join(uid_list, join_quantity, random_list)

        return random_list




