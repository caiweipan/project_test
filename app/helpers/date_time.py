#!/usr/bin/env python
#coding=utf-8

import time
from datetime import datetime, timedelta, date

from codingabc.helpers import log_debug, log_info, log_error


def str2timestamp(str_date, format_style="%Y-%m-%d", zone=None):
    """
    @param:     str_date: string, 时间
    @param:     format_style: string, '%Y-%m-%d %H:%M:%S'
    @return:    int, 转换出错默认返回0
    """

    timeArray = time.strptime(str_date, format_style)
    if zone:
        tz = timezone(zone)
        y,m,d,H,M,S = timeArray[0:6]
        dt = datetime(y,m,d,H,M,S)
        t = tz.localize(dt)
        t = t.astimezone(pytz.utc)
        
        return int(time.mktime(t.utctimetuple()))-time.timezone
    
    return int(time.mktime(timeArray))

def timestamp2str(timestamp, format_style="%Y-%m-%d"):
    """ 时间戳转换为指定格式时间 """

    time_array = time.localtime(timestamp)
    
    return time.strftime(format_style, time_array)

def current_timestamp():
    """ 获取当前时间戳 """

    return int(time.time())

def current_strtime(format_style="%Y-%m-%d %H:%M:%S"):
    """ 获取当前时间 """

    now = datetime.now()

    return now.strftime(format_style)

def today_timestamp():
    """ 获取当天0点00分00秒的时间戳 """

    return int(time.mktime(date.today().timetuple()))

def before_after_timestamp(timestamp, days=0):
    """ 获取今天前后X天的0点00分00秒的时间戳 """
    """ days: 正整数为未来, 负整数为过去 """

    _datetime = datetime.utcfromtimestamp(timestamp)
    day       = _datetime + timedelta(days=days, hours=8)
    day_str   = day.strftime("%Y-%m-%d")
    timestamp = str2timestamp(day_str, "%Y-%m-%d")

    return timestamp

def get_social_time(timestamp):
    """ 获取社交时间，如：xx分钟前 """

    if timestamp <= 0:
        return ''

    ret = ''

    current_time = current_timestamp
    diff_time    = current_time - timestamp
    
    if diff_time <= 0:
        ret = u'来自未来'
    elif diff_time <= 60:
        ret = u'刚刚'
    elif diff_time <= 1*60*60:
        ret = u'%d分钟前' % int(diff_time/60)
    elif diff_time <= 1*24*60*60:
        ret = u'%d小时前' % int(diff_time/(60*60))
    elif diff_time <= 31*24*60*60:
        ret = u'%d天前' % int(diff_time/(24*60*60))
    elif diff_time <= 365*24*60*60:
        ret = u'%d月前' % int(diff_time/(30*24*60*60))
    else:
        ret = u'%d年前' % int(diff_time/(365*24*60*60))

    return ret




