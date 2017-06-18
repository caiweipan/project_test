#!/usr/bin/env python
#coding=utf-8

import urllib2

from flask import current_app

from codingabc.helpers import log_debug, log_info, log_error

import json

from app.helpers.common import urlencode

class YunPian(object):
    """云片网短信service"""
    def __init__(self):
        self.apikey = current_app.config.get('APIKEY')
        #模版ID
        self.tpl_id = '1'


    def send_sms(self, mobile, content, tpl_id='1', cp=u'迈卡车生活'):
        """发送短信"""
        if tpl_id:
            self.tpl_id = tpl_id
        code_content = u'#code#=' + content + u'&#company#=' + cp
        param = {'apikey':self.apikey, 'mobile':mobile, 'tpl_id':self.tpl_id, 'tpl_value':code_content}
        url = 'http://yunpian.com/v1/sms/tpl_send.json'
        requestDate = urlencode(param)
        log_debug(param)
        try:
            res = urllib2.urlopen(url, requestDate, timeout=30).read()
        except Exception, e:
            log_error('[YunPianError] retry:%d, mobile:%s, content:%s, %s' % (json.loads(res)["code"], mobile, content, e))

        log_info('[YunPianService] res:%s, [%s] %s [tpl_value:%s]' % (json.loads(res)["code"], mobile, content, self.tpl_id))
        log_debug(res)

        return res

    def send_sms_text(self, mobile, content):
        """发送短信通用接口"""

        param = {'apikey':self.apikey, 'mobile':mobile, 'text':content}
        url = 'http://yunpian.com/v1/sms/send.json'
        requestDate = urlencode(param)
        log_debug(param)
        try:
            res = urllib2.urlopen(url, requestDate, timeout=30).read()
        except Exception, e:
            log_error('[YunPianError] result_code:%d, content:%s, %s' % (json.loads(res)["code"], content, e))

        log_info('[YunPianService] result_code:%s, [content:%s]' % (json.loads(res)["code"], content))
        log_debug(res)

        return res
