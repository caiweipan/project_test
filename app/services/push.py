#!/usr/bin/env python
#coding=utf-8

import types

from flask import current_app

from codingabc.ext import xinge
from codingabc.database import db
from codingabc.helpers import log_debug, log_info, log_error

from app.models.user import User, UserDevice
from app.services.yunpian import YunPian


class XingePushService(object):
    """信鸽推送服务"""

    def __init__(self, unread_num=1):
        self.unread_num = unread_num

    def _get_message(self, os, title, content, data={}):
        """获取消息体
        :param os 操作系统 ios|android
        :param title 标题
        :param content 内容
        :param data 自定义键值对，key和value都必须是字符串
        :return msg
        """

        custom = {}
        for k,v in data.items():
            if isinstance(v, types.StringType) or isinstance(v, types.UnicodeType):
                custom[k] = v.encode('utf8')
            else:
                custom[k] = str(v)

        msg = None
        if os == 'android':
            msg = xinge.Message()
            msg.type = xinge.Message.TYPE_MESSAGE
        else:
            msg = xinge.MessageIOS()
            msg.type = xinge.Message.TYPE_NOTIFICATION

        msg.title = title.encode('utf8')
        msg.content = content.encode('utf8')
        # 消息为离线设备保存的时间，单位为秒。默认为0，表示只推在线设备
        msg.expireTime = 300

        # 自定义键值对，key和value都必须是字符串
        msg.custom = data

        # 通知展示样式，仅对通知有效
        # 样式编号为2，响铃，震动，不可从通知栏清除，不影响先前通知
        style = xinge.Style(2, 1, 1, 1, 0)
        msg.style = style

        if os == 'ios':
            msg.alert = msg.content
            msg.badge = self.unread_num
            msg.sound = 'default'
            log_info('alert:%s, badge:%s, sound:%s' % (msg.alert, msg.badge, msg.sound))

        return msg


    def push_user(self, uid, title, content, data={}, client_flag='USER', sms=False):
        """用户端推送
        :param title 标题
        :param content 内容
        :param data 自定义键值对，key和value都必须是字符串
        """
        user = db.session.query(User.pushtoken, User.uid, UserDevice.device_os,UserDevice.ud_id).\
                filter(User.uid == UserDevice.uid).\
                filter(User.uid == uid).first()

        if user is None:
            log_info('[PushUser] Can not push user. user is None.')
            return None

        if (user.os not in ('ios', 'android')
                    or not user.pushtoken):
            log_info('[PushUser] Can not push user. uid:%d, os:%s, pushtoken:%s' %
                            (uid, user.os, user.pushtoken))
            return None

        # 初始化app对象，设置有效的access id和secret key
        xingeapp = self._get_xingeapp(user.os.upper(), client_flag)
        if xingeapp is None:
            return None

        msg = self._get_message(user.os, title, content, data)

        # 第三个参数environment仅在iOS下有效。ENV_DEV表示推送APNS开发环境
        tmp = xingeapp.PushSingleDevice(user.pushtoken.encode('utf8'), msg, xinge.XingeApp.ENV_PROD)
        log_info(tmp)



        return tmp


    def _get_xingeapp(self, os, client_flag):
        """获取信鸽推送app"""
        access_id_name  = 'XINGE_%s_%s_ACCESS_ID' % (client_flag, os.upper())
        secret_key_name = 'XINGE_%s_%s_SECRET_KEY' % (client_flag, os.upper())

        access_id  = current_app.config[access_id_name]
        secret_key = current_app.config[secret_key_name]

        if not access_id or not secret_key:
            log_info('[PushError] %s:%s, %s:%s' %
                    (access_id_name, access_id, secret_key_name, secret_key))
            return None

        log_info('access_id:%s, secret_key:%s' % (access_id, secret_key))

        app = xinge.XingeApp(access_id.encode('utf8'), secret_key.encode('utf8'))
        log_debug('Push get app ok')
        return app

