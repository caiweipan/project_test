#!/usr/bin/env python
#coding=utf-8

import json

from codingabc.helpers import log_debug, log_info, log_error

from app.services.yunpian import YunPian


def yunpian_single(mobile, content):
    """ 云片发送单条短信 """

    sms = YunPian()
    res = sms.send_sms_text(mobile, content)
    if res is None:
        log_error(u'[ErrorHelperSmsYunpianSingle] is none: mobile:%s content:%s' % (mobile, content))
        return False

    result = json.loads(res)
    if result['code'] != 0:
        log_error(u'[ErrorHelperSmsYunpianSingle] return error code: mobile:%s content:%s code:%s' % (mobile, content, result['code']))
        return False

    return True




