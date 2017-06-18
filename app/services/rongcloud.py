#!/usr/bin/env python
#coding=utf-8
from flask import current_app

from codingabc.helpers import log_debug, log_info, log_error

from app.services.rongcloud_sdk.group import Group


class RcGroupService(object):
    """ 群组Service """

    def __init__(self):
        _app_key    = current_app.config.get('RONG_CLOUD_APP_KEY', '')
        _app_secret = current_app.config.get('RONG_CLOUD_APP_SECRET', '')
        self.group  = Group(_app_key, _app_secret)

    def create(self, uid, group_id, group_name):
        """
            @use:               创建群组
            @param: uid         要创建群的用户ID
            @param: group_id    要创建的群组ID
            @param: group_name  要创建的群组名称
        """

        res = self.group.create(uid, group_id, group_name)
        ret = res.get()

        if ret['code'] != 200:
            log_error(u'[ErrorServiceRcGroupServiceCreate] create error: ret:%s' % ret)

        return True

    def dismiss(self, uid, group_id):
        """
            @use:               解散群组
            @param: uid         操作解散群的用户ID
            @param: group_id    要解散的群组ID
        """

        res = self.group.dismiss(uid, group_id)
        ret = res.get()

        if ret['code'] != 200:
            log_error(u'[ErrorServiceRcGroupServiceQuit] create error: ret:%s' % ret)

        return True

    def join(self, uid, group_id, group_name):
        """
            @use: 加入群组
            @param: uid         要加入群的用户ID
            @param: group_id    要加入的群组ID
            @param: group_name  要加入的群组名称
        """

        res = self.group.join(uid, group_id, group_name)
        ret = res.get()

        if ret['code'] != 200:
            log_error(u'[ErrorServiceRcGroupServiceJoin] create error: ret:%s' % ret)

        return True

    def quit(self, uid, group_id):
        """
            @use:               退出群组
            @param: uid         要退出群的用户ID
            @param: group_id    要退出的群组ID
        """

        res = self.group.quit(uid, group_id)
        ret = res.get()

        if ret['code'] != 200:
            log_error(u'[ErrorServiceRcGroupServiceQuit] create error: ret:%s' % ret)

        return True




