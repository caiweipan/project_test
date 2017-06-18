#!/usr/bin/env python
#coding=utf-8

import json, urllib2, time

from flask import current_app, request, session

from codingabc.database import db

from codingabc.ext.aliyun import UploadNotAllowed, AliyunOSS
from codingabc.helpers import log_debug, log_info, log_error, toint, randomstr

from app.helpers.user import get_uid
from app.helpers.date_time import current_timestamp
from app.services.rongcloud import RcGroupService
from app.models.user import User


class SaveUserSalonService(object):
    """ 保存群组service """

    def __init__(self, form, us_id=0):
        self.errmsg       = {}
        self.form         = form
        self.us_id        = us_id
        self.current_time = current_timestamp()
        self.is_new       = False
        self.salon        = None
        self.salon_img    = ''

    def check(self):
        """ 检查 """

        # 群组原图
        _salon_img = request.files.get('salon_img', None)

        # 是否创建群组
        self.is_new = True if self.us_id == 0 else False

        # 检查 - 必填项
        required_arr = ['salon_name', 'sort_order', 'desc']
        for key in required_arr:
            value = self.form.get(key, '').strip()
            if not value:
                self.errmsg[key] = u'必填项'

        # 检查 - 新建群组是否上传群组原图
        if self.is_new and not _salon_img:
            self.errmsg['salon_img'] = u'必填项'

        # 检查 - 群组是否存在
        if not self.is_new:
            self.salon = UserSalon.query.get(self.us_id)
            if not self.salon:
                self.errmsg['submit'] = u'群组不存在'

        # 检查 - 群组原图是否合法
        if _salon_img:
            oss = AliyunOSS('user', current_app.config['SAVE_TARGET_PATH'])
            try:
                oss.save(_salon_img)
                self.salon_img = oss.put_to_oss()
            except UploadNotAllowed, e:
                self.errmsg['salon_img'] = u'只允许是图片文件'
            except Exception, e:
                self.errmsg['salon_img'] = u'原图上传失败'

        if len(self.errmsg) > 0:
            log_info(self.errmsg)
            return False

        return True

    def save(self):
        """ 保存 """

        salon_name = self.form.get('salon_name', '').strip()
        desc       = self.form.get('desc', '').strip()
        sort_order = toint(self.form.get('sort_order', 0))
        us_id      = toint(self.form.get('us_id', 0))
        uid        = session['uid']

        if self.is_new:
            self.salon = UserSalon.create(add_time=self.current_time)

        # 群组原图
        if self.salon_img:
            self.salon.update(salon_img=self.salon_img)
        invitation_code = randomstr(6).upper()
        self.salon.update(salon_name=salon_name, desc=desc, user_count=1,
                    sort_order=sort_order,invitation_code=invitation_code, commit=True)

        # 创建rongcloud群组
        if self.is_new:
            admin_uid = get_uid()
            rgs       = RcGroupService()
            rgs.create(admin_uid, self.salon.us_id, self.salon.salon_name)

            uis = UserInSalon()
            uis.uid      = admin_uid
            uis.us_id    = self.salon.us_id
            uis.add_time = int(time.time())
            db.session.add(uis)
            db.session.commit()

        return True


def get_user_data():
    """获取用户资料"""

    user_data_list = User.query.all()
    data_list, data_dict = [], {}
    USERNAME,MOBILE,NICKNAME,AVATAR,REALNAME,GENDER = {}, {}, {}, {}, {}, {}
    for user in user_data_list:
        USERNAME[user.uid] = user.username
        MOBILE[user.uid] = user.mobile
        NICKNAME[user.uid] = user.nickname
        AVATAR[user.uid] = user.avatar
        REALNAME[user.uid] = user.realname
        GENDER[user.uid] = user.gender

    return (USERNAME, MOBILE, NICKNAME, AVATAR, REALNAME, GENDER)
