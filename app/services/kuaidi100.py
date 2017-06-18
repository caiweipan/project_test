#!/usr/bin/env python
#coding=utf-8

import requests, json, hashlib

from flask import current_app, request

from codingabc import code
from codingabc.database import db
from codingabc.helpers import log_debug, log_info, log_error, toint


class KuaiDi100StaticMethodsService(object):
    """ 快递100静态方法Service """

    @staticmethod
    def search(com, num, muti=1, order=u'desc'):
        """ 查询 """

        customer    = current_app.config.get('KUAIDI100_CUSTOMER', '')
        key         = current_app.config.get('KUAIDI100_KEY', '')
        data        = []
        status_text = u'暂无物流信息'

        url   = u'http://poll.kuaidi100.com/poll/query.do'
        param = u'{"com":"%s", "num":"%s"}' % (com, num)

        _sign  = u'%s%s%s' % (param, key, customer)
        sign   = hashlib.md5(_sign).hexdigest()
        sign   = sign.upper()

        data = {'customer':customer, 'param':param, 'sign':sign}
        res  = requests.post(url, data=data)
        res.encoding = 'utf8'

        log_info('[InfoKuaiDi100StaticMethodsServiceSearch][RequestInfo]  url:%s  res.text:%s' % (url, res.text))
        status_code = toint(res.status_code)
        if status_code == 200:
            ret    = res.json()
            status = ret.get('status', None)
            state  = toint(ret.get('state', -1))
            data   = ret.get('data', [])

            if state == 0:
                status_text = u'在途中'
            elif state == 1:
                status_text = u'揽件中'
            elif state == 2:
                status_text = u'疑难'
            elif state == 3:
                status_text = u'已签收'
            elif state == 4:
                status_text = u'退签中'
            elif state == 5:
                status_text = u'派件中'
            elif state == 6:
                status_text = u'已退回'
            else:
                status_text = u'暂无物流信息'
        else:
            log_info('[InfoKuaiDi100StaticMethodsServiceSearch][SearchError]  url:%s  res.text:%s' % (url, res.text))

        log_info('### =============>state:%s, status_text:%s, res.status_code:%s'%(state, status_text, status_code))
        return (data, status_text)




