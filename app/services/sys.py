#!/usr/bin/env python
#coding=utf-8

import json, urllib2

from flask import current_app, request

from codingabc.database import db
from codingabc.helpers import log_debug, log_info, log_error, toint

from app.helpers.date_time import current_timestamp
from app.models.sys import SysSetting


class SaveSysSettingService(object):
    """ 保存系统设置service """

    def __init__(self, form, ss_id=0):
        self.errmsg          = {}
        self.form            = form
        self.ss_id           = ss_id
        self.current_time    = current_timestamp()
        self.sys_setting     = None

    def check(self):
        """ 检查 """

        # 检查 - 必填项
        required_arr = ['cb_id', 'is_invite_new_friends_to_register_as_a_gift_coupon', 'is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons']
        for key in required_arr:
            value = self.form.get(key, '').strip()
            if not value:
                self.errmsg[key] = u'必填项'

        if len(self.errmsg) > 0:
            return False

        return True

    def save(self):
        """ 保存 """

        cb_id                                                                     = toint(self.form.get('cb_id', '').strip())
        is_invite_new_friends_to_register_as_a_gift_coupon                        = toint(self.form.get('is_invite_new_friends_to_register_as_a_gift_coupon', '-1').strip())
        is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons    = toint(self.form.get('is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons', '-1').strip())

        cb_id_info                                                                  = SysSetting.query.filter(SysSetting.key == 'cb_id').first()
        is_invite_new_friends_to_register_as_a_gift_coupon_info                     = SysSetting.query.filter(SysSetting.key == 'is_invite_new_friends_to_register_as_a_gift_coupon').first()
        is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons_info = SysSetting.query.filter(SysSetting.key == 'is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons').first()

        if cb_id_info:
            cb_id_info.update(value=cb_id, commit=True)
        else:
            desc = u'邀请新朋友赠送的优惠券批次id'
            SysSetting.create(key='cb_id', value=cb_id, desc=desc, commit=True)

        if is_invite_new_friends_to_register_as_a_gift_coupon_info:
            is_invite_new_friends_to_register_as_a_gift_coupon_info.update(value=is_invite_new_friends_to_register_as_a_gift_coupon, commit=True)
        else:
            desc = u'邀请新朋友是否注册后赠送优惠券'
            SysSetting.create(key='is_invite_new_friends_to_register_as_a_gift_coupon', value=is_invite_new_friends_to_register_as_a_gift_coupon,desc=desc, commit=True)

        if is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons_info:
            is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons_info.update(value=is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons, commit=True)
        else:
            desc = u'邀请新朋友是否首次下单后赠送优惠券'
            SysSetting.create(key='is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons',desc=desc, value=is_invite_new_friends_for_the_first_time_after_ordered_as_gift_coupons, commit=True)
        return True



