#!/usr/bin/env python
#coding=utf-8

import json, urllib2
from requests.utils import guess_json_utf

from codingabc.helpers import log_debug, log_info, log_error, urlencode


class ApiJsonService(object):
    """ API(josn)服务 """

    def __init__(self, url, params=None, method='GET', 
                timeout=10, cookie_jar=None, json_type='me', headers=[('language', 'en')]):
        self.url        = url
        self.params     = params
        self.method     = method
        self.timeout    = timeout
        self.cookie_jar = cookie_jar
        self.json_type  = json_type
        self.headers    = headers

        self.res        = None
        self.json       = {}
        self.ret        = None
        self.msg        = None
        self.data       = None
        self.set_cookie = ''
        self.encoding   = None

    def call_service(self):
        """ 调用远程服务 """
        try:
            encode_data = None
            if self.params is not None:
                if self.method == 'GET':
                    self.url += '?' + urlencode(self.params)
                    log_debug(self.url)

                elif self.method == 'POST':
                    encode_data = urlencode(self.params)

            opener = urllib2.build_opener()
            opener.addheaders = self.headers
            
            if self.cookie_jar is not None:
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))

            res_obj = opener.open(self.url, data=encode_data, timeout=self.timeout)
            self.set_cookie = res_obj.info().getheader('Set-Cookie')
            self.res = res_obj.read()

            # encoding
            self.encoding = guess_json_utf(self.res)
            if self.encoding:
                self.res = self.res.decode(self.encoding)

            self.json = json.loads(self.res)
            self.ret  = self.json.get('ret')
            self.msg  = self.json.get('msg')
            self.data = self.json.get('data')
        except Exception, e:
            log_debug('[JSONService] url:%s, response:%s, expetion:%s' % (self.url, self.res, e))
            return False

        if self.ret != 0 and self.json_type == 'me':
            log_info('[JSONService] url:%s, response:%s' % (self.url, self.res))
            return False

        return True

    def get_response_cookie(self):
        """ 获取响应返回cookie """
        if not self.set_cookie:
            return {}

        cookie_map = {}
        cookie_arr = self.set_cookie.split(',')
        for cookie in cookie_arr:
            arr = cookie.split(';')
            str_kv = arr[0]
            str_kv = str_kv.strip()
            kv = str_kv.split('=')
            if len(kv) == 2:
                cookie_map[kv[0]] = kv[1]

        return cookie_map




