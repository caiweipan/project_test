#!/usr/bin/env python
#coding=utf-8

from flask import request

from codingabc.helpers import log_debug, log_info, log_error


def get_nav_classname(nav):
    """获取导航菜单css class名"""
    if not nav:
        return ''

    if request.endpoint == nav.get('endpoint', ''):
        return ' class=active'

    child_nav_list = nav.get('child', [])
    for child_nav in child_nav_list:
        if request.endpoint == child_nav.get('endpoint', ''):
            return ' class=active'

    return ''




