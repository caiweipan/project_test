#!/usr/bin/env python
#coding=utf-8

import urllib

from cookielib import Cookie, CookieJar

from flask import current_app, request

from codingabc.helpers import log_debug, log_info, log_error

from app.services.net import ApiJsonService


def get_ajs(uri, params=None, method='GET', timeout=10, api_domain=None,
            session_cookie_name='session', session_cookie_value=None):
    """ 获取API服务实例 """

    # API_DOMAIN
    if api_domain is None:
        api_domain = current_app.config['API_DOMAIN']

    # 获取会话cookie
    if session_cookie_value is None:
        session_cookie_value = request.cookies.get(session_cookie_name, None)

    # 设置会话cookie
    cj = CookieJar()
    if session_cookie_value is not None:
        c = Cookie(None, session_cookie_name, session_cookie_value, 
               port=None, port_specified=None, domain='', 
               domain_specified=None, domain_initial_dot=None, path='/', 
               path_specified=None, secure=None, expires=None, 
               discard=None, comment=None, comment_url=None, 
               rest=None)
        cj.set_cookie(c)
        
    # 格式化请求URL
    url = api_domain + uri

    # API服务实例
    ajs = ApiJsonService(url, params, method, timeout, cj)

    return ajs


def urlencode(params):
    _params = params.copy()
    for k,v in params.items():
        if isinstance(v, types.StringType) or isinstance(v, types.UnicodeType):
            _params[k] = v.encode('utf8')

    return urllib.urlencode(_params)




